import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. تصميم نظيف جداً (ثيم أبيض) ---
st.set_page_config(page_title="Daman Final Fix", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-header { font-size: 28px; color: #1e40af; font-weight: bold; text-align: center; padding: 20px; border-bottom: 2px solid #f3f4f6; }
    .stButton>button { background-color: #2563eb; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔒 دخول نظام ضامن</div>", unsafe_allow_html=True)
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    with st.sidebar:
        target_sheet = st.selectbox("🎯 اختر نوع الشيت:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='main-header'>🚀 معالجة {target_sheet}</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف الخام", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            df_raw = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("تنفيذ الترتيب النهائي"):
                processed_rows = []
                for _, row in df_raw.iterrows():
                    # تنظيف البيانات
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    damen_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    date_val = row.get('تاريخ_الإنشاء', '')

                    # --- الترتيب الصارم من الشمال لليمين (A, B, C...) بدون أي فراغات ---
                    if target_sheet == "Damen's complaint":
                        # مزود | معلومات | مرجع | تاريخ | قيمة | رقم عملية | خدمة | كود | تاجر | محافظة
                        line = [provider, "رفع جماعي", "", date_val, amt, damen_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # معلومات | مرجع | تاريخ | قيمة | رقم عملية | كود | تاجر | محافظة
                        line = ["رفع جماعي", "", date_val, amt, damen_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # مزود | تاريخ | قيمة | معلومات | رقم عملية | خدمة
                        line = [provider, date_val, amt, "رفع جماعي", damen_id, service]
                    
                    else: # Refund Transactions
                        # رقم عملية | معلومات | مرجع | تاريخ | قيمة | خدمة | مزود | تاجر
                        line = [damen_id, "رفع جماعي", "", date_val, amt, service, provider, m_name]
                    
                    processed_rows.append(line)

                # إنشاء الشيت النهائي (تصفير أي أعمدة زايدة)
                df_final = pd.DataFrame(processed_rows)

                st.subheader("📋 معاينة الداتا (من الشمال لليمين):")
                st.dataframe(df_final.head(10), use_container_width=True)

                # --- التصدير الصحيح ---
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Damen_Report')
                    
                    # ضبط اتجاه الشيت من الشمال لليمين بدون أخطاء
                    workbook = writer.book
                    worksheet = writer.sheets['Damen_Report']
                    # السطر الصحيح لعمل RTL = False (يعني يبدأ من الشمال A)
                    worksheet.set_right_to_left(False) 
                
                st.download_button("📥 تحميل الملف الجاهز للصق", output.getvalue(), f"{target_sheet}.xlsx")
        except Exception as e:
            st.error(f"⚠️ خطأ غير متوقع: {e}")