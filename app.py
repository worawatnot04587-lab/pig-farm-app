import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. ตั้งค่าหน้าแอป ---
st.set_page_config(page_title="PigFarm Pro V3.1", layout="centered")

# --- 2. ฟังก์ชันเตรียมฐานข้อมูล (Session State) ---
def init_data():
    if 'sow_loop' not in st.session_state:
        st.session_state.sow_loop = pd.DataFrame(columns=["เลขแม่", "สถานะ", "วันผสม", "เช็คสัด21วัน", "บำรุง84วัน", "ย้ายกรง107วัน", "กำหนดคลอด"])
    if 'fat_pens' not in st.session_state:
        # ปรับชื่อคอลัมน์ให้ตรงกับตอนคำนวณยอดขาย
        st.session_state.fat_pens = pd.DataFrame(columns=["เลขเล้า", "จำนวน", "วันลงหมู", "กำหนดขาย", "รายได้"])
    if 'semen_sales' not in st.session_state:
        # ปรับชื่อคอลัมน์ให้ตรงกับตอนคำนวณยอดขาย
        st.session_state.semen_sales = pd.DataFrame(columns=["วันที่", "ลูกค้า", "โดส", "ราคา", "วันตามงาน"])

init_data()

# --- 3. แถบเมนูหลัก ---
st.title("🐷 Pig Farm Pro")
tab1, tab2, tab3, tab4 = st.tabs(["🏠 หน้าหลัก", "🍼 แม่พันธุ์", "📦 หมูขุน", "🧪 น้ำเชื้อ"])

# --- [หน้าหลัก: Dashboard] ---
with tab1:
    st.subheader("📊 สรุปยอดขายฟาร์ม")
    
    # แก้ไข Logic การบวกยอดขาย (Conversion เป็นตัวเลขก่อนบวก)
    income_fat = pd.to_numeric(st.session_state.fat_pens['รายได้'], errors='coerce').sum()
    income_semen = pd.to_numeric(st.session_state.semen_sales['ราคา'], errors='coerce').sum()
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("ยอดขายหมูขุนรวม", f"{income_fat:,.0f} ฿")
    with c2:
        st.metric("ยอดขายน้ำเชื้อรวม", f"{income_semen:,.0f} ฿")
    
    st.divider()
    st.subheader("🔔 งานด่วนวันนี้")
    today = datetime.now().date()
    tasks = []
    for _, row in st.session_state.sow_loop.iterrows():
        if row['เช็คสัด21วัน'] == str(today): tasks.append(f"🟡 เช็คสัด: แม่ {row['เลขแม่']}")
        if row['กำหนดคลอด'] == str(today): tasks.append(f"🟢 กำหนดคลอด: แม่ {row['เลขแม่']}")
    
    if tasks:
        for t in tasks: st.warning(t)
    else:
        st.info("✅ ไม่มีงานด่วน")

# --- [หมวดแม่พันธุ์] ---
with tab2:
    st.subheader("🍼 ผสมพันธุ์")
    with st.form("mix_form", clear_on_submit=True):
        s_id = st.text_input("เลขแม่พันธุ์")
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        if st.form_submit_button("บันทึก"):
            c21, f84, m107, d114 = d_mix+timedelta(21), d_mix+timedelta(84), d_mix+timedelta(107), d_mix+timedelta(114)
            new_sow = pd.DataFrame([[s_id, "ผสมแล้ว", str(d_mix), str(c21), str(f84), str(m107), str(d114)]], columns=st.session_state.sow_loop.columns)
            st.session_state.sow_loop = pd.concat([st.session_state.sow_loop, new_sow], ignore_index=True)
            st.success("บันทึกสำเร็จ")
    st.dataframe(st.session_state.sow_loop)

# --- [หมวดหมูขุน] ---
with tab3:
    st
