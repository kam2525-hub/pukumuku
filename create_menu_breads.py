"""Build original, editable Pukumuku menu-inspired bread models and game GLBs.

Run with Blender: blender -b -t 4 --python create_menu_breads.py
The undated hand-drawn menu supplied by the owner is a visual reference; the
official site is the current source for names also listed there. No prices are
copied into the game.
"""
import math
import random
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'models' / 'catch_breads'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def mat(name, rgb, rough=.58):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    bs = m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    output = m.node_tree.nodes.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(bs.outputs['BSDF'], output.inputs['Surface'])
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = rough
    return m

M = {
    'bread': mat('焼きたての山吹色', (.72,.34,.095)),
    'light': mat('薄焼きの生地', (.92,.65,.27)),
    'toast': mat('香ばしい焼き目', (.43,.16,.045)),
    'flour': mat('小麦粉', (.94,.83,.63)),
    'cream': mat('カスタード', (.99,.78,.35), .4),
    'chocolate': mat('チョコレート', (.22,.072,.036), .35),
    'red': mat('トマト・ジャム', (.77,.13,.065), .42),
    'green': mat('青菜・ハーブ', (.16,.42,.10)),
    'cheese': mat('溶けたチーズ', (.99,.59,.07), .44),
    'egg': mat('白身', (.96,.89,.72)),
    'yellow': mat('卵黄', (.99,.46,.025), .3),
    'apple': mat('りんご', (.76,.17,.055)),
    'purple': mat('紫いもの皮', (.34,.13,.24)),
    'yam': mat('さつまいもの中身', (.97,.73,.28)),
    'pumpkin': mat('かぼちゃ', (.87,.36,.045)),
    'meat': mat('焼いたパティ', (.39,.13,.055)),
    'sausage': mat('ソーセージ', (.68,.15,.065), .39),
    'fish': mat('サクサク衣', (.82,.49,.16)),
    'raisin': mat('レーズン', (.27,.11,.20)),
    'white': mat('白いクリーム', (.98,.94,.78)),
}

