#fix all %TEMP%
#test all %TEST%
#add debug
import os
import sys
import time
import io
import wta_gen
import wtp_gen
from util import *

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
wmbMeshLoopsDic = {}
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
wmbBoneTable = []
wmbHeaders = []
wmbVerticesOffset = 0
wmbVertexGroupsOffset = 0

class wmb3_header(object):
	def __init__(self, bbox1, bbox2, bone_count, bone_table_size, vertex_group_count, batches_offset, batches_count, lods_count, bone_map_offset, bone_map_count, bone_set_count, materials_offset, materials_count, mesh_group_count, mesh_mat_offset, mesh_mat_pairs): 
		super(wmb3_header, self).__init__()
		self.magicNumber = b'WMB3'
		self.version = 538312982 #always this
		self.unknown08 = 0 #? always zero
		self.flags = -65526 #? always this
		self.boundingBox1 = bbox1
		self.boundingBox2 = bbox2
		self.boneOffset = 144
		self.boneNum = bone_count
		self.boneTableOffset = 144 + (bone_count * 88) + 8
		self.boneTableSize = bone_table_size #?
		self.vertexGroupOffset = (144 + (bone_count * 88) + 8) + bone_table_size
		self.vertexGroupNum = vertex_group_count
		self.batchOffset = batches_offset
		self.batchNum = batches_count
		self.lodOffset = batches_offset + (batches_count * 28)
		self.lodNum = lods_count
		self.boneMapOffset = bone_map_offset
		self.boneMapNum = bone_map_count
		self.boneSetOffset = mesh_mat_offset + (mesh_mat_pairs * 8)
		self.boneSetNum = bone_set_count
		self.materialOffset = materials_offset
		self.materialNum = materials_count
		self.meshGroupOffset = bone_map_offset + (bone_map_count * 4)
		self.meshGroupNum = mesh_group_count
		self.meshMaterialOffset = mesh_mat_offset
		self.meshMaterialNum = mesh_mat_pairs

class wmb3_vertexGroup(object):
	"""docstring for wmb3_vertexGroup"""
	def __init__(self, vertex_offset, vertex_type, vertex_num, loop_num): #(int, int, int, int)
		super(wmb3_vertexGroup, self).__init__()
		self.vertexArrayOffset = vertex_offset #int	
		self.vertexNum = vertex_num
		self.loopNum = loop_num
		self.unknowns = 0
		if vertex_type == 11: #PBS
			self.vertexSize = 28
			self.vertexExFlags = 11
			self.vertexExSize = 20
			self.vertexExArrayOffset = vertex_offset + vertex_num*28 
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*20
		elif vertex_type == 7: #Eyes
			self.vertexSize = 28
			self.vertexExFlags = 7
			self.vertexExSize = 12
			self.vertexExArrayOffset = vertex_offset + vertex_num*28
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*12
		elif vertex_type == 10: #Else
			self.vertexSize = 28
			self.vertexExFlags = 10
			self.vertexExSize = 16
			self.vertexExArrayOffset = vertex_offset + vertex_num*28
			self.loopArrayOffset = (vertex_offset + vertex_num*28) + vertex_num*16
		else: #Else
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
		self.tangent = tangent				
		self.textureUV = uv 	
		self.boneIndex = bone_index
		self.boneWeight = bone_weight
	
