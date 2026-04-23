import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ตั้งค่าหน้าจอให้เหมาะกับมือถือ
st.set_page_config(page_title="Pig Farm Pro", layout="centered")

# --- 1. ระบบฐานข้อมูลชั่วคราว (Session State) ---
def init_all_db():
    if 'sow_db' not in st.session_state:
        st.session_state.sow_db = pd.DataFrame(columns=["ID", "Breed", "MixDate", "Check1", "Check2", "FeedBoost", "MovePen", "DueDate", "Status"])
    if 'fat_db' not in st.session_state:
        st.session_state.fat_db = pd.DataFrame(columns=["PenID", "StartDate", "Amount", "DeadCount", "SellDate", "Income"])
    if 'semen_db' not in st.session_state:
        st.session_state.semen_db = pd.DataFrame(columns=["Date", "Customer", "Breed", "Dose", "Price", "FollowUp"])

init_all_db()

# --- 2. ฟังก์ชันคำนวณวันสำคัญ (Sow Loop) ---
def calculate_sow_dates(mix_date):
    return {
        "Check1": mix_date + timedelta(days=21),
        "Check2": mix_date + timedelta(days=42),
        "FeedBoost": mix_date + timedelta(days=84),
        "MovePen": mix_date + timedelta(days=107),
        "DueDate": mix_date + timedelta(days=114)
    }

# --- 3. แถบเมนูหลัก (Bottom Navigation สไตล์แอปมือถือ) ---
st.title("🐷 Pig Farm Pro")
menu = st.tabs(["🏠 หน้าหลัก", "🍼 แม่พันธุ์", "📦 หมูขุน", "🧪 น้ำเชื้อ", "⚙️ จัดการ"])

# --- 4. ส่วนหน้าหลัก (Dashboard & Daily Tasks) ---
with menu[0]:
    st.subheader("📊 สรุปผลวันนี้")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("รายได้หมูขุน", f"{st.session_state.fat_db['Income'].sum():,.0f} ฿")
    with c2:
        st.metric("ยอดขายน้ำเชื้อ", f"{st.session_state.semen_db['Price'].sum():,.0f} ฿")
    
    st.subheader("📅 กิจกรรมด่วน (Daily Tasks)")
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    # ดึงงานจากตารางแม่พันธุ์
    tasks = []
    for _, row in st.session_state.sow_db.iterrows():
        d_check = datetime.strptime(row['Check1'], '%Y-%m-%d').date()
        d_due = datetime.strptime(row['DueDate'], '%Y-%m-%d').date()
        
        if d_check == today: tasks.append(f"🟡 เช็คสัดรอบ 1: แม่ {row['ID']}")
        if d_due == today: tasks.append(f"🟢 กำหนดคลอด: แม่ {row['ID']}")
        if d_due == tomorrow: tasks.append(f"🔴 พรุ่งนี้คลอด: แม่ {row['ID']}")

    if tasks:
        for t in tasks: st.warning(t)
    else:
        st.info("✅ วันนี้ไม่มีงานด่วน")

# --- 5. หมวดแม่พันธุ์ (Sow Management) ---
with menu[1]:
    st.subheader("🍼 จัดการวงรอบแม่พันธุ์")
    with st.expander("➕ บันทึกการผสมพันธุ์ใหม่", expanded=True):
        with st.form("mix_form", clear_on_submit=True):
            s_id = st.text_input("หมายเลขแม่พันธุ์ / เลขคอก")
            s_breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
            d_mix = st.date_input("วันที่ผสม", today)
            
            if st.form_submit_button("บันทึกและคำนวณวัน"):
                dates = calculate_sow_dates(d_mix)
                new_sow = pd.DataFrame([[
                    s_id, s_breed, str(d_mix), str(dates['Check1']), str(dates['Check2']), 
                    str(dates['FeedBoost']), str(dates['MovePen']), str(dates['DueDate']), "ผสมแล้ว"
                ]], columns=st.session_state.sow_db.columns)
                st.session_state.sow_db = pd.concat([st.session_state.sow_db, new_sow], ignore_index=True)
                st.success(f"บันทึกแม่ {s_id} สำเร็จ!")

    st.write("📋 รายชื่อแม่พันธุ์ในระบบ")
    st.dataframe(st.session_state.sow_db)

# --- 6. หมวดหมูขุน (Fattening Management) ---
with menu[2]:
    st.subheader("📦 จัดการเล้าหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("หมายเลขเล้า")
        f_amt = st.number_input("จำนวนหมูที่ลง (ตัว)", min_value=1)
        f_date = st.date_input("วันที่ลงหมู", today)
        sell_est = f_date + timedelta(days=120)
        st.caption(f"📅 คาดว่าขายได้ประมาณ: {sell_est.strftime('%d/%m/%Y')}")
        
        if st.form_submit_button("เปิดเล้าใหม่"):
            new_fat = pd.DataFrame([[p_id, str(f_date), f_amt, 0, str(sell_est), 0]], columns=st.session_state.fat_db.columns)
            st.session_state.fat_db = pd.concat([st.session_state.fat_db, new_fat], ignore_index=True)
            st.success(
