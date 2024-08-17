import pytesseract
from pdf2image import convert_from_path
import cv2
import os
import streamlit as st
from io import StringIO

# Converts PDF to list of images
def pdf_to_img(pdf):
    pdf_pages = convert_from_path(pdf, dpi=350, poppler_path='/opt/homebrew/bin')
    i = 1
    img_list = []
    for page in pdf_pages:
        page.save('page' + str(i) + '.jpg', 'JPEG')
        img_list.append('page' + str(i) + '.jpg')
        i += 1
    print('PDF to Image Conversion Successful!')
    return img_list

# Each image is processed, contours are plotted and sorted
def bounding_boxes(img_list, show_boxes):
    boxes = {}
    for curr_img in img_list:
        img = cv2.imread(curr_img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, ksize=(9, 9), sigmaX=0)
        thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 30)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        dilate = cv2.dilate(thresh, kernel, iterations=4)
        contours, _ = cv2.findContours(dilate, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

        temp = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if cv2.contourArea(contour) < 10000:
                continue
            temp.append([x, y, w, h])
            if show_boxes:
                cv2.rectangle(img, (x, y), (x + w, y + h), color=(255, 0, 255), thickness=3)
        if show_boxes:
            img = cv2.resize(img, (500, 700), interpolation=cv2.INTER_AREA)
            st.image(image=img, caption=curr_img)
        boxes[curr_img] = temp
    print('Contours saved Successfully!')
    return boxes

# Text is extracted from each contour stored
def extract_text(boxes):
    pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
    text = ''
    for key in boxes:
        img = cv2.imread(key)
        for x, y, w, h in boxes[key]:
            cropped_image = img[y:y + h, x:x + w]
            _, thresh = cv2.threshold(cropped_image, 127, 255, cv2.THRESH_BINARY)
            text += str(pytesseract.image_to_string(thresh, config='-l snd+eng --psm 6'))
    print('Text Extraction Completed!')
    return text

# Base function
def ocr(filename, show_boxes):
    if filename:
        img_list = pdf_to_img(filename)
        boxes = bounding_boxes(img_list, show_boxes)
        if not show_boxes:
            text = extract_text(boxes)
            return text
    else:
        st.warning('Please select a PDF file!')

# Main code
st.title('Text Extraction using OCR')
uploaded_file = st.file_uploader(label='Upload PDF', type='pdf')

if 'text' not in st.session_state:
    st.session_state.text = ''

if 'flag' not in st.session_state:
    st.session_state.flag = False

if uploaded_file:
    filename = uploaded_file.name
    with open(filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    row0col1, row0col2 = st.columns([1, 1])
    with row0col1:
        if st.button(label='Run OCR'):
            st.session_state.text = ocr(filename, 0)
            st.session_state.flag = True
        
        if st.session_state.flag:
            st.download_button(
                label="Save File",
                data=st.session_state.text,
                file_name='extracted_text.txt',
                mime='text/plain'
            )
                
    with row0col2:
        if st.button(label='Bounding Box'):
            ocr(filename, 1)

