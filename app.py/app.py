import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. تصميم واجهة نظيفة وعالمية ---
st.set_page_config(page_title="Daman Logic Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #333; }
    .main-header { font-size: 28px; color: #1e40af; font-weight: bold; text-align: center; padding: 20px; border-bottom: 2px solid #f3f4f6; }
    .stButton>button { background-color: #2563eb; color: white; width: 100%; border-radius: 8px; font-weight: bold; height: 3em; border: none; }
    </style>
    """, unsafe_allow_html=True)

if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔒 دخول نظام ضامن</div>", unsafe_allow_html=True)
    pwd = st.text_input("Security Key:", type="password")
    if st.button("Log In"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("❌ خطأ")
else:
    with st.sidebar:
        target_sheet = st.selectbox("🎯 اختر نوع الشيت المطلوب:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='main-header'>🚀 معالجة {target_sheet}</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف الخام الذي يحتوي على البيانات")

    if uploaded_file:
        try:
            df_raw = pd.read_excel(uploaded_file).fillna("")
            
            if st.button("ابدأ الترتيب الصارم"):
                final_rows = []
                for _, row in df_raw.iterrows():
                    # 1. استخراج وتنظيف الداتا
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    f_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    prov = row.get('مزود_الخدمة_الاساسي', '')
                    serv = row.get('اسم_الخدمة', '')
                    date = row.get('تاريخ_الإنشاء', '')

                    # 2. بناء الصف بناءً على ترتيب ملف Sheets.xlsx
                    if target_sheet == "Damen's complaint":
                        #: مزود | معلومات | مرجع | تاريخ | قيمة | رقم عملية | خدمة | كود | تاجر | محافظة
                        line = [prov, "رفع جماعي", "", date, amt, f_id, serv, m_code, m_name, gov]
                    
                    elif target_sheet in ["Cases V.f cash", "Orange cash", "Etisalat Cash"]:
                        #: معلومات | مرجع | تاريخ | قيمة | رقم عملية | كود | تاجر | محافظة
                        line = ["رفع جماعي", "", date, amt, f_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        #: مزود | تاريخ | قيمة | معلومات | رقم عملية | خدمة
                        line = [prov, date, amt, "رفع جماعي", f_id, serv]
                    
                    else: # Refund Transactions (Reconciliation)
                        #: رقم عملية | معلومات | مرجع | تاريخ | قيمة | خدمة | مزود | تاجر
                        line = [f_id, "رفع جماعي", "", date, amt, serv, prov, m_name]
                    
                    final_rows.append(line)

                # إنشاء شيت جديد تماماً بدون Header أو Index
                df_final = pd.DataFrame(final_rows)
                
                st.write("📋 معاينة الداتا (تبدأ من أول عمود على الشمال A):")
                st.table(df_final.head(10))

                # التصدير الصحيح (LTR)
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
                    writer.sheets['Sheet1'].set_right_to_left(False) # اتجاه شمال ليمين
                
                st.download_button("📥 تحميل الملف المظبوط", output.getvalue(), f"{target_sheet}.xlsx")
        except Exception as e:
            st.error(f"⚠️ حدث خطأ: {e}")