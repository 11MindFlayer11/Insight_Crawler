from urllib.parse import urljoin
import tldextract
from bs4 import BeautifulSoup
import requests
import yake
from typing import List, Dict


def get_core_pages(base_url: str, homepage_content: str) -> list:
    """Identify core pages from homepage links"""
    soup = BeautifulSoup(homepage_content, "html.parser")

    # Common page indicators
    CORE_KEYWORDS = {
        "about",
        "product",
        "service",
        "solution",
        "feature",
        "pricing",
        "contact",
        "blog",
        "careers",
    }

    core_pages = set()
    domain = tldextract.extract(base_url).registered_domain

    for link in soup.find_all("a", href=True):
        href = link["href"].lower()
        absolute_url = urljoin(base_url, href)

        # Filter same-domain links
        if tldextract.extract(absolute_url).registered_domain != domain:
            continue

        # Check for core page indicators
        if any(kw in href for kw in CORE_KEYWORDS):
            core_pages.add(absolute_url)

    return list(core_pages)[:5]  # Limit to 5 core pages


def scrape_page_content(url: str) -> str:
    """Scrape and clean page content"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        # Clean text
        text = soup.get_text(separator="\n")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return ""


def extract_keywords_combined(core_content: List[Dict]) -> Dict:
    """Extract keywords from scraped content using selected method"""
    combined_text = " ".join([page["content"] for page in core_content])

    return combined_text


def _yake_extraction(text: str, top_n: int = 15) -> List[str]:
    """YAKE! implementation (fastest, no GPU needed)"""
    kw_extractor = yake.KeywordExtractor(
        n=3,  # Max 3-word phrases
        top=top_n,
        stopwords=None,
        windowsSize=2,
        dedupLim=0.9,
    )
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]
