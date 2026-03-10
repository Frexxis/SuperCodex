"""
Custom Prompt Installation (Codex)

Installs Codex custom prompt files into `~/.codex/prompts` so that users can
invoke SuperCodex workflows via slash commands (e.g. `/prompts:scx-research`).

Custom prompts are a Codex feature that expands Markdown files into messages.
They are *explicit* (user-invoked) and live in Codex home, not in a repo.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .install_skills import (
    DEFAULT_SKILL_PREFIX,
    _get_commands_source,
    _split_frontmatter,
)

DEFAULT_TARGET = Path("~/.codex/prompts").expanduser()


def install_prompts(
    target_path: Path | None = None,
    force: bool = False,
    prefix: str = DEFAULT_SKILL_PREFIX,
) -> Tuple[bool, str]:
    """
    Install SuperCodex custom prompts (slash commands) for Codex.

    Creates:
      - scx.md (alias -> scx-sc prompt content)
      - scx-<command>.md for each packaged command
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

    # Alias: /scx -> use scx-sc skill (keeps muscle memory from SuperClaude `/sc`).
    alias_name = prefix.rstrip("-")
    alias_file = target_path / f"{alias_name}.md"
    if alias_file.exists() and not force:
        skipped.append(alias_name)
    else:
        try:
            alias_file.write_text(
                _render_alias_prompt(prefix=prefix, command_source=command_source),
                encoding="utf-8",
            )
            installed.append(alias_name)
        except Exception as exc:
            failed.append(f"{alias_name}: {exc}")

    for cmd_file in command_files:
        command_name = cmd_file.stem
        prompt_name = f"{prefix}{command_name}"
        prompt_file = target_path / f"{prompt_name}.md"

        if prompt_file.exists() and not force:
            skipped.append(prompt_name)
            continue

        try:
            raw = cmd_file.read_text(encoding="utf-8")
            frontmatter, body = _split_frontmatter(raw)
            description = frontmatter.get("description") or f"SuperCodex: {command_name}"

            rendered = _render_prompt(
                prompt_name=prompt_name,
                description=description,
                body=body,
            )
            prompt_file.write_text(rendered, encoding="utf-8")
            installed.append(prompt_name)
        except Exception as exc:
            failed.append(f"{prompt_name}: {exc}")

    lines: List[str] = []
    if installed:
        lines.append(f"✅ Installed {len(installed)} prompt(s):")
        for name in installed:
            lines.append(f"   - /prompts:{name}")

    if skipped:
        lines.append(
            f"\n⚠️  Skipped {len(skipped)} existing prompt(s) (use --force to reinstall):"
        )
        for name in skipped:
            lines.append(f"   - /prompts:{name}")

    if failed:
        lines.append(f"\n❌ Failed to install {len(failed)} prompt(s):")
        for item in failed:
            lines.append(f"   - {item}")

    if not installed and not skipped:
        return False, "No prompts were installed"

    lines.append(f"\n📁 Prompts directory: {target_path}")
    lines.append(
        "\n💡 Tip: Restart Codex to load new/updated prompts. Then type `/prompts:` and search for `scx`."
    )

    return len(failed) == 0, "\n".join(lines)


def list_available_prompts(prefix: str = DEFAULT_SKILL_PREFIX) -> List[str]:
    """Return sorted list of available prompt names."""
    command_source = _get_commands_source()
    if not command_source.exists():
        return []

    prompts = {prefix.rstrip("-")}  # /scx alias
    for file in command_source.glob("*.md"):
        if file.stem == "README":
            continue
        prompts.add(f"{prefix}{file.stem}")
    return sorted(prompts)


def list_installed_prompts(
    target_path: Path | None = None, prefix: str = DEFAULT_SKILL_PREFIX
) -> List[str]:
    """Return sorted list of installed prompt names in the target directory."""
    if target_path is None:
        target_path = DEFAULT_TARGET

    if not target_path.exists():
        return []

    installed: List[str] = []
    for file in target_path.glob("*.md"):
        if file.stem == prefix.rstrip("-") or file.stem.startswith(prefix):
            installed.append(file.stem)
    return sorted(installed)


def _render_alias_prompt(*, prefix: str, command_source: Path) -> str:
    """
    Render the `/prompts:scx` alias prompt.

    Prefers using the packaged `sc.md` command body so the alias is useful even
    when skills are not explicitly invoked.
    """
    sc_file = command_source / "sc.md"
    if sc_file.exists():
        raw = sc_file.read_text(encoding="utf-8")
        _frontmatter, body = _split_frontmatter(raw)
        return _render_prompt(
            prompt_name=prefix.rstrip("-"),
            description="SuperCodex: entrypoint (list and usage)",
            body=body,
        )

    # Fallback: minimal help text.
    return (
        "---\n"
        'description: "SuperCodex: entrypoint (list and usage)"\n'
        'argument-hint: [INPUT="<text>"]\n'
        "---\n\n"
        "SuperCodex prompts are invoked as `/prompts:scx-<command>`.\n\n"
        "Examples:\n"
        "- `/prompts:scx-research <query>`\n"
        "- `/prompts:scx-implement <task>`\n"
    )


def _render_prompt(*, prompt_name: str, description: str, body: str) -> str:
    # Use `$ARGUMENTS` so users can call `/prompts:scx-research <query>`.
    safe_description = description.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "---\n"
        f'description: "{safe_description}"\n'
        'argument-hint: [INPUT="<text>"]\n'
        "---\n\n"
        "User input:\n"
        "$ARGUMENTS\n\n"
        + body
    )
