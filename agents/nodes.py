import os, json, re
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from graph.state import ResearchState, SubTask, AgentResult, Citation
from foundry.client import FoundryIQClient

_foundry = FoundryIQClient()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
_llm = None

SYNTHETIC_LEARNERS = [
    {"learner_id": "L-1001", "role": "Cloud Engineer", "certification": "AZ-204", "practice_score_avg": 67, "hours_studied": 18, "exam_outcome": "Fail"},
    {"learner_id": "L-1002", "role": "DevOps Engineer", "certification": "AZ-400", "practice_score_avg": 82, "hours_studied": 24, "exam_outcome": "Pass"},
    {"learner_id": "L-1003", "role": "Data Engineer", "certification": "DP-203", "practice_score_avg": 74, "hours_studied": 20, "exam_outcome": "Pass"},
]

SYNTHETIC_WORK_SIGNALS = [
    {"employee_id": "EMP-001", "meeting_hours_per_week": 22, "focus_hours_per_week": 10, "preferred_learning_slot": "Morning"},
    {"employee_id": "EMP-002", "meeting_hours_per_week": 15, "focus_hours_per_week": 18, "preferred_learning_slot": "Afternoon"},
]

SYNTHETIC_CERTS = {
    "AZ-204": {"skills": ["API Development", "Azure Functions", "Storage"], "recommended_hours": 20},
    "AZ-400": {"skills": ["CI/CD", "Monitoring", "GitHub Actions"], "recommended_hours": 25},
    "DP-203": {"skills": ["Data Factory", "Synapse", "Data Lake"], "recommended_hours": 22},
}

def _get_llm():
    global _llm
    if _llm is None:
        _llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _llm

def _chat(system, user):
    resp = _get_llm().chat.completions.create(
        model=MODEL, temperature=0.2,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}]
    )
    return resp.choices[0].message.content.strip()

def orchestrator_node(state: ResearchState) -> dict:
    system = (
        "You are a certification learning orchestrator. Given a learner certification goal, "
        "decompose into exactly 3 sub-tasks. Respond ONLY with valid JSON list of 3 objects: "
        "task_id (string), task_type (literature, data, or synthesis), description."
    )
    raw = _chat(system, state.query)
    try:
        parsed = json.loads(raw)
    except:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        parsed = json.loads(match.group()) if match else []
    subtasks = [SubTask(task_id=str(t["task_id"]), task_type=t["task_type"], description=t["description"]) for t in parsed] if parsed else [
        SubTask(task_id="t1", task_type="literature", description=f"Find learning path for: {state.query}"),
        SubTask(task_id="t2", task_type="data",       description=f"Assess readiness for: {state.query}"),
        SubTask(task_id="t3", task_type="synthesis",  description=f"Generate study plan for: {state.query}"),
    ]
    return {"subtasks": subtasks, "reasoning_trace": [f"Orchestrator decomposed certification goal into {len(subtasks)} tasks"]}

def literature_agent_node(state: ResearchState) -> dict:
    task = next((t for t in state.subtasks if t.task_type == "literature"), None)
    query = task.description if task else state.query
    retrieval = _foundry.retrieve(query, top_k=5)
    cert_context = json.dumps(SYNTHETIC_CERTS, indent=2)
    system = (
        "You are a Learning Path Curator Agent for enterprise certification programmes. "
        "Recommend a structured learning path with specific skills, resources, and milestones. "
        "Be specific and cite sources. Format as numbered steps."
    )
    summary = _chat(system, f"Goal: {query}\n\nCertification data:\n{cert_context}\n\nSources:\n{retrieval.content}")
    citations = [Citation(source=c["source"], title=c["title"], excerpt=c["excerpt"], relevance_score=c["relevance_score"]) for c in retrieval.citations]
    result = AgentResult(task_id=task.task_id if task else "t1", agent="learning_path_curator", content=summary, citations=citations)
    return {"literature_result": result, "agent_results": [result], "reasoning_trace": [f"Learning Path Curator done — {len(citations)} citations"]}

def data_agent_node(state: ResearchState) -> dict:
    task = next((t for t in state.subtasks if t.task_type == "data"), None)
    query = task.description if task else state.query
    retrieval = _foundry.retrieve(query, top_k=4)
    learner_context = json.dumps(SYNTHETIC_LEARNERS, indent=2)
    work_context = json.dumps(SYNTHETIC_WORK_SIGNALS, indent=2)
    system = (
        "You are an Assessment Agent for enterprise certification programmes. "
        "Analyse learner data and work signals to evaluate readiness. "
        "Generate 3 grounded practice questions. Give a readiness score out of 100. "
        "Use bullet points. Be precise and data-driven."
    )
    summary = _chat(system, f"Goal: {query}\n\nLearner data:\n{learner_context}\n\nWork signals:\n{work_context}\n\nSources:\n{retrieval.content}")
    citations = [Citation(source=c["source"], title=c["title"], excerpt=c["excerpt"], relevance_score=c["relevance_score"]) for c in retrieval.citations]
    result = AgentResult(task_id=task.task_id if task else "t2", agent="assessment_agent", content=summary, citations=citations)
    return {"data_result": result, "agent_results": [result], "reasoning_trace": [f"Assessment Agent done — {len(citations)} citations"]}

def synthesis_agent_node(state: ResearchState) -> dict:
    lit = state.literature_result.content if state.literature_result else ""
    data = state.data_result.content if state.data_result else ""
    work_context = json.dumps(SYNTHETIC_WORK_SIGNALS, indent=2)
    system = (
        "You are a Study Plan Generator Agent for enterprise certification programmes. "
        "Produce a capacity-aware study plan structured as: "
        "(1) Executive Summary (2) Recommended Study Schedule "
        "(3) Key Skills to Focus On (4) Practice Milestones "
        "(5) Manager Insights. Be specific with hours and measurable targets."
    )
    synthesis = _chat(system, f"Goal: {state.query}\n\nLearning path:\n{lit}\n\nAssessment:\n{data}\n\nWork signals:\n{work_context}")
    all_cit = []
    if state.literature_result: all_cit.extend(state.literature_result.citations)
    if state.data_result: all_cit.extend(state.data_result.citations)
    unique = list({c.source: c for c in all_cit}.values())
    result = AgentResult(task_id="t3", agent="study_plan_generator", content=synthesis, citations=unique)
    return {"synthesis_result": result, "agent_results": [result], "all_citations": unique, "reasoning_trace": ["Study Plan Generator complete"]}

def human_review_node(state: ResearchState) -> dict:
    return {"reasoning_trace": ["Awaiting manager approval"]}

def format_response_node(state: ResearchState) -> dict:
    if not state.synthesis_result:
        return {"final_response": "No result.", "reasoning_trace": ["Format: no result"]}
    refs = "\n".join(f"[{i+1}] {c.title} — {c.source}" for i, c in enumerate(state.all_citations))
    return {
        "final_response": f"{state.synthesis_result.content}\n\n---\n**References**\n{refs}",
        "reasoning_trace": ["Final study plan formatted"],
    }
