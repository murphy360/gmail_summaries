# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Home Assistant                            │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  REST Commands   │  │   REST Sensors   │                    │
│  │  - Today Summary │  │  - Email Count   │                    │
│  │  - Kids Summary  │  │  - Summary Text  │                    │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                     │                               │
│           └─────────────────────┘                               │
│                     │ HTTP POST/GET                             │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      │ JSON Request/Response
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Gmail Summaries Service                        │
│                      (Docker Container)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     Flask REST API                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   /health    │  │ /api/emails  │  │/api/summarize│  │  │
│  │  │  (GET)       │  │  (GET)       │  │   (POST)     │  │  │
│  │  └──────────────┘  └──────────────┘  └──────┬───────┘  │  │
│  │                                              │          │  │
│  │  ┌───────────────────────────────────────────┼─────┐  │  │
│  │  │         Application Logic                 │     │  │  │
│  │  │  • Query Parsing                         │     │  │  │
│  │  │  • Time Filter Extraction                │     │  │  │
│  │  │  • Topic Filter Extraction               │     │  │  │
│  │  │  • Email Filtering (Word Boundary)       │     │  │  │
│  │  │  • Error Handling & Logging              │     │  │  │
│  │  └───────────────┬──────────────┬───────────┘     │  │  │
│  └──────────────────┼──────────────┼─────────────────┘  │  │
│                     │              │                     │  │
│           ┌─────────▼─────┐   ┌───▼──────────┐         │  │
│           │ Gmail Client  │   │Gemini Client │         │  │
│           │ (gmail_client)│   │(gemini_client│         │  │
│           └───────┬───────┘   └──────┬───────┘         │  │
│                   │                  │                  │  │
└───────────────────┼──────────────────┼──────────────────┘  │
                    │                  │                     │
        ┌───────────▼────────┐  ┌──────▼─────────┐         │
        │   Gmail API        │  │  Gemini API    │         │
        │ (Google Workspace) │  │ (Google AI)    │         │
        │                    │  │                │         │
        │ • Fetch Unread     │  │ • Generate     │         │
        │ • Apply Filters    │  │   Summary      │         │
        │ • Parse Messages   │  │ • Process Text │         │
        └────────────────────┘  └────────────────┘         │
```

## Component Details

### 1. Home Assistant Integration Layer

**Purpose**: User interface for querying email summaries

**Components**:
- **REST Commands**: Trigger email summary generation
- **REST Sensors**: Track email counts and store summaries
- **Automations**: Schedule automatic summaries
- **Voice Assistant**: Voice-triggered summaries

**Communication**: HTTP JSON requests to Flask API

### 2. Flask REST API

**Purpose**: HTTP interface for the service

**Endpoints**:
- `GET /health` - Health check endpoint
- `POST /api/summarize` - Generate email summary
- `GET /api/emails` - Fetch raw emails (debug)

**Request Processing**:
1. Receive HTTP request with query
2. Parse natural language query
3. Extract time and topic filters
4. Coordinate between Gmail and Gemini clients
5. Return JSON response

### 3. Gmail Client

**Purpose**: Interface with Gmail API

**Authentication**:
- Service Account JSON credentials
- Optional domain-wide delegation

**Operations**:
- Fetch unread emails
- Apply time filters (today, week)
- Parse email content (subject, body, snippet)
- Extract headers and metadata

**API Scope**: `gmail.readonly` (read-only access)

### 4. Gemini Client

**Purpose**: Generate AI-powered summaries

**Authentication**: API Key

**Operations**:
- Receive email data
- Format prompt with context
- Generate intelligent summary
- Fallback to basic summary on error

**Model**: gemini-pro

### 5. Application Logic

**Query Parsing**:
- Extract time filters from natural language
- Extract topic keywords
- Handle case-insensitive matching

**Email Filtering**:
- Word boundary regex matching
- Multi-field search (subject, snippet, body)
- Efficient filtering pipeline

**Error Handling**:
- Graceful degradation
- Detailed logging
- User-friendly error messages

## Data Flow

### Typical Request Flow

1. **User Triggers Request** (Home Assistant)
   ```json
   POST /api/summarize
   {
     "query": "Summarize Today's Unread Emails"
   }
   ```

2. **API Receives & Parses Request**
   - Extract time_filter: "today"
   - Extract topic_filter: none

3. **Gmail Client Fetches Emails**
   - Query: `is:unread newer_than:1d`
   - Returns: List of email objects

4. **Application Filters Emails**
   - Apply topic filter if specified
   - Return matched emails

5. **Gemini Client Generates Summary**
   - Format emails into prompt
   - Call Gemini API
   - Return AI-generated summary

6. **API Returns Response**
   ```json
   {
     "summary": "You have 5 unread emails...",
     "email_count": 5,
     "query": "Summarize Today's Unread Emails",
     "timestamp": "2025-11-19T17:00:00"
   }
   ```

## Security Architecture

### Credential Management

```
┌─────────────────────────────┐
│   Environment Variables      │
│  • GEMINI_API_KEY           │
│  • GOOGLE_SERVICE_ACCOUNT   │
│  • GMAIL_DELEGATED_USER     │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│    Docker Container          │
│  • Mounted credentials dir   │
│  • Read-only volume mount    │
│  • No secrets in image       │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Service Account Auth       │
│  • OAuth 2.0                │
│  • Read-only scope          │
│  • Optional delegation      │
└─────────────────────────────┘
```

### Network Security

```
Home Assistant  ─────────────────┐
                                 │
                                 ▼
┌──────────────────────────────────────┐
│        Docker Network (bridge)        │
│                                       │
│  gmail-summaries:5000                │
└──────────────┬───────────────────────┘
               │
               ├─► Gmail API (HTTPS)
               │
               └─► Gemini API (HTTPS)
```

## Deployment Architecture

### Docker Compose Deployment

```
docker-compose.yml
       │
       ├─► Build Image (Dockerfile)
       │    ├─► Python 3.11 slim base
       │    ├─► Install dependencies
       │    ├─► Copy application code
       │    └─► Configure gunicorn
       │
       ├─► Mount Volumes
       │    └─► ./credentials:/app/credentials:ro
       │
       ├─► Set Environment Variables
       │    └─► From .env file
       │
       └─► Configure Networking
            ├─► Port mapping: 5000:5000
            └─► Bridge network
```

### Scalability Considerations

**Current**: Single container, 2 gunicorn workers

**Future Scaling Options**:
1. Increase gunicorn workers
2. Run multiple containers with load balancer
3. Horizontal scaling with Kubernetes
4. Caching layer for frequent queries
5. Background task queue for long-running summaries

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| API Framework | Flask 3.0 | HTTP REST API |
| WSGI Server | Gunicorn | Production server |
| Email Client | Google Gmail API | Fetch emails |
| AI Service | Google Gemini AI | Generate summaries |
| Authentication | Google OAuth 2.0 | Service account auth |
| Containerization | Docker | Deployment isolation |
| Orchestration | Docker Compose | Multi-service management |
| Integration | Home Assistant | User interface |

## Configuration Management

```
.env file (not in git)
    │
    ├─► GEMINI_API_KEY → Gemini Client
    │
    └─► GOOGLE_SERVICE_ACCOUNT_FILE → Gmail Client
            │
            └─► credentials/service-account.json
                    │
                    ├─► Project ID
                    ├─► Private Key
                    └─► Client Email
```

## Logging & Monitoring

```
Application Logs
    │
    ├─► Flask Request Logs
    ├─► Gmail API Call Logs
    ├─► Gemini API Call Logs
    └─► Error Logs
        │
        └─► Docker Logs (stdout/stderr)
                │
                └─► docker-compose logs -f
```

## Error Handling Flow

```
Request Error
    │
    ├─► Gmail API Error
    │    ├─► Auth Error → Return 500 + log
    │    ├─► API Quota → Return 500 + log
    │    └─► Network Error → Return 500 + log
    │
    ├─► Gemini API Error
    │    ├─► Auth Error → Fallback to basic summary
    │    ├─► API Quota → Fallback to basic summary
    │    └─► Network Error → Fallback to basic summary
    │
    └─► Application Error
         ├─► Invalid Request → Return 400
         ├─► No Emails Found → Return 200 (empty)
         └─► Unexpected Error → Return 500 + log
```

## Future Architecture Enhancements

### Planned Improvements

1. **Caching Layer**
   - Redis for frequently requested summaries
   - TTL-based invalidation

2. **Background Processing**
   - Celery for async processing
   - Scheduled summary generation

3. **Multi-Account Support**
   - Multiple Gmail accounts
   - Account switching in requests

4. **Webhook Support**
   - Real-time email notifications
   - Gmail Push Notifications

5. **Metrics & Monitoring**
   - Prometheus metrics
   - Grafana dashboards
   - Health check endpoints

6. **Advanced AI Features**
   - Custom summary templates
   - Sentiment analysis
   - Priority detection
   - Action item extraction
