"""Verdict generation: clause + retrieved rules -> {verdict, citation, explanation}."""

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_chat_model
from app.schemas import Clause, ClauseVerdict

SYSTEM = """\
You are a Philippine labor-law compliance checker reviewing one clause of an \
employment contract against the governing legal provisions supplied to you.

Verdict definitions:
- Compliant: the clause satisfies the cited provision(s).
- Non-compliant: the clause contradicts or falls below a legal minimum \
(e.g. probation beyond 6 months, overtime below 25% premium, waiving 13th \
month pay).
- Vague: the clause addresses the topic but is too imprecise to verify \
compliance (e.g. "overtime paid per company policy" with no rate).

Rules:
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
