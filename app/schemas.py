"""Pydantic models shared across the pipeline and API."""

from enum import Enum

from pydantic import BaseModel, Field


class ClauseCategory(str, Enum):
    probation = "probation"
    termination = "termination"
    pay = "pay"
    benefits = "benefits"
    hours = "hours"
    ip = "ip"
    dispute = "dispute"
    other = "other"


# Categories every PH employment contract must address; absence is flagged.
REQUIRED_CATEGORIES = [
    ClauseCategory.probation,
    ClauseCategory.termination,
    ClauseCategory.pay,
    ClauseCategory.benefits,
    ClauseCategory.hours,
    ClauseCategory.dispute,
]
# IP is only checked when present in the contract.


class Verdict(str, Enum):
    compliant = "Compliant"
    non_compliant = "Non-compliant"
    vague = "Vague"
    missing = "Missing"


class Clause(BaseModel):
    """One contract clause as segmented by the LLM."""

    clause_type: ClauseCategory = Field(
        description="Which compliance category this clause belongs to"
    )
    text: str = Field(description="Verbatim clause text from the contract")


class SegmentedContract(BaseModel):
    """Structured output of the segmentation chain."""

    clauses: list[Clause]


class ClauseVerdict(BaseModel):
    """Structured output of the verdict chain for one clause."""

    verdict: Verdict
    citation: str = Field(
        description="The specific legal provision relied on, e.g. "
        "'Labor Code, Art. 296 [281]'. Never empty."
    )
    explanation: str = Field(
        description="Plain-English explanation of the verdict for a "
        "non-lawyer, 2-4 sentences"
    )


class ClauseReport(BaseModel):
    """One row of the final report."""

    clause_type: ClauseCategory
    clause_text: str | None = None  # None when the clause is Missing
    verdict: Verdict
    citation: str
    explanation: str


class ComplianceReport(BaseModel):
    """Fixed-schema output of POST /analyze."""

    filename: str
    clauses: list[ClauseReport]
    disclaimer: str = (
        "This automated report is not legal advice and is not a substitute "
        "for consultation with a qualified Philippine labor lawyer."
    )
