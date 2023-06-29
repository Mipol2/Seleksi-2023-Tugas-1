import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from manga import Manga

# Function to extract manga information
def extract_manga_info(soup):
    mangas = soup.find_all('a', class_='AllTitle-module_allTitle_1CIUC')

    res = []

    for item in mangas:
        # Extract id
        href = item['href']
        id = href.split('/')[-1]

        # Extract title
        title = item.find('p', class_='AllTitle-module_title_20PzS').text.strip()

        # Extract author
        author = item.find('p', class_='AllTitle-module_author_2rV8i').text.strip()

        # Extract language
        language = item.find('span', class_='').get('title', '')

        

        # Create a Manga object
        manga_obj = Manga(id, title, author, language)

        # Add manga info to the result list
        res.append(manga_obj.to_dict())

    return res

def extract_manga_description(soup):
    manga = soup.find('p', class_='TitleDetailHeader-module_overview_32fOi').text.strip()
    return manga


def get_info_soup():
        # Set up the Chrome driver
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service('path_to_chromedriver')  # Replace 'path_to_chromedriver' with the actual path to the chromedriver executable
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to the manga list page
    driver.get("https://mangaplus.shueisha.co.jp/manga_list/all")

    # Wait for the manga card elements to be visible
    wait = WebDriverWait(driver, 20)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'AllTitle-module_allTitle_1CIUC')))

    # Get the HTML content of the page
    html = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    return soup

def get_description_soup(id):
    # Set up the Chrome driver
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service('path_to_chromedriver')  # Replace 'path_to_chromedriver' with the actual path to the chromedriver executable
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to the manga list page
    driver.get(f"https://mangaplus.shueisha.co.jp/titles/{id}")

    # Wait for the manga card elements to be visible
    wait = WebDriverWait(driver, 20)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'TitleDetailHeader-module_overview_32fOi')))

    # Get the HTML content of the page
    html = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    return soup


def scrape_manga_data():
    # Extract manga information using the helper function
    soup = get_info_soup()
    manga_data = extract_manga_info(soup)

    for manga in manga_data:
        soup = get_description_soup(manga['id'])
        description = extract_manga_description(soup)
        manga['description'] = description

    return manga_data



if __name__ == "__main__":
    # Scrape manga data
    all_manga_data = scrape_manga_data()

    # Convert the Python objects into JSON and export it to manga.json file.
    with open('manga_list.json', 'w', encoding='utf-8') as f:
        json.dump(all_manga_data, f, indent=4, ensure_ascii=False)

    print("Created manga_list.json file")
