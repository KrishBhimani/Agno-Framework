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
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

async def create_mcp_agent(session):
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[mcp_tools],
        instructions=[
            "You are a Web Research agent with Model Context Protocol (MCP) access to Perplexity Sonar.",
            "Use the MCP tool(s) from the Perplexity Ask server to run live web research and return cited, up-to-date results."
        ],
        markdown=True,
        show_tool_calls=True
    )

async def interactive_agent_loop():
    # Run the Perplexity Ask MCP server locally (stdio transport)
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "server-perplexity-ask"],
        env={"PERPLEXITY_API_KEY": PERPLEXITY_API_KEY}
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                agent = await create_mcp_agent(session)
                print("✅ Connected to Perplexity MCP (stdio). Type 'exit' to quit.\n")
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
