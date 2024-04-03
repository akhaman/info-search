import os
import requests
import shutil
from bs4 import BeautifulSoup

BASE_URL = "https://habr.com/ru/articles"
ARTIFACTS_DIR = "artifacts/task_1"
PAGES_DIR = f"{ARTIFACTS_DIR}/pages"
OUTPUT_INDEX_PATH = f"{ARTIFACTS_DIR}/index.txt"
OUTPUT_ARCHIVE_PATH = f"{ARTIFACTS_DIR}/выкачка"
PAGES_COUNT = 100

def prepare_directory():
    if os.path.exists(ARTIFACTS_DIR):
        shutil.rmtree(ARTIFACTS_DIR)
    os.makedirs(PAGES_DIR)

def scrape_page(page_url):
    response = requests.get(page_url)
    if response.status_code == 200:
        return response.text
    return None


def parse_page(page_content):
    if page_content:
        soup = BeautifulSoup(page_content, "html.parser")
        for data in soup(['style', 'script', 'link']):
            data.decompose()
        return str(soup)
    return None


def save_page(page_content, page_id):
    if page_content:
        page_filename = f"{PAGES_DIR}/{page_id}.html"
        with open(page_filename, "w", encoding="utf-8") as page_file:
            page_file.write(page_content)


def scrape_and_save_pages(start_id, num_pages):
    print("Scraping started...")
    pages_index = {}
    current_page_id = start_id
    while len(pages_index) < num_pages:
        page_url = f"{BASE_URL}/{current_page_id}"
        page_content = scrape_page(page_url)
        if page_content:
            page_content_parsed = parse_page(page_content)
            if page_content_parsed:
                save_page(page_content_parsed, current_page_id)
                pages_index[current_page_id] = page_url
        current_page_id += 1
        print(f"Progress: Page [{current_page_id}] | Index [{len(pages_index)}/{num_pages}]")
    return pages_index


def create_index_file(pages_index):
    with open(OUTPUT_INDEX_PATH, "w", encoding="utf-8") as index_file:
        content = [f"{key} {pages_index[key]}" for key in pages_index.keys()]
        index_file.write("\n".join(content))
    print("Index file saved.")


def create_archive():
    shutil.make_archive(OUTPUT_ARCHIVE_PATH, 'zip', PAGES_DIR)
    print("Archive created.")

if __name__ == '__main__':
    prepare_directory()
    index = scrape_and_save_pages(start_id=1000, num_pages=PAGES_COUNT)
    create_index_file(index)
    create_archive()
