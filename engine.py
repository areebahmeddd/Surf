import concurrent.futures
import random
import heapq
import os
import tkinter as tk

import requests
from bs4 import BeautifulSoup
from tkinter import filedialog

search_engines = {
    "google": {
        "url": "https://www.google.com/search?q=",
        "result_class": "g",
        "title_class": "h3",
        "link_tag": "a"
    },
    "bing": {
        "url": "https://www.bing.com/search?q=",
        "result_class": "b_algo",
        "title_class": "b_title",
        "link_tag": "a"
    },
    "yahoo": {
        "url": "https://search.yahoo.com/search?p=",
        "result_class": "algo",
        "title_class": "title",
        "link_tag": "a"
    }
}

def text_search(query):
    try:
        # Parallelize search tasks using ThreadPoolExecutor and collect the results in all_results list
        with concurrent.futures.ThreadPoolExecutor(len(search_engines)) as executor:
            all_results = [
                result for task in concurrent.futures.as_completed(
                    [
                        executor.submit(fetch_results, query, engine)
                        for engine in search_engines
                    ]
                )
                for result in task.result()
            ]

    except Exception as exc:
        print(f"\nError occurred while performing the search:\n {exc}")
        return []

    # Shuffle the list of all_results randomly
    random.shuffle(all_results)

    # Select the top 10 processed results based on popularity and recency
    processed_results = heapq.nlargest(10, all_results[:30],
        key = lambda x: (x.get("popular", 0) * 10 + x.get("recent", 0))
    )

    # Format the processed results as dictionaries with specific keys
    processed_results = [
        {
            key: search_result[key]
            for key in ["title", "link", "engine"]
        }
        for search_result in processed_results
    ]

    return processed_results

def fetch_results(query, engine):
    try:
        # Connect to a proxy server
        proxy_url = "socks5://148.72.212.183:60302"
        proxies = {"http": proxy_url, "https": proxy_url}

        # Send GET request with the constructed URL and validate response
        search_response = requests.get(
            search_engines[engine]["url"] + query.replace(" ", "+"),
            # proxies = proxies,
            timeout = 30
        )
        search_response.raise_for_status()

        # Process HTML document using BeautifulSoup and store the extracted data in scraped_results list
        html_document = BeautifulSoup(search_response.text, "html.parser")
        scraped_results = []

        if engine == "google":
            # Find all search results on Google
            google_results = html_document.find_all("div", class_ = search_engines[engine]["result_class"])

            for result in google_results:
                # Extract title and link URL from the search result and add to scraped_results list
                scraped_results.append({
                    "title": result.find(search_engines[engine]["title_class"]).text,
                    "link": result.find(search_engines[engine]["link_tag"])["href"],
                    "engine": engine
                })

        elif engine == "bing":
            # Find all search results on Bing
            bing_results = html_document.find_all("li", class_ = search_engines[engine]["result_class"])

            for result in bing_results:
                # Extract title and link URL from the search result and add to scraped_results list
                scraped_results.append({
                    "title": result.find(search_engines[engine]["link_tag"]).text,
                    "link": result.find(search_engines[engine]["link_tag"])["href"],
                    "engine": engine
                })

        elif engine == "yahoo":
            # Find all search results on Yahoo
            yahoo_results = html_document.find_all("div", class_ = search_engines[engine]["result_class"])

            for result in yahoo_results:
                # Extract title and link URL from the search result and add to scraped_results list
                scraped_results.append({
                    "title": result.find(search_engines[engine]["link_tag"]).text,
                    "link": result.find(search_engines[engine]["link_tag"])["href"],
                    "engine": engine
                })

        return scraped_results

    except Exception as exc:
        print(f"\nError occurred while retrieving the search results from {engine}:\n {exc}")
        return []

def image_search(upload_image_entry):
    # Open file explorer to allow the user to select an image
    selected_file = filedialog.askopenfilename()

    # If a file is selected, update the upload image field with the file name
    if selected_file:
        upload_image_entry.delete(0, tk.END)
        file_name = os.path.basename(selected_file)
        upload_image_entry.insert(0, file_name)