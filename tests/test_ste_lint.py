"""Unit tests for .agents/skills/asd-ste100/scripts/ (ste modular linter package)."""

import io
import sys
from pathlib import Path

SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "asd-ste100"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))

from ste.cli import main, run_selftest
from ste.directives import Action, Directive, build_suppressions, parse_directive
from ste.engine import lint_document
from ste.inline import mask_inline
from ste.markdown import _frontmatter, parse, split_table_row
from ste.model import Block, BlockKind, Finding, Severity, Span, Suppressions
from ste.reporter import format_json, format_text
from ste.rules import ALL_RULES, get_rules


def test_span_and_block_locate() -> None:
    """Test Span and Block coordinate mapping."""
    block = Block(
        kind=BlockKind.PARAGRAPH,
        text="First line. Second line.",
        spans=(
            Span(offset=0, line=10, column=1),
            Span(offset=12, line=11, column=5),
        ),
    )
    # First span
    assert block.locate(0) == (10, 1)
    assert block.locate(5) == (10, 6)
    # Second span
    assert block.locate(12) == (11, 5)
    assert block.locate(18) == (11, 11)


def test_suppressions_silencing() -> None:
    """Test Suppressions matching and line ranges."""
    sup = Suppressions(
        ranges=(
            (5, 7, frozenset({"semicolon"})),
            (10, 12, frozenset()),  # silences all
        )
    )
    assert sup.silences(6, "semicolon")
    assert not sup.silences(6, "long-sentence")
    assert not sup.silences(4, "semicolon")
    assert not sup.silences(8, "semicolon")
    # All rules silenced in 10..12
    assert sup.silences(10, "semicolon")
    assert sup.silences(11, "anything")
    assert not sup.silences(13, "anything")


def test_finding_properties_and_dict() -> None:
    """Test Finding dataclass methods."""
    f = Finding(
        file="test.md",
        line=2,
        column=4,
        rule="semicolon",
        severity=Severity.HARD,
        match=";",
        message="STE bans the semicolon.",
    )
    assert f.sort_key == ("test.md", 2, 4, "semicolon")
    d = f.to_dict()
    assert d["file"] == "test.md"
    assert d["line"] == 2
    assert d["column"] == 4
    assert d["rule"] == "semicolon"
    assert d["severity"] == "hard"
    assert d["match"] == ";"


def test_mask_inline_preserves_length() -> None:
    """Verify inline masking preserves string length and column alignment."""
    cases = [
        "Plain text without markup.",
        "Use `code span` inline.",
        "Check [link label](https://example.com/path).",
        "Look at ![image alt](img.png).",
        "See <https://example.com> autolink.",
        "Visit https://example.com/raw naked url.",
        "<span>HTML tag</span>",
        "&amp; and &#123; entities",
        "**bold** and *italic* and ~~strike~~ and `code`",
        "Escaped \\*asterisk\\* in prose",
    ]
    for case in cases:
        masked = mask_inline(case)
        assert len(masked) == len(case), f"Length changed for: {case!r}"


def test_directives_parsing() -> None:
    """Test parsing HTML comment directives."""
    assert parse_directive("not a directive", 1) is None
    d1 = parse_directive("ste-lint-disable", 5)
    assert d1 == Directive(5, Action.DISABLE, frozenset())
    d2 = parse_directive("ste-lint-disable-next-line semicolon, long-sentence", 8)
    assert d2 is not None
    assert d2.action == Action.DISABLE_NEXT_LINE
    assert d2.rules == frozenset({"semicolon", "long-sentence"})

    # Test folding directives into suppressions
    dirs = [
        Directive(3, Action.DISABLE_FILE, frozenset({"passive-voice"})),
        Directive(5, Action.DISABLE, frozenset({"semicolon"})),
        Directive(8, Action.ENABLE, frozenset({"semicolon"})),
        Directive(10, Action.DISABLE_NEXT_LINE, frozenset({"phrasal-verb"})),
    ]
    sup = build_suppressions(dirs, last_line=20)
    assert sup.silences(1, "passive-voice")
    assert sup.silences(20, "passive-voice")
    assert sup.silences(6, "semicolon")
    assert not sup.silences(9, "semicolon")
    assert sup.silences(11, "phrasal-verb")
    assert not sup.silences(12, "phrasal-verb")


def test_split_table_row() -> None:
    """Test GFM table row splitting."""
    assert split_table_row("no pipe here") is None
    assert split_table_row("| only one |") is None

    cells = split_table_row("| Col A | Col B | Col C |")
    assert cells is not None
    assert [c[0] for c in cells] == ["Col A", "Col B", "Col C"]

    escaped = split_table_row("| a \\| b | c |")
    assert escaped is not None
    assert escaped[0][0] == "a \\| b"
    assert escaped[1][0] == "c"


