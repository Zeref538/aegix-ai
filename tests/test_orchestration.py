"""Pipeline orchestration: order, concurrency, category handling, coercion.

The LLM and vector store are stubbed, so this runs without credentials.
"""

import pytest

from app import pipeline
from app.schemas import (
    REQUIRED_CATEGORIES,
    Clause,
    ClauseCategory,
    ClauseVerdict,
    SegmentedContract,
    Verdict,
)

TEXT = "EMPLOYMENT CONTRACT. " * 20


def stub(monkeypatch, clauses, verdict=Verdict.compliant):
    monkeypatch.setattr(
        pipeline, "segment_contract",
        lambda text, llm=None: SegmentedContract(clauses=clauses),
    )
    monkeypatch.setattr(
        pipeline, "retrieve_rules",
        lambda text, cat, **kw: [
            {"citation": "Labor Code, Art. 296 [281]", "title": "t", "text": "x"}
        ],
    )
    monkeypatch.setattr(
        pipeline, "judge_clause",
        lambda clause, rules, llm=None: ClauseVerdict(
            verdict=verdict, citation="Labor Code, Art. 296 [281]", explanation="e"
        ),
    )


def test_missing_categories_are_flagged(monkeypatch):
    stub(monkeypatch, [Clause(clause_type=ClauseCategory.probation, text="six months")])
    report = pipeline.analyze_text(TEXT)

    missing = {c.clause_type for c in report.clauses if c.verdict == Verdict.missing}
    assert missing == set(REQUIRED_CATEGORIES) - {ClauseCategory.probation}
    assert all(c.clause_text is None for c in report.clauses
               if c.verdict == Verdict.missing)


def test_other_category_is_skipped(monkeypatch):
    stub(monkeypatch, [
        Clause(clause_type=ClauseCategory.other, text="confidentiality"),
        Clause(clause_type=ClauseCategory.pay, text="salary"),
    ])
    report = pipeline.analyze_text(TEXT)
    assert ClauseCategory.other not in {c.clause_type for c in report.clauses}


def test_clause_order_is_preserved_under_parallelism(monkeypatch):
    order = [
        ClauseCategory.hours,
        ClauseCategory.pay,
        ClauseCategory.probation,
        ClauseCategory.dispute,
        ClauseCategory.benefits,
    ]
    stub(monkeypatch, [Clause(clause_type=c, text=f"clause {c.value}") for c in order])
    report = pipeline.analyze_text(TEXT)

    judged = [c.clause_type for c in report.clauses if c.verdict != Verdict.missing]
    assert judged == order, "parallel workers must not reorder the report"


def test_judge_saying_missing_is_coerced_to_vague(monkeypatch):
    # "Missing" is reserved for absent categories; a present clause can't be Missing
    stub(monkeypatch, [Clause(clause_type=ClauseCategory.pay, text="salary")],
         verdict=Verdict.missing)
    report = pipeline.analyze_text(TEXT)

    pay = [c for c in report.clauses if c.clause_type == ClauseCategory.pay]
    assert [c.verdict for c in pay] == [Verdict.vague]


def test_duplicate_categories_are_all_kept(monkeypatch):
    stub(monkeypatch, [
        Clause(clause_type=ClauseCategory.benefits, text="SSS"),
        Clause(clause_type=ClauseCategory.benefits, text="PhilHealth"),
    ])
    report = pipeline.analyze_text(TEXT)

    benefits = [c for c in report.clauses if c.clause_type == ClauseCategory.benefits]
    assert len(benefits) == 2, "both benefits clauses must survive into the report"


def test_short_pasted_text_rejected():
    from app.ingest import EmptyPdfError

    with pytest.raises(EmptyPdfError):
        pipeline.analyze_text("too short")


def test_rule_text_is_truncated_for_the_prompt():
    from app.verdict import MAX_RULE_CHARS, format_rules

    block = format_rules(
        [{"citation": "RA 11199, Sec. 9", "title": "Coverage", "text": "y" * 9000}]
    )
    assert len(block) < MAX_RULE_CHARS + 200
    assert block.endswith("[…]")
