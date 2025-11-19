# Detailed Setup Guide

This guide will walk you through setting up the Gmail Summaries service from scratch.

## Prerequisites

### 1. Google Cloud Project Setup

1. **Create or Select a Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note down your Project ID

2. **Enable Gmail API**:
   - In the Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Enter a name (e.g., "gmail-summaries-bot")
   - Add description: "Service account for Gmail Summaries API"
   - Click "Create and Continue"
   - (Optional) Grant roles if needed
   - Click "Continue" then "Done"

4. **Create Service Account Key**:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Click "Create"
   - Save the downloaded JSON file securely

### 2. Enable Domain-Wide Delegation (Google Workspace Only)

If you're using Google Workspace and want to access a specific user's Gmail:

1. **Enable Domain-Wide Delegation**:
   - In the service account details, check "Enable Google Workspace Domain-wide Delegation"
   - Enter a product name (e.g., "Gmail Summaries")
   - Click "Save"

2. **Add OAuth Scope in Workspace Admin Console**:
   - Go to [Google Workspace Admin Console](https://admin.google.com/)
   - Navigate to Security > API Controls > Domain-wide Delegation
   - Click "Add new"
   - Enter your service account's Client ID (found in the JSON key file)
   - Add the OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`
   - Click "Authorize"

### 3. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key or use an existing one
4. Copy the API key and store it securely

## Installation Steps

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/murphy360/gmail_summaries.git
   cd gmail_summaries
   ```

2. **Create credentials directory**:
   ```bash
   mkdir -p credentials
   chmod 700 credentials
   ```

3. **Copy your service account key**:
   ```bash
   cp /path/to/your/downloaded-key.json credentials/service-account.json
   chmod 600 credentials/service-account.json
   ```

4. **Create environment file**:
   ```bash
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```

5. **Edit .env file**:
   ```bash
   # Required: Your Gemini API key
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   
   # Required: Path to service account file (inside container)
   GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json
   
   # Optional: For domain-wide delegation (Google Workspace)
   # GMAIL_DELEGATED_USER=your.email@yourdomain.com
   
   # Optional: Path to credentials on host machine
   CREDENTIALS_PATH=./credentials
   
   # Optional: Change port if needed
   PORT=5000
   ```

6. **Start the service**:
   ```bash
   docker-compose up -d
   ```

7. **Check logs**:
   ```bash
   docker-compose logs -f
   ```

8. **Test the service**:
   ```bash
   curl http://localhost:5000/health
   ```

### Option 2: Docker Run

```bash
docker run -d \
  -p 5000:5000 \
  -e GEMINI_API_KEY="your_gemini_api_key" \
  -e GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json \
  -e GMAIL_DELEGATED_USER="your.email@example.com" \
  -v $(pwd)/credentials:/app/credentials:ro \
  --name gmail-summaries \
  gmail-summaries
```

### Option 3: Local Development

1. **Install Python 3.11+**:
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**:
   ```bash
   export GEMINI_API_KEY="your_gemini_api_key"
   export GOOGLE_SERVICE_ACCOUNT_FILE="./credentials/service-account.json"
   # Optional:
   # export GMAIL_DELEGATED_USER="your.email@example.com"
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

## Testing the API

### Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "gmail-summaries",
  "timestamp": "2025-11-19T17:00:00.000000"
}
```

### Get Today's Email Summary
```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize Today'\''s Unread Emails"}'
```

### Get Kids Activities Summary
```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "Summarize Unread emails for Kids activities"}'
```

### Custom Query with Filters
```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Work emails",
    "time_filter": "today",
    "topic_filter": "work project"
  }'
```

### Debug: Get Raw Emails
```bash
curl "http://localhost:5000/api/emails?time_filter=today"
```

## Home Assistant Integration

1. **Add to configuration.yaml**:
   - Copy the contents from `home_assistant_config.yaml`
   - Update the URL if your service is running on a different host

2. **Restart Home Assistant**:
   ```bash
   # In Home Assistant
   Developer Tools > YAML > Check Configuration
   Developer Tools > YAML > Restart
   ```

3. **Test REST Commands**:
   ```bash
   # In Home Assistant Developer Tools > Services
   Service: rest_command.gmail_summary_today
   ```

4. **Add Dashboard Card**:
   - Go to your dashboard
   - Click "Edit Dashboard"
   - Add a new card with the configuration from `home_assistant_config.yaml`

## Troubleshooting

### Issue: "Gmail credentials not found"
**Solution**: 
- Ensure `GOOGLE_SERVICE_ACCOUNT_FILE` points to a valid JSON file
- Check file permissions: `ls -la credentials/`
- Verify the file is mounted in Docker: `docker exec gmail-summaries ls -la /app/credentials/`

### Issue: "Failed to build Gmail service"
**Solution**:
- Verify the service account JSON file is valid JSON
- Check that Gmail API is enabled in your Google Cloud project
- For domain-wide delegation, ensure it's properly configured in Workspace Admin Console

### Issue: "No unread emails found"
**Solution**:
- Check that you actually have unread emails
- Verify you're using the correct Gmail account (check `GMAIL_DELEGATED_USER`)
- Test with `curl "http://localhost:5000/api/emails"` to see raw emails

### Issue: "Gemini API error"
**Solution**:
- Verify your Gemini API key is valid
- Check API quotas in Google AI Studio
- Ensure you have an active Google Cloud billing account

### Issue: "SSL certificate verification failed" (in logs)
**Solution**:
- This usually happens in corporate networks with SSL inspection
- For Docker: add `ENV PYTHONHTTPSVERIFY=0` to Dockerfile (not recommended for production)
- Better solution: Add your corporate CA certificate to the container

### Issue: Home Assistant can't reach the service
**Solution**:
- If using Docker networks, ensure both containers are on the same network
- Use the container name as hostname: `http://gmail-summaries:5000`
- Or use host machine IP: `http://192.168.1.100:5000`
- Check firewall rules

## Security Best Practices

1. **Never commit credentials**:
   - Service account JSON files should never be in version control
   - Use environment variables for API keys
   - The `.gitignore` is configured to exclude credentials

2. **Use read-only mounts**:
   - Mount credentials as read-only: `-v ./credentials:/app/credentials:ro`

3. **Restrict service account permissions**:
   - Only grant necessary Gmail API scopes
   - Use domain-wide delegation only when needed

4. **Rotate credentials regularly**:
   - Periodically create new service account keys
   - Delete old keys from Google Cloud Console

5. **Network security**:
   - Run the service on a private network
   - Use HTTPS reverse proxy (nginx, traefik) for external access
   - Consider using VPN for remote access

6. **Monitor usage**:
   - Check Google Cloud Console for API usage
   - Monitor logs for suspicious activity
   - Set up billing alerts

## Updating the Service

```bash
# Pull latest code
git pull origin main

# Rebuild Docker image
docker-compose build

# Restart service
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Uninstallation

```bash
# Stop and remove containers
docker-compose down

# Remove images (optional)
docker rmi gmail-summaries

# Remove credentials (be careful!)
rm -rf credentials/

# Remove environment file
rm .env
```

## Getting Help

- Check the [README.md](README.md) for general information
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub for bugs or feature requests
- Check [Google Gmail API documentation](https://developers.google.com/gmail/api)
- Check [Google Gemini API documentation](https://ai.google.dev/docs)
