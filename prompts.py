CATEGORY_PROMPT = """
You are a support operations classifier.
Classify this support ticket into:
1) department: one of Billing, Technical, Account, Other
2) urgency: one of Critical, High, Normal, Low

Ticket subject: {subject}
Ticket body: {body}

Rules:
- Critical: service down, data loss, payment blocked for many users, security incident.
- High: serious issue but workaround exists.
- Normal: standard customer issue.
- Low: minor question or cosmetic issue.
""".strip()

SUMMARY_PROMPT = """
You are a support analyst.
Analyze the ticket and return:
- issue_summary
- root_cause
- suggested_action
- sentiment (Angry, Neutral, Satisfied)

Ticket subject: {subject}
Ticket body: {body}
Department: {department}
Urgency: {urgency}
""".strip()

CRITICAL_REPLY_PROMPT = """
You are a senior customer support specialist.
Write a short professional response for a CRITICAL ticket.
Keep it empathetic, clear, and action-focused.

Ticket subject: {subject}
Ticket body: {body}
Summary: {issue_summary}
Suggested action internally: {suggested_action}
""".strip()
