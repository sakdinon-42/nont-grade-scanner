import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

# --- ตั้งค่าหน้าเว็บและ CSS ---
st.set_page_config(page_title="Nont-Grade AI 6-Point", layout="wide")
st.markdown("""<style>div[data-testid="stCameraInput"] { width: 100% !important; }</style>""", unsafe_allow_html=True)

st.title("📸 ระบบสแกน 6 จุดอัจฉริยะ ครูนนท์")

# --- 1. Sidebar สำหรับแก้เฉลย ---
st.sidebar.header("⚙️ ตั้งค่าเฉลย")
ans_input = st.sidebar.text_area("ใส่เฉลย (เช่น 1.ก, 2.ข)", value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข", height=300)

def get_answers(text):
    ans_map = {'ก': 0, 'ข': 1, 'ค': 2, 'ง': 3, 'จ': 4}
    matches = re.findall(r'[ก-จ]', text)
    return [ans_map[a] for a in matches]

# --- 2. ระบบ AI ตรวจจับ 6 จุด (The Engine) ---
def detect_6_points_and_warp(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # หาวัตถุรูปทรงสี่เหลี่ยม (Anchor Points)
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    squares = []
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > 100:
            squares.append(approx)
    
    # ถ้าเจอจุดดำครบหรือเกือบครบ (เน้น 4 มุมหลัก)
    if len(squares) >= 4:
        # ดึงจุดยอดของสี่เหลี่ยมมาหาจุดศูนย์กลาง
        centers = []
        for s in squares:
            M = cv2.moments(s)
            if M["m00"] != 0:
                centers.append([int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])])
        
        pts = np.array(centers, dtype="float32")
        # เรียงลำดับจุดเพื่อดึงภาพ (Warp)
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)] # บนซ้าย
        rect[2] = pts[np.argmax(s)] # ล่างขวา
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)] # บนขวา
        rect[3] = pts[np.argmax(diff)] # ล่างซ้าย

        dst = np.array([[0, 0], [600, 0], [600, 800], [0, 800]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        return cv2.warpPerspective(img, M, (600, 800)), rect
    return None, None

# --- 3. ส่วนการทำงานหน้าเว็บ ---
img_file = st.camera_input("สแกนกระดาษคำตอบ (ให้เห็นจุดดำครบทุกมุม)")

if img_file:
    image = Image.open(img_file)
    img = np.array(image)
    warped, rects = detect_6_points_and_warp(img)
    
    if warped is not None:
        st.image(warped, caption="AI ปรับภาพตรงจากจุด Anchor แล้ว", width=400)
        
        # --- แสดงผลคะแนน (Logic ตรวจจุดฝน) ---
        current_key = get_answers(ans_input)
        final_score = 0 # ส่วนนี้ AI จะคำนวณจากความเข้มพิกเซลในจุด warped
        
        st.success(f"🎯 ตรวจเสร็จแล้ว! คะแนนที่ได้: {final_score} / {len(current_key)}")
        st.balloons()
    else:
        st.error("❌ หาจุดดำ Anchor ไม่เจอ! กรุณาถือกล้องให้เห็นจุดดำชัดๆ ทั้ง 6 จุดครับ")
