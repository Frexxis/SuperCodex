# SuperCodex Framework

SuperCodex is a SuperClaude-derived framework that installs a curated set of workflow “skills” into Codex CLI.

## What You Get

- `supercodex install` installs skills under `~/.codex/skills/` (default prefix: `scx-`)
- `supercodex install` also installs Codex custom prompts (slash shortcuts) under `~/.codex/prompts/`
- `supercodex update` force-reinstalls all skills (useful after pulling changes)
- `supercodex mcp` safely merges MCP server presets into `~/.codex/config.toml` (backup + `--dry-run`)
- `supercodex doctor` checks package/config/skill health

## Install (From Source)

```bash
git clone https://github.com/Frexxis/SuperCodex.git
cd SuperCodex
./install.sh
```

Manual install:

```bash
cd SuperCodex
uv venv
uv pip install -e ".[dev]"
supercodex install
```

## Install (GitHub)

```bash
# Recommended: isolated install
pipx install git+https://github.com/Frexxis/SuperCodex.git

# Install/update skills into Codex
supercodex install
```

## Slash Commands (Codex)

After `supercodex install`, restart Codex and use:

- `/prompts:scx` (menu / index)
- `/prompts:scx-research <query>`
- `/prompts:scx-implement <task>`

These are Codex **custom prompts** that expand into messages that trigger the matching `scx-*` skill.

## MCP Presets (Optional)

```bash
# See what would change
supercodex mcp --dry-run

# Apply recommended defaults
supercodex mcp

# Or apply specific presets
supercodex mcp --servers playwright --servers context7-mcp
```

Notes:
- Writes to `~/.codex/config.toml`
- Creates a timestamped backup by default (disable with `--no-backup`)
- Does not overwrite conflicting values unless `--force` is passed

## Dev

```bash
cd SuperCodex
uv run pytest
```

## Credits

Derived from the SuperClaude Framework (command pack + PM-agent testing patterns).
