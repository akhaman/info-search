import math
import json
import pymorphy3
import zipfile
import re
import os
import shutil
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

parser = 'html.parser'
morph = pymorphy3.MorphAnalyzer()
ZIP_FILE_PATH = "artifacts/task_1/выкачка.zip"
INVERTED_INDEX_FILE = 'artifacts/task_3/inverted_index.json'
ARTIFACTS_DIR = 'artifacts/task_4/'
TOKENS_TFIDF_DIR = ARTIFACTS_DIR + 'tokens_tfidf/'
LEMMAS_TFIDF_DIR = ARTIFACTS_DIR + 'lemmas_tfidf/'


def extract_unique_filtered_tokens(tokens):
    res = []
    for token in tokens:
        if token.lower() not in stopwords.words("russian") and re.compile("^[а-яё]+$").match(token.lower()):
            res.append(token.lower())
    return set(res)


def list_extract_unique_filtered_tokens(tokens):
    res = []
    for token in tokens:
        if token.lower() not in stopwords.words("russian") and re.compile("^[а-яё]+$").match(token.lower()):
            res.append(token.lower())
    return list(res)


def tokenize_text(text):
    tokens = word_tokenize(text.replace('.', ' '))
    return extract_unique_filtered_tokens(tokens)


def create_inverted_index_tokens(zip_f):
    index = {}

    for i, file in enumerate(zip_f.filelist):
        content = zip_f.open(file)
        text = BeautifulSoup(content, parser).get_text()
        tokens = set(tokenize_text(text))

        for token in tokens:
            if token in index:
                index[token].add(i)
            else:
                index[token] = {i}
    return index


def save_inverted_index(filename, ind):
    inverted_index_file = open(filename, "a", encoding='utf-8')
    for i in ind:
        inverted_index_file.write(i + ": " + " ".join(map(lambda file_number: str(file_number), ind[i])) + "\n")
    inverted_index_file.close()


def get_token_list(text):
    tokens = word_tokenize(text.replace('.', ' '))
    return list_extract_unique_filtered_tokens(tokens)


def read_index(index_file_path):
    with open(INVERTED_INDEX_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def calculate_tf(q, tokens):
    return tokens.count(q) / float(len(tokens))


def calculate_idf(q, index, docs_count=100):
    return math.log(docs_count / float(len(index[q])))


def lemmatize_word(word):
    return morph.parse(word.replace("\n", ""))[0].normal_form


def calculate_tfidf(zip_f, lemmas_index, tokens_index):
    for i, file in enumerate(zip_file.filelist):
        content = zip_f.open(file)
        text = BeautifulSoup(content, parser).get_text()

        tokens = get_token_list(text)
        lemmas = list(map(lemmatize_word, tokens))

        res_tokens = []
        for token in set(tokens):
            if token in tokens_index:
                tf = calculate_tf(token, tokens)
                idf = calculate_idf(token, tokens_index)
                res_tokens.append(f"{token} {idf} {tf * idf}")

        with open(f"{TOKENS_TFIDF_DIR}{file.filename}.txt", "w", encoding='utf-8') as token_f:
            token_f.write("\n".join(res_tokens))

        res_lemmas = []
        for lemma in set(lemmas):
            if lemma in lemmas_index:
                tf = calculate_tf(lemma, lemmas)
                idf = calculate_idf(lemma, lemmas_index)
                res_lemmas.append(f"{lemma} {idf} {tf * idf}")

        with open(f"{LEMMAS_TFIDF_DIR}{file.filename}.txt", "w", encoding='utf-8') as lemma_f:
            lemma_f.write("\n".join(res_lemmas))

def prepare_folders():
    if os.path.exists(ARTIFACTS_DIR):
        shutil.rmtree(ARTIFACTS_DIR)
    os.makedirs(TOKENS_TFIDF_DIR)
    os.makedirs(LEMMAS_TFIDF_DIR)

if __name__ == '__main__':
    prepare_folders()
    zip_file = zipfile.ZipFile(ZIP_FILE_PATH, "r")

    lemmas_index_path = INVERTED_INDEX_FILE
    tokens_index_path = "inverted_index_tokens.txt"

    inverted_index_tokens = create_inverted_index_tokens(zip_file)
    save_inverted_index(tokens_index_path, inverted_index_tokens)

    read_inverted_index = read_index(lemmas_index_path)
    read_inverted_index_tokens = read_index(tokens_index_path)

    calculate_tfidf(zip_file, read_inverted_index, read_inverted_index_tokens)