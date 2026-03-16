import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Nont-Grade Pro", layout="wide")
st.title("📸 ระบบสแกนข้อสอบครูนนท์ (เวอร์ชันจูนเป้า)")

# --- 1. แถบควบคุมด้านซ้าย (Sidebar) ---
st.sidebar.header("🎯 ปรับจูนตำแหน่งสแกน")
x_off = st.sidebar.slider("ขยับซ้าย-ขวา", -200, 200, 0)
y_off = st.sidebar.slider("ขยับขึ้น-ลง", -200, 200, 0)
scale = st.sidebar.slider("ขยาย/หด ขนาดเป้า", 0.5, 1.5, 1.0, 0.01)
thresh_val = st.sidebar.slider("ความเข้มแสง (Threshold)", 50, 200, 150)

ans_input = st.sidebar.text_area("เฉลย (1.ก, 2.ข...)", value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข")

# --- 2. ฟังก์ชันตรวจจับ ---
def get_answers(text):
    ans_map = {'ก': 0, 'ข': 1, 'ค': 2, 'ง': 3, 'จ': 4}
    matches = re.findall(r'[ก-จ]', text)
    return [ans_map[a] for a in matches]

img_file = st.camera_input("สแกนกระดาษคำตอบ")

if img_file:
    image = Image.open(img_file)
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)[1]
    
    current_key = get_answers(ans_input)
    score = 0
    
    # วาดเป้าให้คุณครูเห็นบนหน้าจอ
    debug_img = img.copy()
    
    # พิกัดฐาน (Base Coordinates)
    blocks = [(1,10,143,856), (11,20,394,353), (21,30,394,856), (31,40,646,353), (41,50,646,856)]
    
    for start, end, xs, ys in blocks:
        for i in range(start, end + 1):
            pixel_data = []
            for choice in range(5):
                # คำนวณพิกัดใหม่ตามการปรับจูน
                x = int((xs + (choice * 33.5 * scale)) + x_off)
                y = int((ys + ((i-start) * 39.4 * scale)) + y_off)
                
                # ตรวจสอบความเข้ม
                if y < thresh.shape[0] and x < thresh.shape[1]:
                    roi = thresh[y-8:y+8, x-8:x+8]
                    pixel_data.append(np.sum(roi))
                    # วาดวงกลมสีเขียวโชว์ตำแหน่งที่แอป "ส่อง"
                    cv2.circle(debug_img, (x, y), 5, (0, 255, 0), 2)
            
            if pixel_data and np.argmax(pixel_data) == current_key[i-1 if i-1 < len(current_key) else 0]:
                score += 1

    # --- 3. แสดงผล ---
    st.image(debug_img, caption="ตรวจสอบว่าวงกลมสีเขียวตรงกับจุดที่เด็กฝนไหม")
    st.success(f"🎯 คะแนนที่ได้: {score} / {len(current_key)}")
