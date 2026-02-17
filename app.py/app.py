import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة مستخدم احترافية تفتح النفس ---
st.set_page_config(page_title="Daman Elite Converter", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e0e0e0; }
    .main-title { font-size: 32px; color: #4dabf7; font-weight: bold; text-align: center; padding: 20px; }
    .stButton>button { background: linear-gradient(90deg, #1c7ed6, #22b8cf); color: white; border: none; padding: 10px 24px; border-radius: 8px; font-weight: bold; }
    .stDataFrame { border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. الحماية ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-title'>🔐 نظام ضامن الموحد</div>", unsafe_allow_html=True)
    pwd = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    # --- 3. الإعدادات ---
    with st.sidebar:
        st.header("⚙️ خيارات التصدير")
        target_sheet = st.selectbox("🎯 اختر شيت الوجهة:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.markdown(f"<div class='main-title'>⚡ معالج بيانات {target_sheet}</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 ارفع ملف الإكسيل الخام هنا", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # قراءة الداتا وتجهيزها
            df_raw = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("🪄 ترتيب الداتا وإزالة الفراغات"):
                final_list = []
                for _, row in df_raw.iterrows():
                    # تنظيف رقم العملية (الـ ID)
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    damen_id = f"Damen{raw_id}" if target_sheet != "Refund Transactions" else raw_id
                    
                    # استخراج الحقول
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # --- الترتيب الصارم: يبدأ من العمود A (بدون أي فراغات) ---
                    if target_sheet == "Damen's complaint":
                        # A:مزود | B:ملاحظات | C:مرجع | D:تاريخ | E:مبلغ | F:DamenID | G:خدمة | H:كود | I:تاجر | J:محافظة
                        new_row = [provider, "رفع جماعي", "", "", amt, damen_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # A:ملاحظات | B:مرجع | C:تاريخ | D:مبلغ | E:DamenID | F:كود | G:تاجر | H:محافظة
                        new_row = ["رفع جماعي", "", "", amt, damen_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # A:مزود | B:تاريخ | C:مبلغ | D:ملاحظات | E:DamenID | F:خدمة
                        new_row = [provider, "", amt, "رفع جماعي", damen_id, service]
                    
                    else: # Refund
                        # A:ID | B:ملاحظات | C:مرجع | D:تاريخ | E:مبلغ | F:خدمة | G:مزود | H:تاجر
                        new_row = [damen_id, "رفع جماعي", "", "", amt, service, provider, m_name]
                    
                    final_list.append(new_row)

                # إنشاء DataFrame جديد تماماً يقتل أي "أشباح" لأعمدة قديمة
                df_final = pd.DataFrame(final_list)

                st.success("🏁 تمت المعالجة! إليك المعاينة الصافية:")
                # المعاينة بدون أرقام الجنب المزعجة
                st.table(df_final.head(10))

                # تحويل لإكسيل
                output = BytesIO()
                with pd.ExcelWriter