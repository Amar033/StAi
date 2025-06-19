FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Expose the port that Railway will assign
EXPOSE $PORT

# Start the FastAPI application with Railway's PORT variable
CMD uvicorn main:app --host 0.0.0.0 --port $PORT