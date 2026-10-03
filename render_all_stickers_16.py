import bpy
import math
import os

OUT_BASE = r"C:\Users\akeer.AKERU\unity\Pukumuku2\temp_blend_frames_16"
os.makedirs(OUT_BASE, exist_ok=True)

# 1. 不要・非表示オブジェクトの非表示化
for obj in bpy.data.objects:
    if obj.hide_get():
        obj.hide_render = True

# 2. テキストのメッシュ化
text_obj = bpy.data.objects.get("テキスト")
if text_obj and text_obj.type == 'FONT':
    bpy.context.view_layer.objects.active = text_obj
    text_obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    text_obj.select_set(False)

# 3. 足・脚は幾何学ピボット補正で動かすため、標準のクリーンな親子関係を維持

# 4. カメラセットアップ（解像度: 320x270）
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

# 5. 影ノイズなしのフラット＆クリーンなライティング
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

# カメラ注視用エンプティ
target = bpy.data.objects.get("CamTarget")
if not target:
    target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(target)

cam.constraints.clear()
track = cam.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

# 全16種類のカメラ構図設定（文字被りを防ぎ、足先まで美しく収まるベストな配置！）
CAM_SETUPS_16 = [
    # 01. こんにちは！ (斜めバストアップ、文字スペース上部)
    { "cam_pos": (-6.8, 1.2, 3.0), "tgt_pos": (0, 0, 3.2), "lens": 42 },
    # 02. ありがとう！ (見下ろしハイアングルでお辞儀)
    { "cam_pos": (-7.0, 0.0, 5.0), "tgt_pos": (0, 0, 2.5), "lens": 42 },
    # 03. OK！ (右斜め前から手元アップ、首取れ修正)
    { "cam_pos": (-6.2, -1.5, 2.7), "tgt_pos": (0, -0.4, 2.9), "lens": 38 },
    # 04. NO (正面顔アップ、首振り枠切れ防止マージン)
    { "cam_pos": (-6.6, 0.0, 3.4), "tgt_pos": (0, 0, 3.5), "lens": 40 },
    # 05. 急ぎます！ (斜め25度サイドビュー疾走、顔の表情も走る足の開きも完全連動！)
    { "cam_pos": (-3.2, 8.2, 1.6), "tgt_pos": (-0.2, 0.0, 1.5), "lens": 36 },
    # 06. いただきます♪ (やや見上げバストアップ)
    { "cam_pos": (-6.2, 0.0, 2.4), "tgt_pos": (0, 0, 3.2), "lens": 42 },
    # 07. お疲れさまです (癒やしバストアップ)
    { "cam_pos": (-6.5, 0.0, 3.1), "tgt_pos": (0, 0, 3.2), "lens": 42 },
    # 08. やったー！ (全身見上げ大ジャンプ)
    { "cam_pos": (-10.5, 0.0, 1.4), "tgt_pos": (0, 0, 2.4), "lens": 38 },
    # 09. 考え中... (斜めバストアップ、あご手)
    { "cam_pos": (-6.6, -1.2, 3.0), "tgt_pos": (0, 0, 3.1), "lens": 40 },
    # 10. プンプン！ (腰手・足踏み、全身〜腰上が収まるミディアム)
    { "cam_pos": (-7.8, 0.0, 2.0), "tgt_pos": (0, 0, 2.0), "lens": 38 },
    # 11. 悲しい... (見下ろしハイアングル、肩落とし)
    { "cam_pos": (-6.8, 0.0, 4.6), "tgt_pos": (0, 0, 2.6), "lens": 40 },
    # 12. イエーイ！ (ダンス、全身フルショット)
    { "cam_pos": (-8.5, 0.0, 1.8), "tgt_pos": (0, 0, 1.8), "lens": 38 },
    # 13. ポカ〜ン (正面ミディアム、呆然)
    { "cam_pos": (-6.6, 0.0, 3.1), "tgt_pos": (0, 0, 3.1), "lens": 40 },
    # 14. いらっしゃいませ！ (丁寧なお辞儀、ウエストアップ)
    { "cam_pos": (-7.0, 0.0, 2.6), "tgt_pos": (0, 0, 2.6), "lens": 40 },
    # 15. ブルブル... (寒さで震えるバストアップ)
    { "cam_pos": (-6.5, 0.0, 3.0), "tgt_pos": (0, 0, 3.0), "lens": 40 },
    # 16. 一発逆転！ (力強いあおりローアングル、ガッツポーズ)
    { "cam_pos": (-6.5, -1.0, 1.6), "tgt_pos": (0, 0, 2.5), "lens": 36 },
]

# 各パーツの初期Transformを退避
PARTS_NAMES = ['パン', '顔', 'Esfera UV.001', '胴体', '右腕', '左腕', '右脚', '左脚', '右足', '左足', '右手', '左手']
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

