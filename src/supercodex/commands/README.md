# SuperCodex Command Sources

This directory contains markdown command sources that are converted into Codex skills when users run `supercodex install`.

Target layout:
- `~/.codex/skills/scx-<command>/SKILL.md`

## Available Commands

- **agent.md** - Specialized AI agents
- **index-repo.md** - Repository indexing for context optimization
- **recommend.md** - Command recommendations
- **research.md** - Deep web research with parallel search
- **sc.md** - Show all available commands

## Important

These markdown files are derived from SuperClaude's command pack and kept here for package distribution.

When updating commands:
1. Edit files in `src/supercodex/commands/`
2. Run `supercodex update` to regenerate installed skills
