import numpy as np
import matplotlib.pyplot as plt
import cv2

# Input: The filename of the projected and real image.
# Output: An overlay of the two images with a rectangle
#         around the identified image.
def ssd_match(real_image, projected_image):
    real_image = cv2.imread(real_image)
    real_image = cv2.cvtColor(real_image, cv2.COLOR_BGR2GRAY)

    w,h = real_image.shape
    
    projected_image = cv2.imread(projected_image)
    projected_image = cv2.cvtColor(projected_image, cv2.COLOR_BGR2GRAY)
    projected_image = cv2.resize(projected_image, (0,0), fx=0.5, fy=0.5) 
    projected_image = projected_image.astype('uint8')

    W,H = projected_image.shape

    width = w-W+1
    height = h-H+1

    result = np.zeros((width,height))
    SSD = cv2.matchTemplate(real_image, projected_image, cv2.TM_SQDIFF) #SSD
    
    maxi = (0,0)
    for j in range(SSD.shape[0]):
        for i in range(SSD.shape[1]):
            if SSD[maxi[0],maxi[1]] < SSD[j,i]:
                maxi = (j,i)

    w, h = projected_image.shape

    overlay_img = np.zeros_like(real_image)
    overlay_img[maxi[0]:maxi[0]+w,maxi[1]:maxi[1]+h] = projected_image

    dst = cv2.addWeighted(real_image,0.75,overlay_img,0.25,0)

    cv2.rectangle(dst,(maxi[1],maxi[0]),(maxi[1]+h,maxi[0]+w),[255],2)

    return dst

if __name__ = '__main__'
    plt.imshow(ssd_match('empire-state-building.png','filled_empire.png'),cmap='gray')