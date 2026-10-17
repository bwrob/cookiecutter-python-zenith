---
description: >-
  Authoritative workflow for inspecting, auditing, and benchmarking mature Python project setups and development skills to extract best practices and propose improvements.
  Use when benchmarking external repositories, evaluating tool configurations, or proposing template upgrades.
  Triggers: inspect module, audit repo, benchmark setup, extract skills, inspect-module-setup.
name: inspect-module-setup
version: 1.0.0
---

# Inspect Module Setup (`inspect-module-setup`)

This skill defines the structured workflow for auditing, benchmarking, and
reverse-engineering the architecture, configuration, toolchains, CI/CD, and
agent skills of mature Python projects.

Use this skill whenever benchmarking Zenith against best-in-class repositories,
evaluating modern tooling shifts in the Python ecosystem, analyzing agent skills
used during development, or preparing actionable improvement proposals.

Audit progress, candidate queues, and inspected targets are tracked in
`.agents/skills/inspect-module-setup/`:

- **Candidate Queue** (`.agents/skills/inspect-module-setup/candidates.log`):
  Prioritized queue of validated benchmark modules awaiting audit.
- **Inspected Log** (`.agents/skills/inspect-module-setup/inspected.log`): Persistent
  history of completed repository audits across sessions to prevent duplicate analysis.

---

## 1. The 9-Pillar Audit Framework

Inspect target projects across nine foundational dimensions of modern Python
engineering and AI-assisted development.

### Pillar 1: Packaging & Build System

Examine how the package defines metadata, builds artifacts, and exposes APIs:

- **Build Backend**: Identify the PEP 517/518 backend (`uv_build`, `hatchling`,
  `flit-core`, `maturin`, `poetry-core`, or `setuptools`).
- **Metadata Standard**: Check for PEP 621 compliance (`[project]` table in
  `pyproject.toml`), dynamic versioning (`hatch-vcs`), and classifiers.
- **Layout**: Check for `src/` layout vs flat layout, PEP 561 typing marker
  (`py.typed`), namespace packages, and internal encapsulation (`_internal/`).
- **Entry Points**: Inspect console script entry points (`[project.scripts]`)
  and plugin entry points (`[project.entry-points]`).

### Pillar 2: Dependency & Environment Management

Analyze dependency classification, pin strategies, and locking mechanics:

- **Dependency Separation**: Check separation between core runtime dependencies
  (`dependencies`), optional extras (`[project.optional-dependencies]`), and
  development groups (PEP 735 `[dependency-groups]`).
- **Tooling & Locks**: Inspect environment management tools (`uv`, `poetry`,
  `pdm`) and lockfiles (`uv.lock`). Verify if locks are committed.
- **Pinning Strategy**: Check whether libraries use open lower bounds
  (`package>=1.0.0`) or restrictive upper bounds (`package>=1.0.0,<2.0.0`).

### Pillar 3: Linting, Formatting, & Static Analysis

Evaluate static verification engines, rule selections, and enforcement gates:

- **Linter & Formatter**: Inspect Ruff configuration (`ruff.toml` or
  `[tool.ruff]`), enabled rule prefixes, and per-file ignores.
- **Type Checking**: Identify the type checker (`pyrefly`, `mypy`, `pyright`),
  strictness preset, custom plugins, and stub packages.
- **Cognitive Complexity**: Check for complexity gates (`complexipy`,
  `flake8-cognitive-complexity`, or Ruff `C901`).
- **Architecture Boundaries**: Check for modular boundary checkers (`tach`,
  `import-linter`).
- **Linters for Non-Code Assets**: Check spell-checkers (`typos`), markdown
  linters (`rumdl`, `markdownlint`), and config validators.
- **Git Hooks**: Inspect `.pre-commit-config.yaml` or fast native runners
  (`prek`).

### Pillar 4: Task Runner & Developer Workflows

Review developer automation, command discoverability, and local ergonomics:

