from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TicketInput(BaseModel):
    id: str
    subject: str
    body: str


class TicketCategory(BaseModel):
    department: str = Field(description="Billing / Technical / Account / Other")
    urgency: str = Field(description="Critical / High / Normal / Low")


class TicketSummary(BaseModel):
    issue_summary: str
    root_cause: str
    suggested_action: str
    sentiment: str = Field(description="Angry / Neutral / Satisfied")


class CriticalDraftReply(BaseModel):
    reply_subject: str
    reply_body: str


class TicketResult(BaseModel):
    id: str
    subject: str
    body: str
    category: Optional[TicketCategory] = None
    summary: Optional[TicketSummary] = None
    critical_draft_reply: Optional[CriticalDraftReply] = None


class PipelineState(BaseModel):
    input_csv_path: str
    output_json_path: str = "output_tickets.json"
    tickets: List[TicketInput] = Field(default_factory=list)
    results: List[TicketResult] = Field(default_factory=list)
    grouped_output: Dict[str, Dict[str, List[TicketResult]]] = Field(default_factory=dict)
