# Improvement Proposal: [Area / Feature / Skill] (Learned from [Project Name(s)])

## 1. Executive Summary & Architectural Rationale

Detailed explanation of the discovered pattern, skill, or configuration mechanism:

- **Problem Solved**: What edge case, runtime failure, type-checker crash, or developer friction this addresses.
- **Why It Matters**: Concrete rationale for why best-in-class projects adopt it and why Zenith benefits.

## 2. Benchmark Source & Context

- **Target Project(s)**: `[org/repo]` (with specific file paths and line numbers)
- **Discovered Pattern**: `[e.g., Trusted Publishing OIDC / PEP 735 groups / AI Policy / Custom Agent Skill]`

## 3. Gap Analysis (Target vs. `{{cookiecutter.project_slug}}`)

| Capability | Target Repo Pattern | `{{cookiecutter.project_slug}}` State | Advantage |
| --- | --- | --- | --- |

## 4. Concrete Code Diffs & Drop-in Replacements

Exact configuration diffs and drop-in code blocks targeting specific files in `{{cookiecutter.project_slug}}/` or root assets:

```toml
# File: {{cookiecutter.project_slug}}/[config_file]
<<<<
[existing_content]
====
[proposed_replacement_content]
>>>>
```

## 5. Verification Plan

Exact verification steps and shell commands:

- Unit & template tests (`uv run pytest`).
- Static analysis & formatting verification (`uv run ruff check && uv run ruff format --check`).
- Pre-commit verification (`uv run pre-commit run --all-files`).
- End-to-end template generation & smoke tests (`uv run poe code-quality`).
