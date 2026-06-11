import streamlit as st
import uuid
from graph.pipeline import pipeline
from graph.state import ResearchState

st.set_page_config(page_title="ResearchIQ", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.pipeline-node { text-align: center; padding: 10px 4px; border-radius: 8px; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
</style>
""", unsafe_allow_html=True)

for k, v in [("thread_id", None), ("run_state", "idle"), ("graph_state", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

cfg = lambda tid: {"configurable": {"thread_id": tid}}

def pipeline_bar(state):
    nodes = [
        ("orchestrator", "ti-settings",    "Orchestrator"),
        ("literature",   "ti-book",        "Literature"),
        ("data",         "ti-chart-bar",   "Data"),
        ("synthesis",    "ti-layers",      "Synthesis"),
        ("review",       "ti-user",        "Your review"),
        ("final",        "ti-file-text",   "Final"),
    ]
    trace = getattr(state, "reasoning_trace", []) if state else []
    done_map = {
        "orchestrator": any("Orchestrator" in t for t in trace),
        "literature":   any("Literature" in t for t in trace),
        "data":         any("Data" in t for t in trace),
        "synthesis":    any("Synthesis" in t for t in trace),
        "review":       st.session_state.run_state in ["done"],
        "final":        st.session_state.run_state == "done",
    }
    active_map = {
        "orchestrator": st.session_state.run_state == "running",
        "review":       st.session_state.run_state == "awaiting_approval",
        "final":        st.session_state.run_state == "done",
    }

    cols = st.columns(len(nodes))
    for col, (key, icon, label) in zip(cols, nodes):
        with col:
            if done_map.get(key):
                st.markdown(f"""
                <div style="text-align:center; padding:10px 4px; background:#f0faf4;
                border-radius:8px; border:0.5px solid #d1e8d8;">
                  <div style="font-size:20px; color:#2e7d5e;">✓</div>
                  <div style="font-size:11px; color:#2e7d5e; font-weight:500;">{label}</div>
                </div>""", unsafe_allow_html=True)
            elif active_map.get(key):
                st.markdown(f"""
                <div style="text-align:center; padding:10px 4px; background:#eaf4fd;
                border-radius:8px; border:0.5px solid #b5d4f4;">
                  <div style="font-size:20px;">●</div>
                  <div style="font-size:11px; color:#185fa5; font-weight:500;">{label}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align:center; padding:10px 4px; background:#f8f8f6;
                border-radius:8px; border:0.5px solid #e0e0d8;">
                  <div style="font-size:20px; color:#aaa;">○</div>
                  <div style="font-size:11px; color:#aaa;">{label}</div>
                </div>""", unsafe_allow_html=True)


def citation_cards(citations):
    if not citations:
        return
    cols = st.columns(2)
    for i, c in enumerate(citations):
        with cols[i % 2]:
            score_pct = int(c.relevance_score * 100)
            st.markdown(f"""
            <div style="border:0.5px solid #e0e0d8; border-radius:10px; padding:12px;
            margin-bottom:10px; background:var(--background-color);">
              <div style="font-size:10px; color:#185fa5; margin-bottom:4px;">
                [{i+1}] {c.source}
              </div>
              <div style="font-size:13px; font-weight:500; margin-bottom:6px;">{c.title[:60]}</div>
              <div style="font-size:12px; color:#666; margin-bottom:8px; line-height:1.5;">
                {c.excerpt[:120]}...
              </div>
              <div style="display:flex; align-items:center; gap:8px;">
                <div style="flex:1; height:3px; background:#e8e8e0; border-radius:2px;">
                  <div style="width:{score_pct}%; height:3px; background:#185fa5; border-radius:2px;"></div>
                </div>
                <span style="font-size:10px; color:#888;">{c.relevance_score:.2f}</span>
              </div>
            </div>""", unsafe_allow_html=True)


def trace_display(state):
    if not state:
        return
    trace = getattr(state, "reasoning_trace", [])
    if not trace:
        return
    items = "".join([
        f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;'
        f'font-size:12px;color:#666;">'
        f'<div style="width:6px;height:6px;border-radius:50%;background:#2e7d5e;flex-shrink:0;"></div>'
        f'{t}</div>'
        for t in trace
    ])
    st.markdown(f"""
    <div style="border:0.5px solid #e0e0d8; border-radius:8px; padding:12px 14px;">
      {items}
    </div>""", unsafe_allow_html=True)


# --- Header ---
st.markdown("## ResearchIQ")
st.caption("Multi-agent research assistant · Microsoft Foundry IQ · Agents League 2026")
st.divider()

# --- Search bar ---
col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "Research question",
        placeholder="e.g. What are the latest findings on transformer efficiency?",
        label_visibility="collapsed",
    )
with col2:
    run_btn = st.button("Research", type="primary", use_container_width=True)

# --- Pipeline bar ---
st.markdown("##### Agent pipeline")
pipeline_bar(st.session_state.graph_state)
st.divider()

# --- Run ---
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

# --- Results + review ---
if st.session_state.run_state == "awaiting_approval" and st.session_state.graph_state:
    s = st.session_state.graph_state

    st.markdown("##### Agent results")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Literature agent**")
        if s.literature_result:
            st.markdown(
                f'<div style="font-size:13px;color:#666;line-height:1.6;">'
                f'{s.literature_result.content[:300]}...</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption("No result.")

    with c2:
        st.markdown("**Data agent**")
        if s.data_result:
            st.markdown(
                f'<div style="font-size:13px;color:#666;line-height:1.6;">'
                f'{s.data_result.content[:300]}...</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption("No result.")

    with c3:
        st.markdown("**Synthesis agent**")
        if s.synthesis_result:
            st.markdown(
                f'<div style="font-size:13px;color:#666;line-height:1.6;">'
                f'{s.synthesis_result.content[:300]}...</div>',
                unsafe_allow_html=True
            )
        else:
            st.caption("No result.")

    st.divider()

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("##### Human review")
        st.info("Review the agent results above. Approve to generate the final cited response.")
        ca, cr = st.columns([1, 1])
        with ca:
            if st.button("Approve", type="primary", use_container_width=True):
                with st.spinner("Formatting final response..."):
                    for chunk in pipeline.stream(
                        {"human_approved": True},
                        config=cfg(st.session_state.thread_id),
                        stream_mode="values",
                    ):
                        st.session_state.graph_state = ResearchState(**chunk)
                st.session_state.run_state = "done"
                st.rerun()
        with cr:
            if st.button("Reject", use_container_width=True):
                st.session_state.run_state   = "idle"
                st.session_state.graph_state = None
                st.rerun()

    with col_right:
        st.markdown("##### Reasoning trace")
        trace_display(s)

    st.divider()
    st.markdown("##### Citations")
    citation_cards(s.all_citations)

# --- Final response ---
if st.session_state.run_state == "done" and st.session_state.graph_state:
    s = st.session_state.graph_state

    st.markdown("##### Final cited response")
    st.markdown(s.final_response)
    st.divider()

    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("##### Citations")
        citation_cards(s.all_citations)
    with col_right:
        st.markdown("##### Reasoning trace")
        trace_display(s)

    st.download_button(
        "Download response as markdown",
        data=s.final_response,
        file_name="research_response.md",
        mime="text/markdown",
    )
    if st.button("New query"):
        st.session_state.run_state   = "idle"
        st.session_state.graph_state = None
        st.rerun()