# SuperCodex Framework

SuperCodex is a SuperClaude-derived framework that installs a curated set of workflow “skills” into Codex CLI.

## What You Get

- `supercodex install` installs skills under `~/.codex/skills/` (default prefix: `scx-`)
- `supercodex update` force-reinstalls all skills (useful after pulling changes)
- `supercodex mcp` safely merges MCP server presets into `~/.codex/config.toml` (backup + `--dry-run`)
- `supercodex doctor` checks package/config/skill health

## Install (From Source)

```bash
cd SuperCodex_Framework
./install.sh
```

Manual install:

```bash
cd SuperCodex_Framework
uv venv
uv pip install -e ".[dev]"
supercodex install
```

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
cd SuperCodex_Framework
uv run pytest
```

## Credits

Derived from the SuperClaude Framework (command pack + PM-agent testing patterns).
