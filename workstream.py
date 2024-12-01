from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import anthropic


@dataclass
class IncomingMessage:
    timestamp: datetime
    text: str
    stream_id: str


@dataclass
class Document:
    content: str
    metadata: Dict[str, str]
    timestamp: datetime


class Workstream:
    def __init__(
            self,
            name: str,
            streams: List[str],
            api_key: str,
            baseline_docs: Optional[List[Document]] = None
    ):
        self.name = name
        self.timeline = ""
        self.summary = ""
        self.subscribed_streams = set(streams)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.documents = baseline_docs or []
        self.pending_context = []  # Store messages that weren't added to timeline

    def add_document(self, document: Document) -> None:
        """Add a new document to the workstream's context."""
        self.documents.append(document)

    def _build_context_section(self) -> str:
        """Build the context section from documents and pending messages."""
        context = "\nRelevant Documents:\n"
        for doc in self.documents:
            context += f"\n[{doc.timestamp}] {doc.metadata.get('title', 'Document')}:\n{doc.content}\n"

        if self.pending_context:
            context += "\nPending Messages:\n"
            for msg in self.pending_context:
                context += f"\n[{msg.timestamp}] {msg.stream_id}: {msg.text}"

        return context

    def process_message(self, message: IncomingMessage) -> bool:
        """
        Process an incoming message using Claude API for timeline and summary updates.
        Returns True if message was added to timeline, False if stored as context.
        """
        if message.stream_id not in self.subscribed_streams:
            return False

        # Build context including documents and pending messages
        context_section = self._build_context_section()

        # Determine if message should be added to timeline
        evaluation_prompt = f"""
        You are evaluating whether a new message should be added to a project timeline.

        Guidelines for adding to timeline:
        - Message represents significant progress, decisions, or milestones
        - Contains actionable information or important status updates
        - Adds new context that future readers would benefit from knowing
        - Avoid adding routine updates or intermediate steps unless they reveal important context

        Current Timeline: {self.timeline}

        Context Information: {context_section}

        New Message:
        Timestamp: {message.timestamp}
        Stream: {message.stream_id}
        Message: {message.text}

        Should this message be added to the timeline? Respond with either:
        "ADD" - If the message should be added to the timeline
        "STORE" - If the message should be stored as context for future reference

        Your response should only be one of these two words.
        """

        evaluation_response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1,
            temperature=0,
            messages=[{
                "role": "user",
                "content": evaluation_prompt
            }]
        )

        should_add = evaluation_response.content[0].text.strip() == "ADD"

        if not should_add:
            self.pending_context.append(message)
            return False

        # Update timeline with the new message
        timeline_prompt = f"""
        You are maintaining an append-only timeline of project events. Write updates in a clear, professional style that a project manager would use.

        Guidelines:
        - Format each entry with timestamp, status, and detailed update
        - Include relevant links and references
        - Focus on progress, blockers, decisions, and next steps
        - Be specific about what was accomplished or what needs attention
        - Keep tone professional and factual
        - Incorporate relevant context from documents and pending messages when appropriate

        Example format:
        [2024-03-01 10:00 AM] Status: In Progress
        Completed initial architecture review for data pipeline redesign. Key decisions:
        - Selected Apache Kafka for message queue
        - Identified necessary schema changes (see: docs.internal/schema/v2)
        Next steps: Team to begin implementation of consumer services by EOW.
        Blockers: None currently
        References: RFC-2023-45, Architecture Diagram (confluence/arch/pipeline-v2)

        Current Timeline: {self.timeline}

        {context_section}

        Add this new message as a well-structured update:
        Timestamp: {message.timestamp}
        Message: {message.text}
        """

        timeline_response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
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

        {context_section}
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

        # Clear any pending messages that were incorporated into this update
        self.pending_context = []

        return True