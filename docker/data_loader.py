#!/usr/bin/env python3
"""
Data Loader Utility for AI Chatbot

This module provides functionality to load, process, and index documents
into the Qdrant vector database for semantic search capabilities.

Author: AI Chatbot System
Date: 2024
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from services.qdrant_service import QdrantService
from services.mistral_service import MistralService
from utils.text_processing import TextProcessor
from utils.logger import setup_logger
from config.settings import Settings

logger = setup_logger(__name__)


class DocumentLoader:
    """Handles loading and processing of various document types."""
    
    def __init__(self):
        self.text_processor = TextProcessor()
        self.supported_extensions = {'.txt', '.md', '.pdf', '.docx', '.json'}
    
    def load_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a single document from file path.
        
        Args:
            file_path (Path): Path to the document file
            
        Returns:
            Optional[Dict[str, Any]]: Document metadata and content
        """
        try:
            if file_path.suffix.lower() not in self.supported_extensions:
                logger.warning(f"Unsupported file type: {file_path.suffix}")
                return None
            
            # Extract text content based on file type
            content = self._extract_text(file_path)
            if not content or len(content.strip()) < 10:
                logger.warning(f"Document too short or empty: {file_path}")
                return None
            
            # Generate document metadata
            doc_id = self._generate_doc_id(file_path, content)
            
            document = {
                'id': doc_id,
                'content': content,
                'filename': file_path.name,
                'filepath': str(file_path),
                'extension': file_path.suffix,
                'size': file_path.stat().st_size,
                'modified': file_path.stat().st_mtime,
                'chunks': [],
                'metadata': {
                    'source': 'file_upload',
                    'processed_at': asyncio.get_event_loop().time(),
                    'word_count': len(content.split()),
                    'char_count': len(content)
                }
            }
            
            logger.info(f"Loaded document: {file_path.name} ({len(content)} chars)")
            return document
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            return None
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract text content from various file formats."""
        try:
            if file_path.suffix.lower() == '.txt':
                return file_path.read_text(encoding='utf-8')
            
            elif file_path.suffix.lower() == '.md':
                return file_path.read_text(encoding='utf-8')
            
            elif file_path.suffix.lower() == '.json':
                data = json.loads(file_path.read_text(encoding='utf-8'))
                return json.dumps(data, indent=2) if isinstance(data, dict) else str(data)
            
            elif file_path.suffix.lower() == '.pdf':
                return self._extract_pdf_text(file_path)
            
            elif file_path.suffix.lower() == '.docx':
                return self._extract_docx_text(file_path)
            
            else:
                # Fallback: try to read as text
                return file_path.read_text(encoding='utf-8', errors='ignore')
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF files."""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX files."""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            return ""
    
    def _generate_doc_id(self, file_path: Path, content: str) -> str:
        """Generate unique document ID based on path and content."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        path_hash = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        return f"doc_{path_hash}_{content_hash}"


