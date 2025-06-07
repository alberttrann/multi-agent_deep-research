import os
import json
import logging
from datetime import datetime
import gradio as gr
import google.generativeai as genai
from tavily import TavilyClient
from dotenv import load_dotenv
from logger_config import setup_logging
from typing import List, Dict, Any, Optional
from utils import validate_response, parse_research_results, format_sources_section
from agents import OrchestratorAgent, PlannerAgent, ReportAgent

# Set up logging
loggers = setup_logging()
server_logger = loggers['server']

class MultiAgentSystem:
    def __init__(self, use_gemini=True, gemini_api_key=None, gemini_model=None, 
                 tavily_api_key=None, openrouter_api_key=None, openrouter_model=None):
        self.use_gemini = use_gemini
        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        self.tavily_api_key = tavily_api_key
        self.openrouter_api_key = openrouter_api_key
        self.openrouter_model = openrouter_model

        # Initialize agents
        self.orchestrator = OrchestratorAgent(
            use_gemini=use_gemini, 
            api_key=gemini_api_key if use_gemini else openrouter_api_key,
            openrouter_model=openrouter_model,
            gemini_model=gemini_model
        )
        self.planner = PlannerAgent(
            use_gemini=use_gemini, 
            api_key=gemini_api_key if use_gemini else openrouter_api_key,
            openrouter_model=openrouter_model,
            gemini_model=gemini_model
        )
        self.report_agent = ReportAgent(
            use_gemini=use_gemini, 
            api_key=gemini_api_key if use_gemini else openrouter_api_key,
            openrouter_model=openrouter_model,
            gemini_model=gemini_model
        )

        # Initialize Tavily client
        if tavily_api_key:
            self.tavily_client = TavilyClient(api_key=tavily_api_key)
        else:
            self.tavily_client = None

    def web_search(self, query: str) -> List[Dict[str, str]]:
        """Perform web search using Tavily"""
        if not self.tavily_client:
            raise ValueError("Tavily API key not provided")
        
        try:
            response = self.tavily_client.search(
                query, 
                search_depth="advanced",  # Only 'basic' or 'advanced' are allowed
                max_results=5,  # Limit results to keep responses focused
                async_search=True,  # Use async search for better performance
                timeout=30  # 30 second timeout
            )
            return response.get('results', [])
        except Exception as e:
            server_logger.error(f"Web search failed: {str(e)}")
            raise  # Re-raise the exception to handle it in the calling code
    
    def process_query(self, query: str) -> str:
        """Process a research query using the multi-agent system"""
        try:
            # Step 1: Create a structured research plan
            server_logger.info("Creating research plan...")
            research_plan = self.orchestrator.create_research_plan(query)
            server_logger.info(f"Generated research plan: {json.dumps(research_plan, indent=2)}")
            
            # Step 2: Initialize research process
            all_search_results = []
            MAX_SEARCHES_TOTAL = 30  # Total search limit
            MIN_RESULTS_PER_ITEM = 2  # Minimum results before checking progress
            search_count = 0
            seen_urls = set()  # Track seen URLs to avoid duplicates
            
            # Step 3: Conduct initial research
            while search_count < MAX_SEARCHES_TOTAL:
                # Evaluate current progress
                current_results = [r['content'] for r in all_search_results]
                progress = self.orchestrator.evaluate_research_progress(research_plan, current_results)
                
                # Check if we have completed all aspects
                if all(progress.values()):
                    server_logger.info("Research complete - all aspects covered")
                    break
                
                # Get prioritized list of unfulfilled research needs
                remaining_items = self.planner.prioritize_unfulfilled_requirements(research_plan, progress)
                if not remaining_items:
                    break
                
                # Research each remaining item
                for item_type, research_item in remaining_items:
                    if search_count >= MAX_SEARCHES_TOTAL:
                        server_logger.info(f"Reached maximum total searches ({MAX_SEARCHES_TOTAL})")
                        break
                    
                    server_logger.info(f"Researching {item_type}: {research_item}")
                    search_queries = self.planner.create_search_strategy(research_item, item_type)
                    
                    # Conduct searches for this item
                    item_results = []
                    for search_query in search_queries:
                        if search_count >= MAX_SEARCHES_TOTAL:
                            break
                        
                        # Ensure search query is a simple string
                        query_str = str(search_query).strip()
                        if not query_str:
                            continue
                        
                        server_logger.info(f"Searching for: {query_str}")
                        results = self.web_search(query_str)
                        
                        # Deduplicate results based on URL
                        new_results = []
                        for result in results:
                            url = result.get('url')
                            if url and url not in seen_urls:
                                seen_urls.add(url)
                                new_results.append(result)
                        
                        item_results.extend(new_results)
                        search_count += 1
                        
                        # Check if we have enough results for this item
                        if len(item_results) >= MIN_RESULTS_PER_ITEM:
                            break
                    
                    all_search_results.extend(item_results)
            
            # Step 4: Generate final report
            server_logger.info("Generating final report...")
            contexts, sources = parse_research_results(all_search_results)
            report = self.report_agent.generate_report(
                query=query,
                research_plan=research_plan,
                research_results=contexts
            )
            
            # Add sources section to the report
            report += "\n\n" + format_sources_section(sources)
            
            return report

        except Exception as e:
            server_logger.error(f"Error in process_query: {str(e)}", exc_info=True)
            raise

