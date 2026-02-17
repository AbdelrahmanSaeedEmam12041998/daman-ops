import streamlit as st
import pandas as pd
from io import BytesIO
import os

# --- 1. استايل عالمي (Dark Blue & Clean White) ---
st.set_page_config(page_title="Daman Pro Converter", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { font-size: 30px; color: #1e3a8a; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔐 بوابة ضامن للعمليات</div>", unsafe_allow_html=True)
    with st.container():
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if pwd == "Dispute@Damen.1248#1248*":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("❌ كلمة المرور غير صحيحة")
else:
    # --- 3. الواجهة الجانبية (Sidebar) ---
    with st.sidebar:
        st.markdown("### ⚙️ التحكم")
        target_sheet = st.selectbox("🎯 اختر الشيت المستهدف:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])
        st.divider()
        st.write("✅ النسخة المستقرة v3.0")

    st.markdown(f"<div class='main-header'>🛡️ محول بيانات {target_sheet}</div>", unsafe_allow_html=True)

    # --- 4. منطقة الرفع ---
    uploaded_file = st.file_uploader("📂 اسحب ملف الإكسيل الخام هنا", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            st.info("✅ تم قراءة الملف بنجاح. اضغط على الزر أدناه للتحويل.")
            
            if st.button("🚀 تحويل وترتيب الداتا"):
                final_rows = []
                for _, row in df_in.iterrows():
                    # تنظيف الداتا
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # الترتيب الصارم (بدون أي أصفار أو أعمدة ترحيل في البداية)
                    if target_sheet == "Damen's complaint":
                        data = [p_provider, "رفع جماعي", "", "", amt, final_op, service, m_code, m_name, gov]
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        data = ["رفع جماعي", "", "", amt, final_op, "", m_code, m_name, gov]
                    elif target_sheet == "successful Receipt":
                        data = [p_provider, "", amt, "رفع جماعي", final_op, service]
                    elif target_sheet == "Refund Transactions":
                        data = [final_op, "رفع جماعي", "", "", amt, service, p_provider, m_name]
                    
                    final_rows.append(data)

                # إنشاء الجدول النهائي
                final_df = pd.DataFrame(final_rows)
                
                # عرض معاينة "نظيفة" جداً
                st.markdown("### 📋 معاينة البيانات الجاهزة")
                st.dataframe(final_df, use_container_width=True)

                # زر التحميل
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 تحميل الملف النهائي (جاهز للصق المباشر)",
                    data=output.getvalue(),
                    file_name=f"Fixed_{target_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء المعالجة: {e}")