- **Task Runner**: Identify the task orchestrator (`poethepoet`, `just`, `nox`,
  `tox`, `make`).
- **Standard Tasks**: Look for consistent task naming (`lint`, `format`,
  `type-check`, `test`, `test-fast`, `coverage`, `fix`, `code-quality`).
- **Execution Engine**: Verify whether commands execute inside hermetic virtual
  environments (e.g. `uv run`).

### Pillar 5: Testing Architecture & Quality Assurance

Inspect test framework integration, plugins, and coverage requirements:

- **Framework & Plugins**: Review `pytest` configuration, test discovery
  patterns, and plugins (`pytest-cov`, `pytest-xdist`, `pytest-randomly`,
  `syrupy`, `hypothesis`).
- **Test Organization**: Examine directory layout (`tests/unit/`,
  `tests/integration/`, `tests/fixtures/`, `conftest.py`).
- **Coverage Configuration**: Inspect branch coverage settings, coverage
  fail-under thresholds, and exclusion patterns (`.coveragerc` or
  `pyproject.toml`).
- **Property & Snapshot Testing**: Identify use of property-based testing
  (`hypothesis`) and snapshot assertions (`syrupy`).

### Pillar 6: Documentation & Specification Engineering

Analyze technical documentation generation and asset pipelines:

- **Static Doc Generator**: Identify the engine (`zensical`, `mkdocs-material`,
  `sphinx`). Both `zensical` (`zensical.toml`) and `mkdocs` (`mkdocs.yml`,
  `docs/en/mkdocs.yml`, or multi-file `INHERIT` configs like `mkdocs-common.yml`)
  are first-class targets to learn from. Because `zensical` is built by the
  creators of *Material for MkDocs* and *mkdocstrings*, patterns discovered in
  mature `mkdocs.yml` setups translate directly into `zensical.toml`.
- **Strict Build Validation**: Check for `[project.validation]` rules in
  `zensical.toml` (`invalid_links`, `unresolved_references`, etc.) or
  `strict: true` in `mkdocs.yml`.
- **API Reference Generator**: Inspect docstring parsing tools (`mkdocstrings`,
  `griffe` static AST analysis, `griffe-typingdoc`, `griffe-inherited-docstrings`),
  docstring style (`numpy`, `google`, `auto`), signature cross-references
  (`signature_crossrefs = true`), class inheritance diagrams
  (`show_inheritance_diagram = true`), symbol backlinks (`backlinks = "tree"`),
  internal link hover previews (`zensical.extensions.preview`), and external
  Sphinx inventories (`objects.inv`).
- **AI / LLM Documentation Indexing**: Check for `llms.txt` / `llms-full.txt`
  files or automated generation via `mkdocs-llmstxt` (`llmstxt` plugin).
- **Executable & Tested Snippets**: Check for dynamic code execution
  (`markdown-exec`), external snippet inclusion (`pymdownx.snippets` with
  `check_paths = true`), isolated tested example directories (`docs_src/`), and
  automated doctest verification (`--doctest-modules`, `xdoctest`,
  `pytest-markdown-docs`).
- **Versioning & Redirects**: Check for multi-version deployment (`mike`) and
  URL redirect maps (`mkdocs-redirects` / `[project.plugins.redirects]`).
- **Vector Assets, Terminal Rendering, & Changelogs**: Check for Mermaid
  diagrams, Typst vector layouts (`.typ`), terminal session animations
  (`termynal`, `format_svg`), and fragment-based changelogs (`scriv` in
  `changelog.d/` or `towncrier` in `newsfragments/`).

### Pillar 7: CI/CD & Supply Chain Security

Examine automation pipelines, matrix tests, and publication security:

- **Matrix CI**: Check GitHub Actions workflows for Python versions (3.12, 3.13,
  3.14, 3.15, free-threading), operating systems (Ubuntu, macOS, Windows).
- **Fast Caching**: Review caching mechanisms (Astral `setup-uv`, cache keys).
- **Publication Security**: Verify PyPI Trusted Publishing (OIDC tokens),
  PEP 740 digital attestations, and provenance generation.
