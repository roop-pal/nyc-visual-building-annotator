import conversion
import gml_parser
import collision
import conversion
import projection
import matching
import numpy as np
import cv2
from projection import project


def getMeshLab(R,T):
    return '''<!DOCTYPE ViewState>
    <project>
     <VCGCamera  RotationMatrix="{0} {1} {2} 0 {3} {4} {5} 0 {6} {7} {8} 0 0 0 0 1 " LensDistortion="0 0" TranslationVector="-{9} -{10} -{11} 1" FocalMm="55.1807" CameraType="0" PixelSizeMm="0.0369161 0.0369161" ViewportPx="2397 1726" CenterPx="1198 863"/>
     <ViewSettings NearPlane="0.909327" TrackScale="0.018121" FarPlane="116.735"/>
    </project>'''.format(*[round(i, 7) for i in np.append(R.flatten(),T.flatten())])


def extract_rotation_translation_intrinsics(s):
    rotation_matrix = s[s.find('RotationMatrix') + 16:]
    rm = [float(i) for i in rotation_matrix[:rotation_matrix.find('"')].split(' ')[:-1]]
    R = np.array([rm[:3],rm[4:7],rm[8:11]])
    translation_vector = s[s.find('TranslationVector') + 19:]
    T = np.array([[float(i)] for i in translation_vector[:translation_vector.find('"')].split(' ')[:-1]])
    focal_mm = float(s[s.find('FocalMm') +9:].split('"')[0])
    pixel_mm = float(s[s.find('PixelSizeMm') + 13:].split(' ')[0])
    viewport = s[s.find('ViewportPx') + 12:]
    vx,vy = [int(i) for i in viewport[:viewport.find('"')].split(' ')]
    return R,T,[focal_mm,pixel_mm,vx,vy]


def parse_buildings_info():
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
    return buildings


def putMeshLab(real_image, s, bldg_info=gml_parser.parse('DA12_3D_Buildings_Merged.gml'),bldg_id=False,buildings=parse_buildings_info(),f=1):
    R, T, intrinsics = extract_rotation_translation_intrinsics(s)
    euler = conversion.rotationMatrixToEulerAngles(R)
    coord = collision.collision_check(-T.T[0], euler, bldg_info, step=10)
    print('coord', coord)
    if bldg_id:
        coord = bldg_id
    assert coord
    import matplotlib.pyplot as plt
    p = projection.projection(bldg_info[coord]['polygons'],R,-T.T[0],*intrinsics)
    p = cv2.resize(p, (0, 0), fx=f, fy=f) # Hardcoded only for current meshlab workaround due to different intrinsics. Unnecessary for real examples
    dst = matching.ssd_match(real_image, p)
    txt = buildings[coord][1]+'\n'+buildings[coord][-1]
    fig = plt.figure()
    fig.text(0.5, 0.008, txt, ha='center')
    plt.axis('off')
    plt.imshow(dst, cmap='gray')
    plt.show()


