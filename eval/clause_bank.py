"""Clause variants used to compose the evaluation contracts.

Each variant: (variant_id, clause_text, expected_verdict, citation_must_contain)
citation_must_contain is a substring the model's citation must include to be
scored correct (matched case-insensitively).
"""

BANK: dict[str, list[tuple[str, str, str, str]]] = {
    "probation": [
        ("prob_ok",
         "The Employee shall serve a probationary period of six (6) months "
         "from the start date. The Employee shall be evaluated against the "
         "performance standards in Annex A, which have been explained to the "
         "Employee at the time of engagement. Upon satisfactory completion, "
         "the Employee shall become a regular employee.",
         "Compliant", "296"),
        ("prob_long",
         "The Employee shall undergo a probationary period of twelve (12) "
         "months, which the Company may extend at its sole discretion for "
         "another six (6) months if performance is deemed unsatisfactory.",
         "Non-compliant", "296"),
        ("prob_vague",
         "The Employee will initially be engaged on a probationary basis for "
         "a period to be determined by management, subject to standards that "
         "the Company may issue from time to time.",
         "Vague", "296"),
    ],
    "termination": [
        ("term_ok",
         "Either party may terminate this Contract in accordance with the "
         "Labor Code. The Company may dismiss the Employee only for just or "
         "authorized causes under Articles 297 to 299 of the Labor Code, "
         "observing due process: written notice specifying the grounds, an "
         "opportunity to be heard, and a written notice of decision. The "
         "Employee may resign upon thirty (30) days' prior written notice.",
         "Compliant", "297"),
        ("term_atwill",
         "The Company may terminate the Employee's services at any time, for "
         "any reason or no reason, without prior notice or separation pay, "
         "and the Employee waives any claim arising from such termination.",
         "Non-compliant", "294"),
        ("term_vague",
         "Employment may be ended by the Company in line with company policy "
         "and applicable rules as may be amended from time to time.",
         "Vague", "29"),
    ],
    "pay": [
        ("pay_ok",
         "The Employee shall receive a monthly basic salary of PHP 30,000, "
         "payable in two equal installments on the 15th and last day of each "
         "month. The Employee shall receive 13th month pay equivalent to "
         "one-twelfth (1/12) of the basic salary earned within the calendar "
         "year, payable not later than December 24.",
         "Compliant", "851"),
        ("pay_no13th",
         "The Employee's total compensation package of PHP 35,000 per month "
         "is inclusive of all statutory benefits, and the Employee agrees "
         "that no separate 13th month pay shall be due, having been factored "
         "into the monthly rate.",
         "Non-compliant", "851"),
        ("pay_vague",
         "The Employee shall be compensated in accordance with the Company's "
         "compensation structure, payable on such dates as the Company may "
         "designate.",
         "Vague", ""),
    ],
    "benefits": [
        ("ben_ok",
         "The Company shall enroll the Employee with the Social Security "
         "System (SSS), PhilHealth, and the Home Development Mutual Fund "
         "(Pag-IBIG), and shall remit both employer and employee "
         "contributions as required by RA 11199, RA 11223, and RA 9679. "
         "Employee shares shall be deducted from salary as authorized by law.",
         "Compliant", "11199"),
        ("ben_waive",
         "The Employee, being engaged on a flexible arrangement, agrees to "
         "personally handle any SSS, PhilHealth, or Pag-IBIG enrollment and "
         "contributions, and releases the Company from any obligation to "
         "register or remit contributions on the Employee's behalf.",
         "Non-compliant", ""),
        ("ben_vague",
         "The Employee shall be entitled to government-mandated benefits as "
         "may be applicable.",
         "Vague", ""),
    ],
    "hours": [
        ("hrs_ok",
         "The Employee shall work eight (8) hours per day, Monday to Friday, "
         "from 9:00 a.m. to 6:00 p.m. with a one-hour unpaid meal break. "
         "Work rendered beyond eight hours shall be paid an additional "
         "twenty-five percent (25%) of the hourly rate, and thirty percent "
         "(30%) if performed on a rest day or holiday. The Employee is "
         "entitled to one rest day per week and to five (5) days of service "
         "incentive leave with pay per year.",
         "Compliant", "87"),
        ("hrs_bad",
         "The Employee's normal work schedule shall be ten (10) hours per "
         "day, six (6) days per week. The monthly salary compensates all "
         "hours worked, and no overtime pay shall be due regardless of hours "
         "rendered.",
         "Non-compliant", "8"),
        ("hrs_vague",
         "Working hours shall follow the Company's operational requirements "
         "and may be adjusted as needed. Overtime may be compensated per "
         "company policy.",
         "Vague", ""),
    ],
    "ip": [
        ("ip_ok",
         "All works, inventions, and other output created by the Employee in "
         "the course of and as part of the Employee's regularly-assigned "
         "duties shall belong to the Company, consistent with Section 178.3 "
         "of the Intellectual Property Code. Works created outside the scope "
         "of assigned duties remain the Employee's, even if Company time, "
         "facilities, or materials were used, unless otherwise agreed in "
         "writing.",
         "Compliant", "178"),
        ("ip_all",
         "The Employee assigns to the Company all intellectual property "
         "conceived or created during the period of employment, whether or "
         "not related to the Employee's duties, made during or outside "
         "working hours, including works created before employment.",
         "Non-compliant", "178"),
    ],
    "dispute": [
        ("disp_ok",
         "Any dispute arising from this Contract shall first be referred to "
         "the Company's grievance procedure. Nothing in this Contract shall "
         "prevent the Employee from filing a complaint with the National "
         "Labor Relations Commission or the Department of Labor and "
         "Employment, including under the Single Entry Approach (SEnA).",
         "Compliant", "224"),
        ("disp_bad",
         "The Employee agrees that any and all claims arising from this "
         "employment shall be resolved exclusively by private arbitration "
         "in Singapore at the Employee's expense, and waives recourse to "
         "Philippine labor tribunals.",
         "Non-compliant", "224"),
        ("disp_vague",
         "Disputes shall be settled amicably whenever possible.",
         "Vague", ""),
    ],
}
