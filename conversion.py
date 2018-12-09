import numpy as np
import gml_parser
import math

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

	return [decimal_lat, -decimal_lon]

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
	new_lat_long = np.array([[40.712994,-74.013227], [40.748629,-73.985807],[40.751655,-73.975488],[40.702138,-74.012065],[40.769110,-73.981620]])

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

# Input: Lat/Long string or float
# Output: np.matrix of position in the coordinate system
def GPS_to_coordinate(Lat, Long, inv_H):
    if type(Lat) is str and type(Long) is str:
        new_degrees = convert_degrees(Lat,Long)
    elif type(Lat) is float and type(Long) is float:
        new_degrees = [Lat, Long]
    else:
        raise TypeError

    dest = apply_homography(np.matrix(new_degrees),inv_H)

    return dest.tolist()[0]

def translation_vector(lat,long,pressure,inv_H):
    x,y = GPS_to_coordinate(lat,long,inv_H)
    z = barometer_to_z(pressure)
    T = np.array([[x],[y],[z]])
    return T

# Input: x,y position in the model coordinate system
# Output: Lat/Long in degrees format
def coordinate_to_GPS(x, y):
    dictionary = gml_parser.parse('DA12_3D_Buildings_Merged.gml')
    H = train_homography(dictionary)

    dest = apply_homography(np.matrix([x,y]),H)

    return dest.tolist()[0]


# TODO: Implement using hardcoded sea level pressure
def barometer_to_z(pressure):
    return 0


def rotation_matrix(x, y, z):
    # x,y,z = 0 when phone is flat on table with top facing east
    # normalize from -1 to 1 to 0 to 2pi

    theta = x, y, z

    theta = [axis % 2 * np.pi for axis in theta]

    R_x = np.array([[1, 0, 0],
                    [0, np.cos(theta[0]), -np.sin(theta[0])],
                    [0, np.sin(theta[0]), np.cos(theta[0])]
                    ])

    R_y = np.array([[np.cos(theta[1]), 0, np.sin(theta[1])],
                    [0, 1, 0],
                    [-np.sin(theta[1]), 0, np.cos(theta[1])]
                    ])

    R_z = np.array([[np.cos(theta[2]), -np.sin(theta[2]), 0],
                    [np.sin(theta[2]), np.cos(theta[2]), 0],
                    [0, 0, 1]
                    ])

    R = np.dot(R_z, np.dot(R_y, R_x))

    return R

def camera_matrix(R,T, focal_len=29, pixel_size=0.00122):
    fx = focal_len/pixel_size
    fy = focal_len/pixel_size
    intrinsic_matrix = np.array([[fx,0,0],
                            [0,fy,0],
                            [0,0,1]])
    extrinsic_matrix = np.append(R,T,axis=1)
    camera_matrix = np.matmul(intrinsic_matrix, extrinsic_matrix)
    return camera_matrix


# Checks if a matrix is a valid rotation matrix.
def isRotationMatrix(R):
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype=R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-5


# Calculates rotation matrix to euler angles
# The result is the same as MATLAB except the order
# of the euler angles ( x and z are swapped ).
def rotationMatrixToEulerAngles(R):
    assert (isRotationMatrix(R))

    sy = math.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0

    return np.array([y, x, z])

if __name__ == '__main__':
    # For testing purposes
    dictionary = gml_parser.parse('DA12_3D_Buildings_Merged.gml')
    test = dictionary['Bldg_12210022273']
    H = train_homography(dictionary)
    H_inv = np.linalg.inv(H)

	# Test Case: This is the Castle Clinton National Monument
    # print("The Lat/Long Coordinates of the Castle Clinton National Monument are: ")
    # print(coordinate_to_GPS((test['X'][0]+test['X'][1])/2,(test['Y'][0]+test['Y'][1])/2))
    #
    # # Test Case: One World Trade Center
    # print("The GPS coordinates of One World Trade is",'40 42 46.8,','-74 0 48.6',"which is:")
    # print(GPS_to_coordinate('40 42 46.8','74 0 48.6'))
    #
    # # Test Case: One World Trade in degrees
    # print("Same Test except in Degrees:")
    # print(GPS_to_coordinate(40.713009, -74.013678))
    # s=translation_vector(40.713009, -74.013678,0,np.linalg.inv(H))
    # print(s)