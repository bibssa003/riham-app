import streamlit as st
import google.generativeai as genai
from PIL import Image
import zipfile
import io
import os
import json
from pypdf import PdfReader
import docx
from gtts import gTTS

# 1. إعدادات الصفحة
st.set_page_config(page_title="مساعد الملخصات والحفظ", layout="wide", page_icon="📚")

st.title("📚 تطبيق تلخيص الدروس والمراجعة الذكي")

# 2. القائمة الجانبية لإدخال المفتاح
api_key = st.sidebar.text_input("🔑 أدخل مفتاح Gemini API:", type="password")

if not api_key:
    st.warning("👈 يرجى إدخال مفتاح Gemini API في القائمة الجانبية للبدء.")
    st.stop()

# إعداد المكتبة
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.8-flash')

# 3. اختيار مصدر الدروس
option = st.sidebar.radio(
    "اختر مصدر الدروس:",
    ["📦 رفع ملف (ZIP / PDF / DOCX / TXT / صورة)", "📸 كاميرا / صورة صفحة درس"]
)

prompt_template = """
أنت معلم خبير ومتخصص في تلخيص المناهج وتسهيل الحفظ للطلاب.
قم بتحليل المحتوى المرفق واستخرج:
1. 📝 **ملخص شامل ومكثف للدرس** (النقاط الأساسية والأفكار الجوهرية).
2. 🔑 **المفاهيم والمصطلحات الرئيسية للحفظ** (تعاريف مبسطة ومباشرة).
3. 🧠 **بطاقات مراجعة سريعة (Flashcards)**: 3 إلى 5 أسئلة مع أجوبتها النموذجية للاختبار الذاتي.
"""

mcq_prompt_template = """
أنت معلم خبير. بناءً على النص أو المحتوى المرفق، قم بإنشاء 3 إلى 5 أسئلة اختيار من متعدد (MCQ) لاختبار فهم الطالب.
يجب أن ترجع الإجابة فقط بتنسيق JSON صحيح وقابل للتحليل عبر json.loads وبدون أي نصوص إضافية قبله أو بعده، بالتنسيق التالية:
[
  {
    "question": "السؤال هنا؟",
    "options": ["الخيار 1", "الخيار 2", "الخيار 3", "الخيار 4"],
    "correct_index": 0
  }
]
"""

