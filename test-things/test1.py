# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import scrapermod as sm
import llm
import cache
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import tldextract
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Scrape homepage
# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the site
url = "https://aira.io"
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

# Extract meta info
title_tag = soup.title.string if soup.title else "No <title> found"
description_tag = soup.find("meta", attrs={"name": "description"})
description = (
    description_tag["content"] if description_tag else "No meta description found"
)
H1s = []
for h1 in soup.find_all("h1"):
    H1s.append(h1.get_text(strip=True))

meta = {"title": title_tag, "description": description, "H1s": H1s}

# Extract outbound links
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

# Scrape core pages
homepage_content = requests.get(url).text
core_urls = sm.get_core_pages(url, homepage_content)

core_content = []
for url in core_urls:
    content = sm.scrape_page_content(url)
    if content:
        core_content.append({"url": url, "content": content})

combined_content = sm.extract_keywords_combined(core_content)

# Extract keywords
keywords = sm._yake_extraction(combined_content)

# LLM Summarization and blog titles
summ = llm.summarize_content(combined_content)

result = {
    "meta": meta,
    "outbound_links": outbound_links,
    "keywords": keywords,
    "offerings": summ["offerings"],
    "channels": summ["channels"],
    "blog_titles": summ["blog_titles"],
}
