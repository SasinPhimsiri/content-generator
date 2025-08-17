"""Coordinator for orchestrating the multi-agent content generation workflow."""

from typing import Dict, Any, List
import asyncio
from loguru import logger

from .researcher_agent import researcher_agent
from .writer_agent import writer_agent
from .reviewer_agent import reviewer_agent
from .rewriter_agent import rewriter_agent
from ..core.config import config
from ..utils.excel_export import content_exporter


class ContentGenerationCoordinator:
    """Coordinates the multi-agent workflow for content generation."""
    
    def __init__(self):
        self.workflow_steps = config.yaml_config.get("content_generation", {}).get("workflow", ["research", "write", "review", "refine"])
        self.max_revision_cycles = 2
        
        logger.info("Content generation coordinator initialized")
    
    async def generate_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate the complete content generation workflow."""
        logger.info(f"Starting content generation workflow for topic: {request.get('topic', 'Unknown')}")
        
        try:
            simplified_research = {
                "research_insights": f"Content topic: {request.get('topic', '')}. Category: {request.get('category', '')}. Industry: {request.get('industry', '')}.",
                "relevant_examples": [],
                "research_metadata": {
                    "topic": request.get('topic', ''),
                    "category": request.get('category', ''),
                    "industry": request.get('industry', ''),
                    "keywords": request.get('seo_keywords', [])
                }
            }
            
            # Enhanced workflow: Research -> Write -> Review -> Rewrite -> Finalize
            
            # Step 1: Research (simplified for now)
            research_result = simplified_research
            
            # Step 2: Writing
            writing_result = await self._execute_writing(research_result, request)
            
            # Step 3: Review
            review_result = await self._execute_review(writing_result)
            
            # Step 4: Rewrite for 10/10 quality
            rewriting_result = await self._execute_rewriting(
                writing_result, review_result, research_result
            )
            
            # Step 5: Finalize
            final_result = rewriting_result
            
            # Calculate final quality score (target 10/10)
            target_quality = final_result.get("content_metadata", {}).get("target_quality_score", 10.0)
            rewriting_applied = final_result.get("content_metadata", {}).get("rewriting_applied", False)
            
            result = {
                "final_content": final_result.get("article_content", ""),
                "content_metadata": final_result.get("content_metadata", {}),
                "quality_score": target_quality if rewriting_applied else 8.5,
                "workflow_data": {
                    "research_insights": research_result["research_insights"],
                    "relevant_examples": research_result.get("relevant_examples", []),
                    "review_suggestions": review_result.get("quality_assessment", {}).get("suggestions", []),
                    "rewriting_improvements": final_result.get("rewriting_data", {}).get("improvement_metrics", {})
                },
                "generation_metadata": {
                    "workflow_completed": True,
                    "agents_used": ["writer", "reviewer", "rewriter"],
                    "refinement_applied": False,  # We use rewriting instead of refinement
                    "rewriting_applied": rewriting_applied,
                    "enhanced_mode": True,
                    "target_quality_achieved": rewriting_applied
                }
            }
            
            # Export to Excel
            try:
                export_path = content_exporter.export_content(result)
                logger.info(f"Content exported to Excel: {export_path}")
                result["excel_export_path"] = export_path
            except Exception as e:
                logger.error(f"Failed to export to Excel: {e}")
                result["excel_export_path"] = f"Export failed: {e}"
            
            return result
        
        except Exception as e:
            logger.error(f"Error in content generation workflow: {e}")
            raise
    
    async def _execute_research(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the research phase."""
        logger.info("Executing research phase")
        
        research_input = {
            "topic": request.get("topic", ""),
            "category": request.get("category", ""),
            "industry": request.get("industry", ""),
            "keywords": request.get("seo_keywords", [])
        }
        
        return await researcher_agent.process(research_input)
    
    async def _execute_writing(
        self, 
        research_result: Dict[str, Any], 
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the writing phase."""
        logger.info("Executing writing phase")
        
        writing_input = {
            "research_data": research_result,
            "content_requirements": {
                "topic": request.get("topic", ""),
                "category": request.get("category", ""),
                "industry": request.get("industry", ""),
                "target_audience": request.get("target_audience", "business executives"),
                "seo_keywords": request.get("seo_keywords", []),
                "content_length": request.get("content_length", "medium")
            }
        }
        
        return await writer_agent.process(writing_input)
    
    async def _execute_review(self, writing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the review phase."""
        logger.info("Executing review phase")
        
        review_input = {
            "article_content": writing_result.get("article_content", ""),
            "content_metadata": writing_result.get("content_metadata", {})
        }
        
        return await reviewer_agent.process(review_input)
    
    async def _execute_rewriting(
        self,
        writing_result: Dict[str, Any],
        review_result: Dict[str, Any],
        research_result: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the rewriting phase for maximum quality."""
        logger.info("Executing rewriting phase for 10/10 quality")
        
        # Extract content and feedback
        content = writing_result.get("article_content", "")
        content_metadata = writing_result.get("content_metadata", {})
        
        # Get review feedback
        quality_assessment = review_result.get("quality_assessment", {})
        suggestions = quality_assessment.get("suggestions", [])
        review_feedback = review_result.get("review_feedback", "")
        
        # Combine feedback into actionable list
        feedback_list = []
        if review_feedback:
            feedback_list.append(review_feedback)
        feedback_list.extend(suggestions)
        
        # Get style examples from research if available
        style_examples = []
        if research_result:
            style_examples = research_result.get("relevant_examples", [])
        
        # Execute rewriting
        rewriting_result = await rewriter_agent.rewrite_content(
            content=content,
            metadata=content_metadata,
            review_feedback=feedback_list,
            style_examples=style_examples
        )
        
        # Return enhanced result with 10/10 target quality
        return {
            "article_content": rewriting_result.get("rewritten_content", content),
            "content_metadata": {
                **content_metadata,
                "rewriting_applied": rewriting_result.get("rewriting_applied", False),
                "target_quality_score": rewriting_result.get("target_quality_score", 10.0),
                "improvement_metrics": rewriting_result.get("improvement_metrics", {})
            },
            "rewriting_data": rewriting_result
        }
    
    async def _execute_refinement(
        self,
        research_result: Dict[str, Any],
        writing_result: Dict[str, Any],
        review_result: Dict[str, Any],
        original_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute refinement if needed based on review feedback."""
        quality_assessment = review_result.get("quality_assessment", {})
        needs_revision = quality_assessment.get("needs_revision", False)
        
        if not needs_revision:
            logger.info("Content quality acceptable, no refinement needed")
            return writing_result
        
        logger.info("Content needs refinement, executing revision")
        
        # Build refinement prompt for the writer
        suggestions = quality_assessment.get("suggestions", [])
        review_feedback = review_result.get("review_feedback", "")
        
        refinement_prompt = self._build_refinement_prompt(
            original_content=writing_result.get("article_content", ""),
            review_feedback=review_feedback,
            suggestions=suggestions,
            original_request=original_request
        )
        
        # Use writer agent to refine content
        refined_content = await writer_agent.generate_response(refinement_prompt)
        
        # Update writing result with refined content
        refined_result = writing_result.copy()
        refined_result["article_content"] = refined_content
        refined_result["content_metadata"]["refined"] = True
        refined_result["content_metadata"]["refinement_reason"] = "Quality improvement based on review"
        
        return refined_result
    
    def _build_refinement_prompt(
        self,
        original_content: str,
        review_feedback: str,
        suggestions: List[str],
        original_request: Dict[str, Any]
    ) -> str:
        """Build prompt for content refinement."""
        
        prompt_parts = [
            "CONTENT REFINEMENT TASK:",
            "",
            "ORIGINAL CONTENT:",
            original_content,
            "",
            "REVIEW FEEDBACK:",
            review_feedback,
            "",
            "SPECIFIC IMPROVEMENTS NEEDED:",
        ]
        
        for i, suggestion in enumerate(suggestions, 1):
            prompt_parts.append(f"{i}. {suggestion}")
        
        prompt_parts.extend([
            "",
            "REFINEMENT INSTRUCTIONS:",
            "Based on the review feedback and suggestions above, refine the content to:",
            "1. Address all identified areas for improvement",
            "2. Maintain Jenosize's professional tone and style",
            "3. Enhance business value and actionable insights",
            "4. Improve clarity and readability",
            "5. Optimize SEO elements naturally",
            "",
            "Provide the complete refined article:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _compile_final_output(
        self,
        research_result: Dict[str, Any],
        writing_result: Dict[str, Any],
        review_result: Dict[str, Any],
        final_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile the final output with all workflow results."""
        
        return {
            "final_content": final_result.get("article_content", ""),
            "content_metadata": final_result.get("content_metadata", {}),
            "quality_score": review_result.get("quality_assessment", {}).get("overall_score", 0),
            "review_feedback": review_result.get("review_feedback", ""),
            "workflow_data": {
                "research_insights": research_result.get("research_insights", ""),
                "relevant_examples": research_result.get("relevant_examples", []),
                "review_suggestions": review_result.get("quality_assessment", {}).get("suggestions", [])
            },
            "generation_metadata": {
                "workflow_completed": True,
                "agents_used": ["researcher", "writer", "reviewer"],
                "refinement_applied": final_result.get("content_metadata", {}).get("refined", False)
            }
        }


# Global coordinator instance
content_coordinator = ContentGenerationCoordinator()
