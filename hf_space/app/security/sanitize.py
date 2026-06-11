import re
import html
import unicodedata

def sanitize_input(raw: str) -> str:
    """
    Strips control chars (U+0000-U+001F), zero-width chars (U+200B, U+FEFF),
    and bidirectional override chars. Applies Unicode NFC normalization.
    """
    if raw is None:
        return ""
    if not isinstance(raw, str):
        raw = str(raw)
        
    # Remove control characters (except tab and newline)
    raw = "".join(ch for ch in raw if unicodedata.category(ch)[0] != "C" or ch in ("\t", "\n"))
    
    # Strip zero-width and bidirectional override characters
    # Zero-width space (U+200B), Zero-width no-break space/BOM (U+FEFF)
    # Bidirectional characters: LRO (U+202D), RLO (U+202E), PDF (U+202C), LRE (U+202A), RLE (U+202B)
    strip_chars = ["\u200b", "\ufeff", "\u202d", "\u202e", "\u202c", "\u202a", "\u202b"]
    for char in strip_chars:
        raw = raw.replace(char, "")
        
    # Apply Unicode NFC normalization
    return unicodedata.normalize("NFC", raw)

def escape_html(input_str: str) -> str:
    """
    Escapes HTML special characters (&, <, >, ", ') to prevent XSS.
    """
    if input_str is None:
        return ""
    if not isinstance(input_str, str):
        input_str = str(input_str)
    return html.escape(input_str)

def redact_secrets(input_str: str) -> str:
    """
    Redacts secret-shaped strings from log output.
    Matches: sk-..., Bearer ..., email@domain.com, and generic API key patterns.
    """
    if input_str is None:
        return ""
    if not isinstance(input_str, str):
        input_str = str(input_str)
        
    # Redact OpenAI API keys (sk-...)
    input_str = re.sub(r"sk-[a-zA-Z0-9]{32,}", "[REDACTED_SECRET_KEY]", input_str)
    
    # Redact Authorization: Bearer tokens
    input_str = re.sub(r"(?i)bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*", "Bearer [REDACTED_TOKEN]", input_str)
    
    # Redact email addresses
    input_str = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]", input_str)
    
    # Redact generic API/Secret Key patterns (e.g., API_KEY=..., SECRET=...)
    input_str = re.sub(r"(?i)(api_key|secret|password|passwd|token)\s*[:=]\s*[^\s,\'\"]+", r"\1=[REDACTED]", input_str)
    
    return input_str
