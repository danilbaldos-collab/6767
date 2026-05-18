import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import time
import re


@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')


download_nltk_data()

st.set_page_config(page_title="Анализатор текста", layout="centered")

st.markdown("""
    <style>
    .main {background-color: #f9f9f9;}
    h1 {color: #333333; font-family: 'Helvetica Neue', sans-serif;}
    .stButton>button {background-color: #e5b3c3; color: white; border-radius: 5px; border: none;}
    .stButton>button:hover {background-color: #d497aa; color: white;}
    </style>
    """, unsafe_allow_html=True)

st.title("Анализатор скрытых стереотипов")
st.write(
    "Введите текст, комментарий или отрывок статьи, чтобы проверить его на наличие гендерных предрассудков и токсичности.")

STEREOTYPE_DICT = {
    "змеин": 0.8,
    "клубок": 0.5,
    "слаб": 0.4,
    "пол": 0.3,
    "истеричк": 0.9,
    "гормон": 0.7,
    "женск": 0.3,
    "логик": 0.5,
    "украшен": 0.8,
    "коллектив": 0.2,
    "настоящ": 0.4,
    "предназначен": 0.8
}

EXACT_PHRASES = [
    r"змеиный клубок",
    r"женская логика",
    r"слабый пол",
    r"настоящая женщина",
    r"украшение коллектива",
    r"место на кухне"
]


def analyze_text(text):
    text_lower = text.lower()

    for phrase in EXACT_PHRASES:
        if re.search(phrase, text_lower):
            return 85, "Обнаружено устоявшееся клише. Механизм репродукции: использование гендерно-окрашенной лексики."

    tokens = word_tokenize(text_lower, language="russian")
    stemmer = SnowballStemmer("russian")
    stemmed_tokens = [stemmer.stem(token) for token in tokens]

    toxicity_score = 0
    detected_stems = []

    for stem in stemmed_tokens:
        for key, weight in STEREOTYPE_DICT.items():
            if key in stem:
                toxicity_score += weight * 100
                detected_stems.append(key)

    if toxicity_score >= 80:
        return min(toxicity_score,
                   98), f"Токсичность: Высокая. Скрытое утверждение о профессиональном неравенстве (триггеры: {', '.join(set(detected_stems))})."
    elif toxicity_score >= 40:
        return toxicity_score, "Токсичность: Средняя. Доброжелательный сексизм или навязывание гендерных ролей."
    else:
        return 0, "Токсичность не обнаружена. Текст классифицирован как нейтральный или позитивный."


user_input = st.text_area("Текст для анализа:", height=150,
                          placeholder="Например: Женский коллектив — это всегда змеиный клубок...")

if st.button("Проверить текст"):
    if user_input.strip() == "":
        st.warning("Пожалуйста, введите текст для анализа.")
    else:
        with st.spinner('Алгоритм NLP анализирует семантику...'):
            time.sleep(1.5)

            score, verdict = analyze_text(user_input)

            st.markdown("### Результат анализа:")

            if score > 70:
                st.error(f"Уровень токсичности/стереотипизации: {int(score)}%")
                st.write(verdict)
            elif score > 0:
                st.warning(f"Уровень токсичности/стереотипизации: {int(score)}%")
                st.write(verdict)
            else:
                st.success("Уровень токсичности: 0%")
                st.write(verdict)