# Data Product Development <!-- 1000 words -->

<!-- Understand the specific business problem to be addressed -->

We want to build a data product that becomes an invaluable bid preparation, analysis and feedback tool. Something that allows non-technical users to ask questions about the tenders coming out of the Irish Govt, identify tenders that we maybe should of bid for that didn't and ultimately provides a positive feedback loop that drives further commercial successes.

## ETL

- Scrape
- Parse Tender (fix datatypes)
- Parse PDF (using AI)
- ML/AI Analysis
- Bid Submission
- Bid Status
- Irish Govt Award notification/feedback

## Data sources

There are effectively 4 data sources when it comes to updating the database so that it becomes a useful part of the sales process. The initial ETL pipeline to scoop up tenders, responses from the ML/AI summary process, the Sales Team's bid submission and finally the award notification back from the Irish Govt as to whether the tender has been awarded to Version 1 or someone else.

## Data Product

### Testing

### Scalability

### Performance optimization

### Security

- Who has access to the data internally?

### Regulatory Compliance

- GDPR
- Use Azure service to scrub personal identifiable data

### Flexibility for future Use

Mention using an MCP server

### Best practices

Q: Where do we get best practice info from? (REF: here)

<!--
● Understand the specific business problems to be addressed and identify all necessary data sources.
● Plan and define the data solution, including any ETL processes or data flows. Consider data formats, sizes, and frequency of updates in the design.
● Choose an appropriate data solution (see list below), focusing on compatibility and scalability. This may be a low-code, no-code, or a coded solution, depending on business needs.
● Develop your data product, conduct comprehensive testing, and automate with scheduling.
● Focus on scalability, performance optimization, security, and regulatory compliance.
● Ensure flexibility for future changes and adherence to best practices.
-->
