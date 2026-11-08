import bpy, math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parent
M=P/'models'; M.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name,col,metal=0,rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    return m
steel=mat('Brushed stainless steel',(.64,.69,.72),.78,.29)
edge=mat('Polished edges',(.83,.87,.9),.9,.19)
dark=mat('Inset grip',(.075,.09,.10),.12,.65)
red=mat('Bakery orange grips',(.77,.16,.035),0,.55)

def finish(o,name,material,bevel=0):
    o.name=name; o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Machined round edges','BEVEL'); mod.width=bevel; mod.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def box(name,loc,size,material,bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,material,bevel)

def pin(name,loc,r,depth,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=r,depth=depth,location=loc,rotation=(math.pi/2,0,0))
    o=finish(bpy.context.object,name,material,.005)
    for f in o.data.polygons:f.use_smooth=True
    return o

for sign,label in [(-1,'L'),(1,'R')]:
    before=set(bpy.data.objects)
    vs=[]; faces=[]; count=18
    for i in range(count):
        t=i/(count-1); z=1.20-1.01*t; x=sign*(.035+.27*t+.035*math.sin(math.pi*t))
        width=.075+.025*math.sin(math.pi*t); depth=.045
        vs.extend([(x-width/2,-depth/2,z),(x+width/2,-depth/2,z),(x+width/2,depth/2,z),(x-width/2,depth/2,z)])
    for i in range(count-1):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    faces.extend([(3,2,1,0),(68,69,70,71)])
    me=bpy.data.meshes.new('Pressed steel ribbon'); me.from_pydata(vs,[],faces); me.update()
    o=bpy.data.objects.new('Steel_arm_'+label,me); bpy.context.collection.objects.link(o); finish(o,o.name,steel,.009)
    # Soft, removable bakery grip sleeve and visible steel border.
    o=box('Grip_sleeve_'+label,(sign*.145,-.012,.80),(.095,.062,.37),red,.026); o.rotation_euler.y=-sign*.27
    o=box('Grip_inset_'+label,(sign*.145,-.047,.80),(.048,.006,.26),dark,.014); o.rotation_euler.y=-sign*.27
    for i in range(5):
        z=.71+i*.041; x=sign*(.145+( .80-z)*.27)
        o=box('Grip_rib_'+label,(x,-.052,z),(.046,.008,.007),steel,.003); o.rotation_euler.y=-sign*.27
    box('Jaw_neck_'+label,(sign*.305,0,.135),(.068,.050,.17),steel,.009)
    # Scalloped spoon-shaped jaws with a solid, slightly cupped face.
    vs=[]; fs=[]; n=64; cx=sign*.305
    for layer in [0,1]:
        for i in range(n):
            a=math.tau*i/n; ripple=1+.055*math.cos(10*a)
            vs.append((cx+.096*math.cos(a)*ripple,.17*math.sin(a)*ripple,.045+layer*.034+.018*abs(math.sin(a))))
    vs.extend([(cx,0,.038),(cx,0,.072)])
    for i in range(n):
        j=(i+1)%n; fs.extend([(i,j,n+j,n+i),(128,j,i),(129,n+i,n+j)])
    me=bpy.data.meshes.new('Scalloped jaw'); me.from_pydata(vs,[],fs); me.update()
    o=bpy.data.objects.new('Jaw_'+label,me); bpy.context.collection.objects.link(o); finish(o,o.name,edge,.006)
    for i in range(4):box('Jaw_grip_groove_'+label,(cx,-.10+i*.064,.080),(.12,.008,.006),steel,.002)
    # Parent under an opening pivot while keeping the authored rest shape.
    parts=set(bpy.data.objects)-before
    pivot=bpy.data.objects.new('Arm_'+label,None); bpy.context.collection.objects.link(pivot); pivot.location=(0,0,1.19)
    bpy.context.view_layer.update()
    for o in parts:
        world=o.matrix_world.copy(); o.parent=pivot; o.matrix_world=world

pin('Hinge barrel',(0,0,1.19),.075,.13,steel)
pin('Hinge washer',(0,-.077,1.19),.058,.018,edge)
pin('Hinge rivet',(0,-.089,1.19),.026,.013,dark)
box('Rivet screwdriver slot',(0,-.098,1.19),(.033,.003,.006),steel,.002)
# Raised spring loop above the hinge.
curve=bpy.data.curves.new('Spring loop','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.018; curve.bevel_resolution=3
sp=curve.splines.new('POLY'); sp.points.add(40)
for i,p in enumerate(sp.points):
    a=math.pi*i/40; p.co=(.11*math.cos(a),.018,1.22+.105*math.sin(a),1)
o=bpy.data.objects.new('Spring_loop',curve); bpy.context.collection.objects.link(o); o.data.materials.append(steel)
bpy.ops.object.select_all(action='SELECT'); bpy.context.view_layer.objects.active=o
bpy.ops.object.convert(target='MESH')
bpy.ops.wm.save_as_mainfile(filepath=str(M/'bakery_tongs.blend'))
bpy.ops.export_scene.gltf(filepath=str(M/'bakery_tongs.glb'),export_format='GLB',use_selection=True)

# A studio render for checking the actual modeled object.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.015)); bpy.context.object.data.materials.append(mat('Studio surface',(.76,.72,.64)))
bpy.ops.object.camera_add(location=(1.7,-3.9,2.25)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.68))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=1.75
scene=bpy.context.scene; scene.camera=cam; scene.world.color=(.45,.45,.45)
for pos,power,size in [((-2,-3,4),450,3),((2,1,3),500,2)]:
    bpy.ops.object.light_add(type='AREA',location=pos); lamp=bpy.context.object; lamp.data.energy=power; lamp.data.shape='DISK'; lamp.data.size=size; lamp.rotation_euler=(Vector((0,0,.6))-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES'; scene.cycles.samples=24
scene.render.resolution_x=800; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=str(P/'bakery_tongs_preview.png')
bpy.ops.render.render(write_still=True)