- **Automation**: Check automated release tools (`release-please`,
  `semantic-release`, `changesets`).

### Pillar 8: Governance, Security, & Open Source Health

Review project health, contributor onboarding, and community policies:

- **Issue & PR Templates**: Inspect `.github/ISSUE_TEMPLATE/` and
  `PULL_REQUEST_TEMPLATE.md`.
- **Security & Contributing**: Inspect `SECURITY.md`, `CONTRIBUTING.md`, and
  `CODE_OF_CONDUCT.md`.
- **Dependency Automation**: Inspect Renovate or Dependabot configurations.

### Pillar 9: Agent Skills & AI Development Workflows

Examine how the target repository equips AI agents and developers with custom skills,
instructions, guardrails, and operational tooling:

- **Agent Skills & Custom Capabilities**: Check for repository agent skills
  (`.agents/skills/`, `.agent/skills/`, `.cursor/skills/`, `.gemini/skills/`).
  Identify domain-specific workflows, benchmark harnesses, code generators, or
  diagnostic scripts packaged as skills.
- **Agent Instructions & Discovery**: Inspect `AGENTS.md`, `CLAUDE.md`,
  `.cursorrules`, `.cursor/rules/`, `.windsurfrules`, and
  `.github/copilot-instructions.md`. Evaluate instruction hierarchy, localized
  subfolder instructions, and discovery symlinks (e.g. `CLAUDE.md -> AGENTS.md`).
- **AI Governance & Contribution Policies**: Inspect AI usage policies
  (`AI_POLICY.md`), PR template disclosure checklists (`pull_request_template.md`),
  bot-gating rules, and verification mandates (e.g., local test verification,
  anti-slop policies).
- **Tooling Protocols & Extensions**: Check for Model Context Protocol (MCP)
  server definitions (`mcp.json`, `.cursor/mcp.json`), subagents, sidecars, and
  custom agent runners.
- **Knowledge Encapsulation**: Identify how maintainers encode domain idioms,
  architectural invariants, and anti-patterns into guidelines so both human
  contributors and AI coding assistants generate idiomatic, verified code.

### 9-Pillar Maturity Rubric & Scorecard Standards

Assess benchmark repositories against four objective maturity levels across each pillar
(Max Score: 36 points):

| Level | Classification | Definition & Criteria |
| :---: | :--- | :--- |
| **Level 1** | **Legacy / Minimal** | Legacy `setup.py` / unpinned requirements, flat layout, no type checking, no task runner, single-version or missing CI, no agent instructions. |
| **Level 2** | **Modern Baseline** | PEP 621 `[project]` metadata, basic linting (Flake8/Black/Ruff), standard pytest, basic GitHub Actions CI, basic README docs. |
| **Level 3** | **Advanced Engineering** | PEP 517 build backend (`hatchling`/`poetry-core`), strict typing (`mypy`/`pyright`), committed lockfiles (`uv.lock`/`poetry.lock`), matrix CI, rich docs (`mkdocs-material`/Sphinx), agent instructions (`AGENTS.md`/`CLAUDE.md`). |
| **Level 4** | **Zenith Gold Standard** | Native `uv_build` backend, PEP 735 `[dependency-groups]`, hermetic task orchestration (`poethepoet`), cognitive complexity gates (`complexipy`), architectural boundaries (`tach`), PyPI Trusted Publishing (OIDC) + PEP 740 build attestations, vector/TOML/strict docs (Zensical or advanced MkDocs Material + Typst), comprehensive agent skills (`.agents/skills/`), and explicit AI governance (`AI_POLICY.md`). |

---

## 2. Ingestion & Extraction Workflow

Follow this procedure when auditing an external repository or local project.

### Step 0: Check Candidate Queue & Audit History

Before inspecting a repository or package:

1. Review `.agents/skills/inspect-module-setup/candidates.log` to pick an accepted
   target from the prioritized queue.
