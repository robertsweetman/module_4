"""
eTenders.gov.ie Web Scraper
Scrapes tender data from the eTenders website
Yields individual records for pipeline processing
"""

import requests
from bs4 import BeautifulSoup
import time
from typing import Generator, Dict
import re


def scrape_etenders_page(page_number: int) -> Generator[Dict[str, str], None, None]:
    """
    Scrape tender data from a single page of eTenders website.
    Yields individual tender records for pipeline processing.
    
    Args:
        page_number: The page number to scrape (1-231)
        
    Yields:
        Dictionary containing tender data for each record
    """
    url = f"https://www.etenders.gov.ie/epps/quickSearchAction.do?d-3680175-p={page_number}&searchType=cftFTS&latest=true"
    
    print(f"Scraping page {page_number}...")
    
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table containing tender data
        table = soup.find('table', {'id': 'T01'})
        
        if not table:
            print(f"Warning: No table found on page {page_number}")
            return
        
        # Find all table rows (skip header row)
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            
            # Skip empty rows or rows without enough columns
            if len(cols) < 9:
                continue
            
            # Extract title and detail URL
            title_cell = cols[1]
            title = title_cell.get_text(strip=True)
            detail_url = ''
            title_link = title_cell.find('a')
            if title_link and title_link.get('href'):
                detail_url = title_link.get('href')
                if detail_url.startswith('/'):
                    detail_url = f"https://www.etenders.gov.ie{detail_url}"
            
            # Extract data from columns based on actual structure
            tender_data = {
                'row_number': cols[0].get_text(strip=True),
                'title': title,
                'detail_url': detail_url,
                'resource_id': cols[2].get_text(strip=True),
                'contracting_authority': cols[3].get_text(strip=True),
                'info': cols[4].get_text(strip=True),
                'date_published': cols[5].get_text(strip=True),
                'submission_deadline': cols[6].get_text(strip=True),
                'procedure': cols[7].get_text(strip=True),
                'status': cols[8].get_text(strip=True),
                'notice_pdf_url': '',
                'award_date': '',
                'estimated_value': '',
                'cycle': ''
            }
            
            # Extract Notice PDF URL if exists (column 9)
            if len(cols) > 9:
                notice_pdf_link = cols[9].find('a')
                if notice_pdf_link and notice_pdf_link.get('href'):
                    pdf_url = notice_pdf_link.get('href')
                    # Make absolute URL if relative
                    if pdf_url.startswith('/'):
                        pdf_url = f"https://www.etenders.gov.ie{pdf_url}"
                    tender_data['notice_pdf_url'] = pdf_url
            
            # Extract award date (column 10)
            if len(cols) > 10:
                tender_data['award_date'] = cols[10].get_text(strip=True)
            
            # Extract estimated value (column 11)
            if len(cols) > 11:
                tender_data['estimated_value'] = cols[11].get_text(strip=True)
            
            # Extract cycle (column 12)
            if len(cols) > 12:
                tender_data['cycle'] = cols[12].get_text(strip=True)
            
            yield tender_data
        
        print(f"Processed page {page_number}")
        
    except requests.RequestException as e:
        print(f"Error scraping page {page_number}: {e}")
        return
    except Exception as e:
        print(f"Unexpected error on page {page_number}: {e}")
        return


def scrape_pages(start_page: int = 1, end_page: int = 231, delay: float = 1.0) -> Generator[Dict[str, str], None, None]:
    """
    Scrape tender data from multiple pages.
    Yields individual records for pipeline processing.
    
    Args:
        start_page: First page to scrape (default: 1)
        end_page: Last page to scrape (default: 231)
        delay: Delay between requests in seconds (default: 1.0)
        
    Yields:
        Individual tender data dictionaries
    """
    for page in range(start_page, end_page + 1):
        for tender in scrape_etenders_page(page):
            yield tender
        
        # Add delay to be respectful to the server
        if page < end_page:
            time.sleep(delay)


if __name__ == "__main__":
    # Test with first page only
    print("Testing scraper with page 1...")
    count = 0
    for tender in scrape_etenders_page(1):
        count += 1
        if count == 1:
            print(f"\nSample record:")
            print(tender)
    
    print(f"\nTotal records from page 1: {count}")
