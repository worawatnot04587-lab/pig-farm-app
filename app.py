import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมู V2", layout="wide")

# --- 1. จัดการฐานข้อมูล (Session State) ---
def init_db():
    if 'sow_db' not in st.session_state:
        st.session_state.sow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "สายพันธุ์", "ที่มา", "วันที่ผสม", "กำหนดคลอด"])
    if 'farrow_db' not in st.session_state:
        st.session_state.farrow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "วันที่คลอดจริง", "ลูกรอด", "ลูกตาย", "หมายเหตุ"])
    if 'fat_db' not in st.session_state:
        st.session_state.fat_db = pd.DataFrame(columns=["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])
    if 'semen_db' not in st.session_state:
        st.session_state.semen_db = pd.DataFrame(columns=["วันที่", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

init_db()

# --- 2. เมนูหลัก ---
st.title("🐷 ระบบจัดการฟาร์มหมู (Full Flow)")
menu = ["🏠 หน้าหลัก/สถิติ", "🍼 บันทึกผสม", "👶 บันทึกคลอด", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ จัดการข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 3. ฟังก์ชันการทำงานแต่ละหน้า ---

if choice == "🏠 หน้าหลัก/สถิติ":
    st.subheader("📊 สถิติภาพรวม")
    
    # คำนวณ Metric
    c1, c2, c3, c4 = st.columns(4)
    total_sows = len(st.session_state.sow_db["เลขแม่พันธุ์"].unique())
    total_farrow = len(st.session_state.farrow_db)
    income_fat = st.session_state.fat_db["รายได้"].sum()
    income_semen = st.session_state.semen_db["ราคา"].sum()

    c1.metric("แม่พันธุ์", f"{total_sows} ตัว")
    c2.metric("การคลอด", f"{total_farrow} ครั้ง")
    c3.metric("รายได้หมูขุน", f"{income_fat:,.0f} ฿")
    c4.metric("รายได้น้ำเชื้อ", f"{income_semen:,.0f} ฿")

    st.divider()

    # แสดงกราฟ
    col_a, col_b = st.columns(2)
    with col_a:
        if not st.session_state.farrow_db.empty:
            fig1 = px.bar(st.session_state.farrow_db, x="เลขแม่พันธุ์", y="ลูกรอด", title="จำนวนลูกที่รอดต่อแม่")
            st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        if not st.session_state.fat_db.empty:
            fig2 = px.pie(st.session_state.fat_db, values='จำนวน', names='เลขเล้า', title="สัดส่วนหมูขุนในแต่ละเล้า")
            st.plotly_chart(fig2, use_container_width=True)

elif choice == "🍼 บันทึกผสม":
    st.header("🍼 บันทึกผสมพันธุ์")
    with st.form("mix_form", clear_on_submit=True):
        s_id = st.text_input("เลขแม่พันธุ์")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        origin = st.text_input("ที่มา (พ่อ/แม่)")
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)
        st.info(f"📅 กำหนดคลอด: {d_due.strftime('%d/%m/%Y')}")

        if st.form_submit_button("บันทึก"):
            new_row = pd.DataFrame([[s_id, breed, origin, str(d_mix), str(d_due)]], columns=st.session_state.sow_db.columns)
            st.session_state.sow_db = pd.concat([st.session_state.sow_db, new_row], ignore_index=True)
            st.success("บันทึกข้อมูลเรียบร้อย!")

elif choice == "👶 บันทึกคลอด":
    st.header("👶 บันทึกการคลอด")
    # ดึงรายชื่อแม่พันธุ์จาก sow_db มาโชว์
    sow_list = st.session_state.sow_db["เลขแม่พันธุ์"].unique().tolist()
    
    if not sow_list:
        st.warning("ยังไม่มีข้อมูลแม่พันธุ์ในระบบ กรุณาไปที่เมนู 'บันทึกผสม' ก่อน")
    else:
        with st.form("farrow_form", clear_on_submit=True):
            s_id = st.selectbox("เลือกเลขแม่พันธุ์", sow_list)
            # โชว์วันกำหนดคลอดล่าสุดของแม่ตัวนี้
            due_date = st.session_state.sow_db[st.session_state.sow_db["เลขแม่พันธุ์"] == s_id]["กำหนดคลอด"].iloc[-1]
            st.info(f"วันกำหนดคลอดตามแผน: {due_date}")
            
            d_real = st.date_input("วันที่คลอดจริง", datetime.now())
            alive = st.number_input("ลูกที่รอด (ตัว)", min_value=0)
            dead = st.number_input("ลูกที่ตาย (ตัว)", min_value=0)
            note = st.text_input("หมายเหตุ")
            
            if st.form_submit_button("บันทึกการคลอด"):
                new_farrow = pd.DataFrame([[s_id, str(d_real), alive, dead, note]], columns=st.session_state.farrow_db.columns)
                st.session_state.farrow_db = pd.concat([st.session_state.farrow_db, new_farrow], ignore_index=True)
                st.success("อัปเดตสถานะการคลอดสำเร็จ!")

elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 บันทึกหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า")
        stat = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวน", min_value=1)
        wet = st.number_input("น้ำหนักรวม (กก.)", min_value=0.0)
        pri = st.number_input("รายได้ (บาท)", min_value=0.0)
        dt = st.date_input("วันที่")
        if st.form_submit_button("บันทึก"):
            new_fat = pd.DataFrame([[p_id, stat, amt, str(dt), wet, pri]], columns=st.session_state.fat_db.columns)
            st.session_state.fat_db = pd.concat([st.session_state.fat_db, new_fat], ignore_index=True)
            st.success("บันทึกสำเร็จ")

elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 ขายน้ำเชื้อ")
    with st.form("semen_form", clear_on_submit=True):
        cust = st.text_input("ชื่อลูกค้า")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        dose = st.number_input("จำนวนโดส", min_value=1)
        price = st.number_input("ราคา", min_value=0)
        dt = st.date_input("วันที่ขาย")
        if st.form_submit_button("บันทึก"):
            new_semen = pd.DataFrame([[str(dt), cust, breed, dose, price, str(dt + timedelta(days=21))]], columns=st.session_state.semen_db.columns)
            st.session_state.semen_db = pd.concat([st.session_state.semen_db, new_semen], ignore_index=True)
            st.success("บันทึกสำเร็จ")

elif choice == "🗑️ จัดการข้อมูล":
    st.header("🗑️ ลบข้อมูล/ดูตาราง")
    target = st.radio("เลือกตาราง", ["แม่พันธุ์", "การคลอด", "หมูขุน", "น้ำเชื้อ"], horizontal=True)
    
    if target == "แม่พันธุ์": df = st.session_state.sow_db
    elif target == "การคลอด": df = st.session_state.farrow_db
    elif target == "หมูขุน": df = st.session_state.fat_db
    else: df = st.session_state.semen_db
    
    st.dataframe(df, use_container_width=True)
    if st.button("ล้างข้อมูลหมวดนี้ทั้งหมด"):
        if target == "แม่พันธุ์": st.session_state.sow_db = pd.DataFrame(columns=st.session_state.sow_db.columns)
        elif target == "การคลอด": st.session_state.farrow_db = pd.DataFrame(columns=st.session_state.farrow_db.columns)
        elif target == "หมูขุน": st.session_state.fat_db = pd.DataFrame(columns=st.session_state.fat_db.columns)
        else: st.session_state.semen_db = pd.DataFrame(columns=st.session_state.semen_db.columns)
        st.rerun()