class DataIndexer:
    """Handles indexing of documents into Qdrant vector database."""
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        self.mistral_service = MistralService()
        self.text_processor = TextProcessor()
        self.batch_size = 10
    
    async def index_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Index a list of documents into Qdrant.
        
        Args:
            documents (List[Dict[str, Any]]): List of document objects
            
        Returns:
            Dict[str, Any]: Indexing results and statistics
        """
        if not documents:
            return {'success': False, 'message': 'No documents to index'}
        
        logger.info(f"Starting indexing of {len(documents)} documents")
        
        results = {
            'total_documents': len(documents),
            'successful': 0,
            'failed': 0,
            'total_chunks': 0,
            'errors': []
        }
        
        try:
            # Initialize Qdrant collection if needed
            await self.qdrant_service.initialize_collection()
            
            # Process documents in batches
            for i in range(0, len(documents), self.batch_size):
                batch = documents[i:i + self.batch_size]
                batch_results = await self._process_document_batch(batch)
                
                results['successful'] += batch_results['successful']
                results['failed'] += batch_results['failed']
                results['total_chunks'] += batch_results['chunks']
                results['errors'].extend(batch_results['errors'])
                
                logger.info(f"Processed batch {i//self.batch_size + 1}: "
                          f"{batch_results['successful']}/{len(batch)} documents")
            
            logger.info(f"Indexing completed: {results['successful']}/{results['total_documents']} "
                       f"documents, {results['total_chunks']} chunks")
            
            results['success'] = True
            return results
            
        except Exception as e:
            logger.error(f"Error during indexing: {str(e)}")
            results['success'] = False
            results['errors'].append(str(e))
            return results
    
    async def _process_document_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a batch of documents for indexing."""
        batch_results = {
            'successful': 0,
            'failed': 0,
            'chunks': 0,
            'errors': []
        }
        
        # Process documents concurrently
        tasks = [self._process_single_document(doc) for doc in documents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                batch_results['failed'] += 1
                batch_results['errors'].append(f"Document {documents[i]['filename']}: {str(result)}")
            elif result:
                batch_results['successful'] += 1
                batch_results['chunks'] += result['chunk_count']
            else:
                batch_results['failed'] += 1
        
        return batch_results
    
    async def _process_single_document(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single document for indexing."""
        try:
            # Chunk the document
            chunks = self.text_processor.chunk_text(
                document['content'],
                chunk_size=800,
                overlap=100
            )
            
            if not chunks:
                logger.warning(f"No chunks generated for document {document['filename']}")
                return None
            
            # Generate embeddings for chunks
            chunk_data = []
            for i, chunk in enumerate(chunks):
                try:
                    embedding = await self.mistral_service.get_embeddings(chunk)
                    if embedding:
                        chunk_data.append({
                            'id': f"{document['id']}_chunk_{i}",
                            'vector': embedding,
                            'payload': {
                                'document_id': document['id'],
                                'chunk_index': i,
                                'content': chunk,
                                'filename': document['filename'],
                                'filepath': document['filepath'],
                                'metadata': document['metadata']
                            }
                        })
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {i}: {str(e)}")
                    continue
            
            if not chunk_data:
                logger.warning(f"No valid embeddings generated for document {document['filename']}")
                return None
            
            # Index chunks in Qdrant
            success = await self.qdrant_service.add_documents(chunk_data)
            
            if success:
                logger.info(f"Successfully indexed {len(chunk_data)} chunks for {document['filename']}")
                return {'chunk_count': len(chunk_data)}
            else:
                logger.error(f"Failed to index document {document['filename']}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing document {document['filename']}: {str(e)}")
            raise


async def load_from_directory(directory_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """
    Load all supported documents from a directory.
    
    Args:
        directory_path (str): Path to directory containing documents
        recursive (bool): Whether to search subdirectories
        
    Returns:
        List[Dict[str, Any]]: List of loaded documents
    """
    loader = DocumentLoader()
    documents = []
    
    directory = Path(directory_path)
    if not directory.exists():
        logger.error(f"Directory does not exist: {directory_path}")
        return documents
    
    # Get all files in directory
    pattern = "**/*" if recursive else "*"
    files = [f for f in directory.glob(pattern) if f.is_file()]
    
    logger.info(f"Found {len(files)} files in {directory_path}")
    
    # Process files with thread pool for I/O operations
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [executor.submit(loader.load_document, file_path) for file_path in files]
        
        for task in tasks:
            try:
                document = task.result()
                if document:
                    documents.append(document)
            except Exception as e:
                logger.error(f"Error loading document: {str(e)}")
    
    logger.info(f"Successfully loaded {len(documents)} documents")
    return documents


async def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Load and index documents into Qdrant")
    parser.add_argument(
        "--path", 
        required=True, 
        help="Path to directory containing documents"
    )
    parser.add_argument(
        "--recursive", 
        action="store_true", 
        help="Search subdirectories recursively"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=10, 
        help="Batch size for processing documents"
    )
    parser.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset collection before indexing"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be processed without indexing"
    )
    
    args = parser.parse_args()
    
    try:
        # Load documents from directory
        documents = await load_from_directory(args.path, args.recursive)
        
        if not documents:
            logger.warning("No documents found to process")
            return
        
        if args.dry_run:
            logger.info("DRY RUN - Documents that would be processed:")
            for doc in documents:
                logger.info(f"  - {doc['filename']} ({doc['metadata']['word_count']} words)")
            return
        
        # Initialize indexer
        indexer = DataIndexer()
        indexer.batch_size = args.batch_size
        
        # Reset collection if requested
        if args.reset:
            logger.info("Resetting Qdrant collection...")
            await indexer.qdrant_service.reset_collection()
        
        # Index documents
        results = await indexer.index_documents(documents)
        
        # Print results
        if results['success']:
            logger.info("=" * 50)
            logger.info("INDEXING COMPLETED SUCCESSFULLY")
            logger.info(f"Total documents processed: {results['total_documents']}")
            logger.info(f"Successfully indexed: {results['successful']}")
            logger.info(f"Failed: {results['failed']}")
            logger.info(f"Total chunks created: {results['total_chunks']}")
            logger.info("=" * 50)
        else:
            logger.error("INDEXING FAILED")
            for error in results['errors']:
                logger.error(f"  - {error}")
    
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
