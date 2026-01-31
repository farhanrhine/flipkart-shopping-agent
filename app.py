"""
==============================================================================
FLASK APPLICATION - Flipkart Shopping Agent
==============================================================================
This is the main Flask application that serves the frontend and handles
chat requests using the RAG Agent.

STRUCTURE:
    - GET  /         : Serves the main chat interface (index.html)
    - POST /chat     : Handles chat messages and returns agent responses
    - POST /clear    : Clears chat history for a session
    - GET  /metrics  : Prometheus metrics endpoint (for monitoring)
    - GET  /health   : Health check endpoint (for Kubernetes)

MONITORING:
    - Prometheus metrics at /metrics
    - Grafana can scrape these metrics for dashboards
    - Ready for Docker and Kubernetes deployment
==============================================================================
"""

import sys
import time
from pathlib import Path

# ==============================================================================
# PATH SETUP - Ensure imports work from project root
# ==============================================================================
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, jsonify, session, Response
from src.agent.rag_agent import RAGAgent
from src.pipeline.data_ingestion import DataIngestor

# ==============================================================================
# PROMETHEUS METRICS - For monitoring with Prometheus & Grafana
# ==============================================================================
# Counter: Increments every time an event happens (e.g., requests, errors)
# Histogram: Measures distribution of values (e.g., response times)
# ==============================================================================
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Total HTTP requests counter (labeled by endpoint and method)
REQUEST_COUNT = Counter(
    'flask_request_total',                          # Metric name
    'Total HTTP requests',                          # Description
    ['endpoint', 'method', 'status']                # Labels for filtering
)

# Chat requests counter (specific to chat functionality)
CHAT_REQUEST_COUNT = Counter(
    'chat_request_total',
    'Total chat requests',
    ['status']  # success or error
)

# Response time histogram (measures how long requests take)
REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds',
    'Request latency in seconds',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]   # Time buckets
)

