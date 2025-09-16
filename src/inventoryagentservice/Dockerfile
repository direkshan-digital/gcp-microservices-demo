FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY inventory_agent_service.py .

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8080

# Run the application
CMD ["python", "inventory_agent_service.py"]