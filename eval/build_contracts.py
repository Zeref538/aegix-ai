"""Compose 18 evaluation contracts from the clause bank and render PDFs.

Outputs:
  eval/contracts/*.pdf      — the sample contracts
  eval/ground_truth.json    — expected verdict + citation per category
Missing categories are encoded as null in the spec and expected verdict
"Missing" in the ground truth.
"""

import json
from pathlib import Path

import fitz

from clause_bank import BANK

EVAL_DIR = Path(__file__).resolve().parent
OUT_DIR = EVAL_DIR / "contracts"

REQUIRED = ["probation", "termination", "pay", "benefits", "hours", "dispute"]

HEADINGS = {
    "probation": "Probationary Period",
    "termination": "Termination of Employment",
    "pay": "Compensation",
    "benefits": "Statutory Benefits",
    "hours": "Work Schedule",
    "ip": "Intellectual Property",
    "dispute": "Dispute Resolution",
}

# Each spec: contract name -> {category: variant_id or None (omit)}
# Mix of fully compliant, mixed, adversarial, and sparse contracts.
SPECS: dict[str, dict[str, str | None]] = {
    "c01_fully_compliant": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": "ip_ok", "dispute": "disp_ok"},
    "c02_bad_probation": {"probation": "prob_long", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": None, "dispute": "disp_ok"},
    "c03_no_13th_month": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_no13th", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": None, "dispute": "disp_ok"},
    "c04_benefits_waiver": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_waive", "hours": "hrs_ok",
        "ip": "ip_ok", "dispute": "disp_ok"},
    "c05_at_will": {"probation": "prob_ok", "termination": "term_atwill",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": None, "dispute": "disp_ok"},
    "c06_overtime_waiver": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_bad",
        "ip": None, "dispute": "disp_ok"},
    "c07_ip_overreach": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": "ip_all", "dispute": "disp_ok"},
    "c08_foreign_arbitration": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": "ip_ok", "dispute": "disp_bad"},
    "c09_all_vague": {"probation": "prob_vague", "termination": "term_vague",
        "pay": "pay_vague", "benefits": "ben_vague", "hours": "hrs_vague",
        "ip": None, "dispute": "disp_vague"},
    "c10_everything_wrong": {"probation": "prob_long", "termination": "term_atwill",
        "pay": "pay_no13th", "benefits": "ben_waive", "hours": "hrs_bad",
        "ip": "ip_all", "dispute": "disp_bad"},
    "c11_missing_benefits_pay": {"probation": "prob_ok", "termination": "term_ok",
        "pay": None, "benefits": None, "hours": "hrs_ok",
        "ip": None, "dispute": "disp_ok"},
    "c12_missing_probation_dispute": {"probation": None, "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": "ip_ok", "dispute": None},
    "c13_bare_minimum": {"probation": None, "termination": None,
        "pay": "pay_vague", "benefits": None, "hours": None,
        "ip": None, "dispute": None},
    "c14_mixed_1": {"probation": "prob_vague", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_vague", "hours": "hrs_bad",
        "ip": None, "dispute": "disp_ok"},
    "c15_mixed_2": {"probation": "prob_ok", "termination": "term_vague",
        "pay": "pay_no13th", "benefits": "ben_ok", "hours": "hrs_vague",
        "ip": "ip_all", "dispute": None},
    "c16_mixed_3": {"probation": "prob_long", "termination": "term_ok",
        "pay": "pay_vague", "benefits": "ben_waive", "hours": "hrs_ok",
        "ip": "ip_ok", "dispute": "disp_vague"},
    "c17_missing_hours_term": {"probation": "prob_ok", "termination": None,
        "pay": "pay_ok", "benefits": "ben_ok", "hours": None,
        "ip": None, "dispute": "disp_ok"},
    "c18_compliant_no_ip": {"probation": "prob_ok", "termination": "term_ok",
        "pay": "pay_ok", "benefits": "ben_ok", "hours": "hrs_ok",
        "ip": None, "dispute": "disp_ok"},
}

