import base64
import atexit
import signal
import sys
from pathlib import Path
from typing import Optional

from agno.agent import Agent
from agno.media import Image
from agno.models.openai import OpenAIChat
from mem0 import Memory

# Initialize the Mem0 client
client = None

def initialize_client():
    """Initialize the Memory client with proper error handling."""
    global client
    if client is None:
        try:
            client = Memory()
            print("✅ Memory client initialized successfully.")
        except Exception as e:
            print(f"❌ Failed to initialize Memory client: {e}")
            print("💡 Try cleaning up any existing Qdrant processes or lock files.")
            raise
    return client

def cleanup_client():
    """Cleanup function to properly handle client shutdown."""
    global client
    if client is not None:
        try:
            # The mem0 client doesn't have a direct close() method,
            # but we can clean up resources by setting it to None
            print("🧹 Cleaning up Memory client...")
            client = None
            print("✅ Memory client cleanup completed.")
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    print(f"\n🛑 Received signal {signum}. Cleaning up...")
    cleanup_client()
    sys.exit(0)

# Register cleanup functions
atexit.register(cleanup_client)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize client on module load
client = initialize_client()

# Define the agent
agent = Agent(
    name="Personal Agent",
    model=OpenAIChat(id="gpt-4.1-nano"),
    description="You are a helpful personal agent that helps me with day to day activities."
                "You can process both text and images.",
    markdown=True
)


def chat_user(
    user_input: Optional[str] = None,
    user_id: str = "alex",
    image_path: Optional[str] = None
) -> str:
    """
    Handle user input with memory integration, supporting both text and images.

    Args:
        user_input: The user's text input
        user_id: Unique identifier for the user
        image_path: Path to an image file if provided

    Returns:
        The agent's response as a string
    """
    if image_path:
        # Convert image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Create message objects for text and image
        messages = []

        if user_input:
            messages.append({
                "role": "user",
                "content": user_input
            })

        messages.append({
            "role": "user",
            "content": {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        })

        # Store messages in memory
        client.add(messages, user_id=user_id, output_format='v1.1')
        print("✅ Image and text stored in memory.")

    if user_input:
        # Search for relevant memories
        memories = client.search(user_input, user_id=user_id)
        memory_context = "\n".join(f"- {m['memory']}" for m in memories['results'])

        # Construct the prompt
        prompt = f"""
You are a helpful personal assistant who helps users with their day-to-day activities and keeps track of everything.

Your task is to:
1. Analyze the given image (if present) and extract meaningful details to answer the user's question.
2. Use your past memory of the user to personalize your answer.
3. Combine the image content and memory to generate a helpful, context-aware response.

Here is what I remember about the user:
{memory_context}

User question:
{user_input}
"""
        # Get response from agent
        if image_path:
            response = agent.run(prompt, images=[Image(filepath=Path(image_path))])
        else:
            response = agent.run(prompt)

        # Store the interaction in memory
        interaction_message = [{"role": "user", "content": f"User: {user_input}\nAssistant: {response.content}"}]
        client.add(interaction_message, user_id=user_id, output_format='v1.1')
        return response.content

    return "No user input or image provided."


def reset_client_if_needed():
    """Reset the client if there are persistent issues."""
    global client
    try:
        if client is not None:
            # Test if client is working
            client.get_all(user_id="test_connection", limit=1)
    except Exception as e:
        print(f"⚠️ Client connection issue detected: {e}")
        print("🔄 Attempting to reinitialize client...")
        client = None
        client = initialize_client()

# Example Usage
if __name__ == "__main__":
    try:
        print("🚀 Starting Personal Agent with Memory...")
        print("💡 Type 'exit' or 'quit' to stop, 'reset' to reset client")
        
        while True:
            try:
                user_input = input("🧑 You: ")
                
                if user_input.strip().lower() in {"exit", "quit"}:
                    print("👋 Exiting agent session.")
                    cleanup_client()
                    break
                elif user_input.strip().lower() == "reset":
                    print("🔄 Resetting Memory client...")
                    client = None
                    client = initialize_client()
                    print("✅ Client reset completed.")
                    continue
                else:
                    # Ensure client is working before processing
                    reset_client_if_needed()
                    
                    response = chat_user(
                        user_input,
                        user_id="alex"
                    )
                    print(f"🤖 Assistant: {response}")
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Try typing 'reset' to reinitialize the client.")
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        cleanup_client()
