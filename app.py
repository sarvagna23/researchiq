import streamlit as st
import uuid
from graph.pipeline import pipeline
from graph.state import ResearchState

st.set_page_config(page_title="ResearchIQ", page_icon="🔬", layout="wide")
st.title("ResearchIQ")
st.caption("Multi-agent research assistant · Microsoft Foundry IQ · Agents League 2026")

for k, v in [("thread_id", None), ("run_state", "idle"), ("graph_state", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

cfg = lambda tid: {"configurable": {"thread_id": tid}}

with st.sidebar:
    st.header("Reasoning trace")
    if st.session_state.graph_state:
        for s in st.session_state.graph_state.reasoning_trace:
            st.markdown(f"- {s}")
    else:
        st.caption("Run a query to see agent steps.")
    st.divider()
    st.subheader("Citations")
    if st.session_state.graph_state:
        for i, c in enumerate(st.session_state.graph_state.all_citations):
            with st.expander(f"[{i+1}] {c.title[:50]}"):
                st.write(f"**Source:** {c.source}")
                st.write(f"**Score:** {c.relevance_score:.2f}")
                st.write(c.excerpt)

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input(
        "Research question",
        placeholder="e.g. What are the latest findings on transformer efficiency?"
    )
with col2:
    run_btn = st.button("Research", type="primary", use_container_width=True)

if run_btn and query:
    st.session_state.thread_id   = str(uuid.uuid4())
    st.session_state.run_state   = "running"
    st.session_state.graph_state = None
    with st.spinner("Agents working..."):
        for chunk in pipeline.stream(
            ResearchState(query=query).model_dump(),
            config=cfg(st.session_state.thread_id),
            stream_mode="values",
        ):
            st.session_state.graph_state = ResearchState(**chunk)
    st.session_state.run_state = "awaiting_approval"
    st.rerun()

if st.session_state.run_state == "awaiting_approval" and st.session_state.graph_state:
    s = st.session_state.graph_state
    st.divider()
    st.subheader("Agent synthesis — pending your approval")
    t1, t2, t3 = st.tabs(["Literature", "Data", "Synthesis"])
    with t1:
        st.markdown(s.literature_result.content if s.literature_result else "No result.")
    with t2:
        st.markdown(s.data_result.content if s.data_result else "No result.")
    with t3:
        st.markdown(s.synthesis_result.content if s.synthesis_result else "No result.")
    st.divider()
    st.subheader("Human review")
    st.info("Approve to generate the final cited response, or reject to discard.")
    ca, cr, _ = st.columns([1, 1, 4])
    with ca:
        if st.button("Approve", type="primary"):
            with st.spinner("Formatting..."):
                for chunk in pipeline.stream(
                    {"human_approved": True},
                    config=cfg(st.session_state.thread_id),
                    stream_mode="values",
                ):
                    st.session_state.graph_state = ResearchState(**chunk)
            st.session_state.run_state = "done"
            st.rerun()
    with cr:
        if st.button("Reject"):
            st.session_state.run_state   = "idle"
            st.session_state.graph_state = None
            st.rerun()

if st.session_state.run_state == "done" and st.session_state.graph_state:
    s = st.session_state.graph_state
    st.divider()
    st.subheader("Final cited response")
    st.markdown(s.final_response)
    st.download_button(
        "Download response",
        data=s.final_response,
        file_name="research_response.md",
        mime="text/markdown",
    )
    if st.button("New query"):
        st.session_state.run_state   = "idle"
        st.session_state.graph_state = None
        st.rerun()