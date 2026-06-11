from app.security.headers import SECURITY_HEADERS, get_security_headers_array

def test_security_headers_keys():
    # Verify core HTTP security headers are present
    required_keys = {
        "Content-Security-Policy",
        "Strict-Transport-Security",
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Referrer-Policy",
        "Permissions-Policy"
    }
    for key in required_keys:
        assert key in SECURITY_HEADERS
        assert SECURITY_HEADERS[key] != ""

def test_security_headers_values():
    # Verify strict policies are applied
    assert SECURITY_HEADERS["X-Frame-Options"] == "DENY"
    assert SECURITY_HEADERS["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in SECURITY_HEADERS["Content-Security-Policy"]
    assert "preload" in SECURITY_HEADERS["Strict-Transport-Security"]
    assert "camera=()" in SECURITY_HEADERS["Permissions-Policy"]

def test_get_security_headers_array():
    arr = get_security_headers_array()
    assert isinstance(arr, list)
    assert len(arr) == len(SECURITY_HEADERS)
    
    # Ensure it returns tuples of [key, value]
    for item in arr:
        assert isinstance(item, tuple)
        assert len(item) == 2
        key, val = item
        assert isinstance(key, str)
        assert isinstance(val, str)
        assert SECURITY_HEADERS[key] == val
