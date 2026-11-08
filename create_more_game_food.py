"""Create editable Blender food and game-ready GLB/thumbnail pairs."""
import math
import random
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'models' / 'catch_breads'
OUT.mkdir(parents=True, exist_ok=True)
RNG = random.Random(6291)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=.55):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = roughness
    return m

crust = material('きつね色の焼き皮', (.77,.37,.12))
cream = material('クリーム', (.96,.81,.43), .43)
dark = material('チョコレート', (.23,.095,.065), .35)
green = material('ピクルスの皮', (.14,.38,.09))
pickle = material('ピクルスの果肉', (.58,.71,.27), .47)
pumpkin = material('かぼちゃクリーム', (.82,.38,.075), .42)
potato = material('じゃがいもの白い果肉', (.89,.75,.49))
purple = material('さつまいもの紫皮', (.28,.105,.20))
yam = material('さつまいもの黄身', (.94,.73,.29))
seed = material('クッキー生地', (.94,.75,.41))
sausage = material('焼いたソーセージ', (.62,.13,.055), .35)
mark = material('焼き目', (.26,.075,.035))

def shape(name, pos, scale, mat, segments=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=pos)
    o=bpy.context.object
    o.name=name
    o.scale=scale
    o.data.materials.append(mat)
    for face in o.data.polygons: face.use_smooth=True
    return o

def bun(label='焼きたてパン'):
    return shape(label,(0,0,-.025),(.43,.35,.21),crust)

def torus(label, pos, major, minor, mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=10, major_radius=major,
                                    minor_radius=minor, location=pos)
    o=bpy.context.object
    o.name=label
    o.data.materials.append(mat)
    for face in o.data.polygons: face.use_smooth=True
    return o

def cream_melon():
    bun()
    shape('メロン皮',(0,0,.065),(.41,.34,.16),seed)
    for sign in [-1,1]:
        for d in [-.18,0,.18]:
            strip=shape('格子の焼き溝',(d,0,.211),(.018,.28,.012),crust,24,12)
            strip.rotation_euler[2]=sign*.55
    shape('カスタードのぞき窓',(0,-.30,.054),(.16,.055,.04),cream)

def potato_bread():
    bun('じゃがいもぱんの丸い生地')
    shape('中央のじゃがいも',(0,0,.162),(.24,.19,.105),potato)
    for x,y in [(-.14,.07),(.13,-.08),(0,.02)]:
        shape('こんがりチーズ粒',(x,y,.248),(.045,.032,.013),seed,16,8)

def chocolate_bread():
    bun('チョコぱんの生地')
    for i in range(5):
        x=-.29+i*.145
        shape('ひと口チョコの列',(x,0,.166),(.09,.18,.05),dark,32,16)
    for x in [-.24,-.08,.08,.24]:
        shape('つやのあるチョコ筋',(x,-.07,.216),(.018,.12,.007),cream,16,8)

def pumpkin_montblanc():
    bun('かぼちゃモンブランの土台')
    for ring in range(6):
        rad=.23-ring*.027
        z=.157+ring*.023
        torus('かぼちゃクリームの絞り', (0,0,z), rad,.024,pumpkin)
    shape('かぼちゃの飾り',(0,0,.305),(.06,.055,.03),pumpkin,24,12)
    shape('かぼちゃの種',(0,0,.33),(.028,.05,.008),green,20,10)

def sweet_potato():
    bun('さつまいもぱんの土台')
    for x in [-.19,0,.19]:
        shape('紫のさつまいも皮',(x,0,.165),(.11,.20,.075),purple,32,16)
        shape('ほくほくした黄色い断面',(x,-.028,.204),(.083,.146,.057),yam,32,16)
    for i in range(10):
        x,y=RNG.uniform(-.28,.28),RNG.uniform(-.18,.18)
        shape('ごま',(x,y,.235),(.007,.013,.004),seed,8,4)

def pickles():
    for x,y in [(-.23,-.09),(.03,.10),(.24,-.07)]:
        shape('波形ピクルスの皮',(x,y,0),(.18,.14,.042),green,48,16)
        shape('透けるピクルスの断面',(x,y,.027),(.159,.12,.026),pickle,48,16)
        for n in range(5):
            a=n*math.tau/5
            shape('白い種',(x+.065*math.cos(a),y+.045*math.sin(a),.051),
                  (.013,.007,.003),seed,10,6)

def grilled_sausage():
    shape('一本焼きソーセージ',(0,0,0),(.48,.18,.11),sausage,64,24)
    for x in [-.29,-.14,.01,.16,.30]:
        stripe=shape('香ばしい焼き筋',(x,-.036,.10),(.014,.12,.006),mark,12,8)
        stripe.rotation_euler[2]=-.35

items = {
    'bread_cream_melon': (cream_melon, OUT),
    'bread_potato': (potato_bread, OUT),
    'bread_chocolate': (chocolate_bread, OUT),
    'bread_pumpkin': (pumpkin_montblanc, OUT),
    'bread_sweet_potato': (sweet_potato, OUT),
    'item_pickles': (pickles, ROOT/'models'),
    'item_grilled_sausage': (grilled_sausage, ROOT/'models'),
}
collections={}
for key,(build,directory) in items.items():
    collection=bpy.data.collections.new(key)
    bpy.context.scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[key]
    build()
    collections[key]=collection
    bpy.ops.object.select_all(action='DESELECT')
    for o in collection.objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(directory/(key+'.glb')),use_selection=True)

scene=bpy.context.scene
camera_data=bpy.data.cameras.new('図鑑カメラ')
camera=bpy.data.objects.new('図鑑カメラ',camera_data)
scene.collection.objects.link(camera)
scene.camera=camera
camera_data.type='ORTHO'
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=320
scene.render.resolution_y=320
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='WEBP'
scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=True
scene.display.shading.color_type='MATERIAL'
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.show_cavity=True
scene.view_settings.view_transform='Standard'
scene.view_settings.exposure=.55
for key,collection in collections.items():
    for other in collections.values(): other.hide_render=(other!=collection)
    verts=[o.matrix_world@Vector(c) for o in collection.objects for c in o.bound_box]
    left,right=min(v.x for v in verts),max(v.x for v in verts)
    near,far=min(v.y for v in verts),max(v.y for v in verts)
    bottom,top=min(v.z for v in verts),max(v.z for v in verts)
    center=Vector(((left+right)/2,(near+far)/2,(bottom+top)/2))
    camera_data.ortho_scale=max(right-left,far-near)*1.35
    camera.location=center+Vector((.5,-2,2.1))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    directory=items[key][1]
    scene.render.filepath=str(directory/(key+'.webp'))
    bpy.ops.render.render(write_still=True)
    collection.hide_render=False

for i,collection in enumerate(collections.values()):
    for o in collection.objects:
        o.location.x+=(i%4-1.5)*1.3
        o.location.y+=(i//4)*1.3
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models'/'more_game_food.blend'),compress=True)
