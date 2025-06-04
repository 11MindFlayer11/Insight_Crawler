# Website Details Scraper

Website Details Scraper is a Python-based tool that scrapes and extracts metadata from websites and outputs the results in a downloadable JSON file. It is useful for tasks like SEO audits, web crawling, and data analysis.

## Features

- Scrapes website metadata including:
  - Page Title
  - Meta Description
  - Meta Keywords
  - Open Graph Tags (og:title, og:description, etc.)
- Command-line interface for quick execution
- Suggests probable **target keywords**
- Uses **any LLM** to:
  - Summarize what the company offers
  - Suggest which marketing channels might work best (based on product type)
  - Includes a `/suggest-blogs` endpoint to return 3 SEO-optimized blog title suggestions per website
- Outputs results in a downloadable JSON file

## It requires a running local redis server

Installation steps:
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
## Error Handling & Logging

Robust error handling has been implemented to ensure smooth operation and easier debugging. The tool logs various types of failures with clear messages.

### Handled Errors:

1. **Environment Variable Errors**  
   - Missing or improperly configured API keys and required environment variables are detected and logged.

2. **URL Structure Errors**  
   - Malformed, unreachable, or unsupported URLs trigger an error and are excluded from processing.

3. **Parsing Errors**  
   - Issues during HTML parsing or metadata extraction (e.g., missing tags, malformed HTML) are caught and logged.

4. **Redis Failures**  
   - Errors connecting to or interacting with the local Redis server are logged with suggested resolutions.

5. **LLM API Failures**  
   - Failures in interacting with the language model API (timeouts, authentication errors, malformed responses) are captured and logged.

### Logging Output

- All errors are logged to the console with context-specific messages.
- Optionally, logs can be extended to a file (e.g., `error.log`) for persistent debugging.
