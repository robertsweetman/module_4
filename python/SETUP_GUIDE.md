# Setup Guide for eTenders Scraper

## Step-by-Step Instructions

### 1. Create a Virtual Environment

```bash
# Navigate to the python folder
cd /Users/robert.sweetman/Documents/GitHub/module_4/python

# Create a virtual environment named 'venv'
python3 -m venv venv
```

### 2. Activate the Virtual Environment

```bash
# Activate the virtual environment
source venv/bin/activate
```

You'll see `(venv)` appear at the start of your terminal prompt, indicating the virtual environment is active.

### 3. Install Required Packages

```bash
# Install the dependencies
pip install -r requirements.txt
```

### 4. Run the Scraper

```bash
# Test with page 1 only (quick test)
python etenders_scraper.py
```

This will create `etenders_test.csv` with data from the first page.

### 5. Scrape All Pages (Optional)

To scrape all 231 pages:

1. Open `etenders_scraper.py` in an editor
2. Scroll to the bottom of the file
3. Uncomment the last 6 lines (remove the `#` symbols)
4. Run: `python etenders_scraper.py`

Or run this command directly without editing the file:

```bash
python -c "from etenders_scraper import scrape_all_pages, export_to_csv; data = scrape_all_pages(1, 231, 1.0); export_to_csv(data, 'etenders_full_data.csv')"
```

### 6. Deactivate Virtual Environment

When you're done, deactivate the virtual environment:

```bash
deactivate
```

## Quick Reference

```bash
# Full setup and run (copy and paste all lines)
cd /Users/robert.sweetman/Documents/GitHub/module_4/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python etenders_scraper.py
```

## Output Files

- `etenders_test.csv` - Test data from page 1 (10 records)
- `etenders_full_data.csv` - Full data from all 231 pages (~2,300 records)

## Troubleshooting

**If you see "command not found: python"**, use `python3` instead
**If the virtual environment doesn't activate**, make sure you're in the correct directory
**If packages fail to install**, try upgrading pip first: `pip install --upgrade pip`
