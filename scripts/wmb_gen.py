#fix all %TEMP%
#test all %TEST%
#add debug
import os
import sys
from util import *

class WMB_Header(object):
	def __init__(self, bbox1, bbox2, bone_count, bone_table_size, vertex_group_count, batches_offset, batches_count, lods_offset, lods_count, bone_map_offset, bone_map_count, bone_set_count, materials_offset, materials_count, mesh_group_count, mesh_mat_offset, mesh_mat_pair): #(float 3tuple, float 3tuple, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int)
		self.super(WMB_Header, self).__init__()
		self.magicNumber = b'WMB3'
		self.version = '20160116' #always this
		self.unknown08 = 0 #? always zero
		self.flags = 4294901770 #? always this
		self.boundingBox1 = bbox1
		self.boundingBox2 = bBox2
		self.boneArrayOffset = 144
		self.boneCount = bone_count
		self.boneTableOffset = boneArrayOffset + (boneCount * 88)
		self.boneTableSize = bone_table_size #?
		self.vertexGroupOffset = boneTableOffset + boneTableSize
		self.vertexGroupCount = vertex_group_count
		self.batchesOffset = batches_offset
		self.batchesCount = batches_count
		self.lodsOffset = batches_offset + (batches_count * 28)
		self.lodsCount = lods_count
		self.boneMapOffset = bone_map_offset
		self.boneMapCount = bone_map_count
		self.bonesetOffset = meshMaterialOffset + (meshMaterialCount * 8)
		self.bonesetCount = bonesetCount
		self.materialsOffset = materials_offset
		self.materialsCount = materials_count
		self.meshGroupOffset = boneMapOffset + (boneMapCount * 4)
		self.meshGroupCount = mesh_group_count
		self.meshMaterialOffset = mesh_mat_offset
		self.meshMaterialCount = mesh_mat_pair
		self.unknowns = 0

class wmb3_vertexGroup(object):
	"""docstring for wmb3_vertexGroup"""
	def __init__(self, vertex_offset, vertex_type, vertex_num, loop_num): #(int, int, int, int)
		super(wmb3_vertexGroup, self).__init__()
		self.vertexArrayOffset = vertex_offset #int	
		self.vertexNum = vertex_num
		self.loopNum = loop_num
		self.unknowns = 0
		if vertex_type == 0xb:
			self.vertexSize = 28
			self.vertexExFlags = 11
			self.vertexExSize = 20
			self.vertexExArrayOffset = vertex_offset + vertex_num*28 
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*20
		if vertex_type == 0x7:
			self.vertexSize = 28
			self.vertexExFlags = 7
			self.vertexExSize = 12
			self.vertexExArrayOffset = vertex_offset + vertex_num*28
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*12
		if vertex_type == 0xa:
			self.vertexSize = 28
			self.vertexExFlags = 10
			self.vertexExSize = 16
			self.vertexExArrayOffset = vertex_offset + vertex_num*28
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*16
		else:
			self.vertexSize = 28
			self.vertexExFlags = 10
			self.vertexExSize = 16
			self.vertexExArrayOffset = vertex_offset + vertex_num*28
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*16
						
class wmb3_vertex(object):
	"""docstring for wmb3_vertex"""
	def __init__(self, position, tangent, uv, bone_index, bone_weight): #(float 3tuple, int 3tuple, float 2tuple, int 4tuple, int 4tuple)
		super(wmb3_vertex, self).__init__()
		self.position = position 
		self.tangent = ((tangent[0] * 255) / 2, (tangent[1] * 255) / 2, (tangent[2] * 255) / 2, -1)					
		self.textureUV = uv 	
		self.boneIndex = bone_index
		self.boneWeight = bone_weight
	
