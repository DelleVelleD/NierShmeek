|------------------------------------------|
|            WTA File Structure            |
|------------------------------------------|
| SIZE |            DESCRIPTION            |
|------------------------------------------|
| 0x04 | Magic Number                      | #b'WTA\x00'
| 0x04 | unknown04                         | #always 3
| 0x04 | Texture Count                     |
| 0x04 | Texture Offset Array Offset       | #1 int per texture
| 0x04 | Texture Size Array Offset         | #1 int per texture
| 0x04 | Albedo Info Array Offset          | #1 int per texture, either 637534240 or 570425376
| 0x04 | Texture Identifier Array Offset   | #1 string per texture
| 0x04 | Texture Info Array Offset         | #5 ints per texture
|      | Texture Offset Array              | #the offsets inside the wtp file, equal to padded texture size
|      | Texture Size Array                | #the size of the textures without padding
|      | Albedo Info Array                 | #637534240 if its albedo or hair, 570425376 if not
|      | Texture Identifier Array          | #seemingly random hexa strings, must match identifiers in .wmb
|      | Texture Info Array                | #[dxt, ?, is_cubemap, ?, ?]
|------------------------------------------|
|            Texture Info Array            |
|------------------------------------------|
| 0x04 | DXT Type                          | #71 = dxt1, 74 = dxt3, 77 = dxt5
| 0x04 | UnknownA                          | #always 0
| 0x04 | Is Cubemap                        | #4 if the texture is a cubemap, 0 otherwise
| 0x04 | UnknownB                          | #always 0
| 0x04 | UnknownC                          | #always 0
|------------------------------------------|

