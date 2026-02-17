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