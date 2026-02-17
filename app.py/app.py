import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- 1. إعدادات الواجهة ---
st.set_page_config(page_title="Daman Data Converter", page_icon="⚡", layout="wide")

# --- 2. نظام الحماية ---
PASSWORD_REQUIRED = "Dispute@Damen.1248#1248*"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔑 نظام ضامن لتحويل البيانات")
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ خطأ")
else:
    # --- 3. الإعدادات ---
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        selected_user = st.selectbox("👤 الموظف:", ["ahmed", "barsoum", "abdelrahman", "hanady"])
        target_sheet = st.selectbox("🎯 نوع الشيت:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.title(f"⚡ تحويل لـ: {target_sheet}")

    uploaded_file = st.file_uploader("ارفع الملف الخام", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("🪄 ترتيب حسب الصورة المعتمدة"):
                processed_data = []
                for _, row in df_in.iterrows():
                    # البيانات من ملفك
                    raw_id = str(row.get('ID', ''))
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    today = datetime.now().strftime("%Y-%m-%d")
                    amt = row.get('القيمه_الكليه', 0)
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    created_at = row.get('تاريخ_الإنشاء', '') # تأكد من اسم العمود في ملفك

                    # --- تطبيق الترتيب بناءً على الصورة بالظبط ---
                    
                    if target_sheet == "Damen's complaint":
                        # ترتيب الصورة: مزود الخدمة، معلومات، مرجع، تاريخ، قيمة، رقم عملية، اسم خدمة، كود، تاجر، محافظة
                        data = [p_provider, "رفع جماعي", "", created_at, amt, final_op, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # ترتيب الصورة: معلومات، مرجع، تاريخ، قيمة، رقم عملية، كود، تاجر، محافظة
                        data = ["رفع جماعي", "", created_at, amt, final_op, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # ترتيب الصورة: مزود الخدمة، تاريخ، قيمة، معلومات، رقم عملية، اسم خدمة
                        data = [p_provider, created_at, amt, "رفع جماعي", final_op, service]
                    
                    elif target_sheet == "Refund Transactions":
                        # ترتيب الصورة: رقم عملية، معلومات، مرجع، تاريخ، قيمة، اسم خدمة، مزود، تاجر
                        data = [final_op, "رفع جماعي", "", created_at, amt, service, p_provider, m_name]

                    processed_data.append(data)

                final_df = pd.DataFrame(processed_data)
                st.success("✅ تم الترتيب!")
                st.dataframe(final_df)

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button("📥 تحميل ملف جاهز للصق", output.getvalue(), f"{target_sheet}.xlsx")

        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")