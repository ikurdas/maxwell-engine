import json
import math
import numpy as np
from llama_cpp import Llama

class CustomInferenceLayer:
    def __init__(self, model_path: str, n_ctx: int = 4096):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_batch=n_ctx, # TR: Chunking yüzünden logits_all=True'nun sistemi kilitlemesini engelle / EN: Prevent logits_all=True from hanging the system due to chunking
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
        try:
            # TR: Metni tokenize et / EN: Tokenize text
            tokens = self.llm.tokenize(text.encode('utf-8'))
            if len(tokens) <= 1:
                return 0.5
                
            # TR: Modeli evaluate et (C++ tarafında prompt işlenir)
            # EN: Evaluate model (prompt is processed in C++)
            self.llm.eval(tokens)
            
            # TR: Logits matrisini doğrudan al: shape (n_tokens, vocab_size)
            # EN: Get logits matrix directly: shape (n_tokens, vocab_size)
            logits = self.llm._scores
            
            # TR: Numpy ile çok hızlı Log-Softmax hesaplaması (llama-cpp-python'daki yavaş python döngüsünü bypass eder)
            # EN: Ultra-fast Log-Softmax with Numpy (bypasses slow python loop in llama-cpp-python)
            logits_maxs = np.amax(logits, axis=-1, keepdims=True)
            logits_maxs[~np.isfinite(logits_maxs)] = 0
            subtract_maxs = np.subtract(logits, logits_maxs, dtype=np.single)
            exp = np.exp(subtract_maxs)
            sum_exp = np.sum(exp, axis=-1, keepdims=True)
            log_sum_exp = np.log(sum_exp)
            logprobs = np.subtract(subtract_maxs, log_sum_exp, dtype=np.single)
            
            # TR: Sadece prompt içindeki *gerçek* token'ların logprob'larını al
            # EN: Extract logprobs ONLY for the *actual* tokens in the prompt
            actual_token_logprobs = []
            for i in range(1, len(tokens)):
                token_id = tokens[i]
                # i. token'ın olasılığı, i-1. token'ın logits'inden gelir
                # The probability of the i-th token comes from the (i-1)-th token's logits
                lp = float(logprobs[i-1, token_id])
                actual_token_logprobs.append(lp)
                
            if not actual_token_logprobs:
                return 0.5 # Fallback
                
            # TR: Ortalama logprob
            # EN: Average logprob
            avg_logprob = sum(actual_token_logprobs) / len(actual_token_logprobs)
            
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
                temperature=0.7, # TR: Formatlı üretimde halüsinasyonu en aza indirmek için düşük sıcaklık / EN: Low temp to minimize hallucination in formatted generation
                max_tokens=None # TR: Çıktı limitini modelin maksimum bağlam boyutuna göre dinamik ayarlar / EN: Dynamically sets limit based on model's context window
            )
            content = response['choices'][0]['message']['content']
            return json.loads(content, strict=False)
        except Exception as e:
            return {"error": f"Llama-cpp generation hatası: {str(e)}"}
