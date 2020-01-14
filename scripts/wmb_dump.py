import wmb as wmb_info
from util import *

def dump_dir(wmb_dir):
	fileNames = find_files(wmb_dir, ".wmb")
	for file in fileNames:
		dump_wmb(file)

def dump_wmb(wmb_path):
	
	#WMB Information
	if os.path.exists(wmb_file):
		wmb = wmb_info.WMB3(wmb_file)
		wmb_fp = open(wmb_file, "rb")
	else:
		print("Invalid path: " + wmb_path)
	
	#Bones Information
	boneBuffer = io.TextIO()
	bone_count = wmb.wmb3_header.boneCount
	bone_ids = []
	bone_parents = []
	#bone_lengths = []
	bone_map = []
	bone_map_missing = []
	bone_sets = []
	bone_table = []
	for bone in wmb.boneArray:
		bone_ids.append(bone.boneNumber)
		#bone_lengths.append((bone.))
		bone_parents.append(bone.parentIndex)
	for id in wmb.boneMap:
		bone_map.append(id)
	for id in bone_ids:
		if id not in bone_map:
			bone_map_missing.append(id)
	bone_sets = wmb.boneSetArray
	wmb_fp.seek(52)
	boneTableOffset = to_int(wmb_fp.read(4))
	boneTableSize = to_int(wmb_fp.read(4)) / 2
	wmb_fp.seek(boneTableOffset)
	for i in range(boneTableSize):
		bone_table.append(to_int(wmb_fp.read(2)))
		
	boneBuffer.write("Bone Count: " + str(bone_count) + "\n")
	boneBuffer.write("Bone IDs:\n" + str(bone_ids) + "\n")
	boneBuffer.write("Bone Parents:\n" + str(bone_parents) + "\n")
	boneBuffer.write("Bone Map:\n" + str(bone_map) + "\n")
	boneBuffer.write("Missing bones from bone map:\n" + str(bone_map_missing) + "\n")
	boneBuffer.write("Bone Sets:\n")
	for set in bone_sets:
		boneBuffer.write(str(set) + "\n")
	boneBuffer.write("Bone Table:\n" + str(bone_table) + "\n")
	
	boneBuffer.write("Bone Tree:\n")
	boneTree = []
	def get_parent(bone):
		bone.parentIndex
	bones_sorted = sorted(wmb.boneArray, key=get_parent)
	for bone in bones_sorted:
		
		
			
			
	
	#Vertex Info
	vertex_count = 0
	vertexEx_count = 0
	loop_count = 0
	vertexGroup_count = len(wmb.vertexGroupArray)
	vertexGroup_flags = []
	
	
	
	#Cleanup
	wmb_fp.close()

	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
