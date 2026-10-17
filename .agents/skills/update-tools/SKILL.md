---
description: >-
  Authoritative workflow for updating tool-* skills when upgrading tool versions.
  Use when upgrading dependencies in pyproject.toml or when upstream tools introduce new features, syntax, or flags.
  Triggers: update tools, upgrade tool, update skill, bump dependency, sync skills.
name: update-tools
version: 1.0.0
---

# Updating Tool Skills (`update-tools`)

This skill defines the maintenance workflow for keeping `.agents/skills/tool-*`
up to date when tools used by Zenith are upgraded to new versions.

Use this skill whenever dependencies are upgraded in `pyproject.toml` or when a
tool introduces new features, syntax, or configuration changes.

---

## 1. Upgrade Detection & Inventory

When upgrading project tools, inspect version bumps to identify which skills
require review.

```bash
# Compare lockfile or dependency group changes
git diff pyproject.toml uv.lock
```

### Upstream Sources & Official Skills Registry

| Tool | Official Skill Source | Changelog / Docs |
| --- | --- | --- |
| `poethepoet` | Built into package wheel (`poethepoet/skills/`) | `poethepoet.natn.io` |
| `uv` | `astral-sh/claude-code-plugins` (GitHub) | `docs.astral.sh/uv` |
| `ruff` | `astral-sh/claude-code-plugins` (GitHub) | `docs.astral.sh/ruff` |
| `pyrefly` | Meta Pyrefly repository | `pyrefly.org` |
| `complexipy` | `complexipy` GitHub releases | GitHub releases |
| `tach` | `tach` repository | `docs.gauge.sh` |
| `rumdl` | `rumdl` repository | GitHub releases |
| `typos` | `crate-ci/typos` | GitHub releases |
| `zensical` | `zensical` docs | `zensical.org` |
| `pytest` | `pytest` releases & plugin docs | `docs.pytest.org` |
| `typst` | `typst` releases | `typst.app/docs` |
| `cookiecutter` | Template repository | `cookiecutter.readthedocs.io` |

---

## 2. Researching Upstream Changes

Before editing a skill, review what changed in the upgraded tool version:

1. **Check for upstream official skill updates**:
   - For `poethepoet`, inspect the newly installed wheel:

     ```bash
     uv run python -c "import poethepoet, os; print(os.path.dirname(poethepoet.__file__))"
     ```

   - For Astral tools (`uv`, `ruff`), check `astral-sh/claude-code-plugins`.
2. **Review breaking changes & deprecations**: Check if CLI flags, TOML
   tables, or default behaviors have changed.
3. **Review new configuration options**: Check for new linter rules, new CLI
   subcommands, or optimized settings suitable for Zenith's strict preset.

---

## 3. Updating the Skill Document

Update the corresponding `.agents/skills/tool-<name>/SKILL.md` (and any
reference docs under `references/`):

- **CLI Commands**: Update commands if subcommands or flags changed.
- **Configuration Sections**: Update example TOML tables to match new options.
- **Version Frontmatter**: Bump the skill `version:` field.
- **Strict Formatting Compliance**:
  - Narrative line length: strictly $\le 88$ characters.
  - Code block line length: strictly $\le 79$ characters.
  - Frontmatter sorting: `description` before `name` (MD072).
  - Heading hierarchy: narrative content must precede subheadings (MD082).
  - Blank lines: code fences must be surrounded by blank lines (MD031).
  - Embedded Python: snippets must pass `ruff check` and `ruff format`.

---

## 4. Syncing Template Skills

Zenith maintains skills in both the root repository and the generated template
slug.

> [!IMPORTANT]
> **Repo-Only Skills**:
> `tool-cookiecutter`, `update-tools`, and `inspect-module-setup` belong
> **strictly** to the root template repository. **NEVER** copy them into
> `{{cookiecutter.project_slug}}`.

Sync only the project-facing skills to the template slug:

```bash
# Sync all tool skills EXCEPT tool-cookiecutter
for skill_dir in .agents/skills/tool-*; do
    skill_name=$(basename "$skill_dir")
    if [ "$skill_name" != "tool-cookiecutter" ]; then
        rsync -av --delete "$skill_dir/" \
            "{{cookiecutter.project_slug}}/.agents/skills/$skill_name/"
    fi
done

# Sync python-style-guide
rsync -av --delete .agents/skills/python-style-guide/ \
    "{{cookiecutter.project_slug}}/.agents/skills/python-style-guide/"
```

---

## 5. Verification & Quality Gates

Run the full verification pipeline before committing changes:

```bash
# 1. Lint markdown across all skills
PATH="$(uv run which ruff | xargs dirname):$PATH" \
  uvx rumdl check --config {{cookiecutter.project_slug}}/rumdl.toml .agents/skills

# 2. Check spelling
uvx typos --config {{cookiecutter.project_slug}}/typos.toml .agents/skills

# 3. Run template unit tests
uv run pytest

# 4. Run end-to-end smoke test
uv run python -c "
import tempfile, subprocess
from cookiecutter.main import cookiecutter

with tempfile.TemporaryDirectory() as tmpdir:
    proj = cookiecutter('.', no_input=True, output_dir=tmpdir)
    subprocess.run(['uv', 'sync'], cwd=proj, check=True)
    subprocess.run(['uv', 'run', 'poe', 'code-quality'], cwd=proj, check=True)
    subprocess.run(['uv', 'run', 'poe', 'test'], cwd=proj, check=True)
    subprocess.run(['uv', 'run', 'poe', 'docs-build'], cwd=proj, check=True)
"
```
