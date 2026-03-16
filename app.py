import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

# --- ตั้งค่าหน้าเว็บและ CSS เพื่อขยายกล้อง ---
st.set_page_config(page_title="Nont-Grade AI Pro", layout="wide")
st.markdown("""<style>div[data-testid="stCameraInput"] { width: 100% !important; }</style>""", unsafe_allow_html=True)

st.title("📸 ระบบสแกนข้อสอบอัจฉริยะครูนนท์ V2 (Auto-Align)")

# --- 1. แถบควบคุมด้านซ้ายสำหรับแก้เฉลย ---
st.sidebar.header("⚙️ ตั้งค่าเฉลย")
ans_input = st.sidebar.text_area(
    "ใส่เฉลยของคุณครู (เช่น 1.ก, 2.ข, 3.ค)", 
    value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข", 
    height=300
)

def get_answers(text):
    # ฟังก์ชันดึงเฉพาะตัว ก-จ ที่อยู่หลังจุด
    ans_map = {'ก': 0, 'ข': 1, 'ค': 2, 'ง': 3, 'จ': 4}
    matches = re.findall(r'[ก-จ]', text)
    return [ans_map[a] for a in matches]

# --- 2. ระบบ AI สำหรับดัดภาพให้ตรง (Perspective Transform Engine) ---
def warp_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)
    
    # หาขอบกระดาษสี่เหลี่ยมที่ใหญ่ที่สุด
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) > 0:
        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        
        # ถ้าเจอ 4 มุมของกระดาษ
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            # เรียงลำดับจุด: บนซ้าย, บนขวา, ล่างขวา, ล่างซ้าย
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            
            # ดัดภาพให้กลายเป็นสี่เหลี่ยมขนาดมาตรฐาน 600x800
            dst = np.array([[0, 0], [600, 0], [600, 800], [0, 800]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warped = cv2.warpPerspective(img, M, (600, 800))
            return warped
    return None

# --- 3. ส่วนหลักของการทำงานหน้าเว็บ ---
img_file = st.camera_input("วางกระดาษคำตอบให้เห็นครบทั้ง 4 มุม แล้วกดถ่าย")

if img_file:
    image = Image.open(img_file)
    img = np.array(image)
    
    # ดัดภาพให้ตรงอัตโนมัติ
    with st.spinner('กำลังปรับภาพและตรวจคะแนน...'):
        warped = warp_image(img)
        
        if warped is not None:
            # โชว์ภาพที่ดัดแล้วให้ครูเห็น
            st.image(warped, caption="AI ปรับภาพให้ตรงเรียบร้อยแล้ว", width=300)
            
            # --- 4. โครงสร้างหลักของการตรวจคะแนนจริง (CORE LOGIC) ---
            # ... ส่วนนี้คุณครูต้องนำพิกัดพิกเซลของข้อสอบ ม.1-ม.6 มาใส่ ...
            
            current_key = get_answers(ans_input)
            final_score = 0 # ตัวอย่างคะแนนที่คุณครูต้องใช้ OpenCV คำนวณจริง
            
            # ตัวอย่างเอฟเฟกต์เฉลิมฉลอง
            st.success(f"🎯 ตรวจเสร็จแล้ว! คะแนนที่ได้: {final_score} / {len(current_key)}")
            st.balloons()
            
        else:
            # กรณีที่ AI หาขอบกระดาษไม่เจอ
            st.error("❌ หาขอบกระดาษไม่เจอ! กรุณาวางบนพื้นสีตัดกัน (เช่น กระดาษขาวบนโต๊ะไม้) และถือให้เห็นครบทั้ง 4 มุมครับ")
