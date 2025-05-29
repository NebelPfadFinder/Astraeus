"""
Text Processing Utilities
Handles text preprocessing, chunking, and preparation for vector embedding
"""

import re
import logging
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import unicodedata
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import spacy
from sentence_transformers import SentenceTransformer

# Configure logging
logger = logging.getLogger(__name__)


class ChunkingStrategy(Enum):
    """Text chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SENTENCE_BASED = "sentence_based"
    PARAGRAPH_BASED = "paragraph_based"
    SEMANTIC_BASED = "semantic_based"
    HYBRID = "hybrid"


@dataclass
class TextChunk:
    """Represents a text chunk with metadata"""
    content: str
    start_index: int
    end_index: int
    chunk_id: str
    metadata: Dict = None
    embedding: Optional[List[float]] = None


@dataclass
class ProcessingConfig:
    """Configuration for text processing"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    min_chunk_size: int = 100
    max_chunk_size: int = 1000
    chunking_strategy: ChunkingStrategy = ChunkingStrategy.SENTENCE_BASED
    remove_stopwords: bool = False
    lowercase: bool = True
    remove_punctuation: bool = False
    normalize_whitespace: bool = True
    language: str = "english"


class TextPreprocessor:
    """Handles text cleaning and preprocessing"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.stemmer = PorterStemmer()
        self._setup_nltk()
        self._setup_spacy()
    
    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("Downloading required NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
    
    def _setup_spacy(self):
        """Setup spaCy model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. Some features may be limited.")
            self.nlp = None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalize whitespace
        if self.config.normalize_whitespace:
            text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert to lowercase
        if self.config.lowercase:
            text = text.lower()
        
        # Remove excessive punctuation
        if self.config.remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def remove_stopwords_from_text(self, text: str) -> str:
        """Remove stopwords from text"""
        if not self.config.remove_stopwords:
            return text
        
        try:
            stop_words = set(stopwords.words(self.config.language))
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in stop_words]
            return ' '.join(filtered_words)
        except Exception as e:
            logger.warning(f"Error removing stopwords: {e}")
            return text
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            return entities
        except Exception as e:
            logger.warning(f"Error extracting entities: {e}")
            return []
    
    def preprocess(self, text: str) -> str:
        """Apply full preprocessing pipeline"""
        # Clean text
        text = self.clean_text(text)
        
        # Remove stopwords if configured
        text = self.remove_stopwords_from_text(text)
        
        return text