class wmb3_vertexEx(object): 
	"""docstring for wmb3_vertexEx"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx, self).__init__()
		self.textureUV2 = uv
		self.color = (color[0], color[1], color[2], -1)
		self.normal = (normal[0], normal[1], normal[2], 0)
		self.textureUV3 = uv
				
class wmb3_bone(object): #88 bytes (last one has extra 8 bytes)
	"""docstring for wmb3_bone"""
	def __init__(self, number, parent_index, local_pos, local_rot, world_pos, world_rot, blender_name): #(int, int, wmb3_bone, 3tuple, 3tuple, string)
		super(wmb3_bone, self).__init__()
		self.boneNumber = number #used for physics in .bxm files
		self.parentIndex = parent_index
		#parent_world_pos - world_pos
		self.localPosition = local_pos
		#parent_world_rot - world_rot
		self.localRotation = local_rot
		self.localScale = (1.0, 1.0, 1.0) 
		#armature.pose.bone.head
		self.worldPosition =  world_pos
		#armature.pose.bone.matrix.to_euler()
		self.worldRotation = world_rot
		self.worldScale = (1.0, 1.0, 1.0)
		#usually equal to world_pos, might not be needed ingame %TEST%
		self.worldPositionTpose = world_pos
		self.name = blender_name
		
class wmb3_batch(object):
	"""docstring for wmb3_batch"""
	def __init__(self, vertex_group_index, bone_set_index, vertex_start, loop_start, vertex_num, loop_num, primitive_num): #(int, int, int, int, int, int, int, int)
		super(wmb3_batch, self).__init__()
		self.vertexGroupIndex = vertex_group_index
		self.boneSetIndex = bone_set_index
		self.vertexStart = vertex_start
		self.loopStart = loop_start
		self.vertexNum = vertex_num
		self.loopNum = loop_num
		self.primitiveNum = primitive_num
		
class wmb3_lod(object):
	"""docstring for wmb3_lod"""
	def __init__(self, offset, lod_level, batch_start, batch_info_num): #(int, int, int, int)
		super(wmb3_lod, self).__init__()
		self.lodLevel = lod_level
		self.batchStart = batch_start
		self.batchInfoOffset = offset + 20
		self.batchInfoNum = batch_info_num
		self.nameOffset = (offset + 20) + (batch_info_num * 24)
		
class wmb3_batchInfo(object):
	"""docstring for wmb3_batchInfo"""
	def __init__(self, vertex_group_index, mesh_index, material_index, mesh_mat_pair_index): #(int, int, int, int)
		super(wmb3_batchInfo, self).__init__()
		self.vertexGroupIndex = vertex_group_index
		self.meshIndex = mesh_index
		self.materialIndex = material_index
		self.unknown1 = -1
		self.meshMaterialPairIndex = mesh_mat_pair_index
		self.unknown2 = -1

class wmb3_meshMaterialPair(object):
	"""docstring for wmb3_meshMaterialPair"""
	def __init__(self, mesh_index, material_index): #(int, int)
		super(wmb3_meshMaterialPair, self).__init__()
		self.meshIndex = mesh_index
		self.materialIndex = material_index
		
class wmb3_boneSet(object): 
	"""docstring for wmb3_boneSet"""
	def __init__(self, offset, bone_array): #(int, array)
		super(wmb3_boneSet, self).__init__()
		self.boneSetOffset = offset
		self.boneArray = bone_array
		self.boneIndexNum = len(bone_array)

class wmb3_texture(object):
	"""docstring for wmb3_texture"""
	def __init__(self, filepath, name, texture_type, identifier): #(string, string, string, string)
		super(wmb3_texture, self).__init__()
		self.filepath = filepath
		self.name = name
		self.textureType = texture_type
		self.identifier = identifier
			
class wmb3_material(object):
	"""docstring for wmb3_material"""
	def __init__(self, offset, material_name, shader_name, texture_array): #(int, string, string, array)
		super(wmb3_material, self).__init__()
		#Declarations
		self.first8Bytes = b'\xe0\x07\x07\x00\x05\x00\x0f\x00'
		self.materialNameOffset = offset
		self.materialName = material_name
		self.shaderNameOffset = 0
		self.shaderName = shader_name
		self.techniqueNameOffset = 0
		self.techniqueName = 'Default'
		self.textureOffset = 0
		self.textureArray = texture_array
		self.textureNum = len(texture_array)
		self.textureOffsetArray = [] #int
		self.textureIdentifierArray = [] #string
		self.textureNames = [] #string
		self.paramOffset = 0
		self.paramNum = 2
		self.paramIndexArray = [0, -1]
		self.paramOffsetArray = [] #int
		self.paramNumArray = [] #int
		self.paramArray = [] #float
		self.varOffset = 0
		self.varNum = 0
		self.varNameOffsetsArray = [] #int
		self.varValues = [] #float
		self.varNames = [] #string
	def updateMaterial(self):
		params = 0
		self.shaderNameOffset = self.materialNameOffset + len(self.materialName) + 1
		self.techniqueNameOffset = self.shaderNameOffset + len(self.shaderName) + 1
		if self.shaderName == 'CNS00_XXXXX':
			self.techniqueName = 'Multiplication'
		self.textureOffset = self.techniqueNameOffset + len(self.techniqueName) + 1
		if self.textureNum > 0:
			#Textures
			self.textureOffsetArray.append(self.textureOffset + self.textureNum*8)
			for i in range(len(self.textureArray)):
				self.textureNames.append(self.textureArray[i].textureType)
				if i > 0:
					self.textureOffsetArray.append(self.textureOffset + self.textureNum*8 + len(self.textureNames[i-1]) + 1)
				self.textureIdentifierArray.append(self.textureArray[i].identifier)
			self.paramOffset = self.textureOffsetArray[-1] + len(self.textureNames[-1]) + 1
			#Shader/Material Variables
			if self.shaderName == 'CLT00_XXXXX':
				self.paramNum = 2
				self.varNum = 62
				params = 48
				self.paramArray = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.2, 0.0, 0.0, 0.3, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 1.0, 0.2, 0.6, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_FuzzColorCorrection_X', 'g_FuzzColorCorrection_Y', 'g_FuzzColorCorrection_Z', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_FuzzMul', 'g_FuzzReverse', 'g_FuzzShadowLowerLimit', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceMetalic', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.3, 0.2, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0]
			elif self.shaderName == 'PBS00_XXXXX':
				self.paramNum = 2
				params = 36
				self.varNum = 50
				self.paramArray = [1, 0, 0, 0, 0, 0, 1, 1, 50, 50, 1, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.2, 0, 0, 0, 0, 1, 0.4, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UV2Use', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseLightMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_UseOcclusionMap', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]
			elif self.shaderName == 'SKN00_XXXXX':
				self.paramNum = 2
				params = 44
				self.varNum = 55
				self.paramArray = [1, 0, 0, 0, 0, 0, 0, 0, 20, 20, 1, 0, 0.5, 0.5, 0.5, 0, 0.2, 0, 0, 0, 1, 1.5, 1, 0, 0.291777, 0.039546, 0.039546, 0, 0.806955, 0.300551, 0.201554, 5, 0, 1, 0.63, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OcclusionColor_X', 'g_OcclusionColor_Y', 'g_OcclusionColor_Z', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_TransMissionColor_X', 'g_TransMissionColor_Y', 'g_TransMissionColor_Z', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bDispCurvature', 'g_bDispSpecular', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite', 'g_bUseCurvatureMap', 'g_rho_s', 'g_tuneCurvature']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 50.0, 50.0, 5.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.29177701473236084, 0.03954600170254707, 0.03954600170254707, 0.0, 1.0, 0.8069549798965454, 0.30055099725723267, 0.20155400037765503, 1.0, 1.0, 1.0, 0.8, 0.6299999952316284, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
			elif self. shaderName == 'Eye00_XXXXX':
				self.paramNum = 2
				params = 32
				self.varNum = 39
				self.paramArray = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.8, 0.0, 0.4, 1.0, 0.6, 0.02, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_AddEnvCubeIntensity', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Glossiness', 'g_GlossinessIris', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_LightIrisIntensity', 'g_Metallic', 'g_MetallicIris', 'g_NormalReverse', 'g_ParallaxStrength', 'g_ReflectionIntensity', 'g_UseNormalMap', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.8, 0.4, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6, 0.0, 1.0, 0.0, 0.02, 1.0, 1.0, 0.0, 1.0, 1.0]
			elif self.shaderName == 'Hair01_XXXXX':
				self.paramNum = 2
				params = 52
				self.varNum = 62
				self.paramArray = [1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0.514908, 0.473523, 0.428685, 0, 0.1, 0.2, 0, 0, 0.8, 4, 1, 0, 0, 0, 0, 0, 1, 0.1, 70, 0, 10, 1, 2, 0.02, 0.8, 0.622, -0.36, 0, 0, 1, 0.63, 0.5, 1, 0.5, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NoiseTile_X', 'g_NoiseTile_Y', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_SecondaryGlossiness', 'g_SecondaryMetalic', 'g_SecondarySpecShift', 'g_SpecShift', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceSecondaryGlossiness', 'g_WetMagAlbedo', 'g_WetMagNoiseTile_X', 'g_WetMagNoiseTile_Y', 'g_bAlbedoOverWrite', 'g_bDispNoise', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5149080157279968, 0.47352299094200134, 0.4286850094795227, 1.0, 0.0, 1.0, 0.0, 0.1, 70.0, 1.0, 1.0, 2.0, 4.0, 1.0, 0.1, 0.8, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.2, 10.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.622, 0.8, -0.36, 0.02, 0.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.63, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0]
			elif self.shaderName == 'CNS00_XXXXX':
				self.paramNum = 2
				params = 28
				self.varNum = 34
				self.paramArray = [0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_Decal', 'g_Intensity', 'g_InvalidFog', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_Tile_X', 'g_Tile_Y', 'g_UseMultiplicationBlend', 'g_UseSubtractionBlend', 'g_UvAnimation_X', 'g_UvAnimation_Y', 'g_bAlbedoOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
			else:
				self.paramNum = 2
				params = 36
				self.varNum = 50
				self.paramArray = [1, 0, 0, 0, 0, 0, 1, 1, 50, 50, 1, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.2, 0, 0, 0, 0, 1, 0.4, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UV2Use', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseLightMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_UseOcclusionMap', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]
			#Parameters
			self.paramIndexArray = [0, -1]
			self.paramNumArray = [params - 4, 4]
			self.paramOffsetArray = [self.paramOffset + self.paramNum * 12, self.paramOffset + self.paramNum * 12 + self.paramNumArray[0] * 4]
			self.varOffset = self.paramOffsetArray[-1] + self.paramNumArray[-1] * 4
			self.varNameOffsetsArray = [self.varOffset+496] #int
			for i in range(self.varNum):
				self.varNameOffsetsArray.append(self.varNameOffsetsArray[i] + (len(self.varNames[i]) + 1))
		else:
			print('No textures provided to material: ' + self.materialName)
	
class wmb3_meshGroup(object):
	"""docstring for wmb3_meshGroup"""
	def __init__(self, info_offset, mesh_name, bbox1, bbox2, material_index_array, bone_index_array): #(int, string, float 3tuple, float 3tuple, array, array)
		super(wmb3_meshGroup, self).__init__()
		self.name = mesh_name
		self.nameOffset = info_offset
		self.boundBox1 = bbox1
		self.boundBox2 = bbox2
		self.materialIndexArray = material_index_array
		self.materialsOffset = info_offset + len(mesh_name) + 1
		self.materialsNum = len(material_index_array)
		self.boneIndexArray = bone_index_array
		self.bonesOffset = (info_offset + len(mesh_name) + 1) + (len(material_index_array) * 2)
		self.bonesNum = len(bone_index_array)
		
		
currentOffset = 0 #BUFFER.tell() #%TEMP%

blenderBones = []
blenderMeshes = []
blenderMaterials = []
blenderTextures = []
blenderMeshVerticesDic = {}
blenderMeshLoopsDic = {}
blenderMeshVertexGroupsDic = {}
blenderMeshMaterialsDic = {}
blenderMaterialTexturesDic = {}
blenderBoneIndicesDic = {}
blenderMaterialIndicesDic = {}
wmbMeshVerticesDic = {}
wmbMeshVertexExsDic = {}
wmbBones = []
wmbBoneSets = []
wmbMaterials = []
wmbTextures = []
wmbBatches = []
wmbBatchInfos = []
wmbMeshMaterialPairs = []
wmbLods = []
wmbMeshGroups = []
wmbBoneMap = []
wmbVertexGroups = []

def generateBlenderInfo():
	#Bones
	for bone in bpy.data.armatures[0].bones:
		blenderBones.append(bone)	
	#Meshes
	for object in bpy.data.objects:
		if object.type == 'MESH':
			blenderMeshes.append(object)
	#Materials
	for material in bpy.data.materials:
		blenderMaterials.append(material)
	#Textures
	for texture in bpy.data.textures:
		blenderTextures.append(texture)
	
def generateBlenderDics():
	#Mesh Name:Vertices
	for mesh in blenderMeshes:
		blenderMeshVerticesDic[mesh.data.name] = mesh.data.vertices.values()
	#Mesh Name:Loops
	for mesh in blenderMeshes:
		blenderMeshLoopsDic[mesh.data.name] = mesh.data.loops.values()
	#Mesh Name:Vertex Group Names
	for object in bpy.data.objects:
		if object.type == 'MESH':
			blenderMeshVertexGroupsDic[object.data.name] = object.vertex_groups.keys()
	#Mesh Name:Materials
	for mesh in blenderMeshes:
		blenderMeshMaterialsDic[mesh.data.name] = mesh.data.materials[0]
	#Material Name:Textures
	for material in blenderMaterials:
		if material in blenderMeshMaterialsDic.values():
			textures_array = []
			for i in range(len(material.texture_slots.items())):
				textures_array.append(material.texture_slots[i].texture)
			blenderMaterialTexturesDic[material.name] = textures_array
	#Bone Name:Index
	for i,bone in zip(range(len(blenderBones)), blenderBones):
		blenderBoneIndicesDic[bone.name] = i
	#Material Name:Index
	for i,material in zip(range(len(blenderMaterials)), blenderMaterials):
		blenderMaterialIndicesDic[material.name] = i
	
def generateWMBInfo():
	#Vertices and VertexExs
	for mesh in blenderMeshes:
		#Mesh Info
		mesh.data.calc_tangents()
		mesh_bones = blenderMeshVertexGroupsDic[mesh.data.name]
		meshVertices = []
		meshVertexExs = []
		#Vertex Defaults
		vertex_position = [-1,-1,-1]
		vertex_normal = [-1,-1,-1]
		vertex_tangent = [-1,-1,-1]
		vertex_uv = [-1,-1]
		vertex_colors = [-1,-1,-1]
		for loop in blenderMeshLoopsDic[mesh.data.name]:
			unique_vertices = []
			vIndex = loop.vertex_index
			if not vIndex in unique_vertices:
				vertex_bones = []
				vertex_weights = []
				unique_vertices.append(vIndex)
				#Vertex Position
				vertex_position[0] = mesh.data.vertices[vIndex].co[0]
				vertex_position[1] = mesh.data.vertices[vIndex].co[1]
				vertex_position[2] = mesh.data.vertices[vIndex].co[2]
				#Vertex Normal
				vertex_normal[0] = mesh.data.vertices[vIndex].normal[0]
				vertex_normal[1] = mesh.data.vertices[vIndex].normal[1]
				vertex_normal[2] = mesh.data.vertices[vIndex].normal[2]
				#Vertex Tangent
				vertex_tangent[0] = loop.tangent[0]
				vertex_tangent[1] = loop.tangent[1]
				vertex_tangent[2] = loop.tangent[2]
				#Vertex UV Position
				try:
					vertex_uv[0]  = mesh.data.uv_layers.active.data[vIndex].uv[0]
					vertex_uv[1]  = mesh.data.uv_layers.active.data[vIndex].uv[1]
				except:
					print("Mesh {} doesnt have a uv".format(mesh.name))
				#Vertex Color
				if mesh.data.vertex_colors: 
					vertex_colors[0] = mesh.data.vertex_colors[0].data[vIndex].color[0]
					vertex_colors[1] = mesh.data.vertex_colors[0].data[vIndex].color[1]
					vertex_colors[2] = mesh.data.vertex_colors[0].data[vIndex].color[2]
				#Vertex Bones
				for boneName in mesh_bones:
					vgIndex = mesh.vertex_groups[boneName].index
					for vGroup in mesh.data.vertices[vIndex].groups:
						if vGroup.group == vgIndex:
							vertex_bones.append(blenderBoneIndicesDic[boneName])
							vertex_weights.append(vGroup.weight)
				meshVertices.append(wmb3_vertex(vertex_position, vertex_tangent, vertex_uv, vertex_bones, vertex_weights))
				meshVertexExs.append(wmb3_vertexEx(vertex_uv, vertex_colors, vertex_normal))
		wmbMeshVerticesDic[mesh.data.name] = meshVertices
		wmbMeshVertexExsDic[mesh.data.name] = meshVertexExs
	#Bones
	for i,bone in zip(range(len(blenderBones)), blenderBones):
		number = -1 #bone.wmb_num %TEMP%
		parent_index = -1
		world_pos = (bone.head.x, bone.head.y, bone.head.z)
		world_rot = (bone.matrix.to_euler().x, bone.matrix.to_euler().y, bone.matrix.to_euler().z)
		local_pos = [0,0,0]
		local_rot = [0,0,0]
		name = bone.name
		if bone.parent:
			for i in range(len(wmbBones)):
				if wmbBones[i].name == bone.parent.name:
					parent_index = i
					local_pos[0] = world_pos[0] - wmbBones[i].worldPosition[0]
					local_pos[1] = world_pos[1] - wmbBones[i].worldPosition[1]
					local_pos[2] = world_pos[2] - wmbBones[i].worldPosition[2]
					local_rot[0] = world_rot[0] - wmbBones[i].worldRotation[0]
					local_rot[1] = world_rot[1] - wmbBones[i].worldRotation[1]
					local_rot[2] = world_rot[2] - wmbBones[i].worldRotation[2]
		#if i == 0: %TEST%
			#wmbBones.append(wmb3_bone(4095, -1, local_pos, local_rot,  world_pos, world_rot, name))
		wmbBones.append(wmb3_bone(number, parent_index, local_pos, local_rot,  world_pos, world_rot, name))
	#Bone Sets
	for mesh in blenderMeshes:
		offset = currentOffset
		temp_array = []
		for vertexGroup in blenderMeshVertexGroupsDic[mesh.data.name]:
			for bone in wmbBones:
				if vertexGroup == bone.name:
					temp_array.append(bone)
		if len(wmbBoneSets) > 1:
			wmbBoneSets.append(wmb3_boneSet(wmbBoneSets[-1].boneSetOffset + wmbBoneSets[-1].boneIndexNum * 2, temp_array))
		else:
			wmbBoneSets.append(wmb3_boneSet(offset, temp_array))
	#Textures
	for mesh in blenderMeshes:
		material_name = blenderMeshMaterialsDic[mesh.data.name].name
		for texture in blenderMaterialTexturesDic[material_name]:
			texture_slot = texture.users_material[0].texture_slots[texture.name]
			fp = texture.image.filepath
			name = texture.image.name
			texture_type = ''
			identifier = 'a1b2c3d4' #random_identifier() %TEMP%
			if texture_slot.use_map_color_diffuse:
				texture_type = 'g_AlbedoMap'
			if texture_slot.use_map_normal:
				texture_type = 'g_NormalMap'
			if texture_slot.use_map_specular:
				texture_type = 'g_MaskMap'
			if texture_slot.use_map_diffuse:
				texture_type = 'g_LightMap'
				identifier = '4e9c16f4'
			if texture_slot.use_map_ambient:
				texture_type = 'g_EnvMap'
				identifier = '1fbc0984'
			if texture_slot.use_map_displacement:
				texture_type = 'g_ParallaxMap'
			if texture_slot.use_map_emit:
				texture_type = 'g_IrradianceMap'
				identifier = '1fbc0984'
			if texture_slot.use_map_warp:
				texture_type = 'g_CurvatureMap'
			wmbTextures.append(wmb3_texture(fp, name, texture_type, identifier))
	#Materials
	for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
		material = blenderMeshMaterialsDic[mesh.data.name]
		offset = currentOffset
		name = material.name
		shader = '' #material.shader %TEMP%
		texture_array = []
		if len(wmbMaterials) > 0:
			offset = wmbMaterials[-1].varNameOffsetsArray[-1] + len(wmbMaterials[-1].varNames[-1]) + 1
		for wmb_texture in wmbTextures:
			for blender_texture in blenderMaterialTexturesDic[material.name]:
				if wmb_texture.name == blender_texture.image.name:
					texture_array.append(wmb_texture)
		wmbMaterials.append(wmb3_material(offset, name, shader, texture_array))
		wmbMaterials[i].updateMaterial()
	#Batches and Batch Infos and Mesh Material Pairs
	for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
		shader_name = wmbMaterials[i].shaderName
		vertex_group = -1
		bone_set_index = i
		vertex_start = -1
		loop_start = -1
		vertex_count = len(mesh.data.vertices)
		loop_count = len(mesh.data.loops)
		primitive_count = loop_count / 3
		if shader_name == 'PBS00_XXXXX':
			vertex_group = 1
		elif shader_name == 'Eye00_XXXXX':
			vertex_group = 2
		else:
			vertex_group = 0
		if len(wmbBatches) > 0:
			loop_start = wmbBatches[-1].loopStart + wmbBatches[-1].loopNum
			wmbBatches.append(wmb3_batch(vertex_group, bone_set_index, 0, loop_start, vertex_count, loop_count, primitive_count))
		else:
			wmbBatches.append(wmb3_batch(vertex_group, bone_set_index, 0, 0, vertex_count, loop_count, primitive_count))
		wmbBatchInfos.append(wmb3_batchInfo(i, i, i, i))
		wmbMeshMaterialPairs.append(wmb3_meshMaterialPair(i, i))
	#Lods
	if len(wmbBatches) > 0:
		wmbLods.append(wmb3_lod(currentOffset, 0, 0, len(wmbBatches)))
	#Mesh Groups
	for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
	#im setting one mesh group per mesh %TEST%
	#as of now, bound boxes can be bigger than 1%TEST%
		offset = currentOffset + len(blenderMeshes) * 44
		name = mesh.data.name
		bbox1 = [0,0,0]
		bbox2 = [0,0,0]
		material_index_array = []
		bone_index_array = []
		#Bound Box
		bbox_corners = [mesh.matrix_world * Vector(corner) for corner in mesh.bound_box]
		bbox_min = [10,10,10] #%TEST%
		bbox_max = [-10,-10,-10] #%TEST%
		for vector in bbox_corners:
			if vector[0] < bbox_min[0]:
				bbox_min[0] = vector[0]
			if vector[0] > bbox_max[0]:
				bbox_max[0] = vector[0]
			if vector[1] < bbox_min[1]:
				bbox_min[1] = vector[1]
			if vector[1] > bbox_max[1]:
				bbox_max[1] = vector[1]
			if vector[2] < bbox_min[2]:
				bbox_min[2] = vector[2]
			if vector[2] > bbox_max[2]:
				bbox_max[2] = vector[2]
		bbox_dif = [bbox_max[0] - bbox_min[0], bbox_max[1] - bbox_min[1], bbox_max[2] - bbox_min[2]]
		#bbox_dif = [bbox_max[0] - bbox_min[0] - abs(bbox_min[0]), bbox_max[1] - bbox_min[1], bbox_max[2] - bbox_min[2]] #bbox1_x = 0
		bbox1 = [bbox_min[0], bbox_min[1], bbox_min[2]] #%TEST% can bbox be negative
		#bbox1 = [abs(bbox_min[0]) - abs(bbox_min[0]), abs(bbox_min[1]), abs(bbox_min[2])] #bbox1_x = 0
		bbox2 = bbox_dif
		#Index Arrays
		material_index_array.append(blenderMaterialIndicesDic[blenderMeshMaterialsDic[name].name])
		for bone in wmbBoneSets[i].boneArray:
			bone_index_array.append(blenderBoneIndicesDic[bone.name])
		if len(wmbMeshGroups) > 0:
			wmbMeshGroups.append(wmb3_meshGroup(wmbMeshGroups[-1].bonesOffset + (len(wmbMeshGroups[-1].boneIndexArray) * 2), name, bbox1, bbox2, material_index_array, bone_index_array))
		else:
			wmbMeshGroups.append(wmb3_meshGroup(offset, name, bbox1, bbox2, material_index_array, bone_index_array))
	#Bone Map
	for i,bone in zip(range(len(wmbBones)), wmbBones):
	#bone doesnt go in here if its local_pos x,y,z = its parents local x,y+.1,z (bones without default length)
		if i > 0:
			bone_pos = [round(bone.localPosition[0], 5), round(bone.localPosition[1], 5), round(bone.localPosition[2], 5)]
			parent_pos = [round(wmbBones[bone.parentIndex].localPosition[0], 5), round(wmbBones[bone.parentIndex].localPosition[1], 5), round(wmbBones[bone.parentIndex].localPosition[2], 5)]
			if bone_pos[0] != parent_pos[0] or bone_pos[1] != (parent_pos[1] + 0.1) or bone_pos[2] != parent_pos[2]:
				wmbBoneMap.append(i)
	#Vertex Groups (ALL->PBS->EYE)
	if len(wmbBatches) > 0:
		group0 = [0,0]
		group1 = [0,0]
		group2 = [0,0]
		for batch in wmbBatches:
			if batch.vertexGroupIndex == 0:
				group0[0] += batch.vertexNum
				group0[1] += batch.loopNum
			if batch.vertexGroupIndex == 1:
				group1[0] += batch.vertexNum
				group1[1] += batch.loopNum
			if batch.vertexGroupIndex == 2:
				group2[0] += batch.vertexNum
				group2[1] += batch.loopNum
		wmbVertexGroups.append(wmb3_vertexGroup(currentOffset + 144, 0xa, group0[0], group0[1]))
		wmbVertexGroups.append(wmb3_vertexGroup(wmbVertexGroups[0].loopArrayOffset + wmbVertexGroups[0].loopNum * 4, 0xb, group1[0], group1[1]))
		wmbVertexGroups.append(wmb3_vertexGroup(wmbVertexGroups[1].loopArrayOffset + wmbVertexGroups[1].loopNum * 4, 0x7, group2[0], group1[1]))
			
