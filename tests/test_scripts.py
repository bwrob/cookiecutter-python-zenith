"""Unit tests for repository maintenance and validation scripts."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts import check_skills, sync_example, sync_skills

# --- check_skills.py tests ---


def test_parse_frontmatter_valid() -> None:
    content = (
        "---\nname: my-skill\ndescription: A valid skill description.\n---\n# Body\n"
    )
    meta = check_skills.parse_frontmatter(content)
    assert meta["name"] == "my-skill"
    assert meta["description"] == "A valid skill description."


def test_parse_frontmatter_multiline_folded() -> None:
    content = (
        "---\n"
        "name: my-skill\n"
        "description: >-\n"
        "  A multiline description\n"
        "  that spans multiple lines.\n"
        "extra_key: extra_value\n"
        "---\n"
    )
    meta = check_skills.parse_frontmatter(content)
    assert meta["name"] == "my-skill"
    assert "A multiline description that spans multiple lines." in meta["description"]
    assert meta["extra_key"] == "extra_value"


def test_parse_frontmatter_trailing_multiline() -> None:
    content = "---\nname: my-skill\ndescription: >-\n  Line one\n  Line two\n---\n"
    meta = check_skills.parse_frontmatter(content)
    assert meta["description"] == "Line one Line two"


def test_parse_frontmatter_empty_value_and_orphan_line() -> None:
    content = "---\n  orphan line before any key\nempty_key:\nname: my-skill\n---\n"
    meta = check_skills.parse_frontmatter(content)
    assert "empty_key" not in meta
    assert meta["name"] == "my-skill"


def test_parse_frontmatter_missing_boundary() -> None:
    with pytest.raises(ValueError, match="Missing leading '---'"):
        check_skills.parse_frontmatter("name: my-skill\n")


def test_parse_frontmatter_unclosed() -> None:
    with pytest.raises(ValueError, match="Unclosed frontmatter"):
        check_skills.parse_frontmatter("---\nname: my-skill\n")


def test_validate_skill_missing_file(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    errors = check_skills.validate_skill(skill_dir)
    assert any("Missing required SKILL.md" in e for e in errors)


def test_validate_skill_read_error(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("dummy", encoding="utf-8")

    with patch.object(Path, "read_text", side_effect=OSError("Permission denied")):
        errors = check_skills.validate_skill(skill_dir)
        assert any("Failed to read" in e for e in errors)


def test_validate_skill_invalid_frontmatter(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("invalid content", encoding="utf-8")
    errors = check_skills.validate_skill(skill_dir)
    assert any("Invalid frontmatter" in e for e in errors)


def test_validate_skill_missing_name(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\ndescription: Valid description here.\n---\n", encoding="utf-8"
    )
    errors = check_skills.validate_skill(skill_dir)
    assert any("missing 'name'" in e for e in errors)


def test_validate_skill_name_mismatch(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: wrong-name\ndescription: Valid description here.\n---\n",
        encoding="utf-8",
    )
    errors = check_skills.validate_skill(skill_dir)
    assert any("does not match directory" in e for e in errors)


def test_validate_skill_missing_description(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\n---\n", encoding="utf-8"
    )
    errors = check_skills.validate_skill(skill_dir)
    assert any("missing 'description'" in e for e in errors)


def test_validate_skill_brief_description(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: Short\n---\n", encoding="utf-8"
    )
    errors = check_skills.validate_skill(skill_dir)
    assert any("description is too brief" in e for e in errors)


def test_validate_skill_broken_link(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A valid comprehensive description.\n---\n"
        "See [Template](./templates/missing.md) for details.\n",
        encoding="utf-8",
    )
    errors = check_skills.validate_skill(skill_dir)
    assert any("broken link to missing file" in e for e in errors)


def test_validate_skill_valid(tmp_path: Path) -> None:
    skill_dir = tmp_path / "test-skill"
    templates_dir = skill_dir / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "recipe.md").write_text("# Recipe\n", encoding="utf-8")

    (skill_dir / "SKILL.md").write_text(
        "---\nname: test-skill\ndescription: A valid comprehensive description.\n---\n"
        "See [Recipe](./templates/recipe.md) for details.\n",
        encoding="utf-8",
    )
    errors = check_skills.validate_skill(skill_dir)
    assert errors == []


def test_check_skills_main_missing_dir(tmp_path: Path) -> None:
    ret = check_skills.main([str(tmp_path / "nonexistent")])
    assert ret == 1


def test_check_skills_main_empty_dir(tmp_path: Path) -> None:
    skills_dir = tmp_path / "empty_skills"
    skills_dir.mkdir()
    ret = check_skills.main([str(skills_dir)])
    assert ret == 0


def test_check_skills_main_failure(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "invalid-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\n---\n", encoding="utf-8")
    ret = check_skills.main([str(skills_dir)])
    assert ret == 1


def test_check_skills_main_success(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "valid-skill"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: valid-skill\ndescription: A valid description with plenty of characters.\n---\n",
        encoding="utf-8",
    )
    ret = check_skills.main([str(skills_dir)])
    assert ret == 0


# --- sync_example.py tests ---


def test_sync_example(tmp_path: Path) -> None:
    target_dir = tmp_path / "test-showcase"
    target_dir.mkdir()
    git_dir = target_dir / ".git"
    git_dir.mkdir()
    old_file = target_dir / "old_file.txt"
    old_file.write_text("old", encoding="utf-8")
    old_sub = target_dir / "old_sub"
    old_sub.mkdir()

    fake_rendered = tmp_path / "fake_rendered"
    fake_rendered.mkdir()
    (fake_rendered / "new_file.txt").write_text("new", encoding="utf-8")
    new_sub = fake_rendered / "new_sub"
    new_sub.mkdir()
    (new_sub / "inner.txt").write_text("inner", encoding="utf-8")

    with (
        patch("scripts.sync_example.cookiecutter", return_value=str(fake_rendered)),
        patch("subprocess.run") as mock_run,
    ):
        result = sync_example.sync_example(target_dir, lock=True)
        assert result == target_dir.resolve()
        assert git_dir.exists()
        assert not old_file.exists()
        assert not old_sub.exists()
        assert (target_dir / "new_file.txt").exists()
        assert (target_dir / "new_sub" / "inner.txt").exists()
        assert mock_run.call_count == 2  # uv lock, uv run poe fix


def test_sync_example_no_lock(tmp_path: Path) -> None:
    target_dir = tmp_path / "test-showcase-nolock"
    target_dir.mkdir()

    fake_rendered = tmp_path / "fake_rendered_nolock"
    fake_rendered.mkdir()
    (fake_rendered / "file.txt").write_text("content", encoding="utf-8")

    with (
        patch("scripts.sync_example.cookiecutter", return_value=str(fake_rendered)),
        patch("subprocess.run") as mock_run,
    ):
        result = sync_example.sync_example(target_dir, lock=False)
        assert result == target_dir.resolve()
        assert mock_run.call_count == 1  # only uv run poe fix


def test_sync_example_main() -> None:
    with (
        patch("scripts.sync_example.sync_example") as mock_sync,
        patch.object(sys, "argv", ["sync_example.py", "/tmp/dest", "--no-lock"]),
    ):
        sync_example.main()
        mock_sync.assert_called_once_with(Path("/tmp/dest"), lock=False)


# --- sync_skills.py tests ---


def test_sync_skills_missing_source_or_target(tmp_path: Path) -> None:
    non_existent = tmp_path / "missing"
    existing = tmp_path / "exists"
    existing.mkdir()

    errs_src = sync_skills.sync_skills(non_existent, existing)
    assert any("Source directory not found" in e for e in errs_src)

    errs_tgt = sync_skills.sync_skills(existing, non_existent)
    assert any("Target directory not found" in e for e in errs_tgt)


def test_sync_skills_success_and_check(tmp_path: Path) -> None:
    src_dir = tmp_path / "src_skills"
    src_dir.mkdir()
    (src_dir / "my-skill").mkdir()

    tgt_dir = tmp_path / "tgt_skills"
    tgt_dir.mkdir()

    # Synchronize
    errs = sync_skills.sync_skills(src_dir, tgt_dir, check_only=False)
    assert errs == []
    tgt_skill = tgt_dir / "my-skill"
    assert tgt_skill.is_symlink()

    # Check mode when already in sync
    check_errs = sync_skills.sync_skills(src_dir, tgt_dir, check_only=True)
    assert check_errs == []


def test_sync_skills_check_drift_conditions(tmp_path: Path) -> None:
    src_dir = tmp_path / "src_skills"
    src_dir.mkdir()
    (src_dir / "skill-a").mkdir()
    (src_dir / "skill-b").mkdir()
    (src_dir / "skill-c").mkdir()

    tgt_dir = tmp_path / "tgt_skills"
    tgt_dir.mkdir()

    # skill-a is a symlink pointing to wrong place
    (tgt_dir / "skill-a").symlink_to("../../wrong_path")
    # skill-b is a directory
    (tgt_dir / "skill-b").mkdir()
    # skill-c does not exist in target

    errs = sync_skills.sync_skills(src_dir, tgt_dir, check_only=True)
    assert len(errs) == 3
    assert any("skill-a: symlink points to" in e for e in errs)
    assert any("skill-b: expected symlink" in e for e in errs)
    assert any("skill-c: missing symlink" in e for e in errs)


def test_sync_skills_overwrite_existing(tmp_path: Path) -> None:
    src_dir = tmp_path / "src_skills"
    src_dir.mkdir()
    (src_dir / "skill-dir").mkdir()
    (src_dir / "skill-file").mkdir()

    tgt_dir = tmp_path / "tgt_skills"
    tgt_dir.mkdir()

    # Existing directory
    dir_target = tgt_dir / "skill-dir"
    dir_target.mkdir()
    (dir_target / "nested.txt").write_text("old", encoding="utf-8")

    # Existing regular file
    file_target = tgt_dir / "skill-file"
    file_target.write_text("old file", encoding="utf-8")

    errs = sync_skills.sync_skills(src_dir, tgt_dir, check_only=False)
    assert errs == []
    assert dir_target.is_symlink()
    assert file_target.is_symlink()

    # Re-run with wrong symlink
    dir_target.unlink()
    dir_target.symlink_to("invalid")
    errs2 = sync_skills.sync_skills(src_dir, tgt_dir, check_only=False)
    assert errs2 == []
    assert dir_target.is_symlink()


def test_sync_skills_main(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "sample").mkdir()

    tgt_dir = tmp_path / "tgt"
    tgt_dir.mkdir()

    # Success sync
    ret_sync = sync_skills.main(["--source", str(src_dir), "--target", str(tgt_dir)])
    assert ret_sync == 0

    # Success check
    ret_check = sync_skills.main(
        ["--source", str(src_dir), "--target", str(tgt_dir), "--check"]
    )
    assert ret_check == 0

    # Failure sync (missing source)
    ret_fail_sync = sync_skills.main(
        ["--source", str(tmp_path / "nonexistent"), "--target", str(tgt_dir)]
    )
    assert ret_fail_sync == 1

    # Failure check (missing source)
    ret_fail_check = sync_skills.main(
        ["--source", str(tmp_path / "nonexistent"), "--target", str(tgt_dir), "--check"]
    )
    assert ret_fail_check == 1
