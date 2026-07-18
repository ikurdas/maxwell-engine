import sys
import json
import time
import os
import datetime
from core.engine import MaxwellEngine
from cli import download_model_if_needed

TEST_PAYLOADS = {
    "Test A (Temiz Login)": """
def login(username, password):
    db = get_database_connection()
    user = db.query("SELECT * FROM users WHERE username=%s AND pass=%s", (username, password))
    if user:
        return "Giriş Başarılı"
    return "Hatalı Giriş"
""",
    "Test B (Hardcoded Password)": """
def login(username, password):
    if password == "123456" or password == "admin":
        return "Giriş Başarılı"
    return "Hatalı Giriş"
""",
    "Test C (SQL Injection)": """
def login(username, password):
    db = get_database_connection()
    # Zafiyetli sorgu
    query = f"SELECT * FROM users WHERE username='{username}' AND pass='{password}'"
    user = db.query(query)
    if user:
        return "Giriş Başarılı"
    return "Hatalı Giriş"
""",
    "Test D (Hardcoded + SQL Injection)": """
def login(username, password):
    if username == "super_admin" and password == "admin123":
        return "Sisteme tam yetkiyle giriş yapıldı."
        
    db = get_database_connection()
    user = db.query(f"SELECT * FROM users WHERE username='{username}' AND pass='{password}'")
    
    if user:
        return "Giriş Başarılı"
    return "Hatalı Giriş"
""",
    "Test E (Command Injection + Auth Bypass)": """
import os
def execute_system_command(user_input):
    if "admin" in user_input:
        os.system("rm -rf /")
    return os.system(f"ping -c 4 {user_input}")
"""
}

def run_benchmark():
    print("🚀 Başlatılıyor: Maxwell Engine Güvenlik Zafiyeti Benchmark'ı")
    print("------------------------------------------------------------")
    
    model_name = "Qwen/Qwen2.5-1.5B-Instruct-GGUF:qwen2.5-1.5b-instruct-q4_k_m.gguf"
    print(f"[*] Model indiriliyor veya kontrol ediliyor: {model_name}")
    try:
        model_path = download_model_if_needed(model_name)
    except Exception as e:
        print(f"[!] Model yüklenirken hata oluştu: {e}")
        sys.exit(1)
        
    print("[*] Termodinamik Motor (LLAMA-CPP) başlatılıyor...")
    engine = MaxwellEngine(model_path=model_path)
    print("\n")
    
    results = []
    
    print("| Test Senaryosu | Ölçülen Surprisal Skoru (0.0 - 1.0) | Durum |")
    print("| --- | --- | --- |")
    
    for test_name, payload in TEST_PAYLOADS.items():
        try:
            # LLM Üretimi (Analysis) adımını atlayıp sadece matematiksel Metrik hesaplamasını çalıştırıyoruz
            # ki benchmark sadece saniyeler sürsün (text generation beklemesin)
            surprisal = engine.inference.calculate_surprisal(payload)
            
            # Skoru değerlendirelim
            if surprisal >= 0.7:
                status = "🔴 Kritik Zafiyet (Bifurcation)"
            elif surprisal >= 0.4:
                status = "🟡 Orta Risk (Noise)"
            else:
                status = "🟢 Düşük Risk (Clean)"
                
            print(f"| {test_name} | {surprisal:.4f} | {status} |")
            results.append({"test": test_name, "score": surprisal, "status": status})
            
        except Exception as e:
            print(f"| {test_name} | HATA | {e} |")
            results.append({"test": test_name, "score": "HATA", "status": str(e)})
            
    print("\n[*] Benchmark başarıyla tamamlandı.")
    
    # Save results to a markdown file
    os.makedirs("benchmarks", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join("benchmarks", f"benchmark_results_{timestamp}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Maxwell Engine Security Benchmark\n\n")
        f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model:** {model_name}\n\n")
        f.write("## Test Results (Mathematical Surprisal)\n\n")
        f.write("| Test Senaryosu | Ölçülen Surprisal Skoru (0.0 - 1.0) | Durum |\n")
        f.write("| --- | --- | --- |\n")
        for r in results:
            score_str = f"{r['score']:.4f}" if isinstance(r['score'], float) else r['score']
            f.write(f"| {r['test']} | {score_str} | {r['status']} |\n")
            
    print(f"[*] Rapor kaydedildi: {filepath}")

if __name__ == "__main__":
    run_benchmark()
