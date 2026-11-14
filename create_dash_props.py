import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

OUT_DIR = r"c:\Users\akeer.AKERU\Documents\Codex\2026-10-24\new-chat\pukumuku-web-preview\models\dash_props"
os.makedirs(OUT_DIR, exist_ok=True)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def make_mat(name, base_color, roughness=0.55, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_bevel(obj, width=0.015, segments=2):
    mod = obj.modifiers.new(name="Bevel", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)


def set_smooth(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True


def create_box(name, size, loc, mat, rot=(0, 0, 0), bevel=0.015):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(scale=True)
    if bevel > 0:
        add_bevel(obj, width=bevel, segments=2)
    obj.data.materials.append(mat)
    set_smooth(obj)
    return obj


def create_cyl(name, radius, depth, loc, mat, rot=(0, 0, 0), verts=20):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    set_smooth(obj)
    return obj


def export_glb(filename):
    path = os.path.join(OUT_DIR, filename)
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_materials='EXPORT'
    )
    print(f"Exported: {path}")


# 1. obs_bread_crate.glb (積み上がった木製パン木箱・ジャンプで越えられる障害物)
def build_bread_crate():
    clear_scene()
    m_wood = make_mat("WoodCrate", (0.68, 0.44, 0.22), roughness=0.72)
    m_wood_dark = make_mat("WoodDark", (0.48, 0.29, 0.13), roughness=0.78)
    m_bread = make_mat("BreadRoll", (0.82, 0.52, 0.20), roughness=0.65)
    m_paper = make_mat("CheckPaper", (0.96, 0.90, 0.78), roughness=0.85)

    def add_single_crate(z_base, yaw=0.0):
        # 底板
        create_box("CrateBase", (0.86, 0.60, 0.05), (0, 0, z_base + 0.025), m_wood_dark, (0, 0, yaw), 0.008)
        # 四隅の柱
        for sx in (-0.38, 0.38):
            for sy in (-0.25, 0.25):
                rx = sx * math.cos(yaw) - sy * math.sin(yaw)
                ry = sx * math.sin(yaw) + sy * math.cos(yaw)
                create_box("Post", (0.07, 0.07, 0.38), (rx, ry, z_base + 0.21), m_wood_dark, (0, 0, yaw), 0.008)
        # 横板2段
        for hz in (0.12, 0.30):
            for sy in (-0.28, 0.28):
                rx = -sy * math.sin(yaw)
                ry = sy * math.cos(yaw)
                create_box("SlatsFB", (0.86, 0.03, 0.11), (rx, ry, z_base + hz), m_wood, (0, 0, yaw), 0.006)
            for sx in (-0.41, 0.41):
                rx = sx * math.cos(yaw)
                ry = sx * math.sin(yaw)
                create_box("SlatsLR", (0.03, 0.58, 0.11), (rx, ry, z_base + hz), m_wood, (0, 0, yaw), 0.006)

    add_single_crate(0.0, 0.02)
    add_single_crate(0.40, -0.05)

    # 上の木箱の中に紙と丸パンを乗せる
    create_box("Liner", (0.74, 0.48, 0.02), (0, 0, 0.45), m_paper, (0, 0, -0.05), 0.005)
    for bx, by in [(-0.20, -0.10), (0.02, 0.08), (0.22, -0.08), (-0.15, 0.12)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.11, location=(bx, by, 0.55))
        b = bpy.context.active_object
        b.scale = (1.1, 0.95, 0.72)
        bpy.ops.object.transform_apply(scale=True)
        b.data.materials.append(m_bread)
        set_smooth(b)

    export_glb("obs_bread_crate.glb")


# 2. obs_aframe_sign.glb (パン屋さんのA型黒板スタンド看板)
def build_aframe_sign():
    clear_scene()
    m_frame = make_mat("OakFrame", (0.58, 0.34, 0.15), roughness=0.6)
    m_board = make_mat("ChalkBoard", (0.12, 0.16, 0.14), roughness=0.88)
    m_chalk_orange = make_mat("ChalkOrange", (0.98, 0.55, 0.18), roughness=0.9)
    m_chalk_cream = make_mat("ChalkCream", (0.98, 0.94, 0.82), roughness=0.9)
    m_brass = make_mat("Brass", (0.82, 0.65, 0.25), roughness=0.35, metallic=0.8)

    tilt = math.radians(15)
    for side in (-1, 1):
        y_off = side * 0.22
        rot_x = side * tilt
        # 外枠
        create_box(f"BoardFrame_{side}", (0.76, 0.05, 0.98), (0, y_off, 0.48), m_frame, (rot_x, 0, 0), 0.01)
        # 黒板面
        b_y = y_off + side * 0.026 * math.cos(tilt)
        b_z = 0.52 - 0.026 * math.sin(tilt)
        create_box(f"BoardFace_{side}", (0.64, 0.02, 0.72), (0, b_y, b_z), m_board, (rot_x, 0, 0), 0.003)
        # チョークイラスト風のパンアイコン＆横線
        c_y = y_off + side * 0.038 * math.cos(tilt)
        c_z = 0.63 - 0.038 * math.sin(tilt)
        create_box(f"ChalkTitle_{side}", (0.44, 0.01, 0.08), (0, c_y, c_z), m_chalk_orange, (rot_x, 0, 0), 0.002)
        create_box(f"ChalkLine1_{side}", (0.36, 0.01, 0.035), (0, c_y, c_z - 0.14), m_chalk_cream, (rot_x, 0, 0), 0.001)
        create_box(f"ChalkLine2_{side}", (0.28, 0.01, 0.035), (0, c_y, c_z - 0.23), m_chalk_cream, (rot_x, 0, 0), 0.001)

    # 蝶番チェーン/ヒンジ
    create_cyl("TopHinge", 0.025, 0.78, (0, 0, 0.95), m_brass, (0, math.radians(90), 0), verts=14)
    export_glb("obs_aframe_sign.glb")


# 3. obs_delivery_cart.glb (背の高い4段ベーカリーラック台車 - レーン移動で避ける)
def build_delivery_cart():
    clear_scene()
    m_steel = make_mat("Steel", (0.74, 0.76, 0.78), roughness=0.28, metallic=0.85)
    m_wheel = make_mat("Rubber", (0.12, 0.12, 0.13), roughness=0.85)
    m_tray = make_mat("BakingTray", (0.25, 0.27, 0.30), roughness=0.45, metallic=0.7)
    m_bread1 = make_mat("CrustGold", (0.85, 0.56, 0.20), roughness=0.6)
    m_bread2 = make_mat("CrustWarm", (0.72, 0.38, 0.15), roughness=0.65)

    # キャスター4つ
    for sx in (-0.36, 0.36):
        for sy in (-0.28, 0.28):
            create_cyl("Wheel", 0.065, 0.04, (sx, sy, 0.065), m_wheel, (0, math.radians(90), 0), verts=16)
            create_cyl("Pole", 0.022, 1.95, (sx, sy, 1.09), m_steel, (0, 0, 0), verts=12)

    # 下枠
    create_box("BottomFrame", (0.82, 0.66, 0.04), (0, 0, 0.14), m_steel, bevel=0.008)
    create_box("TopFrame", (0.82, 0.66, 0.04), (0, 0, 2.04), m_steel, bevel=0.008)

    # 4段のトレイと焼きたてパン
    for idx, tz in enumerate([0.45, 0.90, 1.35, 1.80]):
        create_box(f"Tray_{idx}", (0.74, 0.58, 0.03), (0, 0, tz), m_tray, bevel=0.005)
        mat_b = m_bread1 if idx % 2 == 0 else m_bread2
        for bx in (-0.22, 0.0, 0.22):
            for by in (-0.14, 0.14):
                bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=0.085, location=(bx, by, tz + 0.065))
                b = bpy.context.active_object
                b.scale = (1.1, 0.9, 0.65)
                bpy.ops.object.transform_apply(scale=True)
                b.data.materials.append(mat_b)
                set_smooth(b)

    export_glb("obs_delivery_cart.glb")


