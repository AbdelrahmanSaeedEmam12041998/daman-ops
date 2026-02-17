import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة المستخدم (White Professional Theme) ---
st.set_page_config(page_title="Daman Elite Converter", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1f2937; }
    .main-header { font-size: 28px; color: #1e40af; font-weight: bold; text-align: center; padding: 20px; border-bottom: 2px solid #e5e7eb; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 6px; font-weight: 600; width: 100%; height: 3em; }
    .stTable { background-color: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔒 بوابة ضامن للتحويل</div>", unsafe_allow_html=True)
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("❌ خطأ")
else:
    # --- 3. الإعدادات ---
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        target_sheet = st.selectbox("🎯 شيت الوجهة:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])
        if st.button("تسجيل خروج"):
            st.session_state["authenticated"] = False
            st.rerun()

    st.markdown(f"<div class='main-header'>⚡ محول: {target_sheet}</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 ارفع ملف الإكسيل الخام هنا", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # قراءة الملف (بدون التقيد بأي هيكل قديم)
            df_raw = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("🪄 ترتيب واستخراج الملف المظبوط"):
                final_output = []
                for _, row in df_raw.iterrows():
                    # تنظيف رقم العملية
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    damen_id = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    # استخراج الحقول الأساسية
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # --- الترتيب الصارم: أول عنصر = العمود A ---
                    if target_sheet == "Damen's complaint":
                        # A:مزود | B:ملاحظات | C:مرجع | D:تاريخ | E:مبلغ | F:DamenID | G:خدمة | H:كود | I:تاجر | J:محافظة
                        new_row = [provider, "رفع جماعي", "", "", amt, damen_id, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # A:ملاحظات | B:مرجع | C:تاريخ | D:مبلغ | E:DamenID | F:كود | G:تاجر | H:محافظة
                        # لاحظ: رقم العملية DamenID هنا هو العمود الخامس (Index 4) بالظبط.
                        new_row = ["رفع جماعي", "", "", amt, damen_id, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # A:مزود | B:تاريخ | C:مبلغ | D:ملاحظات | E:DamenID | F:خدمة
                        new_row = [provider, "", amt, "رفع جماعي", damen_id, service]
                    
                    else: # Refund Transactions
                        # A:رقم العملية | B:ملاحظات | C:مرجع | D:تاريخ | E:مبلغ | F:خدمة | G:مزود | H:تاجر
                        new_row = [damen_id, "رفع جماعي", "", "", amt, service, provider, m_name]
                    
                    final_output.append(new_row)

                # بناء DataFrame جديد تماماً يضمن انعدام الأعمدة الفارغة
                df_final = pd.DataFrame(final_output)

                st.success("🏁 تمت المعالجة! راجع المعاينة للتأكد من المحاذاة:")
                # استخدام st.table بيوريك الداتا صافية من غير Index (أرقام الجنب)
                st.table(df_final.head(10))

                # التحويل لإكسيل
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # السر هنا: index=False و header=False عشان يبدأ من الخلية A1 مباشرة
                    df_final.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 تحميل الملف النهائي (جاهز للصق)",
                    data=output.getvalue(),
                    file_name=f"Ready_{target_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"⚠️ خطأ: تأكد من عمود 'ID' و 'القيمه_الكليه'. التفاصيل: {e}")