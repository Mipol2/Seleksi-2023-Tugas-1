import getInfo
import time
import json

if __name__ == "__main__":
    start_time = time.time()

    # Scrape manga data
    all_manga_data = getInfo.scrape_manga_data()

    # Convert the Python objects into JSON and export it to manga.json file.
    with open('manga_list.json', 'w', encoding='utf-8') as f:
        json.dump(all_manga_data, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Created manga_list.json file in {execution_time} seconds.")