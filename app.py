import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. ตั้งค่าหน้าแอปให้ดูดีบนมือถือ ---
st.set_page_config(page_title="PigFarm Pro", layout="centered")

# --- 2. ฟังก์ชันเตรียมฐานข้อมูลชั่วคราว ---
def init_data():
    if 'sow_loop' not in st.session_state:
        st.session_state.sow_loop = pd.DataFrame(columns=["เลขแม่", "สถานะ", "วันผสม", "เช็คสัด21วัน", "บำรุง84วัน", "ย้ายกรง107วัน", "กำหนดคลอด"])
    if 'fat_pens' not in st.session_state:
        st.session_state.fat_pens = pd.DataFrame(columns=["เลขเล้า", "จำนวน", "วันลงหมู", "กำหนดขาย(คาดการณ์)", "ตาย/คัดทิ้ง"])
    if 'semen_sales' not in st.session_state:
        st.session_state.semen_sales = pd.DataFrame(columns=["วันที่", "ลูกค้า", "โดส", "ราคา", "วันกลับสัด(แจ้งลูกค้า)"])

init_data()

# --- 3. แถบเมนูหลัก (เน้นกดง่ายบนมือถือ) ---
st.title("🐷 Pig Farm Pro")
tab1, tab2, tab3, tab4 = st.tabs(["🏠 หน้าหลัก", "🍼 แม่พันธุ์", "📦 หมูขุน", "🧪 น้ำเชื้อ"])

# --- [หน้าหลัก: Daily Tasks & Stats] ---
with tab1:
    st.subheader("📊 สรุปฟาร์มวันนี้")
    today = datetime.now().date()
    
    # คำนวณรายได้ (ตัวอย่าง)
    total_semen = st.session_state.semen_sales['ราคา'].sum()
    st.metric("ยอดขายน้ำเชื้อรวม", f"{total_semen:,.0f} ฿")
    
    st.divider()
    st.subheader("🔔 กิจกรรมที่ต้องทำ (วันนี้/พรุ่งนี้)")
    
    # ระบบค้นหางานด่วนจากตารางแม่พันธุ์
    tasks = []
    for _, row in st.session_state.sow_loop.iterrows():
        d_check = datetime.strptime(row['เช็คสัด21วัน'], '%Y-%m-%d').date()
        d_due = datetime.strptime(row['กำหนดคลอด'], '%Y-%m-%d').date()
        
        if d_check == today: tasks.append(f"🟡 เช็คสัด: แม่ {row['เลขแม่']}")
        if d_due == today: tasks.append(f"🟢 กำหนดคลอด: แม่ {row['เลขแม่']}")
        if d_due == today + timedelta(days=1): tasks.append(f"🔴 พรุ่งนี้คลอด: แม่ {row['เลขแม่']}")
    
    if tasks:
        for t in tasks: st.warning(t)
    else:
        st.info("✅ วันนี้ไม่มีงานด่วน")

# --- [หมวดแม่พันธุ์: Loop ผสม-คลอด] ---
with tab2:
    st.subheader("🍼 ระบบวงรอบแม่พันธุ์")
    
    with st.expander("➕ บันทึกการผสมพันธุ์ใหม่", expanded=True):
        with st.form("mix_form", clear_on_submit=True):
            s_id = st.text_input("เลขแม่พันธุ์ / สแกนคอก")
            d_mix = st.date_input("วันที่ผสม", today)
            
            if st.form_submit_button("บันทึกและคำนวณรอบ"):
                # คำนวณวันตามสูตรที่คุณให้มา
                c21 = d_mix + timedelta(days=21)
                f84 = d_mix + timedelta(days=84)
                m107 = d_mix + timedelta(days=107)
                d114 = d_mix + timedelta(days=114)
                
                new_data = pd.DataFrame([[s_id, "ผสมแล้ว", str(d_mix), str(c21), str(f84), str(m107), str(d114)]], 
                                         columns=st.session_state.sow_loop.columns)
                st.session_state.sow_loop = pd.concat([st.session_state.sow_loop, new_data], ignore_index=True)
                st.success(f"บันทึกแม่ {s_id} สำเร็จ! กำหนดคลอด {d114}")

    st.write("📋 สถานะแม่พันธุ์ปัจจุบัน")
    st.dataframe(st.session_state.sow_loop, use_container_width=True)

# --- [หมวดหมูขุน: Pen Tracking] ---
with tab3:
    st.subheader("📦 จัดการเล้าหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า")
        f_amt = st.number_input("จำนวนหมู (ตัว)", min_value=1)
        f_date = st.date_input("วันที่ลงหมู", today)
        f_sell = f_date + timedelta(days=120) # คาดการณ์ขายใน 120 วัน
        
        if st.form_submit_button("เปิดเล้า"):
            new_fat = pd.DataFrame([[p_id, f_amt, str(f_date), str(f_sell), 0]], 
                                    columns=st.session_state.fat_pens.columns)
            st.session_state.fat_pens = pd.concat([st.session_state.fat_pens, new_fat], ignore_index=True)
            st.success(f"ลงหมูเล้า {p_id} แล้ว (กำหนดขายประมาณ {f_sell})")
    
    st.write("📋 รายการเล้าที่เลี้ยงอยู่")
    st.table(st.session_state.fat_pens)

# --- [หมวดน้ำเชื้อ: Semen Sales] ---
with tab4:
    st.subheader("🧪 บันทึกขายน้ำเชื้อ")
    with st.form("semen_form", clear_on_submit=True):
        c_name = st.text_input("ชื่อลูกค้า")
        s_dose = st.number_input("จำนวนโดส", min_value=1)
        s_price = st.number_input("ราคารวม", min_value=0)
        s_date = st.date_input("วันที่ขาย", today)
        s_follow = s_date + timedelta(days=21) # วันตามงาน
        
        if st.form_submit_button("บันทึกการขาย"):
            new_semen = pd.DataFrame([[str(s_date), c_name, s_dose, s_price, str(s_follow)]], 
                                      columns=st.session_state.semen_sales.columns)
            st.session_state.semen_sales = pd.concat([st.session_state.semen_sales, new_semen], ignore_index=True)
            st.success("บันทึกเรียบร้อย! ระบบจะเตือนให้ตามงานในหน้าแรก")

    st.write("📋 ประวัติการขาย")
    st.dataframe(st.session_state.semen_sales, use_container_width=True)
