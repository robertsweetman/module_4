# Impact Assessment and Recommendations for Rollout <!-- 800 words -->

Let's not forget that SALES generate REVENUE

## Data product goals

- Pass a security audit
- Microsoft security tools/checking

## Data product monitoring

How/what tools can be used for Fabrik here (REF: to microsoft docs)

## Business Wins

NOTE: FOCUS MOST OF THE CONTENT OF THIS SECTION HERE!!

How do you visualize this properly? visualisations!!

## Implementation and Rollout Plan

<!-- markdownlint-disable MD033 -->
<style>
  /* Default for dark themes - white text */
  .mermaid text {
    fill: white !important;
  }
  .mermaid .taskText,
  .mermaid .sectionTitle,
  .mermaid .grid text,
  .mermaid .tickText,
  .mermaid .titleText,
  .mermaid .labelText,
  .mermaid .loopText,
  .mermaid .actor text {
    fill: white !important;
  }
  
  /* Handle mdBook light and rust themes - black text */
  html.light .mermaid text,
  html.light .mermaid .taskText,
  html.light .mermaid .sectionTitle,
  html.light .mermaid .grid text,
  html.light .mermaid .tickText,
  html.light .mermaid .titleText,
  html.light .mermaid .labelText,
  html.light .mermaid .loopText,
  html.light .mermaid .actor text,
  html.rust .mermaid text,
  html.rust .mermaid .taskText,
  html.rust .mermaid .sectionTitle,
  html.rust .mermaid .grid text,
  html.rust .mermaid .tickText,
  html.rust .mermaid .titleText,
  html.rust .mermaid .labelText,
  html.rust .mermaid .loopText,
  html.rust .mermaid .actor text {
    fill: black !important;
  }
  
  /* Ensure dark themes have white text */
  html.navy .mermaid text,
  html.navy .mermaid .taskText,
  html.navy .mermaid .sectionTitle,
  html.navy .mermaid .grid text,
  html.navy .mermaid .tickText,
  html.navy .mermaid .titleText,
  html.navy .mermaid .labelText,
  html.navy .mermaid .loopText,
  html.navy .mermaid .actor text,
  html.ayu .mermaid text,
  html.ayu .mermaid .taskText,
  html.ayu .mermaid .sectionTitle,
  html.ayu .mermaid .grid text,
  html.ayu .mermaid .tickText,
  html.ayu .mermaid .titleText,
  html.ayu .mermaid .labelText,
  html.ayu .mermaid .loopText,
  html.ayu .mermaid .actor text,
  html.coal .mermaid text,
  html.coal .mermaid .taskText,
  html.coal .mermaid .sectionTitle,
  html.coal .mermaid .grid text,
  html.coal .mermaid .tickText,
  html.coal .mermaid .titleText,
  html.coal .mermaid .labelText,
  html.coal .mermaid .loopText,
  html.coal .mermaid .actor text {
    fill: white !important;
  }
  
  /* Ensure links and other specific elements have correct colors in light themes */
  html.light .mermaid .flowchart-link,
  html.rust .mermaid .flowchart-link {
    stroke: #333 !important;
  }
  
  /* Ensure links have correct colors in dark themes */
  html.navy .mermaid .flowchart-link,
  html.ayu .mermaid .flowchart-link,
  html.coal .mermaid .flowchart-link {
    stroke: #ccc !important;
  }
  
  /* Additional styles for better visibility in all themes */
  .mermaid .grid path {
    stroke-opacity: 0.5;
  .mermaid .today {
    stroke-width: 2px;
  }
</style>
<!-- markdownlint-enable MD033 -->

```mermaid
gantt
    title Prototype
    dateFormat YYYY-MM-DD
    axisFormat %b '%y
    tickInterval 1month

    Stakeholders Discussion :a1, 2025-07-01, 2w
    Data Gathering         :a2, after a1, 3w
    Prototype              :a3, after a2, 5w
    Stakeholders Review :crit, a4, after a3, 1w
    Go/No-Go Decision       :crit, milestone, a5, after a4, 0d
```

```mermaid
gantt
    title Development
    dateFormat YYYY-MM-DD
    axisFormat %b '%y
    tickInterval 1month

    Architecture :a1, 2025-10-01, 2w
    Planning :crit, a2, 2025-10-01, 2w
    Sprint 1 :a3, after a2, 2w
    Sprint 2 :a4, after a3, 2w
    Sprint 3 :a5, after a4, 2w
    Sprint 4 :a6, after a5, 2w
```

```mermaid
gantt
    title Deployment
    dateFormat YYYY-MM-DD
    axisFormat %b '%y
    tickInterval 1month

    IaC deployment :a1, 2026-01-01, 1w
    Smoke Test :a2, after a1, 3w
    Go/No-Go Live :milestone, crit, a3, after a2, 0d
    Live Trial :a4, after a3, 2w
    Gather User Feedback :a5, after a4, 2w
    Update Model :crit, a6, after a5, 2w
```

<!--
● Set measurable goals for your data product, aiming for improvements in data processing speed, accuracy, and resource efficiency.
● Monitor improvements in processing time, data quality, resource utilisation, scalability, and error rates.
● Assess impacts on user productivity, business decision-making, cost savings, and revenue. Collect user feedback to gauge satisfaction and ease of use.
● Compile findings into a comprehensive report with visualisations for clarity.
-->

<!--

Develops a value analysis showing the potential impact of a data-driven solution and distinctly justify your approach to stakeholders (K14)

RUBRIC - B

Develops a value analysis that quantifies the potential impact of a data-driven solution across multiple business metrics. Includes thorough analysis of stakeholder needs from key departments. Provides a clear implementation plan with defined milestones.

RUBRIC - A

Develops a multi-faceted value analysis that quantifies short-term and long term impacts of a data-driven solution, including ROI projections. Incorporating analysis of stakeholder needs across all levels of the organisation. Provides a detailed implementation plan with phased rollout strategy, specific KPI's for each phase and contingency plans.

-->
