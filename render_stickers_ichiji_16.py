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

# ライティング
for light in [o for o in bpy.data.objects if o.type == 'LIGHT']:
    bpy.data.objects.remove(light)

sun_main = bpy.data.lights.new("SunMain", 'SUN')
sun_main.energy = 4.2
sun_main.use_shadow = False
o_main = bpy.data.objects.new("SunMain", sun_main)
o_main.rotation_euler = (math.radians(90), 0, math.radians(-90))
bpy.context.collection.objects.link(o_main)

sun_top = bpy.data.lights.new("SunTop", 'SUN')
sun_top.energy = 2.0
sun_top.use_shadow = False
o_top = bpy.data.objects.new("SunTop", sun_top)
o_top.rotation_euler = (math.radians(45), math.radians(20), math.radians(-65))
bpy.context.collection.objects.link(o_top)

# カメラ注視点エンプティ
target = bpy.data.objects.get("CamTarget")
if not target:
    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)

cam.constraints.clear()
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 全16種類の個別最適化カメラ構図
CAM_SETUPS = [
    { "cam_pos": (-6.8, 1.2, 2.9), "tgt_pos": (0.0, 0.0, 3.1), "lens": 40 },
    { "cam_pos": (-6.8, 0.0, 4.8), "tgt_pos": (0.0, 0.0, 2.4), "lens": 40 },
    { "cam_pos": (-6.0, -1.4, 2.6), "tgt_pos": (0.0, -0.3, 2.8), "lens": 36 },
    { "cam_pos": (-6.6, 0.0, 3.4), "tgt_pos": (0.0, 0.0, 3.5), "lens": 40 },
    { "cam_pos": (-3.2, 8.2, 1.6), "tgt_pos": (-0.2, 0.0, 1.5), "lens": 36 },
    { "cam_pos": (-6.2, 0.0, 2.2), "tgt_pos": (0.0, 0.0, 3.0), "lens": 40 },
    { "cam_pos": (-6.4, 0.0, 2.9), "tgt_pos": (0.0, 0.0, 3.0), "lens": 40 },
    { "cam_pos": (-10.0, 0.0, 1.2), "tgt_pos": (0.0, 0.0, 2.4), "lens": 36 },
    { "cam_pos": (-6.5, -1.2, 2.9), "tgt_pos": (0.0, 0.0, 3.0), "lens": 40 },
    { "cam_pos": (-7.5, 0.0, 1.8), "tgt_pos": (0.0, 0.0, 1.9), "lens": 38 },
    { "cam_pos": (-6.8, 0.0, 4.4), "tgt_pos": (0.0, 0.0, 2.4), "lens": 40 },
    { "cam_pos": (-8.5, 0.0, 1.8), "tgt_pos": (0.0, 0.0, 1.8), "lens": 38 },
    { "cam_pos": (-6.4, 0.0, 3.0), "tgt_pos": (0.0, 0.0, 3.0), "lens": 40 },
    { "cam_pos": (-7.0, 0.0, 2.4), "tgt_pos": (0.0, 0.0, 2.4), "lens": 40 },
    { "cam_pos": (-6.2, 0.0, 3.0), "tgt_pos": (0.0, 0.0, 3.0), "lens": 40 },
    { "cam_pos": (-6.5, -1.0, 1.5), "tgt_pos": (0.0, 0.0, 2.4), "lens": 36 },
]

# 各パーツの初期Transform退避
PARTS_NAMES = ['パン', '顔', '胴体', '右腕', '左腕', '右脚', '左脚', '右手', '左手']
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
    # 腕のベースポーズ: Tポーズ(x=90/270)を脱却し、自然に体側に下ろした状態(x=0)を基準とする！
    r_arm = parts.get('右腕')
    l_arm = parts.get('左腕')
    if r_arm: r_arm.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')
    if l_arm: l_arm.rotation_euler = mathutils.Euler((0, 0, 0), 'XYZ')

