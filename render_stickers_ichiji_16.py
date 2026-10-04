import bpy
import math
import mathutils
import os

BLEND_FILE = r"C:\Users\akeer.AKERU\OneDrive\Desktop\純くん一時保存.blend"
OUT_BASE = r"C:\Users\akeer.AKERU\unity\Pukumuku2\temp_blend_frames_ichiji_16"
os.makedirs(OUT_BASE, exist_ok=True)

# 1. 非表示オブジェクトのレンダリング無効化
for obj in bpy.data.objects:
    if obj.hide_get():
        obj.hide_render = True

# 2. 胸のテキスト「PUKU MUKU」を胴体にペアレント（胴体のアニメーションに完全追従）
text_obj = bpy.data.objects.get("テキスト")
body = bpy.data.objects.get("胴体")
if text_obj and body:
    mw = text_obj.matrix_world.copy()
    text_obj.parent = body
    text_obj.matrix_world = mw

# 3. 脚と足（靴）をメッシュ結合し、原点を股関節に設定（足の分離・浮きを100%物理的に根絶！）
r_leg = bpy.data.objects.get("右脚")
r_foot = bpy.data.objects.get("右足")
if r_leg and r_foot:
    bpy.context.view_layer.objects.active = r_leg
    r_leg.select_set(True)
    r_foot.select_set(True)
    bpy.ops.object.join()
    r_leg.select_set(False)
    max_z = max(v.co.z for v in r_leg.data.vertices)
    hip_world = r_leg.matrix_world @ mathutils.Vector((0, 0, max_z))
    bpy.context.scene.cursor.location = hip_world
    bpy.context.view_layer.objects.active = r_leg
    r_leg.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    r_leg.select_set(False)

l_leg = bpy.data.objects.get("左脚")
l_foot = bpy.data.objects.get("左足")
if l_leg and l_foot:
    bpy.context.view_layer.objects.active = l_leg
    l_leg.select_set(True)
    l_foot.select_set(True)
    bpy.ops.object.join()
    l_leg.select_set(False)
    max_z = max(v.co.z for v in l_leg.data.vertices)
    hip_world = l_leg.matrix_world @ mathutils.Vector((0, 0, max_z))
    bpy.context.scene.cursor.location = hip_world
    bpy.context.view_layer.objects.active = l_leg
    l_leg.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    l_leg.select_set(False)

# 4. 腕の原点を肩関節に設定（肩抜けゼロで腕・手・指が一体回転）
r_arm = bpy.data.objects.get("右腕")
if r_arm:
    max_z = max(v.co.z for v in r_arm.data.vertices)
    shoulder_world = r_arm.matrix_world @ mathutils.Vector((0, 0, max_z))
    bpy.context.scene.cursor.location = shoulder_world
    bpy.context.view_layer.objects.active = r_arm
    r_arm.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    r_arm.select_set(False)

l_arm = bpy.data.objects.get("左腕")
if l_arm:
    max_z = max(v.co.z for v in l_arm.data.vertices)
    shoulder_world = l_arm.matrix_world @ mathutils.Vector((0, 0, max_z))
    bpy.context.scene.cursor.location = shoulder_world
    bpy.context.view_layer.objects.active = l_arm
    l_arm.select_set(True)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    l_arm.select_set(False)

# 5. カメラセットアップ（320x270、透過RGBA）
cam = bpy.data.objects.get("Camera")
if not cam:
    cam_data = bpy.data.cameras.new("RenderCamera")
    cam = bpy.data.objects.new("RenderCamera", cam_data)
    bpy.context.collection.objects.link(cam)

bpy.context.scene.camera = cam
bpy.context.scene.render.resolution_x = 320
bpy.context.scene.render.resolution_y = 270
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.image_settings.color_mode = 'RGBA'

# 6. ワールド環境光とマルチライティング（全アングル・真横でも影で真っ黒にならず超鮮明！）
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new('World')
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.92, 0.92, 0.96, 1.0)
    bg.inputs['Strength'].default_value = 0.85

for light in [o for o in bpy.data.objects if o.type == 'LIGHT']:
    bpy.data.objects.remove(light)

def add_sun(name, energy, rot_deg):
    sun = bpy.data.lights.new(name, 'SUN')
    sun.energy = energy
    sun.use_shadow = False
    o = bpy.data.objects.new(name, sun)
    o.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    bpy.context.collection.objects.link(o)