# 4. obs_flour_spill.glb (小麦粉の袋＋こぼれた白い小麦粉の山)
def build_flour_spill():
    clear_scene()
    m_sack = make_mat("FlourSack", (0.86, 0.78, 0.63), roughness=0.92)
    m_red_stripe = make_mat("RedStripe", (0.82, 0.22, 0.18), roughness=0.8)
    m_flour = make_mat("FlourPowder", (0.98, 0.97, 0.94), roughness=0.96)

    # 横倒しの小麦粉袋
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=12, radius=0.35, location=(-0.12, 0.06, 0.20))
    sack = bpy.context.active_object
    sack.scale = (1.25, 0.85, 0.62)
    sack.rotation_euler = (0.1, -0.15, 0.35)
    bpy.ops.object.transform_apply(scale=True)
    sack.data.materials.append(m_sack)
    set_smooth(sack)

    # 袋の赤い印
    create_box("SackLabel", (0.28, 0.20, 0.04), (-0.12, 0.06, 0.40), m_red_stripe, (0.1, -0.15, 0.35), 0.008)

    # こぼれた小麦粉の山（複数の平たい丸塊）
    piles = [(0.16, -0.10, 0.04, 0.36, 0.32, 0.10), (0.30, -0.18, 0.025, 0.22, 0.20, 0.06), (0.02, -0.22, 0.02, 0.24, 0.18, 0.05)]
    for i, (px, py, pz, sx, sy, sz) in enumerate(piles):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=1.0, location=(px, py, pz))
        p = bpy.context.active_object
        p.name = f"FlourPile_{i}"
        p.scale = (sx, sy, sz)
        bpy.ops.object.transform_apply(scale=True)
        p.data.materials.append(m_flour)
        set_smooth(p)

    export_glb("obs_flour_spill.glb")


