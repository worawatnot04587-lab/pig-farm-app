import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="ระบบฟาร์มหมู", layout="centered")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🐷 แอปจัดการฟาร์มหมู")
menu = ["🏠 หน้าหลัก", "🍼 บันทึกแม่พันธุ์", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ"]
choice = st.sidebar.radio("เมนู", menu)

# --- 1. หน้าหลัก ---
if choice == "🏠 หน้าหลัก":
    st.subheader("📊 สรุปภาพรวม")
    st.info("ยินดีต้อนรับ! เมื่อคุณบันทึกข้อมูล ข้อมูลจะมาปรากฏที่นี่")

# --- 2. บันทึกแม่พันธุ์ ---
elif choice == "🍼 บันทึกแม่พันธุ์":
    st.header("🍼 บันทึกการผสมพันธุ์")
    with st.form("sow_form", clear_on_submit=True):
        sow_id = st.text_input("เลขแม่พันธุ์")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค"])
        date_bred = st.date_input("วันที่ผสม", datetime.now())
        due_date = date_bred + timedelta(days=114)
        
        if st.form_submit_button("บันทึก"):
            try:
                df = conn.read(worksheet="Sows")
            except:
                df = pd.DataFrame(columns=["เลขแม่พันธุ์", "สายพันธุ์", "วันที่ผสม", "กำหนดคลอด"])
            
            new_row = pd.DataFrame([{"เลขแม่พันธุ์": sow_id, "สายพันธุ์": breed, "วันที่ผสม": str(date_bred), "กำหนดคลอด": str(due_date)}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sows", data=updated_df)
            st.success(f"บันทึกสำเร็จ! กำหนดคลอดคือ {due_date.strftime('%d/%m/%Y')}")

# --- 3. บันทึกหมูขุน ---
elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 บันทึกการลงหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        pen_id = st.text_input("เลขเล้า/คอก")
        amount = st.number_input("จำนวนหมู", min_value=1)
        date_start = st.date_input("วันที่ลงหมู", datetime.now())
        sell_date = date_start + timedelta(days=120)
        
        if st.form_submit_button("บันทึก"):
            try:
                df = conn.read(worksheet="Fattening")
            except:
                df = pd.DataFrame(columns=["เลขเล้า", "จำนวน", "วันที่ลงหมู", "วันคาดการณ์ขาย"])
            
            new_row = pd.DataFrame([{"เลขเล้า": pen_id, "จำนวน": amount, "วันที่ลงหมู": str(date_start), "วันคาดการณ์ขาย": str(sell_date)}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Fattening", data=updated_df)
            st.success(f"บันทึกสำเร็จ! วันขายประมาณการ {sell_date.strftime('%d/%m/%Y')}")

# --- 4. ขายน้ำเชื้อ ---
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 บันทึกการขายน้ำเชื้อ")
    with st.form("semen_form", clear_on_submit=True):
        customer = st.text_input("ชื่อลูกค้า")
        price = st.number_input("ราคารวม", min_value=0)
        date_sale = st.date_input("วันที่ขาย", datetime.now())
        follow_up = date_sale + timedelta(days=21)
        
        if st.form_submit_button("บันทึก"):
            try:
                df = conn.read(worksheet="Semen_Sales")
            except:
                df = pd.DataFrame(columns=["ลูกค้า", "ราคา", "วันที่ขาย", "วันตามงาน"])
            
            new_row = pd.DataFrame([{"ลูกค้า": customer, "ราคา": price, "วันที่ขาย": str(date_sale), "วันตามงาน": str(follow_up)}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Semen_Sales", data=updated_df)
            st.success(f"บันทึกสำเร็จ! วันตามงานคือ {follow_up.strftime('%d/%m/%Y')}")
