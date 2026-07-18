import pytest
import json
from unittest.mock import patch, MagicMock
from core.inference import CustomInferenceLayer
from core.engine import MaxwellEngine
from core.errors import TokenizationError

@patch("core.inference.Llama")
def test_tokenization_error_fail_explicit(mock_llama):
    # Mocking the Llama model so we don't load gigabytes of weights for a unit test
    mock_instance = MagicMock()
    mock_llama.return_value = mock_instance
    
    # We simulate a case where tokenization returns less than 2 tokens
    mock_instance.tokenize.return_value = [1]
    
    inference = CustomInferenceLayer(model_path="dummy_path")
    
    with pytest.raises(TokenizationError) as exc_info:
        inference.calculate_surprisal("a")
        
    assert "Token list is empty or too short." in str(exc_info.value)

@patch("core.inference.Llama")
def test_engine_returns_structured_error_json(mock_llama):
    mock_instance = MagicMock()
    mock_llama.return_value = mock_instance
    mock_instance.tokenize.return_value = [1] # This will trigger TokenizationError
    
    engine = MaxwellEngine(model_path="dummy_path")
    
    # analyze method catches MaxwellError and returns structured JSON
    result_str = engine.analyze("a", use_fractal_router=False)
    result_json = json.loads(result_str)
    
    assert result_json.get("status") == "error"
    assert "error" in result_json
    assert result_json["error"]["code"] == "TokenizationError"

@patch("core.inference.Llama")
def test_metrics_separation(mock_llama):
    mock_instance = MagicMock()
    mock_llama.return_value = mock_instance
    # Simulate a successful logprob extraction
    mock_instance.tokenize.return_value = [0, 1, 2]
    import numpy as np
    mock_instance._scores = np.array([
        [0.1, 0.9, 0.0],
        [0.2, 0.1, 0.7]
    ], dtype=np.single)
    
    # Simulate the LLM chat completion
    mock_instance.create_chat_completion.return_value = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "fraktal_boyut": "Test Boyut",
                    "catallanma_uyarisi": {"mevcut": True, "baglam_farki_skoru": 0.8},
                    "termodinamik_oneri": "Test Öneri"
                })
            }
        }]
    }
    
    engine = MaxwellEngine(model_path="dummy_path")
    result_str = engine.analyze("dummy code", use_fractal_router=False)
    result_json = json.loads(result_str)
    print("DEBUG TEST RESULT:", result_json)
    
    assert "metrics" in result_json
    assert "global_surprisal" in result_json["metrics"]
    assert "analysis" in result_json
    assert "kritiklik_skoru" not in result_json["analysis"] # Enforces separation
    assert result_json["analysis"]["fraktal_boyut"] == "Test Boyut"
