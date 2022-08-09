# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, EnumProperty, IntProperty

from bpy_extras.io_utils import ExportHelper
bl_info = {
    "name": "OpenMW Collada Exporter",
    "author": "OpenMW community, Godot Engine team",
    "version": (1, 10, 11),
    "blender": (2, 83, 0),
    "api": 38691,
    "location": "File > Import-Export",
    "description": ("Export models in Collada format to OpenMW "),
    "warning": "",
    "wiki_url": ("https://openmw.org"),
    "tracker_url": "https://github.com/openmw/collada-exporter",
    "support": "OFFICIAL",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if "export_dae" in locals():
        imp.reload(export_dae)  # noqa


class CE_OT_export_dae(bpy.types.Operator, ExportHelper):
    """Selection to DAE"""
    bl_idname = "export_scene.dae"
    bl_label = "Export DAE"
    bl_options = {"PRESET"}

    filename_ext = ".dae"
    filter_glob : StringProperty(default="*.dae", options={"HIDDEN"})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling
    object_types : EnumProperty(
        name="Object Types",
        options={"ENUM_FLAG"},
        items=(("EMPTY", "Empty", ""),
               ("CAMERA", "Camera", ""),
               ("LAMP", "Lamp", ""),
               ("ARMATURE", "Armature", ""),
               ("MESH", "Mesh", ""),
               ("CURVE", "Curve", ""),
               ),
        default={"EMPTY", "CAMERA", "LAMP", "ARMATURE", "MESH", "CURVE"},
        )

    use_export_selected : BoolProperty(
        name="Selected Objects",
        description="Export only selected objects (and visible in active "
                    "layers if that applies)",
        default=False,
        )
        
    use_mesh_modifiers : BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (on a copy!)",
        default=True,
        )
        
    use_exclude_armature_modifier : BoolProperty(
        name="Exclude Armature Modifier",
        description="Exclude the armature modifier when applying modifiers "
                      "(otherwise animation will be applied on top of the last pose)",
        default=True,
        )
        
    use_tangent_arrays : BoolProperty(
        name="Tangent Arrays",
        description="Export Tangent and Binormal arrays "
                    "(for normalmapping)",
        default=False,
        )
        
    use_triangles : BoolProperty(
        name="Triangulate",
        description="Export Triangles instead of Polygons",
        default=True,
        )
        
    use_copy_images : BoolProperty(
        name="Copy Images",
        description="Copy Images (create images/ subfolder)",
        default=False,
        )
        
    use_active_layers : BoolProperty(
        name="Active Layers",
        description="Export only objects on the active layers",
        default=True,
        )
        
    use_armature_deform_only : BoolProperty(
        name="Only Deform Bones",
        description=("Only export bones which are enabled to deform geometry"),
        default=True,
        )
        
    use_bodypart_description : BoolProperty(
        name="Skinned Body Part",
        description=("Required by OpenMW to know this is an armature of a "
                    "skinned body part. Leave disabled for:\n"
                    "- Rigid body parts without armature deformations\n"
                    "- Animated meshes not used as body parts in OpenMW"),
        default=False,
        )
        
    use_anim : BoolProperty(
        name="Export Animation",
        description="Export keyframe animation",
        default=True,
        )
        
    use_anim_action_all : BoolProperty(
        name="All Actions",
        description=("Export all actions for the first armature found "
                     "in separate DAE files"),
        default=False,
        )
        
    use_anim_skip_noexp : BoolProperty(
        name="Skip (-noexp) Actions",
        description="Skip exporting of actions whose name end in (-noexp)."
                    " Useful to skip control animations",
        default=True,
        )
        
    use_anim_optimize : BoolProperty(
        name="Optimize Keyframes",
        description="Remove double keyframes",
        default=True,
        )
        
    use_shape_key_export : BoolProperty(
        name="Shape Keys",
        description="Export shape keys for selected objects",
        default=False,
        )
        
    anim_optimize_precision : FloatProperty(
        name="Precision",
        description=("Tolerence for comparing double keyframes "
                     "(higher for greater accuracy)"),
        min=1, max=16,
        soft_min=1, soft_max=16,
        default=6.0,
        )
        
    use_metadata : BoolProperty(
        name="Use Metadata",
        default=True,
        options={"HIDDEN"},
        )
        
    scale_factor: FloatProperty(
        name="Scale",
        description="Scale all data",
        min=0.01, max=1000.0,
        default=1.0,
        )
        
    use_textkeys : BoolProperty(
        name="Export Textkeys",
        description=("Export a textkeys file based on pose markers in each exported action."
                     " Needed to define animations for OpenMW"),
        default=False,
        )
       
    anim_source : EnumProperty(
        name="Animation Source",
        items=(("SCENE", "Timeline",
                "Export global scene animation as a single animation clip"),
               ("ACTIONS", "Actions",
               "Export each action as its own animation clip"),
               ("NLA_STRIPS", "NLA Strips",
               "Export each un-muted NLA strip as its own animation clip"),
               ),
        description=(
            'Animation data used to create animation clips\n'
            'in the exported COLLADA file'),
        default="SCENE",
        )

    use_limit_precision : IntProperty(
        name="Data Precision",
        description=("To how many decimals are the exported values limited. \n"
                     "The lower the number, the smaller the exported file"),
        min=4, max=16,
        default=6,
        )

    @property
    def check_extension(self):
        return True
    
    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            "xna_validate",
                                            ))

        from . import export_dae
        return export_dae.save(self, context, **keywords)
    
    def draw(self, context):
        pass

