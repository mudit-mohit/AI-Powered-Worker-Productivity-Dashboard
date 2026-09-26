# Multi-stage build for production deployment
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json ./
RUN npm install

# Copy frontend source
COPY frontend/src ./src
COPY frontend/public ./public

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend/app.py ./backend/
COPY backend/seed_sample_data.py ./backend/

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Expose port
EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Serve both frontend and backend from Flask
CMD cd backend && python app.py