def test_markdown_scanner_structures() -> None:
    """Test markdown parser handling various constructs."""
    text = (
        "---\n"
        "name: test-skill\n"
        "description: >-\n"
        "  First line of description.\n"
        "  Second line of description.\n"
        "---\n"
        "# Main Heading\n"
        "\n"
        "A paragraph with reflowed\n"
        "lines that should join.\n"
        "\n"
        "```python\n"
        "x = 1; y = 2\n"
        "```\n"
        "\n"
        "$$\n"
        "e = mc^2;\n"
        "$$\n"
        "\n"
        "> [!NOTE]\n"
        "> An admonition paragraph inside\n"
        "> a blockquote.\n"
        "\n"
        '!!! tip "Admonition"\n'
        "    Indented admonition text.\n"
        "\n"
        "- First list item and\n"
        "- Second list item\n"
    )
    doc = parse(text, filename="doc.md")
    assert doc.filename == "doc.md"

    kinds = [b.kind for b in doc.blocks]
    assert BlockKind.FRONTMATTER in kinds
    assert BlockKind.HEADING in kinds
    assert BlockKind.PARAGRAPH in kinds
    assert BlockKind.LIST_ITEM in kinds

    # Verify description extraction
    fm_block = next(b for b in doc.blocks if b.kind == BlockKind.FRONTMATTER)
    assert "First line of description" in fm_block.text
    assert "Second line of description" in fm_block.text


def test_markdown_frontmatter_edge_cases() -> None:
    """Test frontmatter parser with missing boundaries or no description."""
    assert _frontmatter([]) == (0, [])
    assert _frontmatter(["# Not frontmatter"]) == (0, [])
    assert _frontmatter(["---", "name: test"]) == (0, [])  # unclosed

    # No description key
    idx, blocks = _frontmatter(["---", "name: test", "---"])
    assert idx == 3
    assert blocks == []

    # Single-line description with quotes
    idx, blocks = _frontmatter(["---", 'description: "Quoted value"', "---"])
    assert idx == 3
    assert len(blocks) == 1
    assert "Quoted value" in blocks[0].text


def test_all_rules_and_get_rules() -> None:
    """Test rule retrieval and filtering."""
    assert len(ALL_RULES) == 9
    active = get_rules(disabled=["semicolon", "passive-voice"])
    assert len(active) == 7
    rule_ids = {r.id for r in active}
    assert "semicolon" not in rule_ids
    assert "passive-voice" not in rule_ids
    assert "phrasal-verb" in rule_ids


def test_lint_engine_and_reporters() -> None:
    """Test engine aggregation and reporter outputs."""
    text = "The system is ready; spin up the cluster."
    doc = parse(text, filename="input.md")
    res = lint_document(doc)
    assert res.hard_count > 0
    assert res.violation_rate > 0.0

    txt_out = format_text(res.findings, res.words_total, res.hard_count, baseline=0)
    assert "violations" in txt_out
    assert "input.md" in txt_out

    json_out = format_json(res.findings, res.words_total, res.hard_count, baseline=0)
    assert '"hard_count":' in json_out
    assert '"violations":' in json_out


def test_cli_selftest() -> None:
    """Run CLI internal selftest directly."""
    assert run_selftest() == 0


def test_cli_execution_with_file_and_stdin(tmp_path: Path) -> None:
    """Test CLI invoking with file argument, stdin, list-rules, and flags."""
    test_file = tmp_path / "sample.md"
    test_file.write_text("All is clean and clear.\n", encoding="utf-8")

    # Clean file passes
    assert main([str(test_file)]) == 0

    # Non-existent file fails
    assert main([str(tmp_path / "missing.md")]) == 1

    # List rules exits 0
    assert main(["--list-rules"]) == 0

    # Selftest flag exits 0
    assert main(["--selftest"]) == 0

    # Stdin input with hard violation
    stdin_stream = io.StringIO("This sentence has; a semicolon.")
    assert main([], stdin=stdin_stream) == 1

    # Stdin with baseline tolerating violation
    stdin_stream2 = io.StringIO("This sentence has; a semicolon.")
    assert main(["--baseline", "1"], stdin=stdin_stream2) == 0

    # JSON output
    stdin_stream3 = io.StringIO("Clean text.")
    assert main(["--json"], stdin=stdin_stream3) == 0
