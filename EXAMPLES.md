# Usage Examples

This document provides practical examples for using the Gmail Summaries service.

## API Examples

### Basic Health Check

```bash
curl http://localhost:5000/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "gmail-summaries",
  "timestamp": "2025-11-19T17:00:00.123456"
}
```

### Today's Email Summary

```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize Today'\''s Unread Emails"
  }'
```

**Response**:
```json
{
  "summary": "You have 12 unread emails today:\n\n**Work Updates (5 emails)**\n- Project status report from John\n- Q4 budget review meeting scheduled\n- New feature deployment notification\n- Team sync-up tomorrow at 10 AM\n- Code review request from Sarah\n\n**Personal (4 emails)**\n- Credit card statement available\n- Package delivery notification\n- Newsletter from your favorite blog\n- Dinner reservation confirmation\n\n**Kids Activities (3 emails)**\n- Soccer practice moved to Thursday\n- School picture day next week\n- Permission slip for field trip\n\n**Action Items**:\n- Review code before tomorrow's meeting\n- Sign permission slip for field trip\n- Confirm dinner reservation",
  "email_count": 12,
  "query": "Summarize Today's Unread Emails",
  "timestamp": "2025-11-19T17:30:45.678901"
}
```

### Topic-Specific Summary

```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize Unread emails for Kids activities"
  }'
```

**Response**:
```json
{
  "summary": "You have 3 unread emails about kids activities:\n\n1. **Soccer Practice Schedule Change**\n   From: Coach Mike\n   The soccer practice has been moved from Wednesday to Thursday at 4 PM due to field maintenance.\n\n2. **School Picture Day**\n   From: Principal Johnson\n   School picture day is scheduled for next Tuesday. Students should wear their best clothes.\n\n3. **Field Trip Permission Slip**\n   From: Mrs. Smith\n   The 5th grade class is planning a field trip to the Science Museum next month. Please sign and return the permission slip by Friday.",
  "email_count": 3,
  "query": "Summarize Unread emails for Kids activities",
  "timestamp": "2025-11-19T17:35:12.345678"
}
```

### Custom Filters

```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Work emails from today",
    "time_filter": "today",
    "topic_filter": "work project"
  }'
```

### Get Raw Emails (Debug)

```bash
curl "http://localhost:5000/api/emails?time_filter=today"
```

**Response**:
```json
{
  "emails": [
    {
      "id": "18c1a2b3d4e5f6g7",
      "subject": "Project Status Update",
      "from": "John Doe <john@example.com>",
      "date": "Tue, 19 Nov 2025 09:30:00 -0800",
      "snippet": "Here is the latest update on the project...",
      "body": "Full email body content here..."
    }
  ],
  "count": 1,
  "timestamp": "2025-11-19T17:40:00.000000"
}
```

## Home Assistant Examples

### REST Command Integration

Add to your `configuration.yaml`:

```yaml
rest_command:
  gmail_summary_today:
    url: "http://gmail-summaries:5000/api/summarize"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "Summarize Today\u0027s Unread Emails"}'
```

Call from automation:

```yaml
- service: rest_command.gmail_summary_today
```

### Sensor Integration

```yaml
sensor:
  - platform: rest
    name: "Daily Email Summary"
    resource: "http://gmail-summaries:5000/api/summarize"
    method: POST
    headers:
      Content-Type: "application/json"
    payload: '{"query": "Summarize Today\u0027s Unread Emails"}'
    value_template: "{{ value_json.email_count }}"
    json_attributes:
      - summary
      - email_count
      - timestamp
    scan_interval: 1800
```

Access in templates:

```yaml
{{ states('sensor.daily_email_summary') }}  # Returns email count
{{ state_attr('sensor.daily_email_summary', 'summary') }}  # Returns summary text
```

### Morning Summary Automation

