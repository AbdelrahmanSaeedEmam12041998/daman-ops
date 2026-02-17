import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة المستخدم العالمية (تصميم مودرن) ---
st.set_page_config(page_title="Daman Pro Converter", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 20px; background: linear-gradient(45deg, #007bff, #00d4ff); color: white; font-weight: bold; border: none; }
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ نظام ضامن - تسجيل الدخول")
    pwd = st.text_input("أدخل كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("❌ كلمة المرور خطأ")
else:
    # --- 3. الإعدادات الجانبية ---
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        target_sheet = st.selectbox("🎯 اختر نوع الشيت:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])
        st.success(f"الوضع الحالي: {target_sheet}")

    st.title(f"🚀 محول بيانات {target_sheet}")
    st.write("ارفع ملف الإكسيل وهيتم ترتيبه فوراً بدون أي أعمدة فاضية.")

    # --- 4. معالجة الملف ---
    uploaded_file = st.file_uploader("📂 اسحب الملف هنا", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # قراءة الملف الأصلي
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("✨ تنفيذ الترتيب السحري"):
                new_data = []
                for _, row in df_in.iterrows():
                    # تجهيز البيانات الأساسية
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # --- الترتيب الصارم بناءً على الصورة (بدون أي مسافات في البداية) ---
                    if target_sheet == "Damen's complaint":
                        # يبدأ من أول خلية A1: مزود | ملاحظات | مرجع | تاريخ | قيمة | رقم عملية | خدمة | كود | تاجر | محافظة
                        row_list = [p_provider, "رفع جماعي", "", "", amt, final_op, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # يبدأ من A1: ملاحظات | مرجع | تاريخ | قيمة | رقم عملية | كود | تاجر | محافظة
                        row_list = ["رفع جماعي", "", "", amt, final_op, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # يبدأ من A1: مزود | تاريخ | قيمة | ملاحظات | رقم عملية | خدمة
                        row_list = [p_provider, "", amt, "رفع جماعي", final_op, service]
                    
                    else: # Refund Transactions
                        # يبدأ من A1: رقم عملية | ملاحظات | مرجع | تاريخ | قيمة | خدمة | مزود | تاجر
                        row_list = [final_op, "رفع جماعي", "", "", amt, service, p_provider, m_name]
                    
                    new_data.append(row_list)

                # إنشاء الـ DataFrame الجديد (بدون أسماء أعمدة وبدون Index)
                final_df = pd.DataFrame(new_data)
                
                st.subheader("📋 المعاينة النهائية (جاهز للصق)")
                st.table(final_df.head(10)) # استخدام st.table بيشيل أرقام الصفوف المزعجة

                # التصدير لإكسيل
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # header=False (عشان ميبقاش فيه صف عناوين)
                    # index=False (عشان ميبقاش فيه عمود أرقام صفوف في الأول)
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 تحميل الملف النهائي (بدون أعمدة فارغة)",
                    data=output.getvalue(),
                    file_name=f"Ready_{target_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")