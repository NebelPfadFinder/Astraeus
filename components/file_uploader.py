"""
File upload functionality for adding documents to the chatbot knowledge base.
Handles various file formats and provides document processing capabilities.
"""

import streamlit as st
import tempfile
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import PyPDF2
import docx
import pandas as pd
from io import BytesIO
import hashlib
import json
from datetime import datetime

from services.qdrant_service import QdrantService
from utils.text_processing import TextProcessor
from utils.logger import get_logger

logger = get_logger(__name__)

class FileUploader:
    """Handles file uploads and document processing for the chatbot."""
    
    SUPPORTED_FORMATS = {
        'pdf': ['pdf'],
        'text': ['txt', 'md', 'rst'],
        'document': ['docx', 'doc'],
        'spreadsheet': ['xlsx', 'xls', 'csv'],
        'json': ['json'],
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, qdrant_service: QdrantService, text_processor: TextProcessor):
        """Initialize the file uploader with required services."""
        self.qdrant_service = qdrant_service
        self.text_processor = text_processor
        self.uploaded_files_cache = {}
    
    def render_upload_interface(self) -> Optional[List[Dict[str, Any]]]:
        """Render the file upload interface in Streamlit."""
        st.subheader("📁 Document Upload")
        
        with st.expander("Upload Documents to Knowledge Base", expanded=False):
            # File upload widget
            uploaded_files = st.file_uploader(
                "Choose files to upload",
                type=self._get_supported_extensions(),
                accept_multiple_files=True,
                help="Supported formats: PDF, TXT, DOCX, XLSX, CSV, JSON, MD"
            )
            
            if uploaded_files:
                return self._process_uploaded_files(uploaded_files)
        
        return None
    
    def _get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions."""
        extensions = []
        for format_group in self.SUPPORTED_FORMATS.values():
            extensions.extend(format_group)
        return extensions
    
    def _process_uploaded_files(self, uploaded_files) -> List[Dict[str, Any]]:
        """Process and display uploaded files."""
        processed_files = []
        
        # Create columns for file info and actions
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{len(uploaded_files)} file(s) selected:**")
            
            for file in uploaded_files:
                # Check file size
                if file.size > self.MAX_FILE_SIZE:
                    st.error(f"❌ {file.name}: File too large (max {self.MAX_FILE_SIZE // (1024*1024)}MB)")
                    continue
                
                # Generate file hash for deduplication
                file_hash = self._generate_file_hash(file)
                
                # Display file info
                file_info = {
                    'name': file.name,
                    'type': file.type,
                    'size': file.size,
                    'hash': file_hash,
                    'content': None,
                    'chunks': None
                }
                
                with st.container():
                    col_info, col_status = st.columns([3, 1])
                    
                    with col_info:
                        st.write(f"📄 **{file.name}**")
                        st.write(f"Size: {self._format_file_size(file.size)} | Type: {file.type}")
                    
                    with col_status:
                        if file_hash in self.uploaded_files_cache:
                            st.success("✅ Cached")
                        else:
                            st.info("🔄 New")
                
                processed_files.append(file_info)
        
        with col2:
            if st.button("🚀 Process Files", type="primary"):
                return self._extract_and_index_files(processed_files, uploaded_files)
        
        return processed_files
    
    def _generate_file_hash(self, file) -> str:
        """Generate SHA-256 hash for file deduplication."""
        file.seek(0)
        content = file.read()
        file.seek(0)
        return hashlib.sha256(content).hexdigest()
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 ** 2):.1f} MB"
    
    def _extract_and_index_files(self, file_info_list: List[Dict], uploaded_files) -> List[Dict[str, Any]]:
        """Extract content from files and index them in Qdrant."""
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (file_info, uploaded_file) in enumerate(zip(file_info_list, uploaded_files)):
            status_text.text(f"Processing {file_info['name']}...")
            
            try:
                # Extract content based on file type
                content = self._extract_content(uploaded_file)
                file_info['content'] = content
                
                if content:
                    # Process and chunk the content
                    chunks = self.text_processor.chunk_text(
                        content, 
                        chunk_size=512,
                        overlap=50
                    )
                    file_info['chunks'] = chunks
                    
                    # Index in Qdrant
                    self._index_document_chunks(file_info, chunks)
                    
                    # Cache the processed file
                    self.uploaded_files_cache[file_info['hash']] = {
                        'name': file_info['name'],
                        'processed_at': datetime.now().isoformat(),
                        'chunk_count': len(chunks)
                    }
                    
                    results.append({
                        'file': file_info['name'],
                        'status': 'success',
                        'chunks': len(chunks),
                        'message': f"Successfully processed {len(chunks)} chunks"
                    })
                    
                    st.success(f"✅ {file_info['name']}: {len(chunks)} chunks indexed")
                
            except Exception as e:
                logger.error(f"Error processing {file_info['name']}: {str(e)}")
                results.append({
                    'file': file_info['name'],
                    'status': 'error',
                    'message': str(e)
                })
                st.error(f"❌ {file_info['name']}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(file_info_list))
        
        status_text.text("Processing complete!")
        
        # Display summary
        self._display_processing_summary(results)
        
        return results
    
    def _extract_content(self, uploaded_file) -> str:
        """Extract text content from uploaded file based on its type."""
        file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
        
        try:
            if file_extension == 'pdf':
                return self._extract_pdf_content(uploaded_file)
            elif file_extension in ['txt', 'md', 'rst']:
                return self._extract_text_content(uploaded_file)
            elif file_extension in ['docx', 'doc']:
                return self._extract_docx_content(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return self._extract_excel_content(uploaded_file)
            elif file_extension == 'csv':
                return self._extract_csv_content(uploaded_file)
            elif file_extension == 'json':
                return self._extract_json_content(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Content extraction failed for {uploaded_file.name}: {str(e)}")
            raise
    
    def _extract_pdf_content(self, file) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
            content = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    content.append(text)
            
            return '\n\n'.join(content)
        except Exception as e:
            raise ValueError(f"Failed to extract PDF content: {str(e)}")
    
    def _extract_text_content(self, file) -> str:
        """Extract content from text files."""
        try:
            content = file.read().decode('utf-8')
            return content
        except UnicodeDecodeError:
            # Try with different encodings
            file.seek(0)
            try:
                content = file.read().decode('latin-1')
                return content
            except Exception as e:
                raise ValueError(f"Failed to decode text file: {str(e)}")
    
    def _extract_docx_content(self, file) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(BytesIO(file.read()))
            content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    content.append(paragraph.text)
            
            return '\n\n'.join(content)
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX content: {str(e)}")
    
    def _extract_excel_content(self, file) -> str:
        """Extract content from Excel file."""
        try:
            df = pd.read_excel(BytesIO(file.read()))
            return df.to_string(index=False)
        except Exception as e:
            raise ValueError(f"Failed to extract Excel content: {str(e)}")
    
    def _extract_csv_content(self, file) -> str:
        """Extract content from CSV file."""
        try:
            df = pd.read_csv(BytesIO(file.read()))
            return df.to_string(index=False)
        except Exception as e:
            raise ValueError(f"Failed to extract CSV content: {str(e)}")
    
    def _extract_json_content(self, file) -> str:
        """Extract content from JSON file."""
        try:
            data = json.load(BytesIO(file.read()))
            return json.dumps(data, indent=2)
        except Exception as e:
            raise ValueError(f"Failed to extract JSON content: {str(e)}")
    
    def _index_document_chunks(self, file_info: Dict, chunks: List[str]):
        """Index document chunks in Qdrant vector database."""
        try:
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    'source_file': file_info['name'],
                    'file_hash': file_info['hash'],
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'file_type': Path(file_info['name']).suffix,
                    'indexed_at': datetime.now().isoformat()
                }
                
                documents.append({
                    'content': chunk,
                    'metadata': doc_metadata
                })
            
            # Add documents to Qdrant
            self.qdrant_service.add_documents(documents)
            logger.info(f"Successfully indexed {len(chunks)} chunks from {file_info['name']}")
            
        except Exception as e:
            logger.error(f"Failed to index chunks for {file_info['name']}: {str(e)}")
            raise
    
    def _display_processing_summary(self, results: List[Dict]):
        """Display summary of file processing results."""
        if not results:
            return
        
        st.subheader("📊 Processing Summary")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        total_chunks = sum(r.get('chunks', 0) for r in results if r['status'] == 'success')
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("✅ Successful", success_count)
        
        with col2:
            st.metric("❌ Failed", error_count)
        
        with col3:
            st.metric("📝 Total Chunks", total_chunks)
        
        # Detailed results
        with st.expander("Detailed Results"):
            for result in results:
                if result['status'] == 'success':
                    st.success(f"✅ {result['file']}: {result['message']}")
                else:
                    st.error(f"❌ {result['file']}: {result['message']}")
    
    def get_uploaded_files_info(self) -> Dict:
        """Get information about uploaded files from cache."""
        return self.uploaded_files_cache
    
    def clear_cache(self):
        """Clear the uploaded files cache."""
        self.uploaded_files_cache.clear()
        st.success("Cache cleared successfully!")


def render_file_management_sidebar():
    """Render file management options in sidebar."""
    st.sidebar.subheader("📁 File Management")
    
    if st.sidebar.button("🗑️ Clear Upload Cache"):
        # This would typically clear the cache
        st.sidebar.success("Cache cleared!")
    
    if st.sidebar.button("📊 View Indexed Documents"):
        # This would show indexed documents
        st.sidebar.info("Feature coming soon!")
    
    # File upload statistics
    st.sidebar.subheader("📈 Upload Statistics")
    st.sidebar.metric("Documents Indexed", 0)  # This would come from actual data
    st.sidebar.metric("Total Chunks", 0)  # This would come from actual data
