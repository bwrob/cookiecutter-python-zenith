"""Formatters for lint results (standard console output and JSON)."""

import json
from collections.abc import Sequence

from ste.model import Finding


def format_text(
    findings: Sequence[Finding],
    words_total: int,
    hard_count: int,
    baseline: int = 0,
) -> str:
    """Format findings in standard compiler/linter terminal format."""
    lines: list[str] = []
    for f in findings:
        lines.append(f"{f.file}:{f.line}:{f.column} {f.rule}: {f.message} [{f.match}]")

    rate = round(len(findings) * 100 / words_total, 1) if words_total else 0.0
    summary = (
        f"\n{len(findings)} violations ({hard_count} hard, baseline {baseline}), "
        f"{words_total} words, {rate} per 100 words\n"
        "Hedges/modality (may, might, could) are never flagged: confidence is content."
    )
    lines.append(summary)
    return "\n".join(lines)


def format_json(
    findings: Sequence[Finding],
    words_total: int,
    hard_count: int,
    baseline: int = 0,
) -> str:
    """Format findings as structured JSON."""
    rate = round(len(findings) * 100 / words_total, 1) if words_total else 0.0
    payload = {
        "violations": [f.to_dict() for f in findings],
        "count": len(findings),
        "hard_count": hard_count,
        "baseline": baseline,
        "words": words_total,
        "per_100_words": rate,
    }
    return json.dumps(payload, indent=2)
