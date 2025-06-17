from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, save_tool
import os


# -----------------------------------------------------------------------------
# Response Model Definition
# -----------------------------------------------------------------------------
class ResearchResponse(BaseModel):
    """
    Structured output format for research results validation.
    Fields:
    - topic: Main research subject (string)
    - summary: Consolidated findings (markdown formatted)
    - sources: Reference URLs (list)
    - tools_used: Utilized tools (list)
    """

    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]


# -----------------------------------------------------------------------------
# Model Configuration
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set!")

# Initialize language model (Flexible model selection)
llm = ChatOpenAI(
    model="gpt-4o-mini",  # Current model - see alternatives below
    openai_api_key=OPENAI_API_KEY,
)

"""
Alternative Model Options:

OpenAI Models:
- gpt-4-turbo-preview: Latest GPT-4 version (128k context)
- gpt-4-0125-preview: Previous GPT-4 iteration
- gpt-3.5-turbo: Faster/cheaper for simple queries
- gpt-4o-mini: Current optimized research model

Open Source/Alternative Models (would require code changes):
- Anthropic Claude 3 (via langchain-anthropic)
- Mistral-7B/Mixtral (via Ollama/LiteLLM)
- Llama 3 (via llama.cpp)
- Google Gemini Pro (via langchain-google-genai)

Considerations when changing models:
- Pricing structure changes
- Different context window sizes
- Varying output formats
- Alternate initialization parameters
"""

# -----------------------------------------------------------------------------
# Output Parsing Setup
# -----------------------------------------------------------------------------
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# -----------------------------------------------------------------------------
# Prompt Engineering
# -----------------------------------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a research assistant that will
            help generate a research paper. Answer the
            user query and use the necessary tools. Wrap 
            the output in this format and provide no 
            other text\n{format_instructions}""",
        ),
        ("placeholder", "{chat_history}"), 
        # Conversation context storage
        ("human", "{query}"), 
        # User input placeholder
        ("placeholder", "{agent_scratchpad}"),  
        # Agent's working memory
    ]
).partial(format_instructions=parser.get_format_instructions())

# -----------------------------------------------------------------------------
# Tool Configuration
# -----------------------------------------------------------------------------
tools = [search_tool, save_tool]  # Core research tools
# tools = [search_tool, wiki_tool, save_tool]  # Uncomment for Wikipedia integration

# -----------------------------------------------------------------------------
# Agent Assembly
# -----------------------------------------------------------------------------
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True  # Enable detailed execution logging
)

"""
Key Architecture Decisions:

1. Model Flexibility:
   - Current OpenAI implementation can be swapped for other LLMs
   - Maintains same interface through LangChain abstractions

2. Tool Chaining:
   - Sequential execution of search -> analysis -> saving
   - Modular design allows adding new tools

3. Validation Layer:
   - Pydantic ensures structured output
   - Prevents malformed responses from reaching users

To switch models:
1. Change model name in ChatOpenAI initialization
2. Adjust prompt templates if needed
3. Update error handling for new model's quirks
4. Modify temperature for desired creativity level
"""
