# Stakeholder Engegement & crafting a solution <!-- 500 words -->

## Key stakeholders and requirements
<!--
Identify key stakeholders, then gather and prioritise requirements
-->
Key stakeholders are the business leaders responsible for the sales effort in Ireland, the development team who build and deploy internal applications and the support team responsible for ongoing management of their applications.

Each of these groups have differing requirements, arguably split between business and technical considerations. It's clear that the Development and Support team's focus isn't the same since one is more concerned with building and deploying whereas the second team is more interested in running and maintainability.

- **Sales Team**: Focus on usability, visibility, and deadline management (core business needs)
- **Tech Team**: Emphasis on security, compliance, and authentication (protecting sensitive tender data)
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

![Requirements](../images/Requirements.png)

## Research

### Database Options

Taking the characteristics of the data into account means we can rule out certain database types.

It's not streaming, unstructured data so no-sql/schema less data types aren't really valuable here. While you could consider each tender record to be a "document" there really isn't the update frequency, scalability issues or fault tolerance requirements for less than 3000 records.

We can use a traditional SQL scheme approach because the structure of the data is well understood, it doesn't update 'that' often and we can use traditional backup methods rather than having to worry about scaling or data-replication. (REF: need a table/article justifying this)

What is possibly open for debate is how to load/update and interact with the database. Should it be in the cloud? Which one? Should it be hosted on a server or as a service? Which particular flavour of SQL should we use? Postgresql? Microsoft SQL?

From talking to Technical & Support stakeholders do know it needs to interact with Microsoft services (Dynamics 365) and connect to Azure, if not run on it entirely so that bears more research.

TODO: WHAT ARE THE OPTIONS HERE?

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

TODO: How to do requirements prioritisation? Can we do a swot analysis somehow or other weighting

## Stakeholder feedback

We'll need to present the ideas visually where possible, both from a sales and technical perspective. The Sales component needs to focus primarily on business outcomes.

TODO: Insert a business process flow diagram here which closes the loop and shows enhancing outcomes for the data gathering/tender responding/feedback and improvement process.

TODO: Insert a technical architecture diagram here which focusses on deployability, loggin, auth (security) and maintainability.

We could also list technical options (at least) with reasons why they were rejected.

This also needs to mention testing and flexible design.

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