def apply_pose(s_idx, t):
    reset_transforms()
    pi = math.pi
    bread = parts.get('パン')
    face = parts.get('顔')
    body = parts.get('胴体')
    r_arm = parts.get('右腕')
    l_arm = parts.get('左腕')
    r_leg = parts.get('右脚')
    l_leg = parts.get('左脚')

    if s_idx == 0:
        # 01. こんにちは！ (右手を高く上げてバイバイ手振り、頭コテンコテン)
        wave = math.sin(t * 4 * pi)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(135)
            r_arm.rotation_euler.y = math.radians(25) * wave
        if face:
            face.rotation_euler.x = math.radians(12) * math.sin(t * 2 * pi)
        if body:
            body.location.z += 0.08 * abs(wave)

    elif s_idx == 1:
        # 02. ありがとう！ (腰から深々とお辞儀し、パッと顔を上げて両手を開く)
        cycle = t
        if cycle < 0.5:
            bow = math.sin(cycle * 2 * pi)
            if body: body.rotation_euler.y = math.radians(38) * bow
            if r_arm and l_arm:
                r_arm.rotation_euler.y = math.radians(25) * bow
                l_arm.rotation_euler.y = math.radians(25) * bow
        else:
            spread = math.sin((cycle - 0.5) * 2 * pi)
            if body:
                body.rotation_euler.y = -math.radians(8) * spread
                body.location.z += 0.06 * spread
            if r_arm and l_arm:
                r_arm.rotation_euler.x = math.radians(45) * spread
                r_arm.rotation_euler.y = math.radians(20) * spread
                l_arm.rotation_euler.x = -math.radians(45) * spread
                l_arm.rotation_euler.y = math.radians(20) * spread

    elif s_idx == 2:
        # 03. OK！ (前に身を乗り出して右腕突き出し親指グッ、力強く2回頷く)
        nod = abs(math.sin(t * 4 * pi))
        if body:
            body.rotation_euler.y = math.radians(12)
            body.location.x += -0.15 * nod
        if r_arm:
            r_arm.rotation_euler.y = math.radians(75)
            r_arm.rotation_euler.x = math.radians(15)
        if face:
            face.rotation_euler.y = math.radians(16) * nod

    elif s_idx == 3:
        # 04. NO (両腕を胸の前で交差して「×」、頭を激しくイヤイヤ振る)
        shake = math.sin(t * 4 * pi)
        if face:
            face.rotation_euler.z = math.radians(26) * shake
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(45)
            r_arm.rotation_euler.x = math.radians(35) + math.radians(8) * shake
            l_arm.rotation_euler.y = math.radians(45)
            l_arm.rotation_euler.x = -math.radians(35) - math.radians(8) * shake

    elif s_idx == 4:
        # 05. 急ぎます！ (前傾猛ダッシュ！結合メッシュにより靴の分離ゼロ！)
        run = math.sin(t * 4 * pi)
        if body:
            body.rotation_euler.y = math.radians(18)
            body.location.z += 0.14 * abs(run)
        if r_leg:
            r_leg.rotation_euler.y = math.radians(50) * run
        if l_leg:
            l_leg.rotation_euler.y = -math.radians(50) * run
        if r_arm:
            r_arm.rotation_euler.y = math.radians(55) * run
        if l_arm:
            l_arm.rotation_euler.y = -math.radians(55) * run

    elif s_idx == 5:
        # 06. いただきます♪ (胸の前で合掌、ピョンピョン跳ねる)
        jump = abs(math.sin(t * 4 * pi))
        if body: body.location.z += 0.16 * jump
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(65)
            r_arm.rotation_euler.x = math.radians(25)
            l_arm.rotation_euler.y = math.radians(65)
            l_arm.rotation_euler.x = -math.radians(25)
        if face:
            face.rotation_euler.y = -math.radians(12) * jump

    elif s_idx == 6:
        # 07. お疲れさまです (お茶を差し出すように優しく両手を前に差し出す)
        breathe = math.sin(t * 2 * pi)
        if body:
            body.rotation_euler.y = math.radians(6) * breathe
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(45) + math.radians(6) * breathe
            r_arm.rotation_euler.x = math.radians(15)
            l_arm.rotation_euler.y = math.radians(45) + math.radians(6) * breathe
            l_arm.rotation_euler.x = -math.radians(15)
        if face:
            face.rotation_euler.x = math.radians(14) * breathe

    elif s_idx == 7:
        # 08. やったー！ (しゃがんでから大ジャンプ！両手両足を大の字！)
        jump_phase = t
        if jump_phase < 0.25:
            squat = math.sin(jump_phase * 4 * pi)
            if body: body.location.z += -0.15 * squat
            if r_leg and l_leg:
                r_leg.rotation_euler.y = -math.radians(20) * squat
                l_leg.rotation_euler.y = -math.radians(20) * squat
        else:
            jp = math.sin((jump_phase - 0.25) / 0.75 * pi)
            if body: body.location.z += 0.65 * jp
            if r_arm and l_arm:
                r_arm.rotation_euler.x = math.radians(145) * jp
                l_arm.rotation_euler.x = -math.radians(145) * jp
            if r_leg and l_leg:
                r_leg.rotation_euler.x = math.radians(22) * jp
                l_leg.rotation_euler.x = -math.radians(22) * jp

    elif s_idx == 8:
        # 09. 考え中... (右手をあごに当て、左手肘支え、うーんと首を回す)
        think = math.sin(t * 2 * pi)
        if r_arm:
            r_arm.rotation_euler.y = math.radians(80)
            r_arm.rotation_euler.x = math.radians(25)
        if l_arm:
            l_arm.rotation_euler.y = math.radians(45)
            l_arm.rotation_euler.x = -math.radians(30)
        if face:
            face.rotation_euler.x = math.radians(16) * think
            face.rotation_euler.y = math.radians(8) * math.cos(t * 2 * pi)

    elif s_idx == 9:
        # 10. プンプン！ (両手腰で仁王立ち、左右の足を交互に足踏みドンドン！)
        stomp = math.sin(t * 4 * pi)
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(45)
            r_arm.rotation_euler.y = math.radians(15)
            l_arm.rotation_euler.x = -math.radians(45)
            l_arm.rotation_euler.y = math.radians(15)
        lift_r = max(0, stomp)
        lift_l = max(0, -stomp)
        if r_leg: r_leg.rotation_euler.y = math.radians(35) * lift_r
        if l_leg: l_leg.rotation_euler.y = math.radians(35) * lift_l
        if body:
            body.location.z += 0.06 * abs(stomp)
            body.rotation_euler.y = math.radians(4) * stomp

    elif s_idx == 10:
        # 11. ごめんなさい... (ガックリうなだれて小さく震える)
        shiver = math.sin(t * 12 * pi)
        slump = abs(math.sin(t * 2 * pi))
        if body:
            body.rotation_euler.y = math.radians(28) + math.radians(4) * slump
            body.location.z += -0.10
            body.location.x += 0.01 * shiver
        if face:
            face.rotation_euler.y = math.radians(22)
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(15)
            l_arm.rotation_euler.y = math.radians(15)

    elif s_idx == 11:
        # 12. イエーイ！ (左右にステップを踏みながら両手ウェーブダンス)
        step = math.sin(t * 4 * pi)
        if body:
            body.location.y += 0.20 * step
            body.rotation_euler.x = math.radians(15) * step
            body.location.z += 0.08 * abs(step)
        if r_leg: r_leg.rotation_euler.x = math.radians(18) * step
        if l_leg: l_leg.rotation_euler.x = -math.radians(18) * step
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(110) + math.radians(30) * step
            l_arm.rotation_euler.x = -math.radians(110) - math.radians(30) * step

    elif s_idx == 12:
        # 13. よろしく！ (右手を額にピッとおいてキリッと敬礼ポーズ)
        salute = math.sin(t * 2 * pi)
        if body:
            body.rotation_euler.y = -math.radians(6)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(65)
            r_arm.rotation_euler.y = math.radians(60)
        if face:
            face.rotation_euler.y = -math.radians(8) + math.radians(4) * salute

    elif s_idx == 13:
        # 14. いらっしゃいませ！ (両手を広げてお店の前でお出迎えお辞儀)
        bow = math.sin(t * 2 * pi)
        if bow < 0: bow = 0
        if body: body.rotation_euler.y = math.radians(30) * bow
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(45)
            r_arm.rotation_euler.y = math.radians(35) * bow
            l_arm.rotation_euler.x = -math.radians(45)
            l_arm.rotation_euler.y = math.radians(35) * bow

    elif s_idx == 14:
        # 15. おやすみなさい (手枕ポーズ、首コテンですやすや眠る)
        sleep = math.sin(t * 2 * pi)
        if body:
            body.location.z += 0.04 * sleep
        if r_arm:
            r_arm.rotation_euler.x = math.radians(35)
            r_arm.rotation_euler.y = math.radians(60)
        if l_arm:
            r_arm.rotation_euler.x = -math.radians(15)
            l_arm.rotation_euler.y = math.radians(45)
        if face:
            face.rotation_euler.x = math.radians(24)

    elif s_idx == 15:
        # 16. 一発逆転！ (右拳を天高く突き上げる熱血ガッツポーズ！)
        punch = math.sin(t * 4 * pi)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(160) + math.radians(15) * punch
        if l_arm:
            l_arm.rotation_euler.x = -math.radians(30)
            l_arm.rotation_euler.y = math.radians(35)
        if body:
            body.location.z += 0.12 * abs(punch)
            body.rotation_euler.y = -math.radians(10)
        if r_leg and l_leg:
            r_leg.rotation_euler.x = math.radians(15)
            l_leg.rotation_euler.x = -math.radians(15)

# レンダリング実行
print("=== STARTING FULL 16-STICKER RENDERING ON 純くん一時保存.blend ===")
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
print("✓ All 320 frames for 16 stickers rendered successfully from 純くん一時保存.blend!")
