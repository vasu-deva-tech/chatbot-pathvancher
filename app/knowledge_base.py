import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """Manages knowledge base for semantic search"""
    
    def __init__(self):
        self.qa_pairs: List[Dict] = []
        self.embeddings: List[List[float]] = []
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load knowledge base from JSON file"""
        try:
            kb_path = Path(__file__).parent.parent / "knowledge_base.json"
            if kb_path.exists():
                with open(kb_path, "r") as f:
                    data = json.load(f)
                    self.qa_pairs = data.get("qa_pairs", [])
                logger.info(f"✓ Loaded {len(self.qa_pairs)} Q&A pairs")
            else:
                logger.warning(f"Knowledge base file not found at {kb_path}")
                self.qa_pairs = []
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            self.qa_pairs = []
    
    def add_qa_pair(self, question: str, answer: str):
        """Add a Q&A pair to knowledge base"""
        self.qa_pairs.append({
            "question": question,
            "answer": answer
        })
    
    def search(self, query: str, embeddings_func, top_k: int = 3) -> List[Dict]:
        """
        Search knowledge base using semantic similarity
        
        Args:
            query: User query
            embeddings_func: Function to get embeddings (e.g., OpenAI)
            top_k: Number of top results to return
        
        Returns:
            List of matching Q&A pairs with similarity scores
        """
        try:
            # Get query embedding
            query_embedding = embeddings_func(query)
            
            if not query_embedding:
                return []
            
            results = []
            
            for qa in self.qa_pairs:
                # Get KB question embedding
                kb_embedding = embeddings_func(qa["question"])
                if not kb_embedding:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, kb_embedding)
                
                results.append({
                    "question": qa["question"],
                    "answer": qa["answer"],
                    "similarity": similarity
                })
            
            # Sort by similarity and return top K
            results.sort(key=lambda x: x["similarity"], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

# Global knowledge base instance
knowledge_base = KnowledgeBase()