# Chat response time (specific to RAG agent)
CHAT_LATENCY = Histogram(
    'chat_response_latency_seconds',
    'Chat response latency in seconds',
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Active sessions gauge (current number of active chat sessions)
ACTIVE_SESSIONS = Gauge(
    'active_sessions',
    'Number of active chat sessions'
)

# Error counter
ERROR_COUNT = Counter(
    'error_total',
    'Total errors',
    ['type']  # error type/location
)


# ==============================================================================
# FLASK APP INITIALIZATION
# ==============================================================================
app = Flask(__name__)
app.secret_key = "flipkart-agent-secret-key-2026"  # Required for session management

# ==============================================================================
# GLOBAL VARIABLES - Initialize once, reuse for all requests
# ==============================================================================
# These are created once when the app starts, not on every request
ingestor = None
agent = None


def get_agent():
    """
    Get or create the RAG agent (singleton pattern).
    This ensures we only connect to AstraDB once.
    """
    global ingestor, agent
    
    if agent is None:
        print("Initializing RAG Agent...")
        ingestor = DataIngestor()
        vstore = ingestor.ingest(load_existing=True)
        agent = RAGAgent(vstore)
        print("RAG Agent ready!")
    
    return agent


# ==============================================================================
# ROUTES
# ==============================================================================

@app.route("/")
def index():
    """
    Serve the main chat interface.
    
    Returns:
        HTML: The index.html template
    """
    # Track request
    REQUEST_COUNT.labels(endpoint='/', method='GET', status='200').inc()
    
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat messages from the user.
    
    Request JSON:
        {
            "message": "user's question here"
        }
    
    Response JSON:
        {
            "response": "agent's answer here",
            "success": true/false
        }
    """
    # Start timing the request
    start_time = time.time()
    
    try:
        # Get the user's message from the request
        data = request.get_json()
        user_message = data.get("message", "").strip()
        
        # Validate the message
        if not user_message:
            REQUEST_COUNT.labels(endpoint='/chat', method='POST', status='400').inc()
            return jsonify({
                "response": "Please enter a message.",
                "success": False
            })
        
        # Get session ID (unique per browser session)
        if "session_id" not in session:
            import uuid
            session["session_id"] = str(uuid.uuid4())
            # Increment active sessions when new session created
            ACTIVE_SESSIONS.inc()
        
        session_id = session["session_id"]
        
        # Get response from the RAG agent
        rag_agent = get_agent()
        response = rag_agent.invoke(user_message, session_id)
        
        # Record metrics
        latency = time.time() - start_time
        CHAT_LATENCY.observe(latency)
        REQUEST_LATENCY.labels(endpoint='/chat').observe(latency)
        REQUEST_COUNT.labels(endpoint='/chat', method='POST', status='200').inc()
        CHAT_REQUEST_COUNT.labels(status='success').inc()
        
        return jsonify({
            "response": response,
            "success": True
        })
        
    except Exception as e:
        # Record error metrics
        latency = time.time() - start_time
        CHAT_LATENCY.observe(latency)
        REQUEST_COUNT.labels(endpoint='/chat', method='POST', status='500').inc()
        CHAT_REQUEST_COUNT.labels(status='error').inc()
        ERROR_COUNT.labels(type='chat_error').inc()
        
        print(f"Error in chat: {e}")
        return jsonify({
            "response": f"Sorry, an error occurred: {str(e)}",
            "success": False
        })


@app.route("/clear", methods=["POST"])
def clear_history():
    """
    Clear the chat history for the current session.
    
    Response JSON:
        {
            "message": "Chat history cleared",
            "success": true
        }
    """
    try:
        # Reset session ID to start fresh
        if "session_id" in session:
            session.pop("session_id")
            # Decrement active sessions when session cleared
            ACTIVE_SESSIONS.dec()
        
        REQUEST_COUNT.labels(endpoint='/clear', method='POST', status='200').inc()
        
        return jsonify({
            "message": "Chat history cleared",
            "success": True
        })
        
    except Exception as e:
        REQUEST_COUNT.labels(endpoint='/clear', method='POST', status='500').inc()
        ERROR_COUNT.labels(type='clear_error').inc()
        
        return jsonify({
            "message": f"Error: {str(e)}",
            "success": False
        })


# ==============================================================================
# PROMETHEUS METRICS ENDPOINT
# ==============================================================================
# This endpoint exposes all metrics for Prometheus to scrape
# Prometheus will call GET /metrics periodically (e.g., every 15s)
# ==============================================================================

@app.route("/metrics")
def metrics():
    """
    Expose Prometheus metrics.
    
    Returns:
        Text: Prometheus-formatted metrics
        
    Usage:
        - Configure Prometheus to scrape http://your-app:5000/metrics
        - Metrics will appear in Grafana dashboards
    """
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# ==============================================================================
# HEALTH CHECK ENDPOINT - For Kubernetes
# ==============================================================================
# Kubernetes uses this to check if the pod is healthy
# - livenessProbe: Is the app alive?
# - readinessProbe: Is the app ready to receive traffic?
# ==============================================================================

@app.route("/health")
def health():
    """
    Health check endpoint for Kubernetes.
    
    Returns:
        JSON: {"status": "healthy"} with 200 OK
        
    Usage in Kubernetes:
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
    """
    return jsonify({
        "status": "healthy",
        "service": "flipkart-shopping-agent"
    })


# ==============================================================================
# RUN THE APP
# ==============================================================================
# This block only runs when you execute: python app.py
# It does NOT run when using a production server like gunicorn

if __name__ == "__main__":
    # Initialize the agent before starting the server
    print("Starting Flipkart Shopping Agent...")
    get_agent()
    
    # Run Flask
    # In production (Docker/K8s), this block usually doesn't run if using Gunicorn
    # But if running via 'python app.py', we should check the environment
    import os
    is_debug = os.getenv("FLASK_ENV") == "development"
    
    app.run(
        host="0.0.0.0",  
        port=5000,        
        debug=is_debug  # Only true if FLASK_ENV=development
    )
