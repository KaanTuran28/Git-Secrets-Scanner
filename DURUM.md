# Durum Günlüğü

> En üstteki kayıt en güncelidir. Her çalışma sonrası buraya kısa bir not düşülür.

---

## 2026-08-20 — Paketleme, JSON çıktı ve lint eklendi

- Konu: `pyproject.toml` ile pip kurulabilir hale getirildi (`pip install -e .` → `git-secrets-scanner` komutu), `--format json` eklendi, ruff lint + CI'a ayrı lint job'u eklendi.
- Durum: ✅ 12/12 test geçiyor, `ruff check .` temiz. `pip install -e .` başarıyla kuruldu ve `pip show` ile doğrulandı; bu makinedeki bir Uygulama Denetimi (App Control) ilkesi üretilen `.exe` launcher'ının doğrudan çalıştırılmasını engellediği için CLI komutu bu ortamda uçtan uca çalıştırılamadı — ama `python git_secrets_scanner.py ...` (aynı kod yolu) testlerle zaten doğrulanmış durumda, bu sadece yerel bir güvenlik yazılımı kısıtlaması, paketleme/kod sorunu değil. GitHub Actions CI'da (Ubuntu runner) bu kısıtlama yok, orada sorunsuz çalışacaktır.

**Sıradaki iş:** GitHub'da `Git-Secrets-Scanner` adıyla repo aç, git init + push.

---

## 2026-08-20 — İlk sürüm oluşturuldu

- Konu: Regex + Shannon entropy tabanlı secrets tarayıcı (AWS key, GitHub/Slack token, private key header, generic API key, hardcoded password, yüksek entropili string) + sentetik örnek repo + 10 testlik pytest paketi + CI hazırlandı.
- Durum: ✅ Çalışıyor, 10/10 test geçiyor, `sample_report.md` gerçek çalıştırmadan üretildi (6 bulgu).

**Sıradaki iş:** GitHub'da `Git-Secrets-Scanner` adıyla repo aç, git init + push.
