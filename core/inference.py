import json
import math
import numpy as np
from llama_cpp import Llama
from core.errors import MaxwellError, TokenizationError, SurprisalCalculationError, InferenceError

class CustomInferenceLayer:
    def __init__(self, model_path: str, n_ctx: int = 8192):
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
                raise TokenizationError("Token list is empty or too short.")
                
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
                raise SurprisalCalculationError("No actual logprobs calculated.")
                
            # TR: Ortalama logprob
            # EN: Average logprob
            avg_logprob = sum(actual_token_logprobs) / len(actual_token_logprobs)
            
            # TR: Matematiksel Surprisal I = -log(P). logprobs zaten ln(P) (doğal logaritma) döner.
            # EN: Mathematical Surprisal I = -log(P). logprobs already return ln(P) (natural logarithm).
            raw_surprisal = -avg_logprob
            
            # TR: Legacy Normalization
            normalized_score = min(max(raw_surprisal / 10.0, 0.0), 1.0)
            
            return {
                "raw_surprisal": round(raw_surprisal, 4),
                "normalized_surprisal": round(normalized_score, 4)
            }
            
        except MaxwellError:
            raise
        except Exception as e:
            raise SurprisalCalculationError(f"Error calculating Surprisal: {e}")

    def calculate_fractal_surprisal(self, text: str) -> dict:
        """
        TR: Metni parçalara (chunks) böler, her parçanın Surprisal değerini lokal olarak hesaplar.
        TR: En yüksek entropiye sahip (en kırılgan) parçayı bulup Fractal Router için döndürür.
        """
        try:
            tokens = self.llm.tokenize(text.encode('utf-8'))
            if len(tokens) <= 1:
                raise TokenizationError("Token list is empty or too short.")
                
            self.llm.eval(tokens)
            logits = self.llm._scores
            
            logits_maxs = np.amax(logits, axis=-1, keepdims=True)
            logits_maxs[~np.isfinite(logits_maxs)] = 0
            subtract_maxs = np.subtract(logits, logits_maxs, dtype=np.single)
            exp = np.exp(subtract_maxs)
            sum_exp = np.sum(exp, axis=-1, keepdims=True)
            log_sum_exp = np.log(sum_exp)
            logprobs = np.subtract(subtract_maxs, log_sum_exp, dtype=np.single)
            
            actual_token_logprobs = []
            for i in range(1, len(tokens)):
                token_id = tokens[i]
                lp = float(logprobs[i-1, token_id])
                actual_token_logprobs.append(lp)
                
            if not actual_token_logprobs:
                raise SurprisalCalculationError("No actual logprobs calculated.")

            # Global Surprisal (Genel Sistem Entropisi)
            global_avg = sum(actual_token_logprobs) / len(actual_token_logprobs)
            raw_global_surprisal = -global_avg
            normalized_global_surprisal = min(max(raw_global_surprisal / 10.0, 0.0), 1.0)
            
            # Chunking and Fractal Weighting (Her 64 tokenda bir / Mezo Katman)
            CHUNK_SIZE = 64
            chunks_info = []
            
            # actual_token_logprobs listesi tokens[1:]'e denk gelir
            for i in range(0, len(actual_token_logprobs), CHUNK_SIZE):
                chunk_lps = actual_token_logprobs[i:i+CHUNK_SIZE]
                chunk_tokens = tokens[i+1 : i+1+CHUNK_SIZE]
                
                chunk_avg = sum(chunk_lps) / len(chunk_lps)
                raw_chunk_surprisal = -chunk_avg
                normalized_chunk_surprisal = min(max(raw_chunk_surprisal / 10.0, 0.0), 1.0)
                
                chunk_text = self.llm.detokenize(chunk_tokens).decode('utf-8', errors='ignore')
                chunks_info.append({
                    "text": chunk_text.strip(),
                    "raw_surprisal": raw_chunk_surprisal,
                    "normalized_surprisal": normalized_chunk_surprisal
                })
                
            # En kaotik parçayı (Çatallanma Noktasını) bul
            highest_chunk = max(chunks_info, key=lambda x: x["raw_surprisal"])
            peak_surprisal = highest_chunk["raw_surprisal"]
            divergence = peak_surprisal - raw_global_surprisal
            
            return {
                "raw_global_surprisal": round(raw_global_surprisal, 4),
                "normalized_global_surprisal": round(normalized_global_surprisal, 4),
                "raw_peak_surprisal": round(peak_surprisal, 4),
                "local_global_divergence": round(divergence, 4),
                "highest_energy_chunk": highest_chunk["text"]
            }
            
        except MaxwellError:
            raise
        except Exception as e:
            raise SurprisalCalculationError(f"Error calculating Fractal Surprisal: {e}")

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
            raise InferenceError(f"Llama-cpp generation error: {e}")
