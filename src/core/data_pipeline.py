"""Data pipeline for processing and cleaning input data."""

import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import asyncio
import httpx
from bs4 import BeautifulSoup
from loguru import logger

from .config import config


class DataProcessor:
    """Handles data cleaning and preprocessing for content generation."""
    
    def __init__(self):
        self.max_content_length = config.content.max_content_length
        self.timeout = 60.0  # Longer timeout for web scraping
    
    async def process_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process and clean input data for content generation."""
        logger.info("Processing input data")
        
        processed_data = {
            "topic": self._clean_text(raw_input.get("topic", "")),
            "category": self._validate_category(raw_input.get("category", "")),
            "industry": self._validate_industry(raw_input.get("industry", "")),
            "target_audience": self._clean_text(raw_input.get("target_audience", "business executives")),
            "seo_keywords": self._process_keywords(raw_input.get("seo_keywords", [])),
            "content_length": self._validate_content_length(raw_input.get("content_length", "medium")),
            "source_urls": raw_input.get("source_urls", []),
            "additional_context": self._clean_text(raw_input.get("additional_context", ""))
        }
        
        # Process source URLs if provided
        if processed_data["source_urls"]:
            source_content = await self._extract_source_content(processed_data["source_urls"])
            processed_data["source_content"] = source_content
        
        # Validate required fields
        self._validate_processed_data(processed_data)
        
        logger.info(f"Successfully processed input data for topic: {processed_data['topic']}")
        return processed_data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text input."""
        if not isinstance(text, str):
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove potentially harmful content
        cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove HTML tags
        cleaned = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', cleaned)  # Keep safe characters
        
        # Truncate if too long
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + "..."
        
        return cleaned
    
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category input."""
        if not category:
            return "Digital Transformation"  # Default category
        
        valid_categories = config.content_categories
        category_clean = self._clean_text(category)
        
        # Check for exact match
        if category_clean in valid_categories:
            return category_clean
        
        # Check for partial match
        for valid_cat in valid_categories:
            if category_clean.lower() in valid_cat.lower() or valid_cat.lower() in category_clean.lower():
                return valid_cat
        
        # Return default if no match
        logger.warning(f"Unknown category '{category}', using default")
        return "Digital Transformation"
    
    def _validate_industry(self, industry: str) -> str:
        """Validate and normalize industry input."""
        if not industry:
            return "General"  # Default industry
        
        valid_industries = config.industries + ["General"]
        industry_clean = self._clean_text(industry)
        
        # Check for exact match
        if industry_clean in valid_industries:
            return industry_clean
        
        # Check for partial match
        for valid_ind in valid_industries:
            if industry_clean.lower() in valid_ind.lower() or valid_ind.lower() in industry_clean.lower():
                return valid_ind
        
        # Return default if no match
        logger.warning(f"Unknown industry '{industry}', using General")
        return "General"
    
    def _process_keywords(self, keywords: List[str]) -> List[str]:
        """Process and clean SEO keywords."""
        if not isinstance(keywords, list):
            if isinstance(keywords, str):
                keywords = [k.strip() for k in keywords.split(",")]
            else:
                return []
        
        processed_keywords = []
        for keyword in keywords[:10]:  # Limit to 10 keywords
            if isinstance(keyword, str):
                clean_keyword = self._clean_text(keyword)
                if clean_keyword and len(clean_keyword) <= 50:
                    processed_keywords.append(clean_keyword)
        
        return processed_keywords
    
    def _validate_content_length(self, content_length: str) -> str:
        """Validate content length setting."""
        valid_lengths = ["short", "medium", "long"]
        if content_length.lower() in valid_lengths:
            return content_length.lower()
        return "medium"  # Default
    
    async def _extract_source_content(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Extract content from source URLs."""
        if not urls:
            return []
        
        source_content = []
        
        for url in urls[:5]:  # Limit to 5 URLs
            try:
                content = await self._fetch_url_content(url)
                if content:
                    source_content.append(content)
            except Exception as e:
                logger.warning(f"Failed to extract content from {url}: {e}")
        
        return source_content
    
    async def _fetch_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and extract content from a URL."""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.warning(f"Invalid URL: {url}")
                return None
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "No title"
                
                # Extract main content
                content_text = self._extract_main_content(soup)
                
                if not content_text:
                    logger.warning(f"No content extracted from {url}")
                    return None
                
                return {
                    "url": url,
                    "title": title_text[:200],  # Truncate title
                    "content": content_text[:2000],  # Truncate content
                    "domain": parsed_url.netloc
                }
        
        except Exception as e:
            logger.warning(f"Error fetching content from {url}: {e}")
            return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
        
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I))
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            # Fallback to body content
            body = soup.find('body')
            text = body.get_text(separator=' ', strip=True) if body else soup.get_text(separator=' ', strip=True)
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\n+', '\n', text)  # Normalize newlines
        
        return text.strip()
    
    def _validate_processed_data(self, data: Dict[str, Any]) -> None:
        """Validate processed data for required fields."""
        if not data.get("topic"):
            raise ValueError("Topic is required and cannot be empty")
        
        if len(data["topic"]) < 3:
            raise ValueError("Topic must be at least 3 characters long")
        
        logger.info("Input data validation completed successfully")


class ContentValidator:
    """Validates generated content for quality and compliance."""
    
    def __init__(self):
        self.min_word_count = 100
        self.max_word_count = 3000
    
    def validate_content(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated content quality."""
        validation_results = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "metrics": {}
        }
        
        # Basic content checks
        word_count = len(content.split())
        validation_results["metrics"]["word_count"] = word_count
        
        if word_count < self.min_word_count:
            validation_results["issues"].append(f"Content too short: {word_count} words (minimum: {self.min_word_count})")
            validation_results["is_valid"] = False
        
        if word_count > self.max_word_count:
            validation_results["issues"].append(f"Content too long: {word_count} words (maximum: {self.max_word_count})")
            validation_results["is_valid"] = False
        
        # Check for empty content
        if not content.strip():
            validation_results["issues"].append("Content is empty")
            validation_results["is_valid"] = False
        
        # Check for placeholder content
        placeholder_patterns = [
            r'\[.*?\]',  # [placeholder]
            r'TODO',
            r'PLACEHOLDER',
            r'Lorem ipsum'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                validation_results["warnings"].append(f"Possible placeholder content found: {pattern}")
        
        # Check SEO keyword integration
        seo_keywords = metadata.get("seo_keywords", [])
        if seo_keywords:
            content_lower = content.lower()
            missing_keywords = []
            for keyword in seo_keywords:
                if keyword.lower() not in content_lower:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                validation_results["warnings"].append(f"SEO keywords not found in content: {', '.join(missing_keywords)}")
        
        # Calculate readability metrics
        sentences = len(re.split(r'[.!?]+', content))
        if sentences > 0:
            avg_words_per_sentence = word_count / sentences
            validation_results["metrics"]["avg_words_per_sentence"] = round(avg_words_per_sentence, 2)
            
            if avg_words_per_sentence > 25:
                validation_results["warnings"].append("Average sentence length is high, consider breaking up long sentences")
        
        return validation_results


# Global instances
data_processor = DataProcessor()
content_validator = ContentValidator()
