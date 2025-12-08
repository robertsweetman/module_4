# Appendix

All python (data-pipeline) code as well as PostrgeSQL setup can be found in [this module 4 repository](https://github.com/robertsweetman/module_4)

```txt
main.py
  │
  ├─> 1. etenders_scraper.py (scrape_pages)
  │   │   └─> Returns generator of raw tender records
  │   │
  │   └─> For each record:
  │       │
  │       ├─> 2. type_coercer.py (coerce_types)
  │       │   └─> Creates tender_record
  │       │
  │       ├─> 3. pdf_parser.py (enrich_record_with_pdf) [if --no-pdfs NOT set]
  │       │   └─> Creates pdf_record
  │       │
  │       ├─> 4. cpv_list_checker.py (check_cpv_codes) [if --no-cpvs NOT set]
  │       │   └─> Creates cpv_record
  │       │
  │       └─> 5. bid_analyzer.py (analyze_tender_for_bid) [if --analyze-bids set]
  │           └─> Creates bid_record
  │
  └─> Output to one of:
      ├─> json_output.py (JSONOutput)
      ├─> csv_output.py (CSVOutput)
      └─> postgres_output.py (PostgresOutput)
```
