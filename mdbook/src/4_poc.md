# Proof of Concept <!-- 500 -->

Do this part (scraping) in Python initially - inc the ETL piece

Possibly use Jupyter notebooks for this?

The revised architecture can be roughed out in a simple proof of concept using Python to capture the eTenders data from the site, parsing the PDF content and have AI split the content of the PDF into additional fields within the pdf_content table.

Before the advent of AI we'd have used Regex for this last step but now that LLM's can output structured data reliably using a locally hosted LLM (possibly running in a container) is basically free.

This gets us to a point where we can see the entire data space and work with the technical and support teams to get the data into a container they can work with.

Following software development best practice around separation of concerns we can have Python fuctions that carry out discrete steps

1. Scrape the data
2. Parse it into the correct type
3. Retreive the PDF content
4. Parse the PDF content using a local LLM
5. Output the content, store or send it 'somewhere'

If we don't know "where" to send the data at this point we could have multiple functions to do step 5 and just vary the "write" parts at the end of steps 2 and 4.

TODO: have a diagram of this

<!--
Design, implement and debug a data product




RUBRIC - B

Develop a comprehensive data product meeting business requirements, with focus on scalability, performance, security and compliance. Conducts thorough testing and logging

RUBRIC - A

Develops a hightly adaptable, scalable data product exceeding current business needs. Implements a solution with optimized performance and proactive security measures. Provides actionable insights driving business value. Evaluates the use of automation and scheduling
-->
