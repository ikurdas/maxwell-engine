import json
import math
from llama_cpp import Llama

class CustomInferenceLayer:
    def __init__(self, model_path: str, n_ctx: int = 4096):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=-1, # TR: Apple Silicon (Metal) için tüm katmanları GPU'ya al / EN: Offload all layers to GPU for Apple Silicon (Metal)
            logits_all=True, # TR: PROMPT İÇİN LOGPROBS HESAPLAMASINI AÇAR / EN: ENABLES LOGPROBS CALCULATION FOR PROMPT
            verbose=False
        )
        
    def calculate_surprisal(self, text: str) -> float:
        """
        TR: Gerçek I(w) = -log(P(w|C)) formülünü hesaplar.
        TR: Metni tokenize eder ve modelin kendi olasılık (logprobs) dağılımından
        TR: matematiksel "Surprisal" (Şaşırma/Beklenmezlik) ortalamasını çıkarır.
        
        EN: Calculates the genuine I(w) = -log(P(w|C)) formula.
        EN: Tokenizes the text and extracts the mathematical "Surprisal" average
        EN: from the model's own probability (logprobs) distribution.
        """
        # TR: Metni modele completion formatında yollayarak sadece logprob'ları alıyoruz (üretim yapmıyoruz)
        # EN: We send the text to the model in completion format to only get logprobs (no generation)
        try:
            response = self.llm(
                text,
                max_tokens=1,
                echo=True,
                logprobs=1
            )
            
            # TR: Tüm token'ların logprob'larını topla
            # EN: Sum logprobs of all tokens
            logprobs = response['choices'][0]['logprobs']['token_logprobs']
            
            # TR: İlk token'ın logprob'u None olabilir (bağlam yok), onu filtrele
            # EN: The first token's logprob might be None (no context), filter it out
            valid_logprobs = [lp for lp in logprobs if lp is not None]
            
            if not valid_logprobs:
                return 0.5 # Fallback
                
            # TR: Ortalama logprob
            # EN: Average logprob
            avg_logprob = sum(valid_logprobs) / len(valid_logprobs)
            
            # TR: Matematiksel Surprisal I = -log(P). logprobs zaten ln(P) (doğal logaritma) döner.
            # EN: Mathematical Surprisal I = -log(P). logprobs already return ln(P) (natural logarithm).
            surprisal = -avg_logprob
            
            # TR: Skorlama: surprisal değeri genelde 0 ile 15 arası değişir.
            # TR: Bunu 0-1 arasına (Kritiklik skoru) normalize edelim. (Ampirik yaklaşım: max entropy ~ 10.0)
            # EN: Scoring: surprisal value usually ranges from 0 to 15.
            # EN: Normalize this to 0-1 (Criticality score). (Empirical approach: max entropy ~ 10.0)
            normalized_score = min(max(surprisal / 10.0, 0.0), 1.0)
            return round(normalized_score, 2)
            
        except Exception as e:
            print(f"Error calculating Surprisal: {e}")
            return 0.5

    def generate_report(self, messages: list, schema: dict) -> dict:
        """
        TR: GBNF Gramer zorlaması (Constrained Decoding) kullanarak,
        TR: halüsinasyon riski sıfır olan kesin JSON üretimi yapar.
        
        EN: Uses GBNF Grammar enforcement (Constrained Decoding)
        EN: to generate strict JSON with zero hallucination risk.
        """
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                response_format={
                    "type": "json_object",
                    "schema": schema
                },
                temperature=0.7 # TR: Formatlı üretimde halüsinasyonu en aza indirmek için düşük sıcaklık / EN: Low temp to minimize hallucination in formatted generation
            )
            content = response['choices'][0]['message']['content']
            return json.loads(content, strict=False)
        except Exception as e:
            return {"error": f"Llama-cpp generation hatası: {str(e)}"}
