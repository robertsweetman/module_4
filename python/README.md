# eTenders.gov.ie Web Scraper

This Python script scrapes tender data from the eTenders.gov.ie website and exports it to CSV format.

## Features

- Scrapes tender data from all 231 pages (10 tenders per page)
- Captures Notice PDF URLs
- Exports data to CSV format
- Includes rate limiting to be respectful to the server

## Requirements

Install the required packages:

```bash
pip install requests beautifulsoup4
```

## Usage

### Test with a Single Page

```python
from etenders_scraper import scrape_etenders_page, export_to_csv

# Scrape page 1
data = scrape_etenders_page(1)
export_to_csv(data, 'etenders_page1.csv')
```

### Scrape All Pages

```python
from etenders_scraper import scrape_all_pages, export_to_csv

# Scrape all 231 pages
all_data = scrape_all_pages(start_page=1, end_page=231, delay=1.0)
export_to_csv(all_data, 'etenders_full_data.csv')
```

### Scrape a Range of Pages

```python
from etenders_scraper import scrape_all_pages, export_to_csv

# Scrape pages 1-10
data = scrape_all_pages(start_page=1, end_page=10, delay=1.0)
export_to_csv(data, 'etenders_partial.csv')
```

## Data Fields

The scraper captures the following fields:

- `row_number`: Row number in the table
- `title`: Tender title
- `reference`: Tender reference number
- `organisation`: Publishing organisation
- `description_link`: Link text for description
- `published_date`: Publication date and time
- `closing_date`: Closing date and time
- `status`: Tender status (e.g., "Open")
- `submission_type`: Type of submission
- `notice_pdf_url`: URL to the Notice PDF document
- `value`: Tender value (if available)
- `interested_parties`: Number of interested parties

## Notes

- The script includes a 1-second delay between requests by default to avoid overwhelming the server
- Scraping all 231 pages will take approximately 4-5 minutes BUT now that additional AI steps have been introduced this might take a few hours intially
- The script handles errors gracefully and will continue scraping even if individual pages fail
