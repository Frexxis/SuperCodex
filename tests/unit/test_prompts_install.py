"""
Unit tests for custom prompt (slash command) installation.
"""

from supercodex.cli.install_prompts import (
    install_prompts,
    list_available_prompts,
    list_installed_prompts,
)


class TestInstallPrompts:
    def test_list_available_prompts(self):
        prompts = list_available_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) > 0
        assert "scx" in prompts
        assert "scx-research" in prompts

    def test_install_prompts_to_temp_dir(self, tmp_path):
        success, message = install_prompts(target_path=tmp_path, force=False)

        assert success is True
        assert "Installed" in message
        assert (tmp_path / "scx.md").exists()
        assert (tmp_path / "scx-research.md").exists()

    def test_install_prompts_skip_existing(self, tmp_path):
        success1, _ = install_prompts(target_path=tmp_path, force=False)
        assert success1 is True

        success2, message2 = install_prompts(target_path=tmp_path, force=False)
        assert success2 is True
        assert "Skipped" in message2

    def test_install_prompts_force_reinstall(self, tmp_path):
        install_prompts(target_path=tmp_path, force=False)

        prompt_file = tmp_path / "scx-research.md"
        prompt_file.write_text("modified")
        assert prompt_file.read_text() == "modified"

        success, _ = install_prompts(target_path=tmp_path, force=True)
        assert success is True
        assert prompt_file.read_text() != "modified"

    def test_list_installed_prompts(self, tmp_path):
        installed_before = list_installed_prompts(target_path=tmp_path)
        assert installed_before == []

        install_prompts(target_path=tmp_path, force=False)
        installed_after = list_installed_prompts(target_path=tmp_path)

        assert "scx" in installed_after
        assert "scx-research" in installed_after

