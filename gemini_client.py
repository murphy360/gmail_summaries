"""
Gemini AI Client for generating email summaries.
"""

import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Gemini AI API."""
    
    def __init__(self):
        """Initialize Gemini AI client."""
        api_key = os.environ.get('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini AI client initialized successfully")
    
    def summarize_emails(self, emails, topic_filter=None):
        """
        Generate a summary of emails using Gemini AI.
        
        Args:
            emails: List of email dictionaries
            topic_filter: Optional topic to focus on
            
        Returns:
            Summary string
        """
        try:
            # Prepare email content for summarization
            email_texts = []
            for idx, email in enumerate(emails, 1):
                email_text = f"""
Email {idx}:
From: {email.get('from', 'Unknown')}
Subject: {email.get('subject', 'No subject')}
Date: {email.get('date', 'Unknown')}
Content: {email.get('snippet', email.get('body', 'No content')[:500])}
---
"""
                email_texts.append(email_text)
            
            combined_emails = "\n".join(email_texts)
            
            # Create prompt
            if topic_filter:
                prompt = f"""Please provide a concise summary of these emails that are related to "{topic_filter}". 
Focus on the key points, important information, and any action items.
Group similar topics together and highlight urgent matters.

Emails to summarize:
{combined_emails}

Summary:"""
            else:
                prompt = f"""Please provide a concise summary of these unread emails.
Focus on the key points, important information, and any action items.
Group similar topics together and highlight urgent matters.

Emails to summarize:
{combined_emails}

Summary:"""
            
            logger.info(f"Generating summary for {len(emails)} emails")
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini AI")
                return "Unable to generate summary at this time."
            
            summary = response.text.strip()
            logger.info("Summary generated successfully")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            # Return a basic summary as fallback
            return self._generate_basic_summary(emails)
    
    def _generate_basic_summary(self, emails):
        """Generate a basic summary without AI (fallback)."""
        if not emails:
            return "No emails to summarize."
        
        summary_parts = [f"You have {len(emails)} unread email(s):\n"]
        
        for idx, email in enumerate(emails[:10], 1):  # Limit to 10 for basic summary
            subject = email.get('subject', 'No subject')
            from_email = email.get('from', 'Unknown sender')
            summary_parts.append(f"{idx}. From {from_email}: {subject}")
        
        if len(emails) > 10:
            summary_parts.append(f"\n... and {len(emails) - 10} more email(s).")
        
        return "\n".join(summary_parts)
