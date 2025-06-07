# Multi-Agent Research System (MCP)

A powerful research assistant system that leverages multiple AI agents to conduct comprehensive technical research and generate detailed reports. The system combines web search capabilities with advanced language models to create well-structured, thoroughly-researched content.

## Features

- **Multi-Agent Architecture**
  - OrchestratorAgent for high-level research planning and progress evaluation
  - PlannerAgent for creating targeted search strategies
  - ReportAgent for synthesizing findings into coherent reports

- **Flexible LLM Support**
  - Google's Gemini API integration
  - OpenRouter API support for various models (Claude 3, etc.)
  - Easy switching between providers

- **Advanced Search Capabilities**
  - Integration with Tavily API for high-quality source gathering
  - Intelligent deduplication and relevance filtering
  - Depth-based content evaluation

- **Smart Research Planning**
  - Dynamic research strategies based on content depth
  - Automatic progress evaluation
  - Prioritized information gathering

- **Rich Reporting**
  - Well-structured markdown output
  - Proper source citation
  - Code examples with language tags
  - Technical accuracy focus

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp.git
cd mcp

# Create and activate virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

Create a .env file in the project root:

```env
OPENROUTER_API_KEY="your-openrouter-key"
TAVILY_API_KEY="your-tavily-key"
YOUR_SITE_URL="http://localhost:7860"  # Optional: For OpenRouter ranking headers
YOUR_SITE_NAME="My Multi-Agent RAG MCP Server"  # Optional
```

## Required API Keys

| Provider | Required | Purpose | Get Key |
|----------|----------|----------|----------|
| Tavily | Yes | Web search | [Tavily API](https://tavily.com) |
| Gemini | Optional* | LLM provider | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| OpenRouter | Optional* | LLM provider | [OpenRouter](https://openrouter.ai/keys) |

\* At least one LLM provider (either Gemini or OpenRouter) is required

## Usage

### Web Interface

```bash
python mcp_server.py
```

Then open your browser to `http://localhost:7860`

## Architecture

### Components

#### OrchestratorAgent
- Creates comprehensive research plans
- Evaluates research progress
- Ensures thorough topic coverage

#### PlannerAgent
- Generates targeted search strategies
- Prioritizes research needs
- Ensures investigation depth

#### ReportAgent
- Synthesizes research findings
- Generates structured reports
- Maintains technical accuracy

#### MultiAgentSystem
- Coordinates agent interactions
- Manages research workflow
- Handles API integrations

## Configuration

### Supported Models

#### Gemini Models
- gemini-2.0-flash
- gemini-2.0-flash-lite
- gemini-1.5-pro
- gemini-2.5-pro-preview-05-06
- gemini-2.5-flash-preview-04-17

#### OpenRouter Models
- Any valid OpenRouter model ID (e.g., "anthropic/claude-3-opus:beta")

### System Parameters

```python
MAX_SEARCHES_TOTAL = 30    # Maximum number of web searches
MIN_RESULTS_PER_ITEM = 3   # Minimum results before progress check
MAX_ATTEMPTS_PER_ITEM = 2  # Maximum research attempts per item
```

## Output Format

The system generates markdown-formatted reports including:
- Comprehensive introduction
- Technical analysis sections
- Code examples with language tags
- Comparative analysis
- Implementation considerations
- Properly cited sources

## Logging

Logs are stored in the logs directory with:
- Daily rotation
- Debug level for file logging
- Info level for console output
- Structured format for easy parsing

## Development

### Project Structure

```
mcp/
├── agents.py           # Agent implementations
├── mcp_server.py      # Web interface server
├── mcp_client.py      # CLI client
├── utils.py           # Utility functions
├── logger_config.py   # Logging configuration
├── requirements.txt   # Dependencies
└── .env              # Environment variables
```

### Adding New Features

1. Agent Modifications:
   - Extend BaseAgent class
   - Implement required methods
   - Add to MultiAgentSystem

2. Custom Search Sources:
   - Implement in MultiAgentSystem.web_search()
   - Add appropriate API configurations

3. UI Enhancements:
   - Modify create_interface() in mcp_server.py
   - Update CSS in css variable

## Support

For questions and support:
- Open an issue in the GitHub repository
- Detailed bug reports should include logs and steps to reproduce

## Acknowledgments

- [Gradio](https://www.gradio.app/) for the web interface
- [Tavily](https://tavily.com/) for web search capabilities
- [Google Gemini](https://makersuite.google.com/) for language model support
- [OpenRouter](https://openrouter.ai/) for additional model access

## Future Features
- MCP implementation
- CLI-based UI

