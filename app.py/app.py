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
    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        target_sheet = st.selectbox("🎯 نوع الشيت المستهدف:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.title(f"⚡ تحويل البيانات لـ: {target_sheet}")
    uploaded_file = st.file_uploader("ارفع الملف الخام", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("🪄 ترتيب الداتا فوراً"):
                processed_data = []
                for _, row in df_in.iterrows():
                    # 1. استخراج رقم العملية وتنظيفه تماماً من أي ".0"
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    # 2. سحب البيانات الأساسية
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    
                    # 3. الترتيب القاتل (بناءً على صورة الترتيب image_d1f95c)
                    if target_sheet == "Damen's complaint":
                        # [0]مزود | [1]رفع جماعي | [2]مرجع(فاضي) | [3]تاريخ(فاضي) | [4]مبلغ | [5]DamenID | [6]خدمة | [7]كود | [8]تاجر | [9]محافظة
                        data = [p_provider, "رفع جماعي", "", "", amt, final_op, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # [0]رفع جماعي | [1]مرجع(فاضي) | [2]تاريخ(فاضي) | [3]مبلغ | [4]DamenID | [5]فراغ | [6]كود | [7]تاجر | [8]محافظة
                        # لاحظ: رقم العملية هنا هو العمود رقم 5 (Index 4)
                        data = ["رفع جماعي", "", "", amt, final_op, "", m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # [0]مزود | [1]تاريخ(فاضي) | [2]مبلغ | [3]رفع جماعي | [4]DamenID | [5]خدمة
                        data = [p_provider, "", amt, "رفع جماعي", final_op, service]
                    
                    elif target_sheet == "Refund Transactions":
                        # [0]ID_صافي | [1]رفع جماعي | [2]مرجع(فاضي) | [3]تاريخ(فاضي) | [4]مبلغ | [5]خدمة | [6]مزود | [7]تاجر
                        data = [final_op, "رفع جماعي", "", "", amt, service, p_provider, m_name]

                    processed_data.append(data)

                final_df = pd.DataFrame(processed_data)
                
                st.success("✅ تم الترتيب!")
                # المعاينة للتأكد قبل التحميل
                st.write("👀 تأكد من ترتيب الأعمدة في الجدول أدناه:")
                st.table(final_df.head(10)) 

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # header=False و index=False عشان ميبقاش فيه أي عمود زيادة
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button("📥 تحميل ملف الـ Paste المباشر", output.getvalue(), f"{target_sheet}_READY.xlsx")

        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")