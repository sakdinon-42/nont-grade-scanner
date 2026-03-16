import cv2
import numpy as np

def detect_bubbles(image_path):
    # 1. โหลดภาพและแปลงเป็นขาวดำเพื่อลด Noise
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    # 2. หาเส้นขอบ (Contours) ทั้งหมดในภาพ
    cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    question_cnts = []
    
    # 3. คัดกรองเอาเฉพาะเส้นขอบที่เป็น "วงกลม" (ช่องฝนข้อสอบ)
    for c in cnts:
        # คำนวณกรอบสี่เหลี่ยมที่ล้อมรอบเส้นขอบนั้น
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        
        # ตรวจสอบขนาด: กว้าง/สูง ต้องพอดี และอัตราส่วนใกล้เคียง 1 (เพื่อยืนยันว่าเป็นวงกลม ไม่ใช่เส้นตรงหรือตัวหนังสือ)
        if w >= 20 and h >= 20 and ar >= 0.9 and ar <= 1.1:
            question_cnts.append(c)

    # 4. วาดวงกลมสีเขียวทับจุดที่ AI หาเจอ (เพื่อ Debug)
    debug_img = img.copy()
    cv2.drawContours(debug_img, question_cnts, -1, (0, 255, 0), 2)
    
    return debug_img, question_cnts
