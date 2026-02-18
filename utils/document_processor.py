"""PDF document processing utilities."""

import pdfplumber
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re
import config


class DocumentProcessor:
    """Process PDF factsheets and create chunks with metadata."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
        return text
    
    def extract_metadata(self, text: str, filename: str) -> Dict[str, str]:
        """Extract metadata from factsheet text."""
        metadata = {
            "source": filename,
            "fund_name": "HDFC Index Fund",
            "month": self._extract_month(filename),
            "year": self._extract_year(filename)
        }
        
        # Try to extract fund manager
        fund_manager_match = re.search(r"Fund Manager[:\s]+([A-Za-z\s]+)", text)
        if fund_manager_match:
            metadata["fund_manager"] = fund_manager_match.group(1).strip()
        
        # Try to extract NAV
        nav_match = re.search(r"NAV[:\s]+[₹Rs.]*\s*([0-9,.]+)", text)
        if nav_match:
            metadata["nav"] = nav_match.group(1).strip()
        
        return metadata
    
    def _extract_month(self, filename: str) -> str:
        """Extract month from filename."""
        months = ["january", "february", "march", "april", "may", "june",
                 "july", "august", "september", "october", "november", "december"]
        filename_lower = filename.lower()
        
        for month in months:
            if month in filename_lower:
                return month.capitalize()
        
        # Try short forms
        month_abbr = {
            "jan": "January", "feb": "February", "mar": "March", "apr": "April",
            "may": "May", "jun": "June", "jul": "July", "aug": "August",
            "sep": "September", "oct": "October", "nov": "November", "dec": "December"
        }
        for abbr, full in month_abbr.items():
            if abbr in filename_lower:
                return full
        
        return "Unknown"
    
    def _extract_year(self, filename: str) -> str:
        """Extract year from filename."""
        year_match = re.search(r"20\d{2}", filename)
        if year_match:
            return year_match.group(0)
        return "2025"  # Default year
    
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Process a PDF and return chunked documents with metadata."""
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"No text extracted from {pdf_path}")
            return []
        
        # Extract metadata
        filename = pdf_path.split("/")[-1]
        metadata = self.extract_metadata(text, filename)
        
        # Create chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata["chunk_id"] = i
            doc_metadata["total_chunks"] = len(chunks)
            
            documents.append(Document(
                page_content=chunk,
                metadata=doc_metadata
            ))
        
        print(f"Processed {pdf_path}: {len(documents)} chunks created")
        return documents
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Document]:
        """Process multiple PDFs and return all documents."""
        all_documents = []
        for pdf_path in pdf_paths:
            documents = self.process_pdf(pdf_path)
            all_documents.extend(documents)
        
        print(f"Total documents created: {len(all_documents)}")
        return all_documents