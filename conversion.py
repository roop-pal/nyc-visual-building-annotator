import numpy as np 
from gml_parser import *
from sklearn.linear_model import LinearRegression

# Input: Latitude and Longitude coordinates (In Degrees, Minutes, Seconds)
#        lattitude: String, Longitude: String
# Output: Latitude and Longitude in simply degrees
#		  tuple of floats: (x, y)
def convert_degrees(latitude,longitude):
	# Changing Lat/Long Format
	lat_split = latitude.split(' ')
	lon_split = longitude.split(' ')
	decimal_lat = float(lat_split[0]) + float(lat_split[1])/60 + float(lat_split[2])/3600
	decimal_lon = float(lon_split[0]) + float(lon_split[1])/60 + float(lon_split[2])/3600

	return [decimal_lat, decimal_lon]

# From Homework 4
def compute_homography(src, dst):
    # This function computes the homography from src to dst.
    #
    # Input:
    #     src: source points, shape (n, 2)
    #     dst: destination points, shape (n, 2)
    # Output:
    #     H: homography from source points to destination points, shape (3, 3)
    
    A = np.zeros([2*src.shape[0], 9])
    for i in range(src.shape[0]):
        A[2*i, :] = np.array([src[i,0],src[i,1],1,0,0,0,
                              -dst[i,0]*src[i,0],-dst[i,0]*src[i,1],-dst[i,0]])
        A[2*i+1, :] = np.array([0,0,0,src[i,0],src[i,1],1,
                                -dst[i,1]*src[i,0],-dst[i,1]*src[i,1],-dst[i,1]])
    
    w, v = np.linalg.eig(np.dot(A.T, A))
    index = np.argmin(w)
    H = v[:, index].reshape([3,3])
    return H

# From Homework 4
def apply_homography(src, H):
    # Applies a homography H onto the source points, src.
    #
    # Input:
    #     src: source points, shape (n, 2)
    #     H: homography from source points to destination points, shape (3, 3)
    # Output:
    #     dst: destination points, shape (n, 2)
    final = np.zeros_like(src)
    for i in range(len(src)):
        transform = np.append(src[i],[[1]],1)
        result = np.dot(H,transform.T)
        result /= result[2]
        final[i] = result.T[:,:2]
    return final

# Makes homography to map from coordinate system to Latitude/Longitude
# Just for the 12th GML File 
def train_homography(dictionary):
	# Manually measured latitude and longitude for 5 buildings
	new_lat_long = np.array([[40.712994,74.013227], [40.748629,73.985807],[40.751655,73.975488],[40.702138,74.012065],[40.769110,73.981620]])

	# Test Buildings in Coordinate System
	One_World_Trade = dictionary['Bldg_21510003972']
	Empire_State = dictionary['Bldg_12210009096']
	Chrysler = dictionary['Bldg_12210010508']
	New_York_Plaza = dictionary['Bldg_21210000601']
	Trump_Int = dictionary['Bldg_12210018998']

	# Build Source Points
	Buildings = [One_World_Trade, Empire_State, Chrysler, New_York_Plaza, Trump_Int]
	src_data = [[(i['X'][0]+i['X'][1])/2,(i['Y'][0]+i['Y'][1])/2] for i in Buildings]

	# Compute Homography
	H = compute_homography(np.matrix(src_data),new_lat_long)
	return H 

if __name__ == '__main__':
	dictionary = parse('DA_WISE_GMLs/DA12_3D_Buildings_Merged.gml')
	H = train_homography(dictionary)
	# Test Case: This is the Castle Clinton National Monument
	test = dictionary['Bldg_12210022273']
	print(apply_homography(np.matrix([(test['X'][0]+test['X'][1])/2,(test['Y'][0]+test['Y'][1])/2]),H))
