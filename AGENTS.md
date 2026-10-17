# AGENTS.md

Operational guidelines, architectural conventions, and workflows for AI coding
assistants working on the **Zenith** template repository.

## Project Stewardship

When working in this repository, your primary responsibility is to the long-term health
of the project, its users (both human and agent), and its maintainers—not merely
satisfying the immediate prompt with the shortest possible patch. Act as the first line
of defense against technical debt, architectural drift, and low-quality contributions by
enforcing end-to-end type safety, clean public abstractions, comprehensive test
coverage, and accurate documentation.

## Pre-flight Checks

Before editing code or executing tasks, ensure an isolated, clean working environment:

1. Check repository status with `git status`. Do not make edits when uncommitted changes
   exist without explicit user consent.
2. Confirm remotes and branches before committing or pushing changes. Use git worktrees
   or dedicated feature branches for non-trivial tasks.
3. Run all commands inside the hermetic project environment using `uv run <command>`.
   Never use global or system Python environments directly.
4. When creating temporary or scratch files, always place them in the `.temp/`
   directory. Never pollute the workspace root or tracked directories with temporary
   files.

## Operational Workflows

- **Environment & Packages**: Always use **`uv`**.
  - Sync environment: `uv sync`
  - Add dependency: `uv add <package>` or `uv add --group dev <package>`
  - Run commands in environment: `uv run <command>`
- **Temporary Files**: When creating temporary files, scratch scripts, or intermediate
  test outputs, always store them in the `.temp/` directory.
- **Task Runner**: All development tasks are managed through **Poe the Poet**:
  - `uv run poe test` (run unit tests)
  - `uv run poe code-quality` (run lint, format-check, and tests)
  - `uv run poe fix` (auto-fix linting and formatting)
- **Verification Gate**: Before proposing or finalizing changes, always verify your
  work:
  - `uv run poe test`
  - `uv run poe code-quality`
  - `uv run pre-commit run --all-files`
  - Always re-read any files modified by formatters or `pre-commit` hooks before making
    subsequent edits.
- **Reproduce-First Bug Scoping**: When fixing a bug, first reproduce the failure with a
  minimal test, trace the root cause, and search the codebase for sibling occurrences of
  the same pattern before editing production code.
- **Complexity Reset Rule**: If a fix or implementation starts requiring layered hacks,
  defensive workarounds, or fighting the type checker, stop and re-evaluate the design
  from first principles rather than piling on patches.
- **AI Contribution Policy**: Consult and adhere to `AI_POLICY.md` for human review,
  local verification, and tool disclosure guidelines.

## Project Instructions Discovery & Compatibility

- **Multi-Agent Discovery & Settings**: Instruction files and configuration profiles are
  maintained in the repository root for seamless compatibility across modern AI coding
  tools:
  - **Claude Code**: `CLAUDE.md` symlink (`ln -s AGENTS.md CLAUDE.md`) and
    `.claude/settings.json` (pre-authorizing hermetic `uv run poe:*` commands).
  - **OpenAI Codex CLI**: `.codex/config.toml` (auto-discovering `AGENTS.md` and setting
    `workspace-write` sandbox).
  - **Google Gemini CLI & Antigravity**: `.gemini/settings.json`
    (`contextFileName: "AGENTS.md"`).
  - **GitHub Copilot**: `.github/copilot-instructions.md` referencing `AGENTS.md`.
  - **Cursor & Windsurf**: `.cursorrules` and `.windsurfrules` symlinks
    (`ln -s AGENTS.md .cursorrules`) and `.cursor/rules/zenith.mdc`.
  - **Aider**: `.aider.conf.yml` (auto-loading `AGENTS.md`, wiring `lint-cmd` and
    `test-cmd` to Poe tasks).
- **Scope Hierarchy**: When exploring subdirectories, check for nested `AGENTS.md` or
  `CLAUDE.md` files; localized instructions take precedence within their scope.
- **Workflow & Tool Guidance**: Consult `.agents/skills/` for lifecycle workflow skills
  (`asd-ste100`, `project-setup`, `code-review`, `git-workflow`, `changelog-writing`, `adr`, `skill-creator`, `zenith-example-sync`)
  and tool-specific guidance (`tool-*/SKILL.md`, `python-style-guide`).

## Repository Architecture

- `cookiecutter.json`: Template configuration, prompts (`__prompts__`), and variable
  definitions.
- `hooks/`: Lifecycle hooks (`pre_gen_project.py`, `post_gen_project.py`).
  - `hooks/post_gen_project.py`: Strips educational comments, cleans conditional files
    (CLI, `.github`, LICENSE), and establishes AI agent compatibility symlinks and
    settings.
- `templates/`: Shared template partials (e.g. CI workflow components).
- `{{cookiecutter.project_slug}}/`: Root directory of the rendered project template.
- `tests/`: Automated tests validating template rendering, conditional branches, and
  generated asset structures.
