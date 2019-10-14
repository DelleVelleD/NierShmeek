import os
import sys
import ctypes
import struct

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
	try:
		filenameArray.sort(key=dds_number)
	except:
		print('-Please put _n after each dds name, where n is order in which they should be placed in the wtp and wta (order albedos and their normals next to eachother)')
	return filenameArray

def pad_dds_dir(dds_dir):
	ddsArray = find_files(dds_dir, 'dds')
	sectorsPerCluster = ctypes.c_ulonglong(0)
	bytesPerSector = ctypes.c_ulonglong(0)
	rootPathName = ctypes.c_wchar_p(u"" + dds_dir)
	ctypes.windll.kernel32.GetDiskFreeSpaceW(rootPathName, ctypes.pointer(sectorsPerCluster), ctypes.pointer(bytesPerSector), None, None,)
	dds_cSize = sectorsPerCluster.value * bytesPerSector.value
	#print(dds_cSize)
	for i in range(len(ddsArray)):
		dds_lSize = os.stat(ddsArray[i]).st_size
		dds_dSize = ((dds_lSize + (dds_cSize - 1)) // dds_cSize) * dds_cSize
		#print(paddingAmount)
		if dds_dSize < 12289:
			paddingAmount = 12288 - dds_lSize 
		elif dds_dSize < 176129:
			paddingAmount = 176128 - dds_lSize 
		elif dds_dSize < 352257:
			paddingAmount = 352256 - dds_lSize 
		elif dds_dSize < 528385:
			paddingAmount = 528384 - dds_lSize 
		elif dds_dSize < 700417:
			paddingAmount = 700416 - dds_lSize 
		elif dds_dSize < 2797569:
			paddingAmount = 2797568 - dds_lSize 
		else:
			paddingAmount = dds_dSize - dds_lSize
		#print(os.stat(ddsArray[i]).st_size)
		dds_fp = open(ddsArray[i], 'ab')
		dds_fp.seek(dds_lSize)
		
		if i != len(ddsArray)-1:
			print("-Padding dds: " + ddsArray[i] + " with " + str(paddingAmount) + " bytes")
			for j in range(paddingAmount-4):
				dds_fp.write(b'\x00')
			dds_fp.write(struct.pack('<I', paddingAmount))
		dds_fp.close()
		#print(os.stat(ddsArray[i]).st_size)

def main(dds_dir, out_path):
	pad_dds_dir(dds_dir)

	filenameArray = find_files(dds_dir, 'dds')
	wtp_fp = open(out_path,'wb')
	
	for i in range(len(filenameArray)):
		dds_fp = open(filenameArray[i],'rb')
		content = dds_fp.read()
		print("-Writing dds: " + filenameArray[i] + " to file: " + out_path + " at position: " + str(i))
		wtp_fp.write(content)
		dds_fp.close()
	wtp_fp.close()

if __name__ == "__main__":
	useage = "\nUseage:\n    python wtp_gen.py output_path dds_folder_path\nEg:    python wtp_gen.py C:\\NierA\\pl000d.wtp C:\\NierA\\dds"
	if len(sys.argv) < 2:
		print(useage)
		exit()
	if len(sys.argv) > 2:
		dds_dir = sys.argv[2]
		output_path = sys.argv[1]
	main(dds_dir, output_path)
