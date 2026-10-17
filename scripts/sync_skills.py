"""Synchronize repository agent skills with template skills as relative symlinks.

The template skills directory (`{{cookiecutter.project_slug}}/.agents/skills/`)
serves as the canonical single source of truth. This script ensures every shared
skill in `.agents/skills/` is a relative symlink pointing directly to its template
counterpart.

Repository-specific skills that only exist in `.agents/skills/` (e.g.
`inspect-module-setup`, `tool-cookiecutter`, `update-tools`, `zenith-example-sync`)
are preserved untouched.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

DEFAULT_SOURCE = Path("{{cookiecutter.project_slug}}/.agents/skills")
DEFAULT_TARGET = Path(".agents/skills")


def sync_skills(
    source_dir: Path,
    target_dir: Path,
    *,
    check_only: bool = False,
) -> list[str]:
    """Ensure skills in target_dir are relative symlinks to source_dir.

    Parameters
    ----------
    source_dir : Path
        Canonical source directory containing template skills.
    target_dir : Path
        Target directory where symlinks should reside (.agents/skills).
    check_only : bool, optional
        If True, only verify that symlinks are valid and up to date without
        making disk changes, by default False.

    Returns
    -------
    list[str]
        List of error messages or discrepancies found.
    """
    errors: list[str] = []

    src_resolved = source_dir.resolve()
    tgt_resolved = target_dir.resolve()

    if not src_resolved.is_dir():
        return [f"Source directory not found: {source_dir}"]
    if not tgt_resolved.is_dir():
        return [f"Target directory not found: {target_dir}"]

    source_skills = sorted(
        [d for d in src_resolved.iterdir() if d.is_dir() and not d.name.startswith(".")]
    )

    for src_skill in source_skills:
        skill_name = src_skill.name
        tgt_skill = target_dir / skill_name
        rel_target = os.path.relpath(src_skill, tgt_resolved)

        if tgt_skill.is_symlink():
            current_target = os.readlink(tgt_skill)
            if current_target == rel_target:
                continue
            if check_only:
                errors.append(
                    f"{skill_name}: symlink points to '{current_target}', expected '{rel_target}'"
                )
                continue
            tgt_skill.unlink()
        elif tgt_skill.exists():
            if check_only:
                errors.append(
                    f"{skill_name}: expected symlink to '{rel_target}', but found directory/file"
                )
                continue
            if tgt_skill.is_dir():
                shutil.rmtree(tgt_skill)
            else:
                tgt_skill.unlink()
        elif check_only:
            errors.append(f"{skill_name}: missing symlink in {target_dir}")
            continue

        tgt_skill.symlink_to(rel_target)

    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for skill synchronization."""
    parser = argparse.ArgumentParser(
        description="Synchronize repository skills with template skills via symlinks."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Path to source template skills directory.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Path to target repository skills directory.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify symlinks without modifying disk; exit non-zero if drift is found.",
    )

    args = parser.parse_args(argv)

    action_label = "Checking" if args.check else "Synchronizing"
    print(f"🔄 {action_label} skills: {args.target} -> {args.source}...")

    errors = sync_skills(args.source, args.target, check_only=args.check)

    if errors:
        prefix = "❌ Verification failed" if args.check else "❌ Synchronization failed"
        print(f"\n{prefix}:", file=sys.stderr)
        for err in errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    success_label = (
        "All skills properly symlinked to template source of truth!"
        if args.check
        else "Successfully synchronized all skills with template source of truth!"
    )
    print(f"✅ {success_label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
