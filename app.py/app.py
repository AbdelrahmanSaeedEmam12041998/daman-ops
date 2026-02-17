import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة مستخدم بمعايير عالمية (Modern White UI) ---
st.set_page_config(page_title="Daman Elite v4", layout="wide")

st.markdown("""
    <style>
    /* تحويل الواجهة لتصميم نظيف وعالمي */
    .stApp { background-color: #ffffff; color: #2d3436; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main-header { font-size: 32px; color: #0984e3; font-weight: 800; text-align: center; padding: 30px 0; border-bottom: 1px solid #dfe6e9; margin-bottom: 40px; }
    .upload-box { border: 2px dashed #0984e3; padding: 40px; border-radius: 15px; text-align: center; background-color: #f1f2f6; }
    .stButton>button { background: linear-gradient(135deg, #0984e3, #6c5ce7); color: white; border: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    /* تنسيق المعاينة */
    .stTable { border: 1px solid #dfe6e9; border-radius: 10px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔐 Daman Data Processor</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Security Key:", type="password")
        if st.button("Enter System"):
            if pwd == "Dispute@Damen.1248#1248*":
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("Invalid Key")
else:
    # --- 3. القائمة الجانبية (شغل احترافي) ---
    with st.sidebar:
        st.markdown("### 🛠️ Control Panel")
        target_sheet = st.selectbox("🎯 Target Sheet Structure:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])
        st.divider()
        st.info("هذا النظام يضمن ترتيب الأعمدة من الشمال لليمين بدون فراغات.")

    st.markdown(f"<div class='main-header'>🚀 {target_sheet} Transformation</div>", unsafe_allow_html=True)

    # --- 4. معالجة البيانات ---
    uploaded_file = st.file_uploader("", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            df_raw = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("Generate Clean File"):
                final_data = []
                for _, row in df_raw.iterrows():
                    # تجهيز المتغيرات
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    damen_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    date_val = row.get('تاريخ_الإنشاء', '')

                    # --- الترتيب الصارم من العمود A بدون فراغات إضافية ---
                    if target_sheet == "Damen's complaint":
                        # A:مزود | B:ملاحظات | C:مرجع | D:تاريخ | E:قيمة | F:DamenID | G:خدمة | H:كود | I:تاجر | J:محافظة
                        row_content = [provider, "رفع جماعي", "", date_val, amt, damen_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # A:ملاحظات | B:مرجع | C:تاريخ | D:قيمة | E:DamenID | F:كود | G:تاجر | H:محافظة
                        # لاحظ: حذفنا العمود الفاضي اللي كان بيعمل ترحيل
                        row_content = ["رفع جماعي", "", date_val, amt, damen_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # A:مزود | B:تاريخ | C:قيمة | D:ملاحظات | E:DamenID | F:خدمة
                        row_content = [provider, date_val, amt, "رفع جماعي", damen_id, service]
                    
                    else: # Refund Transactions
                        # A:ID | B:ملاحظات | C:مرجع | D:تاريخ | E:مبلغ | F:خدمة | G:مزود | H:تاجر
                        row_content = [damen_id, "رفع جماعي", "", date_val, amt, service, provider, m_name]
                    
                    final_data.append(row_content)

                # إنشاء شيت نظيف 100%
                df_final = pd.DataFrame(final_data)
                
                st.markdown("### 📋 Preview (First 10 Rows)")
                st.table(df_final.head(10))

                # التصدير
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # البدء من A1 (index=False, header=False)
                    df_final.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 Download Ready File",
                    data=output.getvalue(),
                    file_name=f"Final_{target_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"Error: {e}")