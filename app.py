import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="ระบบฟาร์มหมู V2.1", layout="wide")

# --- 1. จัดการฐานข้อมูล (Session State) ---
# กำหนดชื่อคอลัมน์ให้เหมือนกันเป๊ะทั้งระบบ
def init_db():
    if 'sow_db' not in st.session_state:
        st.session_state.sow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "สายพันธุ์", "ที่มา", "วันที่ผสม", "กำหนดคลอด"])
    if 'farrow_db' not in st.session_state:
        st.session_state.farrow_db = pd.DataFrame(columns=["เลขแม่พันธุ์", "วันที่คลอดจริง", "ลูกรอด", "ลูกตาย", "หมายเหตุ"])
    if 'fat_db' not in st.session_state:
        st.session_state.fat_db = pd.DataFrame(columns=["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])
    if 'semen_db' not in st.session_state:
        st.session_state.semen_db = pd.DataFrame(columns=["วันที่ขาย", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])

init_db()

# --- 2. เมนูหลัก ---
st.title("🐷 ระบบจัดการฟาร์มหมู")
menu = ["🏠 หน้าหลัก", "🍼 บันทึกผสม", "👶 บันทึกคลอด", "📦 หมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ จัดการข้อมูล"]
choice = st.sidebar.radio("เมนู", menu)

# --- 3. ฟังก์ชันหน้าหลัก ---
if choice == "🏠 หน้าหลัก":
    st.subheader("📊 สถิติรวม")
    c1, c2, c3 = st.columns(3)
    c1.metric("แม่พันธุ์", len(st.session_state.sow_db["เลขแม่พันธุ์"].unique()))
    c2.metric("รายได้หมูขุน", f"{st.session_state.fat_db['รายได้'].sum():,.0f} ฿")
    c3.metric("รายได้น้ำเชื้อ", f"{st.session_state.semen_db['ราคา'].sum():,.0f} ฿")
    
    if not st.session_state.farrow_db.empty:
        fig = px.bar(st.session_state.farrow_db, x="เลขแม่พันธุ์", y="ลูกรอด", title="ลูกที่รอดต่อแม่")
        st.plotly_chart(fig, use_container_width=True)

# --- 4. หน้าบันทึกผสม ---
elif choice == "🍼 บันทึกผสม":
    st.header("🍼 บันทึกการผสมพันธุ์")
    with st.form("mix_form", clear_on_submit=True):
        s_id = st.text_input("เลขแม่พันธุ์")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        origin = st.text_input("ที่มา")
        d_mix = st.date_input("วันที่ผสม", datetime.now())
        d_due = d_mix + timedelta(days=114)
        
        if st.form_submit_button("บันทึก"):
            # แก้ไขตรงนี้ให้คอลัมน์ตรงกับ sow_db เป๊ะๆ
            new_row = pd.DataFrame([[s_id, breed, origin, str(d_mix), str(d_due)]], 
                                     columns=["เลขแม่พันธุ์", "สายพันธุ์", "ที่มา", "วันที่ผสม", "กำหนดคลอด"])
            st.session_state.sow_db = pd.concat([st.session_state.sow_db, new_row], ignore_index=True)
            st.success("บันทึกข้อมูลเรียบร้อย!")

# --- 5. หน้าบันทึกคลอด ---
elif choice == "👶 บันทึกคลอด":
    st.header("👶 บันทึกการคลอด")
    sow_list = st.session_state.sow_db["เลขแม่พันธุ์"].unique().tolist()
    
    if not sow_list:
        st.warning("กรุณาบันทึกการผสมก่อนครับ")
    else:
        with st.form("farrow_form", clear_on_submit=True):
            s_id = st.selectbox("เลือกแม่พันธุ์", sow_list)
            d_real = st.date_input("วันที่คลอดจริง")
            alive = st.number_input("ลูกรอด", min_value=0)
            dead = st.number_input("ลูกตาย", min_value=0)
            note = st.text_input("หมายเหตุ")
            
            if st.form_submit_button("บันทึกการคลอด"):
                new_farrow = pd.DataFrame([[s_id, str(d_real), alive, dead, note]], 
                                           columns=["เลขแม่พันธุ์", "วันที่คลอดจริง", "ลูกรอด", "ลูกตาย", "หมายเหตุ"])
                st.session_state.farrow_db = pd.concat([st.session_state.farrow_db, new_farrow], ignore_index=True)
                st.success("อัปเดตข้อมูลคลอดแล้ว!")

# --- 6. หน้าหมูขุน ---
elif choice == "📦 หมูขุน":
    st.header("📦 บันทึกหมูขุน")
    with st.form("fat_form", clear_on_submit=True):
        p_id = st.text_input("เลขเล้า")
        stat = st.selectbox("สถานะ", ["กำลังเลี้ยง", "ขายแล้ว"])
        amt = st.number_input("จำนวน", min_value=1)
        wet = st.number_input("น้ำหนักรวม (กก.)", min_value=0.0)
        pri = st.number_input("รายได้", min_value=0.0)
        dt = st.date_input("วันที่")
        if st.form_submit_button("บันทึก"):
            new_fat = pd.DataFrame([[p_id, stat, amt, str(dt), wet, pri]], 
                                    columns=["เลขเล้า", "สถานะ", "จำนวน", "วันที่", "น้ำหนัก", "รายได้"])
            st.session_state.fat_db = pd.concat([st.session_state.fat_db, new_fat], ignore_index=True)
            st.success("บันทึกสำเร็จ")

# --- 7. ขายน้ำเชื้อ ---
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 ขายน้ำเชื้อ")
    with st.form("semen_form", clear_on_submit=True):
        cust = st.text_input("ชื่อลูกค้า")
        breed = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        dose = st.number_input("โดส", min_value=1)
        price = st.number_input("ราคารวม", min_value=0)
        dt = st.date_input("วันที่ขาย")
        if st.form_submit_button("บันทึก"):
            new_semen = pd.DataFrame([[str(dt), cust, breed, dose, price, str(dt + timedelta(days=21))]], 
                                      columns=["วันที่ขาย", "ลูกค้า", "สายพันธุ์", "โดส", "ราคา", "วันตามงาน"])
            st.session_state.semen_db = pd.concat([st.session_state.semen_db, new_semen], ignore_index=True)
            st.success("บันทึกสำเร็จ")

# --- 8. จัดการข้อมูล ---
elif choice == "🗑️ จัดการข้อมูล":
    target = st.radio("เลือกตาราง", ["ผสมพันธุ์", "การคลอด", "หมูขุน", "น้ำเชื้อ"], horizontal=True)
    if target == "ผสมพันธุ์": df = st.session_state.sow_db
    elif target == "การคลอด": df = st.session_state.farrow_db
    elif target == "หมูขุน": df = st.session_state.fat_db
    else: df = st.session_state.semen_db
    
    st.dataframe(df, use_container_width=True)
    if st.button("ล้างข้อมูลหมวดนี้"):
        if target == "ผสมพันธุ์": st.session_state.sow_db = pd.DataFrame(columns=st.session_state.sow_db.columns)
        elif target == "การคลอด": st.session_state.farrow_db = pd.DataFrame(columns=st.session_state.farrow_db.columns)
        elif target == "หมูขุน": st.session_state.fat_db = pd.DataFrame(columns=st.session_state.fat_db.columns)
        else: st.session_state.semen_db = pd.DataFrame(columns=st.session_state.semen_db.columns)
        st.rerun()
