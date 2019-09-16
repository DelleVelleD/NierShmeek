import os
import sys
from util import *

class WMB_Header(object):
	def __init__(self, bBox2, bBox3, bBox4, bBox5, bBox6, boneCount, vertexGroupCount, meshCount, meshGroupInfoArrayCount, boneMapCount, bonesetCount, materialCount, meshGroupCount):
		self.super(WMB_Header, self).__init__()
		self.magicNumber = b'WMB3'
		self.version = '20160116' #always this
		self.unknown08 = 0 #? always zero
		self.flags = 4294901770 #? always this
		self.bounding_box1 = 0 #always zero
		self.bounding_box2 = bBox2
		self.bounding_box3 = bBox3
		self.bounding_box4 = bBox4
		self.bounding_box5 = bBox5
		self.bounding_box6 = bBox6
		self.boneArrayOffset = 144
		self.boneCount = boneCount
		self.boneIndexTranslateTableOffset = boneArrayOffset + (boneCount * 88)
		self.boneIndexTranslateTableSize = 0 #?
		self.vertexGroupArrayOffset = 0 #?
		self.vertexGroupCount = vertexGroupCount
		self.meshArrayOffset = 0 #?
		self.meshCount = meshCount
		self.meshGroupInfoArrayHeaderOffset = meshArrayOffset + (meshCount * 28)
		self.meshGroupInfoArrayCount = meshGroupInfoArrayCount
		self.unknownChunk2Offset = 0 #?
		self.unknownChunk2DataCount = 0 #?
		self.boneMapOffset = 0 #?
		self.boneMapCount = boneMapCount
		self.bonesetOffset = meshMaterialOffset + (meshMaterialCount * 8)
		self.bonesetCount = bonesetCount
		self.materialArrayOffset = 0 #?
		self.materialCount = materialCount
		self.meshGroupOffset = boneMapOffset + (boneMapCount * 4)
		self.meshGroupCount = meshGroupCount
		self.meshMaterialOffset = 0 #?
		self.meshMaterialCount = 0 #?
		self.unknown84 = 0
		self.unknown88 = 0
		self.unknown8C = 0

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
		self.positionX = position[0] 
		self.positionY = position[1] 
		self.positionZ = position[2] 
		self.tangentX = (tangent[0] * 255) / 2		
		self.tangentY = (tangent[1] * 255) / 2	
		self.tangentZ = (tangent[2] * 255) / 2	
		self.tangentD = -1						
		self.textureU = uv[0]	
		self.textureV = uv[1] 	
		self.boneIndex1 = bone_index[0]
		self.boneIndex2 = bone_index[1]
		self.boneIndex3 = bone_index[2]
		self.boneIndex4 = bone_index[3]
		self.boneWeight1 = bone_weight[0]
		self.boneWeight2 = bone_weight[1]
		self.boneWeight3 = bone_weight[2]
		self.boneWeight4 = bone_weight[3]
		
class wmb3_vertexEx1(object): #0xb
	"""docstring for wmb3_vertexEx1"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx1 self).__init__()
		self.textureU2 = uv[0]
		self.textureV2 = uv[1]
		self.colorX = color[0]
		self.colorY = color[1]
		self.colorZ = color[2]
		self.colorD = -1
		self.normalX = normal[0]
		self.normalY = normal[1]
		self.normalZ = normal[2]
		self.normalD = 0
		self.textureU3 = textureU2
		self.textureV3 = textureV2
		
class wmb3_vertexEx2(object): #0x7
	"""docstring for wmb3_vertexEx2"""
	def __init__(self, uv, normal): #(float 2tuple, float 3tuple)
		super(wmb3_vertexEx2 self).__init__()
		self.textureU2 = uv[0]
		self.textureV2 = uv[1]
		self.normalX = normal[0]
		self.normalY = normal[1]
		self.normalZ = normal[2]
		self.normalD = 0
			
class wmb3_vertexEx3(object): #0xa
	"""docstring for wmb3_vertexEx3"""
	def __init__(self, uv, color, normal): #(float 2tuple, int 3tuple, float 3tuple)
		super(wmb3_vertexEx3 self).__init__()
		self.textureU2 = uv[0]
		self.textureV2 = uv[1]
		self.colorX = color[0]
		self.colorY = color[1]
		self.colorZ = color[2]
		self.colorD = -1
		self.normalX = normal[0]
		self.normalY = normal[1]
		self.normalZ = normal[2]
		self.normalD = 0	

class wmb3_bone(object): #88 bytes (last one has extra 8 bytes)
	"""docstring for wmb3_bone"""
	def __init__(self, number, parentIndex, parentBone, worldPosition, worldRotation):	#(int, int, bone, tuple, tuple)
		super(wmb3_bone, self).__init__()
		self.boneNumber = number #seems it can be anything, even duplicates
		self.parentIndex = parentIndex

		#parent_world_pos - world_pos
		self.local_positionX = parentBone.world_positionX - world_positionX
		self.local_positionY = parentBone.world_positionY - world_positionY
		self.local_positionZ = parentBone.world_positionZ - world_positionZ
		
		#parent_world_rot - world_rot
		self.local_rotationX = parentBone.world_rotationX - world_rotationX	 
		self.local_rotationY = parentBone.world_rotationY - world_rotationY	 
		self.local_rotationZ = parentBone.world_rotationZ - world_rotationZ	 

		#always 1.0
		self.local_scaleX = 1.0 
		self.local_scaleY = 1.0 
		self.local_scaleZ = 1.0 

		#armature.bone.head_local
		self.world_positionX =  worldPosition[0]
		self.world_positionY =  worldPosition[1]
		self.world_positionZ =  worldPosition[2]
		
		#?
		self.world_rotationX = worldRotation[0]
		self.world_rotationY = worldRotation[1] 
		self.world_rotationZ = worldRotation[2]

		#always 1.0
		self.world_scaleX = 1.0 
		self.world_scaleY = 1.0 
		self.world_scaleZ = 1.0 
		
		#usually equal to world_pos
		self.world_position_tposeX = wpX 
		self.world_position_tposeY = wpY  
		self.world_position_tposeZ = wpZ 
		
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
	def __init__(self, mesh_id, material_id):
		super(wmb3_meshMaterialPair, self).__init__()
		self.meshID = mesh_id
		self.materialID = material_id
		
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
		self.textureOffsetArray = []
		self.textureIdentifierArray = []
		self.textureNames = [] #''
		self.paramOffset = textureOffsetArray[-1] + len(textureNames[-1]) + 1
		self.paramNum = 0
		self.paramIndexArray = [] 
		self.paramOffsetArray = []
		self.paramNumArray = []
		params = 0
		self.paramArray = [] #0
		self.varOffset = paramOffsetArray[-1] + paramNumArray[-1] * 4
		self.varNum = 0
		self.varNameOffestsArray = [varOffset+496] #(0,0)
		self.varValues = []
		self.varNames = [] #''
		
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
		