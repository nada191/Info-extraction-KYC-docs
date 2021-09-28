import cv2
import numpy as np
import math
from typing import Tuple, Union
from deskew import determine_skew
from mtcnn import MTCNN


# Rotate an image
def rotate(image: np.ndarray, angle: float, background: Union[int, Tuple[int, int, int]]) -> np.ndarray:
    old_width, old_height = image.shape[:2]
    angle_radian = math.radians(angle)
    width = abs(np.sin(angle_radian) * old_height) + abs(np.cos(angle_radian) * old_width)
    height = abs(np.sin(angle_radian) * old_width) + abs(np.cos(angle_radian) * old_height)

    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    rot_mat[1, 2] += (width - old_width) / 2
    rot_mat[0, 2] += (height - old_height) / 2
    return cv2.warpAffine(image, rot_mat, (int(round(height)), int(round(width))), borderValue=background)

# correct the skewing images
def deskew(path):
    image = cv2.imread(path)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    angle = determine_skew(grayscale)
    rotated = rotate(image, angle, (0, 0, 0))
    return rotated

# crop the image (id card) and extract the person's photo
def crop_image(img):
    detector = MTCNN()
    data = detector.detect_faces(img)
    biggest = 0
    if data != []:
        for faces in data:
            box = faces['box']
            # calculate the area in the image
            area = box[3] * box[2]
            if area > biggest:
                biggest = area
                bbox = box
        bbox[0] -= 20  # left
        bbox[1] -= 30  # top
        bbox[2] += 50  # right
        bbox[3] += 40  # bottom

        # bbox[0]= 0 if bbox[0]<0 else bbox[0]
        # bbox[1]= 0 if bbox[1]<0 else bbox[1]
        img1 = None
        imgcrop = None
        img1 = img[bbox[1]: bbox[1]+bbox[3], bbox[0]: bbox[0]+bbox[2]] # personal photo
        imgcrop = img[bbox[2]-50:, bbox[1]+20:bbox[1]+1250] # cropped image
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB) # convert from bgr to rgb
        imgcrop = cv2.cvtColor(imgcrop, cv2.COLOR_BGR2RGB) # convert from bgr to rgb

        return (True, img1, imgcrop)
    else:
         return (False, None, None)