"""Create an editable copy of the shop, remove floating door panel, ground floor, add oven, and export."""
import bpy
import bmesh
from pathlib import Path

project = Path(__file__).resolve().parent
source_shop = Path(r"C:\Users\akeer.AKERU\pukumuku\unity-mobile\Assets\Resources\Shop\PukumukuBakery.fbx")
source_oven = Path(r"C:\Users\akeer.AKERU\pukumuku\unity-mobile\Assets\Resources\Workstations\Work_Oven.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)

# 1. Import Shop FBX
bpy.ops.import_scene.fbx(filepath=str(source_shop))

# 2. Delete the floating central door infill panel
# It was located between X in [-0.45, 0.45], Y < -2.3, Z in [1.5, 3.3]
for obj in bpy.data.objects:
    if obj.type == "MESH":
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        verts_to_delete = []
        for v in bm.verts:
            world_pos = obj.matrix_world @ v.co
            if abs(world_pos.x) < 0.45 and world_pos.y < -2.3 and 1.5 < world_pos.z < 3.3:
                verts_to_delete.append(v)
        if verts_to_delete:
            bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
            bm.to_mesh(obj.data)
            obj.data.update()
        bm.free()

# Helper to create colored box panels
def make_box(name, location, dimensions, color, roughness=0.72):
    mat = bpy.data.materials.new(name + ' material')
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1)
        bsdf.inputs['Roughness'].default_value = roughness
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new('Soft edges', 'BEVEL')
    bevel.width = .025
    bevel.segments = 2
    obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return obj

WARM_PLASTER = (0.91, 0.79, 0.61)
HONEY_OAK = (0.36, 0.17, 0.075)
TERRACOTTA = (0.76, 0.58, 0.36)

# Upper gap backing: closes opening between awning beam and showcase tops
make_box('Upper facade gap backing', (0, -2.40, 3.42), (4.80, .18, .58), WARM_PLASTER, roughness=0.72)

# Back kitchen wall (behind oven and counter)
make_box('Kitchen rear wall', (0, 2.50, 1.80), (4.80, .18, 3.60), WARM_PLASTER, roughness=0.72)

# 3. Grounding floor between counter and front base to eliminate floating gap
# Grounding slab and tiles
make_box('Storefront Grounding Slab', (0, -1.30, 0.12), (4.80, 2.40, 0.24), TERRACOTTA, roughness=0.68)
for col in range(4):
    for row in range(3):
        x = -1.80 + col * 1.20
        y = -2.30 + row * 0.90
        make_box(f'Front tile {col}_{row}', (x, y, 0.25), (1.14, 0.84, 0.02), TERRACOTTA, roughness=0.60)

# 4. Import and position the authentic Bakery Work_Oven in kitchen background
bpy.ops.import_scene.fbx(filepath=str(source_oven))
for obj in bpy.context.selected_objects:
    # Scale and center in the kitchen view behind counter
    obj.location.x += 0.10
    obj.location.y += 1.45
    obj.location.z += 0.15
    obj.scale = (0.68, 0.68, 0.68)

# Save blend and export GLB
models_dir = project / 'models'
models_dir.mkdir(parents=True, exist_ok=True)
blend_path = models_dir / 'pukumuku_shop_refined.blend'
glb_path = models_dir / 'pukumuku_blender_shop.glb'

bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format='GLB')
print(f"EXPORT SHOP GLB DONE: {glb_path.name}")

