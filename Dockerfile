# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by pyppeteer
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libgbm1 \
    libxshmfence1 \
    libglu1-mesa \
    wget \
    ca-certificates \
    libnss3 \
    fonts-liberation \
    libappindicator3-1 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Expose the port your app will run on
EXPOSE 8080

# RUN python3 -c "from pyppeteer import chromium_downloader; chromium_downloader.download_chromium()"

# Use Gunicorn as the WSGI server with async workers
CMD ["gunicorn", "-w", "1", "-k", "gthread", "--threads", "1", "-b", "0.0.0.0:8080", "Main:app"]

