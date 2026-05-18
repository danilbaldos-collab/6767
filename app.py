import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import time
import re


@st.cache_resource
def download_nltk_data():
    nltk.download('punkt')
    nltk.download('punkt_tab')


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

STRONG_TRIGGERS = {
    "истеричк": 90,
    "бабск": 80,
    "шкур": 90,
    "недотрах": 95,
    "феминаци": 90,
    "кухн": 60,
    "змеин": 80
}

CONTEXT_TRIGGERS = {
    "слаб": 40,
    "женск": 30,
    "логик": 40,
    "настоящ": 30,
    "предназначен": 40,
    "коллектив": 20,
    "украшен": 40,
    "гормон": 40,
    "внешност": 40,
    "должност": 20,
    "эмоциональн": 30
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
    
    # 1. Проверка на точные клише (наивысший приоритет)
    for phrase in EXACT_PHRASES:
        if re.search(phrase, text_lower):
            return 85, "Обнаружено устоявшееся клише. Механизм репродукции: использование гендерно-окрашенной лексики."
            
    tokens = word_tokenize(text_lower, language="russian")
    stemmer = SnowballStemmer("russian")
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    toxicity_score = 0
    detected_stems = []
    
    # 2. Однозначные триггеры (теперь ищет подстроку в корне, чтобы не пропускать слова)
    for stem in stemmed_tokens:
        for key, weight in STRONG_TRIGGERS.items():
            if key in stem:
                toxicity_score += weight
                if key not in detected_stems:
                    detected_stems.append(key)
                
    # 3. Контекстные триггеры
    context_score = 0
    context_stems = []
    for stem in stemmed_tokens:
        for key, weight in CONTEXT_TRIGGERS.items():
            if key in stem:
                context_score += weight
                if key not in context_stems:
                    context_stems.append(key)
                
    # Прибавляем баллы за контекст, ТОЛЬКО если найдено 2 и более подозрительных слова
    if len(context_stems) >= 2:
        toxicity_score += context_score
        detected_stems.extend(context_stems)
        
    # 4. Итоговая классификация
    if toxicity_score >= 80:
        return min(toxicity_score, 98), f"Токсичность: Высокая. Скрытое утверждение о неравенстве (триггеры: {', '.join(set(detected_stems))})."
    elif toxicity_score >= 50:
        return min(toxicity_score, 79), f"Токсичность: Средняя. Сексизм или навязывание стереотипов (триггеры: {', '.join(set(detected_stems))})."
    else:
        return 0, "Токсичность не обнаружена. Текст классифицирован как нейтральный."
