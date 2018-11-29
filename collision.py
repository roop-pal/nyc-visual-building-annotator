from gml_parser import *
from conversion import *
import math

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
#	   		: beta in the x-z plane
#      : Dictionary of buildings with x,y,z ranges as attributes
# Output: The building you are looking at or False (if it doesn't collide with a building)
def collision_check(position, orientation):
	dictionary = parse('DA_WISE_GMLs/DA12_3D_Buildings_Merged.gml')
	time = 0
	s_x, s_y, s_z = position
	theta, alpha, beta = orientation
	current_position = position

	while within_model_bounds(current_position):
		collision = check_building_collision(current_position, dictionary)
		if collision != False:
			return collision
		else:
			time += 1
			new_x = s_x + time*math.cos(beta)
			new_y = s_y + time*math.sin(theta)
			new_z = s_z + time*math.sin(alpha)
			current_position = (new_x, new_y, new_z)
	return False

if __name__ == '__main__':
	# Simple test that shows what happens if the starting point is in a building
	test_point = [*GPS_to_coordinate(40.713009, 74.013678),0.0]
	coord = collision_check(test_point,[1.0,1.0,1.0])
	assert coord == "Bldg_21510003972", "Cannot identify when intial point is in building"

	test_point = [*GPS_to_coordinate(40.700678,74.017636),0.0]
	coord = collision_check(test_point,[0.0,3.1415/2,3.1415/2])
	assert coord == False, "You aren't suppose to see anything if you look up in the Hudson"
