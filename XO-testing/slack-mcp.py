import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

async def create_mcp_agent(session):
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()
    return Agent(
        model=OpenAIChat(id="gpt-4.1-nano"),
        tools=[mcp_tools],
        instructions=["You are a Slack Automation agent using Pipedream's Model Context Protocol tools. "
                      "You can read messages, post replies, and trigger workflows on Slack."],
        markdown=True,
        show_tool_calls=True
    )
slack=os.getenv('slack')
async def interactive_agent_loop():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "supergateway", "--sse", slack],
        env={}  # Add any required env vars like SLACK_BOT_TOKEN if Pipedream expects them
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                agent = await create_mcp_agent(session)
                print("✅ Connected to Slack MCP Agent. Type 'exit' to quit.\n")
                while True:
                    user_input = input("🧑 You: ")
                    if user_input.strip().lower() in {"exit", "quit"}:
                        print("👋 Exiting agent session.")
                        break
                    await agent.aprint_response(user_input, stream=True)
                    print("-" * 40)
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(interactive_agent_loop())
    except Exception as e:
        print(f"❌ Error on startup: {e}")
