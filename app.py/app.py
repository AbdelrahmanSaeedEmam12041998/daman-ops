import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import os

# --- 1. إعدادات الواجهة (الاحترافية البسيطة) ---
st.set_page_config(page_title="Daman Data Converter", page_icon="⚡", layout="wide")

# تصميم بسيط للواجهة
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

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
            st.error("❌ كلمة المرور غير صحيحة")
else:
    # --- 3. القائمة الجانبية ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        st.header("⚙️ إعدادات التحويل")
        selected_user = st.selectbox("👤 الموظف المسؤول:", ["ahmed", "barsoum", "abdelrahman", "hanady"])
        target_sheet = st.selectbox("🎯 نوع الشيت المطلوب استخراجه:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])
        st.info("💡 هذا النظام يقوم بترتيب البيانات وإضافة 'Damen' تلقائياً.")

    st.title(f"⚡ محول البيانات: {target_sheet}")

    # --- 4. رفع ومعالجة الملف ---
    uploaded_file = st.file_uploader("ارفع ملف الإكسيل الخام هنا", type=["xlsx", "xls"])
    
    if uploaded_file:
        try:
            # قراءة الملف
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            # عرض إحصائيات سريعة
            c1, c2 = st.columns(2)
            c1.metric("عدد العمليات المرصودة", len(df_in))
            c2.metric("المسؤول", selected_user)

            if st.button("🪄 ترتيب وتحويل البيانات الآن"):
                processed_data = []
                for _, row in df_in.iterrows():
                    # سحب البيانات الأساسية بناءً على الأعمدة المتفق عليها
                    raw_id = str(row.get('ID', ''))
                    # إضافة Damen (ما عدا ريفاند)
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    today = datetime.now().strftime("%Y-%m-%d")
                    
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    amt = row.get('القيمه_الكليه', 0)
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # --- تطبيق الترتيب الدقيق للصورة ---
                    if target_sheet == "Refund Transactions":
                        data = [final_op, "معالجة", "", "", amt, service, p_provider, m_name]
                    elif target_sheet == "successful Receipt":
                        data = [selected_user, p_provider, "", amt, "معالجة", final_op, service, today]
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        data = [selected_user, "معالجة", "", "", amt, final_op, "", m_code, m_name, gov, today]
                    else: # Damen's complaint
                        data = [selected_user, p_provider, "معالجة", "", "", amt, final_op, service, m_code, m_name, gov, today]
                    
                    processed_data.append(data)

                # إنشاء الملف الجديد للتحميل
                final_df = pd.DataFrame(processed_data)
                
                st.success("✅ تم الترتيب بنجاح! عاين البيانات ثم اضغط تحميل.")
                st.dataframe(final_df, use_container_width=True)

                # زر التحميل
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index=False, header=False) # بدون عناوين عشان اللصق المباشر
                
                st.download_button(
                    label="📥 تحميل ملف الإكسيل المترتب (جاهز للصق)",
                    data=output.getvalue(),
                    file_name=f"Ready_{target_sheet}_{today}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"⚠️ تأكد من أن الملف يحتوي على أعمدة (ID, القيمه_الكليه، إلخ). الخطأ: {e}")