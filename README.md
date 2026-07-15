# Maxwell Engine (Formerly Antigravity)

**Maxwell Engine** is a Zero-Hallucination, Thermodynamic Code & Architecture Inspector. Unlike standard AI linters that flag every minor code smell (producing noise), Maxwell evaluates code using genuine mathematical *Surprisal* (Logprobs) to find the absolute most critical, system-breaking anomalies (Bifurcations) in your project.

Based on the principles of **Computational Thermodynamics**, this engine filters out low-energy boilerplate noise and focuses exclusively on high-entropy chaos.

---

## 🇹🇷 Türkçe (Turkish) - Maxwell Motoru Nedir?

Maxwell Motoru, sistemlerin karmaşıklığını ve bilgi yoğunluğunu yöneten bir **Hesaplamalı Termodinamik Ünitesidir**. 

Standart yapay zeka araçları kodunuzdaki her ufak detayı (kullanılmayan değişkenler, boşluk hataları, ufak güvenlik uyarıları) listeler. Bu, devasa projelerde "Uyarı Yorgunluğu"na (Alert Fatigue / Gürültüye) sebep olur. Maxwell Motoru ise **"Gürültüyü Filtrele, Kaosu Yakala"** prensibiyle çalışır.

### Nasıl Çalışır? (Sıfır Halüsinasyon Mimarisi)

1. **Gerçek Matematiksel Surprisal Hesabı:** Modelden metni değerlendirmesini "istemek" yerine, `llama-cpp-python` aracılığıyla metnin her bir kelimesi (token) okunduğunda modelin arka planda ürettiği **Logprob (Olasılık) değerleri** hesaplanır. Bu değerlerin doğal logaritma ortalaması alınarak saf $I(w)$ Surprisal değeri hesaplanır.
2. **Kritiklik Skoru:** Eğer kodda `if password == 'admin123'` gibi sisteme aykırı, düşük olasılıklı (beklenmedik) bir satır varsa, modelin olasılık matematiği anında dibe vurur. Sistem bunu yakalar ve yapay zekanın "uydurmasına" (halüsinasyona) izin vermeden doğrudan **1.0 Kritiklik Skoru (Kırmızı Alarmlı Çatallanma)** üretir.
3. **Context İzolasyonu (Prompt Injection Koruması):** Sistem analiz ettiği kodu izole bir kapsül içinde inceler. Böylece kendi içinde LLM terimleri (enerji, prompt, semantik vs.) barındıran kodlar bile sistemi manipüle edemez.

> 💡 **Neden Maxwell? (Motor ve Direksiyon Metaforu)**  
> Standart bir yapay zeka (örn: Qwen 7B) devasa bir veriyi (kod tabanı, sunucu logları, mimari tasarımlar veya karmaşık iş akışları) okuduğunda, kritik bir sistem çöküş riskini (örn: bir veritabanı kilitlenme anı veya `admin123` arka kapısı) görebilir. Ancak aynı zamanda ufak bir yazım hatasını, gereksiz bir boşluğu veya önemsiz bir log uyarısını da görüp hepsini **aynı kefeye koyarak** size 10 maddelik uzun, "gürültülü" bir liste verir.  
> Maxwell Motoru ise modelin boğazını sıkarak şunu söyler: *"Bana diğer 9 ufak hatayı anlatıp kafamı ütüleme. İçlerindeki en kaotik, matematiksel olarak en beklenmedik olan (Surprisal) 1 numaralı yapısal çatallanmayı (Bifurcation) bul ve sadece onu söyle!"*  
> **Özetle:** Arabanın saf gücü ve motoru Qwen/Llama olabilir, ancak o motorun direksiyonu, freni ve devasa veri yığınları (kod, log, metin, mimari) içindeki asıl hedefi tam on ikiden vurmasını sağlayan navigasyon tamamen Maxwell Termodinamik Filtresidir.

> ⚠️ **Neden Ollama veya OpenAI API Kullanılmıyor?**  
> Standart API'ler (Ollama, ChatGPT, Claude) metin üretimi için tasarlanmıştır ve sinir ağının ürettiği **ham matematiksel olasılıkları (Logprobs)** dışarıya tam olarak vermezler. Maxwell Motoru, metin uydurmak yerine kodun "Beklenmezlik (Surprisal)" değerini hesaplar. Bu saf termodinamik hesabı yapabilmek için modelin çekirdeğine doğrudan bağlanmamız (`llama-cpp-python` ile `logits_all=True`) zorunludur. Ollama kullanılsaydı, sistem halüsinasyon gören standart bir Linter'a dönüşürdü.

### Kurumsal Ölçeklendirme (vLLM Entegrasyonu)
Eğer Maxwell Motoru'nu binlerce dosyayı saniyeler içinde analiz edecek devasa bir sunucu kümesinde (Enterprise Scale) çalıştırmak isterseniz **vLLM** kullanabilirsiniz. Ollama'nın aksine vLLM, `prompt_logprobs` parametresi ile gerekli termodinamik matematiği dışarıya açar.
**Nasıl Uygulanır?**
1. vLLM sunucusunu başlatın: `python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B-Instruct`
2. `core/inference.py` içindeki `llama-cpp-python` çağrılarını silip vLLM sunucusuna istek atacak şekilde güncelleyin. İstek atarken mutlaka `"logprobs": 1` ve `"prompt_logprobs": 1` parametrelerini ekleyin.

### Kullanım (CLI & Web Arayüzü)