class wmb3_vertexEx(object): 
	"""docstring for wmb3_vertexEx"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx, self).__init__()
		self.textureUV2 = uv
		self.color = color
		self.normal = normal
		self.textureUV3 = uv
				
class wmb3_bone(object): #88 bytes (last one has extra 8 bytes)
	"""docstring for wmb3_bone"""
	def __init__(self, number, parent_index, local_pos, local_rot, world_pos, world_rot, blender_name): #(int, int, wmb3_bone, 3tuple, 3tuple, string)
		super(wmb3_bone, self).__init__()
		self.boneNumber = number #used for physics in .bxm files and global table
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
		self.meshMaterialPairIndex = mesh_mat_pair_index

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
					self.textureOffsetArray.append(self.textureOffsetArray[i-1] + len(self.textureNames[i-1]) + 1)
				self.textureIdentifierArray.append(self.textureArray[i].identifier)
			self.paramOffset = self.textureOffsetArray[-1] + len(self.textureNames[-1]) + 1
			#Shader/Material Variables
			if self.shaderName == 'CLT00_XXXXX':
				self.paramNum = 2
				self.varNum = 62
				params = 48
				self.paramArray = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.2, 0.0, 0.0, 0.3, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 1.0, 0.2, 0.6, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_FuzzColorCorrection_X', 'g_FuzzColorCorrection_Y', 'g_FuzzColorCorrection_Z', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_FuzzMul', 'g_FuzzReverse', 'g_FuzzShadowLowerLimit', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceMetalic', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.3, 0.2, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0]
			elif self.shaderName == 'PBS00_XXXXX':
				self.paramNum = 2
				params = 36
				self.varNum = 50
				self.paramArray = [1.0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 50.0, 50.0, 1.0, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.2, 0, 0, 0, 0, 1.0, 0.4, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UV2Use', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseLightMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_UseOcclusionMap', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]
			elif self.shaderName == 'SKN00_XXXXX':
				self.paramNum = 2
				params = 44
				self.varNum = 55
				self.paramArray = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 20.0, 20.0, 1.0, 0, 0.5, 0.5, 0.5, 0, 0.2, 0, 0, 0, 1.0, 1.5, 1.0, 0, 0.291777, 0.039546, 0.039546, 0, 0.806955, 0.300551, 0.201554, 5.0, 0, 1.0, 0.63, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OcclusionColor_X', 'g_OcclusionColor_Y', 'g_OcclusionColor_Z', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_TransMissionColor_X', 'g_TransMissionColor_Y', 'g_TransMissionColor_Z', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bDispCurvature', 'g_bDispSpecular', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite', 'g_bUseCurvatureMap', 'g_rho_s', 'g_tuneCurvature']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 50.0, 50.0, 5.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.29177701473236084, 0.03954600170254707, 0.03954600170254707, 0.0, 1.0, 0.8069549798965454, 0.30055099725723267, 0.20155400037765503, 1.0, 1.0, 1.0, 0.8, 0.6299999952316284, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
			elif self.shaderName == 'Eye00_XXXXX':
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
				self.paramArray = [1.0, 1.0, 1.0, 1.0, 0, 1.0, 0, 0, 1.0, 1.0, 0, 0, 0.514908, 0.473523, 0.428685, 0, 0.1, 0.2, 0, 0, 0.8, 4.0, 1.0, 0, 0, 0, 0, 0, 1.0, 0.1, 70.0, 0, 10.0, 1.0, 2.0, 0.02, 0.8, 0.622, -0.36, 0, 0, 1.0, 0.63, 0.5, 1.0, 0.5, 1.0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NoiseTile_X', 'g_NoiseTile_Y', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_SecondaryGlossiness', 'g_SecondaryMetalic', 'g_SecondarySpecShift', 'g_SpecShift', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceSecondaryGlossiness', 'g_WetMagAlbedo', 'g_WetMagNoiseTile_X', 'g_WetMagNoiseTile_Y', 'g_bAlbedoOverWrite', 'g_bDispNoise', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5149080157279968, 0.47352299094200134, 0.4286850094795227, 1.0, 0.0, 1.0, 0.0, 0.1, 70.0, 1.0, 1.0, 2.0, 4.0, 1.0, 0.1, 0.8, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.2, 10.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.622, 0.8, -0.36, 0.02, 0.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.63, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0]
			elif self.shaderName == 'CNS00_XXXXX':
				self.paramNum = 2
				params = 28
				self.varNum = 34
				self.paramArray = [0, 0, 1.0, 0, 0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_Decal', 'g_Intensity', 'g_InvalidFog', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_Tile_X', 'g_Tile_Y', 'g_UseMultiplicationBlend', 'g_UseSubtractionBlend', 'g_UvAnimation_X', 'g_UvAnimation_Y', 'g_bAlbedoOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]
			else:
				self.paramNum = 2
				params = 36
				self.varNum = 50
				self.paramArray = [1.0, 0, 0, 0, 0, 0, 1.0, 1.0, 50.0, 50.0, 1.0, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.2, 0, 0, 0, 0, 1.0, 0.4, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
				self.varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UV2Use', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseLightMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_UseOcclusionMap', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
				self.varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]
			#Parameters
			self.paramNumArray = [params - 4, 4]
			self.paramOffsetArray = [self.paramOffset + self.paramNum * 12 + 8, (self.paramOffset + self.paramNum * 12 + 8) + self.paramNumArray[0] * 4]
			self.varOffset = self.paramOffsetArray[-1] + self.paramNumArray[-1] * 4
			self.varNameOffsetsArray = [self.varOffset+self.varNum*8] #int
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

#Blender Info Grab
def generateBlenderInfo():
	#Bones
	blenderBones.clear()
	for bone in bpy.data.armatures[0].bones:
		blenderBones.append(bone)	
	#Meshes
	blenderMeshes.clear()
	for object in bpy.data.objects:
		if object.type == 'MESH':
			blenderMeshes.append(object)
	#Materials
	blenderMaterials.clear()
	for material in bpy.data.materials:
		blenderMaterials.append(material)
	#Textures
	blenderTextures.clear()
	for texture in bpy.data.textures:
		blenderTextures.append(texture)
	
def generateBlenderDics(): #requires generateBlenderInfo()
	#Mesh Name:Vertices
	blenderMeshVerticesDic.clear()
	for mesh in blenderMeshes:
		blenderMeshVerticesDic[mesh.data.name] = mesh.data.vertices.values()
	#Mesh Name:Loops
	blenderMeshLoopsDic.clear()
	for mesh in blenderMeshes:
		try:
			mesh.data.calc_tangents()
		except:
			print("---Mesh {} doesnt have a uv".format(mesh.data.name))
		blenderMeshLoopsDic[mesh.data.name] = mesh.data.loops.values()
	#Mesh Name:Vertex Group Names
	blenderMeshVertexGroupsDic.clear()
	for object in bpy.data.objects:
		if object.type == 'MESH':
			blenderMeshVertexGroupsDic[object.data.name] = object.vertex_groups.keys()
	if len(blenderMaterials) > 0:
		#Mesh Name:Materials
		blenderMeshMaterialsDic.clear()
		for mesh in blenderMeshes:
			blenderMeshMaterialsDic[mesh.data.name] = mesh.data.materials[0]
		#Material Name:Textures
		blenderMaterialTexturesDic.clear()
		for material in blenderMaterials:
			if material in blenderMeshMaterialsDic.values():
				textures_array = []
				for i in range(len(material.texture_slots.items())):
					textures_array.append(material.texture_slots[i].texture)
				blenderMaterialTexturesDic[material.name] = textures_array
		#Material Name:Index
		blenderMaterialIndicesDic.clear()
		for i,material in zip(range(len(blenderMaterials)), blenderMaterials):
			blenderMaterialIndicesDic[material.name] = i
	#Bone Name:Index
	blenderBoneIndicesDic.clear()
	for i,bone in zip(range(len(blenderBones)), blenderBones):
		blenderBoneIndicesDic[bone.name] = i

#WMB Generation
def generateWMBVertices(): #Vertices/VertexExs/Loops, requires generateBlenderDics()
	wmbMeshVerticesDic.clear()
	wmbMeshVertexExsDic.clear()
	wmbMeshLoopsDic.clear()
	noUV = False
	for mesh in blenderMeshes:
		#Mesh Info
		mesh_bones = blenderMeshVertexGroupsDic[mesh.data.name]
		meshVertices = []
		meshVertexExs = []
		meshLoops = []
		#Vertex Defaults
		vertex_position = [-1,-1,-1]
		vertex_normal = [-1,-1,-1]
		vertex_tangent = [-1,-1,-1]
		vertex_uv = [0, 0]
		vertex_colors = [-1,-1,-1]
		unique_vertices = []
		for loop in blenderMeshLoopsDic[mesh.data.name]:
			vIndex = loop.vertex_index
			if vIndex not in unique_vertices:
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
					noUV = True
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
				#Pad Vertex Bones and Weights to 4
				if len(vertex_bones) < 4:
					for i in range(4-len(vertex_bones)):
						vertex_bones.append(0)
				if len(vertex_weights) < 4:
					for i in range(4-len(vertex_weights)):
						vertex_weights.append(0)
				if len(vertex_bones) > 4:
					vertex_bones = vertex_bones[:4]
				if len(vertex_weights) > 4:
					vertex_weights = vertex_weights[:4]
				meshVertices.append(wmb3_vertex(vertex_position, vertex_tangent, vertex_uv, vertex_bones, vertex_weights))
				meshVertexExs.append(wmb3_vertexEx(vertex_uv, vertex_colors, vertex_normal))
			meshLoops.append(vIndex)
		wmbMeshVerticesDic[mesh.data.name] = meshVertices
		wmbMeshVertexExsDic[mesh.data.name] = meshVertexExs
		wmbMeshLoopsDic[mesh.data.name] = meshLoops
		if noUV:
			print("---Mesh {} doesnt have a uv".format(mesh.data.name))

def generateWMBBones(): #Bones, requires generateBlenderInfo()
	wmbBones.clear()
	for i,bone in zip(range(len(blenderBones)), blenderBones):
		number = bone.boneID #%TEST%
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
	if len(wmbBones) < 147:
		print('There are less than 147 bones, which may cause issues related to the bone index translate table. We dont yet know how it works, so im using pl1040 bones as a default bone table and it has 147 bones.')

def generateWMBBoneSets(currentOffset): #Bone Sets, requires generateBlenderDics()
	wmbBoneSets.clear()
	for mesh in blenderMeshes:
		offset = currentOffset
		temp_array = []
		for vertexGroup in blenderMeshVertexGroupsDic[mesh.data.name]:
			for bone in wmbBones:
				if vertexGroup == bone.name:
					temp_array.append(blenderBoneIndicesDic[bone.name])
		#Pad Bone Set to 8th bone
		if len(temp_array) > 8:
			padding = 8 - (len(temp_array) % 8)
		else:
			padding = 8 - len(temp_array)
		for i in range(padding):
			temp_array.append(0)
		if len(wmbBoneSets) > 0:
			wmbBoneSets.append(wmb3_boneSet(wmbBoneSets[-1].boneSetOffset + wmbBoneSets[-1].boneIndexNum * 2, temp_array))
		else:
			wmbBoneSets.append(wmb3_boneSet(offset + len(blenderMeshes) * 8, temp_array))

def generateWMBTextures(): #Textures, requires generateBlenderDics()
	wmbTextures.clear()
	if len(blenderMaterials) > 0:
		for mesh in blenderMeshes:
			material_name = blenderMeshMaterialsDic[mesh.data.name].name
			for texture in blenderMaterialTexturesDic[material_name]:
				texture_slot = texture.users_material[0].texture_slots[texture.name]
				fp = texture.image.filepath
				name = texture.image.name
				texture_type = ''
				identifier = random_identifier() %TEMP%
				if texture_slot.use_map_color_diffuse:
					texture_type = 'g_AlbedoMap'
				if texture_slot.use_map_normal:
					texture_type = 'g_NormalMap'
				if texture_slot.use_map_specular:
					texture_type = 'g_MaskMap'
				if texture_slot.use_map_diffuse:
					texture_type = 'g_LightMap'
					identifier = '4e9c16f4' #universal in game
				if texture_slot.use_map_ambient:
					texture_type = 'g_EnvMap'
					identifier = '1fbc0984' #universal in game
				if texture_slot.use_map_displacement:
					texture_type = 'g_ParallaxMap'
				if texture_slot.use_map_emit:
					texture_type = 'g_IrradianceMap'
					identifier = '1fbc0984' #universal in game
				if texture_slot.use_map_warp:
					texture_type = 'g_CurvatureMap'
				wmbTextures.append(wmb3_texture(fp, name, texture_type, identifier))
	else:
		print('---Cant generate WMB textures because there are no materials in blender')

def generateWMBMaterials(currentOffset): #Materials, requires generateWMBTextures()
	wmbMaterials.clear()
	if len(blenderMaterials) > 0:
		for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
			offset = currentOffset + len(blenderMeshes) * 48
			material = blenderMeshMaterialsDic[mesh.data.name]
			name = material.name
			shader = material.shader_type #%TEST%
			texture_array = []
			for wmb_texture in wmbTextures:
				for blender_texture in blenderMaterialTexturesDic[material.name]:
					if wmb_texture.name == blender_texture.image.name:
						texture_array.append(wmb_texture)
			if len(wmbMaterials) > 0:
				wmbMaterials.append(wmb3_material(wmbMaterials[-1].varNameOffsetsArray[-1] + len(wmbMaterials[-1].varNames[-1]) + 1, name, shader, texture_array))
			else:
				wmbMaterials.append(wmb3_material(offset, name, shader, texture_array))
			wmbMaterials[i].updateMaterial()
	else:
		print('---Cant generate WMB materials because there are no materials in blender')
		
def generateWMBBatches(): #Batches/Batch Infos/Mesh Material Pairs, requires generateWMBMaterials()
	wmbBatches.clear()
	wmbBatchInfos.clear()
	wmbMeshMaterialPairs.clear()
	for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
		try:
			shader_name = wmbMaterials[i].shaderName
		except:
			shader_name = ''
		vertex_group = -1
		bone_set_index = i
		vertex_start = -1
		loop_start = -1
		vertex_count = len(mesh.data.vertices)
		loop_count = len(mesh.data.loops)
		primitive_count = int(loop_count / 3)
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

def generateWMBLods(currentOffset): #Lods, requires generateWMBBatches()
	wmbLods.clear()
	if len(wmbBatches) > 0:
		wmbLods.append(wmb3_lod(currentOffset, 0, 0, len(wmbBatches)))
	
def generateWMBMeshGroups(currentOffset): #Mesh Groups, requires generateWMBBoneSets()
	wmbMeshGroups.clear()
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
		try:
			material_index_array.append(blenderMaterialIndicesDic[blenderMeshMaterialsDic[name].name])
		except:
			material_index_array.append(0)
			print("---Mesh {} doesnt have a material".format(name))
		for bone in wmbBoneSets[i].boneArray:
			bone_index_array.append(bone)
		if len(wmbMeshGroups) > 0:
			wmbMeshGroups.append(wmb3_meshGroup(wmbMeshGroups[-1].bonesOffset + (len(wmbMeshGroups[-1].boneIndexArray) * 2), name, bbox1, bbox2, material_index_array, bone_index_array))
		else:
			wmbMeshGroups.append(wmb3_meshGroup(offset, name, bbox1, bbox2, material_index_array, bone_index_array))
	
def generateWMBBoneMap(): #Bone Map, requires generateWMBBones()
	wmbBoneMap.clear()
	for i,bone in zip(range(len(wmbBones)), wmbBones):
	#bone doesnt go in here if its local_pos x,y,z = its parents local x,y+.1,z (bones without default length go here)
		if i > 0:
			bone_pos = [round(bone.localPosition[0], 5), round(bone.localPosition[1], 5), round(bone.localPosition[2], 5)]
			parent_pos = [round(wmbBones[bone.parentIndex].localPosition[0], 5), round(wmbBones[bone.parentIndex].localPosition[1], 5), round(wmbBones[bone.parentIndex].localPosition[2], 5)]
			if bone_pos[0] != parent_pos[0] or bone_pos[1] != (parent_pos[1] + 0.1) or bone_pos[2] != parent_pos[2]:
				wmbBoneMap.append(i)
	
def generateWMBVertexGroups(offset): #Vertex Groups (ALL->PBS->EYE), requires generateWMBBatches() 
	wmbVertexGroups.clear()
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
		wmbVertexGroups.append(wmb3_vertexGroup(offset, 10, group0[0], group0[1]))
		wmbVertexGroups.append(wmb3_vertexGroup(wmbVertexGroups[0].loopArrayOffset + wmbVertexGroups[0].loopNum * 4, 11, group1[0], group1[1]))
		wmbVertexGroups.append(wmb3_vertexGroup(wmbVertexGroups[1].loopArrayOffset + wmbVertexGroups[1].loopNum * 4, 7, group2[0], group2[1]))
	else:
		print('--Cant generate WMV vertex groups because there are no WMB batches')

def generateWMBBoneTable(): #Currently requires nothing
	wmbBoneTable.clear()
	#bone table = pl1040 %TEMP%
	lvl1 = [16, 32, 48, -1, -1, -1, -1, -1, -1, -1, 64, 80, 96, -1, -1, 112, 128, 144, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 160, 176, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 192, 208, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 224, 240, 256, 272, -1, 288, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 304, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 320, 336, 352, 368, 384, 400, 416, 432, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 448]
	lvl2 = []
	lvl3 = [1, 37, 38, 39, 40, 41, 115, 116, 117, 118, 87, 88, 89, 92, 2, 7, 8, 9, 10, 3, 4, 5, 6, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 135, 136, 137, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 109, 110, 111, 105, 106, 107, 108, 101, 102, 103, 104, 97, 98, 99, 100, 93, 94, 95, 96, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 141, 113, 140, 112, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 139, 138, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 91, 90, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 36, 35, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 86, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 42, 44, 43, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 45, 71, 72, 4095, 67, 68, 69, 70, 79, 80, 81, 82, 52, 53, 54, 83, 84, 85, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 73, 74, 75, 76, 77, 78, 46, 47, 48, 49, 50, 51, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 114, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 23, 24, 25, 26, 4095, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 28, 29, 30, 31, 32, 33, 34, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 142, 143, 144, 145, 146, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 4095, 0]
	wmbBoneTable.append(lvl1)
	wmbBoneTable.append(lvl3)
		
def generateWMBHeader(): #WMB Header, requires all WMB
	wmbHeaders.clear()
	bbox1 = [10,10,10]
	bbox2 = [-10,-10,-10]
	bone_count = len(wmbBones)
	bone_table_size = 928 #%TEMP%
	vertex_group_count = len(wmbVertexGroups)
	batches_offset = wmbVertexGroups[2].loopArrayOffset + wmbVertexGroups[2].loopNum * 4
	batches_count = len(wmbBatches)
	lods_offset = batches_offset + batches_count*28
	lods_count = len(wmbLods)
	mesh_mat_offset = lods_offset + lods_count*20 + batches_count*24 + 12
	mesh_mat_pairs = len(wmbMeshMaterialPairs)
	bone_set_count = len(wmbBoneSets)
	bone_map_offset = wmbBoneSets[-1].boneSetOffset + wmbBoneSets[-1].boneIndexNum * 2
	bone_map_count = len(wmbBoneMap)
	mesh_group_count = len(wmbMeshGroups)
	materials_offset = wmbMeshGroups[-1].bonesOffset + wmbMeshGroups[-1].bonesNum*2
	materials_count = len(wmbMaterials)
	#Bound Box
	for meshGroup in wmbMeshGroups:
		#Minimum
		if meshGroup.boundBox1[0] < bbox1[0]:
			bbox1[0] = meshGroup.boundBox1[0]
		if meshGroup.boundBox1[1] < bbox1[1]:
			bbox1[1] = meshGroup.boundBox1[1]
		if meshGroup.boundBox1[2] < bbox1[2]:
			bbox1[2] = meshGroup.boundBox1[2]
		#Maximum
		if meshGroup.boundBox2[0] > bbox2[0]:
			bbox2[0] = meshGroup.boundBox2[0]
		if meshGroup.boundBox2[1] > bbox2[1]:
			bbox2[1] = meshGroup.boundBox2[1]
		if meshGroup.boundBox2[2] > bbox2[2]:
			bbox2[2] = meshGroup.boundBox2[2]
	wmbHeaders.append(wmb3_header(bbox1, bbox2, bone_count, bone_table_size, vertex_group_count, batches_offset, batches_count, lods_count, bone_map_offset, bone_map_count, bone_set_count, materials_offset, materials_count, mesh_group_count, mesh_mat_offset, mesh_mat_pairs))
	
def WriteWMB(dir, DEBUG): 
	#Pre-cleanup
	wmbVerticesOffset = 0
	wmbVertexGroupsOffset = 0
	#Begin
	print('-Starting WMB file writing') 
	print('--Grabbing blender information') 
	generateBlenderInfo()
	generateBlenderDics()
	#Buffers
	wmbBuffer = io.BytesIO()
	wmbHeaderBuffer = io.BytesIO()
	wmbBonesBuffer = io.BytesIO()
	wmbBoneTableBuffer = io.BytesIO()
	wmbVertexGroupsBuffer = io.BytesIO()
	verticesBuffer1 = io.BytesIO()
	verticesBuffer2 = io.BytesIO()
	verticesBuffer3 = io.BytesIO()
	vertexExsBuffer1 = io.BytesIO()
	vertexExsBuffer2 = io.BytesIO()
	vertexExsBuffer3 = io.BytesIO()
	loopsBuffer1 = io.BytesIO()
	loopsBuffer2 = io.BytesIO()
	loopsBuffer3 = io.BytesIO()
	wmbBatchesBuffer = io.BytesIO()
	wmbLodsBuffer = io.BytesIO()
	wmbBatchInfosBuffer = io.BytesIO()
	wmbMeshMatsBuffer = io.BytesIO()
	wmbBoneSetsBuffer = io.BytesIO()
	wmbBoneMapBuffer = io.BytesIO()
	wmbMeshGroupsBuffer = io.BytesIO()
	wmbMaterialsBuffer = io.BytesIO()
	#Null Header
	print('--Writing null WMB header at position: {}'.format(wmbBuffer.tell())) 
	wmbBuffer.write(nullBytes(144))
	#Bones
	print('--Writing WMB bones at position: {}'.format(wmbBuffer.tell())) 
	generateWMBBones()
	for bone in wmbBones:
		#Number and Parent Index
		wmbBonesBuffer.write(to_2Byte(bone.boneNumber))
		wmbBonesBuffer.write(to_2Byte(bone.parentIndex))
		#Local Position/Rotation/Scale
		wmbBonesBuffer.write(to_4Byte(bone.localPosition[0]))
		wmbBonesBuffer.write(to_4Byte(bone.localPosition[1]))
		wmbBonesBuffer.write(to_4Byte(bone.localPosition[2]))
		wmbBonesBuffer.write(to_4Byte(bone.localRotation[0]))
		wmbBonesBuffer.write(to_4Byte(bone.localRotation[1]))
		wmbBonesBuffer.write(to_4Byte(bone.localRotation[2]))
		wmbBonesBuffer.write(to_4Byte(bone.localScale[0]))
		wmbBonesBuffer.write(to_4Byte(bone.localScale[1]))
		wmbBonesBuffer.write(to_4Byte(bone.localScale[2]))
		#World Position/Rotation/Scale/Tpose
		wmbBonesBuffer.write(to_4Byte(bone.worldPosition[0]))
		wmbBonesBuffer.write(to_4Byte(bone.worldPosition[1]))
		wmbBonesBuffer.write(to_4Byte(bone.worldPosition[2]))
		wmbBonesBuffer.write(to_4Byte(bone.worldRotation[0]))
		wmbBonesBuffer.write(to_4Byte(bone.worldRotation[1]))
		wmbBonesBuffer.write(to_4Byte(bone.worldRotation[2]))
		wmbBonesBuffer.write(to_4Byte(bone.worldScale[0]))
		wmbBonesBuffer.write(to_4Byte(bone.worldScale[1]))
		wmbBonesBuffer.write(to_4Byte(bone.worldScale[2]))
		wmbBonesBuffer.write(to_4Byte(bone.worldPositionTpose[0]))
		wmbBonesBuffer.write(to_4Byte(bone.worldPositionTpose[1]))
		wmbBonesBuffer.write(to_4Byte(bone.worldPositionTpose[2]))
	wmbBuffer.write(wmbBonesBuffer.getbuffer())
	wmbBuffer.write(nullBytes(8))
	#Bone Table
	print('--Writing WMB bone index translate table at position: {}'.format(wmbBuffer.tell())) 
	generateWMBBoneTable()
	for i in wmbBoneTable[0]:
		wmbBoneTableBuffer.write(to_2Byte(i))
	for i in wmbBoneTable[1]:
		wmbBoneTableBuffer.write(to_2Byte(i))
	wmbBuffer.write(wmbBoneTableBuffer.getbuffer())
	#Null Vertex Groups
	print('--Writing null WMB vertex groups at position: {}'.format(wmbBuffer.tell())) 
	wmbVertexGroupsOffset = wmbBuffer.tell()
	wmbBuffer.write(nullBytes(144))
	#Vertices/VertexExs/Loops
	print('--Generating WMB vertices/vertexExs/loops/textures/materials/batches') 
	start_time = time.time()
	generateWMBVertices()
	print('---Generating WMB vertices/vertexExs/loops took {} seconds'.format(round(time.time()-start_time, 2))) 
	generateWMBTextures()
	generateWMBMaterials(0)
	generateWMBBatches()
	vertCount = 0
	vertExCount = 0
	loopCount = 0
	for i,mesh in zip(range(len(blenderMeshes)), blenderMeshes):
		if wmbBatches[i].vertexGroupIndex == 0:
			for vertex in wmbMeshVerticesDic[mesh.data.name]:
				verticesBuffer1.write(to_4Byte(vertex.position[0]))
				verticesBuffer1.write(to_4Byte(vertex.position[1]))
				verticesBuffer1.write(to_4Byte(vertex.position[2]))
				verticesBuffer1.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer1.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer1.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer1.write(to_1Byte(255))
				verticesBuffer1.write(to_2Byte(vertex.textureUV[0]))
				verticesBuffer1.write(to_2Byte(vertex.textureUV[1]))
				verticesBuffer1.write(to_1Byte(vertex.boneIndex[0]))
				verticesBuffer1.write(to_1Byte(vertex.boneIndex[1]))
				verticesBuffer1.write(to_1Byte(vertex.boneIndex[2]))
				verticesBuffer1.write(to_1Byte(vertex.boneIndex[3]))
				verticesBuffer1.write(to_1Byte(int(vertex.boneWeight[0]*255)))
				verticesBuffer1.write(to_1Byte(int(vertex.boneWeight[1]*255)))
				verticesBuffer1.write(to_1Byte(int(vertex.boneWeight[2]*255)))
				verticesBuffer1.write(to_1Byte(int(vertex.boneWeight[3]*255)))
				vertCount += 1
			for vertexEx in wmbMeshVertexExsDic[mesh.data.name]:
				vertexExsBuffer1.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer1.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer1.write(to_1Byte(int(vertexEx.color[0]*255)))
				vertexExsBuffer1.write(to_1Byte(int(vertexEx.color[1]*255)))
				vertexExsBuffer1.write(to_1Byte(int(vertexEx.color[2]*255)))
				vertexExsBuffer1.write(to_1Byte(255))
				vertexExsBuffer1.write(to_2Byte(vertexEx.normal[0]))
				vertexExsBuffer1.write(to_2Byte(vertexEx.normal[1]))
				vertexExsBuffer1.write(to_2Byte(vertexEx.normal[2]))
				vertexExsBuffer1.write(to_2Byte(0))
				vertExCount += 1
			for vertex_index in wmbMeshLoopsDic[mesh.data.name]:
				loopsBuffer1.write(to_4Byte(vertex_index))
				loopCount += 1
		elif wmbBatches[i].vertexGroupIndex == 1:
			for vertex in wmbMeshVerticesDic[mesh.data.name]:
				verticesBuffer2.write(to_4Byte(vertex.position[0]))
				verticesBuffer2.write(to_4Byte(vertex.position[1]))
				verticesBuffer2.write(to_4Byte(vertex.position[2]))
				verticesBuffer2.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer2.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer2.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer2.write(to_1Byte(255))
				verticesBuffer2.write(to_2Byte(vertex.textureUV[0]))
				verticesBuffer2.write(to_2Byte(vertex.textureUV[1]))
				verticesBuffer2.write(to_1Byte(vertex.boneIndex[0]))
				verticesBuffer2.write(to_1Byte(vertex.boneIndex[1]))
				verticesBuffer2.write(to_1Byte(vertex.boneIndex[2]))
				verticesBuffer2.write(to_1Byte(vertex.boneIndex[3]))
				verticesBuffer2.write(to_1Byte(int(vertex.boneWeight[0]*255)))
				verticesBuffer2.write(to_1Byte(int(vertex.boneWeight[1]*255)))
				verticesBuffer2.write(to_1Byte(int(vertex.boneWeight[2]*255)))
				verticesBuffer2.write(to_1Byte(int(vertex.boneWeight[3]*255)))
			for vertexEx in wmbMeshVertexExsDic[mesh.data.name]:
				vertexExsBuffer2.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer2.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer2.write(to_1Byte(int(vertexEx.color[0]*255)))
				vertexExsBuffer2.write(to_1Byte(int(vertexEx.color[1]*255)))
				vertexExsBuffer2.write(to_1Byte(int(vertexEx.color[2]*255)))
				vertexExsBuffer2.write(to_1Byte(255))
				vertexExsBuffer2.write(to_2Byte(vertexEx.normal[0]))
				vertexExsBuffer2.write(to_2Byte(vertexEx.normal[1]))
				vertexExsBuffer2.write(to_2Byte(vertexEx.normal[2]))
				vertexExsBuffer2.write(to_2Byte(0))
				vertexExsBuffer2.write(to_2Byte(vertexEx.textureUV3[0]))
				vertexExsBuffer2.write(to_2Byte(vertexEx.textureUV3[0]))
			for vertex_index in wmbMeshLoopsDic[mesh.data.name]:
				loopsBuffer2.write(to_4Byte(vertex_index))	
		elif wmbBatches[i].vertexGroupIndex == 2:
			for vertex in wmbMeshVerticesDic[mesh.data.name]:
				verticesBuffer3.write(to_4Byte(vertex.position[0]))
				verticesBuffer3.write(to_4Byte(vertex.position[1]))
				verticesBuffer3.write(to_4Byte(vertex.position[2]))
				verticesBuffer3.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer3.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer3.write(to_1Byte(vertex.tangent[0]))
				verticesBuffer3.write(to_1Byte(255))
				verticesBuffer3.write(to_2Byte(vertex.textureUV[0]))
				verticesBuffer3.write(to_2Byte(vertex.textureUV[1]))
				verticesBuffer3.write(to_1Byte(vertex.boneIndex[0]))
				verticesBuffer3.write(to_1Byte(vertex.boneIndex[1]))
				verticesBuffer3.write(to_1Byte(vertex.boneIndex[2]))
				verticesBuffer3.write(to_1Byte(vertex.boneIndex[3]))
				verticesBuffer3.write(to_1Byte(int(vertex.boneWeight[0]*255)))
				verticesBuffer3.write(to_1Byte(int(vertex.boneWeight[1]*255)))
				verticesBuffer3.write(to_1Byte(int(vertex.boneWeight[2]*255)))
				verticesBuffer3.write(to_1Byte(int(vertex.boneWeight[3]*255)))
			for vertexEx in wmbMeshVertexExsDic[mesh.data.name]:
				vertexExsBuffer3.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer3.write(to_2Byte(vertexEx.textureUV2[0]))
				vertexExsBuffer3.write(to_2Byte(vertexEx.normal[0]))
				vertexExsBuffer3.write(to_2Byte(vertexEx.normal[1]))
				vertexExsBuffer3.write(to_2Byte(vertexEx.normal[2]))
				vertexExsBuffer3.write(to_2Byte(0))
			for vertex_index in wmbMeshLoopsDic[mesh.data.name]:
				loopsBuffer3.write(to_4Byte(vertex_index))
	print('---Writing {} vertices at position: {}'.format(vertCount, wmbBuffer.tell())) 
	wmbVerticesOffset = wmbBuffer.tell()
	wmbBuffer.write(verticesBuffer1.getbuffer())
	print('---Writing {} vertexExs at position: {}'.format(vertExCount, wmbBuffer.tell()))
	wmbBuffer.write(vertexExsBuffer1.getbuffer())
	print('---Writing {} loops at position: {}'.format(loopCount, wmbBuffer.tell()))
	wmbBuffer.write(loopsBuffer1.getbuffer())
	print('---Writing the second group of vertices/vertexEx/loops at position: {}'.format(wmbBuffer.tell())) 
	wmbBuffer.write(verticesBuffer2.getbuffer())
	wmbBuffer.write(vertexExsBuffer2.getbuffer())
	wmbBuffer.write(loopsBuffer2.getbuffer())
	print('---Writing the third group of vertices/vertexEx/loops at position: {}'.format(wmbBuffer.tell())) 
	wmbBuffer.write(verticesBuffer3.getbuffer())
	wmbBuffer.write(vertexExsBuffer3.getbuffer())
	wmbBuffer.write(loopsBuffer3.getbuffer())
	print('--Finished writing WMB vertices/vertexExs/loops in {} seconds'.format(round(time.time()-start_time, 2))) 
	#Batches
	print('--Writing WMB batches at position: {}'.format(wmbBuffer.tell())) 
	for batch in wmbBatches:
		wmbBatchesBuffer.write(to_4Byte(batch.vertexGroupIndex))
		wmbBatchesBuffer.write(to_4Byte(batch.boneSetIndex))
		wmbBatchesBuffer.write(to_4Byte(batch.vertexStart))
		wmbBatchesBuffer.write(to_4Byte(batch.loopStart))
		wmbBatchesBuffer.write(to_4Byte(batch.vertexNum))
		wmbBatchesBuffer.write(to_4Byte(batch.loopNum))
		wmbBatchesBuffer.write(to_4Byte(batch.primitiveNum))
	wmbBuffer.write(wmbBatchesBuffer.getbuffer())
	#Lods
	print('--Writing WMB lods at position: {}'.format(wmbBuffer.tell())) 
	generateWMBLods(wmbBuffer.tell())
	for lod in wmbLods:
		wmbLodsBuffer.write(to_4Byte(lod.nameOffset))
		wmbLodsBuffer.write(to_4Byte(lod.lodLevel))
		wmbLodsBuffer.write(to_4Byte(lod.batchStart))
		wmbLodsBuffer.write(to_4Byte(lod.batchInfoOffset))
		wmbLodsBuffer.write(to_4Byte(lod.batchInfoNum))
	wmbBuffer.write(wmbLodsBuffer.getbuffer())
	#Batch Infos
	print('--Writing WMB batch infos at position: {}'.format(wmbBuffer.tell())) 
	for batchInfo in wmbBatchInfos:
		wmbBatchInfosBuffer.write(to_4Byte(batchInfo.vertexGroupIndex))
		wmbBatchInfosBuffer.write(to_4Byte(batchInfo.meshIndex))
		wmbBatchInfosBuffer.write(to_4Byte(batchInfo.materialIndex))
		wmbBatchInfosBuffer.write(to_4Byte(-1))
		wmbBatchInfosBuffer.write(to_4Byte(batchInfo.meshMaterialPairIndex))
		wmbBatchInfosBuffer.write(to_4Byte(-1))
	wmbBuffer.write(wmbBatchInfosBuffer.getbuffer()) 
	#Lod Name
	print('--Writing lod name at position: {}'.format(wmbBuffer.tell())) 
	wmbBuffer.write(to_4Byte('LOD0')+nullBytes(7))
	#Mesh Material Pairs
	print('--Writing WMB mesh material pairs at position: {}'.format(wmbBuffer.tell())) 
	for meshMat in wmbMeshMaterialPairs:
		wmbMeshMatsBuffer.write(to_4Byte(meshMat.meshIndex))
		wmbMeshMatsBuffer.write(to_4Byte(meshMat.materialIndex))
	wmbBuffer.write(wmbMeshMatsBuffer.getbuffer())
	#Bone Sets
	print('--Writing WMB bone sets at position: {}'.format(wmbBuffer.tell())) 
	generateWMBBoneSets(wmbBuffer.tell())
	for boneSet in wmbBoneSets:
		wmbBoneSetsBuffer.write(to_4Byte(boneSet.boneSetOffset))
		wmbBoneSetsBuffer.write(to_4Byte(boneSet.boneIndexNum))
	for boneSet in wmbBoneSets:
		for boneIndex in boneSet.boneArray:
			wmbBoneSetsBuffer.write(to_2Byte(boneIndex))
	wmbBuffer.write(wmbBoneSetsBuffer.getbuffer()) 
	#Bone Map
	print('--Writing WMB bone map at position: {}'.format(wmbBuffer.tell())) 
	generateWMBBoneMap()
	for boneIndex in wmbBoneMap:
		wmbBoneMapBuffer.write(to_4Byte(boneIndex))
	wmbBuffer.write(wmbBoneMapBuffer.getbuffer())
	#Mesh Groups
	print('--Writing WMB mesh groups at position: {}'.format(wmbBuffer.tell())) 
	generateWMBMeshGroups(wmbBuffer.tell())
	for meshGroup in wmbMeshGroups:
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.nameOffset))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox1[0]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox1[1]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox1[2]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox2[0]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox2[1]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.boundBox2[2]))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.materialsOffset))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.materialsNum))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.bonesOffset))
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.bonesNum))
	for meshGroup in wmbMeshGroups:
		wmbMeshGroupsBuffer.write(to_4Byte(meshGroup.name))
		for matIndex in meshGroup.materialIndexArray:
			wmbMeshGroupsBuffer.write(to_2Byte(matIndex))
		for boneIndex in meshGroup.boneIndexArray:
			wmbMeshGroupsBuffer.write(to_2Byte(boneIndex))
	#if len(wmbMeshGroupsBuffer.getbuffer()) % 8 != 0:	%TEMP%
	#	padding = 8 - len(wmbMeshGroupsBuffer.getbuffer()) % 8
	#	wmbMeshGroupsBuffer.write(nullBytes(padding))
	wmbBuffer.write(wmbMeshGroupsBuffer.getbuffer())
	#Materials
	print('--Writing WMB materials at position: {}'.format(wmbBuffer.tell())) 
	wmbMaterials.clear()
	generateWMBMaterials(wmbBuffer.tell())
	for material in wmbMaterials:
		wmbMaterialsBuffer.write(material.first8Bytes)
		wmbMaterialsBuffer.write(to_4Byte(material.materialNameOffset))
		wmbMaterialsBuffer.write(to_4Byte(material.shaderNameOffset))
		wmbMaterialsBuffer.write(to_4Byte(material.techniqueNameOffset))
		wmbMaterialsBuffer.write(to_4Byte(1))
		wmbMaterialsBuffer.write(to_4Byte(material.textureOffset))
		wmbMaterialsBuffer.write(to_4Byte(material.textureNum))
		wmbMaterialsBuffer.write(to_4Byte(material.paramOffset))
		wmbMaterialsBuffer.write(to_4Byte(material.paramNum))
		wmbMaterialsBuffer.write(to_4Byte(material.varOffset))
		wmbMaterialsBuffer.write(to_4Byte(material.varNum))
	for material in wmbMaterials:
		wmbMaterialsBuffer.write(to_4Byte(material.materialName))
		wmbMaterialsBuffer.write(to_4Byte(material.shaderName))
		wmbMaterialsBuffer.write(to_4Byte(material.techniqueName))
		#Textures
		for texOffset,texIdentifier in zip(material.textureOffsetArray, material.textureIdentifierArray):
			wmbMaterialsBuffer.write(to_4Byte(texOffset))
			wmbMaterialsBuffer.write(to_bytes(texIdentifier))
		for texName in material.textureNames:
			wmbMaterialsBuffer.write(to_4Byte(texName))
		#if len(wmbMaterialsBuffer.getbuffer()) % 8 != 0:  #%TEST%
		#	padding = len(wmbMaterialsBuffer.getbuffer()) % 8
		#	wmbMaterialsBuffer.write(nullBytes(padding))
		#Parameters
		for i,pIndex,pOffset in zip(range(material.paramNum), material.paramIndexArray, material.paramOffsetArray):
			wmbMaterialsBuffer.write(to_4Byte(pIndex))
			wmbMaterialsBuffer.write(to_4Byte(pOffset))
			wmbMaterialsBuffer.write(to_4Byte(material.paramNumArray[i]))
		wmbMaterialsBuffer.write(nullBytes(8))
		for param in material.paramArray:
			wmbMaterialsBuffer.write(to_4Byte(param))
		#Variables
		for vNameOffset, vValue in zip(material.varNameOffsetsArray, material.varValues):
			wmbMaterialsBuffer.write(to_4Byte(vNameOffset))
			wmbMaterialsBuffer.write(to_4Byte(vValue))
		for vName in material.varNames:
			wmbMaterialsBuffer.write(to_4Byte(vName))
	wmbBuffer.write(wmbMaterialsBuffer.getbuffer())
	#Vertex Groups
	wmbBuffer.seek(wmbVertexGroupsOffset)
	print('--Writing WMB vertex groups at position: {}'.format(wmbBuffer.tell())) 
	generateWMBVertexGroups(wmbVerticesOffset)
	for i,vertexGroup in zip(range(len(wmbVertexGroups)), wmbVertexGroups):
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexArrayOffset))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexExArrayOffset))
		wmbVertexGroupsBuffer.write(to_4Byte(0))
		wmbVertexGroupsBuffer.write(to_4Byte(0))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexSize))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexExSize))
		wmbVertexGroupsBuffer.write(to_4Byte(0))
		wmbVertexGroupsBuffer.write(to_4Byte(0))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexNum))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.vertexExFlags))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.loopArrayOffset))
		wmbVertexGroupsBuffer.write(to_4Byte(vertexGroup.loopNum))
	wmbBuffer.write(wmbVertexGroupsBuffer.getbuffer())
	#WMB Header
	wmbBuffer.seek(0)
	print('--Writing WMB header at position: {}'.format(wmbBuffer.tell())) 
	generateWMBHeader()
	wmbHeader = wmbHeaders[0]
	wmbHeaderBuffer.write(wmbHeader.magicNumber)
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.version))
	wmbHeaderBuffer.write(to_4Byte(0))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.flags))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox1[0]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox1[1]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox1[2]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox2[0]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox2[1]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boundingBox2[2]))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneTableOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneTableSize))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.vertexGroupOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.vertexGroupNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.batchOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.batchNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.lodOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.lodNum))
	wmbHeaderBuffer.write(to_4Byte(0))
	wmbHeaderBuffer.write(to_4Byte(0))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneMapOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneMapNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneSetOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.boneSetNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.materialOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.materialNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.meshGroupOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.meshGroupNum))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.meshMaterialOffset))
	wmbHeaderBuffer.write(to_4Byte(wmbHeader.meshMaterialNum))
	wmbHeaderBuffer.write(nullBytes(16))
	wmbBuffer.write(wmbHeaderBuffer.getbuffer())
	#File Write
	print('-Finished writing the WMB file to: ' + dir) 
	wmb_fp = open(dir, 'wb')
	wmb_fp.write(wmbBuffer.getbuffer())
	#File/Buffers Close
	wmb_fp.close()
	wmbBuffer.close()
	wmbHeaderBuffer.close()
	wmbBonesBuffer.close()
	wmbBoneTableBuffer.close()
	wmbVertexGroupsBuffer.close()
	verticesBuffer1.close()
	verticesBuffer2.close()
	verticesBuffer3.close()
	vertexExsBuffer1.close()
	vertexExsBuffer2.close()
	vertexExsBuffer3.close()
	loopsBuffer1.close()
	loopsBuffer2.close()
	loopsBuffer3.close()
	wmbBatchesBuffer.close()
	wmbLodsBuffer.close()
	wmbBatchInfosBuffer.close()
	wmbMeshMatsBuffer.close()
	wmbBoneSetsBuffer.close()
	wmbBoneMapBuffer.close()
	wmbMeshGroupsBuffer.close()
	wmbMaterialsBuffer.close()

def WriteWTA(out_path, DEBUG):
	print('-Starting WTA file writing') 
	print('--Grabbing blender information') 
	generateBlenderInfo()
	generateBlenderDics()
	generateWMBTextures()
	albedo_positions = []
	identifiers = []
	dds_dir = ''
	for texture,i in zip(wmbTextures,range(len(wmbTextures))):
		print('--Getting dds directory')
		img_fp = texture.filepath.split('\\')[0:-1]
		for j in range(len(img_fp)):
			dds_dir += (img_fp[j] + '\\')
		print('--Getting albedo positions')
		if texture.textureType == 'g_AlbedoMap':
			albedo_positions.append(i)
		print('--Getting texture itendifiers')
		identifiers.append(texture.identifier)
	wta_gen.main(out_path, dds_dir, albedo_positions, identifiers)
	print('-Finished writing WTA at {}'.format(out_path))
	
def WriteWTP(out_dir, DEBUG):
	print('-Starting WTP file writing')
	print('--Grabbing blender information')
	generateBlenderInfo()
	generateBlenderDics()
	generateWMBTextures()
	dds_dir = ''
	print('--Getting dds directory')
	img_fp = wmbTextures[0].filepath.split('\\')[0:-1]
	for j in range(len(img_fp)):
		dds_dir += (img_fp[j] + '\\')
	wtp_gen.main(dds_dir, out_path)
	print('-Finished writing WTP at {}'.format(out_path))	

#def WriteDAT() #this involves more than the wta/wtp/wmb so leaving it out for now
	
#if __name__ == '__main__':
#	usage = '\nUsage:\n    blender --background --python output_path\n    Eg: blender --background --python C:\\NierA\\pl000d.wmb'
#	if len(sys.argv) < 4:
#		print(usage)
#		exit()
#	if len(sys.argv) == 4:
#		WriteWMB(sys.argv[3], False)
#	if len(sys.argv) > 4:
#		WriteWMB(sys.argv[3], True)

#WriteWMB('C:\\Users\\User\\Downloads\\NierA\\temp\\2\\pl1040.wmb', True)
#WriteWMB('C:\\NierA\\temp\\6\\pl1040.wmb', True)

shader_names = [
	("CLT00_XXXXX", "Cloth Shader", "Nier:Automata Cloth Shader"),
	("PBS00_XXXXX", "Metallic Shader", "Nier:Automata Metallic Shader"),
	("SKN00_XXXXX", "Skin Shader", "Nier:Automata Skin Shader"),
	("Eye00_XXXXX", "Eye Shader", "Nier:Automata Eye Shader"),
	("Hair01_XXXXX", "Hair Shader", "Nier:Automata Hair Shader"), 
	("CNS00_XXXXX", "Eye Shadow Shader", "Nier:Automata Eye Shadow Shader"),
	]

#bpy.types.Material.shader_name = bpy.props.EnumProperty(items=shader_names, name="WMB Material Shader", default="CLT00_XXXXX")
#bpy.types.Bone.boneID = bpy.props.IntProperty(name="WMB Bone ID",min=-1, max=4095, default=-1)
