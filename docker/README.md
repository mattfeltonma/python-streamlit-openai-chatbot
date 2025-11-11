# Docker Setup

This directory contains all Docker-related configuration files for the chatbot application.

## Files

- **`Dockerfile`** - Multi-stage build configuration for production
- **`docker-compose.yml`** - Basic development setup
- **`docker-compose.dev.yml`** - Development with hot reloading
- **`docker-compose.prod.yml`** - Production with secrets management
- **`.dockerignore`** - Build context exclusions

## Quick Start

### Development
```bash
# From project root, run with hot reloading
cd docker
docker-compose -f docker-compose.dev.yml up --build

# Or basic development
docker-compose up --build
```

### Production
```bash
# Set up Docker secrets first
echo "your-client-id" | docker secret create azure_client_id -
echo "your-client-secret" | docker secret create azure_client_secret -
echo "your-tenant-id" | docker secret create azure_tenant_id -

# Deploy
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Build
```bash
# From project root
docker build -f docker/Dockerfile -t chatbot .
docker run -p 8080:8080 chatbot
```

## Configuration

### Environment Variables
Set these in your `.variables` file in the project root:
```
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
```

### Secrets
For production, use Docker secrets instead of environment variables:
- `azure_client_id`
- `azure_client_secret` 
- `azure_tenant_id`

## Volumes
- **Development**: Source code mounted for hot reloading
- **Production**: No volumes (immutable containers)
- **Secrets**: Mounted as read-only files

## Health Checks
The container includes health checks on `/_stcore/health` endpoint.

## Security Features
- Non-root user (`streamlituser`)
- Minimal base image (Python slim)
- Secret management
- Read-only secret mounts