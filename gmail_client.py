"""
Gmail API Client for fetching emails.
"""

import os
import base64
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GmailClient:
    """Client for interacting with Gmail API."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        """Initialize Gmail API client."""
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Authenticate and return Gmail API service."""
        creds = None
        
        # Check for service account credentials
        service_account_file = os.environ.get('GOOGLE_SERVICE_ACCOUNT_FILE')
        credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        
        if service_account_file and os.path.exists(service_account_file):
            logger.info("Using service account authentication")
            creds = service_account.Credentials.from_service_account_file(
                service_account_file, scopes=self.SCOPES
            )
        elif credentials_json:
            logger.info("Using service account JSON from environment")
            import json
            creds_data = json.loads(credentials_json)
            creds = service_account.Credentials.from_service_account_info(
                creds_data, scopes=self.SCOPES
            )
        else:
            raise ValueError(
                "Gmail credentials not found. Set GOOGLE_SERVICE_ACCOUNT_FILE or "
                "GOOGLE_CREDENTIALS_JSON environment variable."
            )
        
        # Delegate domain-wide authority if needed
        delegated_user = os.environ.get('GMAIL_DELEGATED_USER')
        if delegated_user:
            logger.info(f"Using delegated credentials for user: {delegated_user}")
            creds = creds.with_subject(delegated_user)
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API client initialized successfully")
            return service
        except Exception as e:
            logger.error(f"Failed to build Gmail service: {str(e)}")
            raise
    
    def get_unread_emails(self, time_filter=None, max_results=100):
        """
        Fetch unread emails with optional time filter.
        
        Args:
            time_filter: 'today', 'week', or None
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        try:
            query = 'is:unread'
            
            # Add time filter
            if time_filter == 'today':
                # Gmail query for emails received today
                query += ' newer_than:1d'
            elif time_filter == 'week':
                query += ' newer_than:7d'
            
            logger.info(f"Fetching emails with query: {query}")
            
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.info("No unread emails found")
                return []
            
            logger.info(f"Found {len(messages)} unread emails")
            
            # Fetch full message details
            emails = []
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            raise
        except Exception as e:
            logger.error(f"Error fetching emails: {str(e)}")
            raise
    
    def _get_email_details(self, msg_id):
        """Get details for a specific email message."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message.get('payload', {}).get('headers', [])
            subject = self._get_header(headers, 'Subject')
            from_email = self._get_header(headers, 'From')
            date = self._get_header(headers, 'Date')
            
            # Extract body
            body = self._get_email_body(message.get('payload', {}))
            snippet = message.get('snippet', '')
            
            return {
                'id': msg_id,
                'subject': subject,
                'from': from_email,
                'date': date,
                'snippet': snippet,
                'body': body
            }
            
        except Exception as e:
            logger.error(f"Error getting email details for {msg_id}: {str(e)}")
            return None
    
    def _get_header(self, headers, name):
        """Extract header value by name."""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload):
        """Extract email body from payload."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8')
        
        return body[:5000]  # Limit body size to avoid token limits