```yaml
automation:
  - alias: "Morning Email Briefing"
    description: "Send email summary at 8 AM"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: rest_command.gmail_summary_today
      - delay: "00:00:05"
      - service: notify.mobile_app_phone
        data:
          title: "📧 Morning Email Summary"
          message: "{{ state_attr('sensor.daily_email_summary', 'summary') }}"
          data:
            priority: high
            notification_icon: mdi:email
```

### Kids Activities Check

```yaml
automation:
  - alias: "Check Kids Activities After School"
    trigger:
      - platform: time
        at: "15:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.school_day
        state: "on"
    action:
      - service: rest_command.gmail_summary_kids
      - delay: "00:00:05"
      - choose:
          - conditions:
              - condition: template
                value_template: "{{ states('sensor.gmail_summary_kids')|int > 0 }}"
            sequence:
              - service: notify.mobile_app_phone
                data:
                  title: "🧒 Kids Activities Update"
                  message: "{{ state_attr('sensor.gmail_summary_kids', 'summary') }}"
```

### Voice Assistant Integration

```yaml
automation:
  - alias: "Voice Activated Email Summary"
    trigger:
      - platform: conversation
        command:
          - "What are my emails [today]"
          - "Check my inbox"
          - "Any new emails"
          - "Read my emails"
    action:
      - service: rest_command.gmail_summary_today
      - delay: "00:00:05"
      - service: tts.google_translate_say
        data:
          entity_id: media_player.living_room_speaker
          message: >
            {% set count = states('sensor.daily_email_summary')|int %}
            {% if count == 0 %}
              You have no unread emails.
            {% elif count == 1 %}
              You have 1 unread email. {{ state_attr('sensor.daily_email_summary', 'summary') }}
            {% else %}
              You have {{ count }} unread emails. {{ state_attr('sensor.daily_email_summary', 'summary') }}
            {% endif %}
```

### Dashboard Card Examples

#### Simple Entity Card

```yaml
type: entities
title: 📧 Email Summary
entities:
  - entity: sensor.daily_email_summary
    name: Today's Emails
    icon: mdi:email
  - entity: sensor.gmail_summary_kids
    name: Kids Activities
    icon: mdi:school
```

#### Markdown Card with Full Summary

```yaml
type: markdown
title: 📧 Today's Email Summary
content: |
  **{{ states('sensor.daily_email_summary') }} unread emails**
  
  {{ state_attr('sensor.daily_email_summary', 'summary') }}
  
  ---
  *Last updated: {{ as_timestamp(state_attr('sensor.daily_email_summary', 'timestamp')) | timestamp_custom('%I:%M %p') }}*
```

#### Button Card with Actions

```yaml
type: button
name: Refresh Email Summary
icon: mdi:email-sync
tap_action:
  action: call-service
  service: rest_command.gmail_summary_today
```

#### Conditional Card

```yaml
type: conditional
conditions:
  - entity: sensor.daily_email_summary
    state_not: "0"
card:
  type: markdown
  content: |
    ⚠️ **You have {{ states('sensor.daily_email_summary') }} unread emails!**
    
    {{ state_attr('sensor.daily_email_summary', 'summary')[:200] }}...
```

## Python Examples

### Direct API Usage

```python
import requests
import json

# Service URL
BASE_URL = "http://localhost:5000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(f"Service Status: {response.json()['status']}")

# Get today's summary
payload = {
    "query": "Summarize Today's Unread Emails"
}

response = requests.post(
    f"{BASE_URL}/api/summarize",
    headers={"Content-Type": "application/json"},
    json=payload
)

if response.status_code == 200:
    data = response.json()
    print(f"\nEmail Count: {data['email_count']}")
    print(f"\nSummary:\n{data['summary']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Scheduled Summary Script

```python
#!/usr/bin/env python3
"""Send daily email summary to Slack/Discord/Email."""

import requests
import schedule
import time
from datetime import datetime

