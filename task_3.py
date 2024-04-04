import json
import os
import shutil
import re
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
from pyeda.boolalg.expr import exprvar, OrOp, AndOp, Complement, Variable, expr

PAGES_DIR = 'artifacts/task_1/pages/'
TOKENS_FILE = open('artifacts/task_2/tokens.txt', encoding='utf-8')
ARTIFACTS_DIR = 'artifacts/task_3'
OUTPUT = 'artifacts/task_3/inverted_index.json'

expression_variables = {}
document_locations = set()

def create_index():
    filenames = listdir(PAGES_DIR)
    filenames.sort(key=lambda x: int(x.replace('.html', '')))

    texts = [BeautifulSoup(open(PAGES_DIR + f, encoding='utf-8').read(), 'html.parser').
             get_text().lower() for f in filenames if isfile(join(PAGES_DIR, f))]

    inverted_index = {}
    for token in TOKENS_FILE.read().splitlines():
        for i, text in enumerate(texts):
            if token in text:
                if token not in inverted_index:
                    inverted_index[token] = set()
                inverted_index[token].add(filenames[i])

    for key in inverted_index.keys():
        inverted_index[key] = list(inverted_index[key])
    json_inverted_index = json.dumps(inverted_index, ensure_ascii=False)
    with open(OUTPUT, 'w+', encoding='utf-8') as index_file:
        index_file.write(json_inverted_index)

    
def prepare_folders():
    if os.path.exists(ARTIFACTS_DIR):
        shutil.rmtree(ARTIFACTS_DIR)
    os.makedirs(ARTIFACTS_DIR)

def load_index():
    with open(OUTPUT, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def map_query(expression):
    words = re.findall(r'[a-zA-Z]+', expression)
    latin_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    variables_map = {}
    result = expression

    for i, word in enumerate(words):
        if i < len(latin_alphabet):
            variables_map[latin_alphabet[i]] = word
            result = result.replace(word, latin_alphabet[i])

    return result, variables_map

def search_boolean(expression, variables_map, inverted_index):
    global document_locations, expression_variables
    document_locations = {location for locations in inverted_index.values() for location in locations}
    expression_variables = variables_map

    simplified_expr = simplify(expression)
    result_set = process_expression(simplified_expr)

    if (len(result_set) > 0):
        print(f"Found {len(result_set)} documents: {result_set}")
    else:
        print("No documents found")

def simplify(expression):
    return expression.simplify()

def process_expression(expression):
    if type(expression) is Complement:
        return document_locations.difference(find_word(str(expression)[1::]))
    elif type(expression) is OrOp:
        return set().union(*[process_expression(child) for child in expression.xs])
    elif type(expression) is AndOp:
        result_set = document_locations
        for child in expression.xs:
            result_set = result_set.intersection(process_expression(child))
        return result_set
    elif type(expression) is Variable:
        return find_word(str(expression))
    else:
        return set()

def find_word(word):
    locations = inverted_index.get(expression_variables.get(word))
    if locations is None:
        return set()
    return locations

if __name__ == "__main__":
    prepare_folders()
    create_index()

    inverted_index = load_index()

    while True:
        user_input = input("Enter search query:\n")
        if user_input.lower() == 'exit':
            exit()

        expression, variables_map = map_query(user_input.lower())
        try:
            result_expression = expr(expression)
            search_boolean(result_expression, variables_map, inverted_index)
        except:
            print("Invalid input. Please try again")