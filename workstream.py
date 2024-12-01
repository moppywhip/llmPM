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
        self.pending_context = []

    def add_document(self, document: Document) -> None:
        self.documents.append(document)

    def _build_context_section(self) -> str:
        context = "\nREFERENCE DOCUMENTS:\n"
        for doc in self.documents:
            context += f"\n[{doc.timestamp}] {doc.metadata.get('title', 'Document')}:\n{doc.content}\n"

        if self.pending_context:
            context += "\nPENDING UPDATES:\n"
            for msg in self.pending_context:
                context += f"\n[{msg.timestamp}] {msg.stream_id}: {msg.text}"

        return context

    def _evaluate_message(self, message: IncomingMessage, context_section: str) -> bool:
        evaluation_prompt = f"""
MESSAGE EVALUATION
Workstream: {self.name}
Timestamp: {message.timestamp}
Stream: {message.stream_id}
Content: {message.text}

CRITERIA:
- Significant progress or milestones
- Key decisions or architecture changes
- Important status updates
- Critical issues or blockers
- Performance or reliability impacts

NOTE: MOST messages should be added into pending updates. 
Only when pending updates amount to a substantive update should you respond with "ADD"

CURRENT TIMELINE:
{self.timeline}

CONTEXT:
{context_section}

Respond with exactly one word: ADD or STORE
"""

        try:
            evaluation_response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=10,  # Increased from 1 to allow for proper response
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": evaluation_prompt
                }]
            )

            if not evaluation_response.content:
                print(f"Warning: Empty response received: {evaluation_response}")
                return True  # Default to adding if we get an empty response

            response_text = evaluation_response.content[0].text.strip().upper()
            print(f"Evaluation response: {response_text}")  # Debug line

            return response_text == "ADD"

        except Exception as e:
            print(f"Error during message evaluation: {e}")
            return True  # Default to adding if there's an error

    def process_message(self, message: IncomingMessage) -> bool:
        if message.stream_id not in self.subscribed_streams:
            return False

        context_section = self._build_context_section()
        should_add = self._evaluate_message(message, context_section)

        if not should_add:
            self.pending_context.append(message)
            return False

        timeline_prompt = f"""
WORKSTREAM TIMELINE DOCUMENT
Project: {self.name}
Last Updated: {message.timestamp}

ENTRY FORMAT:
[TIMESTAMP]
<Entry Text>
- Key points and decisions
- Current blockers
- Next steps
REF: Related documents and links

CURRENT TIMELINE:
{self.timeline}

CONTEXT:
{context_section}

NEW UPDATE:
Stream: {message.stream_id}
Message: {message.text}

Remember: ONLY respond with ONE timeline update. Do NOT address me in the response. 
Do NOT write anything meta in the response.
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

        summary_prompt = f"""
WORKSTREAM SUMMARY DOCUMENT
Project: {self.name}

INCLUDE:
- Current project state
- Major milestones and decisions
- Known issues and blockers
- Next critical steps
Maximum 300 words.

TIMELINE: 
{self.timeline}

NEW UPDATE:
{timeline_update}

CONTEXT:
{context_section}

Remember: ONLY respond with the summary document. Do NOT address me in the response. 
Do NOT write anything meta in the response.
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
        self.pending_context = []

        return True