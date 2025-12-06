"""
eTenders Dashboard - Interactive visualization of tender data
"""

import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(
    page_title="eTenders Dashboard",
    page_icon="🇮🇪",
    layout="wide"
)

# Database connection
@st.cache_resource
def get_engine():
    """Create SQLAlchemy engine"""
    db_url = f"postgresql://{os.getenv('DB_USER', 'etenders_user')}:{os.getenv('DB_PASSWORD', 'etenders_pass')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'etenders_db')}"
    return create_engine(db_url)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(query):
    """Execute query and return dataframe"""
    engine = get_engine()
    df = pd.read_sql(query, engine)
    return df

# Header
st.title("🇮🇪 eTenders Intelligence Dashboard")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_tenders = load_data("SELECT COUNT(*) as count FROM etenders_core")
    st.metric("Total Tenders", f"{total_tenders['count'].iloc[0]:,}")

with col2:
    analyzed = load_data("SELECT COUNT(*) as count FROM bid_analysis")
    st.metric("AI Analyzed", f"{analyzed['count'].iloc[0]:,}")

with col3:
    recommended = load_data("""
        SELECT COUNT(*) as count 
        FROM bid_analysis 
        WHERE should_bid = TRUE
    """)
    st.metric("🎯 Recommended Bids", f"{recommended['count'].iloc[0]:,}", 
              delta=f"{(recommended['count'].iloc[0] / total_tenders['count'].iloc[0] * 100):.1f}%" if total_tenders['count'].iloc[0] > 0 else "0%")

with col4:
    total_value = load_data("""
        SELECT COALESCE(SUM(ec.estimated_value_numeric), 0) as total
        FROM etenders_core ec
        JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
        WHERE ba.should_bid = TRUE
        AND ec.estimated_value_numeric IS NOT NULL
    """)
    value = total_value['total'].iloc[0]
    st.metric("💰 Recommended Value", f"€{value:,.0f}" if value else "€0")

with col5:
    avg_confidence = load_data("""
        SELECT AVG(confidence) as avg
        FROM bid_analysis
        WHERE should_bid = TRUE
    """)
    conf = avg_confidence['avg'].iloc[0]
    st.metric("Avg Confidence", f"{conf:.0%}" if pd.notna(conf) else "N/A")

st.markdown("---")

