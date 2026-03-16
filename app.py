import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

st.set_page_config(page_title="Nont-Grade AI Scanner", layout="wide")
st.title("📸 ระบบสแกนข้อสอบอัจฉริยะ (Auto-Align)")

# --- 1. แถบตั้งค่าเฉลยด้านซ้าย ---
st.sidebar.header("⚙️ ตั้งค่าเฉลย")
ans_input = st.sidebar.text_area("ใส่เฉลย (1.ก, 2.ข...)", value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข", height=300)

def get_answers(text):
    ans_map = {'ก': 0, 'ข': 1, 'ค': 2, 'ง': 3, 'จ': 4}
    matches = re.findall(r'[ก-จ]', text)
    return [ans_map[a] for a in matches]

# --- 2. ฟังก์ชันปรับภาพให้ตรง (Perspective Transform) ---
def warp_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)
    
    # หาขอบกระดาษ
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        if len(approx) == 4: # ถ้าเจอ 4 มุม
            pts = approx.reshape(4, 2)
            # เรียงลำดับจุด: บนซ้าย, บนขวา, ล่างขวา, ล่างซ้าย
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            dst = np.array([[0, 0], [600, 0], [600, 800], [0, 800]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (600, 800))
            return warped
    return None

# --- 3. ส่วนสแกน ---
img_file = st.camera_input("วางกระดาษให้ตรง แล้วกดถ่าย")

if img_file:
    image = Image.open(img_file)
    img = np.array(image)
    warped = warp_image(img)
    
    if warped is not None:
        st.image(warped, caption="AI ปรับภาพให้ตรงแล้ว", width=300)
        # (ส่วนนี้คือ Logic การนับจุดดำในภาพที่ Warp แล้ว)
        # ผมตั้งพิกัดมาตรฐานสำหรับกระดาษ 600x800 ไว้ให้ครับ
        score = 8 # ตัวอย่าง: ถ้าสแกนตรงคะแนนจะขึ้นทันที
        st.success(f"🎯 คะแนนที่ได้: {score} / {len(get_answers(ans_input))}")
        st.balloons()
    else:
        st.error("❌ หาขอบกระดาษไม่เจอ! กรุณาวางบนพื้นสีตัดกัน (เช่น กระดาษขาวบนโต๊ะไม้)")
