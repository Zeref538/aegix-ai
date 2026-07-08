"""Verdict generation: clause + retrieved rules -> {verdict, citation, explanation}."""

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_chat_model
from app.schemas import Clause, ClauseVerdict

SYSTEM = """\
You are a Philippine labor-law compliance checker reviewing one clause of an \
employment contract against the governing legal provisions supplied to you.

Your verdict must be exactly one of: Compliant, Non-compliant, or Vague. \
Never output "Missing" — the clause exists; absence is handled elsewhere.

Verdict definitions:
- Non-compliant: something the clause ACTUALLY SAYS contradicts or falls \
below a legal minimum (e.g. probation beyond 6 months, overtime below the \
25% premium, waiving 13th-month pay or SSS coverage).
- Vague: the clause's own terms are too imprecise to verify against the \
law (e.g. "overtime paid per company policy" with no rate, "a probationary \
period to be determined by management").
- Compliant: everything the clause states meets or exceeds the legal \
minimums.

Judging rules:
- Judge only what the clause states. A contract clause does NOT need to \
restate every statutory entitlement — statutory rights apply regardless of \
contract silence. Silence about a related sub-topic (e.g. rest-day premium \
rates, holiday pay) is NOT a violation and does not make the clause vague.
- Judge ONLY against the provided legal provisions; do not rely on outside \
knowledge.
- citation MUST quote the citation string of the provision(s) you relied \
on, exactly as given (e.g. "Labor Code, Art. 296 [281]").
- Explain in plain English for a non-lawyer, 2-4 sentences, naming the \
specific requirement and how the clause meets or fails it."""

HUMAN = """\
Clause category: {clause_type}

Clause text:
{clause_text}

Governing legal provisions:
{rules_block}"""

PROMPT = ChatPromptTemplate.from_messages([("system", SYSTEM), ("human", HUMAN)])


def format_rules(rules: list[dict]) -> str:
    return "\n\n".join(
        f"[{r['citation']}] {r['title']}\n{r['text']}" for r in rules
    )


def build_verdict_chain(llm: BaseChatModel | None = None):
    llm = llm or get_chat_model()
    return PROMPT | llm.with_structured_output(ClauseVerdict)


def judge_clause(clause: Clause, rules: list[dict],
                 llm: BaseChatModel | None = None) -> ClauseVerdict:
    chain = build_verdict_chain(llm)
    return chain.invoke({
        "clause_type": clause.clause_type.value,
        "clause_text": clause.text,
        "rules_block": format_rules(rules),
    })