def oval(name, loc, scale, material, seg=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    o.data.materials.append(M[material])
    if material in ('bread','light'):
        for v in o.data.vertices:
            wobble = 1 + .022*math.sin(v.co.x*13+v.co.y*7)*math.sin(v.co.z*11+v.co.x*5)
            v.co *= wobble
    for p in o.data.polygons: p.use_smooth = True
    return o

def ring(name, loc, radius, tube, material):
    bpy.ops.mesh.primitive_torus_add(major_segments=28, minor_segments=7,
        major_radius=radius, minor_radius=tube, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(M[material])
    for p in o.data.polygons: p.use_smooth = True
    return o

def bun(label='ふっくらした生地', material='bread', long=False):
    return oval(label, (0,0,0), (.46 if long else .40,.27 if long else .36,.17), material)

def seeds(label='トッピング', material='flour', count=8, z=.15, seed=0):
    rng = random.Random(seed)
    for _ in range(count):
        x,y = rng.uniform(-.29,.29),rng.uniform(-.20,.20)
        oval(label,(x,y,z+rng.uniform(0,.025)),(.018,.009,.006),material,10,6)

def score_lines(count=3, material='toast'):
    for i in range(count):
        x=(i-(count-1)/2)*.17
        o=oval('焼き込みの切れ目',(x,-.015,.154),(.022,.19,.009),material,12,8)
        o.rotation_euler[2]=-.27

def roll(material='bread', long=False):
    bun(material=material,long=long)
    for x in (-.22,0,.22):
        oval('ちぎり目のある生地',(x,0,.035),(.17,.29,.14),material)

def bread_slice(raisin=False):
    def block(name, loc, scale, material, bevel):
        bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
        o=bpy.context.object
        o.name=name
        o.dimensions=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        b=o.modifiers.new('やわらかい角','BEVEL')
        b.width=bevel
        b.segments=3
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.modifier_apply(modifier=b.name)
        o.data.materials.append(M[material])
        for face in o.data.polygons:face.use_smooth=True
    block('角食パンの香ばしい耳',(0,0,0),(.76,.46,.48),'toast',.11)
    block('小麦のふんわりした断面',(0,-.245,0),(.69,.038,.40),'flour',.03)
    if raisin:
        rng=random.Random(4)
        for _ in range(13):
            x,z=rng.uniform(-.25,.25),rng.uniform(-.14,.14)
            oval('断面のレーズン',(x,-.275,z),(.028,.008,.021),'raisin',10,6)

def croissant(chocolate=False, sausage=False):
    for i,x in enumerate((-.30,-.17,0,.17,.30)):
        width=.10 if abs(x)>.25 else .17
        oval('折り重なったパイ生地',(x,0,.01),(.15,width,.13),'bread')
        oval('層の焼き色',(x,-.055,.075),(.12,.028,.04),'light',14,8)
    if chocolate:
        for x in (-.23,-.08,.08,.23): oval('チョコの流れ',(x,0,.145),(.025,.13,.012),'chocolate')
    if sausage: oval('顔を出したソーセージ',(0,-.25,.02),(.30,.075,.065),'sausage')

def danish(kind):
    for i in range(4): ring('パイ生地の渦巻き',(0,0,-.045+i*.033),.30-i*.046,.034,'bread')
    oval('フィリング',(0,0,.09),(.21,.20,.05),kind)
    if kind=='apple':
        for x in (-.12,0,.12): oval('薄切りりんご',(x,0,.14),(.06,.14,.018),'apple')
    if kind=='yam': seeds('砂糖粒','white',8,.15,22)

def savory(kind):
    bun(long=kind in ('noodle','sausage','pizza','avocado','tuna'))
    oval('具材を載せるくぼみ',(0,0,.147),(.30,.22,.04),'light')
    if kind=='tomato':
        for x in (-.14,.14): oval('トマトの輪切り',(x,0,.188),(.12,.13,.025),'red')
        seeds('ハーブ','green',7,.215,2)
    elif kind=='mexican':
        oval('ピリ辛トマトソース',(0,0,.195),(.23,.18,.035),'red')
        for x,y in ((-.16,-.06),(-.04,.08),(.13,-.04)):
            oval('メキシカンの具',(x,y,.23),(.07,.06,.04),'meat')
        seeds('香草','green',6,.26,19)
    elif kind=='curry':
        oval('カレーの中身',(0,0,.16),(.20,.17,.047),'meat')
        seeds('カリッとしたパン粉','flour',13,.2,3)
    elif kind in ('corn','corn_cheese'):
        for x in (-.18,-.06,.06,.18):
            for y in (-.09,.07): oval('つぶつぶコーン',(x,y,.21),(.036,.043,.031),'yellow',12,8)
        if kind=='corn_cheese': seeds('チーズ','cheese',7,.24,6)
    elif kind=='egg_salad':
        for x in (-.12,0,.12): oval('たまごサラダ',(x,0,.205),(.09,.12,.058),'egg')
        seeds('黄身','yellow',8,.25,8)
    elif kind=='noodle':
        for i in range(8):
            y=-.16+i*.045
            oval('焼きそばの麺',(0,y,.205),(.28,.012,.016),'toast',12,6)
        seeds('青のり','green',8,.24,7)
    elif kind=='gratin':
        oval('クリーミーなグラタン',(0,0,.20),(.24,.19,.055),'white')
        seeds('こんがりチーズ','cheese',8,.25,7)
    elif kind=='pizza':
        oval('トマトソース',(0,0,.185),(.29,.20,.035),'red')
        seeds('ブロッコリー','green',8,.225,5)
        seeds('チーズ','cheese',7,.24,11)
    elif kind=='avocado':
        for x in (-.18,.0,.18): oval('えび',(x,-.04,.21),(.08,.08,.043),'red')
        for x in (-.12,.12): oval('アボカド',(x,.08,.22),(.10,.07,.035),'green')
    elif kind=='tuna':
        for x in (-.16,0,.16): oval('ツナ',(x,0,.21),(.10,.14,.045),'fish')
        seeds('マヨネーズ','white',7,.25,12)
    elif kind=='sausage':
        oval('長いソーセージ',(0,0,.21),(.35,.09,.07),'sausage')
        for x in (-.20,0,.20): oval('ケチャップ',(x,-.04,.265),(.04,.07,.009),'red')

def sweet(kind):
    bun()
    if kind=='anko':
        oval('こしあんのぞき窓',(0,-.28,.09),(.16,.06,.065),'raisin')
        seeds('黒ごま','raisin',5,.17,1)
    elif kind=='pumpkin':
        oval('かぼちゃあん',(0,0,.16),(.23,.22,.08),'pumpkin')
        for i in range(5): ring('かぼちゃの絞り',(0,0,.17+i*.025),.20-i*.035,.016,'pumpkin')
    elif kind=='lemon':
        oval('レモンのアイシング',(0,0,.16),(.30,.27,.04),'white')
        for x in (-.13,0,.13): oval('レモンピール',(x,0,.20),(.03,.12,.012),'yellow')
    elif kind=='fruit_cheese':
        oval('フルーツクリームチーズ',(0,0,.17),(.25,.20,.065),'white')
        for x,y,c in ((-.12,0,'red'),(.1,.08,'apple'),(.05,-.12,'green')):
            oval('フルーツ',(x,y,.23),(.06,.055,.035),c)
    elif kind=='raisin':
        oval('南台のクリーム',(0,-.02,.165),(.28,.20,.08),'white')
        seeds('レーズン','raisin',13,.22,13)
    elif kind=='cream':
        oval('たっぷりカスタード',(0,-.27,.08),(.17,.065,.07),'cream')
        score_lines(2)
    elif kind=='choco_cream':
        oval('チョコクリーム',(0,-.27,.08),(.17,.065,.07),'chocolate')
        for x in (-.18,0,.18): oval('チョコがけ',(x,0,.16),(.03,.19,.009),'chocolate')
    elif kind=='apple_cinnamon':
        for x in (-.16,0,.16): oval('煮りんご',(x,0,.18),(.09,.16,.045),'apple')
        score_lines(2,'toast')
    elif kind=='salt_anko':
        oval('あんこ',(0,0,.16),(.23,.20,.05),'raisin')
        seeds('塩の結晶','white',7,.21,9)
    elif kind=='melon':
        oval('サクサクのビスケット皮',(0,0,.085),(.38,.33,.13),'light')
        for x in (-.19,0,.19):
            o=oval('メロン模様',(x,0,.198),(.015,.30,.006),'flour',12,8)
            o.rotation_euler[2]=.5

def burger(kind):
    oval('下のバンズ',(0,0,-.16),(.37,.32,.08),'bread')
    oval('シャキシャキレタス',(0,0,-.07),(.38,.32,.027),'green')
    oval('パティまたは具',(0,0,-.015),(.33,.28,.06),'fish' if kind=='fish' else 'meat')
    if kind in ('cheese','pukumuku'): oval('とろけるチーズ',(0,0,.048),(.36,.30,.018),'cheese')
    if kind=='ginger': seeds('しょうが','light',9,.05,14)
    if kind=='teriyaki': oval('照り焼きソース',(0,0,.065),(.32,.27,.024),'toast')
    if kind=='pukumuku':
        for x in (-.14,.14): oval('ピクルス',(x,0,.09),(.09,.08,.02),'green')
    oval('ふっくらした上のバンズ',(0,0,.18),(.39,.33,.16),'bread')
    seeds('白ごま','flour',10,.32,16)

def animal(kind):
    bun('動物ビスケット','light')
    if kind=='frog':
        for x in (-.21,.21): oval('カエルの目',(x,-.14,.17),(.09,.09,.09),'green')
        for x in (-.21,.21): oval('黒目',(x,-.205,.20),(.026,.012,.03),'chocolate')
        oval('まっちゃ色の顔',(0,-.02,.14),(.28,.25,.04),'green')
    else:
        for x in (-.20,.20): oval('パンダの耳',(x,0,.18),(.11,.11,.05),'chocolate')
        for x in (-.13,.13): oval('パンダの目',(x,-.18,.19),(.07,.035,.045),'chocolate')
        oval('パンダの鼻',(0,-.26,.15),(.045,.02,.025),'chocolate')

def mini(kind):
    bun('ひと口サイズのパン')
    if kind=='an': oval('あんのぞき窓',(0,-.28,.06),(.14,.035,.045),'raisin')
    elif kind=='cheese': oval('チーズの小窓',(0,0,.16),(.17,.14,.04),'cheese')
    elif kind=='roll': score_lines(2)

ITEMS = {
 'bread_shokupan': ('食ぱん',lambda:bread_slice()),
 'bread_raisin_shokupan': ('レーズン食ぱん',lambda:bread_slice(True)),
 'bread_petit_roll': ('プチロール',lambda:mini('roll')),
 'bread_petit_an': ('プチあん',lambda:mini('an')),
 'bread_petit_cheese': ('プチチーズ',lambda:mini('cheese')),
 'bread_wiener_croissant': ('ウインナークロワッサン',lambda:croissant(sausage=True)),
 'bread_tomato': ('トマトぱん',lambda:savory('tomato')),
 'bread_curry': ('カレーパン',lambda:savory('curry')),
 'bread_cheese_corn': ('チーズコーンマヨ',lambda:savory('corn_cheese')),
 'bread_corn_mayo': ('コーンマヨネーズ',lambda:savory('corn')),
 'bread_egg_salad': ('たまごサラダ',lambda:savory('egg_salad')),
 'bread_yakisoba': ('やきそばぱん',lambda:savory('noodle')),
 'bread_gratin': ('グラタン',lambda:savory('gratin')),
 'bread_choco_danish': ('チョコデニッシュ',lambda:danish('chocolate')),
 'bread_apple_danish': ('りんごデニッシュ',lambda:danish('apple')),
 'bread_sweet_potato_montblanc': ('さつまいもモンブラン',lambda:danish('yam')),
 'bread_bacon_egg_pie': ('ベーコンエッグパイ',lambda:(danish('egg'),oval('目玉焼きの黄身',(0,0,.16),(.09,.09,.045),'yellow'),oval('ベーコン',(-.13,0,.12),(.25,.035,.015),'meat'))),
 'bread_mexican': ('メキシカンぱん',lambda:savory('mexican')),
 'bread_cinnamon_apple': ('シナモンアップル',lambda:sweet('apple_cinnamon')),
 'bread_pumpkin_bun': ('かぼちゃぱん',lambda:sweet('pumpkin')),
 'bread_koshian': ('こしあんぱん',lambda:sweet('anko')),
 'bread_shrimp_avocado': ('えびアボカドのグラタン',lambda:savory('avocado')),
 'bread_tuna': ('ツナぱん',lambda:savory('tuna')),
 'bread_broccoli_pizza': ('ブロッコリーピザ',lambda:savory('pizza')),
 'bread_fish_burger': ('さばかつバーガー',lambda:burger('fish')),
 'bread_ginger_burger': ('しょうがバーガー',lambda:burger('ginger')),
 'bread_teriyaki_burger': ('てりやきバーガー',lambda:burger('teriyaki')),
 'bread_cheese_burger': ('チーズバーガー',lambda:burger('cheese')),
 'bread_choco_cream': ('チョコクリーム',lambda:sweet('choco_cream')),
 'bread_lemon': ('レモンぱん',lambda:sweet('lemon')),
 'bread_fruit_cheese': ('フルーツチーズ',lambda:sweet('fruit_cheese')),
 'bread_nandai_raisin': ('南台レーズンサンド',lambda:sweet('raisin')),
 'bread_raisin_caramel_danish': ('レーズンキャラメルデニッシュ',lambda:(danish('toast'),seeds('レーズン','raisin',10,.14,18))),
 'bread_salt_anko': ('塩あんぱん',lambda:sweet('salt_anko')),
 'bread_frog_matcha': ('カエルまっちゃビスケット',lambda:animal('frog')),
 'bread_panda_choco': ('パンダチョコビスケット',lambda:animal('panda')),
}

collections={}
for key,(label,build) in ITEMS.items():
    c=bpy.data.collections.new(key)
    bpy.context.scene.collection.children.link(c)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[key]
    build()
    collections[key]=c
    bpy.ops.object.select_all(action='DESELECT')
    for o in c.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/(key+'.glb')),use_selection=True,
        export_draco_mesh_compression_enable=False)
    print('EXPORTED',key,label,flush=True)

scene=bpy.context.scene
camera_data=bpy.data.cameras.new('図鑑用カメラ')
camera=bpy.data.objects.new('図鑑用カメラ',camera_data)
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
for key,c in collections.items():
    for other in collections.values():other.hide_render=(other!=c)
    verts=[o.matrix_world@Vector(v) for o in c.objects for v in o.bound_box]
    lo=Vector(tuple(min(v[i] for v in verts) for i in range(3)))
    hi=Vector(tuple(max(v[i] for v in verts) for i in range(3)))
    center=(lo+hi)/2
    camera_data.ortho_scale=max(hi.x-lo.x,hi.y-lo.y)*1.4
    camera.location=center+Vector((.5,-2,2.1))
    camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/(key+'.webp'))
    bpy.ops.render.render(write_still=True)
    c.hide_render=False

for i,c in enumerate(collections.values()):
    for o in c.objects:
        o.location.x+=(i%7-3)*1.25
        o.location.y+=(i//7)*1.20
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'models'/'menu_breads.blend'),compress=True)
