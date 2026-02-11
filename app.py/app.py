import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Daman Dispute System", page_icon="🛡️", layout="wide")

# --- نظام الحماية ---
PASSWORD_REQUIRED = "Dispute@Damen.1248#1248*"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔑 تسجيل الدخول")
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ خطأ!")
else:
    # --- الروابط ---
    SHEETS_CONFIG = {
        "Damen's complaint": "https://script.google.com/macros/s/AKfycbzP6mE69f30pNZtzz3pSYXlgOt24OpXTXjp0bbfCAYS8fuRemmVtmtLlXR-kXT4UxU4/exec",
        "Cases V.f cash": "https://script.google.com/macros/s/AKfycbwKraVqeycfh_p78Ofpdu6gDKus9KEiHP_BHmSJAHMBNYlU1CduebbMUvbj3k7IxPK2iA/exec",
        "Orange cash": "https://script.google.com/macros/s/AKfycbz9Ki1Nu-g1w1PD0_fWE2Ad4bsO-XCSbqZa3jnGGdKwIj0RzEShcqnCg7HCXouGQohy/exec",
        "Etisalat Cash": "https://script.google.com/macros/s/AKfycbysXh3a-Hn7_aqJcVHA0WvL_essmXm5TmbMyeRX3tt0M8LnA6DBHUU3gl3Re6fWuf-Dsw/exec",
        "successful Receipt": "https://script.google.com/macros/s/AKfycbzUboPmkS4hFojEiymaMIQvrAuw8WgNmdemOudFKKptJIXUsmob7Bxl6hVUeuapHvRQpw/exec",
        "Refund Transactions": "https://script.google.com/macros/s/AKfycbwuGqMmDlbgCs2FxXnuzDyef2HpOIPl6s0243-1wGeyJMigcpQKn9FZGOCCbFLX1dnaPQ/exec"
    }

    with st.sidebar:
        if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
        selected_user = st.selectbox("👤 الموظف:", ["ahmed", "barsoum", "abdelrahman", "hanady"])
        target_sheet = st.selectbox("🎯 الشيت:", list(SHEETS_CONFIG.keys()))
        input_mode = st.radio("📥 الإدخال:", ["إدخال يدوي", "رفع ملف Excel كامل"])
        action_type = st.radio("🚀 الإجراء:", ["حفظ أونلاين (Google Sheet)", "استخراج ملف (Excel Local)"])

    st.title(f"🛡️ معالجة: {target_sheet}")

    if 'data_to_send' not in st.session_state: st.session_state['data_to_send'] = []

    if input_mode == "رفع ملف Excel كامل":
        uploaded_file = st.file_uploader("اختر الملف", type=["xlsx", "xls"])
        if uploaded_file:
            # استخدام engine='openpyxl' صراحةً لحل المشكلة
            try:
                df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
                st.write("👀 معاينة:")
                st.dataframe(df_in.head())
                
                if st.button("تحويل البيانات ⚙️"):
                    temp = []
                    for _, row in df_in.iterrows():
                        op = str(row.get('ID', ''))
                        final_op = op if target_sheet == "Refund Transactions" else f"Damen{op}"
                        today = datetime.now().strftime("%Y-%m-%d")
                        
                        m_code = row.get('كود_التاجر', '')
                        m_name = row.get('اسم_التاجر', '')
                        gov = row.get('اسم_المحافظه', '')
                        amt = row.get('القيمه_الكليه', 0)

                        if target_sheet == "Refund Transactions":
                            d = [final_op, "رفع جماعي", "", "", amt, "", "", m_name]
                        elif target_sheet == "successful Receipt":
                            d = [selected_user, "", "", amt, "رفع جماعي", final_op, "", today]
                        elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                            d = [selected_user, "رفع جماعي", "", "", amt, final_op, "", m_code, m_name, gov, today]
                        else:
                            d = [selected_user, "", "رفع جماعي", "", "", amt, final_op, "", m_code, m_name, gov, today]
                        temp.append(d)
                    st.session_state['data_to_send'] = temp
                    st.success("✅ تم الترتيب!")
            except Exception as e:
                st.error(f"⚠️ خطأ في قراءة الملف: {e}")

    # --- التنفيذ ---
    if st.session_state['data_to_send']:
        final_df = pd.DataFrame(st.session_state['data_to_send'])
        st.table(final_df)
        if action_type == "حفظ أونلاين (Google Sheet)":
            if st.button("إرسال النهائي 🚀"):
                for r in st.session_state['data_to_send']:
                    requests.post(SHEETS_CONFIG[target_sheet], json={"payload": r})
                st.success("✅ تم الإرسال!")
                st.session_state['data_to_send'] = []
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, header=False)
            st.download_button("📥 تحميل المترتب", output.getvalue(), "Damen_Report.xlsx")