"""Reviewer agent for quality assurance and content optimization."""

from typing import Dict, Any, List

from .base_agent import BaseAgent


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and optimizing content quality."""
    
    def __init__(self):
        super().__init__("reviewer")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review content and provide quality assessment and suggestions."""
        self.log_activity("Starting review process", input_data)
        
        article_content = input_data.get("article_content", "")
        content_metadata = input_data.get("content_metadata", {})
        
        if not article_content:
            raise ValueError("Article content is required for review")
        
        # Build review prompt
        review_prompt = self._build_review_prompt(
            article_content=article_content,
            content_metadata=content_metadata
        )
        
        # Generate review and feedback
        review_feedback = await self.generate_response(review_prompt)
        
        # Extract quality score and suggestions from feedback
        quality_assessment = self._parse_review_feedback(review_feedback)
        
        result = {
            "review_feedback": review_feedback,
            "quality_assessment": quality_assessment,
            "content_metadata": content_metadata,
            "review_metadata": {
                "reviewer": "Content Reviewer Agent",
                "review_criteria": [
                    "Jenosize tone alignment",
                    "Business value",
                    "Clarity and readability",
                    "SEO optimization",
                    "Professional quality"
                ]
            }
        }
        
        self.log_activity("Completed review", {
            "quality_score": quality_assessment.get("overall_score", "N/A"),
            "suggestions_count": len(quality_assessment.get("suggestions", []))
        })
        return result
    
    def _build_review_prompt(
        self,
        article_content: str,
        content_metadata: Dict[str, Any]
    ) -> str:
        """Build the review prompt for content evaluation."""
        
        topic = content_metadata.get("topic", "")
        category = content_metadata.get("category", "")
        industry = content_metadata.get("industry", "")
        target_audience = content_metadata.get("target_audience", "")
        seo_keywords = content_metadata.get("seo_keywords", [])
        
        prompt_parts = [
            "CONTENT REVIEW TASK:",
            f"Topic: {topic}",
            f"Category: {category}",
            f"Industry: {industry}",
            f"Target Audience: {target_audience}",
            f"SEO Keywords: {', '.join(seo_keywords)}" if seo_keywords else "",
            "",
            "ARTICLE TO REVIEW:",
            article_content,
            "",
            "REVIEW CRITERIA:",
            "Evaluate the article based on the following criteria:",
            "",
            "1. JENOSIZE TONE ALIGNMENT (Score: 1-10)",
            "   - Professional yet approachable tone",
            "   - Business consulting expertise evident",
            "   - Forward-thinking and insightful perspective",
            "",
            "2. BUSINESS VALUE (Score: 1-10)",
            "   - Actionable insights for business leaders",
            "   - Practical applications and examples",
            "   - Relevance to digital transformation",
            "",
            "3. CLARITY AND READABILITY (Score: 1-10)",
            "   - Clear structure and flow",
            "   - Appropriate language for target audience",
            "   - Logical progression of ideas",
            "",
            "4. SEO OPTIMIZATION (Score: 1-10)",
            "   - Natural integration of keywords",
            "   - Appropriate content length",
            "   - Engaging title and structure",
            "",
            "5. PROFESSIONAL QUALITY (Score: 1-10)",
            "   - Grammar and style consistency",
            "   - Factual accuracy and credibility",
            "   - Overall polish and presentation",
            "",
            "REVIEW FORMAT:",
            "Provide your review in the following format:",
            "",
            "OVERALL SCORE: [X/10]",
            "",
            "DETAILED SCORES:",
            "- Jenosize Tone Alignment: [X/10]",
            "- Business Value: [X/10]",
            "- Clarity and Readability: [X/10]",
            "- SEO Optimization: [X/10]",
            "- Professional Quality: [X/10]",
            "",
            "STRENGTHS:",
            "[List key strengths of the article]",
            "",
            "AREAS FOR IMPROVEMENT:",
            "[List specific suggestions for improvement]",
            "",
            "RECOMMENDED CHANGES:",
            "[Provide specific, actionable recommendations]"
        ]
        
        return "\n".join(filter(None, prompt_parts))
    
    def _parse_review_feedback(self, feedback: str) -> Dict[str, Any]:
        """Parse the review feedback to extract structured data."""
        try:
            lines = feedback.split("\n")
            
            # Extract overall score
            overall_score = None
            for line in lines:
                if "OVERALL SCORE:" in line.upper():
                    score_part = line.split(":")[-1].strip()
                    if "/" in score_part:
                        overall_score = float(score_part.split("/")[0])
                    break
            
            # Extract suggestions (areas for improvement and recommendations)
            suggestions = []
            in_improvement_section = False
            in_recommendations_section = False
            
            for line in lines:
                line = line.strip()
                if "AREAS FOR IMPROVEMENT:" in line.upper():
                    in_improvement_section = True
                    in_recommendations_section = False
                elif "RECOMMENDED CHANGES:" in line.upper():
                    in_improvement_section = False
                    in_recommendations_section = True
                elif line.startswith("-") or line.startswith("•"):
                    if in_improvement_section or in_recommendations_section:
                        suggestions.append(line[1:].strip())
            
            return {
                "overall_score": overall_score or 7.0,  # Default score if parsing fails
                "suggestions": suggestions,
                "needs_revision": (overall_score or 7.0) < 7.0
            }
        
        except Exception as e:
            self.log_activity("Error parsing review feedback", {"error": str(e)})
            return {
                "overall_score": 7.0,
                "suggestions": ["Review parsing failed - manual review recommended"],
                "needs_revision": False
            }


# Global reviewer agent instance
reviewer_agent = ReviewerAgent()
