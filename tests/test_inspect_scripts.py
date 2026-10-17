"""Unit tests for .agents/skills/inspect-module-setup/scripts/ (audit_repo.py & harvest_skills.py)."""

import sys
from pathlib import Path

SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent
    / ".agents"
    / "skills"
    / "inspect-module-setup"
    / "scripts"
)
sys.path.insert(0, str(SCRIPTS_DIR))

import audit_repo
import harvest_skills


def test_pillar_2_dependency_pinning_order(tmp_path: Path) -> None:
    """Bug: >=1.0,<2.0 previously matched gte_count == total before checking upper_count.
    Root cause: if gte_count == total was evaluated before if upper_count > 0.
    Fix: evaluate upper_count > 0 and strict_count > 0 before gte_count == total.
    """
    pyproject_upper: dict[str, object] = {
        "project": {
            "dependencies": [
                "pydantic>=2.0,<3.0",
                "httpx>=0.27.0",
            ]
        }
    }
    audit_upper = audit_repo.audit_pillar_2_dependencies(tmp_path, pyproject_upper)
    assert any(
        "Restrictive upper bounds (`<`) present in 1/2 dependencies" in d
        for d in audit_upper.details
    )

    pyproject_open: dict[str, object] = {
        "project": {
            "dependencies": [
                "pydantic>=2.0",
                "httpx>=0.27.0",
            ]
        }
    }
    audit_open = audit_repo.audit_pillar_2_dependencies(tmp_path, pyproject_open)
    assert any(
        "Pure open lower bounds (`>=`) across all 2 dependencies" in d
        for d in audit_open.details
    )


def test_config_subdirectory_and_ty_detection(tmp_path: Path) -> None:
    """Verify detection of config/ruff.toml, config/ty.toml, config/pytest.ini, and duties.py."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "ruff.toml").write_text(
        '[lint]\nselect = ["ALL"]\n', encoding="utf-8"
    )
    (config_dir / "ty.toml").write_text("[environment]\n", encoding="utf-8")
    (config_dir / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (config_dir / "coverage.ini").write_text("[run]\nbranch = true\n", encoding="utf-8")
    (tmp_path / "duties.py").write_text("# duty tasks\n", encoding="utf-8")

    p3 = audit_repo.audit_pillar_3_static_analysis(tmp_path, {})
    assert any("Ruff configured" in s for s in p3.strengths)
    assert any("Astral `ty`" in s for s in p3.strengths)

    p4 = audit_repo.audit_pillar_4_task_runner(tmp_path, {})
    assert p4.level == 3
    assert any("duties.py" in s for s in p4.strengths)

    p5 = audit_repo.audit_pillar_5_testing(tmp_path, {})
    assert any("Pytest test framework configuration" in s for s in p5.strengths)
    assert any("Coverage tracking configured" in s for s in p5.strengths)


def test_maturin_python_layout_detection(tmp_path: Path) -> None:
    """Verify Maturin python/<pkg> and python/tests layout detection in Pillars 1 and 5."""
    (tmp_path / "python" / "my_pkg").mkdir(parents=True)
    (tmp_path / "python" / "tests").mkdir(parents=True)
    (tmp_path / "Cargo.toml").write_text('[package]\nname = "demo"\n', encoding="utf-8")

    pyproject: dict[str, object] = {
        "build-system": {"build-backend": "maturin", "requires": ["maturin>=1.0"]},
        "project": {"name": "demo"},
    }
    p1 = audit_repo.audit_pillar_1_packaging(tmp_path, pyproject)
    assert any("Dedicated `python/` source layout" in s for s in p1.strengths)
    assert any("Rust / PyO3 extension" in s for s in p1.strengths)

    p5 = audit_repo.audit_pillar_5_testing(tmp_path, pyproject)
    assert any("`python/tests`" in s for s in p5.strengths)


def test_harvest_repo_discovers_agent_configs(tmp_path: Path) -> None:
    """Verify harvest_repo discovers AGENTS.md, novel skills, and AI_POLICY.md."""
    (tmp_path / "AGENTS.md").write_text("# Instructions\n", encoding="utf-8")
    (tmp_path / "AI_POLICY.md").write_text("# AI Policy\n", encoding="utf-8")
    skill_dir = tmp_path / ".agents" / "skills" / "zz-novel-demo-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: zz-novel-demo-skill\ndescription: Demo skill\n---\n# Body\n",
        encoding="utf-8",
    )

    result = harvest_skills.harvest_repo(tmp_path)
    assert any("AGENTS.md" in inst for inst in result.instructions)
    assert result.ai_policy_present is True
    novel_names = {s.name for s in result.novel_skills}
    assert "zz-novel-demo-skill" in novel_names
    assert result.novel_skills[0].description == "Demo skill"
