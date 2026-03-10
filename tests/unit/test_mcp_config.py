"""
Unit tests for Codex MCP config merge

Tests that MCP presets are applied safely and idempotently.
"""

from pathlib import Path

import tomlkit

from supercodex.cli.mcp_config import ensure_mcp_servers


def test_mcp_dry_run_does_not_write(tmp_path):
    cfg = tmp_path / "config.toml"

    success, message = ensure_mcp_servers(config_path=cfg, dry_run=True)
    assert success is True
    assert "DRY RUN" in message
    assert not cfg.exists()


def test_mcp_writes_new_config(tmp_path):
    cfg = tmp_path / "config.toml"

    success, message = ensure_mcp_servers(config_path=cfg, dry_run=False)
    assert success is True
    assert "UPDATED" in message
    assert cfg.exists()

    doc = tomlkit.parse(cfg.read_text(encoding="utf-8"))
    assert "mcp_servers" in doc
    assert "playwright" in doc["mcp_servers"]


def test_mcp_is_idempotent(tmp_path):
    cfg = tmp_path / "config.toml"

    success1, _ = ensure_mcp_servers(config_path=cfg, dry_run=False)
    assert success1 is True

    success2, message2 = ensure_mcp_servers(config_path=cfg, dry_run=False)
    assert success2 is True
    assert "no-op" in message2.lower()


def test_mcp_creates_backup_when_overwriting(tmp_path):
    cfg = tmp_path / "config.toml"

    # First write creates the file.
    ensure_mcp_servers(config_path=cfg, dry_run=False)
    assert cfg.exists()

    # Second write with backup enabled should create a timestamped backup.
    ensure_mcp_servers(config_path=cfg, dry_run=False, backup=True)

    backups = list(Path(tmp_path).glob("config.toml.bak-*"))
    assert len(backups) >= 1

