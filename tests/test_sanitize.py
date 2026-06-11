from app.security.sanitize import sanitize_input, escape_html, redact_secrets

def test_sanitize_input_normal():
    # Happy path
    assert sanitize_input("hello world") == "hello world"

def test_sanitize_input_none():
    # None input
    assert sanitize_input(None) == ""

def test_sanitize_input_non_string():
    # Non-string input
    assert sanitize_input(12345) == "12345"

def test_sanitize_input_control_characters():
    # Control character removal (U+0000 - U+001F)
    # except tab and newline
    dirty = "line1\nline2\x07\x00\x1f"
    clean = "line1\nline2"
    assert sanitize_input(dirty) == clean

def test_sanitize_input_zero_width_chars():
    # Zero-width spaces U+200B and U+FEFF removal
    dirty = "hello\u200bworld\ufeff"
    clean = "helloworld"
    assert sanitize_input(dirty) == clean

def test_sanitize_input_bidi_overrides():
    # Bidirectional characters removal
    dirty = "he\u202dllo\u202ewor\u202cld"
    clean = "helloworld"
    assert sanitize_input(dirty) == clean

def test_sanitize_input_unicode_normalization():
    # NFC normalization (e.g. combined e + acute accent)
    raw = "e\u0301" # decomposed e + acute
    normalized = "\u00e9" # combined e acute
    assert sanitize_input(raw) == normalized

def test_escape_html_normal():
    # Normal input
    assert escape_html("safe text") == "safe text"

def test_escape_html_none():
    assert escape_html(None) == ""

def test_escape_html_non_string():
    assert escape_html(543.21) == "543.21"

def test_escape_html_special_chars():
    # Special HTML characters
    assert escape_html("<script>alert(1);</script>") == "&lt;script&gt;alert(1);&lt;/script&gt;"
    assert escape_html('hello "world" & \'john\'') == "hello &quot;world&quot; &amp; &#x27;john&#x27;"

def test_redact_secrets_none():
    assert redact_secrets(None) == ""

def test_redact_secrets_non_string():
    assert redact_secrets(9876) == "9876"

def test_redact_secrets_openai_key():
    # OpenAI sk-... key pattern
    log = "Connecting with API key sk-abcdef1234567890abcdef1234567890"
    redacted = "Connecting with API key [REDACTED_SECRET_KEY]"
    assert redact_secrets(log) == redacted

def test_redact_secrets_bearer_token():
    # Bearer tokens
    log = "Authorization: Bearer abc123XYZ-abc_123"
    redacted = "Authorization: Bearer [REDACTED_TOKEN]"
    assert redact_secrets(log) == redacted

def test_redact_secrets_email():
    # Email patterns
    log = "Contact info: anish@vit.edu or standard@test.org"
    redacted = "Contact info: [REDACTED_EMAIL] or [REDACTED_EMAIL]"
    assert redact_secrets(log) == redacted

def test_redact_secrets_generic_keywords():
    # API key or Secret assignment patterns
    assert redact_secrets("my_api_key:secret_key_val") == "my_api_key=[REDACTED]"
    assert redact_secrets("db_password = mypwd123") == "db_password=[REDACTED]"
    assert redact_secrets("Token: abc-xyz") == "Token=[REDACTED]"
