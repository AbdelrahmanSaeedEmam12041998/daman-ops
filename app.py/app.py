import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- 1. إعدادات الصفحة واللوجو ---
st.set_page_config(page_title="Daman Dispute System", page_icon="🛡️", layout="wide")

# --- 2. نظام الحماية (كلمة السر) ---
PASSWORD_REQUIRED = "Dispute@Damen.1248#1248*"

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.title("🔑 تسجيل الدخول لنظام ضامن")
        pwd = st.text_input("أدخل كلمة المرور الخاصة بالتيم:", type="password")
        if st.button("دخول للنظام"):
            if pwd == PASSWORD_REQUIRED:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

if check_password():
    # --- 3. روابط الـ 6 شيتات (ضع روابط الـ Deployment الحقيقية هنا) ---
    SHEETS_CONFIG = {
        "Damen's complaint": "https://script.google.com/macros/s/AKfycbzP6mE69f30pNZtzz3pSYXlgOt24OpXTXjp0bbfCAYS8fuRemmVtmtLlXR-kXT4UxU4/exec",
        "Cases V.f cash": "https://script.google.com/macros/s/AKfycbwKraVqeycfh_p78Ofpdu6gDKus9KEiHP_BHmSJAHMBNYlU1CduebbMUvbj3k7IxPK2iA/exec",
        "Orange cash": "https://script.google.com/macros/s/AKfycbz9Ki1Nu-g1w1PD0_fWE2Ad4bsO-XCSbqZa3jnGGdKwIj0RzEShcqnCg7HCXouGQohy/exec",
        "Etisalat Cash": "https://script.google.com/macros/s/AKfycbysXh3a-Hn7_aqJcVHA0WvL_essmXm5TmbMyeRX3tt0M8LnA6DBHUU3gl3Re6fWuf-Dsw/exec",
        "successful Receipt": "https://script.google.com/macros/s/AKfycbzUboPmkS4hFojEiymaMIQvrAuw8WgNmdemOudFKKptJIXUsmob7Bxl6hVUeuapHvRQpw/exec",
        "Refund Transactions": "https://script.google.com/macros/s/AKfycbwuGqMmDlbgCs2FxXnuzDyef2HpOIPl6s0243-1wGeyJMigcpQKn9FZGOCCbFLX1dnaPQ/exec"
    }
    USERS = ["ahmed", "barsoum", "abdelrahman", "hanady"]

    # --- 4. القائمة الجانبية (Sidebar) ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.info("ℹ️ ارفع logo.png لتظهر هنا")
            
        st.header("⚙️ الإعدادات المركزية")
        selected_user = st.selectbox("👤 الموظف المسؤول:", USERS)
        target_sheet = st.selectbox("🎯 الشيت المستهدف:", list(SHEETS_CONFIG.keys()))
        input_mode = st.radio("📥 طريقة الإدخال:", ["إدخال يدوي", "رفع ملف Excel كامل"])
        
        st.divider()
        action_type = st.radio("🛠️ الإجراء المطلوب:", ["حفظ أونلاين (Google Sheet)", "استخراج ملف (Excel Local)"])
        
        if st.button("تسجيل الخروج"):
            st.session_state["authenticated"] = False
            st.rerun()

    st.title(f"🛡️ معالجة بيانات: {target_sheet}")

    if 'data_to_send' not in st.session_state:
        st.session_state['data_to_send'] = []

    # --- 5. منطق الرفع الجماعي (Bulk Upload) المحدث بناءً على صورتك ---
    if input_mode == "رفع ملف Excel كامل":
        uploaded_file = st.file_uploader("اختر ملف الإكسيل الخارجي", type=["xlsx", "xls"])
        if uploaded_file:
            df_in = pd.read_excel(uploaded_file).fillna("")
            st.write("👀 معاينة للملف المرفوع:")
            st.dataframe(df_in.head())
            
            if st.button("تحويل وترتيب البيانات فوراً ⚙️"):
                temp_list = []
                for _, row in df_in.iterrows():
                    # سحب البيانات بناءً على أسماء الأعمدة في ملفك المرفوع
                    op = str(row.get('ID', ''))
                    final_op = op if target_sheet == "Refund Transactions" else f"Damen{op}"
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov_name = row.get('اسم_المحافظه', '')
                    total_amt = row.get('القيمه_الكليه', 0)

                    # الترتيب الاحترافي المتفق عليه
                    if target_sheet == "Refund Transactions":
                        data = [final_op, "رفع جماعي", "", "", total_amt, "", "", m_name]
                    elif target_sheet == "successful Receipt":
                        data = [selected_user, "", "", total_amt, "رفع جماعي", final_op, "", today]
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # [User, ملاحظات, مرجع, إنشاء, مبلغ, عملية, فراغ, كود, تاجر, محافظة, اليوم]
                        data = [selected_user, "رفع جماعي", "", "", total_amt, final_op, "", m_code, m_name, gov_name, today]
                    else: # Damen's complaint
                        data = [selected_user, "", "رفع جماعي", "", "", total_amt, final_op, "", m_code, m_name, gov_name, today]
                    
                    temp_list.append(data)
                st.session_state['data_to_send'] = temp_list
                st.success(f"✅ تم ترتيب {len(temp_list)} صف بنجاح!")

    # --- 6. منطق الإدخال اليدوي ---
    else:
        with st.form("manual_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                op_num = st.text_input("رقم العملية")
                p_provider = st.text_input("مزود الخدمة")
                amount = st.number_input("القيمة الكلية", min_value=0.0)
                ref_num = st.text_input("الرقم المرجعي")
            with c2:
                created_at = st.text_input("تاريخ الإنشاء")
                m_name = st.text_input("اسم التاجر")
                service_name = st.text_input("اسم الخدمة")
                m_code = st.text_input("كود التاجر")
            extra_info = st.text_area("معلومات إضافية")
            gov = st.text_input("المحافظة")
            
            if st.form_submit_button("إضافة ومعالجة الصف"):
                final_op = op_num if target_sheet == "Refund Transactions" else f"Damen{op_num}"
                today = datetime.now().strftime("%Y-%m-%d")
                
                if target_sheet == "Refund Transactions":
                    data = [final_op, extra_info, ref_num, created_at, amount, service_name, p_provider, m_name]
                elif target_sheet == "successful Receipt":
                    data = [selected_user, p_provider, created_at, amount, extra_info, final_op, service_name, today]
                elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                    data = [selected_user, extra_info, ref_num, created_at, amount, final_op, "", m_code, m_name, gov, today]
                else:
                    data = [selected_user, p_provider, extra_info, ref_num, created_at, amount, final_op, service_name, m_code, m_name, gov, today]
                
                st.session_state['data_to_send'] = [data]

    # --- 7. التنفيذ النهائي ---
    if st.session_state['data_to_send']:
        st.write("### 📋 المعاينة المترتبة (جاهز للتنفيذ):")
        final_df = pd.DataFrame(st.session_state['data_to_send'])
        st.table(final_df) # عرض كجدول واضح

        if action_type == "حفظ أونلاين (Google Sheet)":
            if st.button("تأكيد الإرسال النهائي 🚀"):
                for row in st.session_state['data_to_send']:
                    try: requests.post(SHEETS_CONFIG[target_sheet], json={"payload": row})
                    except: pass
                st.success("✅ تم الإرسال بنجاح!")
                st.session_state['data_to_send'] = []
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, header=False)
            st.download_button("📥 تحميل الإكسيل المترتب", output.getvalue(), f"Damen_{target_sheet}.xlsx")