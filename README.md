# Korean Job Sites Scraper

This project scrapes job postings from major Korean job sites including Saramin and JobKorea.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:
```bash
python job_scraper.py
```

The script will:
1. Scrape job postings from Saramin and JobKorea
2. Save the results to `job_postings.csv`

## Features

- Scrapes multiple job sites
- Includes job title, company name, and location
- Saves results in CSV format
- Implements polite scraping with random delays
- Uses proper headers to avoid blocking

## Note

Please be mindful of the websites' terms of service and implement appropriate delays between requests to avoid overwhelming their servers.
