"""Gradio frontend for Jenosize Content Generator."""

import asyncio
import json
from typing import Dict, Any, Optional, Tuple
import httpx
import gradio as gr
from loguru import logger

from ..core.config import config


class ContentGeneratorUI:
    """Gradio UI for the content generator."""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.timeout = 300.0  # 5 minutes for content generation
        
        # Load configuration from API
        self.categories = []
        self.industries = []
        self._load_config()
    
    def _load_config(self):
        """Load configuration from API."""
        try:
            import requests
            response = requests.get(f"{self.api_base_url}/config", timeout=10)
            if response.status_code == 200:
                config_data = response.json()
                self.categories = config_data.get("content_categories", [])
                self.industries = config_data.get("industries", [])
            else:
                logger.warning("Could not load config from API, using defaults")
                self._set_default_config()
        except Exception as e:
            logger.warning(f"Error loading config from API: {e}")
            self._set_default_config()
    
    def _set_default_config(self):
        """Set default configuration."""
        self.categories = [
            "Digital Transformation", "Technology Trends", "Business Innovation",
            "Future of Work", "Data & Analytics", "AI & Automation",
            "Customer Experience", "Cybersecurity"
        ]
        self.industries = [
            "Financial Services", "Healthcare", "Retail & E-commerce",
            "Manufacturing", "Education", "Government",
            "Telecommunications", "Energy & Utilities", "General"
        ]
    
    async def _process_pdf_files(self, pdf_files) -> str:
        """Process uploaded PDF files and extract text content (temporarily disabled)."""
        # PDF functionality temporarily disabled due to Gradio compatibility issues
        return ""
    
    async def generate_content(
        self,
        topic: str,
        category: str,
        industry: str,
        target_audience: str,
        keywords: str,
        content_length: str,
        source_urls: str,
        pdf_files,
        additional_context: str,
        progress=gr.Progress()
    ) -> Tuple[str, str, str, str]:
        """Generate content using the API."""
        
        if not topic.strip():
            return "Error: Topic is required", "", "", ""
        
        try:
            progress(0.1, desc="Preparing request...")
            
            # Process PDF files if provided
            pdf_content = ""
            if pdf_files:
                progress(0.15, desc="Processing PDF files...")
                pdf_content = await self._process_pdf_files(pdf_files)
                if pdf_content:
                    additional_context = f"{additional_context}\n\n**Reference PDF Content:**\n{pdf_content}".strip()
            
            # Prepare request data
            request_data = {
                "topic": topic.strip(),
                "category": category if category != "Select category..." else None,
                "industry": industry if industry != "Select industry..." else None,
                "target_audience": target_audience.strip() if target_audience.strip() else "business executives",
                "seo_keywords": [k.strip() for k in keywords.split(",") if k.strip()] if keywords else [],
                "content_length": content_length.lower(),
                "source_urls": [u.strip() for u in source_urls.split("\n") if u.strip()] if source_urls else [],
                "additional_context": additional_context.strip() if additional_context.strip() else ""
            }
            
            progress(0.2, desc="Generating...")
            
            # Make API request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_base_url}/generate",
                    json=request_data
                )
                
                if response.status_code == 429:
                    return "Error: Rate limit exceeded. Please wait and try again.", "", "", ""
                
                response.raise_for_status()
                result = response.json()
            
            progress(0.9, desc="Processing results...")
            
            # Extract results
            content = result.get("content", "")
            quality_score = result.get("quality_score", 0)
            metadata = result.get("metadata", {})
            validation = result.get("validation_result", {})
            
            # Format metadata display
            excel_path = result.get("excel_export_path")
            metadata_text = self._format_metadata(metadata, quality_score, validation, excel_path)
            
            # Format workflow information
            workflow_data = result.get("workflow_data", {})
            workflow_text = self._format_workflow_data(workflow_data)
            
            # Format validation results
            validation_text = self._format_validation_results(validation)
            
            progress(1.0, desc="Complete!")
            
            return content, metadata_text, workflow_text, validation_text
        
        except httpx.TimeoutException:
            return "Error: Request timed out. Please try again with a simpler topic.", "", "", ""
        
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("detail", str(e))
            except:
                error_detail = str(e)
            
            return f"Error: {error_detail}", "", "", ""
        
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error: {str(e)}", "", "", ""
    
    def _format_metadata(self, metadata: Dict[str, Any], quality_score: float, validation: Dict[str, Any], excel_path: str = None) -> str:
        """Format metadata for display."""
        lines = [
            "## Content Metadata",
            f"**Quality Score:** {quality_score:.1f}/10",
            f"**Topic:** {metadata.get('topic', 'N/A')}",
            f"**Category:** {metadata.get('category', 'N/A')}",
            f"**Industry:** {metadata.get('industry', 'N/A')}",
            f"**Target Audience:** {metadata.get('target_audience', 'N/A')}",
            f"**Estimated Word Count:** {metadata.get('estimated_word_count', 0)}",
            f"**Content Length:** {metadata.get('content_length', 'N/A')}",
        ]
        
        # Add Excel export information
        if excel_path:
            if "Export failed" not in excel_path:
                lines.append(f"**📊 Excel Export:** Saved to `{excel_path}`")
            else:
                lines.append(f"**⚠️ Excel Export:** {excel_path}")
        else:
            lines.append("**📊 Excel Export:** Not available")
        
        if metadata.get('seo_keywords'):
            keywords = ", ".join(metadata['seo_keywords'])
            lines.append(f"**SEO Keywords:** {keywords}")
        
        if metadata.get('refined'):
            lines.append(f"**Content Refined:** Yes ({metadata.get('refinement_reason', 'Quality improvement')})")
        
        # Add validation summary
        metrics = validation.get('metrics', {})
        if metrics:
            lines.extend([
                "",
                "## Content Metrics",
                f"**Actual Word Count:** {metrics.get('word_count', 0)}",
            ])
            
            if 'avg_words_per_sentence' in metrics:
                lines.append(f"**Avg Words per Sentence:** {metrics['avg_words_per_sentence']}")
        
        return "\n".join(lines)
    
    def _format_workflow_data(self, workflow_data: Dict[str, Any]) -> str:
        """Format workflow data for display."""
        lines = ["## Workflow Information"]
        
        research_insights = workflow_data.get('research_insights', '')
        if research_insights:
            lines.extend([
                "",
                "### Research Insights",
                research_insights[:500] + ("..." if len(research_insights) > 500 else "")
            ])
        
        relevant_examples = workflow_data.get('relevant_examples', [])
        if relevant_examples:
            lines.extend([
                "",
                "### Style References Used",
            ])
            for i, example in enumerate(relevant_examples[:2], 1):
                metadata = example.get('metadata', {})
                lines.append(f"**Example {i}:** {metadata.get('category', 'N/A')} - {metadata.get('type', 'N/A')}")
        
        suggestions = workflow_data.get('review_suggestions', [])
        if suggestions:
            lines.extend([
                "",
                "### Review Suggestions Applied",
            ])
            for suggestion in suggestions[:3]:
                lines.append(f"• {suggestion}")
        
        return "\n".join(lines)
    
    def _format_validation_results(self, validation: Dict[str, Any]) -> str:
        """Format validation results for display."""
        lines = ["## Content Validation"]
        
        is_valid = validation.get('is_valid', True)
        lines.append(f"**Status:** {'✅ Valid' if is_valid else '❌ Issues Found'}")
        
        issues = validation.get('issues', [])
        if issues:
            lines.extend([
                "",
                "### Issues",
            ])
            for issue in issues:
                lines.append(f"❌ {issue}")
        
        warnings = validation.get('warnings', [])
        if warnings:
            lines.extend([
                "",
                "### Warnings",
            ])
            for warning in warnings:
                lines.append(f"⚠️ {warning}")
        
        if not issues and not warnings:
            lines.append("\n✅ No issues or warnings found.")
        
        return "\n".join(lines)
    
    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        
        with gr.Blocks(
            title="Jenosize Content Generator",
            theme=gr.themes.Soft(),
            css="""
            .main-header { text-align: center; margin-bottom: 2rem; }
            .input-section { margin-bottom: 1rem; }
            .output-section { margin-top: 2rem; }
            """
        ) as interface:
            
            # Header
            gr.HTML("""
            <div class="main-header">
                <h1>Jenosize Content Generator</h1>
                <p>AI-powered business content creation with multi-agent workflow</p>
                <p><em>Generating take time around 3-5 minutes to highest quality content.</em></p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.HTML("<h3>Content Requirements</h3>")
                    
                    # Main inputs
                    topic_input = gr.Textbox(
                        label="Topic",
                        placeholder="Enter the main topic for your article...",
                        lines=2,
                        max_lines=3
                    )
                    
                    with gr.Row():
                        category_dropdown = gr.Dropdown(
                            choices=["Select category..."] + self.categories,
                            label="Category",
                            value="Select category..."
                        )
                        
                        industry_dropdown = gr.Dropdown(
                            choices=["Select industry..."] + self.industries,
                            label="Industry",
                            value="Select industry..."
                        )
                    
                    target_audience_input = gr.Textbox(
                        label="Target Audience",
                        placeholder="business executives",
                        value="business executives"
                    )
                    
                    keywords_input = gr.Textbox(
                        label="SEO Keywords (comma-separated)",
                        placeholder="digital transformation, innovation, technology",
                        lines=2
                    )
                    
                    content_length_radio = gr.Radio(
                        choices=["Short", "Medium", "Long"],
                        label="Content Length",
                        value="Medium"
                    )
                    
                    # Advanced options
                    with gr.Accordion("Advanced Options", open=False):
                        source_urls_input = gr.Textbox(
                            label="Source URLs (one per line, max 5)",
                            placeholder="https://example.com/article1\nhttps://example.com/article2",
                            lines=3
                        )
                        
                        pdf_files_input = gr.Textbox(
                            label="PDF File Paths (optional - coming soon)",
                            placeholder="PDF upload feature temporarily disabled due to compatibility issues",
                            interactive=False,
                            visible=False
                        )
                        
                        additional_context_input = gr.Textbox(
                            label="Additional Context",
                            placeholder="Any specific requirements or context...",
                            lines=3
                        )
                    
                    # Generate button
                    generate_btn = gr.Button(
                        "Generate Content",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    gr.HTML("<h3>Generated Content</h3>")
                    
                    # Main output
                    content_output = gr.Textbox(
                        label="Article Content",
                        lines=20,
                        max_lines=30,
                        show_copy_button=True
                    )
                    
                    # Tabs for additional information
                    with gr.Tabs():
                        with gr.Tab("Metadata"):
                            metadata_output = gr.Markdown()
                        
                        with gr.Tab("Workflow"):
                            workflow_output = gr.Markdown()
                        
                        with gr.Tab("Validation"):
                            validation_output = gr.Markdown()
            
            # Example inputs
            gr.HTML("<h3>Try These Examples</h3>")
            
            examples = [
                [
                    "The Future of Remote Work in Financial Services",
                    "Future of Work",
                    "Financial Services",
                    "financial executives",
                    "remote work, digital workplace, financial services",
                    "Medium",
                    "",
                    ""
                ],
                [
                    "AI-Driven Customer Experience Transformation",
                    "AI & Automation",
                    "Retail & E-commerce",
                    "retail managers",
                    "artificial intelligence, customer experience, personalization",
                    "Long",
                    "",
                    ""
                ],
                [
                    "Cybersecurity Challenges in Digital Transformation",
                    "Cybersecurity",
                    "Healthcare",
                    "IT leaders",
                    "cybersecurity, digital transformation, healthcare",
                    "Medium",
                    "",
                    ""
                ]
            ]
            
            gr.Examples(
                examples=examples,
                inputs=[
                    topic_input, category_dropdown, industry_dropdown,
                    target_audience_input, keywords_input, content_length_radio,
                    source_urls_input, additional_context_input
                ],
                label="Click an example to load it"
            )
            
            # Set up event handlers
            generate_btn.click(
                fn=self.generate_content,
                inputs=[
                    topic_input, category_dropdown, industry_dropdown,
                    target_audience_input, keywords_input, content_length_radio,
                    source_urls_input, pdf_files_input, additional_context_input
                ],
                outputs=[content_output, metadata_output, workflow_output, validation_output],
                show_progress=True
            )
            
            # Footer
            gr.HTML("""
            <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #eee;">
                <p><strong>Jenosize Content Generator</strong> - Powered by Multi-Agent AI System</p>
                <p><em>Built with Ollama, RAG, and FastAPI</em></p>
            </div>
            """)
        
        return interface
    
    def launch(self, **kwargs):
        """Launch the Gradio interface with automatic port detection."""
        interface = self.create_interface()
        
        # Try to find an available port
        import socket
        def find_free_port(start_port=7860, max_attempts=10):
            for port in range(start_port, start_port + max_attempts):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    try:
                        s.bind(('localhost', port))
                        return port
                    except OSError:
                        continue
            return None
        
        # Find available port
        available_port = find_free_port(7860)
        if available_port is None:
            logger.error("Could not find available port in range 7860-7870")
            available_port = 7860  # Let Gradio handle the error
        
        default_kwargs = {
            "server_name": "0.0.0.0",
            "server_port": available_port,
            "share": False,
            "show_error": True
        }
        default_kwargs.update(kwargs)
        
        logger.info(f"Launching Gradio interface on port {default_kwargs['server_port']}")
        interface.launch(**default_kwargs)


def main():
    """Main function to run the Gradio app."""
    app = ContentGeneratorUI()
    app.launch()


if __name__ == "__main__":
    main()
