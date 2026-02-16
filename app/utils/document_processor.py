"""
Document Processing Utilities
Extract text from PDFs and DOCX files
"""
import PyPDF2
from docx import Document
from pathlib import Path
from typing import Optional


class DocumentProcessor:
    """Extract text from various document formats"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())
            
            return "\n\n".join(text)
        
        except Exception as e:
            raise ValueError(f"Failed to extract PDF: {str(e)}")
    
    @staticmethod
    def extract_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            
            return "\n\n".join(text)
        
        except Exception as e:
            raise ValueError(f"Failed to extract DOCX: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Auto-detect format and extract text
        
        Args:
            file_path: Path to document
            
        Returns:
            Extracted text
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return DocumentProcessor.extract_from_pdf(file_path)
        elif extension == '.docx':
            return DocumentProcessor.extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")


# Global instance
document_processor = DocumentProcessor()