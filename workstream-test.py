from datetime import datetime, timedelta
from workstream import Workstream, IncomingMessage
import os


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

        # Day 2: Development
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

        # Day 3: Testing
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


def main():
    # Initialize workstream
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    workstream = Workstream(
        name="Auth Service Caching Feature",
        streams=["auth-service", "backend-team"],
        api_key=api_key
    )

    # Process messages
    messages = create_test_messages()

    for i, message in enumerate(messages, 1):
        print(f"\nProcessing message {i}/{len(messages)}")
        print(f"Timestamp: {message.timestamp}")
        print(f"Stream: {message.stream_id}")
        print(f"Content: {message.text}")

        workstream.process_message(message)

        print("\nCurrent Summary:")
        print("-" * 50)
        print(workstream.summary)
        print("-" * 50)

        # Optional: uncomment to see full timeline
        # print("\nFull Timeline:")
        # print(workstream.timeline)

        input("Press Enter to continue to next message...")


if __name__ == "__main__":
    main()