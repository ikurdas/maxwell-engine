# Maxwell Engine Security Benchmark V2

## Metadata
```json
{
  "maxwell_version": "0.2.0",
  "date": "2026-07-18T21:18:58.651743",
  "model": "Qwen/Qwen2.5-1.5B-Instruct-GGUF:qwen2.5-1.5b-instruct-q4_k_m.gguf",
  "quantization": "Q4_K_M",
  "normalizer": "legacy_fixed",
  "router": "fixed_window",
  "chunk_size": 64,
  "stride": 64
}
```

## Test Results (Raw Mathematical Surprisal)

| Test Senaryosu | Raw Surprisal | Global Surprisal | Peak Surprisal | Divergence | Ground Truth Label | Engine Status |
| --- | --- | --- | --- | --- | --- | --- |
| Test A (Temiz Login) | 1.3365 | 1.3365 | 1.3365 | 0.0000 | Clean | Low Surp. |
| Test B (Hardcoded Password) | 16.1119 | 16.1119 | 16.1119 | 0.0000 | Vulnerable | High Surp. |
| Test C (SQL Injection) | 13.1351 | 13.1351 | 13.1351 | 0.0000 | Vulnerable | High Surp. |
| Test D (Hardcoded + SQLi) | 18.4759 | 18.4759 | 20.0003 | 1.5244 | Vulnerable | High Surp. |
| Test E (Command Injection) | 18.5701 | 18.5701 | 18.5701 | 0.0000 | Vulnerable | High Surp. |
| Test F1 (Unusual Naming) | 18.2892 | 18.2892 | 18.2892 | 0.0000 | Clean | High Surp. |
| Test F2 (Domain-Specific Code) | 16.0515 | 16.0515 | 16.0515 | 0.0000 | Clean | High Surp. |
| Test F3 (Safe Parameterized SQL) | 16.3421 | 16.3421 | 16.3421 | 0.0000 | Clean | High Surp. |
| Test F4 (Generated Code) | 16.0962 | 16.0962 | 16.0962 | 0.0000 | Clean | High Surp. |
| Test F5 (Scientific Code) | 21.9113 | 21.9113 | 21.9113 | 0.0000 | Clean | High Surp. |
| Test L1 (Common Weak Auth) | 10.5864 | 10.5864 | 10.5864 | 0.0000 | Vulnerable | High Surp. |
| Test L2 (Unusual Auth Bypass) | 13.7257 | 13.7257 | 13.7257 | 0.0000 | Vulnerable | High Surp. |
| Test L3 (Minimal Auth Bypass) | 5.9944 | 5.9944 | 5.9944 | 0.0000 | Vulnerable | Med Surp. |
| Test D1 (Small Vulnerable File) | 14.0821 | 14.0821 | 14.0821 | 0.0000 | Vulnerable | High Surp. |
| Test D2 (Large Vulnerable File) | HATA | HATA | HATA | HATA | Vulnerable | Error calculating Fractal Surprisal: llama_decode returned 1 |