add_sun('SunFront', 3.2, (90, 0, -90)) # 正面 (-X)
add_sun('SunRight', 3.6, (90, 0, 0))   # 右横 (+Y) -> 05番のサイドビューを強力に明るく！
add_sun('SunLeft', 2.4, (90, 0, 180))  # 左横 (-Y)
add_sun('SunTop', 2.5, (45, 0, -45))   # 上から

# 7. カメラ注視点エンプティ
target = bpy.data.objects.get("CamTarget")
if not target:
    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)

cam.constraints.clear()
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 全16種類の個別最適化カメラ構図（純くんを下半分／左右に配置し、上部・対角に広大な文字＆イラスト空間を確保！）
CAM_SETUPS = [
    { "cam_pos": (-11.2, 0.9, 2.7),  "tgt_pos": (0.0, 0.3, 2.4), "lens": 38 },  # 01 こんにちは (右下立ち、左上文字・クロワッサン空き)
    { "cam_pos": (-11.5, 0.0, 3.0),  "tgt_pos": (0.0, 0.0, 2.2), "lens": 38 },  # 02 ありがとう (下部中央お辞儀、上部文字・左右ハート空き)
    { "cam_pos": (-10.8, -0.8, 2.6), "tgt_pos": (0.0, -0.3, 2.3), "lens": 38 }, # 03 了解 (右下親指、左側大文字・バゲット空き)
    { "cam_pos": (-11.0, -0.8, 2.6), "tgt_pos": (0.0, -0.3, 2.3), "lens": 38 }, # 04 NO (右下「×」、左側NO・青ざめ空き)
    { "cam_pos": (-0.8, 10.2, 1.6),  "tgt_pos": (0.0, 0.0, 1.4), "lens": 38 },  # 05 急ぎます (真横サイド疾走全身収容、左上文字、左下大土煙)
    { "cam_pos": (-11.5, 0.0, 2.8),  "tgt_pos": (0.0, 0.0, 2.2), "lens": 38 },  # 06 お願い (下部合掌ピョンピョン、上部文字空き)
    { "cam_pos": (-10.8, -0.8, 2.6), "tgt_pos": (0.0, -0.3, 2.3), "lens": 38 }, # 07 ひとやすみ (右下お茶、左側文字・大マグカップ空き)
    { "cam_pos": (-12.5, 0.0, 2.6),  "tgt_pos": (0.0, 0.0, 1.8), "lens": 38 },  # 08 やったー (大ジャンプでも画面内すっぽり、最上部文字)
    { "cam_pos": (-10.8, 0.8, 2.6),  "tgt_pos": (0.0, 0.3, 2.3), "lens": 38 },  # 09 うーん (左下考え中、右上文字・思考フキダシ空き)
    { "cam_pos": (-11.5, 0.0, 2.8),  "tgt_pos": (0.0, 0.0, 2.2), "lens": 38 },  # 10 プンプン (下部仁王立ち、上部文字・両肩上怒りマーク)
    { "cam_pos": (-11.0, -0.7, 2.7), "tgt_pos": (0.0, -0.2, 2.1), "lens": 38 }, # 11 ごめんなさい (右下うなだれ、左上文字・頭上雨雲空き)
    { "cam_pos": (-11.5, 0.0, 2.6),  "tgt_pos": (0.0, 0.0, 2.0), "lens": 38 },  # 12 いいですね (中央ステップ、上部文字・左右音符空き)
    { "cam_pos": (-10.8, -0.8, 2.6), "tgt_pos": (0.0, -0.3, 2.3), "lens": 38 }, # 13 よろしく (右下敬礼、左側文字・クロワッサン空き)
    { "cam_pos": (-11.5, -0.9, 2.6), "tgt_pos": (0.0, -0.4, 2.0), "lens": 38 }, # 14 いらっしゃいませ (右下お辞儀、左側独立食パン看板空き！)
    { "cam_pos": (-10.8, -0.6, 2.4), "tgt_pos": (0.0, -0.2, 2.0), "lens": 38 }, # 15 おやすみなさい (右下手枕、左上文字・上部三日月空き)
    { "cam_pos": (-11.0, 0.8, 2.6),  "tgt_pos": (0.0, 0.3, 2.2), "lens": 38 },  # 16 がんばります (左下拳突き上げ、右上メラメラ炎空き)
]

