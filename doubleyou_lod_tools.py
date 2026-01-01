import bpy
import bmesh
import math
import time
import re

class SplitUV(bpy.types.Operator):
    bl_idname = 'mesh.splituv'
    bl_label = 'Pack UVs by splitting mesh'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == 'OBJECT'

    def split(self, uv_size, obj, cicled):
        bpy.ops.mesh.fixuv()
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_lay = bm.loops.layers.uv.active

        x_loops = {}
        for face in bm.faces:
            for loop in face.loops:
                if face in x_loops:
                    x_loops[face].append(loop)
                else:
                    x_loops[face] = [loop]

        for face, loops in x_loops.items():
            verts_to_separate_x = []
            loops_len = len(loops)
            for id, loop in enumerate(loops):
                n = id + 1
                if n == loops_len:
                    n = 0
                n_loop = loops[n]
                uv_vert = loop[uv_lay].uv
                n_uv_vert = n_loop[uv_lay].uv
                vert = loop.vert
                n_vert = n_loop.vert
                edge = loop.edge
                edge_len_x = abs(n_uv_vert.x - uv_vert.x)
                if (uv_vert.x > uv_size) and (n_uv_vert.x > uv_size):
                    continue
                else:
                    if (uv_vert.x <= uv_size) and (n_uv_vert.x <= uv_size):
                        continue
                    else:
                        if uv_vert.x < uv_size:
                            cut = ((uv_size - uv_vert.x) / edge_len_x)
                            for e_vert in edge.verts:
                                if e_vert == vert:
                                    verts_to_separate_x.append(bmesh.utils.edge_split(edge, e_vert, cut)[1])
                        elif uv_vert.x == uv_size:
                            verts_to_separate_x.append(vert)
                        if n_uv_vert.x < uv_size:
                            cut = ((uv_size - n_uv_vert.x) / edge_len_x)
                            for e_vert in edge.verts:
                                if e_vert == n_vert:
                                    verts_to_separate_x.append(bmesh.utils.edge_split(edge, e_vert, cut)[1])
                        elif n_uv_vert.x == uv_size:
                            verts_to_separate_x.append(n_vert)
            if len(verts_to_separate_x) == 2:
                try:
                    bmesh.utils.face_split(face, verts_to_separate_x[0], verts_to_separate_x[1])[0]
                except:
                    continue
        bm.to_mesh(mesh)
        bm.free()

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        uv_lay = bm.loops.layers.uv.active

        y_loops = {}
        for face in bm.faces:
            for loop in face.loops:
                if face in y_loops:
                    y_loops[face].append(loop)
                else:
                    y_loops[face] = [loop]

        for face, loops in y_loops.items():
            verts_to_separate_y = []
            loops_len = len(loops)
            for id, loop in enumerate(loops):
                n = id + 1
                if n == loops_len:
                    n = 0
                n_loop = loops[n]
                uv_vert = loop[uv_lay].uv
                n_uv_vert = n_loop[uv_lay].uv
                vert = loop.vert
                n_vert = n_loop.vert
                edge = loop.edge
                edge_len_y = abs(n_uv_vert.y - uv_vert.y)
                if (uv_vert.y > uv_size) and (n_uv_vert.y > uv_size):
                    continue
                else:
                    if (uv_vert.y <= uv_size) and (n_uv_vert.y <= uv_size):
                        continue
                    else:
                        if uv_vert.y < uv_size:
                            cut = ((uv_size - uv_vert.y) / edge_len_y)
                            for e_vert in edge.verts:
                                if e_vert == vert:
                                    verts_to_separate_y.append(bmesh.utils.edge_split(edge, e_vert, cut)[1])
                        elif uv_vert.y == uv_size:
                            verts_to_separate_y.append(vert)
                        if n_uv_vert.y < uv_size:
                            cut = ((uv_size - n_uv_vert.y) / edge_len_y)
                            for e_vert in edge.verts:
                                if e_vert == n_vert:
                                    verts_to_separate_y.append(bmesh.utils.edge_split(edge, e_vert, cut)[1])
                        elif n_uv_vert.y == uv_size:
                            verts_to_separate_y.append(n_vert)
            if len(verts_to_separate_y) == 2:
                try:
                    bmesh.utils.face_split(face, verts_to_separate_y[0], verts_to_separate_y[1])[0]
                except:
                    continue
        bm.to_mesh(mesh)
        bm.free()

        for face in obj.data.polygons:
            x = 0
            y = 0
            if len(face.loop_indices) > 0:
                face_coords = [obj.data.uv_layers.active.data[loop_idx].uv for loop_idx in face.loop_indices]
                xi = min([x.x for x in face_coords])
                yi = min([y.y for y in face_coords])
                while xi >= 0.999:
                    xi -= 1
                    x -= 1
                while yi >= 0.999:
                    yi -= 1
                    y -= 1
                if x != 0:
                    for i in face_coords:
                        i.x += x
                if y != 0:
                    for i in face_coords:
                        i.y += y
        for face in obj.data.polygons:
            if len(face.loop_indices) > 0:
                face_coords = [obj.data.uv_layers.active.data[loop_idx].uv for loop_idx in face.loop_indices]
                xi = max([x.x for x in face_coords])
                yi = max([y.y for y in face_coords])
                if (xi > 1) or (yi > 1):
                    if cicled < 100:
                        return True
        for uv in obj.data.uv_layers:
            for vert in range(len(uv.data) - 1):
                if math.isnan(uv.data[vert].uv.x):
                    uv.data[vert].uv.x = 0
                if math.isnan(uv.data[vert].uv.y):
                    uv.data[vert].uv.y = 0

    def execute(self, context):
        start_time = time.time()
        scn = context.scene
        uv_size = scn.uv_size
        obj = context.active_object
        cicled = 0
        while self.split(uv_size, obj, cicled):
            cicled += 1
        print('{} seconds passed'.format(time.time() - start_time))
        self.report({'INFO'}, 'UVs packed.')
        return{'FINISHED'}

