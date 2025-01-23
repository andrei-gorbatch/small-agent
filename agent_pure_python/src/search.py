# This file contains search tools

import requests
import json
import os

from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Code to download a webpage and parse it using BeautifulSoup
def download_webpage(url):
    response = requests.get(url)
    return response.text

def parse_webpage(html):
    soup = bs(html, "html.parser")
    return soup.get_text()

def get_csv_links_from_url(url):
    html = download_webpage(url)
    soup = bs(html, "html.parser")
    resp = requests.get(url)
    soup = bs(resp.text,'lxml')
    og = soup.find("meta",  property="og:url")
    base = urlparse(url)
    links = []
    for link in soup.find_all('a'):
        current_link = link.get('href')
        if current_link.endswith('csv'):
            if og:
                links.append(og["content"] + current_link)
            else:
                links.append(base.scheme+"://"+base.netloc + current_link)
    if len(links) == 0:
        return ["No CSV links found on the page"]
    
    return links

def get_text_from_url(url):
    html = download_webpage(url)
    text = parse_webpage(html)
    return text

# Code to search Google using the Serper API
def google_search(query):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
    "q": query
    })
    headers = {
    'X-API-KEY': SERPER_API_KEY,
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    results = json.loads(response.text)

    output = parse_snippets(results)

    return output


def parse_snippets(results: dict) -> dict:
    snippets = {}

    for result in results["organic"]:
        if "snippet" in result:
            snippets[result["link"]] = (result["snippet"])

    if len(snippets) == 0:
        return ["No good Google Search Result was found"]
    return snippets


if __name__ == "__main__":
    query = "What is the capital of France?"
    results = google_search(query)
    for result in results:
        print(result)