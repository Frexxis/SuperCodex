"""
Skill Installation (Codex)

Converts SuperClaude-style command markdown files into Codex `SKILL.md` folders.

Target layout (default):
  ~/.codex/skills/scx-<command>/SKILL.md
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_SKILL_PREFIX = "scx-"
DEFAULT_TARGET = Path("~/.codex/skills").expanduser()


def install_skills(
    target_path: Path | None = None,
    force: bool = False,
    prefix: str = DEFAULT_SKILL_PREFIX,
) -> Tuple[bool, str]:
    """
    Install all available skills into the target directory.

    Args:
        target_path: Target installation directory (default: ~/.codex/skills)
        force: Overwrite SKILL.md if already installed
        prefix: Skill name prefix (default: scx-)

    Returns:
        (success, message)
    """
    if target_path is None:
        target_path = DEFAULT_TARGET

    command_source = _get_commands_source()
    if not command_source.exists():
        return False, f"Command source directory not found: {command_source}"

    target_path.mkdir(parents=True, exist_ok=True)

    command_files = sorted(
        p for p in command_source.glob("*.md") if p.stem != "README"
    )
    if not command_files:
        return False, f"No command markdown files found in {command_source}"

    installed: List[str] = []
    skipped: List[str] = []
    failed: List[str] = []

    for cmd_file in command_files:
        command_name = cmd_file.stem
        skill_name = f"{prefix}{command_name}"
        skill_dir = target_path / skill_name
        skill_file = skill_dir / "SKILL.md"

        if skill_file.exists() and not force:
            skipped.append(skill_name)
            continue

        try:
            skill_dir.mkdir(parents=True, exist_ok=True)

            raw = cmd_file.read_text(encoding="utf-8")
            frontmatter, body = _split_frontmatter(raw)
            description = frontmatter.get("description") or f"Codex skill: {command_name}"

            rendered = _render_skill_markdown(
                skill_name=skill_name,
                description=description,
                source_name=command_name,
                body=body,
            )
            skill_file.write_text(rendered, encoding="utf-8")
            installed.append(skill_name)
        except Exception as exc:
            failed.append(f"{skill_name}: {exc}")

    msg_lines: List[str] = []
    if installed:
        msg_lines.append(f"✅ Installed {len(installed)} skills:")
        for name in installed:
            msg_lines.append(f"   - {name}")

    if skipped:
        msg_lines.append(
            f"\n⚠️  Skipped {len(skipped)} existing skills (use --force to reinstall):"
        )
        for name in skipped:
            msg_lines.append(f"   - {name}")

    if failed:
        msg_lines.append(f"\n❌ Failed to install {len(failed)} skills:")
        for item in failed:
            msg_lines.append(f"   - {item}")

    if not installed and not skipped:
        return False, "No skills were installed"

    msg_lines.append(f"\n📁 Installation directory: {target_path}")
    msg_lines.append("\n💡 Tip: Restart Codex CLI if new skills don't appear immediately")

    return len(failed) == 0, "\n".join(msg_lines)


def list_available_skills(prefix: str = DEFAULT_SKILL_PREFIX) -> List[str]:
    """Return sorted list of available skills derived from command markdown files."""
    command_source = _get_commands_source()
    if not command_source.exists():
        return []

    skills: List[str] = []
    for file in command_source.glob("*.md"):
        if file.stem == "README":
            continue
        skills.append(f"{prefix}{file.stem}")
    return sorted(skills)


def list_installed_skills(
    target_path: Path | None = None, prefix: str = DEFAULT_SKILL_PREFIX
) -> List[str]:
    """Return sorted list of installed skills in the target directory."""
    if target_path is None:
        target_path = DEFAULT_TARGET

    if not target_path.exists():
        return []

    installed: List[str] = []
    for item in target_path.iterdir():
        if not item.is_dir():
            continue
        if prefix and not item.name.startswith(prefix):
            continue
        if (item / "SKILL.md").exists():
            installed.append(item.name)
    return sorted(installed)


def _get_commands_source() -> Path:
    """
    Return the directory containing command markdown files packaged with SuperCodex.

    In an installed package this resolves to:
      site-packages/supercodex/commands/
    In a source checkout it resolves to:
      src/supercodex/commands/
    """
    package_root = Path(__file__).resolve().parent.parent
    return package_root / "commands"


_FRONTMATTER_KV_RE = re.compile(r"^([A-Za-z0-9_-]+):\\s*(.*)$")


def _split_frontmatter(markdown: str) -> Tuple[Dict[str, str], str]:
    """
    Split a markdown file into (frontmatter, body).

    Frontmatter is a simple YAML subset delimited by leading `---` lines.
    Only top-level `key: value` pairs are extracted (we only need name/description).
    """
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return {}, markdown

    front_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")

    front: Dict[str, str] = {}
    for raw in front_lines:
        m = _FRONTMATTER_KV_RE.match(raw.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        # Strip surrounding quotes for simple scalar values.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        front[key] = value

    return front, body


def _render_skill_markdown(
    *,
    skill_name: str,
    description: str,
    source_name: str,
    body: str,
) -> str:
    frontmatter = (
        "---\n"
        f'name: "{skill_name}"\n'
        f'description: "{description}"\n'
        "---\n\n"
    )

    note = (
        f"This Codex skill was generated from SuperClaude's `{source_name}` command.\n"
        "Ask Codex to follow the workflow below.\n\n"
    )

    return frontmatter + note + body

