# Gunicorn configuration for CEWE Photo Book Fetcher

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:4200"
backlog = 2048

# Worker processes
workers = 1  # Start with single worker for Flask-SocketIO
worker_class = "gevent"  # Use gevent instead of eventlet for better compatibility
worker_connections = 1000
timeout = 300
keepalive = 2

# Gevent-specific configuration for WebSocket support
def when_ready(server):
    """Configure gevent-websocket when server is ready"""
    from gevent import monkey
    monkey.patch_all()

def post_fork(server, worker):
    """Configure worker after fork"""
    from gevent import monkey
    monkey.patch_all()

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "cewe-photobook-fetcher"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL is handled by nginx reverse proxy, not gunicorn
# Gunicorn serves HTTP only, nginx handles SSL termination

# Environment variables for Flask
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=1',
]

# Worker temp directory
worker_tmp_dir = '/dev/shm'

# Preload app for better performance
preload_app = True 