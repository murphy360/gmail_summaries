# Gmail Summaries Service

A Docker-based REST API service that integrates Gmail and Gemini AI to provide intelligent email summaries. Designed to work seamlessly with Home Assistant and other automation platforms.

## Features

- 📧 **Gmail Integration**: Fetch unread emails using Gmail API
- 🤖 **AI-Powered Summaries**: Generate intelligent summaries using Google's Gemini AI
- 🕐 **Time-Based Filtering**: Filter emails by time (today, this week, etc.)
- 🏷️ **Topic-Based Filtering**: Filter emails by topics (e.g., "kids activities")
- 🐳 **Docker Ready**: Fully containerized with Docker and docker-compose
- 🏠 **Home Assistant Compatible**: Easy REST API integration
- 🔒 **Secure**: Service account authentication for Gmail API

## Quick Start

### Prerequisites

1. **Google Cloud Project** with Gmail API enabled
2. **Service Account** with Gmail API access (or domain-wide delegation)
3. **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/murphy360/gmail_summaries.git
   cd gmail_summaries
   ```

2. **Set up credentials**:
   ```bash
   # Create credentials directory
   mkdir credentials
   
   # Copy your service account JSON file
   cp /path/to/your/service-account.json credentials/service-account.json
   ```

3. **Configure environment**:
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env and add your keys
   nano .env
   ```

4. **Start the service**:
   ```bash
   docker-compose up -d
   ```

5. **Check health**:
   ```bash
   curl http://localhost:5000/health
   ```

## Gmail API Setup

### Creating a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Gmail API
4. Create a Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and description
   - Grant it appropriate roles
   - Create and download JSON key
5. (Optional) Enable domain-wide delegation if using Google Workspace

### Domain-Wide Delegation (Google Workspace)

If you're using Google Workspace and want to access a specific user's Gmail:

1. Enable domain-wide delegation for your service account
2. Add the OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`
3. Set `GMAIL_DELEGATED_USER` in your `.env` file

## API Endpoints

### Health Check
```bash
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "gmail-summaries",
  "timestamp": "2025-11-19T17:00:00.000Z"
}
```

### Summarize Emails
```bash
POST /api/summarize
Content-Type: application/json

{
  "query": "Summarize Today's Unread Emails"
}
```

**Response**:
```json
{
  "summary": "You have 5 unread emails today. Key highlights: ...",
  "email_count": 5,
  "query": "Summarize Today's Unread Emails",
  "timestamp": "2025-11-19T17:00:00.000Z"
}
```

**Supported Query Types**:
- "Summarize Today's Unread Emails"
- "Summarize Unread emails for Kids activities"
- Custom queries with time_filter and topic_filter

**Request Body Options**:
```json
{
  "query": "Your natural language query",
  "time_filter": "today",  // Optional: "today", "week", or omit
  "topic_filter": "kids activities"  // Optional: any topic keyword
}
```

### Get Emails (Debug)
```bash
GET /api/emails?time_filter=today
```

**Response**:
```json
{
  "emails": [...],
  "count": 5,
  "timestamp": "2025-11-19T17:00:00.000Z"
}
```

## Home Assistant Integration

### Configuration.yaml

```yaml
rest_command:
  gmail_summary_today:
    url: "http://localhost:5000/api/summarize"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "Summarize Today''s Unread Emails"}'
    
  gmail_summary_kids:
    url: "http://localhost:5000/api/summarize"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "Summarize Unread emails for Kids activities"}'
```

### Automation Example

```yaml
automation:
  - alias: "Morning Email Summary"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      - service: rest_command.gmail_summary_today
      - service: notify.mobile_app
        data:
          message: "{{ state_attr('rest_command.gmail_summary_today', 'summary') }}"
```

### Using with Sensors

```yaml
sensor:
  - platform: rest
    name: "Gmail Summary Today"
    resource: "http://localhost:5000/api/summarize"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "Summarize Today''s Unread Emails"}'
    value_template: "{{ value_json.email_count }}"
    json_attributes:
      - summary
      - email_count
    scan_interval: 1800  # Update every 30 minutes
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Your Gemini API key from Google AI Studio |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Yes* | Path to service account JSON file |
| `GOOGLE_CREDENTIALS_JSON` | Yes* | Service account JSON as string (alternative) |
| `GMAIL_DELEGATED_USER` | No | Email address for domain-wide delegation |
| `PORT` | No | Port to run the service (default: 5000) |

*Either `GOOGLE_SERVICE_ACCOUNT_FILE` or `GOOGLE_CREDENTIALS_JSON` is required.

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your_key"
export GOOGLE_SERVICE_ACCOUNT_FILE="path/to/service-account.json"

# Run the app
python app.py
```

### Building Docker Image

```bash
docker build -t gmail-summaries .
```

### Running with Docker

```bash
docker run -d \
  -p 5000:5000 \
  -e GEMINI_API_KEY="your_key" \
  -v $(pwd)/credentials:/app/credentials:ro \
  --name gmail-summaries \
  gmail-summaries
```

## Troubleshooting

### Authentication Errors

- Ensure your service account JSON file is valid
- Check that Gmail API is enabled in your Google Cloud project
- Verify domain-wide delegation if using Google Workspace

### No Emails Found

- Check that there are actually unread emails in the inbox
- Verify time filters are working correctly
- Check Gmail API quotas in Google Cloud Console

### Summary Generation Fails

- Verify your Gemini API key is valid
- Check API quotas and limits
- Review logs for specific error messages

## Security Considerations

- **Never commit** service account JSON files or API keys to version control
- Use environment variables or secure secret management
- Restrict service account permissions to minimum required
- Consider using read-only Gmail scopes
- Regularly rotate API keys and service account credentials

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
