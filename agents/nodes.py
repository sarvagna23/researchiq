import os, json, re
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from graph.state import ResearchState, SubTask, AgentResult, Citation
from foundry.client import FoundryIQClient

_foundry = FoundryIQClient()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    return _llm

def _chat(system, user):
    resp = _get_llm().chat.completions.create(
        model=MODEL, temperature=0.2,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}]
    )
    return resp.choices[0].message.content.strip()

def orchestrator_node(state: ResearchState) -> dict:
    system = (
        "You are a research orchestrator. Decompose the query into exactly 3 sub-tasks. "
        "Respond ONLY with valid JSON list of 3 objects: task_id, task_type (literature/data/synthesis), description."
    )
    raw = _chat(system, state.query)
    try:
        parsed = json.loads(raw)
    except:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        parsed = json.loads(match.group()) if match else []
    subtasks = [SubTask(task_id=str(t["task_id"]), task_type=t["task_type"], description=t["description"]) for t in parsed] if parsed else [
        SubTask(task_id="t1", task_type="literature", description=f"Find papers on: {state.query}"),
        SubTask(task_id="t2", task_type="data",       description=f"Extract data on: {state.query}"),
        SubTask(task_id="t3", task_type="synthesis",  description=f"Synthesize: {state.query}"),
    ]
    return {"subtasks": subtasks, "reasoning_trace": [f"Orchestrator decomposed query into {len(subtasks)} tasks"]}

def literature_agent_node(state: ResearchState) -> dict:
    task = next((t for t in state.subtasks if t.task_type == "literature"), None)
    query = task.description if task else state.query
    retrieval = _foundry.retrieve(query, top_k=5)
    summary = _chat(
        "You are a literature specialist. Summarize key themes and findings from these sources in 3-4 paragraphs.",
        f"Query: {query}\n\nSources:\n{retrieval.content}"
    )
    citations = [
        Citation(source=c["source"], title=c["title"], excerpt=c["excerpt"], relevance_score=c["relevance_score"])
        for c in retrieval.citations
    ]
    result = AgentResult(task_id=task.task_id if task else "t1", agent="literature", content=summary, citations=citations)
    return {"literature_result": result, "agent_results": [result], "reasoning_trace": [f"Literature agent done — {len(citations)} citations"]}

def data_agent_node(state: ResearchState) -> dict:
    task = next((t for t in state.subtasks if t.task_type == "data"), None)
    query = task.description if task else state.query
    retrieval = _foundry.retrieve(query, top_k=4)
    summary = _chat(
        "You are a data specialist. Extract key statistics and empirical findings as bullet points.",
        f"Query: {query}\n\nSources:\n{retrieval.content}"
    )
    citations = [
        Citation(source=c["source"], title=c["title"], excerpt=c["excerpt"], relevance_score=c["relevance_score"])
        for c in retrieval.citations
    ]
    result = AgentResult(task_id=task.task_id if task else "t2", agent="data", content=summary, citations=citations)
    return {"data_result": result, "agent_results": [result], "reasoning_trace": [f"Data agent done — {len(citations)} citations"]}

def synthesis_agent_node(state: ResearchState) -> dict:
    lit  = state.literature_result.content if state.literature_result else ""
    data = state.data_result.content       if state.data_result       else ""
    synthesis = _chat(
        "You are a synthesis specialist. Write a structured answer: "
        "(1) Executive Summary (2) Key Findings (3) Evidence & Data (4) Limitations (5) Conclusion.",
        f"Query: {state.query}\n\nLiterature:\n{lit}\n\nData:\n{data}"
    )
    all_cit = []
    if state.literature_result: all_cit.extend(state.literature_result.citations)
    if state.data_result:       all_cit.extend(state.data_result.citations)
    unique = list({c.source: c for c in all_cit}.values())
    result = AgentResult(task_id="t3", agent="synthesis", content=synthesis, citations=unique)
    return {"synthesis_result": result, "agent_results": [result], "all_citations": unique, "reasoning_trace": ["Synthesis complete"]}

def human_review_node(state: ResearchState) -> dict:
    return {"reasoning_trace": ["Awaiting human approval"]}

def format_response_node(state: ResearchState) -> dict:
    if not state.synthesis_result:
        return {"final_response": "No result.", "reasoning_trace": ["Format: no result"]}
    refs = "\n".join(f"[{i+1}] {c.title} — {c.source}" for i, c in enumerate(state.all_citations))
    return {
        "final_response": f"{state.synthesis_result.content}\n\n---\n**References**\n{refs}",
        "reasoning_trace": ["Final response formatted"],
    }