# Two column layout for charts
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 AI Bid Recommendations")
    
    # Pie chart of recommendations
    bid_breakdown = load_data("""
        SELECT 
            CASE 
                WHEN should_bid = TRUE THEN 'Recommended'
                WHEN should_bid = FALSE THEN 'Not Recommended'
                ELSE 'Not Analyzed'
            END as recommendation,
            COUNT(*) as count
        FROM etenders_core ec
        LEFT JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
        GROUP BY recommendation
    """)
    
    fig_pie = px.pie(
        bid_breakdown, 
        values='count', 
        names='recommendation',
        color='recommendation',
        color_discrete_map={
            'Recommended': '#00CC66',
            'Not Recommended': '#FF6B6B',
            'Not Analyzed': '#CCCCCC'
        },
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=True, height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.subheader("💵 Value by Recommendation")
    
    # Bar chart of value distribution
    value_breakdown = load_data("""
        SELECT 
            CASE 
                WHEN ba.should_bid = TRUE THEN 'Recommended'
                WHEN ba.should_bid = FALSE THEN 'Not Recommended'
            END as recommendation,
            COUNT(*) as tender_count,
            COALESCE(SUM(ec.estimated_value_numeric), 0) as total_value
        FROM etenders_core ec
        JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
        WHERE ec.estimated_value_numeric IS NOT NULL
        GROUP BY recommendation
    """)
    
    fig_bar = px.bar(
        value_breakdown,
        x='recommendation',
        y='total_value',
        text='tender_count',
        color='recommendation',
        color_discrete_map={
            'Recommended': '#00CC66',
            'Not Recommended': '#FF6B6B'
        },
        labels={'total_value': 'Total Value (€)', 'recommendation': 'AI Recommendation'}
    )
    fig_bar.update_traces(texttemplate='%{text} tenders', textposition='outside')
    fig_bar.update_layout(showlegend=False, height=350, yaxis_tickformat='€,.0f')
    st.plotly_chart(fig_bar, use_container_width=True)

# Confidence distribution
st.subheader("🎲 AI Confidence Distribution")
confidence_data = load_data("""
    SELECT 
        confidence,
        should_bid,
        estimated_value_numeric as value
    FROM bid_analysis ba
    JOIN etenders_core ec ON ba.resource_id = ec.resource_id
    WHERE confidence IS NOT NULL
""")

if len(confidence_data) > 0:
    fig_scatter = px.scatter(
        confidence_data,
        x='confidence',
        y='value',
        color='should_bid',
        color_discrete_map={True: '#00CC66', False: '#FF6B6B'},
        labels={
            'confidence': 'AI Confidence Score',
            'value': 'Estimated Value (€)',
            'should_bid': 'Recommended'
        },
        hover_data={'confidence': ':.0%', 'value': ':,.0f'}
    )
    fig_scatter.update_layout(height=400, xaxis_tickformat='.0%', yaxis_tickformat='€,.0f')
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("No confidence data available yet")

# Timeline
st.subheader("📅 Tender Timeline - Recommended Bids")
timeline_data = load_data("""
    SELECT 
        DATE_TRUNC('week', ec.date_published_parsed) as week,
        COUNT(*) as tender_count,
        SUM(ec.estimated_value_numeric) as total_value
    FROM etenders_core ec
    JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
    WHERE ba.should_bid = TRUE
    AND ec.date_published_parsed IS NOT NULL
    GROUP BY week
    ORDER BY week DESC
    LIMIT 12
""")

if len(timeline_data) > 0:
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(
        x=timeline_data['week'],
        y=timeline_data['tender_count'],
        name='Tender Count',
        marker_color='#00CC66'
    ))
    fig_timeline.update_layout(
        height=300,
        xaxis_title='Week',
        yaxis_title='Number of Recommended Tenders',
        showlegend=False
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("No timeline data available yet")

# Top Recommended Tenders
st.subheader("🏆 Top Recommended Opportunities")

top_tenders = load_data("""
    SELECT 
        ec.resource_id,
        ec.title,
        ec.contracting_authority,
        ec.estimated_value_numeric as value,
        ec.submission_deadline_parsed as deadline,
        ba.confidence,
        ba.reasoning
    FROM etenders_core ec
    JOIN bid_analysis ba ON ec.resource_id = ba.resource_id
    WHERE ba.should_bid = TRUE
    ORDER BY ba.confidence DESC, ec.estimated_value_numeric DESC
    LIMIT 10
""")

if len(top_tenders) > 0:
    # Format the dataframe
    display_df = top_tenders.copy()
    display_df['value'] = display_df['value'].apply(lambda x: f"€{x:,.0f}" if pd.notna(x) else "N/A")
    display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "N/A")
    display_df['deadline'] = pd.to_datetime(display_df['deadline']).dt.strftime('%Y-%m-%d')
    
    # Rename columns for display
    display_df = display_df.rename(columns={
        'resource_id': 'ID',
        'title': 'Title',
        'contracting_authority': 'Authority',
        'value': 'Value',
        'deadline': 'Deadline',
        'confidence': 'Confidence',
        'reasoning': 'AI Reasoning'
    })
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400,
        column_config={
            "Title": st.column_config.TextColumn("Title", width="large"),
            "AI Reasoning": st.column_config.TextColumn("AI Reasoning", width="large")
        }
    )
else:
    st.info("No recommended tenders found yet. Run the pipeline with --analyze-bids flag.")

# Statistics sidebar
with st.sidebar:
    st.header("📈 Database Stats")
    
    # Record counts
    st.metric("PDFs Parsed", load_data("SELECT COUNT(*) as c FROM etenders_pdf WHERE pdf_parsed = TRUE")['c'].iloc[0])
    st.metric("CPV Validated", load_data("SELECT COUNT(*) as c FROM cpv_checker WHERE has_validated_cpv = TRUE")['c'].iloc[0])
    
    st.markdown("---")
    
    # Value ranges
    st.subheader("Value Distribution")
    value_ranges = load_data("""
        SELECT 
            CASE 
                WHEN estimated_value_numeric < 50000 THEN '< €50k'
                WHEN estimated_value_numeric < 100000 THEN '€50k - €100k'
                WHEN estimated_value_numeric < 250000 THEN '€100k - €250k'
                WHEN estimated_value_numeric < 500000 THEN '€250k - €500k'
                ELSE '> €500k'
            END as range,
            COUNT(*) as count
        FROM etenders_core
        WHERE estimated_value_numeric IS NOT NULL
        GROUP BY range
        ORDER BY MIN(estimated_value_numeric)
    """)
    
    for _, row in value_ranges.iterrows():
        st.text(f"{row['range']}: {row['count']}")
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("Data updates every 5 minutes")
    st.caption(f"Last loaded: {datetime.now().strftime('%H:%M:%S')}")

# Footer
st.markdown("---")
st.caption("eTenders Intelligence Dashboard | Data from etenders.gov.ie")
