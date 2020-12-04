import json
import requests
import time
import warnings
from bs4 import BeautifulSoup
from pathlib import Path
from random import randint
warnings.filterwarnings("ignore", category=UserWarning, module='bs4') # Suppress BS4 Warnings

_URL = "https://api.mycareersfuture.gov.sg/v2/jobs?limit=20&omitCountWithSchemes=true&page={page}&search={search_term}&sortBy=new_posting_date&salary=0"

def clean(data):
    try:
        if isinstance(data, str):
            return BeautifulSoup(data, "html.parser").text
        elif isinstance(data, dict):
            for key, value in data.items():
                data[key] = clean(value)
            return data
        elif isinstance(data, list):
            return [clean(item) for item in data]
        else:
            return data
    except Exception:
        return data

def main():
    print("Scraper Started")

    # Collecting User Input
    print("===================")
    print("Press enter after each parameter")
    search_term = input("Search Term: ")
    output_dir = input("Output Directory Name (unique): ")
    
    # Confirming Input
    print("===================")
    input("Press enter to confirm the information below (or Ctrl-C to terminate the program):\n" +
    "Search Term: '{}',\n".format(search_term) +
    "Output Directory Name: '{}'".format(output_dir))
    
    # Initialisation
    print("===================")
    output_dir = Path(output_dir)
    if output_dir.exists():
        print("Output Directory already exists!")
        exit(1)
    output_dir.mkdir(parents = True)
    
    sess = requests.Session()
    sess.headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36" }

    # Scraping
    print("Starting Scraping Process")
    curr_page_num = 0
    end_page_num = 999
    num_data_scraped = 0

    while curr_page_num <= end_page_num:
        print("== Scraping Page: {}, Total Scraped: {}".format(curr_page_num, num_data_scraped))
        
        # Collecting data
        results = []
        try:
            response = sess.get(_URL.format(
                page = curr_page_num,
                search_term = search_term)
            )
            parsed_response = response.json()
            results = parsed_response["results"]
            end_page_num = parsed_response["total"] // 20 + 1
        except Exception as e:
            print("Error occurred on page: {}. Skipping page.".format(curr_page_num))

        # Output to file
        for result in results:
            uuid = result["uuid"]
            output_filepath = output_dir / (uuid + ".json")
            if output_filepath.exists():
                continue

            result = clean(result)
            with output_filepath.open("w") as f:
                json.dump(result, f, indent = 4)
            num_data_scraped += 1

        curr_page_num += 1 # DO NOT REMOVE

        time.sleep(randint(1, 6) / 2) # Randomly choose delay between [0.5, 3] seconds

    print("Scraping Process Completed")

if __name__ == "__main__":
    main()