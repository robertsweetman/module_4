# Current State Evaluation and Needs Analysis <!-- 1200 words -->

The eTenders application is designed to eliminate the time wasted reading through 50 emails per day and uses AI to discern which tenders should be responded to.

All the tenders are scraped from the Irish Govt eTenders site and stored in a Postgresql database, hosted as an AWS RDS instance, for processing. REF:

## Data Management

The data load of eTenders is currently carried out in a pretty naive fashion.

Initially the goal was to simple get a proof of concept up and running so very little consideration was given to database design, integration, storage etc.

Putting the eTenders as rows and then reporting against their status within the processing pipeline was the only consideration in the beginning.

### eTenders data rows

The application uses AWS Lamdba's written in Rust so from a basic data-gathering perspective we can make use of Rust's struct objects. REF: Why is this good?

```rust
#[derive(Debug, Serialize, Deserialize, Clone)]
struct TenderRecordRaw {
    title: String,
    resource_id: String,
    ca: String,
    info: String,
    published: String,
    deadline: String,
    procedure: String,
    status: String,
    pdf_url: String,
    awarddate: String,
    value: String,
    cycle: String,
}
```

Initially everything is collected as a String type and then parsed into a more appropriate type.

```rust
#[derive(Debug, Serialize, Deserialize, Clone)]
struct TenderRecord {
    title: String,
    resource_id: i64,
    contracting_authority: String,
    info: String,
    published: Option<NaiveDateTime>,
    deadline: Option<NaiveDateTime>,
    procedure: String,
    status: String,
    pdf_url: String,
    awarddate: Option<NaiveDate>,
    value: Option<BigDecimal>,
    cycle: String,
    bid: Option<i32>,
}
```

This TenderRecord struct is now the base object which is either passed between Lambda's or written to the database. It's not a critical consideration but Rust as a language can perform these sorts of data type changes very quickly. Far faster than other languages, with the possible exception of C.

### Database table design and uses

Each record is stored in a single row, like an excel spreadsheet. There is a unique resource_id per tender so we can use this as a key for "something" but not very much consideration has been given to how to use this data beyond the Machine Learning (ML) training that was carried out initially.

In a prior ML training phase, once the eTenders table contained enough records a percentage were manually labelled as 'tenders we should bid on' and then basic linear regression with tokenisation was run against this training data.

No thought has been given to gaining other insights from the data. It's purely been used as an input to an automated ML/AI process to reduce Sales admin time & to try to avoid missing any tenders which should be looked at by a human.

### Tender PDF information parsing

In most, but not all, cases each tender has an accompanying PDF that contains quite a bit more information about the bid process for that particular tender. These PDF's are not always comprehensive and doesn't always follow the same process but they do supply the AI pipeline a lot of valuable context when it comes to deciding whether to bid on something or not.

However, from a database point of view, the entire PDF content is purely being stored as a long text string in an accompanying pdf_content column which is connected to the main eTenders table via the resource_id key. REF: check this!!



<!--
Evaluate the current state of data management at your organisation, including data source integration, storage, quality, compliance with GDPR/HIPAA, security, and tool effectiveness.
-->

## Key Findings
<!--
Highlight key findings and provide actional recommendations
-->

## Needs Analysis
<!--
Detail a comprehensive needs analysis highlighting data related needs and pain points
-->

<!--

Critically evaluate the design and implementation of organisational data architecture against business initiatives

RUBRIC - B

Analyses organisational data architecture, focusing on its alignment with business initiatives. Provides clear and actionable recommendations for improvement.

RUBRIC - A

Critically evaluates organisational data architecture against business initiatives. Provides a comprehensive and strategic set of recommendations for improvement, supported by clear explanations and persuasive rationale.
-->
