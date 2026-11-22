import re
from pathlib import Path


def test_report_has_required_interpretation_limitations_and_outline():
    report = Path("report/report.md").read_text(encoding="utf-8")
    required_statement = (
        "The distinctive structural signatures observed illustrate a potential "
        "privacy concern. They do not establish that any person can actually be "
        "identified, because identification would additionally require accurate "
        "auxiliary knowledge, a reliable matching procedure, and a link from an "
        "anonymous node to a real individual."
    )
    assert required_statement in report
    for reason in (
        "Auxiliary knowledge is required",
        "Exactness is fragile",
        "Uniqueness is graph-relative",
        "Structure is not identity",
        "A necessary, not sufficient, condition",
        "The data are synthetic",
        "Risk is probabilistic",
    ):
        assert reason in report
    for required_heading in (
        "## 1. Introduction and motivation",
        "## 2. Method",
        "## 3. Implementation and reproducibility",
        "## 4. Results",
        "## 5. Privacy interpretation",
        "## 6. Limitations",
        "## 7. Conclusion",
        "## References",
        "## Appendix A. Run details",
    ):
        assert required_heading in report


def test_report_abstract_is_150_whitespace_delimited_words():
    report = Path("report/report.md").read_text(encoding="utf-8")
    abstract = report.split("## Abstract\n\n", 1)[1].split("\n\n## 1.", 1)[0]
    assert len(re.findall(r"\S+", abstract)) == 150
