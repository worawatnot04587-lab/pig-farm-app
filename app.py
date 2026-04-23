import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมู (Local Storage)", layout="wide")

# --- ส่วนจัดการฐานข้อมูลในตัวแอป (Session State) ---
# ระบบจะสร้างตารางเปล่าขึ้นมาถ้าเปิดแอปครั้งแรก
if 'sow_db' not in st.session_state:
    st.session_state.sow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "สายพันธุ์", "พ่อที่มา", "แม่ที่มา", "วันที่ผสม", "กำหนดคลอด"])

if 'fat_db' not in st.session_state:
    st.session_state.fat_db = pd.DataFrame(columns=["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])

if 'semen_db' not in st.session_state:
    st.session_state.semen_db = pd.DataFrame(columns=["วันที่", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

# --- เมนูหลัก ---
st.title("🐷 ระบบจัดการฟาร์มหมู (บันทึกในตัวแอป)")
menu = ["🏠 หน้าหลัก & สถิติ", "🍼 บันทึกแม่พันธุ์", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ จัดการข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 1. หน้าหลัก & สถิติ ---
if choice == "🏠 หน้าหลัก & สถิติ":
    st.subheader("📊 สรุปภาพรวม")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("แม่พันธุ์ทั้งหมด", f"{len(st.session_state.sow_db['เลขแม่พันธุ์'].unique())} ตัว")
    with col2:
        total_fat = st.session_state.fat_db['รายได้'].sum()
        st.metric("รายได้หมูขุน", f"{total_fat:,.2f} ฿")
    with col3:
        total_semen = st.session_state.semen_db['ราคา'].sum()
        st.metric("รายได้น้ำเชื้อ", f"{total_semen:,.2f} ฿")

    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        if not st.session_state.fat_db.empty:
            fig = px.bar(st.session_state.fat_db, x="เลขเล้า", y="จำนวน", color="สถานะ", title="จำนวนหมูขุนรายเล้า")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลกราฟหมูขุน")
            
    with c2:
        if not st.session_state.semen_db.empty:
            fig2 = px.pie(st.session_state.semen_db, values='ราคา', names='สายพันธุ์', title="สัดส่วนรายได้น้ำเชื้อ")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("ยังไม่มีข้อมูลกราฟน้ำเชื้อ")

# --- 2. บันทึกแม่พันธุ์ ---
elif choice == "🍼 บันทึกแม่พันธุ์":
    st.header("🍼 บันทึกแม่พันธุ์")
    
    # ดึงรายชื่อแม่ที่มีอยู่แล้วมาทำ Dropdown
    existing_sows = st.session_state.sow_db["เลขแม่พันธุ์"].unique().tolist()
    
    mode = st.radio("โหมด:", ["บันทึกแม่เดิม (เลือกชื่อ)", "เพิ่มแม่ใหม่ครั้งแรก (ระบุที่มา)"], horizontal=True)
    
    with st.form("sow_form", clear_on_submit=True):
        if mode == "บันทึกแม่เดิม (เลือกชื่อ)" and existing_sows:
            s_id = st.selectbox("เลือกเลขแม่พันธุ์", existing_sows)
            # ดึงสายพันธุ์เดิมมาโชว์
            breed = st.session_state.sow_db[st.session_state.sow_db["เลขแม่พันธุ์"] == s_id]["สายพันธุ์"].iloc[0]
            st.info(f"สายพันธุ์: {breed}")
            f_o, m_o = "-", "-"
        else:
            s_id = st.text_input("ระบุเลขแม่พันธุ์ใหม่")
            breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
            f_o = st.text_input("สายพันธุ์พ่อ (ที่มา)")
            m_o = st.text_input("สายพันธุ์แม่ (ที่มา)")
            
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)
        
        if st.form_submit_button("บันทึกข้อมูล"):
            new_data = pd.DataFrame([[s_id, breed, f_o, m_o, str(d_mix), str(d_due)]], 
                                     columns=st.session_state.sow_db.columns)
            st.session_state.sow_db = pd.concat([st.session_state.sow_db, new_data], ignore_index=True)
            st.success(f"บันทึกข้อมูลแม่ {s_id} เรียบร้อย!")

# --- 3. บันทึกหมูขุน ---
elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 บันทึกหมูขุน")
    
    existing_pens = st.session_state.fat_db["เลขเล้า"].unique().tolist()
    
    with st.form("fat_form", clear_on_submit=True):
        if existing_pens:
            p_id = st.selectbox("เลือกเล้าเดิม หรือระบุใหม่ข้างล่าง", ["เล้าใหม่"] + existing_pens)
            if p_id == "เล้าใหม่":
                p_id = st.text_input("ระบุเลขเล้าใหม่")
        else:
            p_id = st.text_input("ระบุเลขเล้า")
            
        stat = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวนหมู (ตัว)", min_value=0)
        wet = st.number_input("น้ำหนักรวม (กก.)", min_value=0.0)
        pri = st.number_input("รายได้/ราคารวม (บาท)", min_value=0.0)
        dt = st.date_input("วันที่ทำรายการ")
        
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[p_id, stat, amt, str(dt), wet, pri]], 
                                     columns=st.session_state.fat_db.columns)
            st.session_state.fat_db = pd.concat([st.session_state.fat_db, new_data], ignore_index=True)
            st.success("บันทึกข้อมูลหมูขุนแล้ว")

# --- 4. ขายน้ำเชื้อ ---
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 บันทึกการขายน้ำเชื้อ")
    
    with st.form("semen_form", clear_on_submit=True):
        cust = st.text_input("ชื่อลูกค้า")
        breed = st.selectbox("สายพันธุ์น้ำเชื้อ", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        dose = st.number_input("จำนวนโดส", min_value=1)
        price = st.number_input("ราคารวม", min_value=0)
        dt_s = st.date_input("วันที่ขาย")
        dt_f = dt_s + timedelta(days=21)
        
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[str(dt_s), cust, breed, dose, price, str(dt_f)]], 
                                     columns=st.session_state.semen_db.columns)
            st.session_state.semen_db = pd.concat([st.session_state.semen_db, new_data], ignore_index=True)
            st.success("บันทึกยอดขายน้ำเชื้อแล้ว")

# --- 5. จัดการข้อมูล (ดูตาราง/ลบ) ---
elif choice == "🗑️ จัดการข้อมูล":
    st.header("🗑️ จัดการและลบข้อมูล")
    
    tab1, tab2, tab3 = st.tabs(["ประวัติแม่พันธุ์", "ประวัติหมูขุน", "ประวัติขายน้ำเชื้อ"])
    
    with tab1:
        st.dataframe(st.session_state.sow_db, use_container_width=True)
        if st.button("ล้างข้อมูลแม่พันธุ์ทั้งหมด"):
            st.session_state.sow_db = pd.DataFrame(columns=st.session_state.sow_db.columns)
            st.rerun()

    with tab2:
        st.dataframe(st.session_state.fat_db, use_container_width=True)
        if st.button("ล้างข้อมูลหมูขุนทั้งหมด"):
            st.session_state.fat_db = pd.DataFrame(columns=st.session_state.fat_db.columns)
            st.rerun()

    with tab3:
        st.dataframe(st.session_state.semen_db, use_container_width=True)
        if st.button("ล้างข้อมูลน้ำเชื้อทั้งหมด"):
            st.session_state.semen_db = pd.DataFrame(columns=st.session_state.semen_db.columns)
            st.rerun()
