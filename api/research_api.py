"""
Flask REST API Endpoints for AI Research System

Handles research requests and file downloads through RESTful endpoints
"""

# Core web framework imports
from flask_restful import Resource  # Base class for REST resources
from flask import request, jsonify, send_from_directory  # Request handling utilities
import markdown  # Markdown to HTML conversion
import time  # Processing time measurement
import os  # File system operations

# Authentication and AI components
from auth.auth import token_auth  # JWT authentication decorator
from utils.agent_setup import agent_executor, parser  # AI research components


class Research(Resource):
    # method_decorators = [token_auth.login_required]  # Auth control (currently disabled)

    def post(self):
        """
        Handle research requests POST endpoint

        Flow:
        1. Validate input query
        2. Execute research agent pipeline
        3. Format and persist results
        4. Return structured response

        Security: Requires JWT authentication (currently disabled)
        """
        data = request.json
        query = data.get("query")

        # Input validation
        if not query:
            return {"error": "No query provided"}, 400  # HTTP 400 Bad Request

        try:
            start_time = time.time()  # Begin performance tracking

            # Execute AI research pipeline
            result = agent_executor.invoke(
                {
                    "query": query,
                    "chat_history": [],  # Context storage (empty for new sessions)
                    "agent_scratchpad": [],  # Agent's working memory
                }
            )

            # Parse structured output from LLM response
            structured_response = parser.parse(result.get("output"))

            # Convert markdown content to HTML for web display
            html_summary = markdown.markdown(
                structured_response.summary,
                extensions=["fenced_code", "tables"],  # Support code blocks and tables
            )

            # Generate filename with sanitized topic name
            filename = f"research_{structured_response.topic.replace(' ', '_')}.md"
            # Ensure outputs directory exists (add this before file operations)
            os.makedirs("outputs", exist_ok=True)  # <-- Add this line

            # Persist full report to filesystem
            with open(f"outputs/{filename}", "w") as f:
                f.write(
                    f"# {structured_response.topic}\n\n{structured_response.summary}"
                )

            # Construct API response
            return {
                "topic": structured_response.topic, 
                # Research topic title
                "summary": html_summary,  
                # HTML-formatted content
                "sources": structured_response.sources, 
                # Reference URLs
                "tools": structured_response.tools_used,  
                # AI tools utilized
                "download_link": f"/download/{filename}",  
                # File access endpoint
                "processing_time": round(
                    time.time() - start_time, 2
                ),  # Duration in seconds
            }

        except Exception as e:
            # Error handling and logging
            print("Error in /research:", e)  # Server-side logging
            return {
                "error": str(e),  # Developer-facing message
                "details": "Check server logs for more information",  
                # User guidance
            }, 500  # HTTP 500 Internal Server Error


class Download(Resource):
    # Security Note: Authentication disabled for demo purposes
    # Production systems should re-enable auth:
    # method_decorators = [token_auth.login_required]

    def get(self, filename):
        """
        Secure file download endpoint

        Parameters:
        - filename: Sanitized filename from research output

        Security Considerations:
        - Validate filename format
        - Restrict to output directory
        - Enable authentication in production
        """
        # Configure secure download path
        downloads_folder = os.path.join(os.getcwd(), "outputs") 
        # Isolate files

        # Safe file serving with Flask's send_from_directory
        return send_from_directory(
            directory=downloads_folder,  # Restricted base path
            path=filename,  # Sanitized filename
            as_attachment=True,  # Force download dialog
        )


"""
API Security Notes:
1. Authentication: Currently disabled (enable method_decorators for JWT)
2. Input Validation:
   - Research endpoint validates query exists
   - Download endpoint needs filename sanitization
3. File Security:
   - Downloads restricted to 'outputs' directory
   - Never accept user-provided paths
4. Error Handling:
   - Generic error messages to clients
   - Detailed logging server-side
5. Rate Limiting: Should be added in production

Usage Patterns:
- POST /research : Initiate research (JSON payload with "query")
- GET /download/<filename> : Retrieve generated reports
"""
