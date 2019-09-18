import os
import sys
from util import *

class WMB_Header(object):
	def __init__(self, bbox1, bbox2, bone_count, bone_table_size, vertex_group_count, batches_offset, batches_count, lods_offset, lods_count, bone_map_offset, bone_map_count, bone_set_count, materials_offset, materials_count, mesh_group_count, mesh_mat_offset, mesh_mat_pair):
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

class wmb3_vertexGroupHeader(object):
	"""docstring for wmb3_vertexGroupHeader"""
	def __init__(self, vertex_offset, vertex_type, vertex_num, face_num): #(int, string, int, int)
		super(wmb3_vertexHeader, self).__init__()
		self.vertexArrayOffset = vertex_offset #int	
		self.vertexNum = vertex_num
		self.vertexSize = 0 
		self.vertexExArrayOffset = 0
		self.vertexExFlags = 0
		self.vertexExSize = 0
		self.faceArrayOffset = 0
		self.faceNum = face_num
		self.unknowns = 0

		if vertex_type == 0xb:
			vertexSize = 28
			vertexExFlags = 11
			vertexExSize = 20
		if vertex_type == 0x7:
			vertexSize = 28
			vertexExFlags = 7
			vertexExSize = 12
		if vertex_type == 0xa:
			vertexSize = 28
			vertexExFlags = 10
			vertexExSize = 16
			
		vertexExArrayOffset = vertexArrayOffset + vertexNum*vertexSize + 8
		faceArrayOffset = vertexExArrayOffset + vertexNum*vertexExSize
				
class wmb3_vertex(object):
	"""docstring for wmb3_vertex"""
	def __init__(self, position, tangent, uv, bone_index, bone_weight): #(float 3tuple, int 3tuple, float 2tuple, int 4tuple, int 4tuple)
		super(wmb3_vertex, self).__init__()
		self.position = position 
		self.tangent = ((tangent[0] * 255) / 2, (tangent[1] * 255) / 2, (tangent[2] * 255) / 2, -1)					
		self.textureUV = uv 	
		self.boneIndex = bone_index
		self.boneWeight = bone_weight
		
class wmb3_vertexEx1(object): #0xb
	"""docstring for wmb3_vertexEx1"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx1 self).__init__()
		self.textureUV2 = uv
		self.color = (color[0], color[1], color[2], -1)
		self.normal = (normal[0], normal[1], normal[2], 0)
		self.textureUV3 = textureUV2
		
class wmb3_vertexEx2(object): #0x7
	"""docstring for wmb3_vertexEx2"""
	def __init__(self, uv, normal): #(float 2tuple, float 3tuple)
		super(wmb3_vertexEx2 self).__init__()
		self.textureUV2 = uv
		self.normal = (normal[0], normal[1], normal[2], 0)
			
class wmb3_vertexEx3(object): #0xa
	"""docstring for wmb3_vertexEx3"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx3 self).__init__()
		self.textureUV2 = uv
		self.color = (color[0], color[1], color[2], -1)
		self.normal = (normal[0], normal[1], normal[2], 0)

class wmb3_bone(object): #88 bytes (last one has extra 8 bytes)
	"""docstring for wmb3_bone"""
	def __init__(self, number, parent_index, parent_bone, world_pos, world_rot):	#(int, int, bone, tuple, tuple)
		super(wmb3_bone, self).__init__()
		self.boneNumber = number #used for physics in .bxm files
		self.parentIndex = parent_bone
		#parent_world_pos - world_pos
		self.local_position = (parent_bone.world_pos[0] - world_pos[0], parent_bone.world_pos[1] - world_pos[1], parent_bone.world_pos[2] - world_pos[2])
		#parent_world_rot - world_rot
		self.local_rotation = (parent_bone.world_rot[0] - world_rot[0],  parent_bone.world_rot[1] - world_rot[1],  parent_bone.world_rot[2] - world_rot[2])
		self.localScale = (1.0, 1.0, 1.0) 
		#armature.pose.bone.head
		self.worldPosition =  world_pos
		#armature.pose.bone.matrix.to_euler()
		self.worldRotation = world_rot
		self.worldScale = (1.0, 1.0, 1.0)
		#usually equal to world_pos, might not be needed ingame (test)
		self.worldPositionTpose = worldPosition
		
