# Insight Crawler

A powerful web crawling and analysis tool that provides insights about websites using AI-powered content analysis, keyword extraction, and smart caching.

## Features

- Website content analysis and summarization
- Core page identification and scraping
- Keyword extraction using YAKE!
- AI-powered content summarization using GPT-4.1-mini
- Outbound link analysis
- Redis-based caching system
- Blog title suggestions
- Meta information extraction

## Project Structure

```
Insight_Crawler/
├── main.py
├── scrapermod.py
├── llm.py
├── cache.py
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.x
- Redis server running locally on port 6379
- Chrome/Chromium (for Selenium WebDriver)
- GitHub Token for AI model access

## Environment Variables

Required environment variables:
- `GITHUB_TOKEN`: GitHub token for accessing the AI model endpoint

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Ensure Redis is running locally
4. Set up required environment variables

## API Endpoints

### POST /analyze
Performs comprehensive website analysis.

Request body:
```json
{
    "url": "https://example.com"
}
```

Response includes:
- Meta information (title, description, H1 tags)
- Outbound links
- Keywords
- AI-generated offerings summary
- Marketing channel suggestions
- Blog title suggestions

### POST /suggest-blogs
Generates blog title suggestions for a website.

Request body:
```json
{
    "url": "https://example.com"
}
```

## Components

### Main Application (main.py)
- FastAPI application setup
- Route handlers for analysis and blog suggestions
- Selenium integration for dynamic content
- Error handling and validation

### Scraper Module (scrapermod.py)
- Core page identification
- Content scraping and cleaning
- Keyword extraction using YAKE!
- URL processing and validation

### LLM Integration (llm.py)
- OpenAI GPT-4.1-mini integration
- Content summarization
- Marketing channel analysis
- Blog title generation

### Caching System (cache.py)
- Redis integration
- Cache management
- Error handling and fallback mechanisms

## Error Handling

The application includes comprehensive error handling for:
- Invalid URLs
- Failed scraping attempts
- LLM service unavailability
- Cache connection issues
- HTML parsing errors

## Caching Strategy

- Analysis results are cached for 2 hours (7200 seconds)
- Separate caching for full analysis and blog suggestions
- Fallback mechanisms when cache is unavailable

## Running the Application

Start the server:
```bash
python main.py
```

The application will run on `http://0.0.0.0:8000`

#Note: If you face any problems in installing the redis server, here are the steps:
- Windows
  - On Powershell, run the following commands:
    - wsl --install 
  - On Wsl, run the following commands:
    - curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
    - sudo apt-get update
    - sudo apt-get install redis
  - Installation is now complete, to run the redis server: Run the following commands on WSL -
    - sudo service redis-server start
    - redis-cli
- MacOS
  - It can be installed using Homebrew
    - brew install redis
    - brew services start redis
  - Test redis with
    - redis-cli ping
