# Document Converter Service

A simple document conversion service built with FastAPI and LibreOffice for Render.com.

## Features

- Convert DOC to DOCX
- Convert DOC to PDF
- Convert DOCX to PDF
- Simple REST API
- Fast deployment on Render.com

## Deployment on Render.com

### Option 1: One-Click Deployment

1. Fork this repository to your GitHub account
2. Log in to [Render.com](https://render.com)
3. Click "New Web Service"
4. Find and select your forked repository
5. Render will automatically detect the `render.yaml` configuration
6. Click "Create Web Service"

### Option 2: Manual Configuration

1. Log in to [Render.com](https://render.com)
2. Click "New Web Service"
3. Connect your GitHub repository
4. Configure with these settings:
   - **Environment**: Docker
   - **Name**: doc-converter (or your preferred name)
   - **Plan**: Starter
   - **Branch**: main (or your default branch)
   - Everything else can remain as default

5. Click "Create Web Service"

## Usage

### Converting Documents

```bash
# Convert DOC to DOCX
curl -F "file=@document.doc" "https://your-service.onrender.com/convert?format=docx" --output converted.docx

# Convert DOC to PDF
curl -F "file=@document.doc" "https://your-service.onrender.com/convert?format=pdf" --output converted.pdf

# Convert DOCX to PDF
curl -F "file=@document.docx" "https://your-service.onrender.com/convert?format=pdf" --output converted.pdf
```

### API Documentation

Swagger UI is automatically available at:
```
https://your-service.onrender.com/docs
```

## Local Development

### Prerequisites

- Python 3.10+
- LibreOffice
- Docker (optional)

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app:app --reload
```

### Running with Docker

```bash
# Build the Docker image
docker build -t doc-converter .

# Run the container
docker run -p 8000:10000 doc-converter
```

Then access the API at http://localhost:8000

## Why Render instead of Azure Functions?

- **Simplicity**: Render provides a much simpler deployment process
- **Predictable Pricing**: Fixed $7/month for the starter plan
- **No Cold Starts**: Service is always running, no delays
- **Simple Configuration**: No complex cloud infrastructure to manage

## Performance Considerations

- The starter plan on Render includes 512MB RAM and 0.5 CPU
- For heavy document conversion workloads, consider upgrading to a higher plan
- LibreOffice conversion is memory-intensive, watch resource usage for large files 