class TextChunker:
    """Handles text chunking with various strategies"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.preprocessor = TextPreprocessor(config)
    
    def chunk_by_fixed_size(self, text: str) -> List[TextChunk]:
        """Chunk text by fixed character size with overlap"""
        chunks = []
        text_length = len(text)
        
        start = 0
        chunk_id = 0
        
        while start < text_length:
            end = min(start + self.config.chunk_size, text_length)
            
            # Adjust end to avoid splitting words
            if end < text_length:
                # Find the last space before the end
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_content = text[start:end].strip()
            
            if len(chunk_content) >= self.config.min_chunk_size:
                chunks.append(TextChunk(
                    content=chunk_content,
                    start_index=start,
                    end_index=end,
                    chunk_id=f"chunk_{chunk_id}",
                    metadata={'strategy': 'fixed_size'}
                ))
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + self.config.chunk_size - self.config.chunk_overlap, end)
        
        return chunks
    
    def chunk_by_sentences(self, text: str) -> List[TextChunk]:
        """Chunk text by sentences"""
        try:
            sentences = sent_tokenize(text)
        except Exception as e:
            logger.warning(f"Error tokenizing sentences: {e}")
            return self.chunk_by_fixed_size(text)
        
        chunks = []
        current_chunk = ""
        chunk_start = 0
        chunk_id = 0
        
        for i, sentence in enumerate(sentences):
            sentence_start = text.find(sentence, chunk_start if not current_chunk else 0)
            
            # Check if adding this sentence would exceed max chunk size
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) > self.config.max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append(TextChunk(
                    content=current_chunk.strip(),
                    start_index=chunk_start,
                    end_index=chunk_start + len(current_chunk),
                    chunk_id=f"chunk_{chunk_id}",
                    metadata={'strategy': 'sentence_based', 'sentence_count': i}
                ))
                chunk_id += 1
                
                # Start new chunk
                current_chunk = sentence
                chunk_start = sentence_start
            else:
                current_chunk = potential_chunk
                if not current_chunk.strip():
                    chunk_start = sentence_start
        
        # Add the last chunk
        if current_chunk.strip() and len(current_chunk.strip()) >= self.config.min_chunk_size:
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                start_index=chunk_start,
                end_index=chunk_start + len(current_chunk),
                chunk_id=f"chunk_{chunk_id}",
                metadata={'strategy': 'sentence_based'}
            ))
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str) -> List[TextChunk]:
        """Chunk text by paragraphs"""
        # Split by double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_pos = 0
        chunk_id = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            paragraph_start = text.find(paragraph, current_pos)
            
            # If paragraph is too large, split it further
            if len(paragraph) > self.config.max_chunk_size:
                sub_chunks = self.chunk_by_sentences(paragraph)
                for sub_chunk in sub_chunks:
                    sub_chunk.start_index += paragraph_start
                    sub_chunk.end_index += paragraph_start
                    sub_chunk.chunk_id = f"chunk_{chunk_id}"
                    sub_chunk.metadata = {'strategy': 'paragraph_based', 'sub_chunk': True}
                    chunks.append(sub_chunk)
                    chunk_id += 1
            elif len(paragraph) >= self.config.min_chunk_size:
                chunks.append(TextChunk(
                    content=paragraph,
                    start_index=paragraph_start,
                    end_index=paragraph_start + len(paragraph),
                    chunk_id=f"chunk_{chunk_id}",
                    metadata={'strategy': 'paragraph_based'}
                ))
                chunk_id += 1
            
            current_pos = paragraph_start + len(paragraph)
        
        return chunks
    
    def chunk_semantically(self, text: str, model_name: str = "all-MiniLM-L6-v2") -> List[TextChunk]:
        """Chunk text based on semantic similarity"""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(model_name)
        except ImportError:
            logger.warning("sentence-transformers not available, falling back to sentence-based chunking")
            return self.chunk_by_sentences(text)
        
        # First, get sentence-based chunks
        sentence_chunks = self.chunk_by_sentences(text)
        
        if len(sentence_chunks) <= 1:
            return sentence_chunks
        
        # Get embeddings for each chunk
        chunk_texts = [chunk.content for chunk in sentence_chunks]
        embeddings = model.encode(chunk_texts)
        
        # Group semantically similar chunks
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        similarity_matrix = cosine_similarity(embeddings)
        
        # Implement semantic clustering (simplified approach)
        chunks = []
        used_indices = set()
        chunk_id = 0
        
        for i, chunk in enumerate(sentence_chunks):
            if i in used_indices:
                continue
            
            # Find similar chunks
            similar_indices = [i]
            for j in range(i + 1, len(sentence_chunks)):
                if j not in used_indices and similarity_matrix[i][j] > 0.7:  # Threshold
                    similar_indices.append(j)
                    used_indices.add(j)
            
            # Combine similar chunks
            combined_content = " ".join([sentence_chunks[idx].content for idx in similar_indices])
            
            if len(combined_content) <= self.config.max_chunk_size:
                chunks.append(TextChunk(
                    content=combined_content,
                    start_index=sentence_chunks[similar_indices[0]].start_index,
                    end_index=sentence_chunks[similar_indices[-1]].end_index,
                    chunk_id=f"chunk_{chunk_id}",
                    metadata={'strategy': 'semantic_based', 'combined_chunks': len(similar_indices)}
                ))
                chunk_id += 1
                used_indices.add(i)
        
        return chunks
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """Chunk text using the configured strategy"""
        if not text or not isinstance(text, str):
            return []
        
        # Preprocess text
        processed_text = self.preprocessor.preprocess(text)
        
        # Apply chunking strategy
        if self.config.chunking_strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self.chunk_by_fixed_size(processed_text)
        elif self.config.chunking_strategy == ChunkingStrategy.SENTENCE_BASED:
            chunks = self.chunk_by_sentences(processed_text)
        elif self.config.chunking_strategy == ChunkingStrategy.PARAGRAPH_BASED:
            chunks = self.chunk_by_paragraphs(processed_text)
        elif self.config.chunking_strategy == ChunkingStrategy.SEMANTIC_BASED:
            chunks = self.chunk_semantically(processed_text)
        elif self.config.chunking_strategy == ChunkingStrategy.HYBRID:
            # Use sentence-based as default for hybrid
            chunks = self.chunk_by_sentences(processed_text)
        else:
            chunks = self.chunk_by_fixed_size(processed_text)
        
        # Filter chunks by size
        filtered_chunks = [
            chunk for chunk in chunks 
            if self.config.min_chunk_size <= len(chunk.content) <= self.config.max_chunk_size
        ]
        
        logger.info(f"Created {len(filtered_chunks)} chunks using {self.config.chunking_strategy.value}")
        return filtered_chunks


class DocumentProcessor:
    """High-level document processing orchestrator"""
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.chunker = TextChunker(self.config)
    
    def process_document(self, 
                        text: str, 
                        document_id: str = None, 
                        metadata: Dict = None) -> List[TextChunk]:
        """Process a complete document into chunks"""
        
        if not text:
            return []
        
        # Chunk the text
        chunks = self.chunker.chunk_text(text)
        
        # Add document-level metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            'document_id': document_id,
            'total_chunks': len(chunks),
            'processing_config': {
                'chunk_size': self.config.chunk_size,
                'chunking_strategy': self.config.chunking_strategy.value
            }
        })
        
        # Update chunk metadata
        for i, chunk in enumerate(chunks):
            if chunk.metadata is None:
                chunk.metadata = {}
            
            chunk.metadata.update({
                'document_id': document_id,
                'chunk_index': i,
                **doc_metadata
            })
            
            # Update chunk ID to include document ID
            if document_id:
                chunk.chunk_id = f"{document_id}_{chunk.chunk_id}"
        
        return chunks
    
    def process_file(self, file_path: Union[str, Path]) -> List[TextChunk]:
        """Process a file into text chunks"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content based on extension
        if file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        elif file_path.suffix.lower() in ['.md', '.markdown']:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        metadata = {
            'source_file': str(file_path),
            'file_size': file_path.stat().st_size,
            'file_type': file_path.suffix
        }
        
        return self.process_document(
            text=text,
            document_id=file_path.stem,
            metadata=metadata
        )


