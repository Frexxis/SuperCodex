"""
Codex MCP Config Manager

Manages `[mcp_servers.*]` entries in `~/.codex/config.toml` in an idempotent,
format-preserving way (via tomlkit).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import tomlkit

DEFAULT_CODEX_CONFIG = Path("~/.codex/config.toml").expanduser()


@dataclass(frozen=True)
class McpPreset:
    name: str
    description: str
    config: Dict[str, Any]


PRESETS: Dict[str, McpPreset] = {
    "playwright": McpPreset(
        name="playwright",
        description="Playwright MCP server (browser automation)",
        config={"command": "npx", "args": ["@playwright/mcp@latest"]},
    ),
    "firecrawl-mcp": McpPreset(
        name="firecrawl-mcp",
        description="Firecrawl MCP server (web search/scrape)",
        config={"command": "npx", "args": ["-y", "firecrawl-mcp"]},
    ),
    "context7-mcp": McpPreset(
        name="context7-mcp",
        description="Context7 MCP server (official library docs)",
        config={"url": "https://server.smithery.ai/upstash/context7-mcp/mcp"},
    ),
    "sequential-thinking": McpPreset(
        name="sequential-thinking",
        description="Sequential thinking MCP server",
        config={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        },
    ),
}


@dataclass(frozen=True)
class Change:
    kind: str  # added | updated | noop | conflict
    key_path: str
    message: str


def list_available_presets() -> List[McpPreset]:
    return [PRESETS[k] for k in sorted(PRESETS.keys())]


def ensure_mcp_servers(
    *,
    config_path: Path = DEFAULT_CODEX_CONFIG,
    selected: Optional[Iterable[str]] = None,
    force: bool = False,
    dry_run: bool = False,
    backup: bool = True,
) -> Tuple[bool, str]:
    """
    Ensure MCP server presets exist in a Codex config file.

    Args:
        config_path: Path to `config.toml`
        selected: Iterable of preset names; if None, uses recommended defaults
        force: Overwrite differing existing values
        dry_run: Do not write; only report changes
        backup: Create timestamped backup before writing

    Returns:
        (success, message)
    """
    requested = list(selected) if selected is not None else ["playwright", "firecrawl-mcp", "context7-mcp"]

    unknown = [name for name in requested if name not in PRESETS]
    if unknown:
        return False, f"Unknown MCP preset(s): {', '.join(unknown)}"

    doc, exists = _load_toml(config_path)
    changes: List[Change] = []

    mcp_servers = doc.get("mcp_servers")
    if mcp_servers is None or not _is_table(mcp_servers):
        doc["mcp_servers"] = tomlkit.table()
        changes.append(Change("added", "mcp_servers", "Created [mcp_servers] table"))
        mcp_servers = doc["mcp_servers"]

    for name in requested:
        preset = PRESETS[name]
        server_table = mcp_servers.get(name)
        if server_table is None or not _is_table(server_table):
            mcp_servers[name] = tomlkit.table()
            changes.append(Change("added", f"mcp_servers.{name}", "Created server table"))
            server_table = mcp_servers[name]

        for key, value in preset.config.items():
            key_path = f"mcp_servers.{name}.{key}"
            if key not in server_table:
                server_table[key] = value
                changes.append(Change("added", key_path, f"Set to {value!r}"))
                continue

            existing = server_table[key]
            if _toml_value_equal(existing, value):
                changes.append(Change("noop", key_path, "Already set"))
                continue

            if force:
                server_table[key] = value
                changes.append(Change("updated", key_path, f"Overwrote with {value!r}"))
            else:
                changes.append(
                    Change(
                        "conflict",
                        key_path,
                        "Exists with different value (use --force to overwrite)",
                    )
                )

    if dry_run:
        return True, _format_change_report(
            changes=changes, wrote=False, config_path=config_path, existed=exists
        )

    try:
        _write_toml(doc, config_path, backup=backup, existed=exists)
    except Exception as exc:
        return False, f"Failed to write {config_path}: {exc}"

    return True, _format_change_report(
        changes=changes, wrote=True, config_path=config_path, existed=exists
    )


def _load_toml(path: Path) -> Tuple[tomlkit.TOMLDocument, bool]:
    if not path.exists():
        return tomlkit.document(), False
    raw = path.read_text(encoding="utf-8")
    return tomlkit.parse(raw), True


def _write_toml(doc: tomlkit.TOMLDocument, path: Path, *, backup: bool, existed: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if existed and backup and path.exists():
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = path.with_name(f"{path.name}.bak-{ts}")
        backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(tomlkit.dumps(doc), encoding="utf-8")


def _is_table(value: Any) -> bool:
    return isinstance(value, (tomlkit.items.Table, tomlkit.items.InlineTable))


def _toml_value_equal(existing: Any, desired: Any) -> bool:
    # tomlkit wraps lists/strings into its own types; normalize to Python primitives.
    try:
        if isinstance(existing, tomlkit.items.Array) and isinstance(desired, list):
            return list(existing) == desired
    except Exception:
        pass
    return existing == desired


def _format_change_report(*, wrote: bool, config_path: Path, existed: bool, changes: List[Change]) -> str:
    counts = {
        "added": sum(1 for c in changes if c.kind == "added"),
        "updated": sum(1 for c in changes if c.kind == "updated"),
        "noop": sum(1 for c in changes if c.kind == "noop"),
        "conflict": sum(1 for c in changes if c.kind == "conflict"),
    }

    lines: List[str] = []
    header = "DRY RUN" if not wrote else "UPDATED"
    lines.append(f"🔧 MCP config {header}: {config_path}")
    lines.append(f"   File existed: {'yes' if existed else 'no'}")
    lines.append(
        "   Changes: "
        f"{counts['added']} added, {counts['updated']} updated, "
        f"{counts['conflict']} conflicts, {counts['noop']} no-op"
    )

    # Show non-noop changes first.
    for kind in ("added", "updated", "conflict"):
        for c in changes:
            if c.kind != kind:
                continue
            prefix = {"added": "✅", "updated": "♻️", "conflict": "⚠️"}[kind]
            lines.append(f"   {prefix} {c.key_path}: {c.message}")

    if counts["conflict"] > 0:
        lines.append("\n💡 Tip: Re-run with --force to overwrite conflicting values")

    return "\n".join(lines)
