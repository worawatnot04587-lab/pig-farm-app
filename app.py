import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมู V.เสถียร", layout="wide")

# เชื่อมต่อกับ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ฟังก์ชันดึงข้อมูลแบบปลอดภัย ---
def get_safe_data(worksheet_name, expected_cols):
    try:
        df = conn.read(worksheet=worksheet_name, ttl="0")
        if df.empty or len(df.columns) < len(expected_cols):
            return pd.DataFrame(columns=expected_cols)
        return df
    except:
        return pd.DataFrame(columns=expected_cols)

st.title("🐷 ระบบจัดการฟาร์มหมู (Fixed Version)")
menu = ["🏠 หน้าหลัก", "🍼 แม่พันธุ์", "📦 หมูขุน", "🧪 น้ำเชื้อ", "🗑️ ลบข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 1. หน้าหลัก ---
if choice == "🏠 หน้าหลัก":
    st.subheader("📊 สถิติภาพรวม")
    df_sows = get_safe_data("Sows", ["เลขแม่พันธุ์", "สายพันธุ์", "พ่อที่มา", "แม่ที่มา", "วันที่ผสม", "กำหนดคลอด"])
    df_fat = get_safe_data("Fattening", ["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])
    df_semen = get_safe_data("Semen_Sales", ["วันที่", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

    col1, col2, col3 = st.columns(3)
    col1.metric("แม่พันธุ์ทั้งหมด", f"{len(df_sows['เลขแม่พันธุ์'].unique()) if not df_sows.empty else 0} ตัว")
    col2.metric("รายได้หมูขุน", f"{df_fat['รายได้'].sum() if not df_fat.empty else 0:,.0f} ฿")
    col3.metric("รายได้น้ำเชื้อ", f"{df_semen['ราคา'].sum() if not df_semen.empty else 0:,.0f} ฿")

    if not df_fat.empty:
        fig = px.bar(df_fat, x="เลขเล้า", y="จำนวน", color="สถานะ", title="จำนวนหมูในแต่ละเล้า")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. บันทึกแม่พันธุ์ ---
elif choice == "🍼 แม่พันธุ์":
    st.header("🍼 บันทึกแม่พันธุ์")
    df = get_safe_data("Sows", ["เลขแม่พันธุ์", "สายพันธุ์", "พ่อที่มา", "แม่ที่มา", "วันที่ผสม", "กำหนดคลอด"])
    
    with st.form("sow_form", clear_on_submit=True):
        s_id = st.text_input("เลขแม่พันธุ์")
        breed = st.text_input("สายพันธุ์")
        f_o = st.text_input("สายพันธุ์พ่อ (ที่มา)")
        m_o = st.text_input("สายพันธุ์แม่ (ที่มา)")
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)
        
        if st.form_submit_button("บันทึก"):
            new_row = pd.DataFrame([[s_id, breed, f_o, m_o, str(d_mix), str(d_due)]], columns=df.columns)
            updated = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Sows", data=updated)
            st.success("บันทึกสำเร็จ!")

# --- 3. บันทึกหมูขุน ---
elif choice == "📦 หมูขุน":
    st.header("📦 บันทึกหมูขุน")
    df = get_safe_data("Fattening", ["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])
    
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า")
        status = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวน (ตัว)", min_value=0)
        wet = st.number_input("น้ำหนักรวม (กก.)", min_value=0.0)
        pri = st.number_input("รายได้รวม (บาท)", min_value=0.0)
        dt = st.date_input("วันที่ทำรายการ")
        
        if st.form_submit_button("บันทึก"):
            new_row = pd.DataFrame([[p_id, status, amt, str(dt), wet, pri]], columns=df.columns)
            updated = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Fattening", data=updated)
            st.success("บันทึกสำเร็จ!")

# --- 4. ขายน้ำเชื้อ ---
elif choice == "🧪 น้ำเชื้อ":
    st.header("🧪 ขายน้ำเชื้อ")
    df = get_safe_data("Semen_Sales", ["วันที่", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])
    
    with st.form("semen_form", clear_on_submit=True):
        c_name = st.text_input("ชื่อลูกค้า")
        breed = st.text_input("สายพันธุ์")
        dose = st.number_input("จำนวนโดส", min_value=1)
        price = st.number_input("ราคารวม (บาท)", min_value=0)
        dt_sale = st.date_input("วันที่ขาย")
        dt_foll = dt_sale + timedelta(days=21)
        
        if st.form_submit_button("บันทึก"):
            new_row = pd.DataFrame([[str(dt_sale), c_name, breed, dose, price, str(dt_foll)]], columns=df.columns)
            updated = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="Semen_Sales", data=updated)
            st.success("บันทึกสำเร็จ!")

# --- 5. ลบข้อมูล ---
elif choice == "🗑️ ลบข้อมูล":
    st.header("🗑️ จัดการข้อมูล")
    target = st.selectbox("เลือกหมวดที่ต้องการจัดการ", ["Sows", "Fattening", "Semen_Sales"])
    df = conn.read(worksheet=target, ttl="0")
    st.write(f"ข้อมูลปัจจุบันใน {target}:")
    st.dataframe(df)
    
    if not df.empty:
        idx = st.number_input("ใส่เลขลำดับที่ต้องการลบ (0 คือแถวแรก)", min_value=0, max_value=len(df)-1)
        if st.button("ลบแถวนี้"):
            new_df = df.drop(df.index[idx])
            conn.update(worksheet=target, data=new_df)
            st.success("ลบข้อมูลแล้ว!")
            st.rerun()
