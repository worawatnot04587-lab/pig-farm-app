import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมู", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)

# --- ฟังก์ชันดึงข้อมูลแบบระบุคอลัมน์ป้องกัน Error ---
def get_data(sheet_name, cols):
    try:
        # อ่านข้อมูลโดยไม่สนชื่อหัวข้อ (ใช้แถวแรกเป็นข้อมูลไปเลยถ้าไม่มีหัว)
        df = conn.read(worksheet=sheet_name)
        if df.empty:
            return pd.DataFrame(columns=cols)
        return df
    except:
        return pd.DataFrame(columns=cols)

st.title("🐷 ระบบจัดการฟาร์มหมู (V.เสถียรที่สุด)")
menu = ["🏠 หน้าหลัก & กราฟ", "🍼 บันทึกแม่พันธุ์", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ ลบข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 1. หน้าหลัก ---
if choice == "🏠 หน้าหลัก & กราฟ":
    st.subheader("📊 สถิติภาพรวม")
    df_sows = get_data("Sows", ["เลขแม่พันธุ์", "สายพันธุ์", "พ่อพันธุ์", "แม่พันธุ์", "วันที่ผสม", "กำหนดคลอด"])
    df_fat = get_data("Fattening", ["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้รวม"])
    df_semen = get_data("Semen_Sales", ["วันที่", "ชื่อลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

    c1, c2, c3 = st.columns(3)
    c1.metric("แม่พันธุ์", f"{len(df_sows)} ตัว")
    c2.metric("รายได้หมูขุน", f"{df_fat['รายได้รวม'].sum() if not df_fat.empty else 0:,.0f} ฿")
    c3.metric("รายได้น้ำเชื้อ", f"{df_semen['ราคา'].sum() if not df_semen.empty else 0:,.0f} ฿")
    
    if not df_fat.empty:
        fig = px.bar(df_fat, x="เลขเล้า", y="จำนวน", title="จำนวนหมูในแต่ละเล้า", color="สถานะ")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. บันทึกแม่พันธุ์ ---
elif choice == "🍼 บันทึกแม่พันธุ์":
    st.header("🍼 บันทึกแม่พันธุ์")
    df = get_data("Sows", ["เลขแม่พันธุ์", "สายพันธุ์", "พ่อพันธุ์", "แม่พันธุ์", "วันที่ผสม", "กำหนดคลอด"])
    
    mode = st.radio("เลือกโหมด:", ["แม่เดิม", "จดใหม่"], horizontal=True)
    with st.form("sow_form", clear_on_submit=True):
        if mode == "แม่เดิม" and not df.empty:
            sow_id = st.selectbox("เลือกเลขแม่พันธุ์", df["เลขแม่พันธุ์"].unique())
            breed = df[df["เลขแม่พันธุ์"] == sow_id]["สายพันธุ์"].values[0]
            f_o, m_o = "", ""
        else:
            sow_id = st.text_input("เลขแม่พันธุ์ใหม่")
            breed = st.text_input("สายพันธุ์")
            f_o = st.text_input("พ่อพันธุ์(ที่มา)")
            m_o = st.text_input("แม่พันธุ์(ที่มา)")
        
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)

        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[sow_id, breed, f_o, m_o, str(d_mix), str(d_due)]], columns=df.columns)
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Sows", data=updated_df)
            st.success("บันทึกลงช่องคอลัมน์เรียบร้อย!")

# --- 3. บันทึกหมูขุน ---
elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 บันทึกหมูขุน")
    df = get_data("Fattening", ["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้รวม"])
    
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า")
        stat = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวน(ตัว)", min_value=0)
        wet = st.number_input("น้ำหนักรวม(กก.)", min_value=0.0)
        pri = st.number_input("รายได้รวม(บาท)", min_value=0.0)
        dt = st.date_input("วันที่ทำรายการ")
        
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[p_id, stat, amt, str(dt), wet, pri]], columns=df.columns)
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Fattening", data=updated_df)
            st.success("บันทึกสำเร็จ!")

# --- 4. ขายน้ำเชื้อ ---
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 ขายน้ำเชื้อ")
    df = get_data("Semen_Sales", ["วันที่", "ชื่อลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])
    
    with st.form("semen_form", clear_on_submit=True):
        c_name = st.text_input("ชื่อลูกค้า")
        s_breed = st.text_input("สายพันธุ์น้ำเชื้อ")
        dose = st.number_input("จำนวนโดส", min_value=1)
        total = st.number_input("ราคารวม", min_value=0)
        d_sale = st.date_input("วันที่ขาย")
        d_foll = d_sale + timedelta(days=21)
        
        if st.form_submit_button("บันทึก"):
            new_data = pd.DataFrame([[str(d_sale), c_name, s_breed, dose, total, str(d_foll)]], columns=df.columns)
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(worksheet="Semen_Sales", data=updated_df)
            st.success("บันทึกสำเร็จ!")

# --- 5. ลบข้อมูล ---
elif choice == "🗑️ ลบข้อมูล":
    st.header("🗑️ ลบข้อมูล")
    sheet_to_del = st.selectbox("เลือกหมวดที่ต้องการลบ", ["Sows", "Fattening", "Semen_Sales"])
    df = conn.read(worksheet=sheet_to_del)
    if not df.empty:
        idx = st.number_input("ใส่ลำดับที่ต้องการลบ (Index)", min_value=0, max_value=len(df)-1)
        if st.button("ยืนยันการลบ"):
            df = df.drop(df.index[idx])
            conn.update(worksheet=sheet_to_del, data=df)
            st.success("ลบข้อมูลแล้ว")
            st.rerun()
    st.dataframe(df)
