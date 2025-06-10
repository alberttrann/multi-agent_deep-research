import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from markdown_it import MarkdownIt

def validate_response(response: Any, expected_type: type) -> bool:
    """Validate response type and structure"""
    if not isinstance(response, expected_type):
        return False
    return True

def format_source_content(
    title: str,
    url: str,
    date: str,
    content: str,
    source_type: str
) -> str:
    """Format source content with consistent styling"""
    return f"""### Source: {title}
URL: {url}
Date: {date if date else 'Not available'}
Type: {source_type}

**Key Content:**
{content}

---"""

def parse_research_results(results: List[Dict[str, Any]]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse and validate research results"""
    contexts = []
    sources = []
    
    for result in results:
        title = result.get("title", "").strip()
        content = result.get("content", "").strip()
        url = result.get("url", "").strip()
        date = result.get("published_date", "").strip()
        
        if title and content:
            source_type = (
                "research_paper"
                if "arxiv.org" in url or "paper" in url.lower()
                else "article"
            )
            
            sources.append({
                "title": title,
                "url": url,
                "date": date if date else "Date not available",
                "type": source_type
            })
            
            contexts.append(
                format_source_content(title, url, date, content, source_type)
            )
    
    return contexts, sources

def format_sources_section(sources: List[Dict[str, str]]) -> str:
    """Format the sources section of the response with proper markdown"""
    sources_section = "\n\n## Sources Cited\n\n"
    
    if not sources:
        return sources_section + "No sources were found during the research phase."
        
    research_papers = [s for s in sources if s['type'] == 'research_paper']
    articles = [s for s in sources if s['type'] == 'article']
    
    if research_papers:
        sources_section += "\n### Research Papers\n"
        for idx, source in enumerate(research_papers, 1):
            sources_section += f"{idx}. [{source['title']}]({source['url']}) - {source['date']}\n"
    
    if articles:
        sources_section += "\n### Technical Articles & Resources\n"
        for idx, source in enumerate(articles, 1):
            sources_section += f"{idx}. [{source['title']}]({source['url']}) - {source['date']}\n"
            
    # Add line break after sources section
    sources_section += "\n"
    return sources_section

def save_markdown_report(content: str) -> str:
    """Save markdown content to a file and return the file path
    
    Args:
        content: The markdown content to save
        
    Returns:
        str: Path to the generated markdown file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs("generated_reports", exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.md"
        file_path = os.path.join("generated_reports", filename)
        
        # Save markdown content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return file_path
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to save markdown report: {str(e)}")
        raise

def convert_to_html(markdown_content: str) -> str:
    """Convert markdown to styled HTML and save to file
    
    Args:
        markdown_content: The markdown content to convert
        
    Returns:
        str: Path to the generated HTML file
    """
    try:
        # Initialize markdown parser
        md = MarkdownIt('commonmark', {'html': True})
        
        # Convert markdown to HTML
        html_content = md.render(markdown_content)
        
        # Add styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 900px;
                    margin: 40px auto;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{ color: #2c3e50; }}
                code {{
                    background-color: #f5f5f5;
                    padding: 2px 4px;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Monaco', 'Andale Mono', monospace;
                }}
                pre {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                }}
                blockquote {{
                    border-left: 4px solid #2c3e50;
                    margin: 0;
                    padding-left: 20px;
                    color: #666;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{ background-color: #f5f5f5; }}
                img {{ max-width: 100%; height: auto; }}
                .sources {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #eee;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Create output directory if it doesn't exist
        os.makedirs("generated_reports", exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_path = os.path.join("generated_reports", f"report_{timestamp}.html")
        
        # Save HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(styled_html)
            
        return html_path
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to convert markdown to HTML: {str(e)}")
        raise