class MaxwellError(Exception):
    """Base class for all Maxwell Engine exceptions."""
    pass

class TokenizationError(MaxwellError):
    """Raised when tokenization fails."""
    pass

class SurprisalCalculationError(MaxwellError):
    """Raised when Surprisal (Logprob) math calculation fails."""
    pass

class InferenceError(MaxwellError):
    """Raised when LLM inference generation fails."""
    pass
