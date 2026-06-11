# CertIQ 🎓

> Multi-agent enterprise certification learning assistant powered by Microsoft Foundry IQ

Built for the **Microsoft Agents League Hackathon 2026** — Reasoning Agents track.

---

## What it does

CertIQ helps organisations manage internal team certification programmes. A learner states their certification goal and role, and CertIQ routes it through a pipeline of specialised AI agents that work in parallel — grounding all knowledge retrieval through **Microsoft Foundry IQ** — to produce a capacity-aware study plan with a manager approval gate.

**Example:** *"I am a Cloud Engineer targeting AZ-204 in 4 weeks with 10 focus hours per week"*

CertIQ returns a structured study plan with learning path, readiness assessment, practice questions, milestones, and manager insights.

---

## Architecture

```
Learner goal
    ↓
Orchestrator agent        ← decomposes goal into 3 parallel sub-tasks
    ↓                ↓
Learning Path Curator   Assessment Agent   ← parallel, both grounded via Foundry IQ
         ↓             ↓
       Study Plan Generator               ← capacity-aware plan from both agents
            ↓
   Manager review gate                   ← human-in-the-loop approval
            ↓
   Final certified study plan
```

---

## Agents

| Agent | Role |
|---|---|
| Orchestrator | Decomposes certification goal into 3 parallel sub-tasks |
| Learning Path Curator | Retrieves grounded learning paths via Foundry IQ |
| Assessment Agent | Evaluates readiness using learner data and work signals |
| Study Plan Generator | Builds capacity-aware 5-section study plan |
| Manager Review | Human-in-the-loop approval gate before delivery |
| Format Node | Assembles final plan with full citation list |

---

## Microsoft IQ Integration

| IQ Layer | Usage |
|---|---|
| Foundry IQ | Grounds all knowledge retrieval with citations from approved sources |
| Work IQ | Work signals (meeting load, focus hours) inform study scheduling |
| Fabric IQ | Semantic model for certifications, roles, skills, and readiness scores |

---

## Synthetic Data

All learner data is synthetic and for demonstration only — no real PII or customer data.

- Learner performance records (L-1001, L-1002, L-1003)
- Work activity signals (EMP-001, EMP-002)
- Certification semantic model (AZ-204, AZ-400, DP-203)

---

## Tech stack

| Tool | Purpose |
|---|---|
| LangGraph | Agent orchestration + human-in-the-loop interrupt/resume |
| Microsoft Foundry IQ | Grounded knowledge retrieval with citations |
| OpenAI gpt-4o-mini | LLM backbone for all agents |
| Pydantic v2 | Structured state validation between agents |
| Streamlit | Demo UI |

---

## Setup

```bash
git clone https://github.com/sarvagna23/certiq
cd certiq

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# fill in your credentials

streamlit run app.py
```

---

## Judging criteria

| Criterion | How CertIQ addresses it |
|---|---|
| Accuracy & Relevance (25%) | Foundry IQ grounds all retrieval with citations |
| Reasoning & Multi-step (25%) | 5-agent pipeline with explicit reasoning trace |
| Creativity & Originality (15%) | Parallel agents + manager approval gate + work signal integration |
| User Experience (15%) | Pipeline progress bar, citation cards, download button |
| Reliability & Safety (20%) | Pydantic validation, synthetic data only, human approval gate |

---

## Author

**Sai Sarvagna Beeram**
MS Computer Science — Georgia State University (Dec 2026)
GitHub: [sarvagna23](https://github.com/sarvagna23)
LinkedIn: [saisarvagna023](https://linkedin.com/in/saisarvagna023)
