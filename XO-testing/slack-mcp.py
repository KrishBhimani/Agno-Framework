"""
slack_mcp_agent.py
──────────────────
Interactive Agno agent with Model-Context-Protocol (MCP) access to Slack.

Prerequisites
  1. Install the MCP server (uses npx so no global install required):
        npx -y @modelcontextprotocol/server-slack-user --help
  2. Create/get a **User OAuth Token** (starts with xoxp-) for a Slack app
     that’s installed in the workspace, and note your Workspace / Team ID.
     Required scopes for the sample tools: channels:read, chat:write,
     reactions:write, im:history, users:read.
  3. Add these to your .env or shell environment:
        SLACK_TOKEN=xoxp-…          # user token, NOT a bot xoxb token
        SLACK_TEAM_ID=T01234567     # workspace / team ID
        OPENAI_API_KEY=sk-…
"""

import os
import asyncio
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

# ─── Load secrets ──────────────────────────────────────────────────────────
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or ""

SLACK_TOKEN   = os.getenv("SLACK_TOKEN")   or ""
SLACK_TEAM_ID = os.getenv("SLACK_TEAM_ID") or ""

# ─── Build the Agno agent ─────────────────────────────────────────────────
async def create_mcp_agent(session: ClientSession) -> Agent:
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[mcp_tools],
        instructions=[
            "You are a Slack Workplace Assistant with Model Context Protocol "
            "(MCP) access. You can list channels, post messages, reply in "
            "threads, add reactions, and read message history to help users "
            "coordinate work in Slack."
        ],
        markdown=True,
        show_tool_calls=True,
    )

# ─── REPL loop ─────────────────────────────────────────────────────────────
async def interactive_agent_loop() -> None:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-slack-user"],
        env={
            "SLACK_TOKEN": SLACK_TOKEN,
            "SLACK_TEAM_ID": SLACK_TEAM_ID,
        },
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

    except Exception as err:
        print(f"❌ Error: {err}")
    finally:
        # graceful shutdown delay
        await asyncio.sleep(0.1)

# ─── Entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(interactive_agent_loop())
    except Exception as err:
        print(f"❌ Startup error: {err}")
