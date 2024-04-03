import os
import re
import nltk
import ssl
import pymorphy3
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

RESOURCES = "resources/task_2"
OUTPUT_TOKENS = "artifacts/task_2/tokens.txt"
OUTPUT_LEMMA_TOKENS = "artifacts/task_2/lemma_tokens.txt"

def extract_unique_filtered_tokens(text):
    tokens = word_tokenize(text, language='russian')
    uniq_filtered_tokens = set()
    stop_words = set(stopwords.words('russian'))

    for token in tokens:
        cleaned = clean_token(token)
        if cleaned and cleaned not in stop_words and len(cleaned) > 1:
            uniq_filtered_tokens.add(cleaned)

    return uniq_filtered_tokens

def handle_lemmas_and_tokens(tokens):
    analyzer = pymorphy3.MorphAnalyzer()
    lemmas = {}

    with open(OUTPUT_TOKENS, 'w', encoding='utf-8') as tokens_file:
        for token in tokens:
            tokens_file.write(token + '\n')
            normal_form = analyzer.parse(token)[0].normal_form

            if normal_form not in lemmas:
                lemmas[normal_form] = []
            lemmas[normal_form].append(token)

    with open(OUTPUT_LEMMA_TOKENS, 'w', encoding='utf-8') as lemma_tokens_file:
        for lemma, tokens_list in lemmas.items():
            lemma_tokens_file.write(f"{lemma} {' '.join(tokens_list)}\n")

def clean_token(token):
    return re.sub("[^а-яА-ЯёЁ]", '', token)

def download():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    nltk.download('punkt')
    nltk.download('stopwords')

def get_text():
    text = ''
    for article in os.listdir(RESOURCES):
        with open(os.path.join(RESOURCES, article), 'r', encoding='utf-8') as file:
            text += file.read().lower() + '\n'
    
    return text

if __name__ == "__main__":
    download()
    text = get_text()
    unique_filtered_tokens = extract_unique_filtered_tokens(text)
    handle_lemmas_and_tokens(unique_filtered_tokens)