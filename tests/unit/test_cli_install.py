"""
Unit tests for skill installation

Tests the Codex skill installation functionality.
"""

from supercodex.cli.install_skills import (
    install_skills,
    list_available_skills,
    list_installed_skills,
)


class TestInstallSkills:
    """Test suite for install skills functionality"""

    def test_list_available_skills(self):
        skills = list_available_skills()

        assert isinstance(skills, list)
        assert len(skills) > 0
        assert "scx-research" in skills
        assert "scx-index-repo" in skills

    def test_install_skills_to_temp_dir(self, tmp_path):
        target_dir = tmp_path / "skills"

        success, message = install_skills(target_path=target_dir, force=False)

        assert success is True
        assert "Installed" in message
        assert target_dir.exists()

        # Skills are installed as folders with SKILL.md.
        assert (target_dir / "scx-research" / "SKILL.md").exists()
        assert (target_dir / "scx-index-repo" / "SKILL.md").exists()

    def test_install_skills_skip_existing(self, tmp_path):
        target_dir = tmp_path / "skills"

        success1, _ = install_skills(target_path=target_dir, force=False)
        assert success1 is True

        success2, message2 = install_skills(target_path=target_dir, force=False)
        assert success2 is True
        assert "Skipped" in message2

    def test_install_skills_force_reinstall(self, tmp_path):
        target_dir = tmp_path / "skills"

        success1, _ = install_skills(target_path=target_dir, force=False)
        assert success1 is True

        skill_file = target_dir / "scx-research" / "SKILL.md"
        skill_file.write_text("modified")
        assert skill_file.read_text() == "modified"

        success2, message2 = install_skills(target_path=target_dir, force=True)
        assert success2 is True
        assert "Installed" in message2

        content = skill_file.read_text()
        assert content != "modified"
        assert "research" in content.lower()

    def test_list_installed_skills(self, tmp_path):
        target_dir = tmp_path / "skills"

        # Before install
        installed_before = list_installed_skills(target_path=target_dir)
        assert installed_before == []

        # After install
        install_skills(target_path=target_dir, force=False)
        installed_after = list_installed_skills(target_path=target_dir)

        assert isinstance(installed_after, list)
        assert "scx-research" in installed_after

    def test_install_skills_creates_target_directory(self, tmp_path):
        target_dir = tmp_path / "nested" / "skills"
        assert not target_dir.exists()

        success, _ = install_skills(target_path=target_dir, force=False)
        assert success is True
        assert target_dir.exists()

    def test_available_skills_format(self):
        skills = list_available_skills()

        assert all(isinstance(s, str) for s in skills)
        assert all(s.startswith("scx-") for s in skills)
        assert skills == sorted(skills)

    def test_skill_markdown_substantial(self, tmp_path):
        target_dir = tmp_path / "skills"
        install_skills(target_path=target_dir, force=False)

        skill_file = target_dir / "scx-research" / "SKILL.md"
        content = skill_file.read_text()
        assert len(content) > 100

    def test_all_expected_skills_available(self):
        skills = list_available_skills()
        expected = ["scx-agent", "scx-index-repo", "scx-recommend", "scx-research"]

        for name in expected:
            assert name in skills, f"Expected skill '{name}' not found"


class TestInstallSkillsEdgeCases:
    def test_install_to_nonexistent_parent(self, tmp_path):
        target_dir = tmp_path / "a" / "b" / "c" / "skills"

        success, _ = install_skills(target_path=target_dir, force=False)
        assert success is True
        assert target_dir.exists()

    def test_empty_target_directory_ok(self, tmp_path):
        target_dir = tmp_path / "skills"
        target_dir.mkdir()

        success, _ = install_skills(target_path=target_dir, force=False)
        assert success is True


def test_cli_integration():
    """Integration test: verify CLI can import and use install functions."""
    from supercodex.cli.install_skills import list_available_skills

    skills = list_available_skills()
    assert len(skills) > 0

