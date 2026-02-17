import streamlit as st
import pandas as pd
from io import BytesIO

# إعدادات الواجهة (أبيض عالمي)
st.set_page_config(page_title="Daman Final Fix", layout="wide")

if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.title("🛡️ نظام ضامن")
    pwd = st.text_input("Password:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
else:
    target_sheet = st.sidebar.selectbox("🎯 الشيت:", ["Damen's complaint", "Cases V.f cash", "Orange cash", "Etisalat Cash", "successful Receipt", "Refund Transactions"])
    
    uploaded_file = st.file_uploader("ارفع الملف الخام")

    if uploaded_file:
        df_in = pd.read_excel(uploaded_file).fillna("")
        
        if st.button("🚀 ترتيب نهائي"):
            res = []
            for _, row in df_in.iterrows():
                # تجهيز البيانات
                raw_id = str(row.get('ID', '')).split('.')[0].strip()
                f_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                amt = row.get('القيمه_الكليه', '')
                m_code = row.get('كود_التاجر', '')
                m_name = row.get('اسم_التاجر', '')
                gov = row.get('اسم_المحافظه', '')
                prov = row.get('مزود_الخدمة_الاساسي', '')
                serv = row.get('اسم_الخدمة', '')
                date = row.get('تاريخ_الإنشاء', '')

                # الترتيب من العمود A (رقم 0) بدون أي فراغات
                if target_sheet == "Damen's complaint":
                    line = [prov, "رفع جماعي", "", date, amt, f_id, serv, m_code, m_name, gov]
                elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                    # ملاحظات(A) | مرجع(B) | تاريخ(C) | مبلغ(D) | رقم عملية(E) | كود(F) | تاجر(G) | محافظة(H)
                    line = ["رفع جماعي", "", date, amt, f_id, m_code, m_name, gov]
                elif target_sheet == "successful Receipt":
                    line = [prov, date, amt, "رفع جماعي", f_id, serv]
                else: # Refund
                    line = [f_id, "رفع جماعي", "", date, amt, serv, prov, m_name]
                
                res.append(line)

            df_out = pd.DataFrame(res)
            
            # عرض الجدول "كما هو" في الإكسيل
            st.write("📋 المعاينة (تأكد أن البيانات تبدأ من أول عمود):")
            st.table(df_out.head(10)) 

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # index=False يمنع إضافة عمود أرقام في الأول
                # header=False يمنع إضافة صف أسماء في الأول
                df_out.to_excel(writer, index=False, header=False, sheet_name='Sheet1')
                writer.sheets['Sheet1'].set_right_to_left(False) # الاتجاه من الشمال
            
            st.download_button("📥 تحميل الملف المظبوط", output.getvalue(), "Final.xlsx")