def apply_pose(stamp_idx, t):
    reset_transforms()
    pi = math.pi
    bread = parts.get('パン')
    face = parts.get('顔')
    esfera = parts.get('Esfera UV.001')
    body = parts.get('胴体')
    r_arm = parts.get('右腕')
    l_arm = parts.get('左腕')
    r_leg = parts.get('右脚')
    l_leg = parts.get('左脚')
    r_hand = parts.get('右手')
    l_hand = parts.get('左手')
    r_foot = parts.get('右足')
    l_foot = parts.get('左足')

    if stamp_idx == 0:
        # 01. こんにちは！
        wave = math.sin(t * 4 * pi)
        if body: body.location.z += 0.10 * abs(wave)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(135) + math.radians(25) * wave
            r_arm.rotation_euler.y = math.radians(-15)
        if bread and face:
            bread.rotation_euler.x = math.radians(10) * math.sin(t * 2 * pi)
            face.rotation_euler.x = math.radians(10) * math.sin(t * 2 * pi)

    elif stamp_idx == 1:
        # 02. ありがとう！
        bow = math.sin(t * 2 * pi)
        if bow < 0: bow = 0
        if body: body.rotation_euler.y = math.radians(40) * bow
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(35) * bow
            l_arm.rotation_euler.y = math.radians(35) * bow

    elif stamp_idx == 2:
        # 03. OK！ (首取れ防止修正)
        nod = abs(math.sin(t * 4 * pi))
        if r_arm:
            r_arm.rotation_euler.y = math.radians(85)
            r_arm.rotation_euler.x = math.radians(18)
        if bread and face:
            bread.rotation_euler.y = math.radians(14) * nod
            face.rotation_euler.y = math.radians(14) * nod
            bread.location.x += -0.05 * nod
            face.location.x += -0.05 * nod
        if body: body.location.z += 0.05 * nod

    elif stamp_idx == 3:
        # 04. NO (枠切れ防止修正)
        shake = math.sin(t * 4 * pi)
        if bread and face:
            bread.rotation_euler.z = math.radians(24) * shake
            face.rotation_euler.z = math.radians(24) * shake
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(30)
            l_arm.rotation_euler.y = math.radians(30)
            r_arm.rotation_euler.x = math.radians(20) * shake
            l_arm.rotation_euler.x = math.radians(20) * shake

    elif stamp_idx == 4:
        # 05. 急ぎます！ (股関節・肩関節ピボット幾何補正で靴・手先まで完全連動の颯爽ダッシュ！)
        run = math.sin(t * 4 * pi)
        if body:
            body.rotation_euler.y = math.radians(18)
            body.location.z += 0.14 * abs(run)

        # 右脚＆右足（靴）
        ang_r = math.radians(50) * run
        if r_leg:
            r_leg.rotation_euler.y = ang_r
            r_leg.location.x += -math.sin(ang_r) * 1.0
            r_leg.location.z += (1.0 - math.cos(ang_r)) * 1.0
        if r_foot:
            r_foot.rotation_euler.y = ang_r
            r_foot.location.x += -math.sin(ang_r) * 2.18
            r_foot.location.z += (1.0 - math.cos(ang_r)) * 2.18

        # 左脚＆左足（逆相）
        ang_l = -math.radians(50) * run
        if l_leg:
            l_leg.rotation_euler.y = ang_l
            l_leg.location.x += -math.sin(ang_l) * 1.0
            l_leg.location.z += (1.0 - math.cos(ang_l)) * 1.0
        if l_foot:
            l_foot.rotation_euler.y = ang_l
            l_foot.location.x += -math.sin(ang_l) * 2.18
            l_foot.location.z += (1.0 - math.cos(ang_l)) * 2.18

        # 腕の前後振り（肩関節ピボット）
        ang_arm_r = -math.radians(55) * run
        if r_arm:
            r_arm.rotation_euler.y = ang_arm_r
            r_arm.location.x += -math.sin(ang_arm_r) * 1.0
            r_arm.location.z += (1.0 - math.cos(ang_arm_r)) * 1.0
        ang_arm_l = math.radians(55) * run
        if l_arm:
            l_arm.rotation_euler.y = ang_arm_l
            l_arm.location.x += -math.sin(ang_arm_l) * 1.0
            l_arm.location.z += (1.0 - math.cos(ang_arm_l)) * 1.0

    elif stamp_idx == 5:
        # 06. いただきます♪
        bounce = abs(math.sin(t * 4 * pi))
        if body: body.location.z += 0.14 * bounce
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(60)
            r_arm.rotation_euler.x = math.radians(38)
            l_arm.rotation_euler.y = math.radians(60)
            l_arm.rotation_euler.x = -math.radians(38)
        if bread and face:
            bread.rotation_euler.y = -math.radians(12) * bounce
            face.rotation_euler.y = -math.radians(12) * bounce

    elif stamp_idx == 6:
        # 07. お疲れさまです
        tilt = math.sin(t * 2 * pi)
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(50)
            l_arm.rotation_euler.y = math.radians(50)
        if bread and face:
            bread.rotation_euler.x = math.radians(16) * tilt
            face.rotation_euler.x = math.radians(16) * tilt

    elif stamp_idx == 7:
        # 08. やったー！ (大ジャンプ)
        jump = abs(math.sin(t * 4 * pi))
        if body: body.location.z += 0.50 * jump
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(155) + math.radians(12) * jump
            l_arm.rotation_euler.x = -math.radians(155) - math.radians(12) * jump
        if r_leg and l_leg:
            r_leg.rotation_euler.x = math.radians(20) * jump
            l_leg.rotation_euler.x = -math.radians(20) * jump

    elif stamp_idx == 8:
        # 09. 考え中...
        think = math.sin(t * 2 * pi)
        if r_arm:
            r_arm.rotation_euler.y = math.radians(70)
            r_arm.rotation_euler.x = math.radians(40)
        if bread and face:
            bread.rotation_euler.x = math.radians(14) * think
            face.rotation_euler.x = math.radians(14) * think

    elif stamp_idx == 9:
        # 10. プンプン！ (腰手・足踏み)
        stomp = math.sin(t * 4 * pi)
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(45)
            r_arm.rotation_euler.x = math.radians(35)
            l_arm.rotation_euler.y = math.radians(45)
            l_arm.rotation_euler.x = -math.radians(35)
        # 片足ずつ足踏み（靴も完全に連動してリズミカルに上下）
        lift_r = max(0, stomp) * 0.18
        lift_l = max(0, -stomp) * 0.18
        if r_leg: r_leg.location.z += lift_r
        if r_foot: r_foot.location.z += lift_r
        if l_leg: l_leg.location.z += lift_l
        if l_foot: l_foot.location.z += lift_l
        if body: body.location.z += 0.06 * abs(stomp)

    elif stamp_idx == 10:
        # 11. 悲しい...
        slump = abs(math.sin(t * 2 * pi))
        if body:
            body.rotation_euler.y = math.radians(22) * slump
            body.location.z += -0.12 * slump
        if bread and face:
            bread.rotation_euler.y = math.radians(20) * slump
            face.rotation_euler.y = math.radians(20) * slump
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(10)
            l_arm.rotation_euler.y = math.radians(10)

    elif stamp_idx == 11:
        # 12. イエーイ！ (ダンスステップ)
        step = math.sin(t * 4 * pi)
        if body:
            body.location.y += 0.18 * step
            body.rotation_euler.x = math.radians(12) * step
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(120) + math.radians(30) * step
            l_arm.rotation_euler.x = -math.radians(120) + math.radians(30) * step

    elif stamp_idx == 12:
        # 13. ポカ〜ン (呆然)
        if bread and face:
            bread.rotation_euler.x = math.radians(16)
            face.rotation_euler.x = math.radians(16)
            bread.rotation_euler.y = math.radians(8)
            face.rotation_euler.y = math.radians(8)

    elif stamp_idx == 13:
        # 14. いらっしゃいませ！ (お出迎えお辞儀)
        bow = math.sin(t * 2 * pi)
        if bow < 0: bow = 0
        if body: body.rotation_euler.y = math.radians(30) * bow
        if r_arm and l_arm:
            r_arm.rotation_euler.x = math.radians(30) * (1 - bow)
            l_arm.rotation_euler.x = -math.radians(30) * (1 - bow)
            r_arm.rotation_euler.y = math.radians(40) * bow
            l_arm.rotation_euler.y = math.radians(40) * bow

    elif stamp_idx == 14:
        # 15. 風邪気味・ブルブル... (体を抱えて震える)
        shiver = math.sin(t * 16 * pi)
        if body:
            body.location.x += 0.02 * shiver
            body.rotation_euler.z = math.radians(3) * shiver
        if r_arm and l_arm:
            r_arm.rotation_euler.y = math.radians(45)
            r_arm.rotation_euler.x = math.radians(45)
            l_arm.rotation_euler.y = math.radians(45)
            l_arm.rotation_euler.x = -math.radians(45)

    elif stamp_idx == 15:
        # 16. 一発逆転！ (ガッツポーズ突き上げ)
        fist = math.sin(t * 4 * pi)
        if r_arm:
            r_arm.rotation_euler.x = math.radians(160) + math.radians(15) * fist
            r_arm.rotation_euler.y = math.radians(20)
        if body:
            body.location.z += 0.12 * abs(fist)
            body.rotation_euler.y = -math.radians(8)

# レンダリング実行（16スタンプ × 各20フレーム）
print("=== STARTING FULL 16-STICKER BATCH RENDERING (320 frames) ===")
TOTAL_FRAMES = 20

for s_idx in range(16):
    print(f"Rendering Sticker {s_idx+1}/16...")
    s_dir = os.path.join(OUT_BASE, f"sticker_{s_idx+1:02d}")
    os.makedirs(s_dir, exist_ok=True)
    
    # カメラ構図を各スタンプ用に切り替え
    c_info = CAM_SETUPS_16[s_idx]
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
print("✓ All 320 frames for 16 stickers rendered successfully!")
