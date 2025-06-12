from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import tldextract
import time
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the site
url = "https://en.wikipedia.org/wiki/Gauss%E2%80%93Markov_theorem"
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
for h1 in soup.find_all("h1"):
    print("-", h1.get_text(strip=True))

# --- All <a> tags and filter outbound links
print("\nAll <a> tags with outbound links:")
domain_root = tldextract.extract(url).registered_domain

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
        print(f"- {link}")
