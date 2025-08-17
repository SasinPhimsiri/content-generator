"""Rewriter Agent for final content polishing and quality optimization."""

from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..core.config import config


class RewriterAgent(BaseAgent):
    """Agent responsible for final content rewriting and polishing to achieve 10/10 quality."""
    
    def __init__(self):
        super().__init__(agent_name="rewriter")
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input for rewriting (BaseAgent interface compliance)."""
        # Extract required data from input
        content = input_data.get("content", "")
        metadata = input_data.get("metadata", {})
        review_feedback = input_data.get("review_feedback", [])
        style_examples = input_data.get("style_examples", [])
        
        # Use the main rewrite_content method
        return await self.rewrite_content(content, metadata, review_feedback, style_examples)
    
    async def rewrite_content(
        self,
        content: str,
        metadata: Dict[str, Any],
        review_feedback: List[str],
        style_examples: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rewrite content to achieve maximum quality (10/10).
        
        Args:
            content: The content to rewrite
            metadata: Content metadata (topic, category, etc.)
            review_feedback: Feedback from the reviewer agent
            style_examples: Relevant Jenosize style examples
            
        Returns:
            Dict containing rewritten content and improvement details
        """
        
        self.log_activity("Starting content rewriting for maximum quality", {
            "original_length": len(content),
            "feedback_points": len(review_feedback),
            "style_examples": len(style_examples) if style_examples else 0
        })
        
        # Build the rewriting prompt
        prompt = self._build_rewriting_prompt(
            content, metadata, review_feedback, style_examples
        )
        
        try:
            # Generate rewritten content
            response = await self.generate_response(prompt)
            
            # Parse the response
            rewritten_content = self._parse_rewriting_response(response)
            
            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvements(content, rewritten_content)
            
            result = {
                "rewritten_content": rewritten_content,
                "original_content": content,
                "improvement_metrics": improvement_metrics,
                "rewriting_applied": True,
                "target_quality_score": 10.0
            }
            
            self.log_activity("Completed content rewriting", {
                "new_length": len(rewritten_content),
                "improvements_made": improvement_metrics.get("improvements_count", 0)
            })
            
            return result
            
        except Exception as e:
            self.log_activity(f"Error during rewriting: {str(e)}", {"error": True})
            return {
                "rewritten_content": content,  # Return original if rewriting fails
                "original_content": content,
                "improvement_metrics": {"error": str(e)},
                "rewriting_applied": False,
                "target_quality_score": 8.0
            }
    
    def _build_rewriting_prompt(
        self,
        content: str,
        metadata: Dict[str, Any],
        review_feedback: List[str],
        style_examples: List[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for content rewriting."""
        
        # Build style examples section
        style_section = ""
        if style_examples:
            style_section = "\n\n## JENOSIZE STYLE EXAMPLES:\n"
            for i, example in enumerate(style_examples[:2], 1):
                style_section += f"\n### Example {i}:\n{example['content'][:500]}...\n"
        
        # Build feedback section
        feedback_section = ""
        if review_feedback:
            feedback_section = "\n\n## REVIEWER FEEDBACK TO ADDRESS:\n"
            for i, feedback in enumerate(review_feedback, 1):
                feedback_section += f"{i}. {feedback}\n"
        
        prompt = f"""You are Jenosize's expert content rewriter. Your mission is to transform the provided content into a PERFECT 10/10 quality business article that exemplifies Jenosize's professional excellence.

## CONTENT TO REWRITE:
Topic: {metadata.get('topic', 'N/A')}
Category: {metadata.get('category', 'N/A')}
Industry: {metadata.get('industry', 'N/A')}
Target Audience: {metadata.get('target_audience', 'business executives')}
SEO Keywords: {', '.join(metadata.get('seo_keywords', []))}

### ORIGINAL CONTENT:
{content}

{style_section}

{feedback_section}

## YOUR REWRITING MISSION:

Transform this content to achieve PERFECT 10/10 quality by applying these enhancements:

### 1. JENOSIZE EXCELLENCE STANDARDS:
- **Professional Authority**: Establish Jenosize as the definitive expert
- **FUTURE Framework**: Seamlessly integrate F-U-T-U-R-E principles
- **Executive Impact**: Every sentence must provide strategic value
- **Actionable Insights**: Convert theory into practical implementation steps

### 2. CONTENT STRUCTURE PERFECTION:
- **Compelling Hook**: Start with a powerful, attention-grabbing opening
- **Clear Value Proposition**: Immediately establish what executives will gain
- **Logical Flow**: Each paragraph builds naturally to the next
- **Strong Conclusion**: End with clear next steps and call-to-action

### 3. LANGUAGE EXCELLENCE:
- **Precision**: Every word chosen for maximum impact
- **Clarity**: Complex concepts explained simply and elegantly
- **Engagement**: Professional yet compelling tone throughout
- **Authority**: Confident, knowledgeable voice without arrogance

### 4. BUSINESS IMPACT OPTIMIZATION:
- **Strategic Relevance**: Connect every point to business outcomes
- **Market Context**: Reference current trends and challenges
- **Competitive Advantage**: Show how insights provide edge
- **ROI Focus**: Emphasize measurable business benefits

### 5. SEO AND READABILITY:
- **Natural Keyword Integration**: Seamlessly weave in SEO keywords
- **Scannable Format**: Use subheadings, bullet points, and short paragraphs
- **Engaging Subheadings**: Each section header should compel reading
- **Optimal Length**: Comprehensive yet concise

### 6. JENOSIZE BRAND VOICE:
- **Forward-Thinking**: Emphasize innovation and future opportunities
- **Human-Centered**: Technology serves people, not the reverse
- **Solution-Oriented**: Focus on practical problem-solving
- **Collaborative**: Position Jenosize as a strategic partner

## OUTPUT REQUIREMENTS:

Provide ONLY the rewritten content. Make it:
- Significantly improved in quality, clarity, and impact
- Perfectly aligned with Jenosize's professional standards
- Compelling enough to earn a 10/10 quality score
- Ready for immediate publication

Begin the rewritten content now:"""

        return prompt
    
    def _parse_rewriting_response(self, response: str) -> str:
        """Parse and clean the rewriting response."""
        # Clean up the response
        content = response.strip()
        
        # Remove any meta-commentary or instructions that might have leaked through
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that look like instructions or meta-commentary
            if (line.startswith(('Here is', 'Here\'s', 'I have', 'I\'ve', 'The rewritten', 'This rewritten')) 
                or 'rewritten' in line.lower()[:50]
                or line.startswith(('Note:', 'Please', 'Remember'))):
                continue
            if line:
                cleaned_lines.append(line)
        
        return '\n\n'.join(cleaned_lines) if cleaned_lines else content
    
    def _calculate_improvements(self, original: str, rewritten: str) -> Dict[str, Any]:
        """Calculate improvement metrics between original and rewritten content."""
        
        original_words = len(original.split())
        rewritten_words = len(rewritten.split())
        
        # Count sentences
        original_sentences = len([s for s in original.split('.') if s.strip()])
        rewritten_sentences = len([s for s in rewritten.split('.') if s.strip()])
        
        # Calculate readability improvements
        avg_sentence_length_original = original_words / max(original_sentences, 1)
        avg_sentence_length_rewritten = rewritten_words / max(rewritten_sentences, 1)
        
        # Count business terms
        business_terms = [
            'strategy', 'innovation', 'transformation', 'efficiency', 'optimization',
            'competitive advantage', 'roi', 'digital', 'technology', 'future',
            'opportunity', 'growth', 'value', 'solution', 'insight'
        ]
        
        original_business_terms = sum(1 for term in business_terms if term in original.lower())
        rewritten_business_terms = sum(1 for term in business_terms if term in rewritten.lower())
        
        return {
            "word_count_change": rewritten_words - original_words,
            "sentence_count_change": rewritten_sentences - original_sentences,
            "avg_sentence_length_original": round(avg_sentence_length_original, 1),
            "avg_sentence_length_rewritten": round(avg_sentence_length_rewritten, 1),
            "business_terms_original": original_business_terms,
            "business_terms_rewritten": rewritten_business_terms,
            "business_terms_improvement": rewritten_business_terms - original_business_terms,
            "improvements_count": max(0, (rewritten_business_terms - original_business_terms) + 
                                    max(0, original_sentences - rewritten_sentences) // 2),
            "quality_enhancement": "Significant" if rewritten_words > original_words * 1.1 else "Moderate"
        }


# Global rewriter agent instance
rewriter_agent = RewriterAgent()
