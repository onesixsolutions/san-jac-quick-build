import streamlit as st
import json

st.set_page_config(
    page_title="San Jacinto College Advisor",
    page_icon="🎓",
    layout="wide",
)

# ── Snowflake connection ──
from snowflake.snowpark.context import get_active_session
session = get_active_session()

# ── Constants ──
SEARCH_SERVICE = "SAN_JAC_DEMO.CORTEX.SAN_JAC_SEARCH"
SEMANTIC_VIEW = "SAN_JAC_DEMO.CORTEX.SAN_JAC_ANALYTICS"
LLM_MODEL = "claude-3-5-sonnet"

SEARCH_SUGGESTIONS = {
    "What are the prerequisites for College Algebra?": "course lookup",
    "What CPD programs are available for petrochemical workers?": "program search",
    "How does the Stop-Out stage work in the student lifecycle?": "lifecycle info",
    "What is pathway velocity?": "metrics definition",
}

ANALYST_SUGGESTIONS = {
    "How many students are enrolled each term?": "enrollment",
    "What is the A-C success rate by delivery mode?": "course success",
    "How do Pell-eligible students compare to non-Pell on course success?": "equity gap",
    "Which programs have the most enrolled students?": "program enrollment",
}

# ── Sidebar ──
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0;">
            <h2 style="color: #ffc61e; margin-bottom: 0;">San Jacinto College</h2>
            <p style="color: #dfeaf4; font-size: 0.85rem; margin-top: 0.25rem;">Your Goals. Your College.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    mode = st.radio(
        "Assistant Mode",
        ["Catalog & Policy Search", "Student Data Analyst"],
        help="**Catalog Search** queries course catalog, program info, and policy docs.\n\n**Student Data Analyst** answers questions about enrollment, success metrics, and financial aid using live data.",
    )

    if mode == "Catalog & Policy Search":
        st.markdown("##### Filter by Document Type")
        doc_types = {
            "Courses": "course",
            "Programs": "program",
            "Student Lifecycle": "lifecycle",
            "Success Metrics": "metrics",
            "Statistics": "statistics",
            "Overview": "overview",
            "Use Cases": "use-case",
        }
        selected_types = []
        for label, val in doc_types.items():
            if st.checkbox(label, value=True, key=f"dt_{val}"):
                selected_types.append(val)

    st.divider()
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Header ──
st.title("San Jacinto College AI Advisor")
if mode == "Catalog & Policy Search":
    st.caption("Ask questions about courses, programs, prerequisites, policies, and student lifecycle stages.")
else:
    st.caption("Ask questions about enrollment, student success, financial aid, and institutional metrics using live data.")


# ── Cortex Search function ──
def search_catalog(query, doc_type_filter=None, limit=5):
    filter_obj = {}
    if doc_type_filter and len(doc_type_filter) < 7:
        filter_obj = {"@or": [{"@eq": {"DOC_TYPE": t}} for t in doc_type_filter]}

    search_params = {
        "query": query,
        "columns": ["CHUNK_ID", "CONTENT", "DOC_TYPE", "DOC_TITLE", "SOURCE_FILE"],
        "limit": limit,
    }
    if filter_obj:
        search_params["filter"] = filter_obj

    result = session.sql(
        f"""SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                '{SEARCH_SERVICE}',
                $${json.dumps(search_params)}$$
            )
        ):results::VARCHAR AS results"""
    ).collect()

    return json.loads(result[0]["RESULTS"]) if result else []


# ── RAG answer function ──
def generate_search_answer(query, search_results):
    context = "\n\n---\n\n".join(
        [f"[{r.get('DOC_TITLE', 'Unknown')}]\n{r['CONTENT']}" for r in search_results]
    )
    prompt = f"""You are a helpful academic advisor at San Jacinto College, a community college in the Houston, Texas area.
Answer the following question using ONLY the provided context. If the context does not contain enough information, say so.
Be concise, professional, and supportive. Use bullet points when listing multiple items.
Always refer to the institution as "San Jacinto College" on first reference and "the College" afterward.

Context:
{context}

Question: {query}

Answer:"""

    from snowflake.cortex import complete
    return complete(LLM_MODEL, prompt, session=session, stream=True)


