from typing import Annotated, Any
from pydantic import BaseModel, Field
import operator


class Citation(BaseModel):
    source: str
    title: str
    excerpt: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class SubTask(BaseModel):
    task_id: str
    task_type: str
    description: str
    status: str = "pending"


class AgentResult(BaseModel):
    task_id: str
    agent: str
    content: str
    citations: list[Citation] = []
    metadata: dict[str, Any] = {}


class ResearchState(BaseModel):
    query: str = ""
    subtasks: list[SubTask] = []
    agent_results: Annotated[list[AgentResult], operator.add] = []
    literature_result: AgentResult | None = None
    data_result: AgentResult | None = None
    synthesis_result: AgentResult | None = None
    final_response: str = ""
    all_citations: list[Citation] = []
    human_approved: bool = False
    error: str = ""
    reasoning_trace: Annotated[list[str], operator.add] = []