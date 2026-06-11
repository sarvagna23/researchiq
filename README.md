# ResearchIQ 🔬

> Multi-agent academic research assistant powered by Microsoft Foundry IQ

Built for the **Microsoft Agents League Hackathon 2026** — Reasoning Agents track.

---

## What it does

ResearchIQ takes any research question and routes it through a pipeline of specialized AI agents that work in parallel, retrieve grounded knowledge via **Microsoft Foundry IQ**, and produce a structured, cited answer — with a human approval gate before the final response is delivered.

**Example query:** *"What are the latest findings on transformer efficiency vs accuracy trade-offs?"*

ResearchIQ returns a structured 5-section response with citations, reasoning trace, and a downloadable markdown report.

---

## Architecture

```
User query
    ↓
Orchestrator agent       ← decomposes query into 3 sub-tasks
    ↓              ↓
Literature agent    Data agent     ← parallel retrieval via Foundry IQ
         ↓         ↓
       Synthesis agent             ← builds structured answer
            ↓
   Human-in-the-loop review       ← approve or reject before delivery
            ↓
   Final cited response
```

---

## Microsoft IQ Integration

All knowledge retrieval is grounded through **Foundry IQ**:

- Connects to indexed enterprise sources
- Enforces permissions per user
- Returns cited, grounded answers
- Reduces hallucination via source attribution

---

## Agent breakdown

| Agent | Role |
|---|---|
| Orchestrator | Decomposes research query into 3 parallel sub-tasks |
| Literature agent | Retrieves and summarizes relevant papers via Foundry IQ |
| Data agent | Extracts key statistics and empirical evidence via Foundry IQ |
| Synthesis agent | Builds structured 5-section answer from both agents |
| Human review | Interrupt gate — user approves before final delivery |
| Format node | Assembles final response with full citation list |

---

## Tech stack

| Tool | Purpose |
|---|---|
| LangGraph | Agent orchestration + human-in-the-loop interrupt/resume |
| Microsoft Foundry IQ | Grounded knowledge retrieval |
| OpenAI gpt-4o-mini | LLM backbone for all agents |
| Pydantic v2 | Structured state and output validation between agents |
| Streamlit | Demo UI |
| Python 3.13 | Runtime |

---

## Setup

```bash
git clone https://github.com/sarvagna23/researchiq
cd researchiq

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# fill in your credentials in .env

streamlit run app.py
```

---

## Environment variables

```
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
AZURE_AI_FOUNDRY_ENDPOINT=https://your-project.api.azureml.ms
AZURE_AI_PROJECT_ID=your-project-id
FOUNDRY_IQ_INDEX_NAME=research-index
```

> The app runs in mock mode automatically if Foundry IQ credentials are not set — useful for local development.

---

## Demo

1. Enter a research question
2. Watch the 3 agents work in parallel (reasoning trace in sidebar)
3. Review literature, data, and synthesis tabs
4. Approve or reject the synthesis
5. Download the final cited response as markdown

---

## Judging criteria alignment

| Criterion | How ResearchIQ addresses it |
|---|---|
| Accuracy & Relevance (20%) | Foundry IQ grounds all retrieval with citations |
| Reasoning & Multi-step (20%) | 4-agent pipeline with explicit reasoning trace |
| Creativity & Originality (15%) | Human-in-the-loop approval gate + parallel agent fan-out |
| User Experience (15%) | Clean Streamlit UI, tabbed results, download button |
| Reliability & Safety (20%) | Pydantic validation, fallback mock mode, human approval gate |
| Community vote (10%) | Join us on Discord |

---

## Author

**Sai Sarvagna Beeram**
MS Computer Science — Georgia State University (Dec 2026)
GitHub: [sarvagna23](https://github.com/sarvagna23)
LinkedIn: [saisarvagna023](https://linkedin.com/in/saisarvagna023)
