import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import git_secrets_scanner as gss

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLE_REPO = REPO_ROOT / "sample_repo"


def test_detects_aws_access_key():
    findings = gss.scan_file(SAMPLE_REPO / "config.py")
    types = {f["type"] for f in findings}
    assert "aws_access_key" in types


def test_detects_hardcoded_password():
    findings = gss.scan_file(SAMPLE_REPO / "config.py")
    types = {f["type"] for f in findings}
    assert "hardcoded_password" in types


def test_detects_github_and_slack_tokens():
    findings = gss.scan_file(SAMPLE_REPO / "secrets.env")
    types = {f["type"] for f in findings}
    assert "github_token" in types
    assert "slack_token" in types


def test_detects_private_key_header():
    findings = gss.scan_file(SAMPLE_REPO / "id_rsa_fake.pem")
    types = {f["type"] for f in findings}
    assert "private_key_header" in types


def test_clean_file_has_no_findings():
    findings = gss.scan_file(SAMPLE_REPO / "clean_file.py")
    assert findings == []


def test_redacted_snippet_does_not_contain_full_secret():
    findings = gss.scan_file(SAMPLE_REPO / "config.py")
    aws_finding = next(f for f in findings if f["type"] == "aws_access_key")
    assert "AKIAFAKEEXAMPLEKEY01" not in aws_finding["redacted_snippet"]
    assert "*" in aws_finding["redacted_snippet"]


def test_shannon_entropy_low_vs_high():
    low = gss.shannon_entropy("aaaaaaaaaa")
    high = gss.shannon_entropy("aB3$kQ9!zM2@pL7#")
    assert low < high


def test_scan_directory_excludes_git_and_node_modules(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text('AWS_ACCESS_KEY = "AKIAFAKEEXAMPLEKEY02"\n')
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.js").write_text('AWS_ACCESS_KEY = "AKIAFAKEEXAMPLEKEY03"\n')
    (tmp_path / "app.py").write_text('AWS_ACCESS_KEY = "AKIAFAKEEXAMPLEKEY04"\n')

    findings = gss.scan_directory(tmp_path)
    files_hit = {Path(f["file"]).name for f in findings}
    assert "config" not in files_hit
    assert "pkg.js" not in files_hit
    assert "app.py" in files_hit


def test_exit_code_is_nonzero_when_findings_present():
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "git_secrets_scanner.py"), "--path", str(SAMPLE_REPO), "--output", str(REPO_ROOT / "sample_report.md")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1


def test_exit_code_is_zero_when_no_findings(tmp_path):
    (tmp_path / "clean.py").write_text("def add(a, b):\n    return a + b\n")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "git_secrets_scanner.py"), "--path", str(tmp_path), "--output", str(tmp_path / "report.md")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0


def test_json_report_is_valid_json():
    findings = gss.scan_file(SAMPLE_REPO / "config.py")
    parsed = json.loads(gss.render_json_report(findings))
    assert isinstance(parsed, list)
    assert len(parsed) == len(findings)
    assert {"file", "line", "type", "severity", "redacted_snippet"} <= parsed[0].keys()


def test_json_report_does_not_leak_full_secret():
    findings = gss.scan_file(SAMPLE_REPO / "config.py")
    report_text = gss.render_json_report(findings)
    assert "AKIAFAKEEXAMPLEKEY01" not in report_text
