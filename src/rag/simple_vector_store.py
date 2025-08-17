"""Simple vector store implementation compatible with Python 3.9."""

import os
import json
import pickle
import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

from ..core.config import config


class SimpleVectorStore:
    """Simple vector store using TF-IDF and SQLite for Python 3.9 compatibility."""
    
    def __init__(self):
        self.data_dir = Path("data/simple_db")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / "vector_store.db"
        self.vectorizer_path = self.data_dir / "vectorizer.pkl"
        
        # Initialize database
        self._init_database()
        
        # Initialize or load vectorizer
        self.vectorizer = None
        self.document_vectors = None
        self._load_or_create_vectorizer()
        
        logger.info(f"Simple vector store initialized with {self.get_document_count()} documents")
    
    def _init_database(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_or_create_vectorizer(self):
        """Load existing vectorizer or create new one."""
        if self.vectorizer_path.exists():
            try:
                with open(self.vectorizer_path, 'rb') as f:
                    data = pickle.load(f)
                    self.vectorizer = data['vectorizer']
                    self.document_vectors = data['vectors']
                logger.info("Loaded existing vectorizer")
            except Exception as e:
                logger.warning(f"Failed to load vectorizer: {e}, creating new one")
                self._create_new_vectorizer()
        else:
            self._create_new_vectorizer()
    
    def _create_new_vectorizer(self):
        """Create new TF-IDF vectorizer."""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=1.0,  # Allow all documents
            min_df=1     # Minimum document frequency
        )
        
        # Get all documents to fit vectorizer
        documents = self._get_all_documents()
        if documents:
            contents = [doc['content'] for doc in documents]
            self.document_vectors = self.vectorizer.fit_transform(contents)
            self._save_vectorizer()
        else:
            self.document_vectors = None
    
    def _save_vectorizer(self):
        """Save vectorizer and vectors to disk."""
        try:
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump({
                    'vectorizer': self.vectorizer,
                    'vectors': self.document_vectors
                }, f)
        except Exception as e:
            logger.error(f"Failed to save vectorizer: {e}")
    
    def _get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, content, metadata FROM documents')
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                'id': row[0],
                'content': row[1],
                'metadata': json.loads(row[2])
            })
        
        conn.close()
        return documents
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> str:
        """Add a document to the vector store."""
        try:
            if doc_id is None:
                doc_id = f"doc_{self.get_document_count() + 1}"
            
            # Add to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT OR REPLACE INTO documents (id, content, metadata) VALUES (?, ?, ?)',
                (doc_id, content, json.dumps(metadata))
            )
            
            conn.commit()
            conn.close()
            
            # Rebuild vectorizer with new document
            self._create_new_vectorizer()
            
            logger.info(f"Added document {doc_id} to vector store")
            return doc_id
        
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector store."""
        try:
            if self.vectorizer is None or self.document_vectors is None:
                logger.warning("No vectorizer available for search")
                return []
            
            # Get all documents
            documents = self._get_all_documents()
            if not documents:
                return []
            
            # Filter documents by metadata if specified
            if filter_metadata:
                filtered_docs = []
                filtered_indices = []
                for i, doc in enumerate(documents):
                    if self._matches_filter(doc['metadata'], filter_metadata):
                        filtered_docs.append(doc)
                        filtered_indices.append(i)
                documents = filtered_docs
                if not documents:
                    return []
            else:
                filtered_indices = list(range(len(documents)))
            
            # Vectorize query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            if len(filtered_indices) < len(self.document_vectors.toarray()):
                # Filter document vectors
                filtered_vectors = self.document_vectors[filtered_indices]
            else:
                filtered_vectors = self.document_vectors
            
            similarities = cosine_similarity(query_vector, filtered_vectors).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:n_results]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only return documents with positive similarity
                    results.append({
                        "content": documents[idx]['content'],
                        "metadata": documents[idx]['metadata'],
                        "distance": 1 - similarities[idx],  # Convert similarity to distance
                        "id": documents[idx]['id']
                    })
            
            logger.info(f"Found {len(results)} similar documents")
            return results
        
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def _matches_filter(self, metadata: Dict[str, Any], filter_metadata: Dict[str, Any]) -> bool:
        """Check if document metadata matches filter criteria."""
        for key, value in filter_metadata.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM documents')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM documents')
            conn.commit()
            conn.close()
            
            # Reset vectorizer
            self.vectorizer = None
            self.document_vectors = None
            if self.vectorizer_path.exists():
                self.vectorizer_path.unlink()
            
            logger.info("Cleared vector store collection")
        
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise


class SimpleRAGSystem:
    """Simple RAG system using TF-IDF for Python 3.9 compatibility."""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self._initialize_examples()
    
    def _initialize_examples(self):
        """Initialize the vector store with Jenosize content examples."""
        if self.vector_store.get_document_count() == 0:
            self._create_example_content()
    
    def _create_example_content(self):
        """Create example Jenosize content for style learning."""
        examples = [
            {
                "content": """Digital transformation is no longer a choice but a necessity for businesses navigating today's rapidly evolving landscape. Organizations that embrace this shift are positioning themselves for sustainable growth and competitive advantage.

The journey begins with understanding that digital transformation extends far beyond technology adoption. It requires a fundamental rethinking of business processes, customer interactions, and organizational culture. Companies must develop a clear vision that aligns digital initiatives with strategic business objectives.

