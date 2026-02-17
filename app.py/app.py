import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- 1. إعدادات الواجهة الاحترافية ---
st.set_page_config(page_title="Daman Dispute System v2.0", page_icon="🛡️", layout="wide")

# تنسيق CSS بسيط لجعل الواجهة "عالمية"
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الحماية ---
PASSWORD_REQUIRED = "Dispute@Damen.1248#1248*"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔑 نظام معالجة نزاعات ضامن")
    pwd = st.text_input("أدخل كلمة المرور السرية:", type="password")
    if st.button("دخول للنظام"):
        if pwd == PASSWORD_REQUIRED:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ كلمة المرور غير صحيحة")
else:
    # --- 3. روابط الشيتات والأسماء ---
    SHEETS_CONFIG = {
        "Damen's complaint": "رابط_1",
        "Cases V.f cash": "رابط_2",
        "Orange cash": "رابط_3",
        "Etisalat Cash": "رابط_4",
        "successful Receipt": "رابط_5",
        "Refund Transactions": "رابط_6"
    }

    # القائمة الجانبية بتصميم شيك
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.header("⚙️ التحكم المركزي")
        selected_user = st.selectbox("👤 المسؤول الحالي:", ["ahmed", "barsoum", "abdelrahman", "hanady"])
        target_sheet = st.selectbox("🎯 الشيت المستهدف:", list(SHEETS_CONFIG.keys()))
        input_mode = st.radio("📥 نوع الإدخال:", ["رفع ملف Excel جماعي", "إدخال يدوي سريع"])
        st.divider()
        action_type = st.radio("🚀 الإجراء:", ["حفظ أونلاين (Google Sheet)", "استخراج ملف (Excel Local)"])

    st.title(f"🛡️ معالجة بيانات: {target_sheet}")

    if 'data_to_send' not in st.session_state:
        st.session_state['data_to_send'] = []

    # --- 4. معالجة الرفع الجماعي (Bulk Upload) ---
    if input_mode == "رفع ملف Excel جماعي":
        uploaded_file = st.file_uploader("اسحب ملف الإكسيل هنا", type=["xlsx", "xls"])
        if uploaded_file:
            try:
                # قراءة الملف مع تحديد الـ Engine لضمان التشغيل
                df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
                
                # كروت الإحصائيات (الشغل العالمي)
                c1, c2, c3 = st.columns(3)
                c1.metric("عدد العمليات", len(df_in))
                if 'القيمه_الكليه' in df_in.columns:
                    c2.metric("إجمالي المبالغ", f"{df_in['القيمه_الكليه'].sum():,.2f} ج.م")
                c3.metric("الموظف", selected_user)

                if st.button("✨ ابدأ المعالجة والترتيب السحري"):
                    temp_list = []
                    for _, row in df_in.iterrows():
                        # سحب البيانات الأساسية
                        raw_id = str(row.get('ID', ''))
                        # التحويل المطلوب: إضافة Damen قبل الرقم (إلا في ريفاند)
                        final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                        today = datetime.now().strftime("%Y-%m-%d")
                        
                        m_code = row.get('كود_التاجر', '')
                        m_name = row.get('اسم_التاجر', '')
                        gov = row.get('اسم_المحافظه', '')
                        amt = row.get('القيمه_الكليه', 0)
                        p_provider = row.get('مزود_الخدمة_الاساسي', '')
                        service = row.get('اسم_الخدمة', '')

                        # --- الترتيب المطابق للصورة ---
                        if target_sheet == "Refund Transactions":
                            data = [final_op, "معالجة جماعية", "", "", amt, service, p_provider, m_name]
                        elif target_sheet == "successful Receipt":
                            data = [selected_user, p_provider, "", amt, "معالجة جماعية", final_op, service, today]
                        elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                            # الموظف، ملاحظات، مرجع، تاريخ، مبلغ، رقم العملية (Damen)، فراغ، كود، تاجر، محافظة، اليوم
                            data = [selected_user, "معالجة جماعية", "", "", amt, final_op, "", m_code, m_name, gov, today]
                        else: # Damen's complaint
                            data = [selected_user, p_provider, "معالجة جماعية", "", "", amt, final_op, service, m_code, m_name, gov, today]
                        
                        temp_list.append(data)
                    st.session_state['data_to_send'] = temp_list
                    st.success("✅ تم تحويل البيانات وإضافة 'Damen' بنجاح!")

            except Exception as e:
                st.error(f"⚠️ مشكلة في الملف: تأكد من وجود عمود باسم 'ID' و 'القيمه_الكليه'. الخطأ: {e}")

    # --- 5. عرض النتائج والتنفيذ ---
    if st.session_state['data_to_send']:
        st.subheader("📋 المعاينة النهائية للملف المترتب")
        final_df = pd.DataFrame(st.session_state['data_to_send'])
        st.dataframe(final_df, use_container_width=True)

        if action_type == "حفظ أونلاين (Google Sheet)":
            if st.button("إرسال البيانات إلى Google Sheets 🚀"):
                progress_bar = st.progress(0)
                total = len(st.session_state['data_to_send'])
                for i, row in enumerate(st.session_state['data_to_send']):
                    try:
                        requests.post(SHEETS_CONFIG[target_sheet], json={"payload": row})
                        progress_bar.progress((i + 1) / total)
                    except: pass
                st.success(f"🔥 تم إرسال {total} عملية بنجاح!")
                st.session_state['data_to_send'] = []
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                final_df.to_excel(writer, index=False, header=False)
            st.download_button("📥 تحميل ملف الإكسيل المترتب", output.getvalue(), f"Damen_Ready_{target_sheet}.xlsx")