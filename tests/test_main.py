"""End-to-end checks of the command-line entry point."""

from src.main import main


def test_cli_renders_both_formats(tmp_path, capsys):
    path = tmp_path / "repo.txt"
    path.write_text("A: B\nB: A\n", encoding="utf-8")
    result = main(["--package", "A", "--repo-url", str(path), "--mode", "test",
                   "--ascii-tree", "--mermaid"])
    output = capsys.readouterr()
    assert result == 0
    assert "A --> B" in output.out
    assert "B --> A" in output.out
    assert "A (cycle)" in output.out
    assert output.err == ""


def test_cli_reports_malformed_repository(tmp_path, capsys):
    path = tmp_path / "repo.txt"
    path.write_text("invalid\n", encoding="utf-8")
    assert main(["--package", "A", "--repo-url", str(path), "--mode", "test"]) == 1
    assert "Malformed test repository line" in capsys.readouterr().err


def test_cli_reports_unknown_package(tmp_path, capsys):
    path = tmp_path / "repo.txt"
    path.write_text("B:\n", encoding="utf-8")
    assert main(["--package", "A", "--repo-url", str(path), "--mode", "test"]) == 1
    assert "Package not found" in capsys.readouterr().err