# ── Cortex Analyst function ──
def query_analyst(query):
    sql = f"""
    SELECT SNOWFLAKE.CORTEX.ANALYST(
        '{SEMANTIC_VIEW}',
        $${json.dumps([{{"role": "user", "content": [{{"type": "text", "text": query}}]}}])}$$
    ) AS response
    """
    result = session.sql(sql).collect()
    if not result:
        return None, None, None

    response = json.loads(result[0]["RESPONSE"])
    message = response.get("message", {})
    content_items = message.get("content", [])

    text_parts = []
    sql_query = None
    for item in content_items:
        if item.get("type") == "text":
            text_parts.append(item["text"])
        elif item.get("type") == "sql":
            sql_query = item["statement"]

    analyst_text = "\n".join(text_parts) if text_parts else ""

    result_df = None
    if sql_query:
        try:
            result_df = session.sql(sql_query).to_pandas()
        except Exception as e:
            analyst_text += f"\n\n*Error executing generated query: {e}*"

    return analyst_text, sql_query, result_df


# ── Display chat history ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar")):
        if msg.get("sql"):
            st.write(msg["content"])
            with st.expander("Generated SQL"):
                st.code(msg["sql"], language="sql")
            if msg.get("dataframe") is not None:
                st.dataframe(msg["dataframe"], hide_index=True, use_container_width=True)
        elif msg.get("sources"):
            st.write(msg["content"])
            with st.expander(f"Sources ({len(msg['sources'])} documents)"):
                for src in msg["sources"]:
                    st.markdown(f"- **{src['title']}** ({src['type']}) — {src['file']}")
        else:
            st.write(msg["content"])

# ── Suggestion chips ──
if not st.session_state.messages:
    suggestions = SEARCH_SUGGESTIONS if mode == "Catalog & Policy Search" else ANALYST_SUGGESTIONS
    selected = st.selectbox("Try asking:", [""] + list(suggestions.keys()), index=0, label_visibility="collapsed")
    if selected:
        st.session_state.messages.append({"role": "user", "content": selected})
        st.rerun()


# ── Handle new input ──
if prompt := st.chat_input("Ask a question about San Jacinto College..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# ── Process last user message if unanswered ──
if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
):
    user_msg = st.session_state.messages[-1]["content"]

    # Generate response
    with st.chat_message("assistant", avatar="🎓"):
        if mode == "Catalog & Policy Search":
            with st.spinner("Searching catalog..."):
                results = search_catalog(
                    user_msg,
                    doc_type_filter=selected_types if selected_types else None,
                )

            if results:
                response = st.write_stream(generate_search_answer(user_msg, results))
                sources = [
                    {
                        "title": r.get("DOC_TITLE", "Unknown"),
                        "type": r.get("DOC_TYPE", ""),
                        "file": r.get("SOURCE_FILE", ""),
                    }
                    for r in results
                ]
                with st.expander(f"Sources ({len(sources)} documents)"):
                    for src in sources:
                        st.markdown(f"- **{src['title']}** ({src['type']}) — {src['file']}")

                st.session_state.messages.append(
                    {"role": "assistant", "content": response, "sources": sources, "avatar": "🎓"}
                )
            else:
                no_result = "I could not find relevant information in the catalog for that question. Try rephrasing or broadening your search."
                st.write(no_result)
                st.session_state.messages.append(
                    {"role": "assistant", "content": no_result, "avatar": "🎓"}
                )

        else:  # Student Data Analyst
            with st.spinner("Analyzing data..."):
                analyst_text, sql_query, result_df = query_analyst(user_msg)

            if analyst_text:
                st.write(analyst_text)
            if sql_query:
                with st.expander("Generated SQL"):
                    st.code(sql_query, language="sql")
            if result_df is not None and not result_df.empty:
                st.dataframe(result_df, hide_index=True, use_container_width=True)
                if len(result_df.columns) >= 2 and len(result_df) > 1:
                    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
                    if numeric_cols:
                        non_numeric = [c for c in result_df.columns if c not in numeric_cols]
                        if non_numeric:
                            st.bar_chart(result_df, x=non_numeric[0], y=numeric_cols[0])

            msg_data = {
                "role": "assistant",
                "content": analyst_text or "Here are the results:",
                "sql": sql_query,
                "avatar": "🎓",
            }
            if result_df is not None:
                msg_data["dataframe"] = result_df
            st.session_state.messages.append(msg_data)