Key areas of focus include data-driven decision making, customer experience optimization, and operational efficiency enhancement. By leveraging advanced analytics, artificial intelligence, and cloud technologies, businesses can unlock new opportunities for innovation and growth.

Success in digital transformation demands strong leadership commitment, cross-functional collaboration, and a willingness to embrace change. Organizations that take a holistic approach, addressing both technological and human factors, are more likely to achieve lasting transformation.""",
                "metadata": {
                    "category": "Digital Transformation",
                    "industry": "General",
                    "tone": "professional",
                    "type": "article",
                    "word_count": 150
                }
            },
            {
                "content": """Artificial Intelligence is reshaping the business landscape, offering unprecedented opportunities for growth and efficiency. Forward-thinking organizations are leveraging AI not just as a tool, but as a strategic enabler of business transformation.

The most successful AI implementations focus on solving specific business problems rather than pursuing technology for its own sake. Companies are finding value in automating routine tasks, enhancing customer experiences, and generating actionable insights from vast amounts of data.

Key considerations for AI adoption include data quality, ethical implications, and workforce readiness. Organizations must invest in building AI literacy across all levels while ensuring responsible deployment of these powerful technologies.

The future belongs to businesses that can effectively integrate AI into their core operations while maintaining human-centered approaches to customer service and innovation.""",
                "metadata": {
                    "category": "AI & Automation",
                    "industry": "Technology",
                    "tone": "professional",
                    "type": "article",
                    "word_count": 130
                }
            },
            {
                "content": """The modern workplace is undergoing a fundamental transformation, driven by technological advancement and changing employee expectations. Organizations must adapt their approaches to talent management, collaboration, and workplace culture to thrive in this new environment.

Hybrid work models have become the norm, requiring businesses to rethink traditional office structures and management practices. Companies are investing in digital collaboration tools, flexible workspace solutions, and new performance measurement frameworks.

Employee well-being and work-life balance have emerged as critical factors in talent retention and productivity. Organizations that prioritize these aspects are seeing improved employee satisfaction, reduced turnover, and enhanced innovation capacity.

The future of work demands a balance between technological efficiency and human connection. Successful companies will be those that can create engaging, purposeful work experiences while leveraging technology to enhance rather than replace human capabilities.""",
                "metadata": {
                    "category": "Future of Work",
                    "industry": "General",
                    "tone": "professional",
                    "type": "article",
                    "word_count": 140
                }
            }
        ]
        
        for i, example in enumerate(examples):
            self.vector_store.add_document(
                content=example["content"],
                metadata=example["metadata"],
                doc_id=f"example_{i+1}"
            )
        
        logger.info("Initialized vector store with example content")
    
    def get_relevant_examples(
        self,
        topic: str,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Enhanced example retrieval with smart prioritization of Jenosize content."""
        
        all_examples = []
        
        # Step 1: Try to get real Jenosize content first (highest priority)
        jenosize_examples = self.vector_store.search(
            query=topic,
            n_results=n_results * 2,  # Get more to have better selection
            filter_metadata={"source": "jenosize_website"}
        )
        
        # Step 2: Get manual Jenosize-style content (medium priority)
        manual_examples = self.vector_store.search(
            query=topic,
            n_results=n_results,
            filter_metadata={"source": "jenosize_style"}
        )
        
        # Step 3: Get template examples (lowest priority)
        filter_metadata = {}
        if category:
            filter_metadata["category"] = category
        if industry and industry != "General":
            filter_metadata["industry"] = industry
        
        template_examples = self.vector_store.search(
            query=topic,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # Combine and prioritize results
        priority_sources = ["jenosize_website", "jenosize_style", "manual", "template"]
        
        # Sort examples by source priority and quality
        def get_priority_score(example):
            source = example['metadata'].get('source', 'template')
            quality_score = example['metadata'].get('quality_score', 5.0)
            
            # Base priority by source
            if source == "jenosize_website":
                priority = 100
            elif source == "jenosize_style": 
                priority = 80
            elif source == "manual":
                priority = 60
            else:
                priority = 40
            
            # Boost by quality and relevance (distance is lower = better)
            distance = example.get('distance', 1.0)
            relevance_boost = max(0, (1.0 - distance) * 20)
            quality_boost = quality_score * 2
            
            return priority + relevance_boost + quality_boost
        
        # Combine all examples and remove duplicates
        all_candidates = jenosize_examples + manual_examples + template_examples
        seen_content = set()
        unique_examples = []
        
        for example in all_candidates:
            content_hash = hash(example['content'][:100])  # Use first 100 chars as hash
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_examples.append(example)
        
        # Sort by priority score and take top results
        unique_examples.sort(key=get_priority_score, reverse=True)
        final_examples = unique_examples[:n_results]
        
        # Log what we're using
        jenosize_count = len([ex for ex in final_examples if ex['metadata'].get('source') == 'jenosize_website'])
        manual_count = len([ex for ex in final_examples if ex['metadata'].get('source') == 'jenosize_style'])
        template_count = len(final_examples) - jenosize_count - manual_count
        
        logger.info(f"Style examples: {jenosize_count} real Jenosize, {manual_count} manual, {template_count} template")
        
        return final_examples


# Global RAG system instance
simple_rag_system = SimpleRAGSystem()
