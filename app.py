import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Nont-Grade OMR", layout="wide")
st.title("📸 ระบบตรวจข้อสอบ (ปรับจุดสแกนได้)")

# --- 1. แถบตั้งค่าด้านซ้าย ---
st.sidebar.header("1. เฉลย")
ans_input = st.sidebar.text_area("ใส่เฉลย (1.ก, 2.ข...)", value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข", height=150)

st.sidebar.header("2. จูนตำแหน่ง (สำคัญมาก)")
st.sidebar.write("ขยับแถบด้านล่าง จนกว่าจุดสีแดงจะทับวงกลมข้อสอบพอดี")
start_x = st.sidebar.slider("ขยับ ซ้าย-ขวา", 0, 800, 100)
start_y = st.sidebar.slider("ขยับ ขึ้น-ลง", 0, 1000, 200)
space_x = st.sidebar.slider("ระยะห่าง ก.ข.ค.ง.", 10, 50, 25)
space_y = st.sidebar.slider("ระยะห่าง ข้อ 1-2-3", 10, 50, 25)
block_space = st.sidebar.slider("ระยะห่างคอลัมน์", 50, 300, 150)
threshold_val = st.sidebar.slider("ความไวแสง", 50, 200, 120)

def get_answers(text):
    ans_map = {'ก': 0, 'ข': 1, 'ค': 2, 'ง': 3, 'จ': 4}
    matches = re.findall(r'[ก-จ]', text)
    return [ans_map[a] for a in matches if a in ans_map]

# --- 2. ส่วนกล้องและประมวลผล ---
img_file = st.camera_input("พยายามถ่ายให้ตรงและเต็มกระดาษที่สุด")

if img_file:
    # โหลดภาพและปรับขนาดให้เป็นมาตรฐาน (เพื่อให้พิกัดไม่เพี้ยนตามรุ่นมือถือ)
    img = Image.open(img_file)
    img = np.array(img)
    img = cv2.resize(img, (800, 1000)) 
    
    # แปลงเป็นขาวดำเพื่อหาจุดที่ฝน
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, threshold_val, 255, cv2.THRESH_BINARY_INV)
    
    debug_img = img.copy()
    score = 0
    ans_key = get_answers(ans_input)
    
    # --- 3. ตรวจคะแนนจริง (Core Logic) ---
    # ลูปตรวจทั้ง 5 คอลัมน์ (คอลัมน์ละ 10 ข้อ รวม 50 ข้อ)
    for col in range(5):
        for row in range(10):
            q_num = col * 10 + row
            if q_num >= 50: break
            
            pixel_counts = []
            for choice in range(5): # ก ข ค ง จ
                # คำนวณพิกัด x, y ตามแถบเลื่อน
                cx = start_x + (col * block_space) + (choice * space_x)
                cy = start_y + (row * space_y)
                
                # นับความดำในจุดนั้น
                if 0 <= cy-10 < 1000 and 0 <= cx-10 < 800:
                    roi = thresh[cy-10:cy+10, cx-10:cx+10]
                    pixels = cv2.countNonZero(roi)
                    pixel_counts.append(pixels)
                    # วาดกรอบสีแดงให้ครูเห็นว่า AI มองตรงไหน
                    cv2.rectangle(debug_img, (cx-8, cy-8), (cx+8, cy+8), (255, 0, 0), 2)
                else:
                    pixel_counts.append(0)
            
            # ตรวจคำตอบว่าตรงกับเฉลยไหม
            if pixel_counts and q_num < len(ans_key):
                user_ans = np.argmax(pixel_counts)
                max_pixels = pixel_counts[user_ans]
                
                # ถ้าฝนดำพอสมควร และตอบถูก
                if max_pixels > 20: 
                    if user_ans == ans_key[q_num]:
                        score += 1
                        # วาดสีเขียวทับข้อที่ตอบถูก
                        correct_cx = start_x + (col * block_space) + (user_ans * space_x)
                        correct_cy = start_y + (row * space_y)
                        cv2.circle(debug_img, (correct_cx, correct_cy), 8, (0, 255, 0), -1)

    # --- 4. แสดงผล ---
    st.image(debug_img, caption="จุดสีแดงคือที่ AI มอง (ปรับแถบเลื่อนด้านซ้ายให้กรอบแดงไปทับวงกลมข้อสอบ)")
    st.success(f"🎯 ตรวจเสร็จแล้ว! คะแนนที่ได้: {score} / {len(ans_key)}")
    if score > 0:
        st.balloons()
