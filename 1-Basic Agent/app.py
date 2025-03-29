<<<<<<< HEAD
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


agent=Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description="You are an assistant please reply based on the user queries",
    tools=[DuckDuckGoTools()],
    markdown=True
)

agent.print_response("who won the Indian Premiere League in 2024",stream=True)
=======
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


agent=Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description="You are an assistant please reply based on the user queries",
    tools=[DuckDuckGoTools()],
    markdown=True
)

agent.print_response("who won the Indian Premiere League in 2024",stream=True)
>>>>>>> 09cb6032527599c31bca76077440da88c03ead9d
