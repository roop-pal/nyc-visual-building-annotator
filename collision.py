import gml_parser
import conversion
import math
import numpy as np

# Checks if a certain postion is within the range of any building
def check_building_collision(position, dictionary):
	x, y, z = position
	for build in dictionary.keys():
		if dictionary[build]['X'][0] < x < dictionary[build]['X'][1] and dictionary[build]['Y'][0] < y < dictionary[build]['Y'][1] and dictionary[build]['Z'][0] < z < dictionary[build]['Z'][1]:
			return build
	return False	

# Checks whether the position is still in the model
def within_model_bounds(position):
	x,y,z = position
	if 978979.241500825 < x < 1002759.79006824 and 194479.073690146 < y < 220148.669988647 and -39.0158999999985 < z < 1797.1066:
		return True
	else:
		return False

# Input: Current position in the model coordinate frame
#	   : Orientation defined by (theta, alpha, and beta) in radians
#      		: theta is defined as the angle of the line in the x-y plane 
#      		: alpha in the y-z plane
#      : Dictionary of buildings with x,y,z ranges as attributes
# Output: The building you are looking at or False (if it doesn't collide with a building)
def collision_check(position, euler, dictionary,step=5):
	time = 0
	s_x, s_y, s_z = position
	theta, alpha = -euler[0] + np.pi/2, -euler[1] - np.pi/2
	print('theta',theta,'alpha',alpha)
	current_position = position

	while within_model_bounds(current_position):
		collision = check_building_collision(current_position, dictionary)
		if collision != False:
			return collision
		else:
			time += step
			new_x = s_x + time*math.cos(theta)
			new_y = s_y + time*math.sin(theta)
			new_z = s_z + time*math.sin(alpha)
			current_position = (new_x, new_y, new_z)
	return False

def extract_rotation_translation(s):
    rotation_matrix = s[s.find('RotationMatrix') + 16:]
    rm = [float(i) for i in rotation_matrix[:rotation_matrix.find('"')].split(' ')[:-1]]
    R = np.array([rm[:3],rm[4:7],rm[8:11]])
    translation_vector = s[s.find('TranslationVector') + 19:]
    T = np.array([[float(i)] for i in translation_vector[:translation_vector.find('"')].split(' ')[:-1]])
    return R,T

if __name__ == '__main__':
	bldg_info = gml_parser.parse('DA12_3D_Buildings_Merged.gml')
	R,T=extract_rotation_translation('''<!DOCTYPE ViewState>
	<project>
	 <VCGCamera TranslationVector="-988311 -211333 -656.179 1" LensDistortion="0 0" PixelSizeMm="0.0369161 0.0369161" CenterPx="1198 863" FocalMm="55.1807" ViewportPx="2397 1726" RotationMatrix="0.994747 -0.0036457 -0.102304 0 0.10229 -0.00390099 0.994747 0 -0.00402565 -0.999986 -0.00350758 0 0 0 0 1 " CameraType="0"/>
	 <ViewSettings FarPlane="523.686" TrackScale="0.0150035" NearPlane="0.909327"/>
	</project>
		''')
	euler = conversion.rotationMatrixToEulerAngles(R)
	print('euler',euler)
	print('T',-T.T[0])
	H = conversion.train_homography(bldg_info)
	H_inv = np.linalg.inv(H)
	test_point = [*conversion.GPS_to_coordinate(40.713009, -74.013678,H_inv),0.0]
	coord = collision_check(-T.T[0],euler,bldg_info)
	print('coord',coord)


	# coord = collision_check(test_point,[1.0,1.0],bldg_info)
	# assert coord == "Bldg_21510003972", "Cannot identify when intial point is in building"
	#
	# test_point = [*conversion.GPS_to_coordinate(40.700678,-74.017636,H_inv),0.0]
	# coord = collision_check(test_point,[0.0,3.1415/2],bldg_info)
	# assert coord == False, "You aren't suppose to see anything if you look up in the Hudson"
	#
	# test_point = [*conversion.GPS_to_coordinate(40.712348,-74.013641,H_inv),1.0]
	# coord = collision_check(test_point,[math.pi/2,0.0],bldg_info)
	# assert coord == "Bldg_21510003972", "If you are standing in front of One WTC and look north, you should see it"
	#
	# test_point = [*conversion.GPS_to_coordinate(40.748160,-73.984741,H_inv),40.0]
	# coord = collision_check(test_point,[math.pi,0.0],bldg_info)
	# assert coord == "Bldg_12210009096", "If you are standing in front of Empire State Building and look west, you should see it"