# 5. obs_crow.glb (可愛いイタズラカラス)
def build_crow():
    clear_scene()
    m_black = make_mat("CrowBody", (0.08, 0.09, 0.12), roughness=0.55)
    m_wing = make_mat("CrowWing", (0.13, 0.14, 0.19), roughness=0.50)
    m_beak = make_mat("CrowBeak", (0.95, 0.68, 0.12), roughness=0.45)
    m_eye = make_mat("CrowEye", (1.0, 1.0, 1.0), roughness=0.2)
    m_pupil = make_mat("CrowPupil", (0.02, 0.02, 0.02), roughness=0.1)

    # 胴体
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=14, radius=0.26, location=(0, 0, 0.30))
    body = bpy.context.active_object
    body.scale = (0.9, 1.35, 0.92)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(m_black)
    set_smooth(body)

    # 頭
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.18, location=(0, -0.24, 0.44))
    head = bpy.context.active_object
    head.data.materials.append(m_black)
    set_smooth(head)

    # くちばし（前方 -Y 向き）
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.075, radius2=0.01, depth=0.22, location=(0, -0.45, 0.42), rotation=(math.radians(95), 0, 0))
    beak = bpy.context.active_object
    beak.data.materials.append(m_beak)
    set_smooth(beak)

    # 目
    for sx in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.045, location=(sx * 0.11, -0.34, 0.48))
        e = bpy.context.active_object
        e.data.materials.append(m_eye)
        set_smooth(e)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.025, location=(sx * 0.125, -0.37, 0.48))
        pu = bpy.context.active_object
        pu.data.materials.append(m_pupil)
        set_smooth(pu)

    # 広げた羽
    for sx in (-1, 1):
        create_box(f"Wing_{sx}", (0.48, 0.24, 0.05), (sx * 0.38, 0.02, 0.38), m_wing, (0.1, sx * -0.25, sx * 0.18), 0.015)

    # 尾羽
    create_box("Tail", (0.24, 0.28, 0.04), (0, 0.36, 0.26), m_wing, (-0.25, 0, 0), 0.01)

    export_glb("obs_crow.glb")


