#!/usr/bin/env python3
"""
Automated Jenosize Style Learning System

This script automatically scrapes content from Jenosize Ideas website and 
integrates it into the RAG system for enhanced style prompting and few-shot learning.

Usage:
    python auto_style_learner.py              # Run automated scraping and integration
    python auto_style_learner.py --test       # Test scraping without updating vector store
    python auto_style_learner.py --refresh    # Force refresh existing content
    python auto_style_learner.py --max 20     # Scrape up to 20 articles
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add project root to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent))

from .rag.jenosize_scraper import EnhancedJenosizeScraper
from .rag.simple_vector_store import simple_rag_system


class AutomatedStyleLearner:
    """Automated system for learning Jenosize's writing style from their website."""
    
    def __init__(self):
        self.scraper = EnhancedJenosizeScraper()
        self.rag_system = simple_rag_system
        
    async def run_full_automation(self, max_articles: int = 15, force_refresh: bool = False):
        """Run the complete automated style learning pipeline."""
        
        print("🎯 Jenosize Automated Style Learning System")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎪 Target articles: {max_articles}")
        print(f"🔄 Force refresh: {'Yes' if force_refresh else 'No'}")
        print()
        
        try:
            # Step 1: Check current vector store status
            current_count = self.rag_system.vector_store.get_document_count()
            print(f"📊 Current vector store contains {current_count} documents")
            
            # Step 2: Run automated scraping
            print("\n🕷️  Starting automated content scraping...")
            scraped_count = await self.scraper.update_vector_store_auto(
                max_articles=max_articles, 
                force_refresh=force_refresh
            )
            
            # Step 3: Verify integration
            new_count = self.rag_system.vector_store.get_document_count()
            print(f"\n📈 Vector store now contains {new_count} documents (+{new_count - current_count})")
            
            # Step 4: Test style learning
            if scraped_count > 0:
                print("\n🧪 Testing style learning with sample query...")
                await self._test_style_learning()
            
            # Step 5: Generate summary report
            await self._generate_summary_report(scraped_count, new_count - current_count)
            
            return scraped_count
            
        except Exception as e:
            logger.error(f"Error in automated style learning: {e}")
            print(f"\n❌ Error: {e}")
            return 0
    
    async def _test_style_learning(self):
        """Test the style learning system with sample queries."""
        test_topics = [
            "Digital transformation in retail",
            "Future of artificial intelligence in business",
            "Customer experience innovation"
        ]
        
        for topic in test_topics:
            try:
                examples = self.rag_system.get_relevant_examples(
                    topic=topic,
                    category="Digital Transformation",
                    n_results=2
                )
                
                jenosize_examples = [ex for ex in examples if ex['metadata'].get('source') == 'jenosize_website']
                
                if jenosize_examples:
                    print(f"  ✅ Found {len(jenosize_examples)} Jenosize examples for: {topic}")
                    example = jenosize_examples[0]
                    quality_score = example['metadata'].get('quality_score', 'N/A')
                    word_count = example['metadata'].get('word_count', 'N/A')
                    print(f"     📊 Quality: {quality_score}/10, Words: {word_count}")
                else:
                    print(f"  ⚠️  No Jenosize examples found for: {topic}")
                    
            except Exception as e:
                print(f"  ❌ Error testing {topic}: {e}")
    
    async def _generate_summary_report(self, scraped_count: int, added_count: int):
        """Generate a summary report of the automation results."""
        
        print("\n" + "=" * 60)
        print("📋 AUTOMATION SUMMARY REPORT")
        print("=" * 60)
        
        print(f"🎯 Articles successfully scraped: {scraped_count}")
        print(f"📈 New documents added to vector store: {added_count}")
        
        # Check for Jenosize content in vector store
        try:
            test_examples = self.rag_system.get_relevant_examples(
                topic="business digital transformation",
                n_results=5
            )
            
            jenosize_count = len([ex for ex in test_examples if ex['metadata'].get('source') == 'jenosize_website'])
            print(f"🏢 Jenosize-sourced examples available: {jenosize_count}")
            
            if jenosize_count > 0:
                avg_quality = sum(
                    ex['metadata'].get('quality_score', 0) 
                    for ex in test_examples 
                    if ex['metadata'].get('source') == 'jenosize_website'
                ) / jenosize_count
                
                print(f"⭐ Average content quality score: {avg_quality:.1f}/10")
                
        except Exception as e:
            print(f"⚠️  Could not analyze vector store content: {e}")
        
        print("\n🎉 NEXT STEPS:")
        if scraped_count > 0:
            print("  1. Your content generator now has access to real Jenosize content!")
            print("  2. Run content generation to see improved style matching")
            print("  3. Check data/ folder for detailed scraping results")
            print("  4. Monitor content quality and adjust if needed")
        else:
            print("  1. Check internet connectivity and website accessibility")
            print("  2. Review scraping patterns for website structure changes")
            print("  3. Consider running in test mode for debugging")
        
        print(f"\n📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async def test_scraping_only(self):
        """Test scraping without updating the vector store."""
        print("🧪 Testing Jenosize content scraping (no vector store updates)...")
        print("=" * 60)
        
        try:
            # Test page discovery
            articles = await self.scraper.scrape_ideas_page()
            print(f"📄 Discovered {len(articles)} potential content sources")
            
            if not articles:
                print("⚠️  No articles found. This might indicate:")
                print("   - Website structure has changed")
                print("   - Connectivity issues") 
                print("   - Content is dynamically loaded")
                return False
            
            # Show sample discoveries
            print("\n📋 Sample discovered content:")
            for i, article in enumerate(articles[:3], 1):
                print(f"  {i}. {article.get('title', 'No title')[:50]}...")
                print(f"     URL: {article.get('url', 'No URL')}")
                print(f"     Type: {article.get('source', 'Unknown')}")
            
            # Test content scraping
            full_articles = [a for a in articles if 'content' not in a and a.get('url') != self.scraper.ideas_url]
            
            if full_articles:
                print(f"\n🔍 Testing content scraping on first article...")
                test_article = full_articles[0]
                content = await self.scraper.scrape_article_content(test_article['url'])
                
                if content:
                    print("✅ Content scraping successful!")
                    print(f"   Title: {content.get('title', 'No title')}")
                    print(f"   Word count: {content.get('word_count', 0)}")
                    print(f"   Content preview: {content['content'][:150]}...")
                    return True
                else:
                    print("❌ Content scraping failed")
                    return False
            else:
                print("⚠️  No full articles found to test content scraping")
                return len(articles) > 0
                
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False


async def main():
    """Main entry point for the automated style learner."""
    parser = argparse.ArgumentParser(description="Automated Jenosize Style Learning System")
    parser.add_argument('--test', action='store_true', help='Test scraping without updating vector store')
    parser.add_argument('--refresh', action='store_true', help='Force refresh existing content')
    parser.add_argument('--max', type=int, default=15, help='Maximum number of articles to scrape')
    
    args = parser.parse_args()
    
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    learner = AutomatedStyleLearner()
    
    try:
        if args.test:
            success = await learner.test_scraping_only()
            sys.exit(0 if success else 1)
        else:
            count = await learner.run_full_automation(
                max_articles=args.max,
                force_refresh=args.refresh
            )
            sys.exit(0 if count > 0 else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

