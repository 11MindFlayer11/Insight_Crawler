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
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware - ESSENTIAL for frontend to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request/response models
class AnalysisRequest(BaseModel):
    url: str


class AnalysisResponse(BaseModel):
    meta: dict
    outbound_links: List[str]
    keywords: List[str]
    offerings: str
    channels: str
    blog_titles: str


# Use caching functions from scrapermod
get_cache = cache.get_cache
set_cache = cache.set_cache


@app.post("/analyze", response_model=AnalysisResponse)
def analyze_website(request: AnalysisRequest):
    cache_key = f"analysis:{request.url}"
    if cached := get_cache(cache_key):
        return cached

    try:
        # Scrape homepage
        # Setup headless browser
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

        # Load the site
        url = request.url
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
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
            description_tag["content"]
            if description_tag
            else "No meta description found"
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
        homepage_content = html
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
        set_cache(cache_key, result, ttl=7200)
        return result

    except sm.requests.exceptions.RequestException as e:
        raise HTTPException(400, f"Failed to fetch website: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Server error: {str(e)}")


@app.post("/suggest-blogs")
def suggest_blogs(request: AnalysisRequest):
    cache_key = f"blogs:{request.url}"
    if cached := get_cache(cache_key):
        return cached

    # Check analysis cache first
    analysis_cache = get_cache(f"analysis:{request.url}")
    if analysis_cache and "blog_titles" in analysis_cache:
        blog_titles = analysis_cache["blog_titles"]
        set_cache(cache_key, {"titles": blog_titles}, ttl=7200)
        return {"titles": blog_titles}

    # Fallback to full analysis
    analysis = analyze_website(request)
    return {"titles": analysis.blog_titles}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
