import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมูครบวงจร", layout="wide")

# --- ส่วนจัดการฐานข้อมูลชั่วคราว ---
if 'sow_db' not in st.session_state:
    st.session_state.sow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "สายพันธุ์", "ที่มา(พ่อ/แม่)", "วันที่ผสม", "กำหนดคลอด"])

if 'farrow_db' not in st.session_state:
    st.session_state.farrow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "วันที่คลอดจริง", "ลูกรอด(ตัว)", "ลูกตาย(ตัว)", "หมายเหตุ"])

if 'fat_db' not in st.session_state:
    st.session_state.fat_db = pd.DataFrame(columns=["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])

if 'semen_db' not in st.session_state:
    st.session_state.semen_db = pd.DataFrame(columns=["วันที่", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

# --- เมนูหลัก ---
st.title("🐷 ระบบจัดการฟาร์มหมู (Full Flow)")
menu = ["🏠 หน้าหลัก", "🍼 บันทึกผสม", "👶 บันทึกคลอด", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ จัดการข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 1. หน้าหลัก ---
if choice == "🏠 หน้าหลัก":
    st.subheader("📊 สรุปสถิติฟาร์ม")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("แม่พันธุ์ทั้งหมด", f"{len(st.session_state.sow_db['เลขแม่พันธุ์'].unique())} ตัว")
    c2.metric("จำนวนการคลอด", f"{len(st.session_state.farrow_db)} ครั้ง")
    c3.metric("รายได้หมูขุน", f"{st.session_state.fat_db['รายได้'].sum():,.0f} ฿")
    c4.metric("รายได้น้ำเชื้อ", f"{st.session_state.semen_db['ราคา'].sum():,.0f} ฿")
    
    st.divider()
    if not st.session_state.farrow_db.empty:
        fig = px.bar(st.session_state.farrow_db, x="เลขแม่พันธุ์", y="ลูกรอด(ตัว)", title="จำนวนลูกหมูรอดตายแยกตามแม่", color="เลขแม่พันธุ์")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. บันทึกผสม ---
elif choice == "🍼 บันทึกผสม":
    st.header("🍼 บันทึกการผสมพันธุ์")
    existing_sows = st.session_state.sow_db["เลขแม่พันธุ์"].unique().tolist()
    mode = st.radio("โหมด:", ["แม่เดิม", "เพิ่มแม่ใหม่"], horizontal=True)
    
    with st.form("mix_form", clear_on_submit=True):
        if mode == "แม่เดิม" and existing_sows:
            s_id = st.selectbox("เลือกเลขแม่พันธุ์", existing_sows)
            breed = st.session_state.sow_db[st.session_state.sow_db["เลขแม่พันธุ์"] == s_id]["สายพันธุ์"].iloc[0]
            origin = st.session_state.sow_db[st.session_state.sow_db["เลขแม่พันธุ์"] == s_id]["ที่มา(พ่อ/แม่)"].iloc[0]
        else:
            s_id = st.text_input("เลขแม่พันธุ์ใหม่")
            breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
            origin = st.text_input("ที่มา (พ่อ/แม่)")
            
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)
        st.info(f"📅 กำหนดคลอดคาดการณ์: {d_due.strftime('%d/%m/%Y')}")

        if st.form_submit_button("บันทึกการผสม"):
            new_data = pd.DataFrame([[s_id, breed, origin, str(d_mix), str(d_due)]], columns=st.session_state.sow_db.columns)
            st.session_state.sow_db = pd.concat([st.session_state.sow_db, new_data], ignore_index=True)
            st.success("บันทึกข้อมูลสำเร็จ!")

# --- 3. บันทึกคลอด ---
elif choice == "👶 บันทึกคลอด":
    st.header("👶 บันทึกการคลอดลูกหมู")
    # ดึงเฉพาะแม่ที่เคยบันทึกผสมไว้
    sow_in_system = st.session_state.sow_db["เลขแม่พันธุ์"].unique().tolist()
    
    if not sow_in_system:
        st.warning("กรุณาไปบันทึกข้อมูลการผสมพันธุ์ก่อนครับ")
    else:
        with st.form("farrow_form", clear_on_submit=True):
            s_id = st.selectbox("เลือกแม่พันธุ์ที่คลอด", sow_in_system)
            # โชว์วันกำหนดคลอดที่เคยบันทึกไว้
            due_info = st.session_state.sow_db[st.session_state.sow_db["เลขแม่พันธุ์"] == s_id]["กำหนดคลอด"].iloc[-1]
            st.info(f"📅 วันกำหนดคลอดตามแผนคือ: {due_info}")
            
            col1, col2 = st.columns(2)
            d_real = col1.date_input("วันที่คลอดจริง", datetime.now())
            alive = col2.number_input("จำนวนลูกที่รอด (ตัว)", min_value=0, step=1)
            dead = col1.number_input("จำนวนลูกที่ตาย (ตัว)", min_value=0, step=1)
            note = st.text_area("หมายเหตุ/สุขภาพแม่หลังคลอด")
            
            if st.form_submit_button("บันทึกการคลอด"):
                new_farrow = pd.DataFrame([[s_id, str(d_real), alive, dead, note]], columns=st.session_state.farrow_db.columns)
                st.session_state.farrow_db = pd.concat([st.session_state.farrow_db, new_farrow], ignore_index=True)
                st.success(f"บันทึกการคลอดแม่ {s_id} เรียบร้อย! ยินดีด้วยกับสมาชิกใหม่ {alive} ตัว")

# --- 4. บันทึกหมูขุน --- (คงเดิมตามภาพ 08c940)
elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 บันทึกการลงหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า/คอก")
        stat = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวนหมู (ตัว)", min_value=1)
        wet = st.number_input("น้ำหนักรวม (กก.)", min_value=0.0)
        pri = st.number_input("รายได้ (บาท)", min_value=0.0)
        dt = st.date_input("วันที่ทำรายการ")
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[p_id, stat, amt, str(dt), wet, pri]], columns=st.session_state.fat_db.columns)
            st.session_state.fat_db = pd.concat([st.session_state.fat_db, new_data], ignore_index=True)
            st.success("บันทึกสำเร็จ")

# --- 5. ขายน้ำเชื้อ --- (คงเดิมตามภาพ 08cd7e แต่เพิ่มจำนวนโดส)
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 บันทึกการขายน้ำเชื้อ")
    with st.form("semen_form", clear_on_submit=True):
        cust = st.text_input("ชื่อลูกค้า")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        dose = st.number_input("จำนวนโดส", min_value=1)
        price = st.number_input("ราคารวม (บาท)", min_value=0)
        dt_s = st.date_input("วันที่ขาย")
        dt_f = dt_s + timedelta(days=21)
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[str(dt_s), cust, breed, dose, price, str(dt_f)]], columns=st.session_state.semen_db.columns)
            st.session_state.semen_db = pd.concat([st.session_state.semen_db, new_data], ignore_index=True)
            st.success("บันทึกยอดขายสำเร็จ")

