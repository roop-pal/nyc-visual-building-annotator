import conversion
import gml_parser
import collision
import numpy as np
from projection import project

if __name__ == '__main__':

    # Phone input
    # lat,long,pressure = None
    # x,y,z = None
    # image = None


    bldg_info = gml_parser.parse('DA12_3D_Buildings_Merged.gml')

    H = conversion.train_homography(bldg_info)
    H_inv = np.linalg.inv(H)

    # R = conversion.rotation_matrix(x, y, z)
    # T = conversion.translation_vector(lat,long,pressure,H_inv)
    # T = np.array([[9.87285e+05],[2.09991e+05],[6.14687e+02]])
    # Due to serious problems with phone sensor reliability, we have had to resort to finding parameters in MeshLab
    R,T = collision.extract_rotation_translation('''<!DOCTYPE ViewState>
<project>
 <VCGCamera CameraType="0" RotationMatrix="0.942279 -0.32846 0.0649986 0 -0.0871034 -0.0530227 0.994787 0 -0.323302 -0.943028 -0.0785722 0 0 0 0 1 " FocalMm="55.1807" ViewportPx="2397 1726" PixelSizeMm="0.0369161 0.0369161" CenterPx="1198 863" LensDistortion="0 0" TranslationVector="-980273 -198016 -580.979 1"/>
 <ViewSettings NearPlane="0.909327" FarPlane="343.548" TrackScale="0.00312211"/>
</project>

''')
    # C = conversion.camera_matrix(R, T)
    test_point = [*conversion.GPS_to_coordinate(40.748412, -73.985669, H_inv), 0.0]
    euler = conversion.rotationMatrixToEulerAngles(R)
    print('euler', euler)
    print('T', -T.T[0])
    print(-T.T[0], test_point)
    coord = collision.collision_check(-T.T[0], euler, bldg_info,step=1)
    print('coord', coord)
    assert coord
    bldg_id = coord

    import csv

    buildings = {}
    with open('building_ids.tsv', 'r') as f:
        f = csv.reader(f, delimiter='\t')
        i = 0
        info = ''
        for row in f:
            if i % 5 == 0:
                info = row
            if i % 5 == 3:
                buildings['Bldg_' + row[1]] = info
            i += 1

    if bldg_id in buildings:
        print(buildings[bldg_id])