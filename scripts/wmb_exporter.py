bl_info = {
    "name": "Nier: Automata model data exporter",
    "author": "dellevelled",
    "version": (1, 1),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "Export model data to Nier:Automata wmb/wtp/wta",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"}

import bpy
from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, EnumProperty, IntProperty

class ExportNierWMB(bpy.types.Operator, ExportHelper):
	bl_idname = "export.wmb_data"
	bl_label = "Export WMB Data"
	bl_options = {'PRESET'}
	filename_ext = ".wmb"
	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
	
	def execute(self, context):
		from blender2nier import wmb_gen
		wmb_gen.WriteWMB(self.filepath, True)
		return {'FINISHED'}

#class ExportNierWTP(bpy.types.Operator, ExportHelper):
#	bl_idname = "export.wtp_data"
#	bl_label = "Export WTP Data"
#	bl_options = {'PRESET'}
#	filename_ext = ".wtp"
#	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
#	
#	def execute(self, context):
#		from blender2nier import wtp_gen
#		wtp_gen.
#		return {'FINISHED'}
		
#class ExportNierWTA(bpy.types.Operator, ExportHelper):
#	bl_idname = "export.wta_data"
#	bl_label = "Export WTA Data"
#	bl_options = {'PRESET'}
#	filename_ext = ".wta"
#	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
#	
#	def execute(self, context):
#		from blender2nier import wta_gen
#		wta_gen.
#		return {'FINISHED'}
	
#class ExportNier(bpy.types.Operator, ExportHelper):
#	bl_idname = "export.nier_data"
#	bl_label = "Export Nier DAT/DTT"
#	bl_options = {'PRESET'}
#	filename_ext = ".dat"
#	filepath = bpy.props.StringProperty(subtype="FILE_PATH")
#	
#	def execute(self, context):
#		from blender2nier import wmb_gen
#		from blender2nier import wtp_gen
#		from blender2nier import wta_gen
#		wmb_gen.WriteDAT(self.filepath, True)
#		return {'FINISHED'}
	
def menu_func_export(self, context):
	self.layout.operator(ExportNierWMB.bl_idname, text="WMB File for Nier: Automata (.wmb)")
	#self.layout.operator(ExportNierWTP.bl_idname, text="WTP File for Nier: Automata (.wtp)")
	#self.layout.operator(ExportNierWTA.bl_idname, text="WTA File for Nier: Automata (.wta)")
	#self.layout.operator(ExportNier.bl_idname, text="DAT/DTT File for Nier: Automata (.dat/.dtt)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	
if __name__ == '__main__':
	register()