class wmb3_batch(object):
	"""docstring for wmb3_batch"""
	def __init__(self, offset, vertex_group_index, bone_set_index, vertex_start, index_start, vertex_num, index_num, primitive_num): #(int, int, int, int, int, int, int, int)
		super(wmb3_batch, self).__init__()
		self.vertexGroupIndex = vertex_group_index
		self.boneSetIndex = bone_set_index
		self.vertexStart = vertex_start
		self.indexStart = index_start
		self.vertexNum = vertex_num
		self.indexNum = index_num
		self.primitiveNum = primitive_num
		
class wmb3_lod(object):
	"""docstring for wmb3_lod"""
	def __init__(self, offset, lod_level, batch_start, batch_info_num): #(int, int, int, int)
		super(wmb3_lod, self).__init__()
		self.lodLevel = lod_level
		self.batchStart = batch_start
		self.batchInfoOffset = offset
		self.batchInfoNum = batch_info_num
		self.nameOffset = batchInfoOffset + batchInfoNum * 24
		
class wmb3_batchInfo(object):
	"""docstring for wmb3_batchInfo"""
	def __init__(self, vertex_group_index, mesh_index, mesh_mat_pair_index): #(int, int, int, int)
		super(wmb3_batchInfo, self).__init__()
		self.vertexGroupIndex = vertex_group_index
		self.meshIndex = mesh_index
		self.materialIndex = material_index
		self.unknown1 = -1
		self.meshMaterialPairIndex = mesh_mat_pair_index
		self.unknown2 = -1

class wmb3_meshMaterialPair(object): #(int, int)
	"""docstring for wmb3_meshMaterialPair"""
	def __init__(self, mesh_index, material_index):
		super(wmb3_meshMaterialPair, self).__init__()
		self.meshIndex = mesh_index
		self.materialIndex = material_index
		