# Global UI component for progress tracking
progress_output = None

def create_interface():
    """Create the Gradio interface with API key inputs"""
    global progress_output

    css = """
    .log-container { 
        margin: 16px 0;
    }
    .log-output {
        font-family: monospace;
        white-space: pre !important;
        height: 300px;
        overflow-y: auto;
        background-color: #1e1e1e !important;
        color: #d4d4d4 !important;
        padding: 10px;
        border-radius: 4px;
    }
    .research-progress {
        position: relative;
    }
    .minimize-btn {
        position: absolute;
        right: 10px;
        top: 10px;
    }
    """

    with gr.Blocks(title="Multi-Agent Research System", css=css) as interface:
        gr.Markdown("""# Multi-Agent Research System
        This system uses multiple AI agents to perform comprehensive research and analysis.
        Please provide your API keys to begin.""")

        # Progress tracking container with minimize button
        with gr.Row(elem_classes="log-container"):
            with gr.Column(elem_classes="research-progress"):
                progress_output = gr.Textbox(
                    value="Waiting to begin research...",
                    elem_classes=["log-output"],
                    show_label=False,
                    lines=10,
                    max_lines=20,
                    interactive=False
                )
                minimize_btn = gr.Button("🔽", elem_classes="minimize-btn")

        with gr.Row():
            api_type = gr.Radio(
                choices=["Gemini", "OpenRouter"], 
                label="Choose API Type", 
                value="Gemini",
                info="Select which API to use for the agents"
            )

        with gr.Row():
            with gr.Column():
                gemini_key = gr.Textbox(
                    label="Gemini API Key", 
                    placeholder="Enter your Gemini API key",
                    type="password"
                )
                gemini_model = gr.Dropdown(
                    label="Gemini Model",
                    choices=[
                        "gemini-2.0-flash",
                        "gemini-2.0-flash-lite",
                        "gemini-1.5-pro",
                        "gemini-2.5-pro-preview-05-06",
                        "gemini-2.5-flash-preview-04-17"
                    ],
                    value="gemini-2.0-flash",
                    info="Choose Gemini model version"
                )
            with gr.Column():
                tavily_key = gr.Textbox(
                    label="Tavily API Key (Required)", 
                    placeholder="Enter your Tavily API key",
                    type="password"
                )

        with gr.Row():
            with gr.Column():
                openrouter_key = gr.Textbox(
                    label="OpenRouter API Key", 
                    placeholder="Enter your OpenRouter API key",
                    type="password",
                    visible=False
                )
                openrouter_model = gr.Textbox(
                    label="OpenRouter Model ID", 
                    placeholder="e.g., anthropic/claude-3-opus:beta",
                    info="Enter any valid OpenRouter model ID",
                    value="anthropic/claude-3-opus:beta",
                    visible=False
                )

        query_input = gr.Textbox(
            label="Research Query",
            placeholder="Enter your research question...",
            lines=3,
            info="Enter a detailed research question or topic to investigate"
        )

        submit_btn = gr.Button("Begin Research", variant="primary")
        output = gr.Markdown(label="Research Results")

        def update_api_visibility(choice):
            if choice == "Gemini":
                return {
                    gemini_key: gr.update(visible=True),
                    gemini_model: gr.update(visible=True),
                    openrouter_key: gr.update(visible=False),
                    openrouter_model: gr.update(visible=False)
                }
            else:
                return {
                    gemini_key: gr.update(visible=False),
                    gemini_model: gr.update(visible=False),
                    openrouter_key: gr.update(visible=True),
                    openrouter_model: gr.update(visible=True)
                }

        def run_research(query, api_type, gemini_key, gemini_model, tavily_key, openrouter_key, openrouter_model):
            try:
                if not tavily_key:
                    server_logger.error("Missing Tavily API key")
                    return "", "Please provide a Tavily API key for web search capability."
                
                if api_type == "Gemini" and not gemini_key:
                    server_logger.error("Missing Gemini API key")
                    return "", "Please provide a Gemini API key when using Gemini mode."
                    
                if api_type == "OpenRouter" and not openrouter_key:
                    server_logger.error("Missing OpenRouter API key")
                    return "", "Please provide an OpenRouter API key when using OpenRouter mode."

                # Initialize handlers for console output capture
                class LogCaptureHandler(logging.Handler):
                    def __init__(self):
                        super().__init__()
                        self.logs = []

                    def emit(self, record):
                        msg = self.format(record)
                        self.logs.append(msg)
                        # Return update instead of trying to update directly
                        return gr.update(value="\n".join(self.logs))

                # Add handler to capture logs
                log_handler = LogCaptureHandler()
                log_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
                server_logger.addHandler(log_handler)

                system = MultiAgentSystem(
                    use_gemini=(api_type == "Gemini"),
                    gemini_api_key=gemini_key if api_type == "Gemini" else None,
                    gemini_model=gemini_model if api_type == "Gemini" else None,
                    tavily_api_key=tavily_key,
                    openrouter_api_key=openrouter_key if api_type == "OpenRouter" else None,
                    openrouter_model=openrouter_model if api_type == "OpenRouter" else None
                )

                # Run research
                result = system.process_query(query)
                
                # Clean up log handler and return logs with gr.update()
                server_logger.removeHandler(log_handler)
                return gr.update(value="\n".join(log_handler.logs)), result
                
            except Exception as e:
                server_logger.error(f"Research failed: {str(e)}", exc_info=True)
                return gr.update(value=f"ERROR: Research failed: {str(e)}"), f"Research failed: {str(e)}"

        api_type.change(
            fn=update_api_visibility,
            inputs=[api_type],
            outputs=[gemini_key, gemini_model, openrouter_key, openrouter_model]
        )

        submit_btn.click(
            fn=run_research,
            inputs=[query_input, api_type, gemini_key, gemini_model, tavily_key, openrouter_key, openrouter_model],
            outputs=[progress_output, output],
            show_progress="full"
        )

        gr.Examples(
            examples=[
                ["What are the latest advances in transformer architecture optimizations?"],
                ["Explain the mathematical foundations of diffusion models"],
                ["Compare and analyze different approaches to few-shot learning"]
            ],
            inputs=query_input
        )

    return interface

if __name__ == "__main__":
    try:
        server_logger.info("Starting Gradio server")
        interface = create_interface()
        interface.launch(
            server_name="0.0.0.0",
            share=False,
            debug=True
        )
    except Exception as e:
        server_logger.error(f"Failed to start Gradio server: {str(e)}", exc_info=True)
        raise