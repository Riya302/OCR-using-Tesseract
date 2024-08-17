Additiona laguages can be used for the OCR using


custom_config = r'-l LANG --psm 6'
pytesseract.image_to_string(img, config=custom_config)

where LANG is the 3 letter code of the language you want to use in the tesseract library.
You can check the languages available by typing this in the terminal

$ tesseract --list-langs

To download tesseract for a specific language use

$ sudo apt-get install tesseract-ocr-LANG
