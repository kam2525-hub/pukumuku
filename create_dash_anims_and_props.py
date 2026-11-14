import bpy
import math
import os
from mathutils import Euler, Vector

BASE_DIR = r"c:\Users\akeer.AKERU\Documents\Codex\2026-10-24\new-chat\pukumuku-web-preview"
JUN_IN = os.path.join(BASE_DIR, "models", "jun_kun_carry_box.glb")
JUN_OUT = os.path.join(BASE_DIR, "models", "jun_kun_dash.glb")
PROPS_DIR = os.path.join(BASE_DIR, "models", "dash_props")
os.makedirs(PROPS_DIR, exist_ok=True)


def build_jun_dash_animations():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=JUN_IN)

    rig = bpy.data.objects["JunKun_Rig"]
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode='POSE')

    # ポーズボーンをオイラーまたはクォータニオンで操作
    pb_root = rig.pose.bones["Root"]
    pb_body = rig.pose.bones["Body"]
    pb_leg_l = rig.pose.bones["Leg_L"]
    pb_leg_r = rig.pose.bones["Leg_R"]

    for pb in (pb_root, pb_body, pb_leg_l, pb_leg_r):
        pb.rotation_mode = 'QUATERNION'

    # --- 1. Dash_Run (16フレームのダイナミック全力疾走ループ) ---
    act_run = bpy.data.actions.new(name="Dash_Run")
    if not rig.animation_data:
        rig.animation_data_create()
    rig.animation_data.action = act_run

    total_frames = 16
    for f in range(1, total_frames + 2):  # 1..17 (17 == 1 でシームレスループ)
        t = ((f - 1) / total_frames) * math.pi * 2.0

        # 全身の上下バウンス（1ループで2歩）
        bounce = abs(math.sin(t)) * 0.085
        pb_root.location = (0.0, 0.0, bounce)
        pb_root.rotation_quaternion = Euler((0.0, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_root.keyframe_insert(data_path="location", frame=f)
        pb_root.keyframe_insert(data_path="rotation_quaternion", frame=f)

        # 上半身: 前傾姿勢(約16度) + 左右ロール + ひねり
        body_pitch = 0.28 + math.sin(t * 2.0) * 0.04
        body_yaw = math.sin(t) * 0.11
        body_roll = math.cos(t) * 0.06
        pb_body.location = (0.0, 0.0, 0.0)
        pb_body.rotation_quaternion = Euler((body_pitch, body_yaw, body_roll), 'XYZ').to_quaternion()
        pb_body.keyframe_insert(data_path="location", frame=f)
        pb_body.keyframe_insert(data_path="rotation_quaternion", frame=f)

        # 脚のダイナミックな前後スイング (±52度 = ±0.90 rad)
        swing = math.sin(t) * 0.90
        pb_leg_l.rotation_quaternion = Euler((swing, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_leg_r.rotation_quaternion = Euler((-swing, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_leg_l.keyframe_insert(data_path="rotation_quaternion", frame=f)
        pb_leg_r.keyframe_insert(data_path="rotation_quaternion", frame=f)

    # --- 2. Dash_Jump (元気な空中ジャンプポーズ) ---
    act_jump = bpy.data.actions.new(name="Dash_Jump")
    rig.animation_data.action = act_jump
    for f in (1, 10):
        pb_root.location = (0.0, 0.0, 0.04)
        pb_root.rotation_quaternion = Euler((0.0, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_root.keyframe_insert(data_path="location", frame=f)

        pb_body.location = (0.0, 0.0, 0.0)
        pb_body.rotation_quaternion = Euler((0.18, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_body.keyframe_insert(data_path="rotation_quaternion", frame=f)

        pb_leg_l.rotation_quaternion = Euler((-0.78, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_leg_r.rotation_quaternion = Euler((0.68, 0.0, 0.0), 'XYZ').to_quaternion()
        pb_leg_l.keyframe_insert(data_path="rotation_quaternion", frame=f)
        pb_leg_r.keyframe_insert(data_path="rotation_quaternion", frame=f)

    bpy.ops.object.mode_set(mode='OBJECT')

    # NLAトラックへ全アクションをプッシュしてGLBに確実に出力
    for act in list(bpy.data.actions):
        if act.name in ("Carry_Idle", "Dash_Run", "Dash_Jump", "Wave"):
            track = rig.animation_data.nla_tracks.new()
            track.name = act.name
            strip = track.strips.new(act.name, int(act.frame_range[0]), act)
            strip.name = act.name
        else:
            bpy.data.actions.remove(act)

    bpy.ops.export_scene.gltf(
        filepath=JUN_OUT,
        export_format='GLB',
        export_animations=True,
        export_nla_strips=True,
        export_materials='EXPORT'
    )
    print(f"Exported Jun-kun Dash GLB: {JUN_OUT}")


def make_mat(name, base_color, roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def set_smooth(obj):
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = True


# 追加障害物 1: obs_traffic_cone.glb (パン屋さんオレンジのコーン＆バー・ジャンプ可)
def build_traffic_cone():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m_orange = make_mat("ConeOrange", (0.98, 0.42, 0.08), roughness=0.4)
    m_white = make_mat("ConeWhite", (0.98, 0.98, 0.96), roughness=0.35)
    m_black = make_mat("ConeBase", (0.14, 0.14, 0.16), roughness=0.75)

    for sx in (-0.36, 0.36):
        # ベース板
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0.0, 0.03))
        b = bpy.context.active_object
        b.scale = (0.36, 0.36, 0.06)
        bpy.ops.object.transform_apply(scale=True)
        b.data.materials.append(m_black)
        # 円錐本体
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.14, radius2=0.035, depth=0.66, location=(sx, 0.0, 0.38))
        c = bpy.context.active_object
        c.data.materials.append(m_orange)
        set_smooth(c)
        # 白反射帯
        bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.105, radius2=0.072, depth=0.20, location=(sx, 0.0, 0.44))
        w = bpy.context.active_object
        w.data.materials.append(m_white)
        set_smooth(w)

    # 横バー
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.032, depth=0.98, location=(0.0, 0.0, 0.56), rotation=(0, math.radians(90), 0))
    bar = bpy.context.active_object
    bar.data.materials.append(m_white)
    set_smooth(bar)
    for bx in (-0.24, 0.0, 0.24):
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.034, depth=0.10, location=(bx, 0.0, 0.56), rotation=(0, math.radians(90), 0))
        st = bpy.context.active_object
        st.data.materials.append(m_orange)
        set_smooth(st)

    path = os.path.join(PROPS_DIR, "obs_traffic_cone.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True)
    print("Exported:", path)


# 追加障害物 2: obs_oven_rack.glb (背の高い木製ベーカリー棚・回避必須)
def build_oven_rack():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m_wood = make_mat("ShelfWood", (0.56, 0.34, 0.16), roughness=0.68)
    m_iron = make_mat("ShelfIron", (0.18, 0.20, 0.22), roughness=0.45, metallic=0.8)
    m_bread = make_mat("BaguetteGold", (0.85, 0.54, 0.20), roughness=0.62)

    # 側板
    for sx in (-0.42, 0.42):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 1.05))
        side = bpy.context.active_object
        side.scale = (0.06, 0.58, 2.10)
        bpy.ops.object.transform_apply(scale=True)
        side.data.materials.append(m_iron)

    # 4段棚板 + パン
    for idx, tz in enumerate([0.28, 0.78, 1.28, 1.78]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, tz))
        shelf = bpy.context.active_object
        shelf.scale = (0.84, 0.56, 0.05)
        bpy.ops.object.transform_apply(scale=True)
        shelf.data.materials.append(m_wood)

        for bx in (-0.24, 0.0, 0.24):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=10, radius=0.10, location=(bx, 0, tz + 0.09))
            b = bpy.context.active_object
            b.scale = (0.85, 1.75, 0.72)
            bpy.ops.object.transform_apply(scale=True)
            b.data.materials.append(m_bread)
            set_smooth(b)

    # 上部看板
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.14))
    top = bpy.context.active_object
    top.scale = (0.90, 0.60, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    top.data.materials.append(m_wood)

    path = os.path.join(PROPS_DIR, "obs_oven_rack.glb")
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True)
    print("Exported:", path)


if __name__ == "__main__":
    build_jun_dash_animations()
    build_traffic_cone()
    build_oven_rack()
    print("DONE!")
