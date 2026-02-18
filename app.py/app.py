import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة مستخدم بيضاء (Clean & Modern) ---
st.set_page_config(page_title="Daman OMS Processor", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2d3436; }
    .main-header { font-size: 30px; color: #0984e3; font-weight: 800; text-align: center; padding: 20px; border-bottom: 2px solid #dfe6e9; }
    .stButton>button { background: #0984e3; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔒 دخول نظام ضامن (OMS Tool)</div>", unsafe_allow_html=True)
    pwd = st.text_input("Security Key:", type="password")
    if st.button("Log In"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ خيارات التصدير")
        target_sheet = st.selectbox("🎯 اختر نوع الشيت المطلوب:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='main-header'>⚡ محول تقارير OMS إلى: {target_sheet}</div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("ارفع ملف تقرير المعاملات (OMS)", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            # قراءة الملف (سواء CSV أو Excel)
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file).fillna("")
            else:
                df_raw = pd.read_excel(uploaded_file).fillna("")
            
            if st.button("🚀 استخراج البيانات بالترتيب المعتمد"):
                final_rows = []
                
                for _, row in df_raw.iterrows():
                    # سحب البيانات من أعمدة الـ OMS الحقيقية
                    oms_id = str(row.get('ID', '')).split('.')[0].strip()
                    f_id = oms_id if target_sheet == "Refund Transactions" else f"Damen{oms_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    prov = row.get('مزود_الخدمة_الاساسي', '')
                    serv = row.get('اسم_الخدمة', '')
                    # تنسيق التاريخ ليظهر بشكل نظيف
                    date_val = str(row.get('تاريخ_الانشاء', '')).split(',')[0] 

                    # --- الترتيب الصارم بناءً على الكتالوج (من الشمال لليمين) ---
                    if target_sheet == "Damen's complaint":
                        # مزود | معلومات | مرجع | تاريخ | قيمة | رقم عملية | خدمة | كود | تاجر | محافظة
                        line = [prov, "رفع جماعي", "", date_val, amt, f_id, serv, m_code, m_name, gov]
                    
                    elif target_sheet in ["Cases V.f cash", "Orange cash", "Etisalat Cash"]:
                        # معلومات | مرجع | تاريخ | قيمة | رقم عملية | كود | تاجر | محافظة
                        line = ["رفع جماعي", "", date_val, amt, f_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # مزود | تاريخ | قيمة | معلومات | رقم عملية | خدمة
                        line = [prov, date_val, amt, "رفع جماعي", f_id, serv]
                    
                    else: # Refund Transactions
                        # رقم عملية | معلومات | مرجع | تاريخ | قيمة | خدمة | مزود | تاجر
                        line = [f_id, "رفع جماعي", "", date_val, amt, serv, prov, m_name]
                    
                    final_rows.append(line)

                df_final = pd.DataFrame(final_rows)

                st.write("📋 معاينة البيانات الخارجة (تبدأ من العمود A فوراً):")
                st.table(df_final.head(10))

                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Result')
                    # ضبط الاتجاه ليكون من الشمال لليمين
                    writer.sheets['Result'].set_right_to_left(False)
                
                st.download_button("📥 تحميل الملف الجاهز للصق", output.getvalue(), f"{target_sheet}.xlsx")
        except Exception as e:
            st.error(f"⚠️ تأكد من رفع ملف OMS الصحيح. خطأ: {e}")