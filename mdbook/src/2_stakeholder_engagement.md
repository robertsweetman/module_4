# Stakeholder Engegement & crafting a solution <!-- 500 words -->

## Key stakeholders and requirements
<!--
Identify key stakeholders, then gather and prioritise requirements
-->
Key stakeholders are the business leaders responsible for the sales effort in Ireland, the development team who build and deploy internal applications and the support team responsible for ongoing management of their applications.

- **Sales Team**: Focus on usability, visibility, deadline management (core business needs) and winning tenders
- **Development Team**: Emphasis on security, compliance, and authentication (protecting sensitive tender data)
- **Support Team**: Priority on maintainability, alarms, user management, and documentation (keeping the system running smoothly)

<!--
| Stakeholder | Requirements                        | Priority |
|:------------|:-----------------------------------:|---------:|
| Sales Team  | Easy to use, access and update      | High     |
|             | Integrated with Sales Process/CRM   | High     |
|             | Deadline tracking & reminders       | High     |
|             | Tender and Response PDF downloads   | High     |
|             | Search & filtering capabilities *   | Medium   |
|             | Win/loss analysis *                 | Medium   |
|             | Reporting & dashboards              | High     |
|             | Mobile accessibility                | Low      |
| Dev Team    | Scalable                            | Medium   |
|             | Familiar Programming Language       | High     |
|             | Data security & access control      | High     |
|             | GDPR compliance                     | High     |
|             | Backup & disaster recovery          | High     |
|             | API design for integrations         | Medium   |
|             | Database performance optimization   | Medium   |
|             | CI/CD pipeline                      | Medium   |
|             | Infrastructure cost management      | Medium   |
|             | Authentication (SSO/MFA)            | High     |
|             | Audit trails                        | High     |
| Support     | Maintainable                        | High     |
|             | Has logging                         | Medium   |
|             | Alarms when it fails                | High     |
|             | User management & permissions       | High     |
|             | Clear error messages                | Medium   |
|             | Training documentation              | High     |
|             | SLA monitoring                      | Medium   |
|             | Troubleshooting tools               | Medium   |
|             | Backup/restore procedures           | High     |
|             | Usage analytics                     | Low      |
|             | Change management process           | Medium   |
-->

![Requirements](images/Requirements.png)
Figure 3: Business and Technical Requirements

## Research

### Database Options

By taking the characteristics of the data into account we can rule out certain database types.

It's not streaming, unstructured data so no-sql data types aren't really valuable here. While you could consider each tender record to be a "document" there really isn't the update frequency, scalability issues or fault tolerance requirements because we're dealing with less than 3000 records.

We can use a traditional SQL scheme approach because the structure of the data is well understood, it doesn't change often and we can use traditional backup methods rather than having to worry about scaling or data-replication.

- Database schema for tables is well understood
- Database schema doesn't change frequently
- Updates (writes) are infrequent
- Reads are infrequent
- Total data volume is not large (3000 - 5000 records max)  

What is possibly open for debate is how to load/update and interact with the database. Should it be in the cloud? Which one? Should it be hosted on a server or as a service? Which particular flavour of SQL should we use? Postgresql? Microsoft SQL? We can also use several Azure hosted options (Microsoft.com, 2025)

From talking to Technical & Support stakeholders we do know it needs to interact with Microsoft services (Dynamics 365, Fabric) and potentially run in Azure.

We can look at options with a weighting, including a noSQL option for comparison

| Criteria | Weight | Azure SQL | PostgreSQL | Cosmos DB |
|----------|--------|-----------|------------|-----------|
| Sales (M365) Integration | 25% | 8/10 | 8/10 | 7/10 |
| Team Familiarity | 20% | 8/10 | 9/10 | 4/10 |
| Security & Compliance | 20% | 9/10 | 9/10 | 8/10 |
| Cost (3-5k records) | 15% | 6/10 | 9/10 | 5/10 |
| Scalability | 10% | 8/10 | 8/10 | 10/10 |
| Maintainability | 10% | 9/10 | 8/10 | 7/10 |
| **Weighted Score** | | **8.0** | **8.6** | **6.6** |

Figure 4: SWOT Analysis with Weighting

Analysis shows that Azure hosted PostgreSQL is the preferred option, especially because we can also develop the entire solution using locally hosted PostgreSQL to save time initially.

<!--
Using relevant data analysis techniques
  - analyse stakeholder feedback
  - research and compare potential organisational data solutions

Research and compare potential organisational data solutions to generate ideas for developing a data solution

NOTES:
- weighting vs requirements
- SWOT analyse
- ??

-->

## Stakeholder feedback

The commerical team needs to focus primarily on business outcomes and getting feedback on the workflow is far easier when it's explained visually:

```mermaid
flowchart TD
    Start([Daily Tender Check]) --> Gather[Gather Tender Records<br/>from eTenders.gov.ie]
    Gather --> PDF[Extract PDF Content<br/>& Metadata]
    PDF --> CPV{Check CPV Codes<br/>Relevant?}
    
    CPV -->|No| Archive[Archive as<br/>Not Relevant]
    CPV -->|Yes| AI[AI/ML Analysis<br/>Score & Recommend]
    
    AI --> Decision{AI Recommendation<br/>Score > Threshold?}
    Decision -->|No| Archive
    Decision -->|Yes| Alert[Alert Sales Team<br/>via Email/Dashboard]
    
    Alert --> Review[Sales Team Review<br/>in Dashboard]
    Review --> Pursue{Pursue<br/>Tender?}
    
    Pursue -->|No| Declined[Mark as Declined<br/>+ Reason]
    Pursued -->|Yes| BidPrep[Prepare Bid Response]
    
    BidPrep --> UploadDoc[Upload Bid Documents<br/>to Database]
    UploadDoc --> Submit[Submit Tender Response]
    
    Submit --> Track[Track Submission<br/>+ Deadline]
    Track --> Outcome[Await Tender Outcome]
    
    Outcome --> Result{Tender<br/>Result?}
    Result -->|Won| Won[Update: Tender WON<br/>+ Contract Value]
    Result -->|Lost| Lost[Update: Tender LOST<br/>+ Competitor Info]
    
    Won --> Analysis[Analysis Dashboard<br/>Win/Loss Analytics]
    Lost --> Analysis
    Declined --> Analysis
    Archive --> Analysis
    
    Analysis --> Feedback[Feedback Loop:<br/>Improve AI Model]
    Feedback --> Templates[Generate Response<br/>Templates from Wins]
    
    Templates -.->|Improve Future Bids| BidPrep
    Feedback -.->|Retrain Model| AI
    
    Analysis --> Reports[Generate Reports:<br/>- Success Rate by CPV<br/>- Competitor Analysis<br/>- Response Template Library]
    
    Reports --> Start

    style Start fill:#e1f5e1
    style Alert fill:#fff3cd
    style Won fill:#d4edda
    style Lost fill:#f8d7da
    style Analysis fill:#d1ecf1
    style Feedback fill:#cce5ff
    style Templates fill:#d4edda
```

Figure 5: Business Process Flow

We should aim to get technical stakeholder buy in through focusing on data-flow, using standardised tools, ease of support, security, logging and maintainability.

```mermaid
graph TB
    subgraph "External Systems"
        ETenders[eTenders.gov.ie<br/>API]
        M365[Microsoft 365<br/>Dynamics 365]
        Email[Email Service<br/>SMTP/Graph API]
    end
    
    subgraph "Azure Cloud Platform"
        subgraph "Application Layer"
            WebApp[Web Dashboard<br/>ASP.NET/Blazor]
            API[REST API<br/>Authenticated]
            Functions[Azure Functions<br/>Scheduled Tasks]
        end
        
        subgraph "Data Layer"
            PostgreSQL[(Azure PostgreSQL<br/>Managed Service)]
            BlobStorage[Blob Storage<br/>PDF Documents]
            AIService[Azure OpenAI<br/>ML Analysis]
        end
        
        subgraph "Security & Monitoring"
            AAD[Azure AD<br/>SSO/MFA]
            KeyVault[Key Vault<br/>Secrets Management]
            Monitor[Application Insights<br/>Logging & Alerts]
            Backup[Automated Backups<br/>Point-in-Time Recovery]
        end
    end
    
    subgraph "CI/CD Pipeline"
        GitHub[GitHub Repo]
        Actions[GitHub Actions]
        Deploy[Azure DevOps]
    end
    
    ETenders -->|HTTPS| Functions
    Functions -->|Write| PostgreSQL
    Functions -->|Store PDFs| BlobStorage
    Functions -->|AI Analysis| AIService
    
    WebApp -->|Auth| AAD
    API -->|Auth| AAD
    WebApp -->|Query| API
    API -->|Read/Write| PostgreSQL
    API -->|Retrieve PDFs| BlobStorage
    
    PostgreSQL -->|Integration| M365
    API -->|Alerts| Email
    
    API -->|Secrets| KeyVault
    Functions -->|Secrets| KeyVault
    
    WebApp -->|Logs| Monitor
    API -->|Logs| Monitor
    Functions -->|Logs| Monitor
    
    PostgreSQL -->|Daily| Backup
    
    GitHub -->|Trigger| Actions
    Actions -->|Build & Test| Deploy
    Deploy -->|Deploy| WebApp
    Deploy -->|Deploy| Functions
    
    style AAD fill:#0078d4
    style Monitor fill:#ff6b6b
    style KeyVault fill:#ffd93d
    style Backup fill:#6bcf7f
    style PostgreSQL fill:#336791
```

Figure 6: Technical Architecture

We're going to take the Python functions used to develop the proof of concept and re-work them into Azure Functions.

We can also use the PostgreSQL database as a back-end for Microsoft Fabric (abnarain, 2025) which will integrate with incoming email updates about tender awards as well as updates from the Sales Team.

<!--
Generate Ideas for developing a data solution, or update to data architecture
Use data viz tools to present insights and gather initial stakeholder feedback
-->

<!--

Demostrate a funcamental understanding of how to implement a data analytics and/or engineering solution to measure and realise value.

RUBRIC - B

Designs and implements a data solution that meets business requirements. Focuses on scalability, performance optimization, security, and regulatory compliance. Conducts comprehensive testing and automation with scheduling.

RUBRIC - A

Designs and implements a sophisticated data solution that meets business requirements. Focuses on scalability, performance optimization, security, and regulatory compliance. Conducts comprehensive testing and automation with scheduling. Includes flexible design for future changes and adherence to best practices.
-->
