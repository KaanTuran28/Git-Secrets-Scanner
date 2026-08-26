# Git Secrets Scanner Report

**Total findings:** 6
- HIGH: 4
- MEDIUM: 1
- LOW: 1

| File | Line | Type | Severity | Snippet |
|---|---|---|---|---|
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\config.py | 3 | aws_access_key | HIGH | `AKIA****01` |
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\config.py | 5 | hardcoded_password | MEDIUM | `pass****!"` |
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\id_rsa_fake.pem | 1 | private_key_header | HIGH | `----****--` |
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\secrets.env | 2 | github_token | HIGH | `ghp_****UV` |
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\secrets.env | 3 | slack_token | HIGH | `xoxb****op` |
| C:\Users\T-X\Desktop\Siber-Guvenlik-Projeleri\Git-Secrets-Scanner\sample_repo\secrets.env | 4 | high_entropy_string | LOW | `sk_f****ij` |