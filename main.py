# mcp_it_assistant.py
# Simple MCP server for IT support using a text user guide

from mcp.server.fastmcp import FastMCP
import re

# Create MCP server
mcp = FastMCP("IT_Assistant")


def load_guide(filepath="C:/Users/Nicole/Documents/formation/Agentique/mpc/user_guide.txt"):
    """Load and split the user guide into searchable chunks."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = []

        # Split by headers or numbered sections
        sections = re.split(
            r"\n(?=(?:#{1,3}\s|\d+\.\s+[A-Z]))",
            text
        )

        for section in sections:
            section = section.strip()

            if len(section) > 50:  # Keep meaningful sections
                chunks.append({
                    "content": section[:2000],  # Limit chunk size
                    "size": len(section)
                })

        return chunks

    except FileNotFoundError:
        return [{
            "content": "User guide not found. Please ensure user_guide.txt exists.",
            "size": 0
        }]


# Load guide at startup
GUIDE_CHUNKS = load_guide()


@mcp.tool()
def search_guide(query: str) -> str:
    """
    Search the IT user guide for relevant information.
    Use when the user asks about an IT issue.
    """
    query_lower = query.lower()
    results = []

    for chunk in GUIDE_CHUNKS:
        content_lower = chunk["content"].lower()

        # Score based on keyword matches
        score = sum(
            1 for word in query_lower.split()
            if word in content_lower
        )

        if score > 0:
            results.append((score, chunk["content"]))

    results.sort(reverse=True)

    if results:
        top_results = [r[1] for r in results[:2]]
        return "\n\n---\n\n".join(top_results)

    return "No relevant information found in the user guide."


@mcp.tool()
def list_topics() -> str:
    """List available topics from the guide."""
    topics = []

    for chunk in GUIDE_CHUNKS[:10]:
        first_line = chunk["content"].split("\n")[0][:100]
        topics.append(f"- {first_line}")

    return "Available topics:\n" + "\n".join(topics)


@mcp.prompt()
def it_support_prompt(issue: str) -> str:
    """Template for IT support conversations."""
    return f"""
You are an IT support assistant. Help the user with their issue.

User Issue:
{issue}

Instructions:
1. Use the search_guide tool to find relevant info.
2. Provide a clear, step-by-step solution.
"""
    

if __name__ == "__main__":
    mcp.run(transport="stdio")