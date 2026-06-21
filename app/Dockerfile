# Stage 1: Build Frontend
FROM node:20-alpine AS build-stage
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dan install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code backend
COPY . .

# Copy built frontend
COPY --from=build-stage /app/frontend/dist /app/static

# Port
EXPOSE 8080

# Jalankan aplikasi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
