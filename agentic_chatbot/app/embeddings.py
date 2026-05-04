import hashlib
from typing import List, Optional
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class EmbeddingCache:
    """Simple in-memory cache for embeddings"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: dict = {}
        self.max_size = max_size
    
    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding"""
        key = hashlib.md5(text.encode()).hexdigest()
        return self.cache.get(key)
    
    def set(self, text: str, embedding: List[float]):
        """Cache embedding"""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove first item
            self.cache.pop(next(iter(self.cache)))
        
        key = hashlib.md5(text.encode()).hexdigest()
        self.cache[key] = embedding
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()

class EmbeddingService:
    """Service for generating text embeddings using local sentence-transformers"""
    
    def __init__(self, api_key: str = None, model: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service with local model
        
        Args:
            api_key: Unused (for compatibility), OpenRouter doesn't support embeddings
            model: Sentence-transformers model name
        """
        self.model_name = model
        self.cache = EmbeddingCache()
        try:
            self.model = SentenceTransformer(model)
            logger.info(f"✓ Loaded embedding model: {model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """
        Get embedding for text using local sentence-transformers
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None if error
        """
        if not text or not text.strip():
            return None
        
        if not self.model:
            return None
        
        # Check cache first
        cached = self.cache.get(text)
        if cached:
            return cached
        
        try:
            embedding = self.model.encode(text.strip()).tolist()
            
            # Cache the result
            self.cache.set(text, embedding)
            
            return embedding
        
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def get_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Get embeddings for multiple texts (batch)
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            # Check cache first
            cached = self.cache.get(text)
            if cached:
                embeddings.append(cached)
                continue
            
            try:
                emb = self.get_embedding(text)
                embeddings.append(emb)
            except Exception as e:
                logger.error(f"Error in batch embedding: {e}")
                embeddings.append(None)
        
        return embeddings
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        import numpy as np
        
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

# Global embedding service instance
embedding_service: Optional[EmbeddingService] = None

def init_embedding_service(api_key: str = None):
    """Initialize the embedding service with local model"""
    global embedding_service
    embedding_service = EmbeddingService(api_key)
    logger.info("✓ Embedding service initialized (Local: sentence-transformers)")

def get_embedding_service() -> Optional[EmbeddingService]:
    """Get the embedding service instance"""
    return embedding_service
