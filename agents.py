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
            if not api_key:
                raise ValueError("Gemini API key is required when use_gemini=True")
            genai.configure(api_key=api_key)
            self.gemini_model = gemini_model or "gemini-1.5-pro"  # Use a good default model
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
            combined_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
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
        prompt = f"""Analyze the research plan and gathered information to evaluate completeness.

        Research Plan:
        {json.dumps(plan, indent=2)}

        Gathered Information:
        {chr(10).join(gathered_info)}

        Your task: Return a STRICTLY FORMATTED JSON object with only three boolean fields indicating whether the gathered information adequately covers each aspect. Do not include any other text, explanation, or comments.

        Required exact output format (with true/false values):
        {{
            "core_concepts": false,
            "key_questions": false,
            "information_requirements": false
        }}

        Rules:
        - Set a field to true ONLY if the gathered information thoroughly covers that aspect
        - Return ONLY the JSON object, no other text
        - Must be valid JSON parseable by json.loads()"""

        response = self.generate(prompt, self.system_prompt)
        try:
            # Remove any leading/trailing whitespace and quotes
            cleaned_response = response.strip().strip('"').strip()
            # Remove any markdown code block formatting
            cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
            
            # Parse and validate the response has the correct structure
            parsed = json.loads(cleaned_response)
            required_keys = {"core_concepts", "key_questions", "information_requirements"}
            if not all(isinstance(parsed.get(key), bool) for key in required_keys):
                raise ValueError("Response missing required boolean fields")
            
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse evaluation response: {response}")
            # Return a default response indicating no completeness
            return {
                "core_concepts": False,
                "key_questions": False,
                "information_requirements": False
            }

class PlannerAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert research planner that creates targeted search strategies.
        Your role is to identify the key aspects that need deep investigation, focusing on quality over quantity.
        Create research plans that encourage thorough exploration of important concepts rather than shallow coverage of many topics."""

    def create_search_strategy(self, research_item: str, item_type: str) -> List[str]:
        """Create targeted search queries based on the type of research item"""
        prompt = f"""Create 2-3 highly specific search queries for this {item_type}: {research_item}
        
        Focus on Depth:
        - Start with foundational understanding
        - Build up to technical specifics and implementation details
        - Look for real-world examples and case studies
        - Find comparative analyses and benchmarks
        - Seek out critical discussions and limitations
        
        Guidelines:
        - Prefer fewer, more focused queries over many broad ones
        - Each query should build on previous knowledge
        - Target high-quality technical sources
        - Look for detailed explanations rather than surface-level overviews
        
        Return ONLY a JSON array of 2-3 carefully crafted search queries that will yield deep technical information.
        Make each query highly specific and targeted."""
        
        response = self.generate(prompt, self.system_prompt)
        try:
            cleaned_response = response.strip().replace('```json', '').replace('```', '').strip()
            queries = json.loads(cleaned_response)
            return [str(q) for q in queries[:3]]
        except:
            logger.error(f"Failed to parse search queries: {response}")
            return [str(research_item)]

    def prioritize_unfulfilled_requirements(self, plan: Dict[str, List[str]], progress: Dict[str, bool], gathered_info: List[str] = None) -> List[tuple]:
        """Create a prioritized list of remaining research needs with depth checking"""
        items = []
        
        def has_sufficient_depth(topic: str, info: List[str]) -> bool:
            if not info:
                return False
            
            # Count substantial mentions (more than just a passing reference)
            substantial_mentions = 0
            for text in info:
                topic_words = set(topic.lower().split())
                text_lower = text.lower()
                
                # Check if the text contains multiple topic keywords
                keyword_matches = sum(1 for word in topic_words if word in text_lower)
                
                # Check for substantial content (contains multiple keywords and is detailed)
                if keyword_matches >= 2 and len(text) > 300:
                    substantial_mentions += 1
                
            # Require multiple substantial mentions
            return substantial_mentions >= 2
        
        # First priority: core concepts without sufficient depth
        if not progress["core_concepts"]:
            for item in plan["core_concepts"]:
                if not gathered_info or not has_sufficient_depth(item, gathered_info):
                    items.append(("core_concepts", item))
            
        # Second priority: key questions without sufficient answers
        if not progress["key_questions"]:
            for item in plan["key_questions"]:
                if not gathered_info or not has_sufficient_depth(item, gathered_info):
                    items.append(("key_questions", item))
            
        # Third priority: detailed information requirements
        if not progress["information_requirements"]:
            for item in plan["information_requirements"]:
                if not gathered_info or not has_sufficient_depth(item, gathered_info):
                    items.append(("information_requirements", item))
        
        return items

class ReportAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert technical writer and researcher that creates 
        comprehensive, well-structured research reports. Your primary focus is on deep analysis,
        synthesis of information, and meaningful organization of content.
        
        Key Principles:
        1. Quality over Quantity - Focus on depth and insight rather than filling sections
        2. Natural Organization - Let the content guide the structure instead of forcing a rigid outline
        3. Meaningful Connections - Draw relationships between different pieces of information
        4. Critical Analysis - Question assumptions and evaluate trade-offs
        5. Evidence-Based - Support claims with specific technical details and examples"""

    def generate_report(self, query: str, research_plan: Dict[str, List[str]], 
                       research_results: List[str], completion_stats: Dict[str, Any]) -> str:
        prompt = f"""Generate a comprehensive technical report that synthesizes the research findings into a cohesive narrative.

        Query: {query}

        Research Plan:
        {json.dumps(research_plan, indent=2)}

        Research Coverage:
        {json.dumps(completion_stats, indent=2)}

        Research Findings:
        {chr(10).join(research_results)}

        Report Requirements:

        1. Organization:
           - Start with a clear introduction that frames the topic
           - Group related concepts together naturally
           - Only create sections when there's enough substantial content
           - Use appropriate heading levels (# for h1, ## for h2, etc.)
           - Maintain a logical flow of ideas

        2. Content Development:
           - Focus on in-depth analysis of important concepts
           - Provide concrete examples and technical details
           - Compare and contrast different approaches
           - Discuss real-world implications
           - Acknowledge limitations and trade-offs

        3. Synthesis & Analysis:
           - Draw meaningful connections between different sources
           - Evaluate conflicting information
           - Identify patterns and trends
           - Provide reasoned analysis supported by evidence
           - Offer insights beyond just summarizing sources

        4. Technical Accuracy:
           - Use precise technical language
           - Include relevant code examples with language tags
           - Provide performance metrics when available
           - Explain technical concepts clearly
           - Support technical claims with evidence

        5. Formatting:
           - Use proper markdown formatting
           - Include code blocks with language tags when relevant
           - Format lists and tables appropriately
           - Add line breaks between sections
           - Ensure consistent formatting throughout

        Important:
        - Do NOT create sections just to fill a structure
        - Combine related information even if it came from different parts of the research plan
        - Focus on providing meaningful insights rather than covering every possible aspect
        - Only include information that contributes to understanding the topic
        - Skip sections or topics where there isn't enough substantive content"""
        
        return self.generate(prompt, self.system_prompt)
