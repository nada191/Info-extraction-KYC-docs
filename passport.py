import base64
import calendar
import json
import os
import shutil

import cv2
from matplotlib import pyplot as plt
from passporteye import read_mrz

from crop_image import crop_image


# delete signs (<) from the extracted text
def delete_signs(sent):
    sent = sent.strip()
    L = sent.split(' ')
    word = ''
    j = len(L)
    for i in L:
        if i == '':
            j = L.index(i)
    L = L[:j]
    word = ' '.join(L)
    return word

# delete signs (<) from the nationality
def delete_signs_nat(sent):
    sent = sent.strip()
    sent = sent.replace('<', '')
    return sent

# delete signs (<) from the id number
def delete_sign(sent):
    sent = sent.strip()
    j = len(sent)
    for i in sent:
        if i == '<':
            j = sent.index(i)
    sent = sent[:j]
    return sent

# get all the information from the passport
def extract_passport(image):
    status, img, imgcrop = crop_image(image)
    if status:
        plt.imshow(img)
        img_string = base64.b64encode(img)
    else:
        print('No facial image was detected')
        img_string = None

    # Process image
    if os.path.exists('images/deskew'):
        shutil.rmtree('images/deskew', ignore_errors=True)

    os.mkdir('images/deskew')
    cv2.imwrite('images/deskew/rotated.jpg', image)

    mrz = read_mrz('images/deskew/rotated.jpg')

    # get the dict of the info
    mrz_data = mrz.to_dict()

    date = mrz_data['date_of_birth']
    date = date[4:] + ' ' + calendar.month_name[int(date[2:4])] + ' ' + date[0:2]

    info = {}
    info['Nationality'] = delete_signs_nat(delete_signs(mrz_data['nationality']))
    info['Name'] = delete_signs(mrz_data['names'])
    info['Lastname'] = delete_signs(mrz_data['surname'])
    info['Date_of_birth'] = date
    info['Gender'] = mrz_data['sex']
    info['ID_Number'] = delete_sign(mrz_data['personal_number'])
    if img_string != None:
        info['Photo'] = img_string.decode("utf-8")
    else:
        info['Photo'] = ''
    res = json.dumps(info)
    return res

