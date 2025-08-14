import os, asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

load_dotenv()                                   # .env convenience
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
GITHUB_PAT = os.getenv("GITHUB_ACCESS_TOKEN")

async def create_mcp_agent(session: ClientSession) -> Agent:
    mcp_tools = MCPTools(session=session)
    await mcp_tools.initialize()                # discover GitHub toolset
    return Agent(
        model=OpenAIChat(id="gpt-4o"),
        tools=[mcp_tools],
        instructions=[
            "You are a GitHub management agent with Model Context Protocol "
            "(MCP) access to GitHub. Help users read code, file issues & PRs, "
            "review commits and automate workflows via natural-language."
        ],
        markdown=True,
        show_tool_calls=True,
    )

async def interactive_agent_loop() -> None:
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "mcp-remote", "https://api.githubcopilot.com/mcp/",
         "--header", f"Authorization: Bearer {GITHUB_PAT}"],
        env={},  # PAT passed to server
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                agent = await create_mcp_agent(session)
                print("✅  Connected to GitHub MCP Agent — type “exit” to quit\n")
                while True:
                    user_input = input("🧑 You: ")
                    if user_input.strip().lower() in {"exit", "quit"}:
                        print("👋  Bye!")
                        break
                    await agent.aprint_response(user_input, stream=True)
                    print("-" * 40)
    except Exception as e:
        print(f"❌  {e}")
    finally:
        await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(interactive_agent_loop())