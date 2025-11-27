# Current State Evaluation and Needs Analysis <!-- 1200 words -->

The eTenders application is designed to eliminate the time wasted reading through 50 emails per day and uses AI to discern which tenders should be responded to.

## Data Management

<!-- The data load of eTenders is currently carried out in a pretty naive fashion. -->

Initially the goal was to get a simple proof of concept up and running so very little consideration has been given to database design, integration, storage etc.

Storing the eTenders data as rows and then reporting against their status within the processing pipeline was the only consideration in the beginning.

There is no integration with other data sources, the Postgresql database is hosted in AWS RDS (Amazon Web Services, Inc., 2019) so it's quite accessible from the Rust AWS Lambda code and can be backed up there.

However to reduce costs it is still open to the web (via username and password) since putting it behind an AWS Nat Gateway (AWS, 2020) to increase security costs an additional £30 per month.

The database is accessible via a bastion jumpserver so that developers can run psql queries against it but this is primarly for development purposes. It serves mainly as a state storage device to answer the following questions:

1. Which tenders have already been looked at
2. Where is a particular tender record in the AWS Lambda pipeline process
3. Which tenders have we suggested to the business (via email) should be looked into further

The database of tender records isn't the 'product' in this case. The 'respond to this tender' emails are currently the only product or business value resulting from all this work.

### Database table design

The application uses AWS Lamdba's written in Rust so from a basic data-gathering perspective we can make use of Rust's struct objects. Rust structs (doc.rust-lang.org, n.d.) are essentially custom objects which are the 'record' being moved and modified through the ETL pipeline.

![TenderRecordRaw](../images/TenderRecordRaw.png)

Initially everything is collected as a String type and then parsed into a more appropriate type.

![TenderRecord](../images/TenderRecord.png)

This TenderRecord struct is now the base object which is either passed between Lambda's or written to the database. It's not a critical consideration but Rust as a language can perform these sorts of data type changes very quickly. Rust is faster than other languages, with the possible exception of C/C+ (Vietnam Software Outsourcing - MOR Software, 2016) which are also compiled languages.

#### Tender Records Table

Each record is stored in a single row, like an excel spreadsheet. There is a unique resource_id per tender so we can use this as a key for "something" but not very much consideration has been given to how to use this data beyond the Machine Learning (ML) training that was carried out initially. REF: module_2

In a prior ML training phase, once the eTenders table contained enough records, a percentage were manually labelled as 'tenders we should bid on' and then basic linear regression with tokenisation was run against this training data.

No thought has been given to gaining other insights from the data. It's purely been used as an input to an automated ML/AI process to reduce Sales admin time & to try to avoid missing any tenders which should be looked at by a human.

#### PDF Content Table

In most cases each tender has an accompanying PDF that contains more information about the bid process for that particular tender. These PDF's are not always comprehensive and don't always require the same bid process but they do supply the AI pipeline a lot of valuable context when it comes to deciding whether to bid on something or not.

However, from a database point of view, the entire PDF is being stored as a long text string in an accompanying pdf_content column which is linked to the main eTenders table via the resource_id key.

## Key Findings

From talking to stakeholders there has been some very clear feedback.

Reducing the daily tender analysis time has benefited the sales team but the strictly linear workflow (get, parse, analyse, alert) doesn't really leverage the database to deliver further business value beyond automating this one process. Effectively the business value is somewhat limited, given the maintenance and support requirements.

There are also technical challenges in the way this proof-of-concept (POC) has been delivered:

- Runs in AWS, not Azure
  - The companies own infra runs in Azure so this is a general blocker to wider adoption
  - The support/ops team are not set up to support AWS hosted apps
- Uses Rust for Lambda's
  - The business isn't familiar with Rust and can't support it properly
- The Postgresql database is still open to the internet
  - This is a significant security issue
- While this is a pragmatic solution for a POC it's not okay for any sort of production system

The current implementation blocks further integrations with other business processes and tools, both from a sales/commercial and technical point of view.

<!--
Highlight key findings and provide actional recommendations
-->

<!--
Evaluate the current state of data management at your organisation, including data source integration, storage, quality, compliance with GDPR/HIPAA, security, and tool effectiveness.
-->

## Needs Analysis
<!--
Detail a comprehensive needs analysis highlighting data related needs and pain points
-->
### Business Needs

The organisation needs to place the tender requests firmly within the whole bid response process loop. All the current solution does is use AI to help guard against losing the signal within the noise of up to 50 requests per day. It doesn't really add value beyond that.

How can we capture the tender requests, filter out the ones we (as an IT Solutions Consultancy) are not interested in and tie the success or failure of a particular bid back to the original tender request?

This requires a much more robust and holistic data solution which can be referenced back to other parts of the sales effort.

We could update the database with won and lost tenders to help avoid repeating mistakes associated with losing bids. Another example might be updating the bid database with notifications from the Irish Government about who won bids to understand more about our competitors.

If we append what we send in response to tenders that might even allow us to leverage AI to create bid response templates, improve our ML tender analysis solution with actual "won bid" data and be more confident anything our ML/AI highlights will net a positive return on the time investment to respond to a tender request.

### Technical Needs
<!-- is it POC or PoC -->
Creating a PoC that's hard to manage, is in an unfamiliar language and not in a (cloud) environment that the business at large is familiar with is certainly something we should look to resolve.

If we are going to host a more robust solution in the cloud then it at least needs to be in Microsoft's Azure.

Other database considerations are broadly that it needs to be connectable to the wider 'sales process' environment within Version1. It's no good lobbing this into another proprietary tool that can't connect to (for example) Microsoft 365 solutions and tools.

<!--

Critically evaluate the design and implementation of organisational data architecture against business initiatives

RUBRIC - B

Analyses organisational data architecture, focusing on its alignment with business initiatives. Provides clear and actionable recommendations for improvement.

RUBRIC - A

Critically evaluates organisational data architecture against business initiatives. Provides a comprehensive and strategic set of recommendations for improvement, supported by clear explanations and persuasive rationale.
-->

<!--
# Milestone 1
  - Complete a detailed evaluation and restructure proposal for an existing database architecture, focusing on ACID principles and stakeholder requirements.

## Data Architecture Analysis
  - Map out the existing data sources and describe the relationships between them.
  - Evaluate the alignment of the current architecture with ACID principles, scalability, and performance.
  - Identify pain points related to the data architecture, focusing on areas affecting data quality and accessibility.
## Data Integration Challenges and Solution Proposal
  - Discuss integration challenges (data quality, compliance, security) and their impacts on business operations.
  - Develop a restructuring proposal, prioritizing stakeholder needs and outlining improvements in data flow and quality.
  - Include a brief comparison of two potential architectural solutions or tools, with a focus on security and compliance.

IMPORTANT: Create an ERD in lucidchart
-->

<!-- 
VERY IMPORTANT POINTS FROM REVIEW WITH JOE

1. Where possibe EVALUATE choices against a set of criteria
 - explain
 - analyse
 - pros/cons
 - EVALUATE

2. LO3 is a TRAP 
 - design, implement, DEBUG (examples of how to debug), automation and scheduling 

3. Look at EVERY word in the rubric and make sure it's being covered somehow.
-->