class FixUV(bpy.types.Operator):
    bl_idname = 'mesh.fixuv'
    bl_label = 'Move UVs closer to bounds'
    bl_description = ''
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    def execute(self, context):
        start_time = time.time()
        scene = bpy.context.scene
        for obj in scene.objects:
            if obj.type == 'MESH':
                for face in obj.data.polygons:
                    try:
                        face_coords = [obj.data.uv_layers.active.data[loop_idx].uv for loop_idx in face.loop_indices]
                        x = 0
                        y = 0
                        xi = min([x.x for x in face_coords])
                        yi = min([y.y for y in face_coords])
                        while xi >= 0.999:
                            xi -= 1
                            x -= 1
                        while xi < 0:
                            xi += 1
                            x += 1
                        while yi >= 0.999:
                            yi -= 1
                            y -= 1
                        while yi < 0:
                            yi += 1
                            y += 1
                        if x != 0:
                            for i in face_coords:
                                i.x += x
                        if y != 0:
                            for i in face_coords:
                                i.y += y
                    except:
                        print(obj.name + 'Has no UV map')
        print('{} seconds passed'.format(time.time() - start_time))
        self.report({'INFO'}, 'UVs were fixed.')
        return{'FINISHED'}

class BSTriShape(bpy.types.Operator):
    bl_idname = "mesh.bstrishape"
    bl_label = "Flag as BSTriShape"
    bl_description = "Flag as BSTriShape"

    def execute(self, context):
        obj = context.active_object
        obj["flags"] = 14
        obj["pynBlockName"] = "BSTriShape"
        self.report({'INFO'}, f"Flagged {obj.name} as BSTriShape")
        return {'FINISHED'}

class LODMaterial(bpy.types.Operator):
    bl_idname = "mesh.lodmaterial"
    bl_label = "Set LOD Material"
    bl_description = "Change material to use LOD material."

    def execute(self, context):
        obj = context.active_object
        new_name = ''
        for i, mat in enumerate(obj.data.materials):

            if mat and "BSLSP_Shader_Name" in mat:
                original_name = mat["BSLSP_Shader_Name"]

                # Run your string replacement
                new_name = re.sub(r"C:\\projects\\Fallout4\\Build\\PC\\Data\\", "", original_name, flags=re.IGNORECASE)
                if not "materials\\lod\\" in new_name.lower():
                    new_name = re.sub(r"materials\\", r"materials\\lod\\", new_name, flags=re.IGNORECASE)

                # Update the custom property
                mat["BSLSP_Shader_Name"] = new_name

                # Replace material if the renamed one exists in bpy.data.materials
                replacement_mat = bpy.data.materials.get(new_name)
                if replacement_mat:
                    obj.data.materials[i] = replacement_mat
                    self.report({'INFO'}, f"Material slot {i} updated to '{new_name}'")
        self.report({'INFO'}, f"{new_name}")
        return {'FINISHED'}

class PlanarDecimate(bpy.types.Operator):
    bl_idname = "mesh.planardecimate"
    bl_label = "Planar Decimate"
    bl_description = "Set Decimate modifier to Planar and UVs"

    def execute(self, context):
        obj = context.active_object
        bpy.context.view_layer.objects.active = obj

        #Add weld modifier
        bpy.ops.object.modifier_add(type='WELD')
        bpy.ops.object.modifier_apply(modifier="Weld")

        #Add decimate modifier
        bpy.ops.object.modifier_add(type='DECIMATE')
        obj.modifiers["Decimate"].decimate_type='DISSOLVE'
        obj.modifiers["Decimate"].delimit={'UV'}
        obj.modifiers["Decimate"].angle_limit=1.55334

        #Add triangulate modifier
        bpy.ops.object.modifier_add(type='TRIANGULATE')



        self.report({'INFO'}, f"Decimated {obj.name}")
        return {'FINISHED'}
    
