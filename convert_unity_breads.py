"""Convert and generate all bread meshes for Pukumuku catch game."""
import bpy
from pathlib import Path

project = Path(__file__).resolve().parent
source = Path(r"C:\Users\akeer.AKERU\pukumuku\unity-mobile\Assets\Resources\Breads")
models_dir = project / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# 1. Direct conversions from existing multi-material Unity models
bread_mapping = [
    ("bread_burger", "bread_burger_unity"),
    ("bread_loaf", "bread_cream_unity"),        # Cream bun with scoring
    ("bread_egg", "bread_egg_unity"),          # Egg pastry
    ("bread_mushroom", "bread_mushroom_unity"), # Mushroom pastry
    ("bread_negi", "bread_negi_unity"),        # Scallion / Negi pastry
    ("bread_cocoa", "bread_cocoa_unity"),      # Cocoa / Chocolate bun
    ("bread_melon", "bread_melon_unity"),
    ("bread_croissant", "bread_croissant_unity"),
]

for src_name, dst_name in bread_mapping:
    src_file = source / f"{src_name}.fbx"
    if not src_file.exists():
        print(f"Skipping missing {src_file}")
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(src_file))
    dst_file = models_dir / f"{dst_name}.glb"
    bpy.ops.export_scene.gltf(filepath=str(dst_file), export_format='GLB')
    print(f"Exported: {dst_file.name}")

# 2. Generate Real Burnt Bread (コゲパン) based on bread_loaf shape with charred crust & toast marks
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(source / "bread_loaf.fbx"))

# Create charred charcoal material
burnt_charcoal = bpy.data.materials.new("Burnt Charcoal")
burnt_charcoal.use_nodes = True
bsdf = burnt_charcoal.node_tree.nodes.get("Principled BSDF")
if bsdf:
    # Very dark charred brown-black
    bsdf.inputs["Base Color"].default_value = (0.09, 0.07, 0.06, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.92

burnt_crack = bpy.data.materials.new("Burnt Crust Score")
burnt_crack.use_nodes = True
bsdf_crack = burnt_crack.node_tree.nodes.get("Principled BSDF")
if bsdf_crack:
    # Deep ash black
    bsdf_crack.inputs["Base Color"].default_value = (0.03, 0.02, 0.02, 1.0)
    bsdf_crack.inputs["Roughness"].default_value = 0.98

for obj in bpy.data.objects:
    if obj.type == "MESH":
        obj.data.materials.clear()
        if "score" in obj.name.lower():
            obj.data.materials.append(burnt_crack)
        else:
            obj.data.materials.append(burnt_charcoal)

burnt_dst = models_dir / "bread_burnt_unity.glb"
bpy.ops.export_scene.gltf(filepath=str(burnt_dst), export_format='GLB')
print(f"Exported newly designed burnt bread: {burnt_dst.name}")