# --- 6. จัดการข้อมูล ---
elif choice == "🗑️ จัดการข้อมูล":
    st.header("🗑️ ข้อมูลทั้งหมดในระบบ")
    target = st.selectbox("เลือกดูข้อมูล", ["ประวัติผสม", "ประวัติคลอด", "ประวัติหมูขุน", "ประวัติขายน้ำเชื้อ"])
    
    if target == "ประวัติผสม": st.dataframe(st.session_state.sow_db, use_container_width=True)
    if target == "ประวัติคลอด": st.dataframe(st.session_state.farrow_db, use_container_width=True)
    if target == "ประวัติหมูขุน": st.dataframe(st.session_state.fat_db, use_container_width=True)
    if target == "ประวัติขายน้ำเชื้อ": st.dataframe(st.session_state.semen_db, use_container_width=True)
    
    if st.button(f"ล้างข้อมูล{target}ทั้งหมด"):
        if target == "ประวัติผสม": st.session_state.sow_db = pd.DataFrame(columns=st.session_state.sow_db.columns)
        if target == "ประวัติคลอด": st.session_state.farrow_db = pd.DataFrame(columns=st.session_state.farrow_db.columns)
        if target == "ประวัติหมูขุน": st.session_state.fat_db = pd.DataFrame(columns=st.session_state.fat_db.columns)
        if target == "ประวัติขายน้ำเชื้อ": st.session_state.semen_db = pd.DataFrame(columns=st.session_state.semen_db.columns)
        st.rerun()
