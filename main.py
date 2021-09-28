# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pytesseract

from cin import extract_cin
from crop_image import deskew
from passport import extract_passport

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

###### put your own path ######
pytesseract.pytesseract.tesseract_cmd = r'/Users/macbookair/PycharmProjects/stagefinal/tesseract-ocr-setup-3.02.02.exe'

# get info from an image (id card or passport)
def extract(front, back=None):
  if back == None:
    res = extract_passport(deskew(front))
  else:
    res = extract_cin(deskew(front), deskew(back))
  print(res)
  return res


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    res = extract('images/tes1.jpg', 'images/backnada1.jpg')
    # print(res)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
