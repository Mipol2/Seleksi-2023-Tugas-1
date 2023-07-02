import time
import concurrent.futures
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from manga import Manga

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
    manga_obj = Manga(id, title, author, language,'')

    return manga_obj

def extract_manga_description(id):
    # Set up the Chrome driver
    options = Options()
    options.add_argument("--headless")
    service = Service('path_to_chromedriver')

    with webdriver.Chrome(service=service, options=options) as driver:
        # Navigate to the manga page
        driver.get(f"https://mangaplus.shueisha.co.jp/titles/{id}")

        # Wait for the description element to be visible
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'TitleDetailHeader-module_overview_32fOi')))

        # Get the HTML content of the page
        html = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Extract the manga description
    manga_description = soup.find('p', class_='TitleDetailHeader-module_overview_32fOi').text.strip()

    return manga_description

def scrape_manga_data():
    # Set up the Chrome driver
    options = Options()
    options.add_argument("--headless")
    service = Service('path_to_chromedriver')

    with webdriver.Chrome(service=service, options=options) as driver:
        # Navigate to the manga list page
        driver.get("https://mangaplus.shueisha.co.jp/manga_list/all")

        # Wait for the manga card elements to be visible
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'AllTitle-module_allTitle_1CIUC')))

        # Get the HTML content of the page
        html = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Extract manga information using multiple threads
    mangas = soup.find_all('a', class_='AllTitle-module_allTitle_1CIUC')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        manga_objects = list(executor.map(extract_manga_info, mangas))

    # Extract manga descriptions using multiple processes
    with concurrent.futures.ProcessPoolExecutor() as executor:
        manga_ids = [manga.id for manga in manga_objects]
        manga_descriptions = list(executor.map(extract_manga_description, manga_ids))

    # Update manga objects with descriptions
    for manga, description in zip(manga_objects, manga_descriptions):
        manga.description = description

    # Convert manga objects to dictionaries
    manga_data = [manga.to_dict() for manga in manga_objects]

    return manga_data