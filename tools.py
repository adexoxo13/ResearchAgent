"""
AI Research Agent - Core Tools Module

This module implements essential research capabilities for an AI assistant
system, integrating web search, Wikipedia access, and persistent storage 
functionality.
"""

# Import LangChain components for knowledge retrieval and tool integration
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper  # Wikipedia API handler
from langchain.tools import Tool  # Base class for AI-accessible tools
from datetime import datetime  # For timestamping research outputs


def save_to_txt(data: str, filename: str = "research_output.txt"):
    """
    Persists research findings to a text file with structured formatting

    Parameters:
    - data (str): Research content to save (markdown formatted)
    - filename (str): Output file path (default: research_output.txt)

    Returns:
    - str: Confirmation message with file path

    Features:
    - Appends new entries with timestamps
    - Maintains full research history
    - Uses UTF-8 encoding for international text support
    """
    # Generate ISO 8601 timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create structured document header
    formatted_text = f"--- Research Output ---\nTimestamp: {timestamp}\n\n{data}\n\n"

    # Write to file with append mode and proper encoding
    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return f"Data successfully saved to {filename}"


# Create LangChain Tool interface for the save functionality
save_tool = Tool(
    name="save_text_to_file",  # Unique identifier for AI agent
    func=save_to_txt,  # Function to execute
    description="Saves structured research data to a text file.",  # Agent-facing documentation
)

# Configure real-time web search capability using DuckDuckGo
search = DuckDuckGoSearchRun()  # Instantiate search engine client
search_tool = Tool(
    name="search",  # Tool identifier
    func=search.run,  # Executes search queries
    description="Search the web for up-to-date information",  # Usage guidance
)

# Set up Wikipedia integration with controlled parameters
api_wrapper = WikipediaAPIWrapper(
    top_k_results=1,  # Return only most relevant article
    doc_content_chars_max=100,  # Truncate content for concise responses
)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)  # Create executable tool

"""
Tool Configuration Summary:

1. Search Tool (search_tool):
   - Real-time web search using DuckDuckGo
   - Returns raw HTML/plaintext results
   - Ideal for current events and recent developments

2. Wikipedia Tool (wiki_tool):
   - Curated knowledge source
   - Returns verified information snippets
   - Limited to 100 characters for brevity
   - Single result for focused responses

3. Save Tool (save_tool):
   - Persistent storage system
   - Maintains chronological record
   - Structured markdown formatting
   - Non-destructive append operations

Usage Flow:
1. Agent uses search_tool for initial investigation
2. Verifies facts with wiki_tool
3. Saves validated findings with save_tool
4. Process repeats for iterative research
"""