# 6. prop_street_lamp.glb (パン屋通りのレトロ街灯)
def build_street_lamp():
    clear_scene()
    m_iron = make_mat("CastIron", (0.16, 0.18, 0.20), roughness=0.45, metallic=0.75)
    m_glow = make_mat("WarmLamp", (1.0, 0.88, 0.55), roughness=0.15, emission=(1.0, 0.82, 0.42), emission_strength=2.2)

    create_cyl("LampBase", 0.20, 0.24, (0, 0, 0.12), m_iron, verts=12)
    create_cyl("LampPole", 0.065, 2.8, (0, 0, 1.52), m_iron, verts=12)
    create_box("LampArm", (0.55, 0.06, 0.06), (0.24, 0, 2.85), m_iron, bevel=0.01)
    # ランタン部分
    create_cyl("LanternCap", 0.20, 0.10, (0.48, 0, 2.78), m_iron, verts=8)
    create_cyl("LanternGlass", 0.14, 0.26, (0.48, 0, 2.60), m_glow, verts=8)
    create_cyl("LanternBottom", 0.12, 0.06, (0.48, 0, 2.45), m_iron, verts=8)

    export_glb("prop_street_lamp.glb")


# 7. prop_shop_house.glb (商店街の可愛い建物 - 並木通り用)
def build_shop_house():
    clear_scene()
    m_wall = make_mat("CreamWall", (0.96, 0.90, 0.78), roughness=0.85)
    m_roof = make_mat("TerracottaRoof", (0.82, 0.36, 0.22), roughness=0.75)
    m_awning1 = make_mat("AwningOrange", (0.92, 0.46, 0.15), roughness=0.7)
    m_awning2 = make_mat("AwningWhite", (0.98, 0.96, 0.92), roughness=0.7)
    m_window = make_mat("WindowGlow", (1.0, 0.92, 0.68), roughness=0.2, emission=(1.0, 0.86, 0.55), emission_strength=0.9)
    m_wood = make_mat("TrimWood", (0.45, 0.26, 0.12), roughness=0.65)

    # 本体
    create_box("BuildingBody", (2.6, 2.4, 3.2), (0, 0, 1.6), m_wall, bevel=0.03)
    # 屋根
    create_box("Roof", (2.8, 2.6, 0.55), (0, 0, 3.45), m_roof, bevel=0.04)
    # 窓（2階）
    for wx in (-0.65, 0.65):
        create_box(f"WinFrame_{wx}", (0.62, 0.10, 0.72), (wx, -1.21, 2.40), m_wood, bevel=0.01)
        create_box(f"WinGlass_{wx}", (0.50, 0.12, 0.60), (wx, -1.21, 2.40), m_window, bevel=0.005)
    # 1階ショーウィンドウ＆ドア
    create_box("ShopWindow", (1.35, 0.10, 1.05), (-0.42, -1.21, 0.75), m_window, bevel=0.01)
    create_box("ShopDoor", (0.65, 0.10, 1.45), (0.78, -1.21, 0.75), m_wood, bevel=0.01)
    # ストライプ日よけオーニング
    for i in range(6):
        ax = -1.0 + i * 0.40
        mat_a = m_awning1 if i % 2 == 0 else m_awning2
        create_box(f"Awning_{i}", (0.40, 0.68, 0.10), (ax, -1.50, 1.62), mat_a, (math.radians(22), 0, 0), 0.01)

    export_glb("prop_shop_house.glb")


if __name__ == "__main__":
    build_bread_crate()
    build_aframe_sign()
    build_delivery_cart()
    build_flour_spill()
    build_crow()
    build_street_lamp()
    build_shop_house()
    print("ALL DASH PROPS EXPORTED SUCCESSFULLY!")
