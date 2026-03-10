# Repository Guidelines

## Project Structure & Module Organization
- `src/supercodex/` holds the Python package and pytest plugin entrypoints.
- `tests/` contains Python integration/unit suites; markers map to features in `pyproject.toml`.
- `src/supercodex/commands/` holds command markdown sources that are converted into Codex skills by `supercodex install`.
- `plugins/` is kept for upstream reference content (not required for Codex usage).
- `docs/` provides reference packs; start with `docs/developer-guide` for workflow expectations.

## Build, Test, and Development Commands
- `uv venv && uv pip install -e ".[dev]"` installs the framework editable in a local venv.
- `uv run pytest` runs the test suite.
- `uv run supercodex doctor` checks CLI wiring and basic health.
- `make lint` and `make format` delegate to Ruff; run after significant edits.

## Coding Style & Naming Conventions
- Python: 4-space indentation, Black line length 88, Ruff `E,F,I,N,W`; prefer snake_case for modules/functions and PascalCase for classes.
- Keep pytest markers explicit (`@pytest.mark.unit`, etc.) and match file names `test_*.py`.
- Reserve docstrings or inline comments for non-obvious orchestration; let clear naming do the heavy lifting.

## Testing Guidelines
- Default to `uv run pytest`; add `uv run pytest -m unit` to scope runs during development.
- When changes touch CLI or plugin startup, extend integration coverage in `tests/integration/test_pytest_plugin.py`.
- Respect coverage focus on `src/supercodex` (`tool.coverage.run`).

## Commit & Pull Request Guidelines
- Follow Conventional Commits (`feat:`, `fix:`, `refactor:`) as seen in `git log`; keep present-tense summaries under ~72 chars.
- Group related file updates per commit to simplify bisects and release notes.
- Before opening a PR, run `make lint`, `make format`, and `make test`; include summaries of verification steps in the PR description.
- Reference linked issues (`Closes #123`) and, for agent workflow changes, add brief reproduction notes; screenshots only when docs change.
- Tag reviewers listed in `CODEOWNERS` when touching owned directories.
