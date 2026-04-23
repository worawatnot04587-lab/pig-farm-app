import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px  # สำหรับสร้างกราฟสวยๆ

st.set_page_config(page_title="แอปฟาร์มหมูอัจฉริยะ", layout="wide")

# เชื่อมต่อ Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันดึงข้อมูลแบบปลอดภัย
def get_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name)
    except:
        return pd.DataFrame()

st.title("🐷 ระบบจัดการฟาร์มหมู (ฉบับสมบูรณ์ + กราฟสถิติ)")
menu = ["🏠 หน้าหลัก & กราฟสถิติ", "🍼 บันทึกแม่พันธุ์", "📦 บันทึกหมูขุน", "🧪 ขายน้ำเชื้อ", "🗑️ จัดการ/ลบข้อมูล"]
choice = st.sidebar.radio("เมนูหลัก", menu)

# --- 1. หน้าหลัก & กราฟสถิติ (DASHBOARD) ---
if choice == "🏠 หน้าหลัก & กราฟสถิติ":
    st.subheader("📊 วิเคราะห์ข้อมูลฟาร์ม")
    
    df_sows = get_data("Sows")
    df_fat = get_data("Fattening")
    df_semen = get_data("Semen_Sales")

    # ส่วนของตัวเลข Metric
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_sows = len(df_sows["เลขแม่พันธุ์"].unique()) if not df_sows.empty else 0
        st.metric("แม่พันธุ์ทั้งหมด", f"{total_sows} ตัว")
    with col2:
        income_fat = df_fat["รายได้รวม"].sum() if not df_fat.empty and "รายได้รวม" in df_fat.columns else 0
        st.metric("รายได้หมูขุน", f"{income_fat:,.0f} ฿")
    with col3:
        income_semen = df_semen["ราคารวม"].sum() if not df_semen.empty and "ราคารวม" in df_semen.columns else 0
        st.metric("รายได้น้ำเชื้อ", f"{income_semen:,.0f} ฿")
    with col4:
        total_income = income_fat + income_semen
        st.metric("รายได้รวมทั้งหมด", f"{total_income:,.0f} ฿", delta="ภาพรวมรายรับ")

    st.divider()

    # ส่วนของกราฟ
    c1, c2 = st.columns(2)
    with c1:
        st.write("📈 **เปรียบเทียบรายได้ (หมูขุน vs น้ำเชื้อ)**")
        source_data = pd.DataFrame({
            "ประเภท": ["หมูขุน", "น้ำเชื้อ"],
            "รายได้": [income_fat, income_semen]
        })
        fig1 = px.pie(source_data, values='รายได้', names='ประเภท', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.write("🐖 **จำนวนหมูในแต่ละเล้า (ปัจจุบัน)**")
        if not df_fat.empty and "เลขเล้า" in df_fat.columns:
            active_pigs = df_fat[df_fat["สถานะ"] == "กำลังเลี้ยง"]
            if not active_pigs.empty:
                fig2 = px.bar(active_pigs, x="เลขเล้า", y="จำนวนปัจจุบัน", color="เลขเล้า", text_auto=True)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("ไม่มีหมูที่กำลังเลี้ยงในขณะนี้")
        else:
            st.info("ยังไม่มีข้อมูลหมูขุน")

# --- 2. บันทึกแม่พันธุ์ ---
elif choice == "🍼 บันทึกแม่พันธุ์":
    st.header("🍼 จัดการแม่พันธุ์")
    df_sows = get_data("Sows")
    sow_list = df_sows["เลขแม่พันธุ์"].unique().tolist() if not df_sows.empty else []
    
    mode = st.radio("โหมดการทำงาน:", ["บันทึกผสม (แม่เดิมที่มีในระบบ)", "จดทะเบียนแม่พันธุ์ใหม่ (ครั้งแรก)"], horizontal=True)
    
    with st.form("sow_form", clear_on_submit=True):
        if mode == "บันทึกผสม (แม่เดิมที่มีในระบบ)":
            sow_id = st.selectbox("เลือกเลขแม่พันธุ์", sow_list if sow_list else ["ยังไม่มีข้อมูล"])
            if not df_sows.empty and sow_id != "ยังไม่มีข้อมูล":
                current_sow = df_sows[df_sows["เลขแม่พันธุ์"] == sow_id].iloc[-1]
                st.info(f"🧬 สายพันธุ์: {current_sow['สายพันธุ์']} | ที่มา: พ่อ {current_sow.get('พ่อพันธุ์(ที่มา)','-')} / แม่ {current_sow.get('แม่พันธุ์(ที่มา)','-')}")
                breed_final = current_sow['สายพันธุ์']
                f_origin, m_origin = current_sow.get('พ่อพันธุ์(ที่มา)',''), current_sow.get('แม่พันธุ์(ที่มา)','')
            else: breed_final, f_origin, m_origin = "", "", ""
        else:
            sow_id = st.text_input("ระบุเลขแม่พันธุ์ใหม่")
            breed_selected = st.selectbox("สายพันธุ์", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม 2 สายพันธุ์", "อื่นๆ"])
            custom_breed = st.text_input("ระบุสายพันธุ์เพิ่มเติม (ถ้ามี)")
            f_origin = st.text_input("สายพันธุ์พ่อ (ที่มา)")
            m_origin = st.text_input("สายพันธุ์แม่ (ที่มา)")
            breed_final = custom_breed if custom_breed else breed_selected

        date_bred = st.date_input("วันที่ผสมล่าสุด", datetime.now())
        due_date = date_bred + timedelta(days=114)
        st.write(f"📅 **วันกำหนดคลอดคาดการณ์: {due_date.strftime('%d/%m/%Y')}**")

        if st.form_submit_button("บันทึกข้อมูล"):
            new_row = pd.DataFrame([{"เลขแม่พันธุ์": sow_id, "สายพันธุ์": breed_final, "พ่อพันธุ์(ที่มา)": f_origin, "แม่พันธุ์(ที่มา)": m_origin, "วันที่ผสม": str(date_bred), "กำหนดคลอด": str(due_date)}])
            updated_df = pd.concat([df_sows, new_row], ignore_index=True) if not df_sows.empty else new_row
            conn.update(worksheet="Sows", data=updated_df)
            st.success("บันทึกข้อมูลสำเร็จ!")

# --- 3. บันทึกหมูขุน ---
elif choice == "📦 บันทึกหมูขุน":
    st.header("📦 จัดการหมูขุน")
    df_fat = get_data("Fattening")
    pen_list = df_fat["เลขเล้า"].unique().tolist() if not df_fat.empty else []
    
    mode_fat = st.radio("โหมด:", ["ลงหมูใหม่ (เล้าใหม่)", "จัดการเล้าเดิม (ลงเพิ่ม/ขาย)"], horizontal=True)

    with st.form("fat_form"):
        if mode_fat == "ลงหมูใหม่ (เล้าใหม่)":
            pen_id = st.text_input("เลขเล้า/คอก")
            action = "ลงหมูใหม่"
        else:
            pen_id = st.selectbox("เลือกเล้า", pen_list if pen_list else ["ไม่มีข้อมูล"])
            action = st.selectbox("กิจกรรม", ["ลงหมูเพิ่ม", "บันทึกขาย/คัดออก"])

        if "ขาย" in action:
            col_a, col_b = st.columns(2)
            amount = col_a.number_input("จำนวนที่ขาย (ตัว)", min_value=1)
            total_weight = col_b.number_input("น้ำหนักรวมทั้งหมด (กก.)", min_value=0.0)
            price_per_kg = st.number_input("ราคากิโลกรัมละ (บาท)", min_value=0.0)
            income = total_weight * price_per_kg
            date_act = st.date_input("วันที่ขาย")
        else:
            amount = st.number_input("จำนวนหมูที่ลง (ตัว)", min_value=1)
            date_act = st.date_input("วันที่ลงหมู")
            income, total_weight = 0, 0

        if st.form_submit_button("บันทึกข้อมูล"):
            new_row = pd.DataFrame([{"เลขเล้า": pen_id, "สถานะ": "ขายแล้ว" if "ขาย" in action else "กำลังเลี้ยง", "จำนวนปัจจุบัน": amount, "วันที่ลงหมู/ขาย": str(date_act), "น้ำหนักรวมที่ขาย": total_weight, "รายได้รวม": income}])
            updated_df = pd.concat([df_fat, new_row], ignore_index=True) if not df_fat.empty else new_row
            conn.update(worksheet="Fattening", data=updated_df)
            st.success("บันทึกสำเร็จ!")

# --- 4. ขายน้ำเชื้อ ---
elif choice == "🧪 ขายน้ำเชื้อ":
    st.header("🧪 บันทึกการขายน้ำเชื้อ")
    df_semen = get_data("Semen_Sales")
    customer_list = df_semen["ชื่อลูกค้า"].unique().tolist() if not df_semen.empty else []

    with st.form("semen_form"):
        cust_type = st.radio("ลูกค้า:", ["ใหม่", "เดิม"], horizontal=True)
        customer_name = st.text_input("ชื่อลูกค้า") if cust_type == "ใหม่" else st.selectbox("เลือกชื่อลูกค้า", customer_list)
        breed = st.selectbox("สายพันธุ์น้ำเชื้อ", ["แลนด์เรซ", "ลาร์จไวท์", "ดูร็อค", "ผสม"])
        doses = st.number_input("จำนวนโดส", min_value=1)
        price = st.number_input("ราคารวม (บาท)", min_value=0)
        date_sale = st.date_input("วันที่ขาย", datetime.now())
        
        if st.form_submit_button("บันทึก"):
            new_row = pd.DataFrame([{"วันที่ขาย": str(date_sale), "ชื่อลูกค้า": customer_name, "สายพันธุ์": breed, "จำนวนโดส": doses, "ราคารวม": price, "วันตามงาน": str(date_sale + timedelta(days=21))}])
            updated_df = pd.concat([df_semen, new_row], ignore_index=True) if not df_semen.empty else new_row
            conn.update(worksheet="Semen_Sales", data=updated_df)
            st.success("บันทึกการขายน้ำเชื้อเรียบร้อย!")

# --- 5. จัดการ/ลบข้อมูล ---
elif choice == "🗑️ จัดการ/ลบข้อมูล":
    st.header("🗑️ จัดการและลบข้อมูล")
    st.warning("ระวัง: การลบข้อมูลไม่สามารถย้อนคืนได้")
    
    t1, t2, t3 = st.tabs(["ลบแม่พันธุ์", "ลบหมูขุน", "ลบน้ำเชื้อ"])
    
    with t1:
        df = get_data("Sows")
        if not df.empty:
            for i, row in df.iterrows():
                if st.button(f"ลบแถว {i}: แม่ {row['เลขแม่พันธุ์']} ({row.get('วันที่ผสม','')})", key=f"sow_{i}"):
                    conn.update(worksheet="Sows", data=df.drop(i))
                    st.rerun()
            st.table(df)

    with t2:
        df = get_data("Fattening")
        if not df.empty:
            for i, row in df.iterrows():
                if st.button(f"ลบแถว {i}: เล้า {row['เลขเล้า']} ({row['สถานะ']})", key=f"fat_{i}"):
                    conn.update(worksheet="Fattening", data=df.drop(i))
                    st.rerun()
            st.table(df)

    with t3:
        df = get_data("Semen_Sales")
        if not df.empty:
            for i, row in df.iterrows():
                if st.button(f"ลบแถว {i}: ลูกค้า {row['ชื่อลูกค้า']} ({row['ราคารวม']}฿)", key=f"semen_{i}"):
                    conn.update(worksheet="Semen_Sales", data=df.drop(i))
                    st.rerun()
            st.table(df)
