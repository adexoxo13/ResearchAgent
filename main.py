"""
Research Portal - Main Application Entry Point

Implements the web interface and REST API endpoints with authentication flow.
"""

# Core framework imports
from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Api  # For RESTful endpoint management

# Security components
from auth.auth import basic_auth, token_auth, generate_token, verify_token

# API endpoint handlers
from api.research_api import Research, Download

# Environment configuration
import os

# Initialize Flask application
app = Flask(__name__)
api = Api(app)  # Initialize REST API


@app.route("/")
def home():
    """
    Main application entry point with token validation

    Flow:
    1. Check for token in URL parameters
    2. Validate token authenticity
    3. Redirect to app or login based on validity

    Security Features:
    - Token required for access
    - Server-side token validation
    - Automatic redirect on invalid sessions
    """
    token = request.args.get("token")

    # First layer: Token presence check
    if not token:
        return redirect("/login")

    # Second layer: Token validation
    user = verify_token(token)
    if not user:
        return redirect("/login")

    return render_template("app.html", token=token)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Authentication gateway with dual functionality:
    - GET: Display login form
    - POST: Process credentials and issue token

    Security Considerations:
    - Plain password comparison (not recommended for production)
    - Token generation on successful auth
    - Error handling for invalid credentials
    """
    if request.method == "POST":
        # Retrieve form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Environment-based credential validation
        valid_username = os.environ.get("BASIC_AUTH_USERNAME")
        valid_password = os.environ.get("BASIC_AUTH_PASSWORD")

        if username == valid_username and password == valid_password:
            # Generate time-limited access token
            token = generate_token(username)
            return redirect(f"/?token={token}")

        # Failed authentication
        return render_template("login.html", error="Invalid credentials")

    # GET request - show login form
    return render_template("login.html")


# Register API endpoints
api.add_resource(Research, "/research")  # Research processing endpoint
api.add_resource(Download, "/download/<filename>")  # File download endpoint

if __name__ == "__main__":
    # Server configuration
    app.run(host="0.0.0.0", port=5000)  # Accessible from any network interface

"""
Security Architecture Overview:

1. Authentication Flow:
   - Login Page → Credential Validation → Token Generation → App Access
   - Token persists in client-side session storage

2. Defense Layers:
   - Token presence check (client-side)
   - Cryptographic token validation (server-side)
   - Environment-based credentials

3. Session Management:
   - JWT tokens with 24h expiration
   - No server-side session storage
   - Automatic token invalidation on expiry

Critical Security Notes:

1. Password Handling:
   - Current implementation compares plaintext passwords
   - UNSAFE FOR PRODUCTION - should use password hashing

2. Environment Variables:
   - Requires proper configuration:
     export BASIC_AUTH_USERNAME=admin
     export BASIC_AUTH_PASSWORD=securepassword
     export SECRET_KEY=complex-secret-key

3. HTTPS Requirement:
   - Always use in production to protect tokens
   - Configure reverse proxy with SSL termination

4. Token Storage:
   - Client-side sessionStorage used
   - Consider httpOnly cookies for enhanced security

Production Recommendations:

1. Add rate limiting for API endpoints
2. Implement password hashing with bcrypt
3. Add CSRF protection for forms
4. Enable CORS policies for API endpoints
5. Add request validation middleware
6. Implement proper logging
7. Set up monitoring/alerting
"""
