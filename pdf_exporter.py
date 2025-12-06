"""
Rättskoll OCR Test - PDF Exporter
==================================
Extracts selected pages from PDF documents and saves as new files.
"""

from io import BytesIO
from pathlib import Path
from datetime import datetime

from pypdf import PdfReader, PdfWriter

from config import OUTPUT_DIR


class PDFExportError(Exception):
    """Custom exception for PDF export errors."""
    pass


class PDFExporter:
    """
    Extracts and exports selected pages from PDF documents.
    """

    def __init__(self, output_dir: Path = OUTPUT_DIR):
        """
        Initialize PDF exporter.

        Args:
            output_dir: Directory to save exported PDFs
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    def extract_pages(
        self,
        pdf_bytes: bytes,
        page_numbers: list[int],
    ) -> bytes:
        """
        Extract selected pages and return as PDF bytes.

        Args:
            pdf_bytes: Source PDF content
            page_numbers: 1-indexed page numbers to extract

        Returns:
            New PDF as bytes containing only selected pages
        """
        try:
            reader = PdfReader(BytesIO(pdf_bytes))
            writer = PdfWriter()

            for page_num in sorted(page_numbers):
                # pypdf uses 0-indexed pages
                idx = page_num - 1
                if 0 <= idx < len(reader.pages):
                    writer.add_page(reader.pages[idx])

            output = BytesIO()
            writer.write(output)
            return output.getvalue()

        except Exception as e:
            raise PDFExportError(f"Failed to extract pages: {e}")

    def save_to_file(
        self,
        pdf_bytes: bytes,
        page_numbers: list[int],
        original_filename: str,
    ) -> Path:
        """
        Extract pages and save to outputs/ directory.

        Args:
            pdf_bytes: Source PDF content
            page_numbers: 1-indexed page numbers to extract
            original_filename: Original PDF filename for naming

        Returns:
            Path to saved file
        """
        extracted = self.extract_pages(pdf_bytes, page_numbers)

        # Generate output filename
        base_name = Path(original_filename).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        page_desc = self._describe_pages(page_numbers)
        output_name = f"{base_name}_{page_desc}_{timestamp}.pdf"

        output_path = self.output_dir / output_name
        output_path.write_bytes(extracted)

        return output_path

    def _describe_pages(self, page_numbers: list[int]) -> str:
        """Create short description of page selection for filename."""
        if not page_numbers:
            return "empty"
        if len(page_numbers) == 1:
            return f"p{page_numbers[0]}"
        elif len(page_numbers) <= 3:
            return f"p{'_'.join(str(p) for p in sorted(page_numbers))}"
        else:
            sorted_pages = sorted(page_numbers)
            return f"p{sorted_pages[0]}-{sorted_pages[-1]}_{len(page_numbers)}pages"