if __name__ == '__main__':
    # ABANDONED DUE TO POOR SENSOR DATA
    # lat, long, altitude = 40.7682033, -73.9791756, 343.548
    # x, y, z = -1.1263802, -1.36967965, -0.18913514
    # image = 'messy-max/1.png'
    # H = conversion.train_homography(bldg_info)
    # H_inv = np.linalg.inv(H)
    # test_point = [*conversion.GPS_to_coordinate(40.768203392140656, -73.97917561542701,H_inv),altitude]
    # coord = collision.collision_check(test_point,[x,y,z],bldg_info)
    # print('coord',coord)
    # R = conversion.rotation_matrix(x, y, z)
    # R = np.array([[ 0.422264  ,  0.906445  ,  0.00707832],
    #    [-0.0808311 ,  0.0298754 ,  0.99628   ],
    #    [ 0.902862  , -0.421265  ,  0.0858845 ]])
    # T = conversion.translation_vector(lat, long, -altitude, H_inv)

    # lat, long, pressure = 40.7687992, -73.9793076, 0
    # x, y, z = 0.03045, 0.81916, 0.56975
    # image = 'messy-max/2.png'
    # H = conversion.train_homography(bldg_info)
    # H_inv = np.linalg.inv(H)
    # R = conversion.rotation_matrix(x, y, z)
    # T = conversion.translation_vector(lat,long,pressure,H_inv)
    # print(getMeshLab(R,T))
    # Due to serious problems with phone sensor reliability, we have had to resort to finding parameters in MeshLab
    # Collision works for this input.
    # '''<!DOCTYPE ViewState>
    # <project>
    #  <VCGCamera RotationMatrix="0.422264 0.906445 0.00707832 0 -0.0808311 0.0298754 0.99628 0 0.902862 -0.421265 0.0858845 0 0 0 0 1 " PixelSizeMm="0.0369161 0.0369161" TranslationVector="-990057 -219171 -345.052 1" ViewportPx="2397 1726" CenterPx="1198 863" CameraType="0" LensDistortion="0 0" FocalMm="55.1807"/>
    #  <ViewSettings NearPlane="0.909327" TrackScale="0.00263221" FarPlane="101.296"/>
    # </project>'''


    putMeshLab(cv2.imread('1.png'),'''<!DOCTYPE ViewState>
    <project>
     <VCGCamera ViewportPx="907 622" CameraType="0" RotationMatrix="0.306982 0.950231 0.0531318 0 0.0740677 -0.0795119 0.994078 0 0.948829 -0.301229 -0.0947902 0 0 0 0 1 " TranslationVector="-990496 -219173 -67.16 1" FocalMm="19.8855" LensDistortion="0 0" CenterPx="453 311" PixelSizeMm="0.0369161 0.0369161"/>
     <ViewSettings TrackScale="0.00265847" FarPlane="111.982" NearPlane="0.909327"/>
     </project>
        ''',bldg_id='Bldg_12210018998',f=11)

    putMeshLab(cv2.imread('2.png'),'''<!DOCTYPE ViewState>
    <project>
     <VCGCamera ViewportPx="2397 1726" FocalMm="55.1807" TranslationVector="-989869 -219875 -148.972 1" CenterPx="1198 863" CameraType="0" RotationMatrix="-0.998049 -0.0623382 -0.00352987 0 -0.0224335 0.305258 0.952005 0 -0.0582688 0.950227 -0.306061 0 0 0 0 1 " LensDistortion="0 0" PixelSizeMm="0.0369161 0.0369161"/>
     <ViewSettings TrackScale="0.00674607" NearPlane="0.909327" FarPlane="675.975"/>
    </project>
    ''', bldg_id='Bldg_12210022082',f=2.5)

    putMeshLab(cv2.imread('3.png'),'''<!DOCTYPE ViewState>
    <project>
     <VCGCamera ViewportPx="2397 1726" FocalMm="55.1807" TranslationVector="-990654 -218787 -187.559 1" CenterPx="1198 863" CameraType="0" RotationMatrix="-0.906211 -0.422289 -0.0212921 0 -0.0453347 0.0469731 0.997867 0 -0.420388 0.905243 -0.0617113 0 0 0 0 1 " LensDistortion="0 0" PixelSizeMm="0.0369161 0.0369161"/>
     <ViewSettings TrackScale="0.0260809" NearPlane="0.909327" FarPlane="2827.78"/>
    </project>
    ''', bldg_id='Bldg_12210017697',f=3)

    putMeshLab(cv2.imread('4.png'),'''<!DOCTYPE ViewState>
    <project>
     <VCGCamera CenterPx="453 311" RotationMatrix="0.708013 0.700694 0.0880097 0 -0.180904 0.0594887 0.9817 0 0.682635 -0.710978 0.168877 0 0 0 0 1 " LensDistortion="0 0" PixelSizeMm="0.0369161 0.0369161" ViewportPx="907 622" FocalMm="19.8855" CameraType="0" TranslationVector="-992083 -217930 -367.952 1"/>
     <ViewSettings NearPlane="0.909327" FarPlane="114.83" TrackScale="0.00290449"/>
    </project>''', bldg_id='Bldg_12210005483',f=9)