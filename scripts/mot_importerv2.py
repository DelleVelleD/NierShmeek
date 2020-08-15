def format_motion_data(frame_count, records):
	formatted_records = {} #{boneNumber: POSX[], POSY[], POSZ[], ROTX[], ROTY[], ROTZ[], SCALEX[], SCALEY[], SCALEZ[]}
	
	for record in records:
		bone_records = formatted_records.setdefault(record.bone_id, [None]*9)
		if 0 <= record.valueType <= 5: # 0-5 index no change
			frames = []
			for i in range(frame_count):
				frames.append(record.get_frame(i))
			bone_records[record.valueType] = frames
			
			for value, i in zip(bone_records[record.valueType], range(len(bone_records[record.valueType]))):
				if value == None:
					print(record.offset, record.bone_id, i, record.valueType, record.recordType)
		elif 7 <= record.valueType <= 9: # 7-9 index need to (-1), because valueType:6 skipped.
			frames = []
			for i in range(frame_count):
				frames.append(record.get_frame(i))
			bone_records[record.valueType - 1] = frames
			
			for value, i in zip(bone_records[record.valueType - 1], range(len(bone_records[record.valueType - 1]))):
				if value == None:
					print(record.offset, record.bone_id, i, record.valueType, record.recordType)
		else:
			print('[MOT-Error] Unknown value type:%d' % (record.valueType))
		
	#fill in missing records
	default_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0] #%TODO% translation default might be different
	for bone_id, bone_records in formatted_records.items():
		for i in range(len(bone_records)):
			if bone_records[i] is None:
				bone_records[i] = [default_value[i]] * frame_count
	
	motion_data = {} #{boneNumber: POS[(frameIndex, x, y, z)], ROT[(frameIndex, x, y, z, w)], SCALE[(frameIndex, x, y, z)]}
	for bone_id, bone_records in formatted_records.items():
		pos_frames = []
		rot_frames = []
		scale_frames = []
		for i in range(frame_count):
			pos_frames.append([i, mathutils.Vector(bone_records[0][i], bone_records[1][i], bone_records[2][i]]))
			rot = mathutils.Euler((bone_records[3][i], bone_records[4][i], bone_records[5][i]), 'XYZ')
			rot_frames.append([i, rot.to_quaternion()])
			scale_frames.append([i, mathutils.Vector(bone_records[6][i], bone_records[7][i], bone_records[8][i]]))
	
		motion_data[bone_id] = [pos_frames, rot_frames, scale_frames]
		
	return motion_data

def construct_action(wmb, mot, motion_data, armature, rotation_resample=False): #(wmb.py WMB object, mot.py MOT object, motion data from above, blender armature object)
	print('[+] importing motion %s' % mot.motionName)
	action = bpy.data.actions.new(name=mot.motionName)
	action.use_fake_user = True
	#action.target_user = armature.name #%TODO% figure this out
	if armature.animation_data is None:
		armature.animation_data_create()
	armature.animation_data.action = action
	
	bpy.context.view_layer.objects.active = armature 
	bpy.ops.object.mode_set(mode='POSE') #Set armature to pose mode
	bone_mapping = armature["bone_mapping"] #Get bones from armature
	pose_bones = bpy.context.view_layer.objects.active.pose.bones 
	
	print('[MOT-Info] armature.name: %s' % (armature.name))
	print('[MOT-Info] bpy.context.view_layer.objects.active.name: %s' % (bpy.context.view_layer.objects.active.name))
	
	used_bones = []
	for bone_number, values in motion.items():
		pos_values, rot_values, scale_values = values
		bone_name = bone_mapping.get(str(bone_number))
		
		if bone_name is None:
			print('[MOT-Error] bone_number = %d not found in bone_mapping.' % (bone_number))
			continue
			
		pose_bone = pose_bones.get(bone_name)
		if pose_bone is None:
			print('[MOT-Error] %s not found in armature.pose.bones.' % (bone_name))
			continue
		
		if bone_name not in used_bones:
			used_bones.append(bone_name)
	
		if pos_values is not None:
			for pos_value in pos_values:
				frame = pos_value[0] + 1
				pose_bone.matrix = pose_bone.matrix_basis.Translation(pos_value[1])
				pose_bone.keyframe_insert("matrix_basis", index=-1, frame=frame)
		else:
			pose_bone.keyframe_insert("matrix_basis", index=-1, frame=1)
			
