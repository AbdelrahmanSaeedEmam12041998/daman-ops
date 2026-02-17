import streamlit as st
import pandas as pd
from io import BytesIO

# --- 1. واجهة المستخدم (تنسيق احترافي) ---
st.set_page_config(page_title="Daman Converter Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background: linear-gradient(45deg, #1e3a8a, #3b82f6); color: white; border: none; height: 3em; font-size: 18px; }
    .css-1offfwp { background-color: #1a1c23; } 
    </style>
    """, unsafe_allow_html=True)

# --- 2. نظام الدخول ---
if "authenticated" not in st.session_state: st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🛡️ تسجيل دخول نظام ضامن")
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("دخول"):
        if pwd == "Dispute@Damen.1248#1248*":
            st.session_state["authenticated"] = True
            st.rerun()
        else: st.error("❌ خطأ")
else:
    with st.sidebar:
        st.header("⚙️ الإعدادات")
        target_sheet = st.selectbox("🎯 اختر الشيت المستهدف:", 
                                   ["Damen's complaint", "Cases V.f cash", "Orange cash", 
                                    "Etisalat Cash", "successful Receipt", "Refund Transactions"])

    st.title(f"🚀 معالج بيانات: {target_sheet}")

    uploaded_file = st.file_uploader("📂 ارفع ملف الإكسيل الخام", type=["xlsx", "xls"])

    if uploaded_file:
        try:
            # قراءة الملف الأصلي
            df_in = pd.read_excel(uploaded_file, engine='openpyxl').fillna("")
            
            if st.button("✨ ترتيب واستخراج الملف الآن"):
                final_output_rows = []
                
                for _, row in df_in.iterrows():
                    # تنظيف الداتا وتجهيز Damen ID
                    raw_id = str(row.get('ID', '')).split('.')[0].strip()
                    # إضافة Damen فقط لو مش ريفاند
                    final_op = raw_id if target_sheet == "Refund Transactions" else f"Damen{raw_id}"
                    
                    amt = row.get('القيمه_الكليه', '')
                    m_code = row.get('كود_التاجر', '')
                    m_name = row.get('اسم_التاجر', '')
                    gov = row.get('اسم_المحافظه', '')
                    p_provider = row.get('مزود_الخدمة_الاساسي', '')
                    service = row.get('اسم_الخدمة', '')

                    # --- الترتيب الصارم: أول عنصر في القائمة = أول عمود (A) ---
                    if target_sheet == "Damen's complaint":
                        # [A]مزود | [B]ملاحظات | [C]مرجع | [D]تاريخ | [E]قيمة | [F]DamenID | [G]خدمة | [H]كود | [I]تاجر | [J]محافظة
                        current_row = [p_provider, "رفع جماعي", "", "", amt, final_op, service, m_code, m_name, gov]
                    
                    elif any(x in target_sheet for x in ["V.f", "Orange", "Etisalat"]):
                        # [A]ملاحظات | [B]مرجع | [C]تاريخ | [D]قيمة | [E]DamenID | [F]كود | [G]تاجر | [H]محافظة
                        current_row = ["رفع جماعي", "", "", amt, final_op, m_code, m_name, gov]
                    
                    elif target_sheet == "successful Receipt":
                        # [A]مزود | [B]تاريخ | [C]قيمة | [D]ملاحظات | [E]DamenID | [F]خدمة
                        current_row = [p_provider, "", amt, "رفع جماعي", final_op, service]
                    
                    else: # Refund Transactions
                        # [A]ID_صافي | [B]ملاحظات | [C]مرجع | [D]تاريخ | [E]قيمة | [F]خدمة | [G]مزود | [H]تاجر
                        current_row = [final_op, "رفع جماعي", "", "", amt, service, p_provider, m_name]
                    
                    final_output_rows.append(current_row)

                # إنشاء DataFrame جديد تماماً من القائمة النظيفة
                final_df = pd.DataFrame(final_output_rows)

                st.success("✅ تم الترتيب! عاين البيانات بالأسفل:")
                # عرض الجدول بدون index (الأرقام الجانبية) للتأكد
                st.dataframe(final_df, use_container_width=True)

                # التصدير لإكسيل
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # index=False و header=False يضمنان عدم وجود أعمدة أو صفوف إضافية نهائياً
                    final_df.to_excel(writer, index=False, header=False)
                
                st.download_button(
                    label="📥 تحميل الملف النهائي (جاهز للصق المباشر)",
                    data=output.getvalue(),
                    file_name=f"Fixed_{target_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")