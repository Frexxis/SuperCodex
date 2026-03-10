"""
SuperCodex CLI Main Entry Point

Provides command-line interface for SuperCodex operations.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

# Add src/ to path for direct execution from a source checkout.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from supercodex import __version__


@click.group()
@click.version_option(version=__version__, prog_name="SuperCodex")
def main() -> None:
    """SuperCodex - AI-enhanced development framework for Codex CLI."""


@main.command()
@click.option(
    "--target",
    default="~/.codex/skills",
    help="Installation directory (default: ~/.codex/skills)",
)
@click.option("--force", is_flag=True, help="Force reinstall if skills already exist")
@click.option(
    "--list",
    "list_only",
    is_flag=True,
    help="List available skills without installing",
)
def install(target: str, force: bool, list_only: bool) -> None:
    """
    Install SuperCodex skills for Codex CLI

    Converts command markdown files packaged with SuperCodex into Codex skills:
      ~/.codex/skills/scx-<command>/SKILL.md
    """
    from .install_skills import (
        install_skills,
        list_available_skills,
        list_installed_skills,
    )

    target_path = Path(target).expanduser()

    if list_only:
        available = list_available_skills()
        installed = set(list_installed_skills(target_path=target_path))

        click.echo("📋 Available Skills:")
        for skill in available:
            status = "✅ installed" if skill in installed else "⬜ not installed"
            click.echo(f"   {skill:24} {status}")
        click.echo(f"\nTotal: {len(available)} available, {len(installed)} installed")
        return

    click.echo(f"📦 Installing SuperCodex skills to {target_path}...\n")
    success, message = install_skills(target_path=target_path, force=force)
    click.echo(message)
    if not success:
        raise SystemExit(1)


@main.command()
@click.option(
    "--target",
    default="~/.codex/skills",
    help="Installation directory (default: ~/.codex/skills)",
)
def update(target: str) -> None:
    """Update SuperCodex skills to match the current package version."""
    from .install_skills import install_skills

    target_path = Path(target).expanduser()
    click.echo(f"🔄 Updating SuperCodex skills in {target_path}...\n")
    success, message = install_skills(target_path=target_path, force=True)
    click.echo(message)
    if not success:
        raise SystemExit(1)


@main.command()
@click.option("--servers", "-s", multiple=True, help="Specific MCP presets to apply")
@click.option("--list", "list_only", is_flag=True, help="List available MCP presets")
@click.option(
    "--config",
    "config_path",
    default="~/.codex/config.toml",
    help="Codex config path (default: ~/.codex/config.toml)",
)
@click.option("--dry-run", is_flag=True, help="Show changes without writing")
@click.option("--force", is_flag=True, help="Overwrite conflicting existing values")
@click.option("--no-backup", is_flag=True, help="Disable backup before writing")
def mcp(servers, list_only: bool, config_path: str, dry_run: bool, force: bool, no_backup: bool) -> None:
    """Manage MCP server presets in Codex `config.toml`."""
    from .mcp_config import ensure_mcp_servers, list_available_presets

    if list_only:
        click.echo("📋 Available MCP presets:")
        for preset in list_available_presets():
            click.echo(f"   - {preset.name:18} {preset.description}")
        return

    cfg = Path(config_path).expanduser()
    selected = list(servers) if servers else None
    success, message = ensure_mcp_servers(
        config_path=cfg,
        selected=selected,
        force=force,
        dry_run=dry_run,
        backup=not no_backup,
    )
    click.echo(message)
    if not success:
        raise SystemExit(1)


@main.command()
@click.option("--verbose", is_flag=True, help="Show detailed diagnostic information")
def doctor(verbose: bool) -> None:
    """Check SuperCodex installation health."""
    from .doctor import run_doctor

    click.echo("🔍 SuperCodex Doctor\n")
    results = run_doctor(verbose=verbose)

    for check in results["checks"]:
        status_symbol = "✅" if check["passed"] else "❌"
        click.echo(f"{status_symbol} {check['name']}")

        if verbose and check.get("details"):
            for detail in check["details"]:
                click.echo(f"    {detail}")

    click.echo()
    total = len(results["checks"])
    passed = sum(1 for check in results["checks"] if check["passed"])

    if passed == total:
        click.echo("✅ SuperCodex is healthy")
    else:
        click.echo(f"⚠️  {total - passed}/{total} checks failed")
        raise SystemExit(1)


@main.command()
def version() -> None:
    """Show SuperCodex version."""
    click.echo(f"SuperCodex version {__version__}")


if __name__ == "__main__":
    main()