class wmb3_boneSet(object): #(int, array)
	"""docstring for wmb3_boneSet"""
	def __init__(self, offset, bone_array):
		super(wmb3_boneSet, self).__init__()
		self.boneSetOffset = offset
		self.boneIndexNum = len(boneArray)
		self.boneArray = bone_array

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
		self.first8Bytes = b'\xe0\x07\x07\x00\x05\x00\x0f\x00'
		self.materialNameOffset = offset
		self.materialName = material_name
		self.shaderNameOffset = materialNameOffset + len(materialName) + 1
		self.shaderName = shader_name
		self.techniqueNameOffset = shaderNameOffset + len(shaderName) + 1
		self.techniqueName = ''
		self.textureOffset = techniqueNameOffset + len(techniqueName) + 1
		textureArray = texture_array
		self.textureNum = 0
		self.textureOffsetArray = [] #int
		self.textureIdentifierArray = [] #string
		self.textureNames = [] #string
		self.paramOffset = textureOffsetArray[-1] + len(textureNames[-1]) + 1
		self.paramNum = 0
		self.paramIndexArray = [] #int
		self.paramOffsetArray = [] #int
		self.paramNumArray = [] #int
		params = 0
		self.paramArray = [] #float
		self.varOffset = paramOffsetArray[-1] + paramNumArray[-1] * 4
		self.varNum = 0
		self.varNameOffestsArray = [varOffset+496] #int
		self.varValues = [] #float
		self.varNames = [] #string
		
		#Textures
		textureOffsetArray.append(textureOffset + textureNum*8)
		for i in range(len(textureArray)):
			textureNum += 1
			textureNames.append(textureArray[i].textureType)
			if i > 0:
				textureOffsetArray.append(textureOffset + textureNum*8 + len(textureNames[i-1]) + 1)
			textureIdentifierArray.append(textureArray[i].identifier)

		#Shader/Material Variables
		if shaderName == 'CLT00_XXXXX':
			techniqueName = 'Default'
			paramNum = 2
			varNum = 62
			params = 48
			paramArray = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.2, 0.0, 0.0, 0.3, 1.0, 2.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 0.0, 1.0, 0.2, 0.6, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_FuzzColorCorrection_X', 'g_FuzzColorCorrection_Y', 'g_FuzzColorCorrection_Z', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_FuzzMul', 'g_FuzzReverse', 'g_FuzzShadowLowerLimit', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceMetalic', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.1, 0.1, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.3, 0.2, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.4, 0.0, 0.0, 0.4, 0.0, 0.0, 0.0]

		elif shaderName == 'PBS00_XXXXX':

			techniqueName = 'Default'
			paramNum = 2
			params = 36
			varNum = 50
			paramArray = [1, 0, 0, 0, 0, 0, 1, 1, 50, 50, 1, 0, 0, 0, 0, 0, 0.5, 0.5, 0, 0.2, 0, 0, 0, 0, 1, 0.4, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Decal', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_Tile_X', 'g_Tile_Y', 'g_UV2Use', 'g_UseDetailNormalMap', 'g_UseEnvWet', 'g_UseLightMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_UseOcclusionMap', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]

		elif shaderName == 'SKN00_XXXXX':
			techniqueName = 'Default'
			paramNum = 2
			params = 44
			varNum = 55
			paramArray = [1, 0, 0, 0, 0, 0, 0, 0, 20, 20, 1, 0, 0.5, 0.5, 0.5, 0, 0.2, 0, 0, 0, 1, 1.5, 1, 0, 0.291777, 0.039546, 0.039546, 0, 0.806955, 0.300551, 0.201554, 5, 0, 1, 0.63, 0.8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_Glossiness', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OcclusionColor_X', 'g_OcclusionColor_Y', 'g_OcclusionColor_Z', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_TransMissionColor_X', 'g_TransMissionColor_Y', 'g_TransMissionColor_Z', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetMagAlbedo', 'g_bAlbedoOverWrite', 'g_bDispCurvature', 'g_bDispSpecular', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite', 'g_bUseCurvatureMap', 'g_rho_s', 'g_tuneCurvature']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 50.0, 50.0, 5.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.29177701473236084, 0.03954600170254707, 0.03954600170254707, 0.0, 1.0, 0.8069549798965454, 0.30055099725723267, 0.20155400037765503, 1.0, 1.0, 1.0, 0.8, 0.6299999952316284, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]

		elif shaderName == 'Eye00_XXXXX':
			techniqueName = 'Default'
			paramNum = 2
			params = 32
			varNum = 39
			paramArray = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 0.8, 0.0, 0.4, 1.0, 0.6, 0.02, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_AddEnvCubeIntensity', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_Anisotropic', 'g_Glossiness', 'g_GlossinessIris', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_LightIrisIntensity', 'g_Metallic', 'g_MetallicIris', 'g_NormalReverse', 'g_ParallaxStrength', 'g_ReflectionIntensity', 'g_UseNormalMap', 'g_bAlbedoOverWrite', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.8, 0.4, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6, 0.0, 1.0, 0.0, 0.02, 1.0, 1.0, 0.0, 1.0, 1.0]

		elif shaderName == 'Hair01_XXXXX':
			techniqueName = 'Default'
			paramNum = 2
			params = 52
			varNum = 62
			paramArray = [1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0.514908, 0.473523, 0.428685, 0, 0.1, 0.2, 0, 0, 0.8, 4, 1, 0, 0, 0, 0, 0, 1, 0.1, 70, 0, 10, 1, 2, 0.02, 0.8, 0.622, -0.36, 0, 0, 1, 0.63, 0.5, 1, 0.5, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_AmbientLightIntensity', 'g_AnisoLightMode', 'g_AnisoLightMode2', 'g_Anisotropic', 'g_Anisotropic_X', 'g_Anisotropic_Y', 'g_DetailNormalTile_X', 'g_DetailNormalTile_Y', 'g_EnvRoughnessHosei', 'g_FuzzExponent', 'g_FuzzMaskEffective', 'g_Glossiness', 'g_HilIghtIntensity', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_LightIntensity', 'g_Metallic', 'g_NoiseTile_X', 'g_NoiseTile_Y', 'g_NormalReverse', 'g_ObjWetStrength', 'g_OffShadowCast', 'g_ReflectionIntensity', 'g_SecondaryGlossiness', 'g_SecondaryMetalic', 'g_SecondarySpecShift', 'g_SpecShift', 'g_UseDetailNormalMap', 'g_UseNormalMap', 'g_UseObjWet', 'g_WetConvergenceGlossiness', 'g_WetConvergenceHLI', 'g_WetConvergenceSecondaryGlossiness', 'g_WetMagAlbedo', 'g_WetMagNoiseTile_X', 'g_WetMagNoiseTile_Y', 'g_bAlbedoOverWrite', 'g_bDispNoise', 'g_bGlossinessOverWrite', 'g_bMetalicOverWrite']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5149080157279968, 0.47352299094200134, 0.4286850094795227, 1.0, 0.0, 1.0, 0.0, 0.1, 70.0, 1.0, 1.0, 2.0, 4.0, 1.0, 0.1, 0.8, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.2, 10.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.622, 0.8, -0.36, 0.02, 0.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.63, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0]

		elif shaderName == 'CNS00_XXXXX':
			techniqueName = 'Multiplication'
			paramNum = 2
			params = 28
			varNum = 34
			paramArray = [0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0.5, 0.5, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
			varNames = ['Binormal0', 'Color0', 'Normal', 'Position', 'Tangent0', 'TexCoord0', 'TexCoord1', 'g_1BitMask', 'g_AlbedoColor_X', 'g_AlbedoColor_Y', 'g_AlbedoColor_Z', 'g_Decal', 'g_Intensity', 'g_InvalidFog', 'g_IsSwatchRender', 'g_LighIntensity0', 'g_LighIntensity1', 'g_LighIntensity2', 'g_LightColor0_X', 'g_LightColor0_Y', 'g_LightColor0_Z', 'g_LightColor1_X', 'g_LightColor1_Y', 'g_LightColor1_Z', 'g_LightColor2_X', 'g_LightColor2_Y', 'g_LightColor2_Z', 'g_Tile_X', 'g_Tile_Y', 'g_UseMultiplicationBlend', 'g_UseSubtractionBlend', 'g_UvAnimation_X', 'g_UvAnimation_Y', 'g_bAlbedoOverWrite']
			for i in range(varNum):
				varNameOffestsArray.append(varNameOffestsArray[i] + (len(varNames[i]) + 1))
			varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]

		#Parameters
		paramIndexArray = [0, -1]
		paramNumArray = [params - 4, 4]
		paramOffsetArray = [paramOffset + paramNum * 12, paramOffset + paramNum * 12 + paramNumArray[0] * 4]
			
		#debug
		print('Name: ' + materialName)
		print('Shader: ' + shaderName)
				
class wmb3_boneMap(object):
	"""docstring for wmb3_boneMap"""
	def __init__(self, bone_array):
		super(wmb3_boneMap, self).__init__()
		self.bones = bone_array
		
class wmb3_meshGroup(object):
	"""docstring for wmb3_meshGroup"""
	def __init__(self, info_offset, name, bbox1, bbox2, material_index_array, bone_index_array): #(int, string, float 3tuple, float 3tuple, array, array)
		super(wmb3_meshGroup, self).__init__()
		self.name = name
		self.nameOffset = info_offset
		self.boundBox1 = bbox1
		self.boundBox2 = bbox2
		self.materialIndexArray = material_index_array
		self.materialsOffset = nameOffset + len(name) + 1
		self.materialsNum = len(material_index_array)
		self.boneIndexArray = bone_index_array
		self.bonesOffset = materialsOffset + materialNum * 2
		self.bonesNum = len(bone_index_array)
		
