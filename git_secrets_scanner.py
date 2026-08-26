#!/usr/bin/env python3
"""Scan a directory tree for likely leaked secrets (API keys, tokens, private keys, passwords)."""
import argparse
import json
import math
import os
import re
import sys
from fnmatch import fnmatch
from pathlib import Path

DEFAULT_EXCLUDES = [".git", "node_modules", ".venv", "venv", "__pycache__"]

DETECTORS = [
    ("aws_access_key", "HIGH", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", "HIGH", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("slack_token", "HIGH", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,48}")),
    ("private_key_header", "HIGH", re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----")),
    ("generic_api_key", "MEDIUM", re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][0-9a-zA-Z]{16,45}['\"]")),
    ("hardcoded_password", "MEDIUM", re.compile(r"(?i)password\s*=\s*['\"].{6,}['\"]")),
]

ENTROPY_CANDIDATE_RE = re.compile(r"""[:=]\s*['"]([A-Za-z0-9+/_-]{20,})['"]""")
ENTROPY_THRESHOLD = 4.0


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def _redact(value: str) -> str:
    if len(value) <= 6:
        return "****"
    return f"{value[:4]}****{value[-2:]}"


def _is_binary(sample: bytes) -> bool:
    return b"\x00" in sample


def scan_file(path) -> list:
    path = Path(path)
    findings = []
    try:
        raw = path.read_bytes()
    except OSError:
        return findings
    if _is_binary(raw[:1024]):
        return findings
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return findings

    for line_no, line in enumerate(text.splitlines(), start=1):
        matched_spans = []
        for det_type, severity, pattern in DETECTORS:
            for m in pattern.finditer(line):
                findings.append({
                    "file": str(path),
                    "line": line_no,
                    "type": det_type,
                    "severity": severity,
                    "redacted_snippet": _redact(m.group(0)),
                })
                matched_spans.append(m.span())

        for m in ENTROPY_CANDIDATE_RE.finditer(line):
            candidate = m.group(1)
            if shannon_entropy(candidate) > ENTROPY_THRESHOLD:
                already_covered = any(span[0] <= m.start(1) < span[1] for span in matched_spans)
                if not already_covered:
                    findings.append({
                        "file": str(path),
                        "line": line_no,
                        "type": "high_entropy_string",
                        "severity": "LOW",
                        "redacted_snippet": _redact(candidate),
                    })

    return findings


def _is_excluded_dir(dirname: str, exclude_globs) -> bool:
    return any(fnmatch(dirname, pattern) for pattern in exclude_globs)


def scan_directory(path, exclude_globs=None) -> list:
    exclude_globs = list(DEFAULT_EXCLUDES) + list(exclude_globs or [])
    findings = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not _is_excluded_dir(d, exclude_globs)]
        for filename in files:
            if any(fnmatch(filename, pattern) for pattern in exclude_globs):
                continue
            file_path = Path(root) / filename
            findings.extend(scan_file(file_path))
    return findings


def render_report(findings: list) -> str:
    lines = ["# Git Secrets Scanner Report", ""]
    lines.append(f"**Total findings:** {len(findings)}")
    by_severity = {}
    for f in findings:
        by_severity[f["severity"]] = by_severity.get(f["severity"], 0) + 1
    for sev in ("HIGH", "MEDIUM", "LOW"):
        if sev in by_severity:
            lines.append(f"- {sev}: {by_severity[sev]}")
    lines.append("")
    if findings:
        lines.append("| File | Line | Type | Severity | Snippet |")
        lines.append("|---|---|---|---|---|")
        for f in sorted(findings, key=lambda x: (x["file"], x["line"])):
            lines.append(f"| {f['file']} | {f['line']} | {f['type']} | {f['severity']} | `{f['redacted_snippet']}` |")
    else:
        lines.append("No secrets found.")
    return "\n".join(lines)


def render_json_report(findings: list) -> str:
    return json.dumps(findings, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Scan a directory for likely leaked secrets.")
    parser.add_argument("--path", required=True)
    parser.add_argument("--output", default="sample_report.md")
    parser.add_argument("--exclude", default="", help="Comma-separated glob patterns to exclude")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    exclude_globs = [g.strip() for g in args.exclude.split(",") if g.strip()]
    findings = scan_directory(args.path, exclude_globs=exclude_globs)
    report = render_json_report(findings) if args.format == "json" else render_report(findings)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Scanned {args.path}: {len(findings)} finding(s). Report written to {args.output}")

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
