"""Regex pattern-based structural STE rules."""

import re
from dataclasses import dataclass

from ste.model import Document, Finding, Severity


@dataclass(frozen=True, slots=True)
class PatternRule:
    """A rule that checks blocks for regex matches."""

    id: str
    severity: Severity
    pattern: re.Pattern[str]
    message: str
    description: str

    def check(self, document: Document) -> list[Finding]:
        """Scan each block in the document for pattern matches."""
        findings: list[Finding] = []
        for block in document.blocks:
            for match in self.pattern.finditer(block.text):
                line, col = block.locate(match.start())
                if document.suppressions.silences(line, self.id):
                    continue
                findings.append(
                    Finding(
                        file=document.filename,
                        line=line,
                        column=col,
                        rule=self.id,
                        severity=self.severity,
                        match=match.group(0),
                        message=self.message,
                    )
                )
        return findings


SEMICOLON_RULE = PatternRule(
    id="semicolon",
    severity=Severity.HARD,
    pattern=re.compile(r";"),
    message="STE bans the semicolon (Rule 8.1). Split into separate sentences.",
    description="Check for prohibited semicolons.",
)

PHRASAL_VERB_RULE = PatternRule(
    id="phrasal-verb",
    severity=Severity.HARD,
    pattern=re.compile(
        r"\b(spin(?:ning|s)? up|spun up|reach(?:ing|es|ed)? out|div(?:e|es|ing|ed) into|"
        r"dove into|kick(?:ing|s|ed)? off|circl(?:e|es|ing|ed) back|touch(?:ing|es|ed)? base)\b",
        re.IGNORECASE,
    ),
    message="Soft phrasal verb. Use the single plain verb (start, contact, read, begin).",
    description="Check for informal phrasal verbs.",
)

MARKETING_ADJECTIVE_RULE = PatternRule(
    id="marketing-adjective",
    severity=Severity.HARD,
    pattern=re.compile(
        r"\b(seamless(?:ly)?|robust(?:ly)?|cutting-edge|effortless(?:ly)?|blazing[- ]fast|"
        r"world-class|state-of-the-art|game-chang(?:ing|er))\b",
        re.IGNORECASE,
    ),
    message="Marketing adjective. Delete, or replace with the measurement that earns the claim.",
    description="Check for hyperbolic marketing adjectives.",
)

NOMINALIZATION_RULE = PatternRule(
    id="nominalization",
    severity=Severity.HARD,
    pattern=re.compile(
        r"\b(perform|performs|performed|conduct|conducts|conducted|carry out|carries out|carried out)"
        r"\s+(?:a|an|the)\s+\w+(?:tion|sion|ment|ance|ence|ysis)\b",
        re.IGNORECASE,
    ),
    message="Action frozen into a noun. Use the verb (analyze, not perform an analysis of).",
    description="Check for nominalized verbs (e.g. 'perform an analysis').",
)

PASSIVE_VOICE_RULE = PatternRule(
    id="passive-voice",
    severity=Severity.ADVISORY,
    pattern=re.compile(
        r"\b(is|are|was|were|been|being)\s+(\w+ed|given|taken|made|done|found|seen|known|"
        r"shown|written|built|sent|set|run|read|kept|held|left|put)\b(?!\s+(?:to|for|by)\s+\w+ing)",
        re.IGNORECASE,
    ),
    message="Possible passive voice. Name the actor and use an active verb, unless the actor is unknown or irrelevant.",
    description="Check for passive voice constructions (advisory).",
)

PRESENT_PERFECT_RULE = PatternRule(
    id="present-perfect",
    severity=Severity.ADVISORY,
    # Hedges (may have, might have, could have, should have, would have, must have) are protected.
    pattern=re.compile(
        r"(?<!\bmay )(?<!\bmight )(?<!\bcould )(?<!\bshould )(?<!\bwould )(?<!\bmust )"
        r"\b(has|have|had)\s+(?:been\s+)?\w+(?:ed|en)\b",
        re.IGNORECASE,
    ),
    message="Compound tense. Use simple past/present unless current relevance is the point (then keep and flag).",
    description="Check for compound tenses / present perfect (advisory).",
)

PATTERN_RULES: tuple[PatternRule, ...] = (
    SEMICOLON_RULE,
    PHRASAL_VERB_RULE,
    MARKETING_ADJECTIVE_RULE,
    NOMINALIZATION_RULE,
    PASSIVE_VOICE_RULE,
    PRESENT_PERFECT_RULE,
)
