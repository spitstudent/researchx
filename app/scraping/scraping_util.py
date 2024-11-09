import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib
import time
from config import settings
from serpapi import GoogleSearch
import json

def fetch_arxiv_papers(query, max_results=20, delay=3):
    papers = []
    for start in range(0, max_results, 10):
        # Query the ArXiv API
        url = f'http://export.arxiv.org/api/query?search_query={query}&start={start}&max_results=10'
        response = requests.get(url)
        
        # Parse the XML with BeautifulSoup
        soup = BeautifulSoup(response.content, 'xml')
        
        # Loop through each entry in the XML and extract details
        for entry in soup.find_all('entry'):
            title = entry.title.text
            summary = entry.summary.text
            authors = [author.find('name').text for author in entry.find_all('author')]
            pdf_link = entry.find('link', {'type': 'application/pdf'})['href']
            

            papers.append({
                "title": title,
                "summary": summary,
                "authors": authors,
                "pdf_link": pdf_link
            })
        

        time.sleep(delay)
    return papers



def get_google_scholar_citations(title):
    """Fetch citation count from Google Scholar."""
    # Search for the paper on Google Scholar
    query = urllib.parse.quote(title)
    search_url = f"https://scholar.google.com/scholar?q={query}"

    # Send a request to Google Scholar
    response = requests.get(search_url)

    # Check if the request was successful
    if response.status_code != 200:
        print("Failed to retrieve data from Google Scholar.")
        return 0

    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for citation counts in the search results
    citation_count = 0
    for result in soup.find_all('div', class_='gs_ri'):
        citation_info = result.find('div', class_='gs_fl').find_all('a')
        for info in citation_info:
            if 'Cited by' in info.text:
                citation_count = int(info.text.split(' ')[-1])  # Extract the number
                return citation_count
    
    return citation_count

def fetch_related_papers(query):
    query = query+ " site:semanticscholar.org"
    search = GoogleSearch({
        "q": query,
        "location": "United States",
        "hl": "en",
        "gl": "us",
        "api_key": settings.serp_api_key
    })
    
    results = search.get_dict()
    related_papers = []

    try:
        if "organic_results" in results:
            for result in results["organic_results"]:
                title = result.get("title", "No title available")
                link = result.get("link", "No link available")
                snippet = result.get("snippet", "No snippet available")
                
                related_papers.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet
                })
    except Exception as e:
        print(f"An error occurred: {e}")

    # Return results in JSON format
    return json.dumps(related_papers, indent=4)

# Example usage
# query = "Attention is all you need site:semanticscholar.org"
# query = "Attention is all you need"
# print(get_google_scholar_citations(query))
# related_papers_json = fetch_related_papers(query)
# print(related_papers_json)
