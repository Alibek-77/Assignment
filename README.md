# Assignment 4 - Option B (Support Ticket Triage)

Mini Agent system built with **LangGraph + Gemini + Pydantic Structured Outputs**.

## What this system does
- Reads support tickets from CSV (`id, subject, body`)
- Classifies each ticket by:
  - `department`: Billing / Technical / Account / Other
  - `urgency`: Critical / High / Normal / Low
- Generates a structured issue analysis
- Creates a draft reply for Critical tickets (bonus feature)
- Exports tickets grouped by department and priority into JSON

## Assignment Criteria Coverage
- LangGraph pipeline with 3+ nodes: **5 nodes** (`ingest -> categorize -> summarize -> draft_critical -> export`)
- 2+ LLM calls with Pydantic Structured Outputs: **3 structured calls**
  - Call 1: `TicketCategory`
  - Call 2: `TicketSummary`
  - Bonus call: `CriticalDraftReply`
- Pydantic models: `TicketCategory`, `TicketSummary`, `CriticalDraftReply`, `PipelineState`, etc.
- prompts.py: all prompts are stored in `src/prompts.py`
- Bonus feature from Option B: draft reply generation for Critical tickets
- Bonus ready: LangSmith tracing supported via `@traceable`

## Project Structure
- `main.py` - CLI entrypoint
- `src/models.py` - all Pydantic models and state schema
- `src/prompts.py` - named prompt constants
- `src/pipeline.py` - LangGraph nodes and graph wiring
- `tickets.sample.csv` - sample input
- `sample_output.json` - sample output format
- `.env.example` - environment variable template

## Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configure API keys
Copy `.env.example` to `.env` and set:
- `GEMINI_API_KEY`
- Optional for bonus tracing:
  - `LANGSMITH_API_KEY`
  - `LANGSMITH_TRACING=true`
  - `LANGSMITH_PROJECT=assignment4-option-b`

## Run
```bash
python main.py --input tickets.sample.csv --output output_tickets.json
```

## Input format
CSV must contain columns:
- `id`
- `subject`
- `body`

## Output format
JSON grouped by department and urgency, for example:
```json
{
  "total_tickets": 5,
  "grouped_by_department_and_priority": {
    "Technical": {
      "High": [
        {
          "id": "2",
          "subject": "Password reset not working",
          "category": {"department": "Technical", "urgency": "High"},
          "summary": {"issue_summary": "..."}
        }
      ]
    }
  }
}
```

## Defense Talking Points
1. Why LangGraph: explicit workflow control, clear node orchestration, maintainable pipeline.
2. Why Pydantic structured output: reliable schema, typed data, safer downstream processing.
3. Why multiple LLM calls: split responsibilities improves consistency and makes debugging easier.
4. Bonus feature: critical ticket auto-draft helps support agents respond faster.
5. Scalability: node-based architecture allows adding SLA checks, auto-routing, and analytics.

## Common Questions + Short Answers
- **Q: Where are your 2+ LLM calls?**
  - In `categorize_tickets`, `summarize_tickets`, and `draft_critical_replies`.
- **Q: Where is the graph state?**
  - `PipelineState` in `src/models.py`.
- **Q: Where are prompts?**
  - `src/prompts.py` as named constants.
- **Q: How is output validated?**
  - Every LLM response is parsed to Pydantic models before further use.
- **Q: What is your bonus implementation?**
  - Critical-ticket draft replies and optional LangSmith tracing.