2. Check `.agents/skills/inspect-module-setup/inspected.log` to verify historical audits
   and prevent duplicate analysis:

```bash
# View queued candidates awaiting inspection
cat .agents/skills/inspect-module-setup/candidates.log 2>/dev/null

# View list of previously inspected modules
cat .agents/skills/inspect-module-setup/inspected.log 2>/dev/null
```

### Step 1: Run Automated 9-Pillar Inspection Scanner

Execute the automated scanner on a local directory or remote GitHub repository.
The scanner evaluates all 9 pillars, calculates the maturity score, generates
the Gap Radar table, and extracts agent skills:

```bash
# Deep audit a local directory or remote GitHub repository (evaluates all 9 pillars & extracts learnings)
uv run python .agents/skills/inspect-module-setup/scripts/audit_repo.py <target_path_or_org/repo> [--output <report.md>] [--subpath <subdir>] [--refresh]

# Examples:
# uv run python .agents/skills/inspect-module-setup/scripts/audit_repo.py <org>/<repo>
# uv run python .agents/skills/inspect-module-setup/scripts/audit_repo.py .temp/inspect-<repo>
```

### Step 2: Harvest & Benchmark Agent Skills

Run dedicated skill harvesting to extract, inspect, and benchmark the target's AI
instructions, Cursor rules (`.mdc`), MCP servers, and skills against Zenith's
`.agents/skills/` library:

```bash
# Deep harvest agent skills, instructions, MCP declarations, and AI policies
uv run python .agents/skills/inspect-module-setup/scripts/harvest_skills.py <target_path_or_org/repo> [--refresh]
```

### Step 3: Deep-Dive Configuration Review

Inspect discovered nuances, custom flags, specialized skills, or unusual tool
configurations:

```bash
cd .temp/inspect-<repo>

# Packaging, dependencies, and tools
cat pyproject.toml

# Tool-specific configurations
ls -la ruff.toml .ruff.toml pyrefly.toml mypy.ini tach.toml \
  .pre-commit-config.yaml 2>/dev/null

# Agent skills, instructions, and AI policies
ls -la AGENTS.md CLAUDE.md AI_POLICY.md .cursorrules .windsurfrules \
  .github/copilot-instructions.md 2>/dev/null
ls -la .agents/skills/ .agent/skills/ .cursor/rules/ .cursor/skills/ 2>/dev/null

# Documentation configs (Zensical / MkDocs / Sphinx / llms.txt)
ls -la zensical.toml mkdocs*.yml mkdocs*.yaml llms.txt docs/ docs_src/ 2>/dev/null

# Task runner definitions
ls -la poe_tasks.toml Justfile Makefile noxfile.py tox.ini 2>/dev/null

# CI/CD pipelines
ls -la .github/workflows/
```

### Step 4: Transition Modules Between Candidates and Inspected

Once an audit or benchmark review is concluded, move the module from
`.agents/skills/inspect-module-setup/candidates.log` to
`.agents/skills/inspect-module-setup/inspected.log` (or re-queue modules back
into `candidates.log` when resetting or re-auditing):

```bash
# Move a completed module from candidates.log to inspected.log
uv run python .agents/skills/inspect-module-setup/scripts/transition_module.py <module_name>

# Move a specific module from inspected.log back to candidates.log
uv run python .agents/skills/inspect-module-setup/scripts/transition_module.py --requeue <module_name>

# Move all modules from inspected.log back to candidates.log
uv run python .agents/skills/inspect-module-setup/scripts/transition_module.py --requeue-all
```

### Step 5: Inspect & Prune Clone Cache

Manage local disk consumption of cached benchmark repositories under `.temp/`:

```bash
# Check cache status and sizes across all cached clones
uv run python .agents/skills/inspect-module-setup/scripts/prune_cache.py --status

# Enforce a maximum cache budget (e.g. 500 MB), pruning oldest clones first
uv run python .agents/skills/inspect-module-setup/scripts/prune_cache.py --max-size-mb 500

# Delete a specific target clone
uv run python .agents/skills/inspect-module-setup/scripts/prune_cache.py --target inspect-<repo>
```

