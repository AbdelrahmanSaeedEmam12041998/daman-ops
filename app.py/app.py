import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. التصميم العالمي (Modern White UI) ---
st.set_page_config(page_title="Daman Elite v4.2", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2d3436; }
    .main-header { font-size: 30px; color: #0984e3; font-weight: 800; text-align: center; padding: 20px; border-bottom: 1px solid #dfe6e9; }
    .stButton>button { background: linear-gradient(135deg, #0984e3, #6c5ce7); color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; height: 3em; }
    .stTable { border: 1px solid #dfe6e9; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔐 Daman Data System</div>", unsafe_allow_html=True)
    pwd = st.text_input("Security Key:", type="password")
    if st.button("Enter"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("Invalid Key")
else:
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        target_sheet = st.selectbox("🎯 اختر نوع الشيت:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='main-header'>🚀 {target_sheet} (LTR Mode)</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل الخام", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            df_raw = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("تحويل وترتيب البيانات"):
                final_data = []
                for _, row in df_raw.iterrows():
                    # تنظيف الـ ID وتجهيز البيانات
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    damen_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    date_val = row.get('تاريخ_الإنشاء', '')

                    # --- الترتيب الصارم من الشمال لليمين حسب صورتك ---
                    if target_sheet == "Damen's complaint":
                        row_content = [provider, "رفع جماعي", "", date_val, amt, damen_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        row_content = ["رفع جماعي", "", date_val, amt, damen_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        row_content = [provider, date_val, amt, "رفع جماعي", damen_id, service]
                    
                    else: # Refund Transactions
                        row_content = [damen_id, "رفع جماعي", "", date_val, amt, service, provider, m_name]
                    
                    final_data.append(row_content)

                df_final = pd.DataFrame(final_data)

                st.markdown("### 📋 معاينة الشيت (من الشمال لليمين):")
                st.table(df_final.head(10))

                # --- التصدير مع جعل الشيت Left-to-Right ---
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False)
                    
                    # الوصول إلى "Worksheet" لتغيير الاتجاه
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    # السطر السحري لجعل الاتجاه من الشمال لليمين
                    worksheet.right_to_left(False) 
                
                st.download_button("📥 تحميل الملف النهائي (LTR)", output.getvalue(), f"{target_sheet}_LTR.xlsx")
        except Exception as e:
            st.error(f"Error: {e}")