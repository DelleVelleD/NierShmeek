import bpy, bmesh, math, mathutils
import nier2blender.mot as MOT

def show_message(message = "", title = "Message Box", icon = 'INFO'):
	def draw(self, context):
		self.layout.label(text = message)
		self.layout.alignment = 'CENTER'
	bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
	
	
	
def format_motion_data(frame_count, records):
	formatted_records = {} #{bone_id: POSX[], POSY[], POSZ[], ROTX[], ROTY[], ROTZ[], SCALEX[], SCALEY[], SCALEZ[]}
	
	
	for record in records:
		bone_records = formatted_records.setdefault(record.bone_id, [None]*9)
		if 0 <= record.valueType <= 5: # 0-5 index no change
			frames = []
			for i in range(frame_count):
				frames.append(record.get_frame(i))
			bone_records[record.valueType] = frames
		elif 7 <= record.valueType <= 9: # 7-9 index need to (-1), because valueType:6 skipped.
			frames = []
			for i in range(frame_count):
				frames.append(record.get_frame(i))
			bone_records[record.valueType - 1] = frames
		else:
			print('[Error] Unknown TrackType:%d' % (record.recordType))
		
	#fill in missing records
	default_value = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
	for bone_id, bone_records in formatted_records.items():
		for i in range(len(bone_records)):
			if bone_records[i] is None:
				bone_records[i] = [default_value[i]] * frame_count
	
	motions = {} #{bone_id: POS[(frameIndex, x, y, z)], ROT[(frameIndex, x, y, z, w)], SCALE[(frameIndex, x, y, z)]}
	for bone_id, bone_records in formatted_records.items():
		pos_frames = []
		rot_frames = []
		scale_frames = []
		
		for i in range(frame_count):
			pos_frames.append(i, bone_records[0][i], bone_records[1][i], bone_records[2][i])
			rot = mathutils.Euler((bone_records[3][i], bone_records[4][i], bone_records[5][i]), 'XYZ')
			quat = rot.to_quaternion()
			rot_frames.append(i, quat.x, quat.y, quat.z, quat.w)
			scale_frames.append(i, bone_records[6][i], bone_records[7][i], bone_records[8][i])
	
		motions[bone_id] = [pos_frames, rot_frames, scale_frames]
		
	return motions
	
def construct_action(motion, armature, bind_pose, rotation_resample=False): #(mot.py MOT object, blender.data.armatures object)
	action = bpy.data.actions.new(name=motion.header.motionName)
	action.use_fake_user = True
	action.target_user = armature.name
	if armature.animation_data is None:
		armature.animation_data_create()
	armature.animation_data.action = action
	
	bpy.context.scene.objects.active = armature
	bpy.ops.object.mode_set(mode='POSE') #Set armature to pose mode
	bone_mapping = armature["bone_mapping"] #Get bones from armature
	pose_bones = armature.pose.bones 
	
	print('[Info] armature.name: %s' % (armature.name))
	print('[Info] armature.data.name: %s' % (armature.data.name))
	
	used_bones = []
	for bone_number, values in motion.items(): #loop through bones
		pos_values, rot_values, scale_values = values
		bone_name = bone_mapping.get(str(bone_number))
		
		if bone_name is None:
			print('[Error] bone_number = %d not found in bone_mapping.' % (bone_number))
			continue
		pose_bone = pose_bones.get(bone_name)
		if pose_bone is None:
			print('[Error] %s not found in armature.pose.bones.' % (bone_name))
			continue
		
		if bone_name not in used_bones:
			used_bones.append(bone_name)
			
		#position keyframes
		if pos_values is not None:
			for pos_value in pos_values:
				frame = pos_value[0] + 1 #set initial frame to 1
				pose_bone.location = mathutils.Vector(pos_value[1:4])
				pose_bone.location -= bind_pose[bone_name][0] #offset pose_bone location from normal pose
				pose_bone.keyframe_insert("location", index=-1, frame=frame)
		else:
			pose_bone.location = mathutils.Vector([0,0,0]) #if no position values, set to 0,0,0
			pose_bone.keyframe_insert("location", index=-1, frame=1)
				
		#rotation keyframes
		if rot_values is not None:
			prev_frame = 1
			for rot_value in rot_values:
				frame = rot_value[0] + 1
				quat = mathutils.Quaternion([rot_value[4], rot_value[1], rot_value[2], rot_value[3]]) # In blender, quaternion is stored in order of w, x, y, z
				quat *= bind_pose[bone_name][1].inverted() #offset pose_bone rotation from normal pose
				
				if frame - prev_frame > 1 and rotation_resample: #option to have blender slerp the values
					prev_quat = mathutils.Quaternion(pose_bone.rotation_quaternion)
					step = 1.0 / (frame - prev_frame)
					fraction = 0.0
					for i in range(frame - prev_frame):
						fraction += step
						_q = prev_quat.slerp(quat, fraction)
						pose_bone.rotation_quaternion = _q
						pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=prev_frame + i + 1)
				else:
					pose_bone.rotation_quaternion = quat
					pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=frame)
				prev_frame = frame
		else:
			pose_bone.rotation_quaternion = mathutils.Quaternion([1, 0, 0, 0])
			pose_bone.keyframe_insert("rotation_quaternion", index=-1, frame=1)
					
		#scale keyframe
		if scale_values is not None:
			for scale_value in scale_values:
				frame = scale_value[0]
				pose_bone.scale = mathutils.Vector(scale_value[1:4])
				pose_bone.scale.x /= bind_pose[bone_name][2].x
				pose_bone.scale.y /= bind_pose[bone_name][2].y
				pose_bone.scale.z /= bind_pose[bone_name][2].z
				pose_bone.keyframe_insert("scale", index=-1, frame=frame)
		else:
			pose_bone.scale = mathutils.Vector([1,1,1])
			pose_bone.keyframe_insert("scale", index=-1, frame=1)
				
	print('[INFO] Motion Bones Used: ')
	uBones = ''
	for boneNum in used_bones:
		uBones += boneNum + ', '
	print(uBones)	
					
	#%TODO% find out why he converts to linear interpolation
	#force linear interpolation
	for fcurve in action.fcurves:
		for keyframe_point in fcurve.keyframe_points:
			keyframe_point.interpolation = 'LINEAR'
			
	bpy.ops.object.mode_set(mode='OBJECT')
					
					
def calc_bind_pose_transform(armature):
	m = mathutils.Matrix()
	m[0].xyzw = 1, 0, 0, 0
	m[1].xyzw = 0, 0, 1, 0
	m[2].xyzw = 0, -1, 0, 0
	m[3].xyzw = 0, 0, 0, 1

	# TODO:骨骼p,r,s数据计算可能不正确
	bind_pose = {}
	for bone in armature.data.edit_bones:
		if bone.parent is None:
			loc_mat = m * bone.matrix
		else:
			loc_mat = (m * bone.parent.matrix).inverted() * (m * bone.matrix)
		loc, rot, scale = loc_mat.decompose()
		bind_pose[bone.name] = (loc, rot, scale)
	return bind_pose

def main(armature):	
	
					
					
					
					