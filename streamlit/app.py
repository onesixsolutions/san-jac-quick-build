"""
San Jac Demo — Streamlit in Snowflake
Unified interface: Cortex Search (doc Q&A) + Cortex Analyst (data Q&A).

Deploy: Snowsight > Projects > Streamlit > + Streamlit App
     or: snow streamlit deploy
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session
import snowflake.cortex as cortex
import json

session = get_active_session()

st.set_page_config(page_title="San Jac AI Assistant", page_icon="🎓", layout="wide")
st.title("San Jac AI Assistant")
st.caption("Powered by Snowflake Cortex | Demo Environment")

tab_search, tab_analyst = st.tabs(["Document Q&A", "Data Q&A"])

# ── Tab 1: Cortex Search ──────────────────────────────────────────────────────
with tab_search:
    st.subheader("Ask questions about San Jac policies & handbooks")
    query = st.text_input("Your question:", placeholder="What is the financial aid appeal process?")

    if query:
        with st.spinner("Searching documents..."):
            results = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                    'SAN_JAC_DEMO.CORTEX.SAN_JAC_DOCS_SEARCH',
                    '{query.replace("'", "''")}',
                    {{'limit': 3}}
                ) AS response
            """).collect()

            response = json.loads(results[0]["RESPONSE"])
            for r in response.get("results", []):
                with st.expander(f"Source: {r.get('file_name', 'unknown')}"):
                    st.write(r.get("content", ""))

# ── Tab 2: Cortex Analyst ─────────────────────────────────────────────────────
with tab_analyst:
    st.subheader("Ask questions about enrollment & student data")
    nl_query = st.text_input(
        "Your question:",
        placeholder="How many students are enrolled in MATH 1314 this term?",
        key="analyst_input"
    )

    if nl_query:
        with st.spinner("Analyzing data..."):
            # Use Cortex Analyst REST API via session
            resp = session.sql(f"""
                SELECT SNOWFLAKE.CORTEX.ANALYST(
                    '{nl_query.replace("'", "''")}',
                    '@SAN_JAC_DEMO.CORTEX.ANALYST_STAGE/semantic_model.yaml'
                ) AS result
            """).collect()

            result = json.loads(resp[0]["RESULT"])
            generated_sql = result.get("sql", "")
            st.code(generated_sql, language="sql")

            if generated_sql:
                try:
                    df = session.sql(generated_sql).to_pandas()
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.warning(f"Could not execute generated SQL: {e}")
