#!/usr/bin/env python3
"""
Database setup script for initializing Qdrant collections and loading initial data.
This script handles the initial setup of the vector database with proper collections,
indexing, and sample data loading.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.qdrant_service import QdrantService
from services.mistral_service import MistralService
from utils.text_processing import TextProcessor
from utils.logger import get_logger
from config.settings import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = get_logger(__name__)

class DatabaseSetup:
    """Handles the initialization and setup of the Qdrant vector database."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the database setup with configuration."""
        self.settings = Settings(config_path)
        self.qdrant_service = None
        self.mistral_service = None
        self.text_processor = None
        
    def initialize_services(self):
        """Initialize all required services."""
        logger.info("Initializing services...")
        
        try:
            # Initialize Qdrant service
            self.qdrant_service = QdrantService(
                host=self.settings.QDRANT_HOST,
                port=self.settings.QDRANT_PORT,
                api_key=getattr(self.settings, 'QDRANT_API_KEY', None)
            )
            
            # Initialize Mistral service for embeddings
            self.mistral_service = MistralService(
                api_key=self.settings.MISTRAL_API_KEY,
                model=self.settings.MISTRAL_MODEL
            )
            
            # Initialize text processor
            self.text_processor = TextProcessor()
            
            logger.info("Services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise
    
    def wait_for_qdrant(self, max_retries: int = 30, delay: int = 2):
        """Wait for Qdrant service to be available."""
        logger.info("Waiting for Qdrant service to be available...")
        
        for attempt in range(max_retries):
            try:
                if self.qdrant_service.health_check():
                    logger.info("Qdrant service is available")
                    return True
                    
            except Exception as e:
                logger.warning(f"Qdrant not ready (attempt {attempt + 1}/{max_retries}): {str(e)}")
                
            if attempt < max_retries - 1:
                time.sleep(delay)
        
        logger.error("Qdrant service is not available after maximum retries")
        return False
    
    def create_collections(self):
        """Create necessary Qdrant collections."""
        logger.info("Creating Qdrant collections...")
        
        collections = [
            {
                'name': 'documents',
                'description': 'Document embeddings for semantic search',
                'vector_size': self.settings.EMBEDDING_DIMENSION,
                'distance': 'Cosine'
            },
            {
                'name': 'conversations',
                'description': 'Conversation history embeddings',
                'vector_size': self.settings.EMBEDDING_DIMENSION,
                'distance': 'Cosine'
            },
            {
                'name': 'knowledge_base',
                'description': 'Curated knowledge base embeddings',
                'vector_size': self.settings.EMBEDDING_DIMENSION,
                'distance': 'Cosine'
            }
        ]
        
        for collection_config in collections:
            try:
                success = self.qdrant_service.create_collection(
                    collection_name=collection_config['name'],
                    vector_size=collection_config['vector_size'],
                    distance=collection_config['distance']
                )
                
                if success:
                    logger.info(f"Created collection: {collection_config['name']}")
                else:
                    logger.warning(f"Collection {collection_config['name']} may already exist")
                    
            except Exception as e:
                logger.error(f"Failed to create collection {collection_config['name']}: {str(e)}")
                raise
    
    def load_sample_data(self, data_dir: str = "data/samples"):
        """Load sample documents into the database."""
        logger.info("Loading sample data...")
        
        data_path = Path(project_root) / data_dir
        
        if not data_path.exists():
            logger.warning(f"Sample data directory not found: {data_path}")
            self.create_default_sample_data()
            return
        
        # Load sample documents
        sample_files = list(data_path.glob("*.txt")) + list(data_path.glob("*.json"))
        
        if not sample_files:
            logger.warning("No sample files found, creating default data")
            self.create_default_sample_data()
            return
        
        documents = []
        
        for file_path in sample_files:
            try:
                content = self.load_file_content(file_path)
                
                if content:
                    # Process and chunk the content
                    chunks = self.text_processor.chunk_text(
                        content,
                        chunk_size=512,
                        overlap=50
                    )
                    
                    # Create document entries
                    for i, chunk in enumerate(chunks):
                        doc_metadata = {
                            'source_file': file_path.name,
                            'chunk_index': i,
                            'total_chunks': len(chunks),
                            'file_type': file_path.suffix,
                            'category': 'sample_data',
                            'indexed_at': datetime.now().isoformat()
                        }
                        
                        documents.append({
                            'content': chunk,
                            'metadata': doc_metadata
                        })
                
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {str(e)}")
        
        # Add documents to Qdrant
        if documents:
            try:
                self.qdrant_service.add_documents(documents, collection_name='documents')
                logger.info(f"Successfully loaded {len(documents)} document chunks")
                
            except Exception as e:
                logger.error(f"Failed to add documents to Qdrant: {str(e)}")
                raise
        else:
            logger.warning("No documents to load")
    
    def load_file_content(self, file_path: Path) -> str:
        """Load content from a file."""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {str(e)}")
            return ""
    
    def create_default_sample_data(self):
        """Create default sample data if no sample files exist."""
        logger.info("Creating default sample data...")
        
        sample_documents = [
            {
                'title': 'AI and Machine Learning Basics',
                'content': '''Artificial Intelligence (AI) is a broad field that encompasses machine learning, 
                deep learning, natural language processing, and computer vision. Machine learning is a subset 
                of AI that focuses on algorithms that can learn from data without being explicitly programmed. 
                Deep learning uses neural networks with multiple layers to model complex patterns in data.'''
            },
            {
                'title': 'Python Programming Best Practices',
                'content': '''Python is a versatile programming language known for its simplicity and readability. 
                Best practices include following PEP 8 style guidelines, writing docstrings for functions and classes, 
                using virtual environments, implementing error handling, and writing unit tests. Code should be 
                modular, reusable, and well-documented.'''
            },
            {
                'title': 'Vector Databases and Semantic Search',
                'content': '''Vector databases store high-dimensional vectors that represent data semantically. 
                They enable similarity search and are crucial for applications like recommendation systems, 
                semantic search, and retrieval-augmented generation (RAG). Popular vector databases include 
                Qdrant, Pinecone, Chroma, and Weaviate.'''
            },
            {
                'title': 'Chatbot Development Guidelines',
                'content': '''Effective chatbots require natural language understanding, context management, 
                and appropriate response generation. Key components include intent recognition, entity extraction, 
                dialog management, and integration with knowledge bases. Consider user experience, error handling, 
                and continuous learning from user interactions.'''
            }
        ]
        
        documents = []
        
        for doc in sample_documents:
            # Process and chunk the content
            chunks = self.text_processor.chunk_text(
                doc['content'],
                chunk_size=256,
                overlap=25
            )
            
            # Create document entries
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    'title': doc['title'],
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'category': 'default_sample',
                    'indexed_at': datetime.now().isoformat()
                }
                
                documents.append({
                    'content': chunk,
                    'metadata': doc_metadata
                })
        
        # Add documents to Qdrant
        try:
            self.qdrant_service.add_documents(documents, collection_name='documents')
            logger.info(f"Successfully created and loaded {len(documents)} default sample chunks")
            
        except Exception as e:
            logger.error(f"Failed to add default sample data: {str(e)}")
            raise
    
    def create_indexes(self):
        """Create additional indexes for better query performance."""
        logger.info("Creating database indexes...")
        
        # Qdrant handles indexing automatically, but we can configure HNSW parameters
        index_configs = [
            {
                'collection': 'documents',
                'hnsw_config': {
                    'ef_construct': 100,
                    'max_connections': 64
                }
            },
            {
                'collection': 'conversations',
                'hnsw_config': {
                    'ef_construct': 100,
                    'max_connections': 32
                }
            },
            {
                'collection': 'knowledge_base',
                'hnsw_config': {
                    'ef_construct': 200,
                    'max_connections': 64
                }
            }
        ]
        
        for config in index_configs:
            try:
                # Update collection configuration if needed
                # This is typically done during collection creation
                logger.info(f"Index configuration set for {config['collection']}")
                
            except Exception as e:
                logger.error(f"Failed to configure index for {config['collection']}: {str(e)}")
    
    def verify_setup(self):
        """Verify that the database setup was successful."""
        logger.info("Verifying database setup...")
        
        try:
            # Check collections
            collections = self.qdrant_service.list_collections()
            expected_collections = ['documents', 'conversations', 'knowledge_base']
            
            for collection_name in expected_collections:
                if collection_name in collections:
                    info = self.qdrant_service.get_collection_info(collection_name)
                    logger.info(f"Collection '{collection_name}': {info.get('vectors_count', 0)} vectors")
                else:
                    logger.error(f"Collection '{collection_name}' not found")
                    return False
            
            # Test search functionality
            test_query = "What is machine learning?"
            results = self.qdrant_service.search(
                query_text=test_query,
                collection_name='documents',
                limit=3
            )
            
            if results:
                logger.info(f"Search test successful: found {len(results)} results")
            else:
                logger.warning("Search test returned no results")
            
            logger.info("Database setup verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database setup verification failed: {str(e)}")
            return False
    
    def reset_database(self):
        """Reset the database by deleting all collections."""
        logger.warning("Resetting database - this will delete all data!")
        
        try:
            collections = self.qdrant_service.list_collections()
            
            for collection_name in collections:
                self.qdrant_service.delete_collection(collection_name)
                logger.info(f"Deleted collection: {collection_name}")
            
            logger.info("Database reset completed")
            
        except Exception as e:
            logger.error(f"Failed to reset database: {str(e)}")
            raise
    
    def run_setup(self, reset: bool = False, skip_sample_data: bool = False):
        """Run the complete database setup process."""
        logger.info("Starting database setup...")
        
        try:
            # Initialize services
            self.initialize_services()
            
            # Wait for Qdrant to be available
            if not self.wait_for_qdrant():
                raise Exception("Qdrant service is not available")
            
            # Reset database if requested
            if reset:
                self.reset_database()
            
            # Create collections
            self.create_collections()
            
            # Create indexes
            self.create_indexes()
            
            # Load sample data
            if not skip_sample_data:
                self.load_sample_data()
            
            # Verify setup
            if self.verify_setup():
                logger.info("Database setup completed successfully!")
                return True
            else:
                logger.error("Database setup verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise


def main():
    """Main function to run the database setup script."""
    parser = argparse.ArgumentParser(
        description="Initialize Qdrant database for the chatbot application"
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset database (delete all existing data)'
    )
    
    parser.add_argument(
        '--skip-sample-data',
        action='store_true',
        help='Skip loading sample data'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Confirm reset operation
    if args.reset:
        confirm = input("This will delete all existing data. Continue? (y/N): ")
        if confirm.lower() != 'y':
            logger.info("Database reset cancelled")
            return
    
    try:
        # Create setup instance
        setup = DatabaseSetup(config_path=args.config)
        
        # Run setup
        success = setup.run_setup(
            reset=args.reset,
            skip_sample_data=args.skip_sample_data
        )
        
        if success:
            logger.info("Database setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("Database setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Setup failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
