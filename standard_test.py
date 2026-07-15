import json
import sys
from huggingface_hub import hf_hub_download
from core.inference import CustomInferenceLayer

STANDARD_PROMPT = """Sen kıdemli bir yazılım mühendisisin.
Aşağıdaki kodu güvenlik açıkları, mantık hataları ve genel kod kalitesi açısından incele.
Cevabını sadece JSON formatında ver."""

schema = {
    "type": "object",
    "properties": {
        "bulunan_hatalar": {"type": "string", "description": "Kodda bulunan tüm hatalar"},
        "guvenlik_aciklari": {"type": "string", "description": "Güvenlik zafiyetleri"},
        "standart_oneri": {"type": "string", "description": "Nasıl düzeltileceğine dair öneri"}
    },
    "required": ["bulunan_hatalar", "guvenlik_aciklari", "standart_oneri"],
    "additionalProperties": False
}

def run_test():
    if len(sys.argv) < 2:
        print("Usage: python standard_test.py <file_path>")
        return
        
    target_file = sys.argv[1]
    with open(target_file, "r", encoding="utf-8") as f:
        code = f.read()
        
    print("[*] Loading Standard Model (Thermodynamic rules disabled)...")
    # TR: Zaten önbellekte (cache) olan modeli kullanıyoruz, tekrar indirmeyecek
    # EN: We are using the model that is already in cache, it will not download again
    model_path = hf_hub_download(repo_id="bartowski/Qwen2.5-7B-Instruct-GGUF", filename="Qwen2.5-7B-Instruct-Q4_K_M.gguf")
    
    inference = CustomInferenceLayer(model_path=model_path)
    
    messages = [
        {"role": "system", "content": STANDARD_PROMPT},
        {"role": "user", "content": code}
    ]
    
    print("[*] Performing standard analysis, please wait...\n")
    report = inference.generate_report(messages, schema)
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_test()
