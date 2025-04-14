"""
Authentication System for Research Portal

Implements dual authentication layers:
1. Basic Authentication - For initial login
2. JWT Token Authentication - For API endpoints
"""

# Security components
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import check_password_hash
import jwt  # JSON Web Token implementation
from datetime import datetime, timedelta
import os

# Initialize authentication handlers
basic_auth = HTTPBasicAuth()  # For username/password login
token_auth = HTTPTokenAuth(scheme="Bearer")  # For JWT protected endpoints

# Security Configuration
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "super-secret"
)  # Always override in production!

# User Credentials Storage (Single user setup)
users = {
    # Stores username: password_hash pairs
    os.environ.get("BASIC_AUTH_USERNAME"): os.environ.get("BASIC_AUTH_PASSWORD_HASH")
}


@basic_auth.verify_password
def verify_password(username, password):
    """
    Basic Authentication Validator

    Parameters:
    - username: Submitted username
    - password: Submitted plaintext password

    Process:
    1. Retrieve stored hash for username
    2. Verify against provided password
    3. Return username if valid

    Security Note:
    - Passwords should be stored as hashes, never plaintext
    - Uses Werkzeug's secure password hashing
    """
    stored_hash = users.get(username)
    if stored_hash and check_password_hash(stored_hash, password):
        return username  # Authentication successful
    return None  # Authentication failed


def generate_token(username):
    """
    JWT Token Generator

    Parameters:
    - username: Authenticated username

    Returns:
    - Signed JWT token with 24h expiration

    Token Structure:
    - sub: Subject (username)
    - iat: Issued at time (UTC)
    - exp: Expiration time (UTC + 24h)

    Security Features:
    - HS256 algorithm for signing
    - Short expiration time
    - Server-side secret key
    """
    return jwt.encode(
        {
            "sub": username,  # Subject identifier
            "iat": datetime.utcnow(),  # Issued at
            "exp": datetime.utcnow() + timedelta(hours=24),  # Expiration
        },
        SECRET_KEY,  # Never expose this!
        algorithm="HS256",  # HMAC + SHA256
    )


@token_auth.verify_token
def verify_token(token):
    """
    JWT Token Validator

    Parameters:
    - token: JWT from Authorization header

    Returns:
    - username if valid token, None otherwise

    Validation Process:
    1. Decode token using secret key
    2. Verify cryptographic signature
    3. Check expiration time
    4. Return subject (username) if valid

    Security Features:
    - Automatic expiration checking
    - Signature verification
    - Algorithm enforcement
    """
    try:
        data = jwt.decode(
            token, SECRET_KEY, algorithms=["HS256"]  # Algorithm allowlist
        )
        return data["sub"]  # Return username
    except jwt.PyJWTError as e:
        # Handle all JWT exceptions (expired, invalid, etc.)
        print(f"Token verification failed: {str(e)}")
        return None


"""
Security Best Practices:

1. Secret Management:
   - Store SECRET_KEY in environment variables
   - Never commit secrets to version control
   - Rotate keys regularly

2. Password Handling:
   - Always hash passwords with salt
   - Use strong hashing algorithms (bcrypt recommended)
   - Never store plaintext passwords

3. Token Security:
   - Keep tokens short-lived
   - Use HTTPS in production
   - Store tokens securely on client-side

4. User Management:
   - Implement lockouts after failed attempts
   - Support multiple users in production
   - Consider OAuth2 for third-party auth

Usage Flow:
1. User logs in with /login endpoint (Basic Auth)
2. Server returns JWT token
3. Client includes token in Authorization header
4. Protected endpoints verify token validity
"""
