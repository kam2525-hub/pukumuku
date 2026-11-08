"""Build the original Bread Catch bakery set with Blender 4.5 in background mode."""

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.noise import noise_vector


OUTPUT = Path(__file__).resolve().parent / "models" / "catch_breads"
OUTPUT.mkdir(parents=True, exist_ok=True)
TAU = math.tau
RNG = random.Random(51108)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def linear(channel):
    channel = min(1.0, max(0.0, channel))
    return channel / 12.92 if channel < 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def rgb(hex_color):
    return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4))


def material(name, roughness, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    # glTF multiplies its white base color by the exported COLOR_0 attribute.
    return mat


CRUST = material("焼き目と気泡", 0.62)
GLAZE = material("卵でつやを出した焼き皮", 0.4)
COOKIE = material("サクサクのクッキー生地", 0.81)
FILLING = material("具材", 0.52)
YOLK = material("半熟のつや", 0.30)
GOLD = material("金箔", 0.32, 0.36)


def mesh(name, vertices, faces, palette, mat, color_at):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    data.materials.append(mat)
    color = data.color_attributes.new(name="Baked Color", type="BYTE_COLOR", domain="POINT")
    for entry, point in zip(color.data, vertices):
        tone = color_at(point)
        base = [a + (b - a) * tone for a, b in zip(*palette)]
        entry.color = (*map(linear, base), 1.0)
    for poly in data.polygons:
        poly.use_smooth = True
    return obj


def grain(point):
    v = Vector(point)
    return noise_vector(v * 5.0)[0] * 0.15 + noise_vector(v * 103.0)[1] * 0.12


def ellipsoid(name, center, radii, colors, mat=CRUST, shape=None, tone=None, n=56, m=28):
    # Ring caps share single vertices so no degenerate faces are exported.
    vertices = []
    for row in range(m + 1):
        theta = math.pi * row / m
        for col in range(1 if row in (0, m) else n):
            a = TAU * col / n
            u = math.sin(theta) * math.cos(a)
            v = math.sin(theta) * math.sin(a)
            w = math.cos(theta)
            x, y, z = shape(u, v, w, a) if shape else (u, v, w)
            vertices.append(tuple(o + p * r for o, p, r in zip(center, (x, y, z), radii)))
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    for row in range(m - 2):
        first = 1 + row * n
        for i in range(n):
            a = first + i
            b = first + (i + 1) % n
            faces.append((a, a + n, b + n, b))
    bottom = len(vertices) - 1
    faces.extend((bottom, bottom - n + (i + 1) % n, bottom - n + i) for i in range(n))

    def surface_color(p):
        height = (p[2] - center[2]) / radii[2]
        return min(1, max(0, (tone(p, height) if tone else 0.42 + 0.45 * height) + grain(p)))

    return mesh(name, vertices, faces, tuple(map(rgb, colors)), mat, surface_color)


def bun(name, center, radii, colors=("ECB064", "A84A14"), **options):
    def baked(u, v, w, a):
        bump = 1 + 0.025 * math.sin(5 * a + 0.5) + 0.012 * math.cos(11 * a - 2 * w)
        return u * bump, v * bump, max(-0.63, w)
    return ellipsoid(name, center, radii, colors, shape=baked, **options)


def bits(name, points, colors, size, mat=FILLING):
    """Merge small toppings into one mesh to keep browser draw calls low."""
    parts = []
    for center, stretch in points:
        radii = tuple(r * stretch for r in size)
        parts.append(ellipsoid(name, center, radii, colors, mat, n=8, m=5))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    return bpy.context.object


def croissant():
    vertices, faces = [], []
    rings, sides = 120, 36
    for i in range(rings + 1):
        t = 2 * i / rings - 1
        radius = 0.012 + 0.153 * max(0, 1 - abs(t)) ** 0.65
        roll = 1 + 0.14 * math.sin(22 * t) + 0.05 * math.sin(66 * t)
        for j in range(sides):
            angle = TAU * j / sides
            x = 0.54 * t + 0.25 * t * radius * math.cos(angle)
            y = 0.23 - 0.58 * t * t + radius * roll * math.cos(angle)
            z = 0.04 * t + 0.80 * radius * roll * math.sin(angle)
            vertices.append((x, y, z))
    for row in range(rings):
        for j in range(sides):
            a = row * sides + j
            b = row * sides + (j + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces += [tuple(reversed(range(sides))), tuple(range(rings * sides, (rings + 1) * sides))]

    def color(p):
        fold = max(0, math.sin(52 * p[0] + 6 * p[1])) ** 5
        return min(1, max(0, 0.40 + 2.1 * p[2] + 0.26 * fold + grain(p)))

    mesh("折り込んだバター生地", vertices, faces, (rgb("FFCF80"), rgb("BC4C12")), GLAZE, color)


def melon():
    bun("ふんわりした中生地", (0, 0, -0.045), (0.423, 0.423, 0.24))

    def lattice(x, y):
        return max(math.exp(-((q - round(q / 0.26) * 0.26) / 0.043) ** 2)
                   for q in (x + y, x - y))

    def shell(u, v, w, a):
        groove = lattice(u, v) * max(0, min(1, w * 3))
        return u, v, max(-0.19, w) - 0.12 * groove

    ellipsoid("格子を刻んだクッキー皮", (0, 0, 0), (0.449, 0.449, 0.266),
              ("FFF0AF", "CA802E"), COOKIE, shape=shell,
              tone=lambda p, h: 0.24 + 0.52 * lattice(p[0] / 0.449, p[1] / 0.449),
              n=120, m=64)
    points = []
    for _ in range(70):
        x, y = (RNG.uniform(-0.33, 0.33) for _ in range(2))
        r = (x*x + y*y) / 0.449**2
        if r < 0.75 and lattice(x / 0.449, y / 0.449) < 0.25:
            points.append(((x, y, 0.266 * math.sqrt(1 - r)), RNG.uniform(0.55, 1.25)))
    bits("ざらめ", points, ("FFEFCA", "E9B95F"), (0.012, 0.010, 0.007))


def cream():
    def scallop(u, v, w, a):
        front = max(0, -v)
        return u, v + 0.15 * front**2 * math.cos(12 * u), max(-0.56, w)
    ellipsoid("切り込みの入ったグローブ型", (0, 0, -0.008), (0.46, 0.34, 0.228),
              ("F7BF70", "B75617"), GLAZE, shape=scallop)
    ellipsoid("割れ目からのぞくカスタード", (-0.07, -0.248, 0.09),
              (0.18, 0.046, 0.047), ("FFF2AE", "E9A732"), YOLK)


def burger():
    bun("下のバンズ", (0, 0, -0.162), (0.432, 0.375, 0.09))

    def leaf(u, v, w, a):
        edge = 1 + 0.061 * math.sin(14 * a) + 0.035 * math.sin(27 * a)
        return u * edge, v * edge, w + math.sin(12 * a) * (1 - abs(w)) * 0.46

    ellipsoid("フリルレタス", (0, 0, -0.101), (0.425, 0.377, 0.045), ("BBDB5A", "357536"),
              FILLING, shape=leaf)
    ellipsoid("粗挽きパティ", (0, 0, -0.053), (0.423, 0.365, 0.071), ("9B5E3A", "482017"),
              COOKIE, shape=leaf)
    ellipsoid("トマト", (0.005, -0.013, 0.013), (0.407, 0.36, 0.048), ("F36238", "AB2620"), YOLK)

    def cheese(u, v, w, a):
        square = max(abs(math.cos(a)), abs(math.sin(a))) ** -0.52
        return u * square, v * square, w - 0.9 * (square - 1)

    ellipsoid("とろけたチェダー", (0, 0, 0.041), (0.393, 0.345, 0.034), ("FFC33A", "F88D10"),
              YOLK, shape=cheese)
    bun("ごまバンズ", (0, 0, 0.074), (0.444, 0.376, 0.146), mat=GLAZE)
    points = []
    for _ in range(44):
        x, y = RNG.uniform(-0.36, 0.36), RNG.uniform(-0.28, 0.28)
        r = (x / 0.444)**2 + (y / 0.376)**2
        if r < 0.8:
            points.append(((x, y, 0.074 + 0.146 * math.sqrt(1 - r)), RNG.uniform(0.7, 1.3)))
    bits("白ごま", points, ("FFF0BE", "C28B4A"), (0.022, 0.009, 0.007))


def savory_bun(name):
    bun(name, (0, 0, -0.059), (0.456, 0.332, 0.24), mat=GLAZE)


def egg():
    savory_bun("香ばしいたまごパンの生地")

    def white(u, v, w, a):
        edge = 1 + 0.083 * math.sin(5 * a) + 0.041 * math.cos(9 * a)
        return u * edge, v * edge, w

    ellipsoid("縁がこんがりした白身", (0, 0, 0.137), (0.367, 0.249, 0.045),
              ("D99043", "FFF0CE"), FILLING, shape=white)
    ellipsoid("丸い半熟の黄身", (0.037, -0.021, 0.166), (0.144, 0.132, 0.064),
              ("FFD244", "F68C0A"), YOLK)


def mushroom():
    savory_bun("きのこパンの生地")
    for x, y, size in [(-0.207, -0.054, 1.0), (0.0, 0.083, 0.92), (0.195, -0.093, 1.1)]:
        ellipsoid("きのこの軸", (x, y - 0.058, 0.167),
                  (0.033, 0.082 * size, 0.021), ("FFE0AB", "BA8056"), FILLING, n=28, m=16)
        ellipsoid("焼ききのこの傘", (x, y + 0.024, 0.180),
                  (0.113 * size, 0.076 * size, 0.044), ("D69964", "7F4730"), GLAZE, n=36, m=20)
    points = [((RNG.uniform(-0.23, 0.23), RNG.uniform(-0.14, 0.13), 0.167), 1)
              for _ in range(17)]
    bits("刻みパセリ", points, ("92A63F", "3B6027"), (0.017, 0.009, 0.009))


def negi():
    savory_bun("ねぎパンの生地")
    ellipsoid("香ばしいみそチーズ", (0, 0, 0.137), (0.358, 0.236, 0.053),
              ("F8CB77", "B3642B"), GLAZE)
    parts = []
    for i in range(18):
        x = RNG.uniform(-0.295, 0.295)
        y = RNG.uniform(-0.14, 0.14) * (1 - abs(x))
        z = 0.163 + 0.027 * (1 - abs(x) / 0.295)
        bpy.ops.mesh.primitive_torus_add(major_segments=18, minor_segments=8,
                                        major_radius=RNG.uniform(0.030, 0.048),
                                        minor_radius=0.009, location=(x, y, z),
                                        rotation=(RNG.uniform(-0.4, 0.4), RNG.uniform(-0.4, 0.4), 0))
        raw = bpy.context.object
        vertices = [tuple(raw.matrix_world @ v.co) for v in raw.data.vertices]
        faces = [tuple(p.vertices) for p in raw.data.polygons]
        bpy.data.objects.remove(raw, do_unlink=True)
        palette = ("E3E9A3", "76A747") if i % 3 == 0 else ("A1CC50", "257140")
        parts.append(mesh("小口切りのねぎ", vertices, faces, tuple(map(rgb, palette)), FILLING,
                          lambda p: 0.48 + grain(p)))
    bpy.ops.object.select_all(action="DESELECT")
    for obj in parts:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()


def cocoa():
    def swirl(u, v, w, a):
        r = math.hypot(u, v)
        fold = max(0, math.cos(3 * a + r * 13)) ** 4
        return u, v, max(-0.65, w) - 0.10 * fold * r * max(0, w)
    ellipsoid("ココアを折り込んだ渦巻き生地", (0, 0, 0), (0.459, 0.34, 0.22),
              ("AB6C4D", "42201A"), CRUST, shape=swirl,
              tone=lambda p, h: 0.54 + 0.36 * math.cos(
                  3 * math.atan2(p[1] / 0.34, p[0] / 0.459) + 13 * math.hypot(p[0] / 0.459, p[1] / 0.34)),
              n=104, m=48)
    points = [((x, y, 0.22 * math.sqrt(1 - (x / 0.459)**2 - (y / 0.34)**2)), 1)
              for x, y in [(-0.18, 0.05), (-0.07, -0.17), (0.19, 0.08), (0.1, 0.15), (0.22, -0.08)]]
    bits("刻んだチョコ", points, ("64362A", "341919"), (0.034, 0.028, 0.018), GLAZE)


def gold():
    def petals(u, v, w, a):
        edge = 1 + 0.09 * math.cos(8 * a)
        return u * edge, v * edge, max(-0.64, w)
    ellipsoid("八つのひだをつけた金箔パン", (0, 0, 0), (0.294, 0.227, 0.205),
              ("FFD259", "E8820A"), GOLD, shape=petals)
    ellipsoid("純くんの顔を押した金の焼き印", (0, 0, 0.144), (0.186, 0.154, 0.076),
              ("FFF2AD", "F6B72A"), GOLD)
    for x in (-0.056, 0.056):
        ellipsoid("焼き印の目", (x, -0.008, 0.214), (0.019, 0.028, 0.009),
                  ("8E4612", "6B3210"), FILLING, n=18, m=10)
    ellipsoid("焼き印の口", (0, -0.072, 0.213), (0.042, 0.016, 0.010),
              ("9F4D13", "73340F"), FILLING, n=24, m=12)


def burnt():
    def charred(u, v, w, a):
        edge = 1 + 0.065 * math.sin(7 * a + w * 2) + 0.032 * math.cos(19 * a)
        return u * edge, v * edge, max(-0.64, w) + 0.045 * math.sin(23 * u + v * 12)
    ellipsoid("焦げた皮と裂け目", (0, 0, 0), (0.452, 0.33, 0.208),
              ("76503A", "211815"), COOKIE, shape=charred,
              tone=lambda p, h: 0.5 + 0.44 * math.tanh(noise_vector(Vector(p) * 8)[0] * 3 + h))
    points = [((x, y, 0.208 * math.sqrt(1 - (x / 0.452)**2 - (y / 0.33)**2)), 1)
              for x, y in [(-0.22, -0.071), (-0.086, 0.13), (0.14, -0.1), (0.22, 0.08)]]
    bits("焼き割れの縁", points, ("66422F", "39231B"), (0.060, 0.014, 0.012), COOKIE)


BAKERY = [croissant, melon, cream, burger, egg, mushroom, negi, cocoa, gold, burnt]
scene = bpy.context.scene
parts_by_bread = {}
for bake in BAKERY:
    collection = bpy.data.collections.new("bread_" + bake.__name__)
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
    bake()
    parts_by_bread[collection] = list(collection.objects)
    bpy.ops.object.select_all(action="DESELECT")
    for part in collection.objects:
        part.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT / (collection.name + ".glb")),
                              use_selection=True, export_vertex_color="ACTIVE",
                              export_all_vertex_colors=True)