class QuickDecimate(bpy.types.Operator):
    bl_idname = "mesh.quickplanardecimate"
    bl_label = "Quick Decimate"
    bl_description = "Set Decimate modifier to Planar and UVs and Apply"

    def execute(self, context):
        obj = context.active_object
        bpy.context.view_layer.objects.active = obj

        #Add decimate modifier
        bpy.ops.object.modifier_add(type='DECIMATE')
        obj.modifiers["Decimate"].decimate_type='DISSOLVE'
        obj.modifiers["Decimate"].delimit={'UV'}
        obj.modifiers["Decimate"].angle_limit=0.0174533
        bpy.ops.object.modifier_apply(modifier="Decimate")

        #Add triangulate modifier
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier="Triangulate")



        self.report({'INFO'}, f"Decimated {obj.name}")
        return {'FINISHED'}

class QuickWeld(bpy.types.Operator):
    bl_idname = "mesh.weld"
    bl_label = "Quick Weld"
    bl_description = "Weld vertices in the mesh"

    def execute(self, context):
        obj = context.active_object
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.modifier_add(type='WELD')
        bpy.ops.object.modifier_apply(modifier="Weld")

        self.report({'INFO'}, f"Welded {obj.name}")
        return {'FINISHED'}

class QuickTriangulate(bpy.types.Operator):
    bl_idname = "mesh.triangulate"
    bl_label = "Quick Triangulate"
    bl_description = "Triangulate the mesh"

    def execute(self, context):
        obj = context.active_object
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.ops.object.modifier_apply(modifier="Triangulate")

        self.report({'INFO'}, f"Triangulated {obj.name}")
        return {'FINISHED'}

class QuickSolidify(bpy.types.Operator):
    bl_idname = "mesh.msolidify"
    bl_label = "Add Solidify Modifier"
    bl_description = "Add Solidify Modifier"

    def execute(self, context):
        obj = context.active_object
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 50
        bpy.context.object.modifiers["Solidify"].offset = 0

        self.report({'INFO'}, f"Solidified {obj.name}")
        return {'FINISHED'}
    
class DeleteLooseGeometry(bpy.types.Operator):
    bl_idname = "mesh.deleteloosegeometry"
    bl_label = "Delete Loose Geometry"
    bl_description = "Delete Loose Geometry"

    def execute(self, context):
        if context.active_object and context.active_object.type == 'MESH':
            bpy.ops.object.mode_set(mode='EDIT')

            obj = context.active_object
            bm = bmesh.from_edit_mesh(obj.data)

             # Delete loose vertices
            loose_verts = [v for v in bm.verts if not v.link_faces]
            bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

            # Delete loose edges
            loose_edges = [e for e in bm.edges if not e.link_faces]
            bmesh.ops.delete(bm, geom=loose_edges, context='EDGES')

            # Update the mesh
            bmesh.update_edit_mesh(obj.data)
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Remove unused material slots
            bpy.ops.object.material_slot_remove_unused()


            self.report({'INFO'}, f"Removed loose geometry from {obj.name}")
            return {'FINISHED'}

# Define the UI panel
class VIEW3D_PT_MyScriptPanel(bpy.types.Panel):
    bl_label = "DoubleYou LOD Tools"
    bl_idname = "VIEW3D_PT_my_script_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'DoubleYou'

    def draw(self, context):
        layout = self.layout
        layout.operator("mesh.fixuv")
        layout.operator("mesh.splituv")
        layout.operator("mesh.planardecimate")
        layout.operator("mesh.weld")
        layout.operator("mesh.quickplanardecimate")
        layout.operator("mesh.triangulate")
        layout.operator("mesh.deleteloosegeometry")
        layout.operator("mesh.msolidify")
        layout.operator("mesh.bstrishape")
        layout.operator("mesh.lodmaterial")
        

# Register the classes
classes = [
    SplitUV,
    FixUV,
    BSTriShape,
    LODMaterial,
    PlanarDecimate,
    QuickWeld,
    QuickTriangulate,
    QuickSolidify,
    QuickDecimate,
    DeleteLooseGeometry,
    VIEW3D_PT_MyScriptPanel
]

def register():
    bpy.types.Scene.uv_size = bpy.props.FloatProperty(
        name="UV Size",
        description="Threshold for UV splitting",
        default=1.0,
        min=0.01,
        max=10.0
    )

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()