def send_email_summary():
    """Fetch and send email summary."""
    try:
        # Get summary
        response = requests.post(
            "http://localhost:5000/api/summarize",
            json={"query": "Summarize Today's Unread Emails"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Send to Slack (example)
            slack_webhook = "YOUR_SLACK_WEBHOOK_URL"
            slack_data = {
                "text": f"📧 Daily Email Summary ({data['email_count']} emails)",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": data['summary']
                        }
                    }
                ]
            }
            requests.post(slack_webhook, json=slack_data)
            
            print(f"[{datetime.now()}] Summary sent successfully")
        else:
            print(f"[{datetime.now()}] Error: {response.status_code}")
            
    except Exception as e:
        print(f"[{datetime.now()}] Exception: {e}")

# Schedule daily at 8 AM
schedule.every().day.at("08:00").do(send_email_summary)

print("Email summary scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Docker Examples

### Run with Custom Port

```bash
docker run -d \
  -p 8080:5000 \
  -e GEMINI_API_KEY="your_key" \
  -e GOOGLE_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json \
  -v $(pwd)/credentials:/app/credentials:ro \
  --name gmail-summaries \
  gmail-summaries
```

### Run with Environment File

```bash
docker run -d \
  -p 5000:5000 \
  --env-file .env \
  -v $(pwd)/credentials:/app/credentials:ro \
  --name gmail-summaries \
  gmail-summaries
```

### View Logs

```bash
# Follow logs
docker logs -f gmail-summaries

# Last 100 lines
docker logs --tail 100 gmail-summaries

# With timestamps
docker logs -t gmail-summaries
```

### Interactive Shell

```bash
# Start shell in running container
docker exec -it gmail-summaries /bin/bash

# Run Python in container
docker exec -it gmail-summaries python -c "import app; print(app.app.name)"
```

## Troubleshooting Examples

### Test Gmail Connection

```bash
curl -X GET "http://localhost:5000/api/emails?time_filter=today" | jq
```

### Check Service Health

```bash
# Simple check
curl http://localhost:5000/health

# With details
curl -v http://localhost:5000/health

# Monitor continuously
watch -n 5 'curl -s http://localhost:5000/health | jq'
```

### Test with Different Queries

```bash
# Work emails
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "work", "time_filter": "today"}' | jq

# Family emails
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"topic_filter": "family"}' | jq

# Specific topic
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"topic_filter": "meeting schedule"}' | jq
```

## Advanced Examples

### Custom Summary Request

```bash
curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Summarize urgent work emails from today about the project",
    "time_filter": "today",
    "topic_filter": "urgent work project"
  }' | jq '.summary'
```

### Batch Processing Multiple Queries

```bash
#!/bin/bash

# Array of topics
topics=("work" "kids" "finance" "personal")

for topic in "${topics[@]}"; do
    echo "=== $topic Emails ==="
    curl -s -X POST http://localhost:5000/api/summarize \
      -H "Content-Type: application/json" \
      -d "{\"topic_filter\": \"$topic\"}" | jq -r '.summary'
    echo ""
done
```

### JSON Output Processing

```bash
# Get just the summary text
curl -s -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "today"}' | jq -r '.summary'

# Get email count
curl -s -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "today"}' | jq -r '.email_count'

# Save to file
curl -s -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "today"}' | jq '.' > summary.json
```

## Integration Examples

### Node-RED Flow

```json
[
    {
        "id": "email_summary",
        "type": "http request",
        "name": "Get Email Summary",
        "method": "POST",
        "url": "http://gmail-summaries:5000/api/summarize",
        "payload": "{\"query\": \"today\"}",
        "headers": {"Content-Type": "application/json"}
    }
]
```

### Zapier/Make.com Webhook

Webhook URL: `http://your-server:5000/api/summarize`  
Method: POST  
Body:
```json
{
  "query": "Summarize Today's Unread Emails"
}
```

### Cron Job

```bash
# Add to crontab (crontab -e)
0 8 * * 1-5 curl -X POST http://localhost:5000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"query": "today"}' | mail -s "Daily Email Summary" you@example.com
```
