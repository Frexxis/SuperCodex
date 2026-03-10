---
name: sc
description: SuperCodex skill index - lists available scx-* skills and how to install them
---

# SuperCodex Skill Index

🚀 **SuperCodex Framework** - Codex CLI skill pack

## Usage

SuperCodex installs skills under the `scx-` prefix:

```
scx-<skill>
```

## Install / Update

```bash
supercodex install          # Install skills
supercodex install --list   # List available/installed
supercodex update           # Force reinstall all skills
```

## Available Skills (Examples)

| Skill | Purpose |
|------|---------|
| `scx-research` | Deep web research workflow |
| `scx-index-repo` | Repository indexing workflow |
| `scx-implement` | Implementation workflow |
| `scx-test` | Testing workflow |
| `scx-pm` | Project management workflow |
| `scx-help` | Help and usage |

## Examples

### Research
```
Use `scx-research` to research a topic with sources.
```

### Index Repository
```
Use `scx-index-repo` to generate/update `PROJECT_INDEX.md`.
```

## Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `supercodex install` | Install skills | `supercodex install` |
| `supercodex install --list` | List skills | `supercodex install --list` |
| `supercodex mcp --dry-run` | Preview MCP changes | `supercodex mcp --dry-run` |
| `supercodex doctor` | Health check | `supercodex doctor` |

## Features

- **Parallel Execution**: Research runs multiple searches in parallel
- **Evidence-Based**: All findings backed by sources
- **Context-Aware**: Uses repository context when available
- **Token Efficient**: Optimized for minimal token usage

## MCP Presets (Optional)

```bash
supercodex mcp --list
supercodex mcp --dry-run
supercodex mcp
```

💡 Tip: Use `supercodex version` to see the installed package version.
