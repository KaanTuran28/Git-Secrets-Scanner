# Git Secrets Scanner

![CI](https://github.com/KaanTuran28/Git-Secrets-Scanner/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

<p align="center"><b><a href="#english">English</a></b> · <b><a href="#türkçe">Türkçe</a></b></p>

---

## English

A lightweight, dependency-free CLI that scans a directory (or a git working copy) for likely leaked secrets and credentials — API keys, tokens, private keys, hardcoded passwords, and high-entropy strings that don't match a known pattern.

### Overview

Secrets accidentally committed to a repository (API keys, private keys, passwords) are one of the most common and costly security mistakes. This tool gives you a fast, offline, zero-dependency way to catch them before they ever reach a remote — locally, in a pre-commit hook, or as a CI gate.

### Installation

Requires Python 3.9+. No external dependencies for the scanner itself.

```bash
git clone https://github.com/KaanTuran28/Git-Secrets-Scanner.git
cd Git-Secrets-Scanner
```

Or install it as a CLI command:

```bash
pip install -e .
git-secrets-scanner --path . --output report.md
```

### Usage

```bash
python git_secrets_scanner.py --path . --output report.md
python git_secrets_scanner.py --path . --exclude "*.min.js,dist" --output report.md
python git_secrets_scanner.py --path . --format json --output report.json
```

`--format` accepts `markdown` (default) or `json`. The script exits with code `0` if no secrets were found, and `1` if at least one finding was reported — this makes it usable directly as a CI gate or pre-commit hook.

### Detectors

| Detector | What it catches | Severity |
|---|---|---|
| `aws_access_key` | AWS access key IDs (`AKIA...`) | HIGH |
| `github_token` | GitHub personal access tokens (`ghp_...`) | HIGH |
| `slack_token` | Slack bot/user/app tokens (`xox[baprs]-...`) | HIGH |
| `private_key_header` | PEM private key headers (RSA/EC/DSA/OpenSSH) | HIGH |
| `generic_api_key` | `api_key = "..."` style assignments | MEDIUM |
| `hardcoded_password` | `password = "..."` style assignments | MEDIUM |
| `high_entropy_string` | Long, high-Shannon-entropy strings assigned to a variable that don't match a known pattern | LOW |

Matches are redacted in the report (only the first 4 and last 2 characters are shown) so the report itself is safe to share.

### Use as a pre-commit hook / CI gate

Because the script returns a non-zero exit code when it finds something, you can wire it directly into CI:

```yaml
- name: Scan for leaked secrets
  run: python git_secrets_scanner.py --path . --output secrets-report.md
```

Or as a local pre-commit hook (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
python git_secrets_scanner.py --path . --output /tmp/secrets-report.md || exit 1
```

### Example Output

Running against the bundled `sample_repo/` (all values are fake/non-functional fixtures):

```
Scanned sample_repo: 6 finding(s). Report written to sample_report.md
```

See [`sample_report.md`](./sample_report.md) for the full generated report. All secrets in `sample_repo/` are synthetic and non-functional — they exist only to demonstrate detection.

### Project Structure

```
Git-Secrets-Scanner/
├── git_secrets_scanner.py
├── pyproject.toml
├── sample_repo/
│   ├── config.py
│   ├── secrets.env
│   ├── id_rsa_fake.pem
│   └── clean_file.py
├── sample_report.md
├── tests/
│   └── test_git_secrets_scanner.py
├── .github/workflows/ci.yml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── .gitignore
```

### Testing

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -v
```

### License

MIT — see [LICENSE](./LICENSE).

---

## Türkçe

Bir dizini (veya bir git çalışma kopyasını) muhtemel sızdırılmış sırlar ve kimlik bilgileri için tarayan, harici bağımlılığı olmayan, hafif bir CLI — API anahtarları, tokenlar, özel anahtarlar, koda gömülü (hardcoded) parolalar ve bilinen bir kalıba uymayan yüksek entropili dizgiler.

### Genel Bakış

Bir repoya yanlışlıkla commit edilen sırlar (API anahtarları, özel anahtarlar, parolalar) en yaygın ve en maliyetli güvenlik hatalarından biridir. Bu araç, bunları bir remote'a ulaşmadan önce yakalamanın hızlı, çevrimdışı ve sıfır bağımlılıklı bir yolunu sunar — yerel olarak, bir pre-commit hook'unda veya bir CI kapısı (gate) olarak.

### Kurulum

Python 3.9+ gerektirir. Tarayıcının kendisi için harici bağımlılık yoktur.

```bash
git clone https://github.com/KaanTuran28/Git-Secrets-Scanner.git
cd Git-Secrets-Scanner
```

Veya bir CLI komutu olarak kurun:

```bash
pip install -e .
git-secrets-scanner --path . --output report.md
```

### Kullanım

```bash
python git_secrets_scanner.py --path . --output report.md
python git_secrets_scanner.py --path . --exclude "*.min.js,dist" --output report.md
python git_secrets_scanner.py --path . --format json --output report.json
```

`--format`, `markdown` (varsayılan) veya `json` kabul eder. Betik, hiçbir sır bulunamazsa `0` koduyla, en az bir bulgu raporlanmışsa `1` koduyla çıkış yapar — bu da onu doğrudan bir CI kapısı veya pre-commit hook'u olarak kullanılabilir kılar.

### Dedektörler

| Dedektör | Neyi Yakalar | Önem Derecesi |
|---|---|---|
| `aws_access_key` | AWS erişim anahtarı kimlikleri (`AKIA...`) | HIGH |
| `github_token` | GitHub kişisel erişim tokenları (`ghp_...`) | HIGH |
| `slack_token` | Slack bot/kullanıcı/uygulama tokenları (`xox[baprs]-...`) | HIGH |
| `private_key_header` | PEM özel anahtar başlıkları (RSA/EC/DSA/OpenSSH) | HIGH |
| `generic_api_key` | `api_key = "..."` tarzı atamalar | MEDIUM |
| `hardcoded_password` | `password = "..."` tarzı atamalar | MEDIUM |
| `high_entropy_string` | Bir değişkene atanmış, bilinen bir kalıba uymayan, uzun ve yüksek Shannon entropili dizgiler | LOW |

Eşleşmeler raporda maskelenir (yalnızca ilk 4 ve son 2 karakter gösterilir), böylece raporun kendisi paylaşmak için güvenlidir.

### Pre-commit hook / CI kapısı olarak kullanım

Betik bir şey bulduğunda sıfır olmayan bir çıkış kodu döndürdüğü için, doğrudan CI'a bağlayabilirsiniz:

```yaml
- name: Scan for leaked secrets
  run: python git_secrets_scanner.py --path . --output secrets-report.md
```

Veya yerel bir pre-commit hook'u olarak (`.git/hooks/pre-commit`):

```bash
#!/bin/sh
python git_secrets_scanner.py --path . --output /tmp/secrets-report.md || exit 1
```

### Örnek Çıktı

Ürünle birlikte gelen `sample_repo/` dizinine karşı çalıştırıldığında (tüm değerler sahte/işlevsiz test verileridir):

```
Scanned sample_repo: 6 finding(s). Report written to sample_report.md
```

Üretilen tam raporu görmek için [`sample_report.md`](./sample_report.md) dosyasına bakın. `sample_repo/` içindeki tüm sırlar sentetiktir ve işlevsel değildir — yalnızca tespiti göstermek için var olurlar.

### Proje Yapısı

```
Git-Secrets-Scanner/
├── git_secrets_scanner.py
├── pyproject.toml
├── sample_repo/
│   ├── config.py
│   ├── secrets.env
│   ├── id_rsa_fake.pem
│   └── clean_file.py
├── sample_report.md
├── tests/
│   └── test_git_secrets_scanner.py
├── .github/workflows/ci.yml
├── requirements.txt
├── requirements-dev.txt
├── LICENSE
└── .gitignore
```

### Test

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -v
```

### Lisans

MIT — bkz. [LICENSE](./LICENSE).

---