studio = bpy.data.collections.new("図鑑の撮影")
scene.collection.children.link(studio)
camera_data = bpy.data.cameras.new("パン図鑑")
camera = bpy.data.objects.new("パン図鑑", camera_data)
studio.objects.link(camera)
scene.camera = camera
camera_data.type = "ORTHO"
scene.render.engine = "BLENDER_WORKBENCH"
scene.render.resolution_x = scene.render.resolution_y = 320
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "WEBP"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.quality = 88
scene.render.film_transparent = True
scene.view_settings.view_transform = "Standard"
scene.view_settings.exposure = 0.55
shading = scene.display.shading
shading.light = "STUDIO"
shading.studio_light = "paint.sl"
shading.studiolight_rotate_z = 0.25
shading.color_type = "VERTEX"
shading.show_shadows = True
shading.show_cavity = True
shading.cavity_type = "BOTH"
shading.curvature_ridge_factor = 0.9
shading.curvature_valley_factor = 0.7

for collection, parts in parts_by_bread.items():
    for other in parts_by_bread:
        other.hide_render = other != collection
    bounds = [part.matrix_world @ Vector(corner) for part in parts for corner in part.bound_box]
    width = max(p.x for p in bounds) - min(p.x for p in bounds)
    depth = max(p.y for p in bounds) - min(p.y for p in bounds)
    camera_data.ortho_scale = max(width, depth) * 1.25
    center = sum(bounds, Vector()) / len(bounds)
    center.x = (max(p.x for p in bounds) + min(p.x for p in bounds)) / 2
    center.y = (max(p.y for p in bounds) + min(p.y for p in bounds)) / 2
    camera.location = center + Vector((0.68, -2.55, 2.75))
    camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(OUTPUT / (collection.name + ".webp"))
    bpy.ops.render.render(write_still=True)

# Arrange the editable bakery on a grid after exporting centered game assets.
for i, (collection, parts) in enumerate(parts_by_bread.items()):
    collection.hide_render = False
    for part in parts:
        part.location += Vector(((i % 5 - 2) * 1.25, (0.5 - i // 5) * 1.22, 0))
bpy.ops.object.select_all(action="DESELECT")
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "bakery.blend"), compress=True)
