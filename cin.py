import base64
import json
from math import ceil

import cv2
from fuzzywuzzy import process
import re

from matplotlib import pyplot as plt

from crop_image import crop_image
from extract import extract_easyocr, order_boxes

MONTH_NAME = ['جانفي', 'فيفري', 'مارس' 'افريل', 'ماي', 'جوان', 'جويلية', 'اوت', 'سبتمبر', 'اكتوبر', 'نوفمبر', 'ديسمبر']
birth = ['الولادة', 'لولادة','ولادة','لادة','ادة']
name_begin = ['لاسم', 'اسم', 'سم', 'م', 'الاسم']
lastname_begin = ['ب', 'قب', 'لقب', 'للقب', 'اللقب', 'القب']
adress_begin = ['العنوان', 'لعنوان', 'عنوان', 'نوان']
government = ['نابل','المهدية','منوبة','المنستير','مدنين','الكاف','القيروان','قفصة','القصرين','قبلي','قابس','صفاقس',' سيدي بوزيد','سوسة','سليانة','زغوان','جندوبة','تونس','توزر','تطاوين','بنزرت',' بن عروس','باجة','أريانة']

# extract date from the date line
def EAST_extract_date(sent):
  sent = sent.strip()
  L = sent.split(' ')
  k = process.extractOne(L[0], birth)
  if k[1] >= 70:
    L.remove(L[0])
  m = L[1]
  L[1] = process.extractOne(m, MONTH_NAME)[0] # Get the word in the list that is most similar to ours
  verified_sent = ' '.join(L)
  return (verified_sent)

# extract the name from the name line
def EAST_extract_name(sent):
  sent = sent.strip()
  stringList = sent.split(' ')
  k = process.extractOne(stringList[0], name_begin)
  if k[1] >= 50 :
    stringList.remove(stringList[0])
  verifiedname = ' '.join(stringList)
  return (verifiedname)

# extract the lastname from the lastname line
def EAST_extract_lastname(sent):
  sent = sent.strip()
  stringList = sent.split(' ')
  k = process.extractOne(stringList[0], lastname_begin)
  if k[1] >= 50 :
    stringList.remove(stringList[0])
  verifiedlastname = ' '.join(stringList)
  return (verifiedlastname)

# extract the id card number from the id card number line
def EAST_extract_nid(sent):
  sent = sent.strip()  # Remove spaces at the beginning and at the end
  nmb_list = [s for s in sent.split() if s.isdigit()]
  nmb = "".join(nmb_list)
  nmb_list, nmb, len(nmb)

  if len(nmb) == 8:
    return nmb
  else:
    return None


# obtain all the information from the front of the identity card
def Extract_CIN_FRONT(image):
  status, img, imgcrp = crop_image(image)
  if status:
    plt.imshow(img)
    img_string = base64.b64encode(img)
  else:
    print('No facial image was detected')
    img = None
    imgcrp = None
    img_string = None

  sent_list = list()
  nid = 'Not Found'
  name = "Not Found"
  lastname = "Not Found"
  birthday = 'Not Found'

  l = image.shape
  if imgcrp.all() == None:  # if we didn't dectect the face, we gonna crop it (id card)
    im = image[ceil(l[0] * 0.25):ceil(l[0] - l[0] * 0.15), ceil(l[1] * 0.27):ceil(l[1] - l[1] * 0.06)]
    res = extract_easyocr(im, 1)
  else:
    res = extract_easyocr(imgcrp, 1)

  ######## order the boxes to read line by line #########
  resfinal = order_boxes(res)

  # the first element must be the nid
  s = 0
  for i in resfinal:
    if i[1].isdigit():
      s = resfinal.index(i)
      break
    else:
      continue
  # print(s)

  # print(resfinal)
  nidsent = resfinal[s][1]
  lastnamesent = resfinal[s + 1][1]
  namesent = resfinal[s + 2][1]
  m = re.search(r"\d", resfinal[s + 4][1]) # the date of birth must start with a number
  new = resfinal[s + 4][1][m.start():]

  nid_extract = EAST_extract_nid(nidsent)
  lastname_extract = EAST_extract_lastname(lastnamesent)
  name_extract = EAST_extract_name(namesent)
  birth_extract = EAST_extract_date(new)

  if nid_extract != None:
    nid = nid_extract
  if name_extract != None:
    name = name_extract
  if lastname_extract != None:
    lastname = lastname_extract
  if birth_extract != None:
    birthday = birth_extract

  l = birthday.split(' ')
  if len(l[0]) > 2:  # if the date does not start with two digits
    l[0] = l[0][:2]
  birthday = ' '.join(l)

  info_dict = dict()
  info_dict['Nid'] = nid
  info_dict['Name'] = name
  info_dict['Last Name'] = lastname
  info_dict['Date_of_Birth'] = birthday
  info_dict['Photo'] = img_string.decode("utf-8")

  return (info_dict)


# obtain the address from the back of the identity card
def Extract_CIN_BACK(image):
  image = cv2.resize(image, (540, 330))
  res = extract_easyocr(image, 0)
  resfinal = order_boxes(res)
  sent  = resfinal[2][1]+' '+resfinal[3][1]
  # print(sent)
  sent = sent.strip()
  stringList = sent.split(' ')
  k = process.extractOne(stringList[0], adress_begin)
  if k[1] >= 50 :
    stringList.remove(stringList[0])
  stringList[-1] = process.extractOne(stringList[-1], government)[0]
  verifiedadress = ' '.join(stringList)
  return verifiedadress

# obtain all the information from the identity card
def extract_cin(front, back):
  resultat = Extract_CIN_FRONT(front)
  resultat['Address'] = Extract_CIN_BACK(back)
  # print(resultat)
  res = json.dumps(resultat)
  return res