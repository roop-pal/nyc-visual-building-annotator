import conversion
import gml_parser
import numpy as np
from projection import project

if __name__ == '__main__':

    # Phone input
    lat,long,pressure = None
    x,y,z = None
    image = None

    bldg_info = gml_parser.parse('DA12_3D_Buildings_Merged.gml')

    H = conversion.train_homography(bldg_info)
    H_inv = np.linalg.inv(H)

    R = conversion.rotation_matrix(x, y, z) # DOUBLE CHECK CUZ PROBABLY WRONG
    # T = translation_vector(lat,long,pressure,H_inv)
    T = np.array([[9.87285e+05],[2.09991e+05],[6.14687e+02]])
    C = conversion.camera_matrix(R, T) # if time DOUBLE CHECK

    bldg_id = 'Bldg_12210009096'

    project(C,bldg_id, bldg_info[bldg_id]['polygons'])
