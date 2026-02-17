import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. التصميم (Minimalist Global UI) ---
st.set_page_config(page_title="Daman Pro Converter", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #2d3436; }
    .header-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-bottom: 3px solid #0984e3; text-align: center; margin-bottom: 30px; }
    .stButton>button { background: #0984e3; color: white; border-radius: 5px; height: 3em; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. التحقق من الهوية ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='header-box'><h1>🔐 نظام ضامن الموحد</h1></div>", unsafe_allow_html=True)
    pwd = st.text_input("Security Key:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    # --- 3. واجهة التحكم ---
    with st.sidebar:
        st.markdown("### ⚙️ الإعدادات")
        target_sheet = st.selectbox("🎯 نوع الشيت المستهدف:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='header-box'><h1>🚀 معالج {target_sheet}</h1></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("ارفع الملف الخام هنا", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # قراءة الداتا الخام
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("⚡ تنفيذ الترتيب النهائي (A1 Start)"):
                final_data_list = []
                
                for _, row in df_in.iterrows():
                    # 1. تجهيز المتغيرات وتنظيف الـ ID
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    final_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')
                    date_val = row.get('تاريخ_الإنشاء', '')

                    # 2. بناء الصف الصافي (الترتيب من العمود A فوراً)
                    # الترتيب بناءً على صورة الكتالوج (image_152763.png)
                    if target_sheet == "Damen's complaint":
                        # [A]مزود | [B]ملاحظات | [C]مرجع | [D]تاريخ | [E]قيمة | [F]ID | [G]خدمة | [H]كود | [I]تاجر | [J]محافظة
                        new_row = [provider, "رفع جماعي", "", date_val, amt, final_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # [A]ملاحظات | [B]مرجع | [C]تاريخ | [D]قيمة | [E]ID | [F]كود | [G]تاجر | [H]محافظة
                        new_row = ["رفع جماعي", "", date_val, amt, final_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # [A]مزود | [B]تاريخ | [C]قيمة | [D]ملاحظات | [E]ID | [F]خدمة
                        new_row = [provider, date_val, amt, "رفع جماعي", final_id, service]
                    
                    else: # Refund Transactions
                        # [A]ID | [B]ملاحظات | [C]مرجع | [D]تاريخ | [E]قيمة | [F]خدمة | [G]مزود | [H]تاجر
                        new_row = [final_id, "رفع جماعي", "", date_val, amt, service, provider, m_name]
                    
                    final_data_list.append(new_row)

                # إنشاء DataFrame جديد تماماً "أبيض يا ورد" بدون أي أعمدة مخفية
                df_final = pd.DataFrame(final_data_list)

                st.success("✅ تم الترتيب بنجاح!")
                # المعاينة للتأكد (يجب أن تبدأ البيانات من العمود 0 فوراً)
                st.table(df_final.head(10))

                # --- 4. التصدير المظبوط ---
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # البدء من A1 (index=False و header=False)
                    df_final.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    # إجبار الاتجاه من الشمال لليمين
                    worksheet.set_right_to_left(False) 
                
                st.download_button("📥 تحميل ملف الـ Paste المباشر", output.getvalue(), f"Ready_{target_sheet}.xlsx")

        except Exception as e:
            st.error(f"⚠️ خطأ في أسماء الأعمدة: {e}")