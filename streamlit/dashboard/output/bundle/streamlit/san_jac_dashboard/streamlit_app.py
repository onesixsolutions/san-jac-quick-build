import streamlit as st
import json

st.set_page_config(
    page_title="San Jacinto College — Institutional Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)

# ── Snowflake connection ──
from snowflake.snowpark.context import get_active_session
session = get_active_session()

SEMANTIC_VIEW = "SAN_JAC_DEMO.CORTEX.SAN_JAC_ANALYTICS"

# ── Sidebar ──
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0;">
            <h2 style="color: #ffc61e; margin-bottom: 0;">San Jacinto College</h2>
            <p style="color: #dfeaf4; font-size: 0.85rem; margin-top: 0.25rem;">Institutional Research Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    terms_df = session.sql(
        "SELECT TERM_ID, TERM_NAME FROM SAN_JAC_DEMO.ANALYTICS.DIM_TERM ORDER BY START_DATE DESC"
    ).to_pandas()
    term_options = dict(zip(terms_df["TERM_NAME"], terms_df["TERM_ID"]))
    selected_term_name = st.selectbox("Academic Term", list(term_options.keys()))
    selected_term = term_options[selected_term_name]

    campus_df = session.sql(
        "SELECT CAMPUS_ID, CAMPUS_NAME FROM SAN_JAC_DEMO.ANALYTICS.DIM_CAMPUS ORDER BY CAMPUS_NAME"
    ).to_pandas()
    campus_list = ["All Campuses"] + campus_df["CAMPUS_NAME"].tolist()
    selected_campus = st.selectbox("Campus", campus_list)

    st.divider()
    st.caption("Data refreshed from SAN_JAC_DEMO.ANALYTICS")


# ── Helper: build WHERE clause ──
def campus_filter(alias="e", campus_col="CAMPUS_ID"):
    if selected_campus == "All Campuses":
        return ""
    cid = campus_df[campus_df["CAMPUS_NAME"] == selected_campus]["CAMPUS_ID"].iloc[0]
    return f" AND {alias}.{campus_col} = '{cid}'"


# ── Tab layout ──
tab_kpi, tab_analyst, tab_lifecycle = st.tabs(
    [":chart_with_upwards_trend: KPI Overview", ":speech_balloon: Ask the Data", ":busts_in_silhouette: Student Lifecycle"]
)

# ════════════════════════════════════════
# TAB 1: KPI Overview
# ════════════════════════════════════════
with tab_kpi:
    st.subheader(f"Key Performance Indicators — {selected_term_name}")

    # ── KPI queries ──
    kpi_sql = f"""
    SELECT
        COUNT(DISTINCT e.STUDENT_ID) AS headcount,
        ROUND(SUM(CASE WHEN e.TOTAL_SCH_ATTEMPTED >= 12 THEN 1 ELSE 0 END) * 100.0
              / NULLIF(COUNT(DISTINCT e.STUDENT_ID), 0), 1) AS ft_rate,
        ROUND(SUM(CASE WHEN e.IS_ONLINE_ONLY = TRUE THEN 1 ELSE 0 END) * 100.0
              / NULLIF(COUNT(*), 0), 1) AS online_rate,
        ROUND(SUM(CASE WHEN e.WITHDREW_TERM = TRUE THEN 1 ELSE 0 END) * 100.0
              / NULLIF(COUNT(*), 0), 1) AS withdrawal_rate
    FROM SAN_JAC_DEMO.ANALYTICS.FACT_ENROLLMENT e
    WHERE e.TERM_ID = '{selected_term}'{campus_filter()}
    """
    kpi = session.sql(kpi_sql).to_pandas()

    success_sql = f"""
    SELECT
        ROUND(SUM(CASE WHEN ca.AC_SUCCESS = TRUE THEN 1 ELSE 0 END) * 100.0
              / NULLIF(COUNT(*), 0), 1) AS ac_success_rate
    FROM SAN_JAC_DEMO.ANALYTICS.FACT_COURSE_ATTEMPT ca
    WHERE ca.TERM_ID = '{selected_term}'{campus_filter("ca")}
    """
    success = session.sql(success_sql).to_pandas()

    pell_sql = f"""
    SELECT ROUND(SUM(CASE WHEN s.PELL_ELIGIBLE = TRUE THEN 1 ELSE 0 END) * 100.0
                 / NULLIF(COUNT(*), 0), 1) AS pell_rate
    FROM SAN_JAC_DEMO.ANALYTICS.FACT_ENROLLMENT e
    JOIN SAN_JAC_DEMO.ANALYTICS.DIM_STUDENT s ON e.STUDENT_ID = s.STUDENT_ID
    WHERE e.TERM_ID = '{selected_term}'{campus_filter()}
    """
    pell = session.sql(pell_sql).to_pandas()

    # ── KPI cards ──
    k1, k2, k3 = st.columns(3)
    k1.metric("Enrollment", f"{int(kpi['HEADCOUNT'].iloc[0]):,}")
    k2.metric("Full-Time Rate", f"{kpi['FT_RATE'].iloc[0]}%")
    k3.metric("A-C Success Rate", f"{success['AC_SUCCESS_RATE'].iloc[0]}%")

    k4, k5, k6 = st.columns(3)
    k4.metric("Withdrawal Rate", f"{kpi['WITHDRAWAL_RATE'].iloc[0]}%")
    k5.metric("Pell Eligible", f"{pell['PELL_RATE'].iloc[0]}%")
    k6.metric("Online-Only", f"{kpi['ONLINE_RATE'].iloc[0]}%")

    st.divider()

    # ── Trend + Demographics charts ──
    col_trend, col_demo = st.columns(2)

    with col_trend:
        st.markdown("**Enrollment by Term**")
        trend_sql = """
        SELECT t.TERM_NAME, COUNT(DISTINCT e.STUDENT_ID) AS headcount
        FROM SAN_JAC_DEMO.ANALYTICS.FACT_ENROLLMENT e
        JOIN SAN_JAC_DEMO.ANALYTICS.DIM_TERM t ON e.TERM_ID = t.TERM_ID
        GROUP BY t.TERM_NAME, t.START_DATE
        ORDER BY t.START_DATE
        """
        trend = session.sql(trend_sql).to_pandas()
        st.bar_chart(trend, x="TERM_NAME", y="HEADCOUNT")

    with col_demo:
        st.markdown("**Enrollment by Ethnicity**")
        demo_sql = f"""
        SELECT s.ETHNICITY, COUNT(DISTINCT e.STUDENT_ID) AS students
        FROM SAN_JAC_DEMO.ANALYTICS.FACT_ENROLLMENT e
        JOIN SAN_JAC_DEMO.ANALYTICS.DIM_STUDENT s ON e.STUDENT_ID = s.STUDENT_ID
        WHERE e.TERM_ID = '{selected_term}'{campus_filter()}
        GROUP BY s.ETHNICITY
        ORDER BY students DESC
        """
        demo = session.sql(demo_sql).to_pandas()
        st.bar_chart(demo, x="ETHNICITY", y="STUDENTS")

    # ── Program table ──
    st.markdown("**Top Programs by Enrollment**")
    prog_sql = f"""
    SELECT p.AREA_OF_STUDY, p.PROGRAM_NAME,
           COUNT(DISTINCT e.STUDENT_ID) AS enrolled,
           ROUND(AVG(e.TOTAL_SCH_COMPLETED), 1) AS avg_sch
    FROM SAN_JAC_DEMO.ANALYTICS.FACT_ENROLLMENT e
    JOIN SAN_JAC_DEMO.ANALYTICS.DIM_PROGRAM p ON e.PROGRAM_ID = p.PROGRAM_ID
    WHERE e.TERM_ID = '{selected_term}'{campus_filter()}
    GROUP BY p.AREA_OF_STUDY, p.PROGRAM_NAME
    ORDER BY enrolled DESC
    LIMIT 15
    """
    prog = session.sql(prog_sql).to_pandas()
    st.dataframe(prog, hide_index=True, use_container_width=True)


# ════════════════════════════════════════
# TAB 2: Ask the Data (Cortex Analyst)
# ════════════════════════════════════════
with tab_analyst:
    st.subheader("Ask the Data")
    st.caption("Ask natural language questions about enrollment, student success, financial aid, and outcomes. Powered by Cortex Analyst.")

    if "analyst_messages" not in st.session_state:
        st.session_state.analyst_messages = []

    # Display history
    for msg in st.session_state.analyst_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sql"):
                with st.expander("Generated SQL"):
                    st.code(msg["sql"], language="sql")
            if msg.get("dataframe") is not None:
                st.dataframe(msg["dataframe"], hide_index=True, use_container_width=True)

    # Suggestions
    ANALYST_SUGGESTIONS = [
        "What is the Fall-to-Fall persistence rate?",
        "Show A-C success rate by ethnicity and gender",
        "Which gateway courses have the lowest success rate?",
        "How does financial aid unmet need vary by aid type?",
    ]
    if not st.session_state.analyst_messages:
        selected = st.selectbox("Try asking:", [""] + ANALYST_SUGGESTIONS, index=0, label_visibility="collapsed")
        if selected:
            st.session_state.analyst_messages.append({"role": "user", "content": selected})
            st.rerun()

    if prompt := st.chat_input("Ask about student data...", key="analyst_input"):
        st.session_state.analyst_messages.append({"role": "user", "content": prompt})
        st.rerun()

    # Process last unanswered message
    if (
        st.session_state.analyst_messages
        and st.session_state.analyst_messages[-1]["role"] == "user"
    ):
        user_msg = st.session_state.analyst_messages[-1]["content"]

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                analyst_sql = f"""
                SELECT SNOWFLAKE.CORTEX.ANALYST(
                    '{SEMANTIC_VIEW}',
                    $${json.dumps([{{"role": "user", "content": [{{"type": "text", "text": user_msg}}]}}])}$$
                ) AS response
                """
                result = session.sql(analyst_sql).collect()

            analyst_text = ""
            sql_query = None
            result_df = None

            if result:
                response = json.loads(result[0]["RESPONSE"])
                message = response.get("message", {})
                for item in message.get("content", []):
                    if item.get("type") == "text":
                        analyst_text += item["text"] + "\n"
                    elif item.get("type") == "sql":
                        sql_query = item["statement"]

                if sql_query:
                    try:
                        result_df = session.sql(sql_query).to_pandas()
                    except Exception as e:
                        analyst_text += f"\n*Query error: {e}*"

            if analyst_text:
                st.write(analyst_text.strip())
            if sql_query:
                with st.expander("Generated SQL"):
                    st.code(sql_query, language="sql")
            if result_df is not None and not result_df.empty:
                st.dataframe(result_df, hide_index=True, use_container_width=True)
                if len(result_df.columns) >= 2 and len(result_df) > 1:
                    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
                    non_numeric = [c for c in result_df.columns if c not in numeric_cols]
                    if numeric_cols and non_numeric:
                        st.bar_chart(result_df, x=non_numeric[0], y=numeric_cols[0])

            msg_data = {
                "role": "assistant",
                "content": analyst_text.strip() or "Here are the results:",
                "sql": sql_query,
            }
            if result_df is not None:
                msg_data["dataframe"] = result_df
            st.session_state.analyst_messages.append(msg_data)


# ════════════════════════════════════════
# TAB 3: Student Lifecycle
# ════════════════════════════════════════
with tab_lifecycle:
    st.subheader("Student Lifecycle — TargetX Stage Distribution")
    st.caption("Current distribution of students across TargetX CRM stages with average time in each stage.")

    lifecycle_sql = f"""
    SELECT ds.STAGE_NAME, ds.SORT_ORDER,
           COUNT(DISTINCT ssh.STUDENT_ID) AS students,
           ROUND(AVG(COALESCE(ssh.DAYS_IN_STAGE,
                 DATEDIFF('day', ssh.STAGE_START_DATE, CURRENT_DATE()))), 0) AS avg_days
    FROM SAN_JAC_DEMO.ANALYTICS.FACT_STUDENT_STAGE_HISTORY ssh
    JOIN SAN_JAC_DEMO.ANALYTICS.DIM_STAGE ds ON ssh.STAGE_ID = ds.STAGE_ID
    WHERE ssh.STAGE_END_DATE IS NULL
    GROUP BY ds.STAGE_NAME, ds.SORT_ORDER
    ORDER BY ds.SORT_ORDER
    """
    lifecycle = session.sql(lifecycle_sql).to_pandas()

    # Funnel-style bar chart
    st.markdown("**Students by Current Stage**")
    st.bar_chart(lifecycle, x="STAGE_NAME", y="STUDENTS")

    # Detail table
    st.markdown("**Stage Details**")
    display_df = lifecycle[["STAGE_NAME", "STUDENTS", "AVG_DAYS"]].copy()
    display_df.columns = ["Stage", "Students", "Avg. Days in Stage"]
    st.dataframe(display_df, hide_index=True, use_container_width=True)

    # Stop-Out and Recruit-Back callouts
    col_so, col_rb = st.columns(2)
    with col_so:
        so_row = lifecycle[lifecycle["STAGE_NAME"].str.contains("Stop", case=False, na=False)]
        so_count = int(so_row["STUDENTS"].iloc[0]) if not so_row.empty else 0
        so_days = int(so_row["AVG_DAYS"].iloc[0]) if not so_row.empty else 0
        st.metric("Stop-Out Students", f"{so_count:,}")
        st.caption(f"Average {so_days} days since last enrollment")

    with col_rb:
        rb_row = lifecycle[lifecycle["STAGE_NAME"].str.contains("Recruit", case=False, na=False)]
        rb_count = int(rb_row["STUDENTS"].iloc[0]) if not rb_row.empty else 0
        rb_days = int(rb_row["AVG_DAYS"].iloc[0]) if not rb_row.empty else 0
        st.metric("Recruit-Back Students", f"{rb_count:,}")
        st.caption(f"Average {rb_days} days stalled in registration")