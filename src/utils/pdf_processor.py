import PyPDF2
from typing import Optional

class PDFProcessor:
    """Handles PDF file processing and text extraction"""
    
    def __init__(self):
        """Initialize PDF processor"""
        pass
        
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            str: Extracted text content
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PyPDF2.PdfReadError: If PDF file is invalid or corrupted
        """
        try:
            with open(pdf_path, 'rb') as file:
                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
                
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        except PyPDF2.PdfReadError as e:
            raise PyPDF2.PdfReadError(f"Error reading PDF file: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error processing PDF: {str(e)}")
            
    def get_metadata(self, pdf_path: str) -> dict:
        """
        Extract metadata from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            dict: PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return reader.metadata
        except Exception as e:
            return {"error": str(e)} 