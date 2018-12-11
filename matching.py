import numpy as np
import matplotlib.pyplot as plt
import cv2


# Input: The filename of the projected and real image.
# Output: An overlay of the two images with a rectangle
#         around the identified image.
def ssd_match(real_image, projected_image):
    saved_real = real_image.copy()
    saved_proj = real_image.copy()
    saved_proj = np.stack((saved_proj,) * 3, -1)

    real_image = real_image.astype('uint8')
    real_image = cv2.cvtColor(real_image, cv2.COLOR_BGR2GRAY)

    w, h = real_image.shape
    projected_image = projected_image.astype('uint8')

    W, H = projected_image.shape

    width = w - W + 1
    height = h - H + 1

    SSD = cv2.matchTemplate(real_image, projected_image, cv2.TM_SQDIFF)  # SSD

    maxi = (0, 0)
    for j in range(SSD.shape[0]):
        for i in range(SSD.shape[1]):
            if SSD[maxi[0], maxi[1]] < SSD[j, i]:
                maxi = (j, i)

    w, h = projected_image.shape
    overlay_img = np.zeros_like(real_image)
    overlay_img[maxi[0]:maxi[0] + w, maxi[1]:maxi[1] + h] = projected_image

    overlay_img = np.stack((overlay_img,) * 3, -1)
    dst = cv2.addWeighted(saved_real, 0.75, overlay_img, 0.25, 0)

    return dst

if __name__ == '__main__':
    plt.imshow(ssd_match('empire-state-building.png','filled_empire.png'),cmap='gray')