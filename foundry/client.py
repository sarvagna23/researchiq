import os
from dataclasses import dataclass
from typing import Any

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


@dataclass
class FoundryResult:
    content: str
    citations: list[dict[str, Any]]
    grounded: bool


class FoundryIQClient:
    def __init__(self):
        self.endpoint   = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT", "")
        self.index_name = os.getenv("FOUNDRY_IQ_INDEX_NAME", "research-index")
        self._client    = None
        if AZURE_AVAILABLE and self.endpoint:
            self._client = AIProjectClient(
                endpoint=self.endpoint,
                credential=DefaultAzureCredential(),
            )

    def retrieve(self, query: str, top_k: int = 5) -> FoundryResult:
        if self._client:
            return self._retrieve_azure(query, top_k)
        return self._retrieve_mock(query, top_k)

    def _retrieve_azure(self, query: str, top_k: int) -> FoundryResult:
        search = self._client.indexes.search(
            index_name=self.index_name, query=query, top=top_k
        )
        citations = [
            {
                "source": r.metadata.get("source", ""),
                "title":  r.metadata.get("title", "Unknown"),
                "excerpt": r.content[:300],
                "relevance_score": r.score,
            }
            for r in search.results
        ]
        return FoundryResult(
            content="\n\n".join(r.content for r in search.results),
            citations=citations,
            grounded=True,
        )

    def _retrieve_mock(self, query: str, top_k: int) -> FoundryResult:
        return FoundryResult(
            content=f"[MOCK] Foundry IQ retrieved {top_k} results for: {query}",
            citations=[
                {
                    "source": "mock://paper-001",
                    "title": f"Study on: {query[:40]}",
                    "excerpt": "Key findings relevant to the query...",
                    "relevance_score": 0.92,
                },
                {
                    "source": "mock://paper-002",
                    "title": "Supporting evidence paper",
                    "excerpt": "Additional context and supporting data...",
                    "relevance_score": 0.85,
                },
            ],
            grounded=False,
        )