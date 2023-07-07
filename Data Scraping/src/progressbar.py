import concurrent.futures
import json
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from manga import Manga

class MangaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Manga):
            return obj.__dict__
        return super().default(obj)

def extract_manga_info(item):
    # Extract id
    href = item['href']
    id = href.split('/')[-1]

    # Extract title
    title = item.find('p', class_='AllTitle-module_title_20PzS').text.strip()

    # Extract author
    author = item.find('p', class_='AllTitle-module_author_2rV8i').text.strip()

    # Extract language
    language = item.find('span', class_='').get('title', '')

    # Create a Manga object with an empty description
    manga_obj = Manga(id, title, author, language, '')

    return manga_obj

def scrape_manga_info():
    options = Options()
    options.add_argument('headless')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    with driver as driver:
        driver.get("https://mangaplus.shueisha.co.jp/manga_list/all")

        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'AllTitle-module_allTitle_1CIUC')))

        html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")

    mangas = soup.find_all('a', class_='AllTitle-module_allTitle_1CIUC')
    manga_objects = list(map(extract_manga_info, mangas))

    # Progress bar initialization for manga info scraping
    total_manga_count = len(manga_objects)
    progress_bar = tqdm(total=total_manga_count, desc="Scraping Manga info", unit="manga")

    for manga in manga_objects:
        # Scraping manga info here
        progress_bar.update(1)

    progress_bar.close()

    return manga_objects

def scrape_manga_descriptions(manga_objects):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        description_futures = []
        for manga in manga_objects:
            description_futures.append(executor.submit(extract_manga_description, manga))

        # Progress bar initialization for manga description scraping
        total_manga_count = len(manga_objects)
        progress_bar = tqdm(total=total_manga_count, desc="Scraping Manga Descriptions", unit="manga")

        # Monitor progress of description extraction
        while not all(future.done() for future in description_futures):
            completed_count = sum(future.done() for future in description_futures)
            progress_bar.update(completed_count - progress_bar.n)
            time.sleep(0.1)

        progress_bar.close()

def extract_manga_description(manga):
    try:
        options = Options()
        options.add_argument('headless')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(options=options)

        with driver as driver:
            driver.get(f"https://mangaplus.shueisha.co.jp/titles/{manga.id}")

            wait = WebDriverWait(driver, 20)
            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'TitleDetailHeader-module_overview_32fOi')))

            html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")
        manga_description = soup.find('p', class_='TitleDetailHeader-module_overview_32fOi').text.strip()

        manga.description = manga_description
    except Exception as e:
        print(f"Error occurred while scraping description for manga with id {manga.id}: {str(e)}")
        manga.description = ""

def scrape_manga_data():
    manga_objects = scrape_manga_info()
    scrape_manga_descriptions(manga_objects)
    return manga_objects


if __name__ == "__main__":
    start_time = time.time()
    all_manga_data = scrape_manga_data()
    elapsed_time = time.time() - start_time
    print(f"\nScraped {len(all_manga_data)} manga descriptions in {elapsed_time:.2f} seconds.")

    # Get the current working directory
    current_dir = os.getcwd()

    # Construct the file path
    file_path = os.path.join(current_dir, "Data Scraping", "data", "mangas.json")

    # Write data to JSON file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_manga_data, f, indent=4, ensure_ascii=False)
        print(f"Data has been written to {file_path}")
    except IOError:
        print(f"Error: Failed to write data to {file_path}")
