SECURITY_HEADERS = {
    # Content-Security-Policy: Prevent cross-site scripting (XSS) and code injection.
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    ),
    # Strict-Transport-Security (HSTS): Force HTTP connections to HTTPS.
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    # X-Frame-Options: Protect against Clickjacking attacks.
    "X-Frame-Options": "DENY",
    # X-Content-Type-Options: Disable MIME sniffing.
    "X-Content-Type-Options": "nosniff",
    # Referrer-Policy: Control what referrer information is sent.
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Permissions-Policy: Restrict access to sensitive browser features.
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

def get_security_headers_array():
    """
    Returns security headers as a list of [key, value] tuples.
    Useful for middleware configurations or hosting platforms.
    """
    return list(SECURITY_HEADERS.items())
