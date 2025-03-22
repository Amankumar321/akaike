import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os

load_dotenv()

def is_valid_url(url):
    """Check if URL is accessible and not returning 404, 403, or errors."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_google_news(company_name):
    search_url = f"https://www.google.com/search?q={company_name}+news&hl=en&tbm=nws&num=100"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for result in soup.find_all("div", class_="Gx5Zad"):
        if len(articles) >= int(os.getenv("MAX_ARTICLES")):  # Stop once we have max valid articles
            break
        
        title_element = result.find("div", class_="BNeawe")
        title = title_element.text if title_element else "No Title"
        
        url = result.a["href"] if result.a else "#"
        if url.startswith("/url?"):
            url = re.search(r'q=(?P<url>(.*?))&', url)
            url = url.group("url") if url else "#"
        
        if not is_valid_url(url):  # Skip broken or inaccessible links
            continue

        try:
            page_response = requests.get(url, headers=headers, timeout=5)
            if page_response.status_code != 200:
                continue
            page_soup = BeautifulSoup(page_response.text, "html.parser")
            content = page_soup.get_text(separator="\n", strip=True)

            # Detect JS-heavy pages (Cloudflare, etc.)
            if "Just a moment..." in content or "Checking your browser" in content:
                continue  

            articles.append({
                "title": title,
                "url": url,
                "content": content
            })

        except requests.RequestException:
            continue  # Skip failed requests

    return articles
