import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from huggingface_hub import hf_hub_download
import uvicorn

from core.engine import MaxwellEngine

engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    # TR: Sunucu başlarken modeli (Qwen2.5 7B) yükle. 
    # EN: Load the model (Qwen2.5 7B) when the server starts.
    # TR: Not: Hızlı başlasın diye isterseniz 1.5B'yi de varsayılan yapabilirsiniz.
    # EN: Note: You can make 1.5B default if you want faster startup.
    print("[*] Starting Maxwell Engine (FastAPI)...")
    try:
        repo_id = "Qwen/Qwen2.5-7B-Instruct-GGUF"
        filename1 = "qwen2.5-7b-instruct-q4_k_m-00001-of-00002.gguf"
        filename2 = "qwen2.5-7b-instruct-q4_k_m-00002-of-00002.gguf"
        
        # TR: 7B modeli iki parça olduğu için ikisini de indirdiğimizden emin olmalıyız
        print("[*] Downloading model parts (this may take a few minutes)...")
        hf_hub_download(repo_id=repo_id, filename=filename2) # Part 2'yi cache'e al
        model_path = hf_hub_download(repo_id=repo_id, filename=filename1) # Part 1'i yükle
        
        engine = MaxwellEngine(model_path=model_path)
        print("[*] Model loaded successfully.")
    except Exception as e:
        print(f"[!] Error loading model: {e}")
    yield
    print("[*] Shutting down server, performing cleanup...")

app = FastAPI(lifespan=lifespan)

# TR: Statik dosyaları (HTML/CSS/JS) sunmak için
# EN: To serve static files (HTML/CSS/JS)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class AnalyzeRequest(BaseModel):
    code: str
    mode: str = "maxwell"

STANDARD_PROMPT = """Sen kıdemli bir yazılım mühendisisin.
Aşağıdaki kodu güvenlik açıkları, mantık hataları ve genel kod kalitesi açısından incele.
Cevabını sadece JSON formatında ver."""

standard_schema = {
    "type": "object",
    "properties": {
        "bulunan_hatalar": {"type": "string", "description": "Kodda bulunan tüm hatalar"},
        "guvenlik_aciklari": {"type": "string", "description": "Güvenlik zafiyetleri"},
        "standart_oneri": {"type": "string", "description": "Nasıl düzeltileceğine dair öneri"}
    },
    "required": ["bulunan_hatalar", "guvenlik_aciklari", "standart_oneri"],
    "additionalProperties": False
}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/analyze")
async def analyze_endpoint(req: AnalyzeRequest):
    global engine
    if engine is None:
        return JSONResponse(status_code=503, content={"error": "Motor henüz yüklenmedi veya başlatılamadı."})
    
    if not req.code or not req.code.strip():
        return JSONResponse(status_code=400, content={"error": "Lütfen analiz edilecek kodu girin."})
    
    try:
        if req.mode == "standard":
            messages = [
                {"role": "system", "content": STANDARD_PROMPT},
                {"role": "user", "content": req.code}
            ]
            result_json = engine.inference.generate_report(messages, standard_schema)
            return {"mode": "standard", "result": result_json}
        else:
            result_str = engine.analyze(req.code)
            # TR: strict=False çünkü LLM bazen kontrol karakteri üretebilir
            # EN: strict=False because LLM can sometimes produce control characters
            result_json = json.loads(result_str, strict=False)
            return {"mode": "maxwell", "result": result_json}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    # TR: HuggingFace Spaces üzerinde çalışıyorsa port 7860 olmak zorundadır.
    import os
    port = 7860 if os.environ.get("SPACE_ID") else 3141
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
