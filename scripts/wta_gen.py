import os
import sys
import struct
import random

def dds_number(dds_path):
	split_dds = dds_path.split('_')
	#print(split_dds)
	dds_num = split_dds[-1].split('.')
	#print(dds_num)
	return int(dds_num[0])

def find_files(dir_name,ext):
	filenameArray = []
	for dirpath,dirnames,filename in os.walk(dir_name):
		for file in filename:
			filename = "%s\%s"%(dirpath,file)
			#print(filename)
			if filename.find(ext) > -1:
				filenameArray.append(filename)
	filenameArray.sort(key=dds_number)
	return filenameArray
	
def to_bytes(arg):
	if type(arg) == int:
		return struct.pack('<I', arg)
	if type(arg) == str:
		return struct.pack('<I', int(arg, 16))

def main(out_dir, dds_dir, albedos, identifiers):
	wta_fp = open(out_dir,'wb')

	dds_files = find_files(dds_dir, 'dds')
	albedos_array = albedos.split(',')
	for i in range(len(albedos_array)):
		albedos_array[i] = int(albedos_array[i])
	identifiers_array = identifiers.split(',')
	#print(albedos_array)

	unknown04 = 3
	textureCount = len(dds_files)
	paddingAmount = ((textureCount + 7) // 8) * 8	#rounds up to the nearest 8th integer
	textureOffsetArrayOffset = 32
	textureSizeArrayOffset = textureOffsetArrayOffset + (paddingAmount * 4)
	unknownArrayOffset1 = textureSizeArrayOffset + (paddingAmount * 4)
	textureIdentifierArrayOffset = unknownArrayOffset1 + (paddingAmount * 4)
	unknownArrayOffset2 = textureIdentifierArrayOffset + (paddingAmount * 4)
	wtaTextureOffset = [0] * textureCount
	wtaTextureSize = [0] * textureCount
	wtaTextureIdentifier = [0] * textureCount
	unknownArray1 = [0] * textureCount
	unknownArray2 = []
	
	for i in range(len(dds_files)):
		dds_fp = open(dds_files[i], 'rb')
		dds_paddedSize = os.stat(dds_files[i]).st_size

		#checks dds dxt and cube map info
		dds_fp.seek(84)
		dxt = dds_fp.read(4)
		dds_fp.seek(112)
		cube = dds_fp.read(4)

		#finds how much padding bytes are added to a dds
		dds_padding = 0
		dds_fp.seek(128)
		temp_reading = dds_fp.read(16)
		while temp_reading:
			if temp_reading == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' and not dxt == b'DXT3':
				dds_padding += 16
			temp_reading = dds_fp.read(16)
		print(dds_padding)
		#print(dds_paddedSize)

		#wtaTextureOffset
		if i+1 in range(len(wtaTextureSize)):
			if dds_paddedSize < 12289:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 12288
			elif dds_paddedSize < 176129:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 176128
			elif dds_paddedSize < 352257:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 352256
			elif dds_paddedSize < 528385:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 528384
			elif dds_paddedSize < 700417:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 700416
			elif dds_paddedSize < 2797569:
				wtaTextureOffset[i+1] = wtaTextureOffset[i] + 2797568
			else:
				wtaTextureOffset[i+1] = dds_paddedSize
		#wtaTextureSize
		wtaTextureSize[i] = dds_paddedSize - dds_padding
		#wtaTextureIdentifier
		wtaTextureIdentifier[i] = identifiers_array[i]
		#unknownArray1
		if i in albedos_array:
			unknownArray1[i] = 637534240
		else:
			unknownArray1[i] = 570425376
		#unknownArray2
		if dxt == b'DXT1':
			unknownArray2.append(71)
			unknownArray2.append(3)
			if cube == b'\x00\xfe\x00\x00':
				unknownArray2.append(4)
			else:
				unknownArray2.append(0)
			unknownArray2.append(1)
			unknownArray2.append(0)
		if dxt == b'DXT3':
			unknownArray2.append(74)
			unknownArray2.append(3)
			if cube == b'\x00\xfe\x00\x00':
				unknownArray2.append(4)
			else:
				unknownArray2.append(0)
			unknownArray2.append(1)
			unknownArray2.append(0)
		if dxt == b'DXT5':
			unknownArray2.append(77)
			unknownArray2.append(3)
			if cube == b'\x00\xfe\x00\x00':
				unknownArray2.append(4)
			else:
				unknownArray2.append(0)
			unknownArray2.append(1)
			unknownArray2.append(0)
		dds_fp.close()

	#temp defaults
	#wtaTextureIdentifier = ['7a861a50', '31522db9', '6eff561f', '74aed53b', '3373e322', '6fd76040', '632ddfb6', '125b5aec', '4c6d5e48', '2fd4343c', '168ec964', '64b8fa0b', '421e76d1']
	print( wtaTextureIdentifier)
	print(wtaTextureOffset)
	print(wtaTextureSize)

	padding = b''
	for i in range(paddingAmount - textureCount):
		padding += b'\x00\x00\x00\x00'

	wta_fp.write(b'WTB\x00')
	wta_fp.write(to_bytes(unknown04))
	wta_fp.write(to_bytes(textureCount))
	wta_fp.write(to_bytes(textureOffsetArrayOffset))
	wta_fp.write(to_bytes(textureSizeArrayOffset))
	wta_fp.write(to_bytes(unknownArrayOffset1))
	wta_fp.write(to_bytes(textureIdentifierArrayOffset))
	wta_fp.write(to_bytes(unknownArrayOffset2))
	for i in range(textureCount):
		wta_fp.write(to_bytes(wtaTextureOffset[i]))
	wta_fp.write(padding)
	for i in range(textureCount):
		wta_fp.write(to_bytes(wtaTextureSize[i]))
	wta_fp.write(padding)
	for i in range(textureCount):
		wta_fp.write(to_bytes(unknownArray1[i]))
	wta_fp.write(padding)
	for i in range(textureCount):
		wta_fp.write(to_bytes(wtaTextureIdentifier[i]))
	wta_fp.write(padding)
	for i in range(textureCount):
		wta_fp.write(to_bytes(unknownArray2[(i*5)]))
		wta_fp.write(to_bytes(unknownArray2[(i*5)+1]))
		wta_fp.write(to_bytes(unknownArray2[(i*5)+2]))
		wta_fp.write(to_bytes(unknownArray2[(i*5)+3]))
		wta_fp.write(to_bytes(unknownArray2[(i*5)+4]))
	wta_fp.write(padding)

	wta_fp.close()

if __name__ == "__main__":
	useage = "\nUseage:(arrays comma seperated, no space)\n    python wta_gen.py output_path dds_folder_path albedo_positions_array identifiers_array\n    Eg: python wta_gen.py C:\\NierA\\pl000d.wta C:\\NierA\\dds 0,2 a1b2c3d4,b2a1c3d4,8longhex"
	if len(sys.argv) < 4:
		print(useage)
		exit()
	if len(sys.argv) > 4:
		out_dir = sys.argv[1]
		dds_dir = sys.argv[2]
		albedos = sys.argv[3]
		identifiers = sys.argv[4]
	main(out_dir, dds_dir, albedos, identifiers)
