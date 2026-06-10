from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import ResearchState
from agents.nodes import (
    orchestrator_node,
    literature_agent_node,
    data_agent_node,
    synthesis_agent_node,
    human_review_node,
    format_response_node,
)


def route_after_human_review(state: ResearchState) -> str:
    return "format_response" if state.human_approved else "human_review"


def build_pipeline():
    graph = StateGraph(ResearchState)

    graph.add_node("orchestrator",     orchestrator_node)
    graph.add_node("literature_agent", literature_agent_node)
    graph.add_node("data_agent",       data_agent_node)
    graph.add_node("synthesis_agent",  synthesis_agent_node)
    graph.add_node("human_review",     human_review_node)
    graph.add_node("format_response",  format_response_node)

    graph.set_entry_point("orchestrator")

    graph.add_edge("orchestrator",     "literature_agent")
    graph.add_edge("orchestrator",     "data_agent")
    graph.add_edge("literature_agent", "synthesis_agent")
    graph.add_edge("data_agent",       "synthesis_agent")
    graph.add_edge("synthesis_agent",  "human_review")

    graph.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "format_response": "format_response",
            "human_review":    "human_review",
        },
    )

    graph.add_edge("format_response", END)
    return graph


def compile_pipeline():
    memory = MemorySaver()
    return build_pipeline().compile(
        checkpointer=memory,
        interrupt_before=["human_review"],
    )


pipeline = compile_pipeline()