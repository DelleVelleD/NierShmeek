import bpy
from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntegerProperty

class ExportNierWMB(bpy.types.Operator, ImportHelper):
	bl_idname = "export.wmb_data"
	bl_label = "Export WMB Data"
	bl_options = {'Preset'}
	filename_ext = ".wmb"
	
	def execute(self, context):
		from blender2nier import wmb_gen
		return wmb_gen.WriteWMB(self.filepath, True)
		
def menu_func_import(self, context):
	self.layout.operator(ExportNierWMB