---

## 3. Batch Inspection & Cross-Repository Synthesis Mode

When Zenith's setup is already mature and single-repository audits hit diminishing
returns, run **Batch Inspection Mode** across a cohort of $N$ candidates (typically
10–25 repositories). Auditing a cohort and synthesizing at the end separates
**convergent ecosystem standards** (patterns independently adopted across multiple
flagship projects) from noisy one-off repo quirks, while still capturing singular
high-leverage breakthroughs.

### Phase 1: Cohort Selection & Workspace Preparation

1. Read the top $N$ candidates from `.agents/skills/inspect-module-setup/candidates.log`
   and verify none appear in `inspected.log`.
2. Ensure `.temp/batch-inspection/` exists (archive or clear prior batch reports if
   starting a new batch):

   ```bash
   mkdir -p .temp/batch-inspection
   ```

### Phase 2: Sequential or Subagent-Parallel Deep Audits (`.temp/batch-inspection/<NN>-<slug>.md`)

For each candidate $i \in \{1 \dots N\}$ (either sequentially or partitioned across
parallel subagents in chunks of 2–3 repositories per subagent):

1. **Automated Baseline Scan**: Run `audit_repo.py` and write the initial report to
   `.temp/batch-inspection/<NN>-<slug>.md`:

   ```bash
   uv run python .agents/skills/inspect-module-setup/scripts/audit_repo.py <org>/<repo> \
     --output .temp/batch-inspection/<NN>-<slug>.md
   ```

2. **Mandatory Deep-Dive Manual Inspection**:
   Never rely solely on the automated scorecard. Manually inspect the cloned repository
   in `.temp/inspect-<repo>/`:
   - `pyproject.toml`, `uv.lock`, and build backend configuration.
   - Static analysis & task configs (`ruff.toml`, `pyrefly.toml`, `mypy.ini`,
     `tach.toml`, `.importlinter`, `poe_tasks.toml`, `Justfile`,
     `.pre-commit-config.yaml`).
   - Testing architecture (`pytest.ini`, `tests/conftest.py`, `.coveragerc`, custom
     pytest hooks, property/snapshot/concurrency test idioms).
   - Documentation pipeline (`zensical.toml`, `mkdocs.yml`, `llms.txt`, doc validation
     scripts).
   - CI/CD workflows (`.github/workflows/*.yml`, OIDC/provenance, matrix splits).
   - Agent skills & governance (`AGENTS.md`, `CLAUDE.md`, `AI_POLICY.md`,
     `.agents/skills/`, `.claude/skills/`, `.cursor/rules/`).

3. **Append Deep-Dive Findings & Concrete Proposals**:
   Append a structured **`## 4. Deep-Dive Findings & Proposals for Zenith`** section to
   `.temp/batch-inspection/<NN>-<slug>.md`. **Never stop at vague or high-level observations.**
   For every discovery, compare the finding directly against `{{cookiecutter.project_slug}}`
   and formulate a concrete, well-explained proposal containing:
   - **Exact Target File**: Target path in `{{cookiecutter.project_slug}}/` (e.g. `{{cookiecutter.project_slug}}/pyproject.toml`, `{{cookiecutter.project_slug}}/tach.toml`, `{{cookiecutter.project_slug}}/pytest.ini`, `{{cookiecutter.project_slug}}/ruff.toml`, etc.) and corresponding root assets.
   - **Concrete Code Diff / Drop-in Replacement**: Exact code snippets or before/after diffs ready for immediate execution.
   - **Well-Explained Architectural Rationale**: Detailed explanation of the mechanism, what edge cases, runtime crashes, or developer friction it prevents, and why Zenith benefits.
   - **Verification Plan**: Exact commands (`uv run pytest`, `uv run ruff check`) to validate the update.

