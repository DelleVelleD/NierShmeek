import os
import sys
import ctypes

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
		paddingAmount = dds_dSize - dds_lSize
		#print(paddingAmount)

		#print(os.stat(ddsArray[i]).st_size)
		dds_fp = open(ddsArray[i], 'ab')
		print("padding dds: " + ddsArray[i] + " with " + str(paddingAmount) + " bytes")
		dds_fp.seek(dds_lSize)
		
		if i != len(ddsArray)-1:
			for j in range(paddingAmount):
				dds_fp.write(b'\x00')
		dds_fp.close()
		#print(os.stat(ddsArray[i]).st_size)

def main(dds_dir, wtpName):
	pad_dds_dir(dds_dir)

	wtp_fp = open(dds_dir + '/' + wtpName + '.wtp','wb')
	filenameArray = find_files(dds_dir, 'dds')
	for i in range(len(filenameArray)):
		dds_fp = open(filenameArray[i],'rb')
		content = dds_fp.read()
		print("writing dds: " + filenameArray[i] + " to file: " + wtpName + ".wtp at position: " + str(i))
		wtp_fp.write(content)
		dds_fp.close()
	wtp_fp.close()

if __name__ == "__main__":
	useage = "\nUseage:(places wtp file in dds folder)\n    python wtp_gen.py dds_folder_path wtp_name"
	if len(sys.argv) < 2:
		print(useage)
		exit()
	if len(sys.argv) > 2:
		dds_dir = sys.argv[1]
		wtp_name = sys.argv[2]
	main(dds_dir, wtp_name)