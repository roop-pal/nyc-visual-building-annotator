import numpy as np
import cv2
import matplotlib.pyplot as plt
import conversion


#################
# Assumes translation vector comes in with x and y as positive numbers (maybe z too, not sure if that matters)
# To update just change lines 29-31
#################


def project(R, T, building_polys, focal_length=29, pixel_size=0.00122, view_x=3024, view_y=4032):
    print('focal_length:',focal_length,'pixel_size:',pixel_size,'view_x:',view_x,view_y)
    #Input: R - rotation matrix
    #       T - translation vector
    #       building_polys - list of lists of polygons

    center_x, center_y = view_x // 2, view_y // 2
    x_offset, y_offset, z_offset = T[0], T[1], T[2]
    T = np.array([[0], [0], [0]])

    C = conversion.camera_matrix(R, T, focal_length, pixel_size, center_x, center_y)

    twoD_pts = []
    for polygon in building_polys:
        poly_pts = np.zeros((len(polygon), 2))
        for idx, pt in enumerate(polygon):
            pt = np.array(pt)
            pt[0] -= x_offset
            pt[1] -= y_offset
            pt[2] -= z_offset
            new_pt = np.append(pt, np.array([1]), axis=0)
            new_pt = np.matmul(C, new_pt)
            new_pt = new_pt[:2] / new_pt[2]
            poly_pts[idx] = new_pt
        twoD_pts.append(poly_pts)

    new_img = np.zeros((view_y, view_x))
    for poly in twoD_pts:
        poly = poly.astype(int)
        for pt in poly:
            if not (0 < pt[0] < view_x) and not (0 < pt[1] < view_y): continue
        cv2.fillPoly(new_img, pts=[poly], color=(255, 255, 255))
    flipped_new = np.fliplr(new_img)
    print(flipped_new)

    # import IPython
    # IPython.embed()
    nonzero = cv2.findNonZero(flipped_new.astype('uint8'))
    nonzero = nonzero.reshape((nonzero.shape[0], nonzero.shape[2]))
    final = flipped_new[np.min(nonzero[:, 1]):np.max(nonzero[:, 1]), np.min(nonzero[:, 0]):np.max(nonzero[:, 0])]
    return final

def projection(building_polys,R,T,focal_length=29,pixel_size=0.00122,view_x = 3024,view_y = 4032):
    center_x,center_y = view_x//2, view_y//2

    x_offset,y_offset,z_offset = T[0],T[1],T[2]
    T = np.array([[0], [0], [0]])

    C = conversion.camera_matrix(R, T, focal_length, pixel_size, center_x, center_y)

    twoD_pts = []
    #for polygon in building_polys[bldg_id]:
    for polygon in building_polys:
        poly_pts = np.zeros((len(polygon),2))
        for idx, pt in enumerate(polygon):
            pt = np.array(pt)
            pt[0] -= x_offset
            pt[1] -= y_offset
            pt[2] -= z_offset
            new_pt = np.append(pt,np.array([1]), axis=0)
            new_pt = np.matmul(C,new_pt)
            new_pt = new_pt[:2]/new_pt[2]
            poly_pts[idx] = new_pt
        twoD_pts.append(poly_pts)

    new_img = np.zeros((view_y, view_x))
    for poly in twoD_pts:
        poly = poly.astype(int)
        for pt in poly:
            if not(0 < pt[0] < view_x) and not(0 < pt[1] < view_y):
                continue
        cv2.fillPoly(new_img, pts=[poly], color=(255,255,255))
    flipped_new = np.fliplr(new_img)
    nonzero = cv2.findNonZero(flipped_new.astype('uint8'))
    nonzero = nonzero.reshape((nonzero.shape[0],nonzero.shape[2]))
    final = flipped_new[np.min(nonzero[:,1]):np.max(nonzero[:,1]),np.min(nonzero[:,0]):np.max(nonzero[:,0])]
    return final