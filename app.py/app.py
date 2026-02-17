import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Daman Converter Pro", page_icon="⚡", layout="wide")

# --- 2. الحماية ---
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
        else: st.error("❌ خطأ")
else:
    # --- 3. الإعدادات ---
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        target_sheet = st.selectbox("🎯 نوع الشيت المستهدف:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.title(f"⚡ تحويل البيانات لـ: {target_sheet}")

    uploaded_file = st.file_uploader("ارفع الملف الخام", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            # قراءة الملف مع التأكد من المكتبة
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("🪄 ترتيب الداتا فوراً"):
                processed_data = []
                for _, row in df_in.iterrows():
                    # سحب القيم من ملفك الأصلي (تأكد من مطابقة الأسماء في الإكسيل المرفوع)
                    raw_id = str(row.get('ID', '')).split('.')[0] # تنظيف الرقم من أي علامات عشرية
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    # استخراج التاريخ بشكل نظيف
                    raw_date = row.get('تاريخ_الإنشاء', '')
                    date_val = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if raw_date != "" else ""

                    # --- الترتيب الصارم (بدون أعمدة فاضية في البداية) ---
                    
                    if target_sheet == "Damen's complaint":
                        # ترتيب: مزود، ملاحظات، مرجع، تاريخ، قيمة، رقم عملية، خدمة، كود، تاجر، محافظة
                        data = [p_provider, "رفع جماعي", "", date_val, amt, final_op, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # ترتيب: ملاحظات، مرجع، تاريخ، قيمة، رقم عملية، كود، تاجر، محافظة
                        data = ["رفع جماعي", "", date_val, amt, final_op, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # ترتيب: مزود، تاريخ، قيمة، ملاحظات، رقم عملية، خدمة
                        data = [p_provider, date_val, amt, "رفع جماعي", final_op, service]
                    
                    elif target_sheet == "Refund Transactions":
                        # ترتيب: رقم عملية، ملاحظات، مرجع، تاريخ، قيمة، خدمة، مزود، تاجر
                        data = [final_op, "رفع جماعي", "", date_val, amt, service, p_provider, m_name]

                    processed_data.append(data)

                final_df = pd.DataFrame(processed_data)
                
                # إزالة أي أعمدة فارغة تماماً في بداية الجدول لضمان الـ Paste المظبوط
                st.success("✅ تم الترتيب بنجاح!")
                st.dataframe(final_df) # عرض للتأكد

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # التحويل بدون Header وبدون Index وبدون أي زحزحة
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button("📥 تحميل الملف النهائي", output.getvalue(), f"{target_sheet}_Ready.xlsx")

        except Exception as e:
            st.error(f"⚠️ تأكد من أسماء الأعمدة في ملفك (ID، القيمه_الكليه). الخطأ: {e}")