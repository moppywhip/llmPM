from dataclasses import dataclass
from datetime import datetime
from typing import List
import anthropic

@dataclass
class IncomingMessage:
    timestamp: datetime
    text: str
    stream_id: str

class Workstream:
    def __init__(
        self,
        name: str,
        streams: List[str],
        api_key: str
    ):
        self.name = name
        self.timeline = ""
        self.summary = ""
        self.subscribed_streams = set(streams)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def process_message(self, message: IncomingMessage) -> None:
        """
        Process an incoming message using Claude API for timeline and summary updates.
        """
        if message.stream_id in self.subscribed_streams:
            # Update timeline
            timeline_prompt = f"""
            You are maintaining an append-only timeline of events.
            Follow these rules:
            - Add the new message as a new entry with its timestamp
            - Maintain chronological order
            - Use consistent formatting
            - Preserve all previous timeline entries
            - Focus on facts and key information
            
            Current Timeline: {self.timeline}
            
            Add this new message:
            Timestamp: {message.timestamp}
            Message: {message.text}
            """
            
            timeline_response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": timeline_prompt
                }]
            )
            timeline_update = timeline_response.content[0].text
            
            # Update summary
            summary_prompt = f"""
            You are maintaining a concise summary of events and progress.
            Follow these rules:
            - Keep the summary focused on key updates, changes, and milestones
            - Maintain a clear narrative of the overall progression
            - Keep the summary under 300 words
            - Update based on the new timeline entry while preserving important context
            - Be objective and factual
            
            Prior Timeline: {self.timeline}
            New Timeline Entry: {timeline_update}
            Current Summary: {self.summary}
            """
            
            summary_response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": summary_prompt
                }]
            )
            self.summary = summary_response.content[0].text
            self.timeline += "\n" + timeline_update
