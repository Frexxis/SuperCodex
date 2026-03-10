"""
SuperCodex Doctor Command

Health check for SuperCodex installation and Codex CLI integration points.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def run_doctor(verbose: bool = False) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    checks.append(_check_importable())
    checks.append(_check_command_sources())
    checks.append(_check_skills_installed())
    checks.append(_check_prompts_installed())
    checks.append(_check_codex_config())

    return {"checks": checks, "passed": all(c["passed"] for c in checks)}


def _check_importable() -> Dict[str, Any]:
    try:
        import supercodex

        return {
            "name": "Package import",
            "passed": True,
            "details": [f"SuperCodex {supercodex.__version__} import OK"],
        }
    except Exception as exc:
        return {
            "name": "Package import",
            "passed": False,
            "details": [f"Could not import supercodex: {exc}"],
        }


def _check_command_sources() -> Dict[str, Any]:
    # Source of truth is packaged commands in src/supercodex/commands.
    try:
        from .install_skills import _get_commands_source

        commands_dir = _get_commands_source()
        if not commands_dir.exists():
            return {
                "name": "Command sources",
                "passed": False,
                "details": [f"Missing command directory: {commands_dir}"],
            }

        files = [p for p in commands_dir.glob("*.md") if p.stem != "README"]
        if not files:
            return {
                "name": "Command sources",
                "passed": False,
                "details": [f"No command markdown files found in {commands_dir}"],
            }

        return {
            "name": "Command sources",
            "passed": True,
            "details": [f"Found {len(files)} command markdown files"],
        }
    except Exception as exc:
        return {
            "name": "Command sources",
            "passed": False,
            "details": [f"Failed to inspect command sources: {exc}"],
        }


def _check_skills_installed() -> Dict[str, Any]:
    skills_dir = Path("~/.codex/skills").expanduser()
    if not skills_dir.exists():
        return {
            "name": "Skills installed",
            "passed": True,  # Optional
            "details": ["No ~/.codex/skills directory (run: supercodex install)"],
        }

    skills = []
    for item in skills_dir.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists() and item.name.startswith("scx-"):
            skills.append(item.name)

    if skills:
        details = [f"{len(skills)} skill(s) installed under {skills_dir}"]
        if len(skills) <= 10:
            details.append(", ".join(sorted(skills)))
        return {"name": "Skills installed", "passed": True, "details": details}

    return {
        "name": "Skills installed",
        "passed": True,  # Optional
        "details": [f"No scx-* skills found in {skills_dir} (run: supercodex install)"],
    }


def _check_codex_config() -> Dict[str, Any]:
    config_path = Path("~/.codex/config.toml").expanduser()
    if not config_path.exists():
        return {
            "name": "Codex config",
            "passed": True,  # Optional
            "details": ["No ~/.codex/config.toml (run: supercodex mcp)"],
        }

    try:
        # Only do a light check to avoid being brittle.
        raw = config_path.read_text(encoding="utf-8")
        has_mcp = "[mcp_servers" in raw

        details = [f"Config file present: {config_path}"]
        details.append("mcp_servers configured" if has_mcp else "mcp_servers not configured")
        return {"name": "Codex config", "passed": True, "details": details}
    except Exception as exc:
        return {
            "name": "Codex config",
            "passed": False,
            "details": [f"Could not read config: {exc}"],
        }


def _check_prompts_installed() -> Dict[str, Any]:
    prompts_dir = Path("~/.codex/prompts").expanduser()
    if not prompts_dir.exists():
        return {
            "name": "Slash prompts installed",
            "passed": True,  # Optional
            "details": ["No ~/.codex/prompts directory (run: supercodex prompts)"],
        }

    prompt_files = sorted(p.name for p in prompts_dir.glob("scx*.md"))
    if prompt_files:
        details = [f"Found {len(prompt_files)} scx* prompt(s) under {prompts_dir}"]
        if len(prompt_files) <= 10:
            details.append(", ".join(prompt_files))
        return {"name": "Slash prompts installed", "passed": True, "details": details}

    return {
        "name": "Slash prompts installed",
        "passed": True,  # Optional
        "details": [f"No scx* prompts found in {prompts_dir} (run: supercodex prompts)"],
    }