pl1040.wta:
  magicNumber:b'WTB\x00'
  unknown04:3
  textureCount:13
  textureOffsetArrayOffset:32
  textureSizeArrayOffset:96
  unknownArrayOffset1:160
  textureIdentifierArrayOffset:224
  unknownArrayOffset2:288
  wtaTextureOffset:[0, 700416, 1400832, 4198400, 4374528, 4726784, 4902912, 4915200, 5091328, 5443584, 5619712, 5795840, 6324224]
  wtaTextureSize:[699192, 699192, 2796344, 174904, 349680, 174904, 11064, 174904, 349680, 174904, 174904, 524576, 1398256]
  wtaTextureIdentifier:['7a861a50', '31522db9', '6eff561f', '74aed53b', '3373e322', '6fd76040', '632ddfb6', '125b5aec', '4c6d5e48', '2fd4343c', '168ec964', '64b8fa0b', '421e76d1']
  unknownArray1:['26000020', '22000020', '22000020', '26000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '26000020', '26000020']
  unknownArray2:[71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 4, 1, 0, 74, 3, 0, 1, 0, 0, 0, 0]
  pointer2:0x230

pl000d.wta:
  magicNumber:b'WTB\x00'
  unknown04:3
  textureCount:28
  textureOffsetArrayOffset:32
  textureSizeArrayOffset:160
  unknownArrayOffset1:288
  textureIdentifierArrayOffset:416
  unknownArrayOffset2:544
  wtaTextureOffset:[0, 700416, 2101248, 4898816, 7696384, 7872512, 8224768, 8925184, 8937472, 9113600, 9125888, 9216000, 9228288, 9404416, 9756672, 9932800, 10461184, 10637312, 10813440, 11513856, 12214272, 12390400, 13090816, 13791232, 14491648, 15192064, 16592896, 17293312]
  wtaTextureSize:[699192, 1398256, 2796344, 2796344, 174904, 349680, 699192, 11064, 174904, 11064, 87536, 11064, 174904, 349680, 174904, 524576, 174904, 174904, 699192, 699192, 174904, 699192, 699192, 699192, 699192, 1398256, 699192, 2796344]
  wtaTextureIdentifier:['541f36b6', '6d15dd57', '74a38a40', '4f6683cd', '2fdb97d9', '189f1c9d', '34a222a2', '77eeaa6a', '39b7a553', '3ca41a88', '57976458', '342e0e2c', '0b22233a', '232362a9', '41ec55b6', '5c3ad97f', '4d30b6f4', '5fc5791b', '5649038f', '1504751c', '662d4bb3', '0e7dc067', '118f210a', '4c971788', '3ce7c865', '2d3f3d10', '34896a07', '279e7d1e']
  unknownArray1:['26000020', '22000020', '22000020', '22000020', '26000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '22000020', '26000020', '26000020', '22000020', '22000020', '26000020', '22000020', '22000020', '26000020', '26000020', '26000020', '22000020', '22000020', '22000020']
  unknownArray2:[71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 4, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0, 77, 3, 0, 1, 0, 71, 3, 0, 1, 0, 71, 3, 0, 1, 0]
  pointer2:'0x450'

pl1040.wmb:
	magicNumber= b'WMB\x00'
	version= 538312982 = '20160116' #might be able to be anything
	unknown08 = 0 #? always zero
	flags = 4294901770 #? always this
	bounding_box1 = 0.0 #always zero
	bounding_box2 = 0.8718799948692322
	bounding_box3 = 0.004234999418258667
	bounding_box4 = 0.5242999792098999
	bounding_box5 = 0.8714199662208557
	bounding_box6 = 0.22001498937606812
	boneArrayOffset = 144 #always 144
	boneCount = 147
	boneIndexTranslateTableOffset = 13088 #boneArrayOffset + (boneCount * 88)
	boneIndexTranslateTableSize = 928
	vertexGroupArrayOffset = 14016 #boneIndexTranslateTableOffset + boneIndexTranslateTableSize
	vertexGroupCount = 3
	meshArrayOffset = 2817192
	meshCount = 14
	meshGroupInfoArrayHeaderOffset = 2817584 #meshArrayOffset + (meshCount * 28)
	meshGroupInfoArrayCount = 1
	meshMaterialOffset = 2817952
	meshMaterialCount = 14
	unknownChunk2Offset = 0
	unknownChunk2DataCount = 0
	bonesetOffset = 2818064 #meshMaterialOffset + (meshMaterialCount * 8)
	bonesetCount = 13
	boneMapOffset = 2818784
	boneMapCount = 138
	meshGroupOffset = 2819336 #boneMapOffset + (boneMapCount * 4)
	meshGroupCount = 6
	materialArrayOffset = 2820128
	materialCount = 6
	unknown84 = 0
	unknown88 = 0
	unknown8C = 0

	pl1040.wmb.materials[0]:
		unknownA = 460768
		unknownB = 983045
		materialNameOffset = 2820416
		materialName = 'ES0a11_CLT'
		effectNameOffset = 2820427
		effectName = 'CLT00_XXXXX'
		techniqueNameOffset = 2820439
		techniqueName = 'Default'
		unknownC = 1
		textureOffset = 2820447
		textureNum = 7
		paramOffset = 2820592
		paramNum = 2
		varOffset = 2820816
		varNum = 62
		textureArray = [(2820503, '7a861a50'), (2820515, '31522db9'), (2820525, '4e9c16f4'), (2820536, '6eff561f'), (2820548, '7fd4929a'), (2820566, '1fbc0984'), (2820575, '1fbc0984')]
		textureNames = ['g_AlbedoMap','g_MaskMap','g_MaskMap2','g_NormalMap','g_DetailNormalMap','g_EnvMap','g_IrradianceMap']
		paramArray = [(0, 2820624, 44), (-1, 2820800, 4)]
		param1Values = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.018340999260544777, 0.018340999260544777, 0.018340999260544777, 0.0, 0.0, 0.0, 0.0, 0.30000001192092896, 0.5, 3.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.10000000149011612, 0.10000000149011612, 0.0, 0.0, 0.0, 0.6299999952316284, 0.8500000238418579, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0]
		param2Values = [0.0, 0.0, 0.0, 0.0]
		varArray = [(2821322, 0.0), (2821329, 0.0), (2821336, 0.0), (2821345, 0.0), (2821354, 0.0), (2821364, 0.0), (2821374, 1.0), (2821385, 0.018340999260544777), (2821401, 0.018340999260544777), (2821417, 0.018340999260544777), (2821433, 1.0), (2821457, 0.0), (2821474, 0.0), (2821492, 0.0), (2821506, 0.10000000149011612), (2821522, 0.10000000149011612), (2821538, 0.0), (2821546, 1.0), (2821567, 1.0), (2821588, 1.0), (2821612, 1.0), (2821636, 1.0), (2821660, 3.0), (2821675, 0.5), (2821695, 0.0), (2821705, 0.0), (2821719, 0.30000001192092896), (2821742, 0.0), (2821755, 0.5), (2821774, 0.0), (2821791, 1.0), (2821808, 1.0), (2821825, 1.0), (2821842, 1.0), (2821858, 1.0), (2821874, 1.0), (2821890, 1.0), (2821906, 1.0), (2821922, 1.0), (2821938, 1.0), (2821954, 1.0), (2821970, 1.0), (2821986, 1.0), (2822003, 0.0), (2822014, 0.0), (2822030, 0.5), (2822047, 0.0), (2822063, 1.0), (2822085, 1.0), (2822094, 1.0), (2822103, 0.0), (2822124, 0.0), (2822136, 1.0), (2822151, 0.0), (2822163, 0.8500000238418579), (2822190, 0.0), (2822210, 0.0), (2822234, 0.6299999952316284), (2822249, 0.0), (2822268, 0.0), (2822291, 0.0)]
		varNames = ['Binormal0','Color0','Normal','Position','Tangent0','TexCoord0','TexCoord1','g_1BitMask','g_AlbedoColor_X','g_AlbedoColor_Y','g_AlbedoColor_Z','g_AmbientLightIntensity','g_AnisoLightMode','g_AnisoLightMode2','g_Anisotropic','g_Anisotropic_X','g_Anisotropic_Y','g_Decal','g_DetailNormalTile_X','g_DetailNormalTile_Y','g_FuzzColorCorrection_X','g_FuzzColorCorrection_Y','g_FuzzColorCorrection_Z','g_FuzzExponent','g_FuzzMaskEffective','g_FuzzMul','g_FuzzReverse','g_FuzzShadowLowerLimit','g_Glossiness','g_HilIghtIntensity','g_IsSwatchRender','g_LighIntensity0','g_LighIntensity1','g_LighIntensity2','g_LightColor0_X','g_LightColor0_Y','g_LightColor0_Z','g_LightColor1_X','g_LightColor1_Y','g_LightColor1_Z','g_LightColor2_X','g_LightColor2_Y','g_LightColor2_Z','g_LightIntensity','g_Metallic','g_NormalReverse','g_ObjWetStrength','g_OffShadowCast','g_ReflectionIntensity','g_Tile_X','g_Tile_Y','g_UseDetailNormalMap','g_UseEnvWet','g_UseNormalMap','g_UseObjWet','g_WetConvergenceGlossiness','g_WetConvergenceHLI','g_WetConvergenceMetalic','g_WetMagAlbedo','g_bAlbedoOverWrite','g_bGlossinessOverWrite','g_bMetalicOverWrite']

pl000d.wmb:
	magicNumber= b'WMB\x00'
	version= 538312982 = '20160116' #might be able to be anything
	unknown08 = 0 #? always zero
	flags = 4294901770 #? always this
	bounding_box1 = 0.0 #always zero
	bounding_box2 = 0.8522949814796448
	bounding_box3 = 0.002584993839263916
	bounding_box4 = 0.5134899616241455
	bounding_box5 = 0.8530550003051758
	bounding_box6 = 0.3016049861907959
	boneArrayOffset = 144
	boneCount = 198
	boneIndexTranslateTableOffset = 17568
	boneIndexTranslateTableSize = 1088
	vertexGroupArrayOffset = 18656
	vertexGroupCount = 3
	meshArrayOffset = 9945952
	meshCount = 36
	meshGroupInfoArrayHeaderOffset = 9946960
	meshGroupInfoArrayCount = 1
	unknownChunk3Offset = 9947856
	unknownChunk3DataCount = 30
	unknownChunk2Offset = 0
	unknownChunk2Data = 0
	bonesetOffset = 9948096
	bonesetCount = 32
	boneMapOffset = 9950256
	boneMapCount = 183
	meshGroupOffset = 9950988
	meshGroupCount = 14
	materialArrayOffset = 9952784
	materialCount = 15
	unknown84 = 0
	unknown88 = 0
	unknown8C = 0
	
	pl000d.wmb.materials[0]:
		effectName = 'CLT00_XXXXX'
		varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.10000000149011612, 0.10000000149011612, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 0.0, 0.0, 0.30000001192092896, 0.20000000298023224, 1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.4000000059604645, 0.0, 0.0, 0.4000000059604645, 0.0, 0.0, 0.0]
		texture Array {'g_AlbedoMap': '3ce7c865', 'g_MaskMap': '2d3f3d10', 'g_MaskMap2': '34896a07', 'g_NormalMap': '279e7d1e', 'g_DetailNormalMap': '7fd4929a', 'g_EnvMap': '1fbc0984', 'g_IrradianceMap': '1fbc0984'}
	pl000d.wmb.materials[1]:
		effectName = 'PBS00_XXXXX'
		varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.6, 0.5, 0.0, 0.0, 0.0]
	pl000d.wmb.materials[2]:
		effectName = 'SKN00_XXXXX'
		varValues = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 1.0, 0.0, 50.0, 50.0, 5.0, 0.2, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.29177701473236084, 0.03954600170254707, 0.03954600170254707, 0.0, 1.0, 0.8069549798965454, 0.30055099725723267, 0.20155400037765503, 1.0, 1.0, 1.0, 0.8, 0.6299999952316284, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]]
	pl000d.wmb.materials[5]:
		effectName = 'Eye00_XXXXX'
		varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5, 0.5, 0.5, 1.0, 0.0, 0.8, 0.4, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6, 0.0, 1.0, 0.0, 0.02, 1.0, 1.0, 0.0, 1.0, 1.0]
	pl000d.wmb.materials[9]:
		effectName = 'Hair01_XXXXX'
		varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.5149080157279968, 0.47352299094200134, 0.4286850094795227, 1.0, 0.0, 1.0, 0.0, 0.1, 70.0, 1.0, 1.0, 2.0, 4.0, 1.0, 0.1, 0.8, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.2, 10.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.622, 0.8, -0.36, 0.02, 0.0, 1.0, 1.0, 0.5, 0.5, 1.0, 0.63, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0]
	pl000d.wmb.materials[14]:
		effectName = 'CNS00_XXXXX'
		varValues = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0]

TODO:
fix wmb_header flags, not always -65226 (check wolf's /wmb/wmb_header.py)
fix to_1Byte to be more accurate on float to ubyte conversion (check wolf's /vertexgroups/vertexgroup.py)
fix vertex grab from blender (invert y, tangent sign)
add default cases if required items arent present (give error or generate empty or both)

identifiers need to match with those in .wmb (test if changing them in .wmb allows custom in .wta)
(meh)remove debug code on wta, make dbug code in wtp look better
test material objects
test textures objects




