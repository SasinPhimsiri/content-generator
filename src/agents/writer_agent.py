"""Writer agent for creating high-quality business content."""

from typing import Dict, Any, List

from .base_agent import BaseAgent


class WriterAgent(BaseAgent):
    """Agent responsible for writing business articles and content."""
    
    def __init__(self):
        super().__init__("writer")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Write content based on research insights and requirements."""
        self.log_activity("Starting writing process", input_data)
        
        # Extract inputs
        research_data = input_data.get("research_data", {})
        content_requirements = input_data.get("content_requirements", {})
        
        research_insights = research_data.get("research_insights", "")
        relevant_examples = research_data.get("relevant_examples", [])
        
        topic = content_requirements.get("topic", "")
        category = content_requirements.get("category", "")
        industry = content_requirements.get("industry", "")
        target_audience = content_requirements.get("target_audience", "business executives")
        seo_keywords = content_requirements.get("seo_keywords", [])
        content_length = content_requirements.get("content_length", "medium")
        
        if not research_insights:
            raise ValueError("Research insights are required for writing")
        
        # Build writing prompt
        writing_prompt = self._build_writing_prompt(
            research_insights=research_insights,
            relevant_examples=relevant_examples,
            topic=topic,
            category=category,
            industry=industry,
            target_audience=target_audience,
            seo_keywords=seo_keywords,
            content_length=content_length
        )
        
        # Generate content
        article_content = await self.generate_response(writing_prompt)
        
        result = {
            "article_content": article_content,
            "content_metadata": {
                "topic": topic,
                "category": category,
                "industry": industry,
                "target_audience": target_audience,
                "seo_keywords": seo_keywords,
                "estimated_word_count": len(article_content.split()),
                "content_length": content_length
            }
        }
        
        self.log_activity("Completed writing", {
            "topic": topic,
            "word_count": len(article_content.split())
        })
        return result
    
    def _build_writing_prompt(
        self,
        research_insights: str,
        relevant_examples: List[Dict[str, Any]],
        topic: str,
        category: str,
        industry: str,
        target_audience: str,
        seo_keywords: List[str],
        content_length: str
    ) -> str:
        """Build the writing prompt with all necessary context."""
        
        # Define content length guidelines
        length_guidelines = {
            "short": "400-600 words",
            "medium": "800-1200 words",
            "long": "1500-2000 words"
        }
        
        word_target = length_guidelines.get(content_length, "800-1200 words")
        
        prompt_parts = [
            "WRITING TASK:",
            f"Topic: {topic}",
            f"Category: {category}",
            f"Industry: {industry}",
            f"Target Audience: {target_audience}",
            f"Target Length: {word_target}",
            f"SEO Keywords: {', '.join(seo_keywords)}" if seo_keywords else "",
            "",
            "RESEARCH INSIGHTS:",
            research_insights,
            "",
        ]
        
        # Add style examples
        if relevant_examples:
            prompt_parts.append("STYLE REFERENCE EXAMPLES:")
            for i, example in enumerate(relevant_examples, 1):
                prompt_parts.append(f"\nExample {i} Style:")
                prompt_parts.append(example["content"][:400] + "...")
            prompt_parts.append("")
        
        # Add writing instructions
        prompt_parts.extend([
            "WRITING INSTRUCTIONS:",
            "Write a comprehensive business article that:",
            "1. Follows Jenosize's professional yet approachable tone",
            "2. Provides actionable insights for business leaders",
            "3. Maintains focus on digital transformation themes",
            "4. Uses clear, engaging language suitable for executives",
            "5. Includes practical examples and applications",
            "6. Naturally incorporates the provided SEO keywords",
            "7. Structures content with clear sections and flow",
            "",
            "ARTICLE STRUCTURE:",
            "- Compelling introduction that hooks the reader",
            "- Well-organized body with clear sections",
            "- Practical insights and actionable recommendations",
            "- Strong conclusion that reinforces key messages",
            "",
            "Write the complete article now:"
        ])
        
        return "\n".join(filter(None, prompt_parts))


# Global writer agent instance
writer_agent = WriterAgent()