# Utility functions
def create_default_config() -> ProcessingConfig:
    """Create default processing configuration"""
    return ProcessingConfig()


def quick_chunk(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Quick text chunking utility function"""
    config = ProcessingConfig(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        chunking_strategy=ChunkingStrategy.FIXED_SIZE
    )
    
    processor = DocumentProcessor(config)
    chunks = processor.process_document(text)
    
    return [chunk.content for chunk in chunks]


def estimate_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Estimate token count for text (rough approximation)"""
    # Rough estimation: 1 token ≈ 4 characters for English text
    return len(text) // 4


if __name__ == "__main__":
    # Example usage
    sample_text = """
    This is a sample document for testing text processing utilities.
    It contains multiple sentences and paragraphs to demonstrate chunking.
    
    The text processing module handles various strategies for breaking down
    large documents into manageable chunks for vector embedding and retrieval.
    
    Each chunk maintains metadata about its source and processing parameters.
    """
    
    config = ProcessingConfig(
        chunk_size=100,
        chunking_strategy=ChunkingStrategy.SENTENCE_BASED
    )
    
    processor = DocumentProcessor(config)
    chunks = processor.process_document(sample_text, document_id="sample_doc")
    
    print(f"Created {len(chunks)} chunks:")
    for chunk in chunks:
        print(f"- {chunk.chunk_id}: {chunk.content[:50]}...")
        print(f"  Metadata: {chunk.metadata}")
        print()
