from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import tldextract
import time
from urllib.parse import urlparse
from urllib.parse import urljoin
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import scrapermod as sm


# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the site
url = "https://aira.io/"
driver.get(url)
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
except:
    print("No <h1> tag found after waiting.")

# Get page HTML
html = driver.page_source
driver.quit()

# Parse HTML
soup = BeautifulSoup(html, "html.parser")

# --- <title>
title_tag = soup.title.string if soup.title else "No <title> found"
print("Title:", title_tag)

# --- <meta name="description">
description_tag = soup.find("meta", attrs={"name": "description"})
description = (
    description_tag["content"] if description_tag else "No meta description found"
)
print("Description:", description)

# --- All <h1> tags
print("\nAll <h1> tags:")
H1s = []
for h1 in soup.find_all("h1"):
    H1s.append(h1.get_text(strip=True))
    print("-", h1.get_text(strip=True))

# --- All <a> tags and filter outbound links
print("\nAll <a> tags with outbound links:")
domain_root = tldextract.extract(url).registered_domain
outbound_links = []
for a_tag in soup.find_all("a", href=True):
    link = a_tag["href"]
    parsed = tldextract.extract(link)
    link_domain = parsed.registered_domain

    # Normalize relative links
    if link.startswith("/"):
        continue  # internal relative
    if not parsed.domain:
        continue  # likely anchor or JS

    # Filter outbound
    if link_domain and link_domain != domain_root:
        outbound_links.append(link)
        print(f"- {link}")

# soup is the o/p of beautiful soup

homepage_content = requests.get(url).text
core_urls = sm.get_core_pages(url, homepage_content)

core_content = []
for url in core_urls:
    content = sm.scrape_page_content(url)
    if content:
        core_content.append({"url": url, "content": content})

combined_content = sm.extract_keywords_combined(core_content)

keywords = sm._yake_extraction(combined_content)

summ = sm.summarize_content(combined_content)

meta = {"title": title_tag, "description": description, "H1s": H1s}
summ.update(
    {
        "metadata": meta,
        "Outbound_links": outbound_links,
        "keywords": keywords,
    }
)

sm.set_cache(key=url, data=summ)
