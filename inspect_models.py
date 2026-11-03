import bpy
from mathutils import Vector
from pathlib import Path

root = Path(r'C:\Users\akeer.AKERU\pukumuku\unity-mobile\Assets\Resources')
for path in [root/'Shop'/'PukumukuBakery.fbx',root/'Breads'/'bread_melon.fbx',root/'Breads'/'bread_croissant.fbx',root/'Breads'/'bread_loaf.fbx',root/'Breads'/'bread_burger.fbx']:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(path))
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    coords = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
    print('MODEL',path.name, 'MIN', tuple(round(min(v[i] for v in coords), 3) for i in range(3)), 'MAX', tuple(round(max(v[i] for v in coords), 3) for i in range(3)), 'COUNT', len(meshes))
