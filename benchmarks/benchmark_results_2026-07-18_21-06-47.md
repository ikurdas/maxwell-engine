# Maxwell Engine Security Benchmark

**Date:** 2026-07-18 21:06:47
**Model:** Qwen/Qwen2.5-1.5B-Instruct-GGUF:qwen2.5-1.5b-instruct-q4_k_m.gguf

## Test Results (Mathematical Surprisal)

| Test Senaryosu | Ölçülen Surprisal Skoru (0.0 - 1.0) | Durum |
| --- | --- | --- |
| Test A (Temiz Login) | 0.1300 | 🟢 Düşük Risk (Clean) |
| Test B (Hardcoded Password) | 1.0000 | 🔴 Kritik Zafiyet (Bifurcation) |
| Test C (SQL Injection) | 1.0000 | 🔴 Kritik Zafiyet (Bifurcation) |
| Test D (Hardcoded + SQL Injection) | 1.0000 | 🔴 Kritik Zafiyet (Bifurcation) |
| Test E (Command Injection + Auth Bypass) | 1.0000 | 🔴 Kritik Zafiyet (Bifurcation) |
