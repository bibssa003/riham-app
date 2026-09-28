import streamlit as st
from PIL import Image
import io

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="RIHAM - مساعد الملخصات الذكي",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. تحسين المظهر والتنسيق يدعم اللغة العربية (RTL)
st.markdown("""
    <style>
    /* ضبط اتجاه الصفحة من اليمين إلى اليسار */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-title {
        color: #0d6efd;
        text-align: center;
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 3. الهيدر والعنوان
st.markdown("<h1 class='main-title'>RIHAM 📚</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>مساعد الملخصات الذكي</p>", unsafe_allow_html=True)

st.divider()

st.subheader("مسح درس جديد 📸")

# 4. اختيار طريقة التقاط/رفع الصورة
method = st.radio(
    "اختر الطريقة:",
    ["رفع أو التقاط صورة (موصى به للتطبيق)", "الكاميرا المباشرة"],
    index=0
)

image_file = None

if method == "رفع أو التقاط صورة (موصى به للتطبيق)":
    st.info("💡 عند الضغط بالأسفل من الهاتف، يمكنك التقاط صورة فورية بكاميرا الهاتف أو اختيار صورة من المعرض.")
    uploaded_file = st.file_uploader(
        "التقط صورة لصفحة الدرس أو اخترها من الجهاز:",
        type=["jpg", "jpeg", "png", "webp"]
    )
    if uploaded_file is not None:
        image_file = uploaded_file

else:
    st.warning("⚠️ الكاميرا المباشرة قد تتطلب فتح التطبيق عبر متصفح عادي مثل Chrome.")
    camera_file = st.camera_input("التقط صورة لصفحة الدرس")
    if camera_file is not None:
        image_file = camera_file

# 5. عرض الصورة المعالجة وإجراء التلخيص
if image_file is not None:
    st.success("تم استلام صورة الدرس بنجاح! ✅")
    
    # عرض معاينة للصورة
    image = Image.open(image_file)
    st.image(image, caption="صورة الدرس", use_column_width=True)
    
    st.divider()
    
    # زر بدء التلخيص بالذكاء الاصطناعي
    if st.button("🚀 تلخيص الدرس الآن", use_container_width=True):
        with st.spinner("جاري قراءة وتلخيص الدرس بواسطة الذكاء الاصطناعي... ⏳"):
            
            # --- هنا يمكنك ربط كود Gemini API أو نموذج التلخيص الخاص بك ---
            
            st.markdown("### 📝 ملخص الدرس:")
            st.success("""
            **1. المفهوم الرئيسي:**
            هذا المفهوم يعبر عن النقاط الأساسية المستخرجة من صفحة الدرس.
            
            **2. أهم النقاط والمعادلات:**
            - النقطة الأولى المهمة في الدرس.
            - النقطة الثانية والملاحظات المتعلقة بها.
            
            **3. الخلاصة:**
            ملخص سريع يسهل حفظه واستذكاره قبل الاختبارات.
            """)
            
            # زر تحميل الملخص
            st.download_button(
                label="📥 تحميل الملخص كملف نصي",
                data="ملخص الدرس من تطبيق RIHAM",
                file_name="lesson_summary.txt",
                mime="text/plain",
                use_container_width=True
            )