def extract_text_from_docx(stream):
    """دالة لاستخراج النصوص من ملفات Word (.docx)"""
    doc = docx.Document(stream)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def create_docx_download(text_content):
    """دالة إنشاء ملف Word جاهز للتحميل"""
    doc = docx.Document()
    doc.add_heading("ملخص الدرس - تطبيق المراجعة الذكي", level=1)
    for line in text_content.split('\n'):
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def text_to_speech_audio(text_content):
    """دالة تحويل النص إلى صوت MP3"""
    clean_text = text_content.replace('*', '').replace('#', '')
    tts = gTTS(text=clean_text[:1000], lang='ar')  # تحويل أول 1000 حرف لحجم مناسب
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def render_study_tools(content_input, is_image=False):
    """عرض أدوات الحفظ والتفاعل (التلخيص، الصوت، Word، كويز MCQ)"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ تلخيص هذا الدرس", key="btn_summary"):
            with st.spinner("جاري التلخيص..."):
                try:
                    res = model.generate_content([prompt_template, content_input])
                    st.session_state['summary_text'] = res.text
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التلخيص: {e}")

    with col2:
        if st.button("🧪 توليد اختبار MCQ تفاعلي", key="btn_mcq"):
            with st.spinner("جاري إنشاء الأسئلة..."):
                try:
                    res = model.generate_content([mcq_prompt_template, content_input])
                    clean_json = res.text.strip().replace("```json", "").replace("```", "")
                    st.session_state['mcq_data'] = json.loads(clean_json)
                    st.session_state['user_answers'] = {}
                except Exception as e:
                    st.error(f"حدث خطأ أثناء إنشاء الاختبار: {e}")

    # عرض الملخص والصوت والتصدير عند توفره
    if 'summary_text' in st.session_state:
        st.markdown("---")
        st.subheader("📝 الملخص ونقاط الحفظ:")
        st.markdown(st.session_state['summary_text'])
        
        c_audio, c_doc = st.columns(2)
        with c_audio:
            if st.button("🔊 الاستماع للملخص صوتیّاً"):
                with st.spinner("جاري تجهيز المقطع الصوتي..."):
                    audio_bytes = text_to_speech_audio(st.session_state['summary_text'])
                    st.audio(audio_bytes, format='audio/mp3')
        
        with c_doc:
            docx_bytes = create_docx_download(st.session_state['summary_text'])
            st.download_button(
                label="📥 تحميل الملخص بصيغة Word (.docx)",
                data=docx_bytes,
                file_name="ملخص_الدرس.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    # عرض الاختبار التفاعلي MCQ
    if 'mcq_data' in st.session_state:
        st.markdown("---")
        st.subheader("🧪 اختبار تفاعلي سريع (MCQ)")
        
        mcqs = st.session_state['mcq_data']
        score = 0
        submitted = st.button("✅ تصحيح الاختبار")

        for idx, q in enumerate(mcqs):
            st.markdown(f"**س{idx+1}: {q['question']}**")
            user_choice = st.radio(
                "اختر الإجابة الصحيحة:", 
                q['options'], 
                key=f"mcq_{idx}"
            )
            selected_idx = q['options'].index(user_choice)
            
            if submitted:
                if selected_idx == q['correct_index']:
                    st.success("إجابة صحيحة! 👏")
                    score += 1
                else:
                    correct_text = q['options'][q['correct_index']]
                    st.error(f"إجابة خاطئة. الإجابة الصحيحة هي: {correct_text}")
            st.write("")

        if submitted:
            st.info(f"🏆 النتيجة النهائية: {score} من {len(mcqs)}")

# -------------------------------------------------------------------
# الخيار الأول: رفع ملفات المناهج والدروس
# -------------------------------------------------------------------
if option == "📦 رفع ملف (ZIP / PDF / DOCX / TXT / صورة)":
    st.subheader("رفع ملخصات ودروس (ZIP / PDF / DOCX / TXT / صور)")
    uploaded_file = st.file_uploader(
        "اختر ملف الدرس:", 
        type=["zip", "pdf", "docx", "txt", "png", "jpg", "jpeg", "webp"]
    )
    
    if uploaded_file:
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_ext == ".zip":
            with zipfile.ZipFile(uploaded_file, 'r') as z:
                file_list = [f for f in z.namelist() if not f.startswith('__MACOSX') and not f.endswith('/')]
                st.success(f"📦 تم العثور على {len(file_list)} ملف داخل الـ ZIP.")
                selected_inside = st.selectbox("اختر الدرس الذي تريد تلخيصه:", file_list)
                
                if selected_inside:
                    sub_ext = os.path.splitext(selected_inside)[1].lower()
                    file_bytes = z.read(selected_inside)
                    
                    if sub_ext == '.pdf':
                        reader = PdfReader(io.BytesIO(file_bytes))
                        text_content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                        render_study_tools(text_content)
                    elif sub_ext == '.docx':
                        text_content = extract_text_from_docx(io.BytesIO(file_bytes))
                        render_study_tools(text_content)
                    elif sub_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                        st.image(image, caption=selected_inside, use_container_width=True)
                        render_study_tools(image, is_image=True)
                    elif sub_ext in ['.txt', '.md']:
                        text_content = file_bytes.decode('utf-8', errors='ignore')
                        render_study_tools(text_content)

        elif file_ext == ".pdf":
            reader = PdfReader(uploaded_file)
            text_content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            render_study_tools(text_content)

        elif file_ext == ".docx":
            text_content = extract_text_from_docx(uploaded_file)
            render_study_tools(text_content)

        elif file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption=uploaded_file.name, use_container_width=True)
            render_study_tools(image, is_image=True)

        elif file_ext in [".txt", ".md"]:
            text_content = uploaded_file.read().decode('utf-8', errors='ignore')
            render_study_tools(text_content)

# -------------------------------------------------------------------
# الخيار الثاني: الكاميرا أو رفع صورة
# -------------------------------------------------------------------
else:
    st.subheader("📸 مسح درس جديد (كاميرا / صورة)")
    source = st.radio("اختر الطريقة:", ["الكاميرا المباشرة", "رفع صورة من الجهاز"])
    img_file = st.camera_input("التقط صورة لصفحة الدرس") if source == "الكاميرا المباشرة" else st.file_uploader("اختر صورة الدرس:", type=["jpg", "jpeg", "png", "webp"])
        
    if img_file:
        image = Image.open(img_file).convert("RGB")
        st.image(image, caption="الصفحة المحددة", use_container_width=True)
        render_study_tools(image, is_image=True)