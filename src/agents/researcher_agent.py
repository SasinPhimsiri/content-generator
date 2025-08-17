"""Research agent for gathering insights and information."""

from typing import Dict, Any, List
import asyncio

from .base_agent import BaseAgent
from ..rag.simple_vector_store import simple_rag_system as rag_system


class ResearcherAgent(BaseAgent):
    """Agent responsible for researching topics and gathering insights."""
    
    def __init__(self):
        super().__init__("researcher")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research the given topic and gather relevant insights."""
        self.log_activity("Starting research process", input_data)
        
        topic = input_data.get("topic", "")
        category = input_data.get("category", "")
        industry = input_data.get("industry", "")
        keywords = input_data.get("keywords", [])
        
        if not topic:
            raise ValueError("Topic is required for research")
        
        # Get relevant examples from RAG system
        relevant_examples = rag_system.get_relevant_examples(
            topic=topic,
            category=category,
            industry=industry,
            n_results=2
        )
        
        # Prepare research prompt
        research_prompt = self._build_research_prompt(
            topic=topic,
            category=category,
            industry=industry,
            keywords=keywords,
            examples=relevant_examples
        )
        
        # Generate research insights
        research_content = await self.generate_response(research_prompt)
        
        result = {
            "research_insights": research_content,
            "relevant_examples": relevant_examples,
            "research_metadata": {
                "topic": topic,
                "category": category,
                "industry": industry,
                "keywords": keywords
            }
        }
        
        self.log_activity("Completed research", {"topic": topic, "insights_length": len(research_content)})
        return result
    
    def _build_research_prompt(
        self,
        topic: str,
        category: str,
        industry: str,
        keywords: List[str],
        examples: List[Dict[str, Any]]
    ) -> str:
        """Build the research prompt with context and examples."""
        
        prompt_parts = [
            f"Research Topic: {topic}",
            f"Category: {category}" if category else "",
            f"Industry: {industry}" if industry else "",
            f"Keywords: {', '.join(keywords)}" if keywords else "",
        ]
        
        # Add relevant examples for context
        if examples:
            prompt_parts.append("\nRelevant Content Examples:")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"\nExample {i}:")
                prompt_parts.append(example["content"][:300] + "...")
        
        prompt_parts.extend([
            "\nBased on the above context, provide comprehensive research insights that include:",
            "1. Current market trends and developments",
            "2. Key challenges and opportunities",
            "3. Industry-specific considerations",
            "4. Future outlook and predictions",
            "5. Practical implications for businesses",
            "",
            "Focus on factual, data-driven insights that align with professional business consulting standards.",
            "Ensure the research is relevant to digital transformation and business innovation themes."
        ])
        
        return "\n".join(filter(None, prompt_parts))


# Global researcher agent instance
researcher_agent = ResearcherAgent()
