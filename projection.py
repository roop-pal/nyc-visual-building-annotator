import numpy as np
import matplotlib.pyplot as plt

def project(C,bldg_id, building_polys):
    total_num_pts = 0
    for polygon in building_polys:
        total_num_pts += len(polygon)

    all_2D_pts = np.zeros((total_num_pts, 2))  # for np.max and np.min

    twoD_pts = []
    all_idx = 0
    for polygon in building_polys:
        poly_pts = np.zeros((len(polygon), 2))
        for idx, pt in enumerate(polygon):
            new_pt = np.append(np.array(pt), np.array([1]), axis=0)
            new_pt = np.matmul(C, new_pt)
            new_pt = new_pt[:2] / new_pt[2]
            poly_pts[idx] = new_pt
            all_2D_pts[all_idx] = new_pt  # for np.max and np.min
            all_idx += 1
        twoD_pts.append(poly_pts)

    max_x = np.max(all_2D_pts[:, 0])
    min_x = np.min(all_2D_pts[:, 0])
    max_y = np.max(all_2D_pts[:, 1])
    min_y = np.min(all_2D_pts[:, 1])

    # adjust pts to fit within window
    if min_x < 0:
        for poly in twoD_pts:
            poly[:, 0] -= min_x
        all_2D_pts[:, 0] -= min_x
    if min_y < 0:
        for poly in twoD_pts:
            poly[:, 1] -= min_y
        all_2D_pts[:, 1] -= min_y

    max_x = np.max(all_2D_pts[:, 0])
    min_x = np.min(all_2D_pts[:, 0])
    max_y = np.max(all_2D_pts[:, 1])
    min_y = np.min(all_2D_pts[:, 1])

    scale = (max_y - min_y) / 1000

    new_img = np.zeros((1001, int((max_x - min_x) / scale) + 1))

    for idx, poly in enumerate(twoD_pts):
        poly[:, 0] -= min_x
        poly[:, 0] /= scale
        poly[:, 1] -= min_y
        poly[:, 1] /= scale
        twoD_pts[idx] = poly.astype(int)

    for poly in twoD_pts:
        # cv2.polylines(new_img,[poly],False,(255,255,255))
        cv2.fillPoly(new_img, pts=[poly], color=(255, 255, 255))
        cv2.polylines(new_img, [poly], 1, (0, 255, 255))

    plt.figure(figsize=(20, 10))

    plt.imshow(new_img, cmap='gray')
    plt.show()