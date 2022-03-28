import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
img = cv.imread('F:\\ABEN\\wheat_spike_count\\androidTest\\pexels-pixabay-41959.jpg',0)
blur = cv.GaussianBlur(img,(5,5),0)
ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)

th3 = cv.cvtColor(th3, cv.COLOR_GRAY2RGB)
th3[np.all(th3 == (0, 0, 0), axis=-1)] = (66,66,66)
th3[np.all(th3 == (255, 255, 255), axis=-1)] = (255,204,0)
cv.imwrite('Wfilename.png',th3)
plt.imsave('WBgray.png',th3)
plt.imshow(th3,'gray')
plt.show()
