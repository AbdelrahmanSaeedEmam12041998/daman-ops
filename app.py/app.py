import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO

# --- إعدادات الصفحة والروابط ---
st.set_page_config(page_title="Daman Control Center", layout="wide")

SHEETS_CONFIG = {
    "Damen's complaint": "https://script.google.com/macros/s/AKfycbzP6mE69f30pNZtzz3pSYXlgOt24OpXTXjp0bbfCAYS8fuRemmVtmtLlXR-kXT4UxU4/exec",
    "Cases V.f cash": "https://script.google.com/macros/s/AKfycbwKraVqeycfh_p78Ofpdu6gDKus9KEiHP_BHmSJAHMBNYlU1CduebbMUvbj3k7IxPK2iA/exec",
    "Orange cash": "https://script.google.com/macros/s/AKfycbz9Ki1Nu-g1w1PD0_fWE2Ad4bsO-XCSbqZa3jnGGdKwIj0RzEShcqnCg7HCXouGQohy/exec",
    "Etisalat Cash": "https://script.google.com/macros/s/AKfycbysXh3a-Hn7_aqJcVHA0WvL_essmXm5TmbMyeRX3tt0M8LnA6DBHUU3gl3Re6fWuf-Dsw/exec",
    "successful Receipt": "https://script.google.com/macros/s/AKfycbzUboPmkS4hFojEiymaMIQvrAuw8WgNmdemOudFKKptJIXUsmob7Bxl6hVUeuapHvRQpw/exec",
    "Refund Transactions": "https://script.google.com/macros/s/AKfycbwuGqMmDlbgCs2FxXnuzDyef2HpOIPl6s0243-1wGeyJMigcpQKn9FZGOCCbFLX1dnaPQ/exec"
}
USERS = ["ahmed", "barsoum", "abdelrahman", "hanady"]

st.title("🛡️ منظومة ضامن: الإدخال والتحميل الذكي")

# --- اختيار المستخدم والشيت في السايدبار ---
with st.sidebar:
    st.header("⚙️ الإعدادات")
    selected_user = st.selectbox("👤 المستخدم:", USERS)
    target_sheet = st.selectbox("🎯 وجهة البيانات:", list(SHEETS_CONFIG.keys()))
    mode = st.radio("🚀 الإجراء المطلوب:", ["إرسال للجوجل شيت", "تنزيل ملف Excel فقط"])

st.divider()

# --- فورم الإدخال ---
with st.form("main_form"):
    col1, col2 = st.columns(2)
    with col1:
        op_num = st.text_input("رقم العملية")
        p_provider = st.text_input("مزود الخدمة الأساسي")
        ref_num = st.text_input("الرقم المرجعي")
        amount = st.number_input("القيمة الكلية", min_value=0.0)
    with col2:
        created_at = st.text_input("تاريخ الإنشاء")
        service_name = st.text_input("اسم الخدمة")
        m_name = st.text_input("اسم التاجر")
        extra_info = st.text_area("معلومات إضافية")
    
    # خانات متغيرة حسب الشيت
    m_code = st.text_input("كود التاجر") if "Receipt" not in target_sheet else ""
    gov = st.text_input("المحافظة") if "Cash" in target_sheet or "complaint" in target_sheet else ""

    submit = st.form_submit_button("تنفيذ العملية ✨")

if submit:
    # 1. تجهيز البيانات حسب القواعد اللي اتفقنا عليها
    final_op_num = op_num if target_sheet == "Refund Transactions" else f"Damen{op_num}"
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 2. بناء الليست (الترتيب المعتمد)
    if target_sheet == "Refund Transactions":
        row_data = [final_op_num, extra_info, ref_num, created_at, amount, service_name, p_provider, m_name]
        headers = ["رقم العملية", "معلومات اضافية", "الرقم المرجعي", "تاريخ الانشاء", "القيمة", "الخدمة", "المزود", "التاجر"]
    elif target_sheet == "successful Receipt":
        row_data = [selected_user, p_provider, created_at, amount, extra_info, final_op_num, service_name, entry_date]
        headers = ["User", "المزود", "تاريخ الانشاء", "القيمة", "معلومات اضافية", "رقم العملية", "الخدمة", "تاريخ التسجيل"]
    else:
        # شيتات الكاش والشكاوي (مع العمود الفاضي في الكاش)
        empty_col = "" if "Cash" in target_sheet else p_provider
        row_data = [selected_user, extra_info, ref_num, created_at, amount, final_op_num, empty_col, m_code, m_name, gov, entry_date]
        headers = ["User", "معلومات اضافية", "المرجع", "الإنشاء", "القيمة", "العملية", "فراغ/مزود", "كود التاجر", "التاجر", "المحافظة", "التاريخ"]

    # --- الإجراء الأول: الإرسال السحابي ---
    if mode == "إرسال للجوجل شيت":
        res = requests.post(SHEETS_CONFIG[target_sheet], json={"payload": row_data})
        if res.status_code == 200:
            st.success(f"✅ تم التسجيل في {target_sheet} أونلاين!")
    
    # --- الإجراء الثاني: التحميل كـ Excel ---
    else:
        df = pd.DataFrame([row_data], columns=headers)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        
        st.download_button(
            label="📥 اضغط هنا لتحميل ملف Excel المترتب",
            data=output.getvalue(),
            file_name=f"{target_sheet}_{op_num}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )