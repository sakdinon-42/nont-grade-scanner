import streamlit as st
import cv2
import numpy as np
from PIL import Image
import re

# ตั้งค่าหน้าเว็บให้แสดงผลเต็มจอ
st.set_page_config(page_title="Nont-Grade 9:16 Pro", layout="centered")

# --- 🛠️ ส่วนของ CSS ปรับกล้อง 9:16 และกรอบเล็ง ---
st.markdown("""
    <style>
    /* บังคับช่องกล้องให้เป็น 9:16 */
    div[data-testid="stCameraInput"] {
        width: 100% !important;
        max-width: 500px; /* จำกัดความกว้างให้ดูสวยในคอม */
        margin: 0 auto;
        aspect-ratio: 9 / 16; /* ขนาดมาตรฐานมือถือ */
        position: relative;
        overflow: hidden;
        border-radius: 15px;
        border: 2px solid #333;
    }
    
    /* กรอบ Container ของจุดเล็ง */
    .overlay {
        position: absolute;
        top: 10%; left: 10%;
        width: 80%; height: 80%;
        pointer-events: none;
        z-index: 100;
    }
    
    /* สไตล์จุดเล็งสี่เหลี่ยมสีเขียว */
    .guide-box {
        position: absolute;
        width: 40px; height: 40px;
        border: 4px solid #00FF00;
        box-shadow: 0 0 15px #00FF00;
        border-radius: 5px;
    }
    
    /* พิกัด 6 จุดอ้างอิงตามกระดาษ */
    .tl { top: 0; left: 0; }           /* บนซ้าย */
    .tr { top: 0; right: 0; }          /* บนขวา */
    .ml { top: 48%; left: 0; }         /* กลางซ้าย */
    .mr { top: 48%; right: 0; }        /* กลางขวา */
    .bl { bottom: 0; left: 0; }        /* ล่างซ้าย */
    .br { bottom: 0; right: 0; }       /* ล่างขวา */
    </style>
    
    <div class="overlay">
        <div class="guide-box tl"></div>
        <div class="guide-box tr"></div>
        <div class="guide-box ml"></div>
        <div class="guide-box mr"></div>
        <div class="guide-box bl"></div>
        <div class="guide-box br"></div>
    </div>
    """, unsafe_allow_html=True)

st.title("📸 Nont-Grade Scanner (9:16)")
st.write("เล็งจุดสีเขียวให้ทับสี่เหลี่ยมสีดำบนกระดาษทั้ง 6 จุด")

# --- แถบแก้ไขเฉลย (Sidebar) ---
st.sidebar.header("⚙️ ตั้งค่าเฉลย")
ans_input = st.sidebar.text_area("เฉลย (1.ก, 2.ข...)", value="1.ข, 2.ก, 3.ข, 4.ข, 5.ข", height=300)

# --- ส่วนรับภาพ ---
img_file = st.camera_input("กดถ่ายเมื่อจุดเขียวทับจุดดำบนกระดาษแล้ว")

if img_file:
    st.balloons()
    st.success("สแกนสำเร็จ! ระบบกำลังประมวลผล...")
