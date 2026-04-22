from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from typing import Dict, List

from langgraph.graph import END, START, StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from src.models import (
    CriticalDraftReply,
    PipelineState,
    TicketCategory,
    TicketInput,
    TicketResult,
    TicketSummary,
)
from src.prompts import CATEGORY_PROMPT, CRITICAL_REPLY_PROMPT, SUMMARY_PROMPT

try:
    from langsmith import traceable
except ImportError: 

    def traceable(func):
        return func


def _build_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")
    return ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct",  # убери :free
    openai_api_key=api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0,
    )


@traceable(name="load_tickets")
def ingest_tickets(state: PipelineState) -> PipelineState:
    tickets: List[TicketInput] = []
    with open(state.input_csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(
                TicketInput(
                    id=str(row.get("id", "")).strip(),
                    subject=str(row.get("subject", "")).strip(),
                    body=str(row.get("body", "")).strip(),
                )
            )

    state.tickets = tickets
    state.results = [
        TicketResult(id=t.id, subject=t.subject, body=t.body)
        for t in tickets
    ]
    return state


@traceable(name="categorize_tickets")
def categorize_tickets(state: PipelineState) -> PipelineState:
    llm = _build_llm().with_structured_output(TicketCategory)

    for ticket_result in state.results:
        category = llm.invoke(
            CATEGORY_PROMPT.format(subject=ticket_result.subject, body=ticket_result.body)
        )
        ticket_result.category = category

    return state


@traceable(name="summarize_tickets")
def summarize_tickets(state: PipelineState) -> PipelineState:
    llm = _build_llm().with_structured_output(TicketSummary)

    for ticket_result in state.results:
        if ticket_result.category is None:
            raise ValueError(f"Ticket {ticket_result.id} has no category before summary step")

        summary = llm.invoke(
            SUMMARY_PROMPT.format(
                subject=ticket_result.subject,
                body=ticket_result.body,
                department=ticket_result.category.department,
                urgency=ticket_result.category.urgency,
            )
        )
        ticket_result.summary = summary

    return state


@traceable(name="draft_critical_replies")
def draft_critical_replies(state: PipelineState) -> PipelineState:
    llm = _build_llm().with_structured_output(CriticalDraftReply)

    for ticket_result in state.results:
        if ticket_result.category is None or ticket_result.summary is None:
            continue

        if ticket_result.category.urgency == "Critical":
            draft = llm.invoke(
                CRITICAL_REPLY_PROMPT.format(
                    subject=ticket_result.subject,
                    body=ticket_result.body,
                    issue_summary=ticket_result.summary.issue_summary,
                    suggested_action=ticket_result.summary.suggested_action,
                )
            )
            ticket_result.critical_draft_reply = draft

    return state


@traceable(name="group_and_export")
def group_and_export(state: PipelineState) -> PipelineState:
    grouped: Dict[str, Dict[str, List[TicketResult]]] = defaultdict(lambda: defaultdict(list))

    for ticket_result in state.results:
        department = "Other"
        urgency = "Normal"

        if ticket_result.category is not None:
            department = ticket_result.category.department
            urgency = ticket_result.category.urgency

        grouped[department][urgency].append(ticket_result)

    state.grouped_output = {
        dep: {urg: tickets for urg, tickets in urgency_map.items()}
        for dep, urgency_map in grouped.items()
    }

    output_payload = {
        "total_tickets": len(state.results),
        "grouped_by_department_and_priority": {
            dep: {
                urg: [item.model_dump() for item in items]
                for urg, items in urgency_map.items()
            }
            for dep, urgency_map in state.grouped_output.items()
        },
    }

    with open(state.output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, indent=2)

    return state


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("ingest", ingest_tickets)
    graph.add_node("categorize", categorize_tickets)
    graph.add_node("summarize", summarize_tickets)
    graph.add_node("draft_critical", draft_critical_replies)
    graph.add_node("export", group_and_export)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "categorize")
    graph.add_edge("categorize", "summarize")
    graph.add_edge("summarize", "draft_critical")
    graph.add_edge("draft_critical", "export")
    graph.add_edge("export", END)

    return graph.compile()


def run_pipeline(input_csv_path: str, output_json_path: str = "output_tickets.json") -> PipelineState:
    app = build_graph()
    initial_state = PipelineState(input_csv_path=input_csv_path, output_json_path=output_json_path)
    final_state = app.invoke(initial_state)

    if isinstance(final_state, dict):
        return PipelineState(**final_state)
    return final_state
