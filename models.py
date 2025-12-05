"""
Rättskoll OCR Test - Data Models
=================================
Pydantic models for structured OCR data with full type safety.
"""

from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional


class OCRPage(BaseModel):
    """
    Single page OCR result with provenance tracking.
    
    Page numbers are 1-indexed to match PDF page numbering.
    """
    
    page_number: int = Field(
        ..., 
        ge=1, 
        description="1-indexed page number matching PDF"
    )
    text: str = Field(
        default="",
        description="Extracted markdown text from OCR"
    )
    success: bool = Field(
        default=True,
        description="Whether OCR succeeded for this page"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if OCR failed"
    )
    processing_time: float = Field(
        default=0.0,
        ge=0,
        description="Time in seconds to process this page"
    )
    
    @computed_field
    @property
    def has_content(self) -> bool:
        """Check if page has meaningful content."""
        return len(self.text.strip()) > 10
    
    @computed_field
    @property
    def word_count(self) -> int:
        """Approximate word count."""
        return len(self.text.split())


class OCRResult(BaseModel):
    """
    Complete OCR result for a document.
    
    Contains all pages and aggregate statistics.
    """
    
    filename: str = Field(
        ...,
        description="Original PDF filename"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages in document"
    )
    pages: list[OCRPage] = Field(
        default_factory=list,
        description="OCR results for each page"
    )
    processing_time: float = Field(
        default=0.0,
        ge=0,
        description="Total processing time in seconds"
    )
    processed_at: datetime = Field(
        default_factory=datetime.now,
        description="When processing completed"
    )
    
    @computed_field
    @property
    def success_rate(self) -> float:
        """Percentage of pages successfully processed."""
        if not self.pages:
            return 0.0
        successful = sum(1 for p in self.pages if p.success)
        return successful / len(self.pages)
    
    @computed_field
    @property
    def successful_pages(self) -> int:
        """Count of successfully processed pages."""
        return sum(1 for p in self.pages if p.success)
    
    @computed_field
    @property
    def failed_pages(self) -> int:
        """Count of failed pages."""
        return sum(1 for p in self.pages if not p.success)
    
    @computed_field
    @property
    def total_words(self) -> int:
        """Total word count across all pages."""
        return sum(p.word_count for p in self.pages)
    
    def get_page(self, page_number: int) -> Optional[OCRPage]:
        """Get a specific page by number (1-indexed)."""
        for page in self.pages:
            if page.page_number == page_number:
                return page
        return None
    
    def get_full_text(self, separator: str = "\n\n---\n\n") -> str:
        """
        Get all text concatenated with page markers.
        
        Args:
            separator: Text between pages
            
        Returns:
            Full document text with page references
        """
        parts = []
        for page in self.pages:
            if page.success and page.has_content:
                parts.append(f"[Sida {page.page_number}]\n\n{page.text}")
        return separator.join(parts)
    
    def to_export_dict(self) -> dict:
        """
        Export-friendly dictionary format.
        
        Converts datetime to ISO string for JSON serialization.
        """
        return {
            "filename": self.filename,
            "total_pages": self.total_pages,
            "successful_pages": self.successful_pages,
            "failed_pages": self.failed_pages,
            "success_rate": round(self.success_rate, 3),
            "total_words": self.total_words,
            "processing_time": round(self.processing_time, 2),
            "processed_at": self.processed_at.isoformat(),
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.text,
                    "success": p.success,
                    "error": p.error,
                    "word_count": p.word_count,
                    "processing_time": round(p.processing_time, 2)
                }
                for p in self.pages
            ]
        }


class ProcessingProgress(BaseModel):
    """
    Real-time processing progress for UI updates.
    """
    
    current_page: int = Field(default=0, ge=0)
    total_pages: int = Field(default=0, ge=0)
    status: str = Field(default="idle")
    current_page_status: str = Field(default="")
    elapsed_seconds: float = Field(default=0.0, ge=0)
    
    @computed_field
    @property
    def progress_percent(self) -> int:
        """Progress as percentage 0-100."""
        if self.total_pages == 0:
            return 0
        return int((self.current_page / self.total_pages) * 100)
    
    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.current_page >= self.total_pages and self.total_pages > 0


# =============================================================================
# FUTURE MODELS (Phase 2+)
# =============================================================================
# These are placeholders for the full Rättskoll system

class TimelineEvent(BaseModel):
    """Timeline event extracted from FUP (Phase 2)."""
    
    id: str
    description: str
    datetime_str: Optional[str] = None
    source_page: int
    source_quote: str
    involves_persons: list[str] = Field(default_factory=list)


class Person(BaseModel):
    """Person mentioned in FUP (Phase 2)."""
    
    id: str
    name: str
    role: str  # misstänkt, målsägande, vittne, polis
    mentioned_pages: list[int] = Field(default_factory=list)


class Claim(BaseModel):
    """Factual assertion from FUP (Phase 2)."""
    
    id: str
    claim_text: str
    claimant: str
    source_page: int
    source_quote: str
