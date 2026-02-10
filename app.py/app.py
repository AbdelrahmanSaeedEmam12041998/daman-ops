import streamlit as st
import requests

# --- حط لينك جوجل الجديد هنا ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzP6mE69f30pNZtzz3pSYXlgOt24OpXTXjp0bbfCAYS8fuRemmVtmtLlXR-kXT4UxU4/exec" 

st.set_page_config(page_title="Daman Dispute", layout="centered")
st.title("🛡️ نظام نزاعات ضامن")

with st.form("dispute_form", clear_on_submit=True):
    p_op = st.text_input("رقم عملية المزود")
    op = st.text_input("رقم العملية")
    amt = st.number_input("المبلغ", min_value=0)
    m_name = st.text_input("اسم التاجر")
    gov = st.text_input("المحافظة")
    
    submit = st.form_submit_button("إرسال للسيستم 🚀")
    
    if submit:
        # تجهيز البيانات
        payload = {"providerOpNum": p_op, "opNum": op, "amount": amt, "merchantName": m_name, "gov": gov}
        try:
            res = requests.post(SCRIPT_URL, json=payload)
            if res.status_code == 200:
                st.success("✅ تم الحفظ في الشيت بنجاح!")
            else:
                st.error("❌ مشكلة في الرابط، تأكد من الـ Deployment")
        except Exception as e:
            st.error(f"خطأ في الاتصال: {e}")