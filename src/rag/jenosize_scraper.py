"""Enhanced scraper to extract Jenosize content for automated style learning."""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from .simple_vector_store import SimpleVectorStore


class EnhancedJenosizeScraper:
    """Enhanced scraper for Jenosize Ideas content with automated style learning."""
    
    def __init__(self):
        self.base_url = "https://www.jenosize.com"
        self.ideas_url = "https://www.jenosize.com/en/ideas"
        self.timeout = 30.0
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Initialize vector store for Jenosize content
        self.vector_store = SimpleVectorStore()
        
        # Cache for scraped URLs to avoid duplicates
        self.scraped_urls = set()
        
        # Rate limiting
        self.request_delay = 2.0  # seconds between requests
        self.last_request_time = 0
        
    async def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            await asyncio.sleep(self.request_delay - time_since_last)
        
        self.last_request_time = time.time()

    async def scrape_ideas_page(self) -> List[Dict[str, Any]]:
        """Enhanced scraping of Jenosize Ideas page with better article detection."""
        logger.info("Scraping Jenosize Ideas page with enhanced detection...")
        
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(self.ideas_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find article links and metadata
                articles = []
                found_urls = set()
                
                # Enhanced article detection patterns
                article_patterns = [
                    r'/ideas/[^/]+',
                    r'/article/[^/]+', 
                    r'/blog/[^/]+',
                    r'/insights/[^/]+',
                    r'/thought-leadership/[^/]+',
                    r'/en/ideas/[^/]+',
                ]
                
                # Look for all links
                all_links = soup.find_all('a', href=True)
                
                for link in all_links:
                    href = link.get('href', '').strip()
                    if not href:
                        continue
                    
                    # Check against patterns
                    is_article = any(re.search(pattern, href) for pattern in article_patterns)
                    
                    if is_article:
                        # Normalize URL
                        if href.startswith('/'):
                            full_url = urljoin(self.base_url, href)
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            continue
                        
                        if full_url not in found_urls:
                            found_urls.add(full_url)
                            
                            # Extract title and metadata
                            title = self._extract_enhanced_title(link, soup)
                            
                            if title and len(title) > 5:
                                articles.append({
                                    'url': full_url,
                                    'title': title,
                                    'source': 'jenosize_ideas',
                                    'discovered_at': datetime.now().isoformat()
                                })
                
                # Look for content cards, article previews, and structured content
                content_selectors = [
                    '[class*="article"]',
                    '[class*="post"]', 
                    '[class*="content"]',
                    '[class*="card"]',
                    '[class*="item"]',
                    '.editor-picks',
                    '[data-article]',
                    'article'
                ]
                
                for selector in content_selectors:
                    cards = soup.select(selector)
                    for card in cards:
                        # Try to extract article link from card
                        card_link = card.find('a', href=True)
                        if card_link:
                            href = card_link.get('href', '')
                            if any(re.search(pattern, href) for pattern in article_patterns):
                                full_url = urljoin(self.base_url, href) if href.startswith('/') else href
                                
                                if full_url not in found_urls:
                                    found_urls.add(full_url)
                                    title = self._extract_enhanced_title(card_link, card)
                                    
                                    if title and len(title) > 5:
                                        articles.append({
                                            'url': full_url,
                                            'title': title,
                                            'source': 'jenosize_ideas',
                                            'discovered_at': datetime.now().isoformat()
                                        })
                        
                        # Extract preview content if available
                        preview_text = self._extract_enhanced_preview_text(card)
                        if preview_text and len(preview_text) > 100:
                            articles.append({
                                'url': self.ideas_url,
                                'title': 'Jenosize Ideas Preview Content',
                                'content': preview_text,
                                'source': 'jenosize_preview',
                                'discovered_at': datetime.now().isoformat()
                            })
                
                # Remove duplicates and filter
                unique_articles = []
                seen_titles = set()
                
                for article in articles:
                    title_key = article['title'].lower().strip()
                    if title_key not in seen_titles and len(title_key) > 10:
                        seen_titles.add(title_key)
                        unique_articles.append(article)
                
                logger.info(f"Found {len(unique_articles)} unique articles/content pieces")
                return unique_articles
                
        except Exception as e:
            logger.error(f"Error scraping ideas page: {e}")
            return []
    
    async def scrape_article_content(self, article_url: str) -> Optional[Dict[str, Any]]:
        """Enhanced scraping of individual article content."""
        if article_url in self.scraped_urls:
            logger.info(f"Skipping already scraped URL: {article_url}")
            return None
            
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(article_url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract article content with enhanced methods
                content = self._extract_enhanced_article_content(soup)
                title = self._extract_enhanced_article_title(soup)
                category = self._extract_enhanced_category(soup)
                summary = self._extract_article_summary(soup)
                
                if content and len(content) > 200:  # Minimum content length
                    self.scraped_urls.add(article_url)
                    
                    # Analyze content characteristics for better style learning
                    style_characteristics = self._analyze_content_style(content)
                    
                    return {
                        'url': article_url,
                        'title': title,
                        'content': content,
                        'summary': summary,
                        'category': category,
                        'source': 'jenosize_article',
                        'word_count': len(content.split()),
                        'scraped_at': datetime.now().isoformat(),
                        'style_characteristics': style_characteristics
                    }
                
        except Exception as e:
            logger.warning(f"Error scraping article {article_url}: {e}")
            
        return None
    
    def _extract_enhanced_title(self, element, context_soup=None) -> str:
        """Enhanced title extraction with multiple fallbacks."""
        # Try different title sources in order of preference
        title_sources = [
            lambda: element.get('title'),
            lambda: element.get('aria-label'),
            lambda: element.get_text().strip(),
            lambda: element.find('img', alt=True).get('alt') if element.find('img', alt=True) else None,
        ]
        
        # If we have context, try to find title in parent elements
        if context_soup and hasattr(element, 'parent'):
            parent = element.parent
            for _ in range(3):  # Check up to 3 levels up
                if parent:
                    title_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if title_elem:
                        title_sources.append(lambda: title_elem.get_text().strip())
                    parent = parent.parent
        
        for source in title_sources:
            try:
                title = source()
                if title:
                    cleaned = self._clean_text(title)
                    if len(cleaned) > 5:
                        return cleaned
            except:
                continue
        
        return "Jenosize Article"
    
    def _extract_enhanced_article_title(self, soup: BeautifulSoup) -> str:
        """Enhanced article title extraction."""
        # Try different title selectors in order of preference
        title_selectors = [
            'h1.title',
            'h1.article-title', 
            'h1.post-title',
            '.page-title h1',
            '.article-header h1',
            'h1',
            '.title',
            '.article-title',
            '.post-title',
            'meta[property="og:title"]',
            'meta[name="twitter:title"]',
            'title'
        ]
        
        for selector in title_selectors:
            try:
                if selector.startswith('meta'):
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get('content', '')
                else:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text()
                
                if title:
                    cleaned = self._clean_text(title)
                    if len(cleaned) > 5 and not self._is_generic_title(cleaned):
                        return cleaned
            except:
                continue
        
        return "Jenosize Article"
    
    def _extract_enhanced_category(self, soup: BeautifulSoup) -> str:
        """Enhanced category extraction."""
        # Try to find category indicators
        category_selectors = [
            '.article-category',
            '.post-category',
            '.category',
            '.tag:first-child',
            '.tags .tag:first-child',
            '[class*="category"]:not([class*="categories"])',
            '[data-category]',
            '.breadcrumb a:last-child',
            'meta[property="article:section"]',
            'meta[name="keywords"]'
        ]
        
        for selector in category_selectors:
            try:
                if selector.startswith('meta'):
                    elem = soup.select_one(selector)
                    if elem:
                        category = elem.get('content', '')
                elif selector == '[data-category]':
                    elem = soup.select_one(selector)
                    if elem:
                        category = elem.get('data-category', '')
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        category = elem.get_text()
                
                if category:
                    cleaned = self._clean_text(category)
                    if cleaned and not self._is_generic_category(cleaned):
                        return cleaned
            except:
                continue
        
        return "Business Insights"
    
    def _extract_enhanced_article_content(self, soup: BeautifulSoup) -> str:
        """Enhanced article content extraction with better cleaning."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript']):
            element.decompose()
        
        # Try different content selectors in order of preference
        content_selectors = [
            '.article-content',
            '.post-content', 
            '.entry-content',
            'article .content',
            '.main-content',
            'main article',
            'article',
            '.content',
            'main',
            '[role="main"]'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove navigation and sidebar elements within content
                for unwanted in content_elem(['nav', 'aside', '.sidebar', '.navigation', '.menu']):
                    unwanted.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                content = self._clean_enhanced_content(content)
                if len(content) > 200:
                    return content
        
        # Fallback: extract from body but be more selective
        body = soup.find('body')
        if body:
            # Remove common non-content elements
            for unwanted in body(['.header', '.footer', '.sidebar', '.navigation', '.menu', '.ads']):
                unwanted.decompose()
                
            content = body.get_text(separator='\n', strip=True)
            return self._clean_enhanced_content(content)
        
        return ""
    
    def _extract_enhanced_preview_text(self, element) -> str:
        """Enhanced preview text extraction."""
        # Try to find preview/summary text
        preview_selectors = [
            '.excerpt',
            '.summary', 
            '.preview',
            '.description',
            'p:first-of-type'
        ]
        
        for selector in preview_selectors:
            preview_elem = element.select_one(selector)
            if preview_elem:
                text = preview_elem.get_text(separator=' ', strip=True)
                cleaned = self._clean_text(text)
                if len(cleaned) > 50:
                    return cleaned
        
        # Fallback to general text
        text = element.get_text(separator=' ', strip=True)
        return self._clean_text(text)
    
    def _extract_article_summary(self, soup: BeautifulSoup) -> str:
        """Extract article summary/description."""
        summary_selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]', 
            'meta[name="twitter:description"]',
            '.article-summary',
            '.post-excerpt',
            '.excerpt',
            '.summary'
        ]
        
        for selector in summary_selectors:
            try:
                if selector.startswith('meta'):
                    elem = soup.select_one(selector)
                    if elem:
                        summary = elem.get('content', '')
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        summary = elem.get_text()
                
                if summary:
                    cleaned = self._clean_text(summary)
                    if len(cleaned) > 20:
                        return cleaned
            except:
                continue
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
        
        return text[:500]  # Limit length
    
    def _clean_enhanced_content(self, content: str) -> str:
        """Enhanced content cleaning with better filtering."""
        if not content:
            return ""
        
        # Split into lines and clean
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip short lines, navigation, etc.
            if (len(line) > 30 and 
                not self._is_navigation_line(line) and 
                not self._is_boilerplate_line(line) and
                self._is_meaningful_content(line)):
                cleaned_lines.append(line)
        
        content = '\n\n'.join(cleaned_lines)
        
        # Remove extra whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        return content[:5000]  # Increased limit for better content
    
    def _is_navigation_line(self, line: str) -> bool:
        """Check if line is likely navigation/menu content."""
        nav_indicators = [
            'home', 'about', 'contact', 'menu', 'login', 'register',
            'privacy', 'terms', 'cookie', 'follow us', 'social',
            'facebook', 'twitter', 'linkedin', 'instagram', 'subscribe',
            'newsletter', 'copyright', 'all rights reserved', 'terms of service'
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in nav_indicators)
    
    def _is_boilerplate_line(self, line: str) -> bool:
        """Check if line is boilerplate/template content."""
        boilerplate_patterns = [
            r'^\d+\s+(minutes?|hours?|days?)\s+ago$',
            r'^(read more|continue reading|learn more)$',
            r'^(share|like|comment|subscribe)$',
            r'^tags?:',
            r'^categories?:',
            r'^posted (on|in|by)',
            r'^written by',
            r'^\d+\s+comments?$'
        ]
        
        line_lower = line.lower().strip()
        return any(re.search(pattern, line_lower) for pattern in boilerplate_patterns)
    
    def _is_meaningful_content(self, line: str) -> bool:
        """Check if line contains meaningful content."""
        # Must contain some letters
        if not re.search(r'[a-zA-Z]', line):
            return False
        
        # Should have reasonable word count
        words = line.split()
        if len(words) < 5:
            return False
        
        # Should not be mostly numbers or symbols
        letter_count = sum(1 for c in line if c.isalpha())
        if letter_count < len(line) * 0.5:
            return False
        
        return True
    
    def _is_generic_title(self, title: str) -> bool:
        """Check if title is too generic."""
        generic_titles = [
            'home', 'about', 'contact', 'blog', 'news', 'articles',
            'page not found', '404', 'error', 'loading'
        ]
        return title.lower().strip() in generic_titles
    
    def _is_generic_category(self, category: str) -> bool:
        """Check if category is too generic."""
        generic_categories = [
            'home', 'about', 'contact', 'general', 'other', 'misc',
            'uncategorized', 'default'
        ]
        return category.lower().strip() in generic_categories
    
    def _analyze_content_style(self, content: str) -> Dict[str, Any]:
        """Analyze content for style characteristics."""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        
        # Basic metrics
        word_count = len(words)
        sentence_count = len([s for s in sentences if s.strip()])
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Style indicators
        has_questions = '?' in content
        has_bullet_points = bool(re.search(r'^\s*[-•*]\s+', content, re.MULTILINE))
        has_numbers = bool(re.search(r'\d+', content))
        
        # Business/professional terms
        business_terms = [
            'digital transformation', 'innovation', 'strategy', 'technology',
            'business', 'market', 'customer', 'solution', 'opportunity',
            'growth', 'efficiency', 'optimization', 'automation'
        ]
        
        business_term_count = sum(1 for term in business_terms if term.lower() in content.lower())
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'has_questions': has_questions,
            'has_bullet_points': has_bullet_points,
            'has_numbers': has_numbers,
            'business_term_density': round(business_term_count / max(word_count, 1) * 100, 2),
            'formality_score': self._calculate_formality_score(content)
        }
    
    def _calculate_formality_score(self, content: str) -> float:
        """Calculate a simple formality score (0-10)."""
        # Factors that increase formality
        formal_indicators = [
            r'\b(furthermore|moreover|consequently|therefore|thus)\b',
            r'\b(organizations?|enterprises?|corporations?)\b',
            r'\b(implementation|optimization|transformation)\b',
            r'\b(strategic|comprehensive|substantial)\b'
        ]
        
        # Factors that decrease formality  
        informal_indicators = [
            r'\b(gonna|wanna|gotta)\b',
            r'!{2,}',
            r'\b(awesome|cool|amazing)\b'
        ]
        
        formal_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in formal_indicators)
        informal_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in informal_indicators)
        
        # Base score of 5, adjust based on indicators
        score = 5.0 + (formal_count * 0.5) - (informal_count * 0.8)
        return max(0.0, min(10.0, score))
    
    async def update_vector_store_auto(self, max_articles: int = 15, force_refresh: bool = False):
        """Enhanced automated vector store update with smart content selection."""
        logger.info(f"Starting automated Jenosize content scraping (max: {max_articles} articles)...")
        
        try:
            # Clear existing Jenosize content if force refresh
            if force_refresh:
                await self._clear_jenosize_content()
            
            # Get articles from ideas page
            articles = await self.scrape_ideas_page()
            logger.info(f"Discovered {len(articles)} potential content sources")
            
            # Prioritize articles with full URLs over preview content
            full_articles = [a for a in articles if 'content' not in a and a.get('url') != self.ideas_url]
            preview_content = [a for a in articles if 'content' in a]
            
            # Scrape individual articles
            scraped_content = []
            success_count = 0
            
            # Process full articles first
            for i, article in enumerate(full_articles[:max_articles]):
                if success_count >= max_articles:
                    break
                    
                logger.info(f"Scraping article {i+1}/{min(len(full_articles), max_articles)}: {article.get('title', 'Unknown')}")
                content = await self.scrape_article_content(article['url'])
                
                if content:
                    scraped_content.append(content)
                    success_count += 1
                    logger.info(f"✓ Successfully scraped: {content['title'][:60]}...")
                else:
                    logger.warning(f"✗ Failed to scrape: {article.get('title', 'Unknown')}")
            
            # Add preview content if we need more
            remaining_slots = max_articles - success_count
            if remaining_slots > 0 and preview_content:
                logger.info(f"Adding {min(remaining_slots, len(preview_content))} preview content pieces")
                scraped_content.extend(preview_content[:remaining_slots])
            
            # Add to vector store with enhanced metadata
            added_count = 0
            for i, content in enumerate(scraped_content):
                if content.get('content'):
                    doc_id = f"jenosize_auto_{int(time.time())}_{i+1}"
                    
                    # Enhanced metadata for better style learning
                    metadata = {
                        "category": content.get('category', 'Business Insights'),
                        "industry": "Digital Transformation", 
                        "tone": "jenosize_professional",
                        "type": "article" if content.get('source') == 'jenosize_article' else "preview",
                        "source": "jenosize_website",
                        "word_count": content.get('word_count', len(content['content'].split())),
                        "url": content.get('url', ''),
                        "scraped_at": content.get('scraped_at', datetime.now().isoformat()),
                        "title": content.get('title', 'Jenosize Content'),
                        "summary": content.get('summary', ''),
                        "style_characteristics": content.get('style_characteristics', {}),
                        "framework": "FUTURE",  # Jenosize's framework
                        "quality_score": self._calculate_content_quality(content['content'])
                    }
                    
                    try:
                        self.vector_store.add_document(
                            content=content['content'],
                            metadata=metadata,
                            doc_id=doc_id
                        )
                        added_count += 1
                        logger.info(f"✓ Added to vector store: {content.get('title', 'Unknown')[:50]}...")
                    except Exception as e:
                        logger.warning(f"✗ Failed to add content to vector store: {e}")
            
            # Save scraped content for inspection
            if scraped_content:
                await self._save_scraped_content_enhanced(scraped_content)
            
            logger.info(f"🎉 Successfully added {added_count} Jenosize articles to vector store")
            return added_count
            
        except Exception as e:
            logger.error(f"Error in automated vector store update: {e}")
            return 0
    
    async def _clear_jenosize_content(self):
        """Clear existing Jenosize content from vector store."""
        logger.info("Clearing existing Jenosize content...")
        # This would need to be implemented based on the vector store's capabilities
        # For now, we'll just log the intent
        logger.info("Note: Manual clearing of existing content may be needed")
    
    def _calculate_content_quality(self, content: str) -> float:
        """Calculate a quality score for content (0-10)."""
        if not content:
            return 0.0
        
        words = content.split()
        word_count = len(words)
        
        # Factors that increase quality
        quality_score = 5.0  # Base score
        
        # Word count (optimal range: 300-2000 words)
        if 300 <= word_count <= 2000:
            quality_score += 1.0
        elif word_count > 100:
            quality_score += 0.5
        
        # Sentence structure variety
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) > 5:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                variety = len(set(sentence_lengths)) / len(sentence_lengths)
                quality_score += variety * 1.0
        
        # Business terminology
        business_terms = [
            'digital transformation', 'innovation', 'strategy', 'technology',
            'business', 'market', 'customer', 'solution', 'opportunity'
        ]
        term_count = sum(1 for term in business_terms if term.lower() in content.lower())
        quality_score += min(term_count * 0.2, 1.0)
        
        # Paragraph structure
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if len(paragraphs) >= 3:
            quality_score += 0.5
        
        return min(10.0, max(0.0, quality_score))
    
    async def _save_scraped_content_enhanced(self, content_list: List[Dict[str, Any]]):
        """Save scraped content with enhanced metadata."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jenosize_scraped_{timestamp}.json"
        output_file = Path("data") / filename
        output_file.parent.mkdir(exist_ok=True)
        
        # Prepare data for saving
        save_data = {
            "scraped_at": datetime.now().isoformat(),
            "total_articles": len(content_list),
            "scraper_version": "enhanced_v2",
            "articles": content_list
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved detailed scraped content to: {output_file}")
    
    async def save_scraped_content(self, filename: str = "jenosize_content.json"):
        """Save scraped content to file for inspection (legacy method)."""
        return await self._save_scraped_content_enhanced(
            await self.scrape_ideas_page()
        )


# Backward compatibility alias
JenosizeScraper = EnhancedJenosizeScraper


async def main():
    """Enhanced main function to test the automated scraper."""
    scraper = EnhancedJenosizeScraper()
    
    print("🚀 Starting Enhanced Jenosize Content Scraper...")
    print("=" * 60)
    
    try:
        # Run automated scraping and vector store update
        count = await scraper.update_vector_store_auto(max_articles=10, force_refresh=False)
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully processed {count} Jenosize articles!")
        print("🎯 Articles are now available for style prompting and few-shot learning")
        print("📊 Check the data/ folder for detailed scraping results")
        
        if count > 0:
            print("\n🔥 Your content generator now has access to real Jenosize content!")
            print("💡 Run your content generation to see the improved style matching")
        else:
            print("\n⚠️  No content was successfully scraped.")
            print("💭 This might be due to website structure changes or connectivity issues")
            print("🔧 Consider checking the scraping patterns or running in debug mode")
            
    except Exception as e:
        print(f"\n❌ Error during automated scraping: {e}")
        print("🛠️  Check logs for detailed error information")


async def test_scraping():
    """Test function for debugging scraping issues."""
    scraper = EnhancedJenosizeScraper()
    
    print("🔍 Testing Jenosize Ideas page scraping...")
    articles = await scraper.scrape_ideas_page()
    
    print(f"📄 Found {len(articles)} potential content sources:")
    for i, article in enumerate(articles[:5], 1):
        print(f"  {i}. {article.get('title', 'No title')[:60]}...")
        print(f"     URL: {article.get('url', 'No URL')}")
        print(f"     Source: {article.get('source', 'Unknown')}")
        print()
    
    if articles:
        print("🧪 Testing article content scraping...")
        test_article = next((a for a in articles if 'content' not in a and a.get('url') != scraper.ideas_url), None)
        
        if test_article:
            content = await scraper.scrape_article_content(test_article['url'])
            if content:
                print(f"✅ Successfully scraped test article:")
                print(f"   Title: {content.get('title', 'No title')}")
                print(f"   Word count: {content.get('word_count', 0)}")
                print(f"   Quality score: {content.get('style_characteristics', {}).get('formality_score', 'N/A')}")
                print(f"   Content preview: {content['content'][:200]}...")
            else:
                print("❌ Failed to scrape test article content")
        else:
            print("⚠️  No suitable test article found")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_scraping())
    else:
        asyncio.run(main())