PREAMBLES = [
    "EMPLOYMENT CONTRACT\n\nThis Employment Contract is entered into by and "
    "between {company} (the \"Company\") and the undersigned employee (the "
    "\"Employee\").\n",
    "CONTRACT OF EMPLOYMENT\n\nKNOW ALL MEN BY THESE PRESENTS: {company}, a "
    "corporation organized under Philippine law, hereby engages the Employee "
    "under the following terms and conditions:\n",
    "EMPLOYMENT AGREEMENT\n\n{company} and the Employee agree as follows:\n",
]

COMPANIES = ["Maharlika Tech Solutions Inc.", "Bayanihan Logistics Corp.",
             "Sampaguita Retail Group Inc."]

CLOSING = (
    "\nIN WITNESS WHEREOF, the parties have signed this Contract on the date "
    "first written above.\n\n_____________________\nEmployer\n\n"
    "_____________________\nEmployee"
)

BANK_BY_ID = {vid: (text, verdict, cite)
              for variants in BANK.values()
              for (vid, text, verdict, cite) in variants}

# Numbering styles to vary formatting across contracts
STYLES = [
    lambda i, h: f"{i}. {h}",
    lambda i, h: f"Section {i}. {h.upper()}",
    lambda i, h: f"ARTICLE {['I','II','III','IV','V','VI','VII','VIII'][i-1]} — {h}",
]


def compose(name: str, spec: dict[str, str | None], idx: int) -> tuple[str, dict]:
    style = STYLES[idx % len(STYLES)]
    preamble = PREAMBLES[idx % len(PREAMBLES)].format(
        company=COMPANIES[idx % len(COMPANIES)])
    parts = [preamble]
    truth: dict[str, dict] = {}
    n = 0
    for cat, variant in spec.items():
        if variant is None:
            if cat in REQUIRED:
                truth[cat] = {"verdict": "Missing", "citation_must_contain": ""}
            continue
        text, verdict, cite = BANK_BY_ID[variant]
        n += 1
        parts.append(f"\n{style(n, HEADINGS[cat])}\n{text}\n")
        truth[cat] = {"verdict": verdict, "citation_must_contain": cite,
                      "variant": variant}
    parts.append(CLOSING)
    return "".join(parts), truth


def render_pdf(text: str, path: Path) -> None:
    doc = fitz.open()
    page = doc.new_page()
    rect = fitz.Rect(54, 54, 558, 788)
    remaining = text
    while remaining:
        spilled = page.insert_textbox(rect, remaining, fontsize=10,
                                      fontname="times-roman")
        if spilled >= 0:
            break
        # insert_textbox returns negative deficit; find split point manually
        # by binary search on how much fits
        lo, hi = 0, len(remaining)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            test = doc.new_page()
            fits = test.insert_textbox(rect, remaining[:mid], fontsize=10,
                                       fontname="times-roman") >= 0
            doc.delete_page(doc.page_count - 1)
            if fits:
                lo = mid
            else:
                hi = mid - 1
        # Split at last newline before the cutoff to keep lines intact
        cut = remaining.rfind("\n", 0, lo) if lo < len(remaining) else lo
        cut = cut if cut > 0 else lo
        page.insert_textbox(rect, remaining[:cut], fontsize=10,
                            fontname="times-roman")
        remaining = remaining[cut:].lstrip("\n")
        if remaining:
            page = doc.new_page()
        else:
            break
    else:
        pass
    doc.save(path)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ground_truth: dict[str, dict] = {}
    for idx, (name, spec) in enumerate(SPECS.items()):
        text, truth = compose(name, spec, idx)
        render_pdf(text, OUT_DIR / f"{name}.pdf")
        ground_truth[name] = truth
    gt_path = EVAL_DIR / "ground_truth.json"
    gt_path.write_text(json.dumps(ground_truth, indent=2), encoding="utf-8")
    print(f"rendered {len(SPECS)} contracts to {OUT_DIR}")
    print(f"ground truth: {gt_path}")


if __name__ == "__main__":
    main()
