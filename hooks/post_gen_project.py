import os
import re
import shutil
import subprocess

PROJECT_DIR = os.path.realpath(os.path.curdir)

CONFIG_FILES_WITH_HEADERS = [
    "pyproject.toml",
    "poe_tasks.toml",
    "ruff.toml",
    "pyrefly.toml",
    "complexipy.toml",
    "zensical.toml",
    "rumdl.toml",
    "tach.toml",
    ".coveragerc",
    "pytest.ini",
    ".taplo.toml",
    "typos.toml",
    ".pre-commit-config.yaml",
    ".prettierrc.yaml",
    ".editorconfig",
    ".zizmor.yml",
    os.path.join(".codex", "config.toml"),
    ".aider.conf.yml",
    "cosmic-ray.toml",
]


def remove_file(*filepath_parts: str) -> None:
    path = os.path.join(PROJECT_DIR, *filepath_parts)
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)


def remove_dir(*dirpath_parts: str) -> None:
    path = os.path.join(PROJECT_DIR, *dirpath_parts)
    if os.path.isdir(path):
        shutil.rmtree(path)


def strip_config_headers() -> None:
    """Strip explanatory template comments from generated configuration files."""
    pattern = re.compile(r"^# =+[^\n]*\n(?:#[^\n]*\n)*# =+[^\n]*\n+")
    for filename in CONFIG_FILES_WITH_HEADERS:
        filepath = os.path.join(PROJECT_DIR, filename)
        if not os.path.isfile(filepath):
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = pattern.sub("", content)
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)


def to_bool(val: object) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "yes", "1", "t", "y", "on")


def setup_agent_instructions() -> None:
    """Ensure agent instruction symlinks and configuration directories exist for all AI tools."""
    agents_path = os.path.join(PROJECT_DIR, "AGENTS.md")

    # Link standard instruction aliases to AGENTS.md
    for alias_name in ("CLAUDE.md", ".cursorrules", ".windsurfrules"):
        alias_path = os.path.join(PROJECT_DIR, alias_name)
        if os.path.isfile(agents_path) and not os.path.lexists(alias_path):
            try:
                os.symlink("AGENTS.md", alias_path)
            except (OSError, NotImplementedError):
                # Fallback for platforms or environments without symlink privileges
                shutil.copyfile(agents_path, alias_path)

    # Establish modern Cursor rules directory
    cursor_rules_dir = os.path.join(PROJECT_DIR, ".cursor", "rules")
    os.makedirs(cursor_rules_dir, exist_ok=True)
    cursor_rule_file = os.path.join(cursor_rules_dir, "zenith.mdc")
    if not os.path.isfile(cursor_rule_file):
        with open(cursor_rule_file, "w", encoding="utf-8") as f:
            f.write(
                "---\n"
                "description: Authoritative project conventions, typing standards, and workflows\n"
                'globs: ["*"]\n'
                "alwaysApply: true\n"
                "---\n\n"
                "# Project Guidelines\n\n"
                "Consult [AGENTS.md](../../AGENTS.md) for authoritative operational guidelines, architectural conventions, and development workflows.\n"
            )

    gemini_dir = os.path.join(PROJECT_DIR, ".gemini")
    os.makedirs(gemini_dir, exist_ok=True)
    gemini_settings = os.path.join(gemini_dir, "settings.json")
    if not os.path.isfile(gemini_settings):
        with open(gemini_settings, "w", encoding="utf-8") as f:
            f.write('{\n    "contextFileName": "AGENTS.md"\n}\n')

    claude_dir = os.path.join(PROJECT_DIR, ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    claude_settings = os.path.join(claude_dir, "settings.json")
    if not os.path.isfile(claude_settings):
        with open(claude_settings, "w", encoding="utf-8") as f:
            f.write(
                "{\n"
                '    "permissions": {\n'
                '        "allow": [\n'
                '            "Bash(uv run poe:*)",\n'
                '            "Bash(uv run pytest:*)",\n'
                '            "Bash(uv run ruff:*)",\n'
                '            "Bash(uv run pyrefly:*)",\n'
                '            "Bash(uv run complexipy:*)",\n'
                '            "Bash(uv run tach:*)",\n'
                '            "Bash(uv run rumdl:*)",\n'
                '            "Bash(uv run typos:*)",\n'
                '            "Bash(uv run taplo:*)",\n'
                '            "Bash(uv run zizmor:*)",\n'
                '            "Bash(uv run pre-commit:*)"\n'
                "        ],\n"
                '        "deny": [\n'
                '            "Bash(rm -rf /*)",\n'
                '            "Bash(git push --force:*)"\n'
                "        ]\n"
                "    }\n"
                "}\n"
            )

    codex_dir = os.path.join(PROJECT_DIR, ".codex")
    os.makedirs(codex_dir, exist_ok=True)
    codex_config = os.path.join(codex_dir, "config.toml")
    if not os.path.isfile(codex_config):
        with open(codex_config, "w", encoding="utf-8") as f:
            f.write(
                'approval_policy                = "on-request"\n'
                'project_doc_fallback_filenames = [ "AGENTS.md", "CLAUDE.md" ]\n'
                'sandbox_mode                   = "workspace-write"\n'
            )


def main() -> None:
    include_cli = to_bool("{{ cookiecutter.include_cli }}")
    include_ci_testing = to_bool("{{ cookiecutter.include_ci_testing }}")
    include_ci_publishing = to_bool("{{ cookiecutter.include_ci_publishing }}")
    license_type = "{{ cookiecutter.license }}"
    package_name = "{{ cookiecutter.package_name }}"

    # Strip template educational header comments from generated project configs
    strip_config_headers()

    if not include_cli:
        remove_file("src", package_name, "cli.py")
        remove_file("src", package_name, "_lazy.py")
        remove_file("src", package_name, "__main__.py")
        remove_file("tests", "test_cli.py")
        remove_file("docs", "javascripts", "termynal.js")
        remove_file("docs", "stylesheets", "termynal.css")
        remove_dir("docs", "stylesheets")

    if not include_ci_testing:
        remove_file(".github", "workflows", "python_tests.yaml")
        remove_file(".github", "workflows", "test_redistribute.yaml")
        remove_file(".github", "workflows", "guard-dependencies.yaml")
        remove_file(".github", "workflows", "dependabot-automerge.yaml")
        remove_file(".github", "codecov.yml")

    if not include_ci_publishing:
        remove_file(".github", "workflows", "publish.yaml")
        remove_file(".github", "workflows", "docs.yaml")

    if not include_ci_testing and not include_ci_publishing:
        remove_dir(".github")
        remove_file(".zizmor.yml")
        remove_dir(".agents", "skills", "tool-zizmor")

    if license_type.lower() == "none":
        remove_file("LICENSE")

    setup_agent_instructions()
    format_toml_files()


def format_toml_files() -> None:
    """Format generated TOML files with Taplo if available in PATH."""
    taplo_bin = shutil.which("taplo")
    if taplo_bin:
        try:
            subprocess.run(
                [taplo_bin, "format"],
                cwd=PROJECT_DIR,
                check=False,
                capture_output=True,
            )
        except (OSError, subprocess.SubprocessError):
            pass


if __name__ == "__main__":
    main()
