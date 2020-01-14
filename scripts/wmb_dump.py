fileNames = find_files(wmb_dir, ".wmb")

import wmb as wmb_info

def dump_wmb(wmb_path):
	#WMB Information
	if os.path.exists(wmb_file):
		wmb = wmb_info.WMB3(wmb_file)
		wmb_fp = open(wmb_file, "rb")
	else:
		print("Invalid path: " + wmb_path)
	
	#Bones Information
	bone_count = wmb.wmb3_header.boneCount
	bone_ids = []
	#bone_lengths = []
	bone_map = []
	bone_map_missing = []
	bone_sets = []
	bone_table = []
	for bone in wmb.boneArray:
		bone_ids.append(bone.boneNumber)
		#bone_lengths.append((bone.))
	for id in wmb.boneMap:
		bone_map.append(id)
	for id in bone_ids:
		if id not in bone_map:
			bone_map_missing.append(id)
	bone_sets = wmb.boneSetArray
	
	
	#
	
	
	#Cleanup
	wmb_fp.close()
