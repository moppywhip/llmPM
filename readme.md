# Workstream Prototype

A simple prototype for tracking and summarizing streams of messages using Claude's API. The system maintains both a chronological timeline and an auto-updating summary of events.

## Core Concepts

- **Workstream**: Tracks and summarizes a specific set of activities by monitoring selected message streams
- **Timeline**: An append-only log of all messages in chronological order
- **Summary**: A concise, automatically updated overview of key developments

## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

## Usage Example

```python
from workstream import Workstream, IncomingMessage
from datetime import datetime

# Initialize a workstream
workstream = Workstream(
    name="My Project",
    streams=["channel-1", "channel-2"],
    api_key="your-api-key"
)

# Process a message
message = IncomingMessage(
    timestamp=datetime.now(),
    text="Important update: Phase 1 complete",
    stream_id="channel-1"
)

workstream.process_message(message)

# Get current summary
print(workstream.summary)
```

## Testing

Run the included test script to see the system in action:
```bash
python workstream_test.py
```

The test simulates a software development project but the Workstream class is designed to work with any type of project or workflow.

## Limitations

- Currently uses a simple string for timeline storage
- No persistence layer
- Single-instance only
- No message threading or relationships