def menu_func(self, context):
    self.layout.operator(CE_OT_export_dae.bl_idname, text="OpenMW Collada (.dae)")

class DAE_PT_export_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading = "Limit to", align = True)
        col.prop(operator, 'use_export_selected')
        col.prop(operator, 'use_active_layers')
        
        layout.column().prop(operator, 'object_types')
        
        col = layout.column(heading = "Extras", align = True)
        col.prop(operator, 'use_copy_images')
        col.prop(operator, 'use_textkeys')

class DAE_PT_export_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(heading = "Scale", align = True)
        col.prop(operator, 'scale_factor')

class DAE_PT_export_geometry(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Geometry"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(align = True)
        col.prop(operator, 'use_mesh_modifiers')
        col.prop(operator, 'use_exclude_armature_modifier')
        col.prop(operator, 'use_tangent_arrays')
        col.prop(operator, 'use_triangles')
        col.prop(operator, 'use_shape_key_export')


class DAE_PT_export_armature(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Armature"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
        
        col = layout.column(align = True)
        col.prop(operator, 'use_armature_deform_only')
        col.prop(operator, 'use_bodypart_description')
        
class DAE_PT_export_animation(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Animation"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw_header(self, context):
        sfile = context.space_data
        operator = sfile.active_operator

        self.layout.prop(operator, "use_anim", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator        

        layout.enabled = operator.use_anim
        layout.prop(operator, 'anim_source', text="Source")
        col = layout.column(align = True)
        if operator.anim_source == "ACTIONS":
            col.prop(operator, 'use_anim_skip_noexp')
        col.prop(operator, 'use_anim_optimize')
        col.prop(operator, 'anim_optimize_precision')


class DAE_PT_export_extras(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Extra"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator
            
        return operator.bl_idname == "EXPORT_SCENE_OT_dae"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        sfile = context.space_data
        operator = sfile.active_operator
          
        col = layout.column(align = True)
        col.prop(operator, 'use_limit_precision')
    
classes = (
    CE_OT_export_dae,
    DAE_PT_export_include,
    DAE_PT_export_transform,
    DAE_PT_export_geometry,
    DAE_PT_export_armature,
    DAE_PT_export_animation,
    DAE_PT_export_extras
)

def register():  
    from bpy.utils import register_class

    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():    
    from bpy.utils import unregister_class
    
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
