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

There are effectively 4 data sources when it comes to updating the database so that it becomes a useful part of the sales process. The initial ETL pipeline to scoop up tenders, responses from the ML/AI summary process, the Sales Team's bid submission and finally the award notification (via email) sent back from the Irish Govt about whether the tender has been awarded to Version 1 or someone else.

## DB Schema

### eTenders Core data

- resource_id is the primary key (PK)
- title
- contracting authority
- tender submission deadline
- procedure
- status
- PDF URL
- award date
- estimated value
- cycle

 Initial load: ~2300 records (230 pages x 10 rows)
 Update Frequency: Daily incremental scrapes for new tenders

### eTenders PDF

- document_id (PK)
- tender_id is the foreign key (FK)
- PDF URL
- raw text
-

## Bid Submissions** - Internal Sales process tracking

## Data Product

### Testing

This exists to ensure data quality and overall system reliability

#### Unit Testing

We can use Python to test things like web scraping accuracy by validating the extraced fields match the source data. We can test PDF parsing by AI against a set of sample PDF's that we already know the content of. We should also check the data types being parsed and written to the database.

#### Integration Testing

This is the category of 'does the database work in relation to the things it's connected to' like the Power Automate connections, MCP Server (if we choose to implement one) and what happens when we try to inject or append malformed data to the database?

#### User Acceptance Testing

The various user groups need to be happy that the solution is workable for them. Can the Sales team easily update information about a bid from their point of view? Does the Support team have enough logging available to see whether something has gone wrong?

#### Automated Testing

We should have something run on a daily basis to check that the eTenders information is still accessible and the formatting of that hasn't changed.

### Scalability

### Performance optimization

### Security

This should be implemented at several levels (REF: is there a best practice guide on this?)

**Who has access?**
Using Role-Based Access Control (RBAC) allows us to split access into groups and ensure "least privilege" (REF: needed) for each. For example we'd give Sales "read" access to everything but only "write" access to bid submissions fields and Management would get "read all" and so on. (REF: expand this?)

We could ensure only authorized individuals have access using Azure AD integration with Single Sign-On (SSO) and Multi-Factor authentication (REF:) and access should be auditable in the logs to see who accessed or updated what and when.

**Data Protection**
All data should be encrypted at rest and in transit using TLS 1.3 or higher with API keys and secrets held in secure storage like Azure Key Vault with automated key rotation built in. (REF:)

**Application Security**
To guard against attacks or just data input mistakes we need input validation to prevent things like SQL injection attacks and XSS (cross site scripting) as well as rate limiting on any API's that are created to prevent miss-use.

**Network Security**
Ideally the database should NOT be publically available on the web. If we _do_ happen to need this we should at least enable DDOS protection on any public IP/ports. Use an Network Security Group with a port/source whitelist and also put everything behind a NAT Gateway (if in AWS still) although this has about a £30 per month running cost.

**Compliance & Governance**
It would be worth having a third party carry out an annual independent security audit and writing an incident response plan in the event of a data breach.

The data can also be considered as 'internal only', 'confidential' or whether any of it might be classified as 'public'.

Since this database will contain our response to bids we really should consider it internal & confidential so this should form the basis of our decision making around access and security.

### Regulatory Compliance

An important part of the design is meeting data protection regulations and other industry standards (REF: what are these?)

**GDPR:**
Only the necessary minimum data should be collected and certainly not anything that could be considered personally identifiable information (REF:)
We can use AI related services from cloud providers to purge public identifiable information (PII) and have the ability to remove any on request.

**Data Retention and Auditing:**
We need to have some sort of database backup policy like monthly point in time recovery with a years backups in archive (to reduce cost).

Logging is required to allow auditing of data access requests, logins and even performance behaviour.

**Meeting industry standards:**
We need to document security controls like ISO 27001 (REF: which are the relevant ones) and any cloud compliance certificates i.e. ISO 27018 which is cloud specific (REF:)

### Flexibility for future Use

The most obvious win with regards to flexibility for the future is allowing the database to be interrogated/integrated with a Model Conext Protocol server.

**MCP Server Integration:**
This MCP implementation empowers end-users to ask natural language questions of the data, for example: - "Show me all the healthcare tenders over €1m in value in the last 12 months".

This also enables AI tools to use the data and extrapolate from other calls from user driven AI Assistants returning structured responses which contain references back to their 'source' tenders.

**Predictive Analytics and AI:**
Once enough tenders, bids and responses or success/failure data exist in the database this can start to be used in the ML training to return an overall probability of a successful bid based on historical patterns.

Another use might be taking the previously submitted winning bids and having AI produce an auto-generated first draft for new responses that takes context from historical successes.

**Technology Agnostic Design:**
One thing that was missing from the POC (REF: format?) was the initial design was highly tuned to AWS, use of Lambdas and Rust as the function language.

Recognising that this is not portable or particularly cloud agnostic should definitely influence our design decisions.

We should attempt to use a more generic approach like containerisation (REF:) for it's ability to be deployed on any cloud, or on-prem. We should use open standards for core components like REST API's, using JSON for data internchange and standards like OAuth 2.0 for authentication.

This means we won't get painted into a corner when going from building the solution (the Dev part) to deploying and running it i.e. the "Ops" part.

### Best practices

There are a LOT of sources and influences on best practices when it comes to database design, deployment, software engineering and AI/ML.

**Data Engineering:**
If we're going to host this solution in the cloud (again) we can look at the Microsoft or AWS well architected framework guides which inform security, reliability, operational scalability and cost-optimisation at the 'cloud' level.

These also link to DevOps practices like deploying everything using infrastructure as code tools (bicep, terraform, pulumi), using version control for scripts, automated testing and CI/CD pipelines.

**Software Development:**
This covers basic things like clean code principles (REF:), having meaningful code reviews, deployment gates and adhering to the twelve factor app methodology as much as possible (REF:).

**AI/ML best practices:**
We must follow responsible AI principals (REF:) with a human in the loop to check any decision making and ensure accountability

<!--
**References:**
- Azure Architecture Center: Reference architectures for data analytics solutions
- Google SRE Book: Site Reliability Engineering principles
- DAMA-DMBOK: Data Management Body of Knowledge for data governance
- OWASP: Web application security standards and testing guidelines
-->

<!--
● Understand the specific business problems to be addressed and identify all necessary data sources.
● Plan and define the data solution, including any ETL processes or data flows. Consider data formats, sizes, and frequency of updates in the design.
● Choose an appropriate data solution (see list below), focusing on compatibility and scalability. This may be a low-code, no-code, or a coded solution, depending on business needs.
● Develop your data product, conduct comprehensive testing, and automate with scheduling.
● Focus on scalability, performance optimization, security, and regulatory compliance.
● Ensure flexibility for future changes and adherence to best practices.
-->

<!-- Milestone 2
## Design and develop a scalable, secure ETL pipeline proof of concept that adheres to industry best practices.
  - Stakeholder Identification and Needs Analysis
  - Identify key stakeholders involved in the data engineering process and detail their roles.
  - Conduct a needs analysis based on stakeholder feedback, categorizing primary requirements and challenges.
  - Prioritize these needs in alignment with business goals and outline high-level requirements for a data solution.
## ETL Process Requirements and Solution Selection
  - Specify the ETL process requirements, focusing on data types, flow frequency, volume, and data quality standards.
  - Compare and evaluate at least two ETL tools or frameworks (e.g., Apache Airflow vs. AWS Glue) for their alignment with organizational requirements.
  - Justify the selection based on criteria like performance, scalability, security, and regulatory compliance.
-->
