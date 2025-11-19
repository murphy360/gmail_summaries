"""
Gmail Summaries Service - A REST API service for summarizing Gmail emails using Gemini AI.
"""

import os
import logging
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from gmail_client import GmailClient
from gemini_client import GeminiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize clients
gmail_client = None
gemini_client = None


def init_clients():
    """Initialize Gmail and Gemini clients."""
    global gmail_client, gemini_client
    
    try:
        gmail_client = GmailClient()
        gemini_client = GeminiClient()
        logger.info("Clients initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {str(e)}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'gmail-summaries',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/summarize', methods=['POST'])
def summarize_emails():
    """
    Summarize emails based on query parameters.
    
    Expected JSON body:
    {
        "query": "Summarize Today's Unread Emails" or "Summarize Unread emails for Kids activities",
        "time_filter": "today" (optional),
        "topic_filter": "kids activities" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        query = data.get('query', '')
        time_filter = data.get('time_filter')
        topic_filter = data.get('topic_filter')
        
        # Parse query if not explicitly provided filters
        if not time_filter and 'today' in query.lower():
            time_filter = 'today'
        
        if not topic_filter:
            # Extract topic from query
            query_lower = query.lower()
            if 'kids' in query_lower or 'children' in query_lower:
                topic_filter = 'kids activities'
        
        logger.info(f"Processing query: {query}, time_filter: {time_filter}, topic_filter: {topic_filter}")
        
        # Fetch emails
        emails = gmail_client.get_unread_emails(time_filter=time_filter)
        
        if not emails:
            return jsonify({
                'summary': 'No unread emails found matching your criteria.',
                'email_count': 0
            }), 200
        
        # Filter by topic if specified
        if topic_filter:
            emails = filter_emails_by_topic(emails, topic_filter)
        
        if not emails:
            return jsonify({
                'summary': f'No emails found matching topic: {topic_filter}',
                'email_count': 0
            }), 200
        
        # Generate summary using Gemini
        summary = gemini_client.summarize_emails(emails, topic_filter)
        
        return jsonify({
            'summary': summary,
            'email_count': len(emails),
            'query': query,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


def filter_emails_by_topic(emails, topic):
    """Filter emails by topic keywords."""
    topic_keywords = topic.lower().split()
    filtered = []
    
    for email in emails:
        subject = email.get('subject', '').lower()
        snippet = email.get('snippet', '').lower()
        body = email.get('body', '').lower()
        
        # Check if any keyword is in subject, snippet, or body
        for keyword in topic_keywords:
            if keyword in subject or keyword in snippet or keyword in body:
                filtered.append(email)
                break
    
    return filtered


@app.route('/api/emails', methods=['GET'])
def get_emails():
    """
    Get unread emails (for debugging purposes).
    
    Query parameters:
    - time_filter: 'today', 'week', etc.
    """
    try:
        time_filter = request.args.get('time_filter')
        emails = gmail_client.get_unread_emails(time_filter=time_filter)
        
        return jsonify({
            'emails': emails,
            'count': len(emails),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    init_clients()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
