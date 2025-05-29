import asyncio
import aiohttp
import json
import hashlib
from typing import List, Dict, Any, Optional
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)

class QdrantService:
    """Service class for interacting with Qdrant vector database."""
    
    def __init__(
        self, 
        url: str = "http://localhost:6333", 
        api_key: Optional[str] = None,
        collection_name: str = "chatbot_knowledge",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize Qdrant service.
        
        Args:
            url: Qdrant server URL
            api_key: Optional API key for authentication
            collection_name: Name of the collection to use
            embedding_model: Sentence transformer model for embeddings
        """
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.collection_name = collection_name
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Setup headers
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["api-key"] = api_key
    
    async def initialize_collection(self, vector_size: int = 384):
        """
        Initialize the Qdrant collection if it doesn't exist.
        
        Args:
            vector_size: Size of the embedding vectors (384 for all-MiniLM-L6-v2)
        """
        try:
            # Check if collection exists
            collection_exists = await self._collection_exists()
            
            if not collection_exists:
                # Create collection
                collection_config = {
                    "vectors": {
                        "size": vector_size,
                        "distance": "Cosine"
                    },
                    "optimizers_config": {
                        "default_segment_number": 2
                    },
                    "replication_factor": 1
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.put(
                        f"{self.url}/collections/{self.collection_name}",
                        headers=self.headers,
                        json=collection_config,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status in [200, 201]:
                            logger.info(f"Created collection: {self.collection_name}")
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to create collection: {response.status} - {error_text}")
                            return False
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                return True
                
        except Exception as e:
            logger.error(f"Error initializing collection: {str(e)}")
            return False
    
    async def _collection_exists(self) -> bool:
        """Check if the collection exists."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/collections/{self.collection_name}",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents with 'text' and optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure collection exists
            await self.initialize_collection()
            
            points = []
            for i, doc in enumerate(documents):
                text = doc.get('text', '')
                if not text:
                    continue
                
                # Generate embedding
                embedding = self.embedding_model.encode(text).tolist()
                
                # Create unique ID based on content hash
                doc_id = hashlib.sha256(text.encode()).hexdigest()[:16]
                
                # Prepare point data
                point = {
                    "id": doc_id,
                    "vector": embedding,
                    "payload": {
                        "text": text,
                        "timestamp": doc.get('timestamp'),
                        "source": doc.get('source', 'unknown'),
                        "metadata": doc.get('metadata', {})
                    }
                }
                points.append(point)
            
            if not points:
                logger.warning("No valid documents to add")
                return False
            
            # Upload points to Qdrant
            upload_data = {
                "points": points
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.url}/collections/{self.collection_name}/points",
                    headers=self.headers,
                    json=upload_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status in [200, 201]:
                        logger.info(f"Successfully added {len(points)} documents")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to add documents: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    async def search_similar(
        self, 
        query: str, 
        limit: int = 5, 
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search.
        
        Args:
            query: Search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of similar documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare search request
            search_data = {
                "vector": query_embedding,
                "limit": limit,
                "score_threshold": score_threshold,
                "with_payload": True,
                "with_vector": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.url}/collections/{self.collection_name}/points/search",
                    headers=self.headers,
                    json=search_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Process search results
                        documents = []
                        for hit in result.get("result", []):
                            doc = {
                                "text": hit["payload"]["text"],
                                "score": hit["score"],
                                "source": hit["payload"].get("source", "unknown"),
                                "metadata": hit["payload"].get("metadata", {}),
                                "id": hit["id"]
                            }
                            documents.append(doc)
                        
                        logger.info(f"Found {len(documents)} similar documents for query: '{query[:50]}...'")
                        return documents
                    else:
                        error_text = await response.text()
                        logger.error(f"Search failed: {response.status} - {error_text}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error searching similar documents: {str(e)}")
            return []
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Collection information dictionary
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/collections/{self.collection_name}",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {}
                        
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {}
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the collection.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            delete_data = {
                "points": [doc_id]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.url}/collections/{self.collection_name}/points/delete",
                    headers=self.headers,
                    json=delete_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        logger.info(f"Deleted document: {doc_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to delete document: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """
        Check if Qdrant is accessible.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.url}/collections",
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False
    
    def get_embedding_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model.
        
        Returns:
            Model information dictionary
        """
        return {
            "model_name": self.embedding_model._modules['0'].auto_model.config.name_or_path,
            "max_seq_length": self.embedding_model.get_max_seq_length(),
            "embedding_dimension": self.embedding_model.get_sentence_embedding_dimension()
        }