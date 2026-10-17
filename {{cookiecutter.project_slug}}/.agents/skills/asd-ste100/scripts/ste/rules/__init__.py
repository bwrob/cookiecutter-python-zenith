"""Registry and aggregation of STE structural rules."""

from collections.abc import Sequence

from ste.rules.base import Rule
from ste.rules.lists import DANGLING_CONJUNCTION_RULE, DanglingConjunctionRule
from ste.rules.patterns import (
    MARKETING_ADJECTIVE_RULE,
    NOMINALIZATION_RULE,
    PASSIVE_VOICE_RULE,
    PATTERN_RULES,
    PHRASAL_VERB_RULE,
    PRESENT_PERFECT_RULE,
    SEMICOLON_RULE,
    PatternRule,
)
from ste.rules.sentences import LONG_SENTENCE_RULE, LongSentenceRule
from ste.rules.synonyms import SYNONYM_ROTATION_RULE, SynonymRotationRule

ALL_RULES: tuple[Rule, ...] = (
    *PATTERN_RULES,
    LONG_SENTENCE_RULE,
    SYNONYM_ROTATION_RULE,
    DANGLING_CONJUNCTION_RULE,
)

RULE_MAP: dict[str, Rule] = {rule.id: rule for rule in ALL_RULES}


def get_rules(disabled: Sequence[str] | None = None) -> tuple[Rule, ...]:
    """Return active rules, excluding any rule IDs listed in `disabled`."""
    if not disabled:
        return ALL_RULES
    disabled_set = set(disabled)
    return tuple(rule for rule in ALL_RULES if rule.id not in disabled_set)


__all__ = [
    "ALL_RULES",
    "DANGLING_CONJUNCTION_RULE",
    "LONG_SENTENCE_RULE",
    "MARKETING_ADJECTIVE_RULE",
    "NOMINALIZATION_RULE",
    "PASSIVE_VOICE_RULE",
    "PATTERN_RULES",
    "PHRASAL_VERB_RULE",
    "PRESENT_PERFECT_RULE",
    "RULE_MAP",
    "SEMICOLON_RULE",
    "SYNONYM_ROTATION_RULE",
    "DanglingConjunctionRule",
    "LongSentenceRule",
    "PatternRule",
    "Rule",
    "SynonymRotationRule",
    "get_rules",
]
