"""Excel export functionality for generated content."""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from loguru import logger


class ContentExporter:
    """Handles exporting generated content to Excel files."""
    
    def __init__(self, export_folder: str = "generated_content"):
        """Initialize the exporter with a target folder."""
        self.export_folder = Path(export_folder)
        self.export_folder.mkdir(exist_ok=True)
        self.excel_file = self.export_folder / "jenosize_content_history.xlsx"
        
    def export_content(self, content_data: Dict[str, Any]) -> str:
        """Export content to Excel file, appending to existing data."""
        try:
            # Prepare data for export
            export_row = self._prepare_export_data(content_data)
            
            # Load existing data or create new DataFrame
            if self.excel_file.exists():
                try:
                    df = pd.read_excel(self.excel_file)
                    logger.info(f"Loaded existing Excel file with {len(df)} rows")
                except Exception as e:
                    logger.warning(f"Could not read existing Excel file: {e}. Creating new one.")
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
                logger.info("Creating new Excel file")
            
            # Add new row
            new_df = pd.DataFrame([export_row])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.excel_file, index=False, engine='openpyxl')
            
            logger.info(f"Content exported to {self.excel_file}")
            logger.info(f"Total entries in file: {len(df)}")
            
            return str(self.excel_file)
            
        except Exception as e:
            logger.error(f"Error exporting content to Excel: {e}")
            return f"Export failed: {str(e)}"
    
    def _prepare_export_data(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content data for Excel export."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Extract main content
        final_content = content_data.get("final_content", "")
        content_metadata = content_data.get("content_metadata", {})
        workflow_data = content_data.get("workflow_data", {})
        generation_metadata = content_data.get("generation_metadata", {})
        
        # Calculate content stats
        word_count = len(final_content.split()) if final_content else 0
        char_count = len(final_content) if final_content else 0
        
        # Extract workflow info
        agents_used = ", ".join(generation_metadata.get("agents_used", []))
        quality_score = content_data.get("quality_score", 0.0)
        
        # Prepare export row
        export_row = {
            "Timestamp": timestamp,
            "Topic": content_metadata.get("topic", ""),
            "Category": content_metadata.get("category", ""),
            "Industry": content_metadata.get("industry", ""),
            "Target Audience": content_metadata.get("target_audience", ""),
            "SEO Keywords": ", ".join(content_metadata.get("seo_keywords", [])),
            "Content Length": content_metadata.get("content_length", ""),
            "Word Count": word_count,
            "Character Count": char_count,
            "Quality Score": quality_score,
            "Agents Used": agents_used,
            "Rewriting Applied": generation_metadata.get("rewriting_applied", False),
            "Target Quality Achieved": generation_metadata.get("target_quality_achieved", False),
            "Research Insights": workflow_data.get("research_insights", "")[:500],  # Limit length
            "Review Suggestions Count": len(workflow_data.get("review_suggestions", [])),
            "Generated Content": final_content
        }
        
        return export_row
    
    def get_export_stats(self) -> Dict[str, Any]:
        """Get statistics about exported content."""
        if not self.excel_file.exists():
            return {"total_entries": 0, "file_exists": False}
        
        try:
            df = pd.read_excel(self.excel_file)
            stats = {
                "total_entries": len(df),
                "file_exists": True,
                "file_path": str(self.excel_file),
                "file_size_mb": round(self.excel_file.stat().st_size / 1024 / 1024, 2),
                "latest_entry": df["Timestamp"].max() if len(df) > 0 else None,
                "average_quality": round(df["Quality Score"].mean(), 2) if len(df) > 0 else 0,
                "top_categories": df["Category"].value_counts().head(3).to_dict() if len(df) > 0 else {}
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting export stats: {e}")
            return {"total_entries": 0, "file_exists": True, "error": str(e)}


# Global exporter instance
content_exporter = ContentExporter()