> **🔒 Gizlilik Notu:** Maxwell Motoru %100 lokal (çevrimdışı) çalışır. İlk çalıştırdığınızda HuggingFace üzerinden açık kaynaklı bir GGUF modelini (Qwen2.5) bilgisayarınıza indirir. Kodunuz hiçbir bulut API'sine (OpenAI, Anthropic vb.) gönderilmez.

#### 1. Web Arayüzü (Önerilen)
DorgEnt NLP tasarımıyla güçlendirilmiş, A/B testi yapabileceğiniz modern web arayüzünü başlatmak için:
```bash
# Gerekli kütüphaneleri yükleyin (FastAPI, Uvicorn, Llama-cpp vb.)
pip install -r requirements.txt

# Sunucuyu başlatın
python app.py
# Tarayıcınızda açın: http://localhost:3141
```

#### 2. Terminal (CLI) Kullanımı
```bash
# Model otomatik indirilerek CLI analizi başlar (Varsayılan Qwen 1.5B)
python cli.py qa_examples/bad_auth.py

# Çok daha zeki ve isabetli 7B modeli ile tam analiz
python cli.py qa_examples/bad_auth.py -m bartowski/Qwen2.5-7B-Instruct-GGUF:Qwen2.5-7B-Instruct-Q4_K_M.gguf
```

---

## 🇬🇧 English - What is Maxwell Engine?

Maxwell Engine is a **Computational Thermodynamic Unit** designed to manage system complexity, information density, and entropic balance.

Standard AI code reviewers will list every minor detail (unused variables, whitespace issues, generic security warnings). In massive projects, this causes "Alert Fatigue" (Noise). Maxwell Engine operates on the principle of **"Filter the Noise, Catch the Chaos"**.

### How it Works (Zero-Hallucination Architecture)

1. **True Mathematical Surprisal:** Instead of asking the model to "guess" a score, the engine uses `llama-cpp-python` with `logits_all=True` to extract raw neural **Logprobs**. It calculates the average natural logarithm of these probabilities to compute the pure $I(w)$ Surprisal value.
2. **Criticality Score:** If there is a highly unexpected, anomalous line in the code (like a hardcoded backdoor `if password == 'admin123'`), the model's token probability drops exponentially. The engine intercepts this math and hardcodes a **1.0 Criticality Score** (Bifurcation Point), completely eliminating LLM score hallucination.
3. **Context Isolation (Prompt Injection Shield):** The engine wraps the target code in a strict containment prompt. This ensures that even if you feed it code that contains AI terminology (prompts, semantic gravity, energy), the model won't get confused and will still analyze it purely as a structural observer.

> 💡 **Why Maxwell? (The Engine vs. Steering Metaphor)**  
> When a standard AI (e.g., Qwen 7B) reads a massive dataset (a codebase, server logs, architectural designs, or complex business workflows), it might spot a critical system-collapse risk (like a database deadlock or an `admin123` backdoor). However, it will also notice a minor typo, an unused variable, or a harmless warning, treating them all equally and giving you a 10-point list of noise.  
> Maxwell Engine, however, chokes the model's output and says: *"Do not bother me with the 9 minor formatting issues. Calculate the mathematical probabilities, find the single most chaotic, high-energy (Surprisal) structural anomaly (Bifurcation), and only report that!"*  
> **In short:** The raw power (the engine) of the car might be Qwen/Llama, but the steering wheel, the brakes, and the sniper-like navigation system that hits the bullseye through massive piles of data (code, logs, text, architecture) is purely the Maxwell Thermodynamic Filter.

> ⚠️ **Why not use Ollama or OpenAI APIs?**  
> Standard APIs (like Ollama, ChatGPT, or Claude) are built for text generation and heavily abstract or hide the raw neural network probabilities (**Logprobs**). Maxwell Engine does not "guess" code quality; it mathematically calculates its "Surprisal". To perform this thermodynamic calculation, we must hook directly into the model's core (using `llama-cpp-python` with `logits_all=True`). If we used Ollama, the engine would degrade into a standard hallucinating linter.

### Enterprise Scaling (vLLM Integration)
If you want to deploy Maxwell Engine across a massive server cluster to analyze thousands of files per second, you can use **vLLM**. Unlike Ollama, the vLLM API supports the `prompt_logprobs` parameter, which exposes the exact thermodynamic math Maxwell needs.
**How to Implement:**
1. Start your vLLM server: `python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen2.5-7B-Instruct`
2. Replace the `llama-cpp-python` implementation in `core/inference.py` with a simple HTTP request to your vLLM server. Ensure you include `"logprobs": 1` and `"prompt_logprobs": 1` in your JSON payload.

### Usage (CLI & Web UI)

> **🔒 Privacy Note:** Maxwell Engine runs 100% locally. On first run, it automatically downloads an open-source GGUF model (Qwen2.5) from HuggingFace to your local cache. Your code is never sent to any cloud API (OpenAI, Anthropic, etc.).

#### 1. Web Interface (Recommended)
To launch the modern, glassmorphism UI with A/B testing capabilities:
```bash
# Install dependencies (FastAPI, Uvicorn, Llama-cpp, etc.)
pip install -r requirements.txt

# Start the local server
python app.py
# Open your browser at: http://localhost:3141
```

#### 2. Terminal (CLI) Usage
```bash
# Analyze a file (Downloads Qwen 1.5B by default)
python cli.py qa_examples/bad_auth.py

# Full intelligent analysis with the 7B model
python cli.py qa_examples/bad_auth.py -m bartowski/Qwen2.5-7B-Instruct-GGUF:Qwen2.5-7B-Instruct-Q4_K_M.gguf
```
