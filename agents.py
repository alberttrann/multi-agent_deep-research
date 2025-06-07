import os
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, use_gemini: bool = True, api_key: Optional[str] = None, 
                 openrouter_model: Optional[str] = None, gemini_model: Optional[str] = None):
        self.use_gemini = use_gemini
        if use_gemini:
            genai.configure(api_key=api_key)
            self.gemini_model = gemini_model or "gemini-pro"
        else:
            self.openrouter_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key
            )
            self.model = openrouter_model or "anthropic/claude-3-opus:beta"

    def _generate_with_gemini(self, prompt: str, system_prompt: str) -> str:
        try:
            model = genai.GenerativeModel(model_name=self.gemini_model)
            # Combine system prompt and user prompt for Gemini
            combined_prompt = f"{system_prompt}\n\nUser request: {prompt}"
            response = model.generate_content(
                combined_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise

    def _generate_with_openrouter(self, prompt: str, system_prompt: str) -> str:
        completion = self.openrouter_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        return completion.choices[0].message.content

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            if self.use_gemini:
                return self._generate_with_gemini(prompt, system_prompt)
            else:
                return self._generate_with_openrouter(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise

class OrchestratorAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert research planner that develops comprehensive research strategies.
        Your role is to create structured research plans that identify what information is needed and why.
        Focus on the logical flow of information needed to answer the query comprehensively."""

    def create_research_plan(self, query: str) -> Dict[str, List[str]]:
        """Create a structured research plan with clear objectives"""
        prompt = f"""Create a detailed research plan for the following query: {query}

        Return a JSON object with the following structure:
        {{
            "core_concepts": ["list of fundamental concepts that need to be understood"],
            "key_questions": ["specific questions that need to be answered"],
            "information_requirements": ["specific pieces of information needed to answer each question"],
            "research_priorities": ["ordered list of research priorities"]
        }}

        Make sure the plan flows logically and each item contributes to answering the main query."""
        
        response = self.generate(prompt, self.system_prompt)
        try:
            # Clean the response of any markdown formatting
            cleaned_response = response.strip().replace('```json', '').replace('```', '').strip()
            plan = json.loads(cleaned_response)
            logger.info(f"Generated research plan: {json.dumps(plan, indent=2)}")
            return plan
        except:
            logger.error(f"Failed to parse research plan: {response}")
            # Return a basic plan structure if parsing fails
            return {
                "core_concepts": [query],
                "key_questions": [query],
                "information_requirements": [query],
                "research_priorities": [query]
            }

    def evaluate_research_progress(self, plan: Dict[str, List[str]], gathered_info: List[str]) -> Dict[str, bool]:
        """Evaluate if we have enough information for each aspect of the plan"""
        prompt = f"""Based on the research plan and gathered information, evaluate if we have sufficient information for each aspect.

        Research Plan:
        {json.dumps(plan, indent=2)}

        Gathered Information:
        {chr(10).join(gathered_info)}

        Return a JSON object indicating completeness for each aspect:
        {{
            "core_concepts": true/false,
            "key_questions": true/false,
            "information_requirements": true/false
        }}
        Only return true if the gathered information adequately covers that aspect."""

        response = self.generate(prompt, self.system_prompt)
        try:
            cleaned_response = response.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_response)
        except:
            logger.error(f"Failed to parse evaluation response: {response}")
            return {"core_concepts": False, "key_questions": False, "information_requirements": False}

class PlannerAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert research planner that creates targeted search strategies.
        Create specific, focused search queries that will yield relevant information for each research objective.
        Your queries must be simple text strings without any special formatting or structure."""

    def create_search_strategy(self, research_item: str, item_type: str) -> List[str]:
        """Create targeted search queries based on the type of research item"""
        prompt = f"""Create 2-3 focused search queries for this {item_type}: {research_item}
        
        Guidelines based on type:
        - For core_concepts: Focus on definitions, explanations, and foundational understanding
        - For key_questions: Focus on finding specific answers and examples
        - For information_requirements: Focus on detailed technical information and data
        
        Return ONLY a JSON array of simple search query strings. Examples:
        ["what is transformer architecture", "transformer architecture explained", "attention mechanism in transformers"]
        
        Make queries specific and relevant, but keep them as simple text strings."""
        
        response = self.generate(prompt, self.system_prompt)
        try:
            cleaned_response = response.strip().replace('```json', '').replace('```', '').strip()
            queries = json.loads(cleaned_response)
            # Ensure we return strings only and limit to 3 queries
            return [str(q) for q in queries[:3]]
        except:
            logger.error(f"Failed to parse search queries: {response}")
            return [str(research_item)]

    def prioritize_unfulfilled_requirements(self, plan: Dict[str, List[str]], progress: Dict[str, bool]) -> List[tuple]:
        """Create a prioritized list of remaining research needs"""
        items = []
        
        # First priority: unfulfilled core concepts
        if not progress["core_concepts"]:
            items.extend([("core_concepts", item) for item in plan["core_concepts"]])
            
        # Second priority: key questions
        if not progress["key_questions"]:
            items.extend([("key_questions", item) for item in plan["key_questions"]])
            
        # Third priority: detailed information requirements
        if not progress["information_requirements"]:
            items.extend([("information_requirements", item) for item in plan["information_requirements"]])
        
        return items

class ReportAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert technical writer that creates comprehensive, 
        well-structured research reports. Synthesize the provided information based on the research plan 
        and create a coherent narrative that thoroughly answers the original query."""

    def generate_report(self, query: str, research_plan: Dict[str, List[str]], research_results: List[str]) -> str:
        prompt = f"""Query: {query}

        Research Plan:
        {json.dumps(research_plan, indent=2)}

        Research Findings:
        {chr(10).join(research_results)}

        Generate a comprehensive technical report that:
        1. Follows the structure of the research plan
        2. Addresses each core concept thoroughly
        3. Answers all key questions identified
        4. Provides detailed analysis based on the information requirements
        5. Uses clear section headings following the research priorities
        6. Synthesizes information into a coherent narrative
        7. Supports claims with specific evidence from the research
        8. Identifies any remaining gaps or uncertainties

        Format the report with clear section headings and ensure it flows logically."""
        
        return self.generate(prompt, self.system_prompt)