"""
Rättskoll OCR Test - PDF Processor
===================================
Converts PDF documents to images for OCR processing.
"""

import tempfile
from pathlib import Path
from typing import BinaryIO
from PIL import Image

from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError

from config import PDF_DPI, IMAGE_FORMAT


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""
    pass


class PDFProcessor:
    """
    Converts PDF documents to PIL Images for OCR.
    
    Handles both file paths and file-like objects (for Streamlit uploads).
    """
    
    def __init__(self, dpi: int = PDF_DPI):
        """
        Initialize PDF processor.
        
        Args:
            dpi: Resolution for image conversion. Higher = better quality but slower.
                 200 is recommended balance, 300 for difficult scans.
        """
        self.dpi = dpi
    
    def from_path(self, pdf_path: str | Path) -> list[Image.Image]:
        """
        Convert PDF file to list of PIL Images.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PIL Image objects, one per page
            
        Raises:
            PDFProcessingError: If PDF cannot be processed
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise PDFProcessingError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.suffix.lower() == ".pdf":
            raise PDFProcessingError(f"File is not a PDF: {pdf_path}")
        
        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt=IMAGE_FORMAT.lower()
            )
            return images
            
        except PDFInfoNotInstalledError:
            raise PDFProcessingError(
                "Poppler not installed. Install with:\n"
                "  Mac: brew install poppler\n"
                "  Ubuntu: apt-get install poppler-utils\n"
                "  Windows: Download from poppler releases"
            )
        except PDFPageCountError as e:
            raise PDFProcessingError(f"Could not read PDF pages: {e}")
        except Exception as e:
            raise PDFProcessingError(f"Failed to process PDF: {e}")
    
    def from_bytes(self, pdf_bytes: bytes) -> list[Image.Image]:
        """
        Convert PDF bytes to list of PIL Images.
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            List of PIL Image objects, one per page
            
        Raises:
            PDFProcessingError: If PDF cannot be processed
        """
        try:
            images = convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt=IMAGE_FORMAT.lower()
            )
            return images
            
        except PDFInfoNotInstalledError:
            raise PDFProcessingError(
                "Poppler not installed. Install with:\n"
                "  Mac: brew install poppler\n"
                "  Ubuntu: apt-get install poppler-utils\n"
                "  Windows: Download from poppler releases"
            )
        except PDFPageCountError as e:
            raise PDFProcessingError(f"Could not read PDF pages: {e}")
        except Exception as e:
            raise PDFProcessingError(f"Failed to process PDF: {e}")
    
    def from_upload(self, uploaded_file: BinaryIO) -> list[Image.Image]:
        """
        Convert Streamlit UploadedFile to list of PIL Images.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            List of PIL Image objects, one per page
        """
        pdf_bytes = uploaded_file.read()
        # Reset file pointer for potential re-reads
        uploaded_file.seek(0)
        return self.from_bytes(pdf_bytes)
    
    def get_page_count(self, pdf_path: str | Path) -> int:
        """
        Get number of pages in PDF without full conversion.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        from pdf2image.pdf2image import pdfinfo_from_path
        
        try:
            info = pdfinfo_from_path(str(pdf_path))
            return info.get("Pages", 0)
        except Exception:
            # Fallback: do full conversion and count
            images = self.from_path(pdf_path)
            return len(images)
    
    def get_page_count_from_bytes(self, pdf_bytes: bytes) -> int:
        """
        Get number of pages from PDF bytes without full conversion.

        Args:
            pdf_bytes: PDF file as bytes

        Returns:
            Number of pages
        """
        # Try pypdf first (faster, no temp file needed)
        try:
            from io import BytesIO
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(pdf_bytes))
            return len(reader.pages)
        except Exception:
            # Fallback to pdf2image temp file method
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=True) as tmp:
                tmp.write(pdf_bytes)
                tmp.flush()
                return self.get_page_count(tmp.name)

    def generate_thumbnails(
        self,
        pdf_bytes: bytes,
        page_numbers: list[int],
        thumbnail_dpi: int = 50
    ) -> dict[int, Image.Image]:
        """
        Generate low-resolution thumbnails for specific pages.

        Args:
            pdf_bytes: PDF file content
            page_numbers: 1-indexed page numbers to generate thumbnails for
            thumbnail_dpi: Low DPI for speed (50 recommended)

        Returns:
            Dict mapping page_number -> PIL Image thumbnail
        """
        thumbnails = {}

        for page_num in page_numbers:
            try:
                # pdf2image uses 1-indexed pages with first_page/last_page
                images = convert_from_bytes(
                    pdf_bytes,
                    dpi=thumbnail_dpi,
                    fmt=IMAGE_FORMAT.lower(),
                    first_page=page_num,
                    last_page=page_num
                )
                if images:
                    thumbnails[page_num] = images[0]
            except Exception:
                # Skip failed pages
                continue

        return thumbnails

    def from_bytes_selected(
        self,
        pdf_bytes: bytes,
        page_numbers: list[int]
    ) -> list[tuple[int, Image.Image]]:
        """
        Convert only selected pages to images.

        Args:
            pdf_bytes: PDF file content
            page_numbers: 1-indexed page numbers to convert

        Returns:
            List of (page_number, PIL Image) tuples preserving original page numbers
        """
        result = []

        for page_num in sorted(page_numbers):
            try:
                images = convert_from_bytes(
                    pdf_bytes,
                    dpi=self.dpi,
                    fmt=IMAGE_FORMAT.lower(),
                    first_page=page_num,
                    last_page=page_num
                )
                if images:
                    result.append((page_num, images[0]))
            except Exception as e:
                # Create placeholder for failed conversions
                raise PDFProcessingError(f"Failed to convert page {page_num}: {e}")

        return result


def pdf_to_images(
    source: str | Path | bytes | BinaryIO,
    dpi: int = PDF_DPI
) -> list[Image.Image]:
    """
    Convenience function to convert PDF to images.
    
    Automatically detects input type and processes accordingly.
    
    Args:
        source: PDF path, bytes, or file-like object
        dpi: Resolution for conversion
        
    Returns:
        List of PIL Image objects
    """
    processor = PDFProcessor(dpi=dpi)
    
    if isinstance(source, (str, Path)):
        return processor.from_path(source)
    elif isinstance(source, bytes):
        return processor.from_bytes(source)
    else:
        # Assume file-like object
        return processor.from_upload(source)


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_processor.py <pdf_path>")
        print("Example: python pdf_processor.py test_docs/sample.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    print(f"Processing: {pdf_path}")
    
    try:
        processor = PDFProcessor()
        images = processor.from_path(pdf_path)
        print(f"✅ Successfully converted {len(images)} pages")
        
        for i, img in enumerate(images, 1):
            print(f"   Page {i}: {img.size[0]}x{img.size[1]} pixels")
            
    except PDFProcessingError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