# 各パーツの初期Transform退避
PARTS_NAMES = ['パン', '顔', '胴体', '右腕', '左腕', '右脚', '左脚']
initial_transforms = {}
parts = {}
for name in PARTS_NAMES:
    obj = bpy.data.objects.get(name)
    if obj:
        parts[name] = obj
        initial_transforms[name] = {
            'loc': obj.location.copy(),
            'rot': obj.rotation_euler.copy(),
            'scale': obj.scale.copy()
        }

def reset_transforms():
    for name, init in initial_transforms.items():
        obj = parts.get(name)
        if obj:
            obj.location = init['loc'].copy()
            obj.rotation_euler = init['rot'].copy()
            obj.scale = init['scale'].copy()
    # 腕のベースポーズ: 自然に体側に下ろした状態(x=0)を基準とする
    r_arm = parts.get('右腕')
    l_arm = parts.get('左腕')
    if r_arm: r_arm.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')
    if l_arm: l_arm.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

def apply_pose(s_idx, t):
    reset_transforms()
    pi = math.pi
    face = parts.get('顔')
    body = parts.get('胴体')
    r_arm = parts.get('右腕')
    l_arm = parts.get('左腕')
    r_leg = parts.get('右脚')
    l_leg = parts.get('左脚')

    # 【重要幾何学ルール】
    # 正面は -X。
    # 前傾・うなだれ・下向き頷き・前への腕脚振り = Y軸回転マイナス (負)！
    # 後傾・仰け反り・胸を張る・後ろへの腕脚振り = Y軸回転プラス (正)！
    # 腕の左右（冠状面）の開閉・手振り = X軸回転！

    if s_idx == 0:
        # 01. こんにちは！ (右手を斜め上に掲げ、X軸回転で画面左右に可愛くバイバイ！)
        wave = math.sin(t * 4 * pi)
        if r_arm:
            # X軸回転で左右に手振り
            r_arm.rotation_euler.x = math.radians(130) + math.radians(22) * wave
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(10)
        if face:
            # 首コテン
            face.rotation_euler.x = math.radians(14) * math.sin(t * 2 * pi)
        if body:
            body.location.z += 0.04 * abs(wave)

    elif s_idx == 1:
        # 02. ありがとうございます (前半: 前傾で深々とお辞儀ペコリ、後半: パッと顔を上げて両手を広げ感謝！)
        cycle = t
        if cycle < 0.5:
            bow = math.sin(cycle * 2 * pi)
            if body:
                body.rotation_euler.y = -math.radians(35) * bow # 前傾お辞儀！
            if face:
                face.rotation_euler.y = -math.radians(15) * bow # 下を向く！
            if r_arm and l_arm:
                r_arm.rotation_euler.y = -math.radians(20) * bow
                l_arm.rotation_euler.y = -math.radians(20) * bow
        else:
            spread = math.sin((cycle - 0.5) * 2 * pi)
            if body:
                body.rotation_euler.y = math.radians(6) * spread # 少し胸を張る
                body.location.z += 0.05 * spread
            if r_arm and l_arm:
                r_arm.rotation_euler.x = math.radians(40) * spread
                l_arm.rotation_euler.x = -math.radians(40) * spread

    elif s_idx == 2:
        # 03. 了解です！ (右腕突き出し親指グッ、力強く2回頷く！)
        nod = abs(math.sin(t * 4 * pi))
        if body:
            body.rotation_euler.y = -math.radians(8) # わずかに前傾
        if r_arm:
            r_arm.rotation_euler.y = -math.radians(75) # 前に突き出す！
            r_arm.rotation_euler.x = math.radians(15)
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(30) # 腰付近
            l_arm.rotation_euler.y = -math.radians(15)
        if face:
            face.rotation_euler.y = -math.radians(18) * nod # 前＝下向き頷き！

    elif s_idx == 3:
        # 04. NO (両腕を胸の前で「×」交差、首を激しくイヤイヤ振る！)
        shake = math.sin(t * 4 * pi)
        if face:
            face.rotation_euler.z = math.radians(25) * shake # 左右イヤイヤ
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(35)
            r_arm.rotation_euler.y = -math.radians(45) # 前で交差
            l_arm.rotation_euler.x = -math.radians(35)
            l_arm.rotation_euler.y = -math.radians(45)

    elif s_idx == 4:
        # 05. 急ぎます！ (サイドビュー前傾猛ダッシュ！靴の分離ゼロ＆超明るい！)
        run = math.sin(t * 4 * pi)
        if body:
            body.rotation_euler.y = -math.radians(20) # 前傾姿勢！
            body.location.z += 0.12 * abs(run)
        if r_leg:
            r_leg.rotation_euler.y = -math.radians(50) * run
        if l_leg:
            l_leg.rotation_euler.y = math.radians(50) * run
        if r_arm:
            r_arm.rotation_euler.y = -math.radians(55) * run
        if l_arm:
            l_arm.rotation_euler.y = math.radians(55) * run

    elif s_idx == 5:
        # 06. お願いします (胸の前で両手合掌、ピョンピョン跳ねる！)
        jump = abs(math.sin(t * 4 * pi))
        if body:
            body.location.z += 0.15 * jump
            body.rotation_euler.y = -math.radians(4) * jump
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(25)
            r_arm.rotation_euler.y = -math.radians(65)
            l_arm.rotation_euler.x = -math.radians(25)
            l_arm.rotation_euler.y = -math.radians(65)
        if face:
            face.rotation_euler.y = -math.radians(8) * jump

    elif s_idx == 6:
        # 07. ひとやすみ (お茶を差し出すように優しく両手を差し出し、ほっこり揺れ)
        breathe = math.sin(t * 2 * pi)
        if body:
            body.rotation_euler.y = -math.radians(8) * breathe # 優しい会釈！
        if r_arm and l_arm:
            r_arm.rotation_euler.y = -math.radians(45) - math.radians(6) * breathe
            r_arm.rotation_euler.x = math.radians(15)
            l_arm.rotation_euler.y = -math.radians(45) - math.radians(6) * breathe
            l_arm.rotation_euler.x = -math.radians(15)
        if face:
            face.rotation_euler.x = math.radians(12) * breathe

    elif s_idx == 7:
        # 08. やったー！ (しゃがんでから大ジャンプ！両手両足を大の字！)
        jump_phase = t
        if jump_phase < 0.25:
            squat = math.sin(jump_phase * 4 * pi)
            if body:
                body.location.z += -0.12 * squat
            if r_leg and l_leg:
                r_leg.rotation_euler.y = math.radians(20) * squat
                l_leg.rotation_euler.y = math.radians(20) * squat
        else:
            jp = math.sin((jump_phase - 0.25) / 0.75 * pi)
            if body:
                body.location.z += 0.55 * jp
            if r_arm and l_arm:
                r_arm.rotation_euler.x = math.radians(145) * jp
                l_arm.rotation_euler.x = -math.radians(145) * jp
            if r_leg and l_leg:
                r_leg.rotation_euler.x = math.radians(20) * jp
                l_leg.rotation_euler.x = -math.radians(20) * jp

    elif s_idx == 8:
        # 09. うーん… (右手をあごに当て、首を左右に傾げて考え込む)
        think = math.sin(t * 2 * pi)
        if r_arm:
            r_arm.rotation_euler.y = -math.radians(80) # あごへ
            r_arm.rotation_euler.x = math.radians(20)
        if l_arm:
            l_arm.rotation_euler.y = -math.radians(40) # 肘支え
            l_arm.rotation_euler.x = -math.radians(25)
        if face:
            face.rotation_euler.x = math.radians(16) * think # 首傾げ
            face.rotation_euler.y = -math.radians(8) * math.cos(t * 2 * pi)

    elif s_idx == 9:
        # 10. プンプン！ (両手腰で仁王立ち、左右の足を交互に足踏みドンドン！)
        stomp = math.sin(t * 4 * pi)
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(40)
            r_arm.rotation_euler.y = -math.radians(15)
            l_arm.rotation_euler.x = -math.radians(40)
            l_arm.rotation_euler.y = -math.radians(15)
        lift_r = max(0, stomp)
        lift_l = max(0, -stomp)
        if r_leg: r_leg.rotation_euler.y = -math.radians(35) * lift_r
        if l_leg: l_leg.rotation_euler.y = -math.radians(35) * lift_l
        if body:
            body.location.z += 0.05 * abs(stomp)
            body.rotation_euler.y = -math.radians(6) # 少し前傾

    elif s_idx == 10:
        # 11. ごめんなさい… (ガックリうなだれて小さくプルプル震える)
        shiver = math.sin(t * 16 * pi)
        slump = abs(math.sin(t * 2 * pi))
        if body:
            body.rotation_euler.y = -math.radians(30) - math.radians(4) * slump # 前傾！
            body.location.z += -0.10
            body.location.x += 0.01 * shiver
        if face:
            face.rotation_euler.y = -math.radians(25) # ガックリ下を向く！
        if r_arm and l_arm:
            r_arm.rotation_euler.y = -math.radians(15)
            l_arm.rotation_euler.y = -math.radians(15)

    elif s_idx == 11:
        # 12. いいですね！ (左右にステップを踏みながら両手ウェーブダンス)
        step = math.sin(t * 4 * pi)
        if body:
            body.location.y += 0.16 * step
            body.rotation_euler.x = math.radians(12) * step
            body.location.z += 0.06 * abs(step)
        if r_leg: r_leg.rotation_euler.x = math.radians(15) * step
        if l_leg: l_leg.rotation_euler.x = -math.radians(15) * step
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(105) + math.radians(25) * step
            l_arm.rotation_euler.x = -math.radians(105) - math.radians(25) * step

    elif s_idx == 12:
        # 13. よろしくです (右手を額にピッとおいてキリッと敬礼ポーズ)
        salute = math.sin(t * 2 * pi)
        if body:
            body.rotation_euler.y = -math.radians(6)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(65)
            r_arm.rotation_euler.y = -math.radians(60) # 額へ敬礼！
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(20)
        if face:
            face.rotation_euler.x = math.radians(6) * salute

    elif s_idx == 13:
        # 14. いらっしゃいませ！ (両手を広げてお店の前でお出迎えお辞儀)
        bow = max(0, math.sin(t * 2 * pi))
        if body:
            body.rotation_euler.y = -math.radians(32) * bow # 前傾お辞儀！
        if face:
            face.rotation_euler.y = -math.radians(15) * bow # 下向き
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(45)
            r_arm.rotation_euler.y = -math.radians(35) * bow
            l_arm.rotation_euler.x = -math.radians(45)
            l_arm.rotation_euler.y = -math.radians(35) * bow

    elif s_idx == 14:
        # 15. おやすみなさい (手枕ポーズ、首コテンですやすや眠る)
        sleep = math.sin(t * 2 * pi)
        if body:
            body.location.z += 0.04 * sleep
        if r_arm:
            r_arm.rotation_euler.x = math.radians(35)
            r_arm.rotation_euler.y = -math.radians(60) # 手枕
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(15)
            l_arm.rotation_euler.y = -math.radians(45)
        if face:
            face.rotation_euler.x = math.radians(22) # 首コテン

    elif s_idx == 15:
        # 16. がんばります！ (右拳を力強く天高く突き上げる熱血ガッツポーズ！)
        punch = math.sin(t * 4 * pi)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(160) + math.radians(15) * punch # 天高く拳！
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(25)
            l_arm.rotation_euler.y = -math.radians(30)
        if body:
            body.location.z += 0.08 * abs(punch)
            body.rotation_euler.y = -math.radians(8) # 前傾気合
        if r_leg and l_leg:
            r_leg.rotation_euler.x = math.radians(15)
            l_leg.rotation_euler.x = -math.radians(15)

# レンダリング実行
print("=== STARTING COMPLETE RE-RENDERING OF 16 STICKERS ===")
TOTAL_FRAMES = 20

for s_idx in range(16):
    print(f"Rendering Sticker {s_idx+1}/16...")
    s_dir = os.path.join(OUT_BASE, f"sticker_{s_idx+1:02d}")
    os.makedirs(s_dir, exist_ok=True)
    
    c_info = CAM_SETUPS[s_idx]
    cam.location = c_info["cam_pos"]
    cam.data.lens = c_info["lens"]
    target.location = c_info["tgt_pos"]
    bpy.context.view_layer.update()
    
    for f in range(TOTAL_FRAMES):
        t = f / TOTAL_FRAMES
        apply_pose(s_idx, t)
        bpy.context.view_layer.update()
        
        frame_path = os.path.join(s_dir, f"frame_{f:02d}.png")
        bpy.context.scene.render.filepath = frame_path
        bpy.ops.render.render(write_still=True)

reset_transforms()
print("✓ All 320 frames for 16 stickers rendered successfully with corrected rotation axes and lighting!")