4. **Transition & Cache Hygiene**: Once `.temp/batch-inspection/<NN>-<slug>.md` is
   complete, transition the module from `candidates.log` to `inspected.log` and prune
   cached clones to bound disk usage:

   ```bash
   uv run python .agents/skills/inspect-module-setup/scripts/transition_module.py <slug>
   uv run python .agents/skills/inspect-module-setup/scripts/prune_cache.py --max-size-mb 500
   ```

### Phase 3: Cross-Cohort Synthesis (`.temp/batch-inspection/00-SYNTHESIS.md`)

After all $N$ individual reports (`01-<slug>.md` through `<NN>-<slug>.md`) are written:

1. Read and cross-reference all `<NN>-<slug>.md` reports in `.temp/batch-inspection/`.
2. Deduplicate overlapping findings, filter out low-signal or domain-specific noise, and
   organize the highest-leverage proposals into
   `.temp/batch-inspection/00-SYNTHESIS.md`:
   - **Scorecard Summary Table**: All $N$ repositories with their 9-Pillar score and
     headline discovery.
   - **Prioritized Unified Proposals**:
     - **Tier 1 (P0)**: Packaging (`pyproject.toml`), CI/CD (`.github/workflows/`), &
       Supply-Chain Security
     - **Tier 2 (P1)**: Testing (`pytest.ini`, `.coveragerc`), Static Analysis
       (`ruff.toml`, `pyrefly.toml`, `tach.toml`), & Task Runner (`poe_tasks.toml`)
     - **Tier 3 (P2)**: Documentation (`zensical.toml`) & LLM Context (`llms.txt`)
     - **Tier 4 (P3)**: Agent Skills (`.agents/skills/*/SKILL.md`), Governance
       (`AGENTS.md`, `AI_POLICY.md`), & Inspector Script Improvements
   - **Explicit Rejections / Anti-Bloat Filter**: Patterns observed in the cohort that
     Zenith intentionally rejects (and why).
3. **Always Present Concrete, Well-Explained Proposals with Diff Blocks**:
   When presenting the synthesized findings to the user, never provide mere bullet-point
   summaries. For each proposed change, provide:
   - The comparison between `{{cookiecutter.project_slug}}` and the benchmark cohort.
   - The exact target file path in `{{cookiecutter.project_slug}}/`.
   - The drop-in code snippet or configuration diff.
   - A thorough, well-explained justification covering architectural invariants, runtime
     safety, and developer experience.
   - A verification plan.

---

## 4. Candidate Queue & Audit Persistence

- **Audit History Log** (`.agents/skills/inspect-module-setup/inspected.log`):
  Persistent record of completed repository audits across sessions to prevent duplicate
  analysis.
- **Candidate Queue** (`.agents/skills/inspect-module-setup/candidates.log`):
  Prioritized queue of validated benchmark candidates awaiting audit.

Always check `.agents/skills/inspect-module-setup/candidates.log` for upcoming benchmark
targets and verify `.agents/skills/inspect-module-setup/inspected.log` to prevent
duplicate effort.

---

## 5. Concrete Proposal Standard

Every improvement proposal generated from this skill (whether from a single-repository
audit or a batch cohort synthesis) **MUST** follow the standardized template defined in:
👉 [templates/proposal_template.md](./templates/proposal_template.md)

Key required sections include:

1. **Executive Summary & Architectural Rationale**: Detailed explanation of the mechanism, edge cases solved, and why Zenith benefits.
2. **Benchmark Source & Context**: Specific repositories, file paths, and discovered patterns.
3. **Gap Analysis**: Comparison matrix between target repositories and `{{cookiecutter.project_slug}}`.
4. **Concrete Code Diffs & Drop-in Replacements**: Exact before/after code diffs targeting specific files in `{{cookiecutter.project_slug}}/` or root assets.
5. **Verification Plan**: Exact commands (`pytest`, `ruff`, `pre-commit`) to validate changes.
