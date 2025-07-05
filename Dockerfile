FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p images output temp_spreads

# Make shell scripts executable
RUN chmod +x *.sh

# Expose port
EXPOSE 4200

# Set environment variables
ENV FLASK_APP=web_interface.py
ENV FLASK_ENV=production

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4200/ || exit 1

# Make startup scripts executable
RUN chmod +x start_enhanced_web.sh start_container.sh

# Start the application using the container-optimized startup script
CMD ["./start_container.sh"] 