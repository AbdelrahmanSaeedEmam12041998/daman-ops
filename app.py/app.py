import streamlit as st
import requests

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="Daman Dispute System", page_icon="🛡️", layout="wide")

# الرابط بتاعك (تأكد إنه شغال)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzP6mE69f30pNZtzz3pSYXlgOt24OpXTXjp0bbfCAYS8fuRemmVtmtLlXR-kXT4UxU4/exec"

# --- 2. نظام تسجيل الدخول البسيط ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.title("🔐 تسجيل الدخول")
    password = st.text_input("أدخل كلمة المرور", type="password")
    if st.button("دخول"):
        if password == "daman2024":  # تقدر تغير الباسورد من هنا
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("كلمة المرور خاطئة")

if not st.session_state['logged_in']:
    login()
else:
    # --- 3. تصميم واجهة البرنامج (بعد الدخول) ---
    st.sidebar.title("🛡️ قائمة التحكم")
    page = st.sidebar.radio("اختر المهمة:", ["تسجيل نزاع جديد", "البحث والاستعلام"])
    
    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    if page == "تسجيل نزاع جديد":
        st.header("📝 تسجيل عملية نزاع جديدة")
        with st.form("main_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                p_op = st.text_input("رقم عملية المزود")
                op = st.text_input("رقم العملية الأساسي")
            with col2:
                amt = st.number_input("المبلغ", min_value=0)
                m_name = st.text_input("اسم التاجر")
            
            gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "أخرى"])
            
            submit = st.form_submit_button("إرسال البيانات للجوجل شيت 🚀")
            
            if submit:
                if p_op and op:
                    payload = {"providerOpNum": p_op, "opNum": op, "amount": amt, "merchantName": m_name, "gov": gov}
                    res = requests.post(SCRIPT_URL, json=payload)
                    if res.status_code == 200:
                        st.success("✅ تم الحفظ بنجاح!")
                    else:
                        st.error("❌ فشل الاتصال بالسيرفر")
                else:
                    st.warning("⚠️ يرجى ملء الخانات الأساسية")

    elif page == "البحث والاستعلام":
        st.header("🔍 الاستعلام عن حالة عملية")
        search_query = st.text_input("أدخل رقم العملية للبحث عنها:")
        if st.button("بحث"):
            st.info("جاري تطوير الربط المباشر مع قاعدة البيانات لعرض النتائج هنا...")
            # ملحوظة: البحث محتاج كود doGet في جوجل شيت، هنعمله الخطوة الجاية