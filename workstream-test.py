from datetime import datetime, timedelta
from workstream import Workstream, IncomingMessage, Document
import os
from pathlib import Path

def create_baseline_docs() -> list[Document]:
    """Create baseline documents for the auth service project."""
    return [
        Document(
            content="""
            Authentication Service Overview

            Current Implementation:
            - JWT-based authentication
            - Direct database lookups for token validation
            - Average latency: 150ms
            - Peak load: 1000 req/sec

            Known Issues:
            - High database load during peak hours
            - Occasional timeout errors under heavy load
            - Token revocation requires full database scan

            Performance Requirements:
            - Target latency: <50ms
            - Support for 2000 req/sec
            - Immediate token revocation capability
            """,
            metadata={
                "title": "Auth Service Technical Spec",
                "type": "specification",
                "version": "1.0"
            },
            timestamp=datetime(2024, 2, 28, 15, 0)
        ),
        Document(
            content="""
            Redis Caching Implementation Guidelines

            Requirements:
            1. Implement write-through caching
            2. Set up connection pooling
            3. Configure proper error handling and retries
            4. Implement monitoring and alerts

            Success Criteria:
            - 50% reduction in database load
            - 99th percentile latency under 100ms
            - Zero data inconsistency incidents
            """,
            metadata={
                "title": "Redis Caching RFC",
                "type": "rfc",
                "version": "1.0"
            },
            timestamp=datetime(2024, 2, 29, 10, 0)
        )
    ]


def create_test_messages() -> list[IncomingMessage]:
    """Create a series of test messages simulating a software development timeline."""
    base_time = datetime(2024, 3, 1, 10, 0)

    return [
        # Day 1: Project Kickoff
        IncomingMessage(
            timestamp=base_time,
            stream_id="auth-service",
            text="Starting implementation of Redis caching for auth tokens to improve service performance"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(hours=2),
            stream_id="auth-service",
            text="Team discussion: Considering TTL-based approach vs explicit invalidation for cache management"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(hours=4),
            stream_id="backend-team",
            text="Architecture decision: Will implement both TTL (24h) and explicit invalidation approaches"
        ),

        # Day 2: Development Progress
        IncomingMessage(
            timestamp=base_time + timedelta(days=1),
            stream_id="auth-service",
            text="Initial implementation complete, PR opened for review"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(days=1, hours=4),
            stream_id="auth-service",
            text="PR feedback received: Need to improve error handling and add connection retries"
        ),

        # Day 3: Testing Phase
        IncomingMessage(
            timestamp=base_time + timedelta(days=2),
            stream_id="auth-service",
            text="Changes merged, beginning load testing in staging"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(days=2, hours=3),
            stream_id="auth-service",
            text="Load testing revealed memory leak in connection pool"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(days=2, hours=5),
            stream_id="auth-service",
            text="Memory leak fixed, new tests show stable performance"
        ),

        # Day 4: Deployment
        IncomingMessage(
            timestamp=base_time + timedelta(days=3),
            stream_id="backend-team",
            text="Feature approved for production, starting canary deployment"
        ),
        IncomingMessage(
            timestamp=base_time + timedelta(days=3, hours=6),
            stream_id="auth-service",
            text="Canary deployment successful. Performance metrics show 60% latency reduction"
        )
    ]


def ensure_test_folder():
    """Create test folder if it doesn't exist."""
    test_dir = Path("test")
    test_dir.mkdir(exist_ok=True)
    return test_dir


def main():
    # Initialize workstream
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    # Create test directory and get path
    test_dir = ensure_test_folder()

    # Create workstream with baseline documents
    workstream = Workstream(
        name="Auth Service Caching Feature",
        streams=["auth-service", "backend-team"],
        api_key=api_key,
        baseline_docs=create_baseline_docs()
    )

    # Process messages
    messages = create_test_messages()

    for i, message in enumerate(messages, 1):
        print(f"\nProcessing message {i}/{len(messages)}")
        print(f"Timestamp: {message.timestamp}")
        print(f"Stream: {message.stream_id}")
        print(f"Content: {message.text}")

        was_added = workstream.process_message(message)

        print(f"\nMessage {'added to timeline' if was_added else 'stored as context'}")

        # Write timeline and summary to files
        timeline_path = test_dir / "timeline.txt"
        summary_path = test_dir / "summary.txt"

        with open(timeline_path, "w") as t:
            t.write(workstream.timeline)

        with open(summary_path, "w") as s:
            s.write(workstream.summary)

        # Optional: uncomment to see full timeline
        print("\nFull Timeline:")
        print(workstream.timeline)

        input("Press Enter to continue to next message...")


if __name__ == "__main__":
    main()