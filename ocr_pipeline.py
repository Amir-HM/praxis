"""
Rättskoll OCR Test - OCR Pipeline
==================================
DeepSeek-OCR integration via Replicate API and Google Gemini integration.
"""

import base64
import time
from io import BytesIO
from typing import Callable, Optional

import replicate
from PIL import Image

from config import (
    OCR_MODEL,
    OCR_TASK_TYPE,
    OCR_RESOLUTION,
    MAX_RETRIES,
    RETRY_BASE_DELAY,
    REPLICATE_API_TOKEN,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
    GEMINI_SYSTEM_PROMPT,
    GEMINI_GENERATION_CONFIG,
    PROVIDER_REPLICATE,
    PROVIDER_GEMINI,
    DEFAULT_PROVIDER,
)
from models import OCRPage, OCRResult, ProcessingProgress


class OCRError(Exception):
    """Custom exception for OCR errors."""
    pass


class OCRPipeline:
    """
    OCR pipeline supporting multiple providers (Replicate/DeepSeek, Google/Gemini).
    """
    
    def __init__(
        self,
        provider: str = DEFAULT_PROVIDER,
        max_retries: int = MAX_RETRIES,
    ):
        """
        Initialize OCR pipeline.
        
        Args:
            provider: OCR provider to use
            max_retries: Maximum retry attempts per page
        """
        self.provider = provider
        self.max_retries = max_retries
        
        # Validate configuration based on provider
        if self.provider == PROVIDER_REPLICATE:
            if not REPLICATE_API_TOKEN:
                raise OCRError(
                    "REPLICATE_API_TOKEN not set. "
                    "Add it to .env file or set as environment variable."
                )
            self.model = OCR_MODEL
            self.task_type = OCR_TASK_TYPE
            self.resolution = OCR_RESOLUTION
            
        elif self.provider == PROVIDER_GEMINI:
            if not GOOGLE_API_KEY:
                raise OCRError(
                    "GOOGLE_API_KEY not set. "
                    "Add it to .env file or set as environment variable."
                )
            # Initialize Gemini
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=GEMINI_SYSTEM_PROMPT,
                generation_config=GEMINI_GENERATION_CONFIG
            )
        else:
            raise OCRError(f"Unknown provider: {provider}")
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 data URI.
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 data URI string for API
        """
        buffer = BytesIO()
        
        # Convert to RGB if necessary (for PNG with alpha)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        image.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return f"data:image/png;base64,{img_base64}"
    
    def _ocr_with_replicate(self, image: Image.Image) -> str:
        """Process image with Replicate (DeepSeek)."""
        image_data = self.image_to_base64(image)
        output = replicate.run(
            self.model,
            input={
                "image": image_data,
                "task_type": self.task_type,
                "resolution_size": self.resolution,
            }
        )
        if isinstance(output, str):
            return output
        return "".join(output) if output else ""

    def _ocr_with_gemini(self, image: Image.Image) -> str:
        """Process image with Google Gemini."""
        # gemini supports PIL image directly
        response = self.gemini_model.generate_content(
            ["Extract all text from this document page in markdown format:", image]
        )
        return response.text

    def ocr_single_page(
        self,
        image: Image.Image,
        page_number: int,
    ) -> OCRPage:
        """
        Process a single page through OCR.
        
        Args:
            image: PIL Image of the page
            page_number: 1-indexed page number
            
        Returns:
            OCRPage with extracted text and metadata
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                text = ""
                if self.provider == PROVIDER_REPLICATE:
                    text = self._ocr_with_replicate(image)
                elif self.provider == PROVIDER_GEMINI:
                    text = self._ocr_with_gemini(image)
                else:
                    raise OCRError(f"Unknown provider: {self.provider}")
                
                processing_time = time.time() - start_time
                
                return OCRPage(
                    page_number=page_number,
                    text=text,
                    success=True,
                    error=None,
                    processing_time=processing_time,
                )
                
            except Exception as e:
                last_error = str(e)
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    time.sleep(delay)
                    continue
        
        # All retries failed
        processing_time = time.time() - start_time
        return OCRPage(
            page_number=page_number,
            text="",
            success=False,
            error=last_error,
            processing_time=processing_time,
        )
    
    def process_document(
        self,
        images: list[Image.Image],
        filename: str = "document.pdf",
        progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
    ) -> OCRResult:
        """
        Process all pages of a document.
        
        Args:
            images: List of PIL Images, one per page
            filename: Original filename for metadata
            progress_callback: Optional callback for progress updates
            
        Returns:
            OCRResult with all pages and statistics
        """
        total_pages = len(images)
        pages: list[OCRPage] = []
        start_time = time.time()
        
        for i, image in enumerate(images):
            page_number = i + 1  # 1-indexed
            
            # Update progress
            if progress_callback:
                progress = ProcessingProgress(
                    current_page=i,
                    total_pages=total_pages,
                    status="processing",
                    current_page_status=f"Bearbetar sida {page_number}...",
                    elapsed_seconds=time.time() - start_time,
                )
                progress_callback(progress)
            
            # Process page
            page_result = self.ocr_single_page(image, page_number)
            pages.append(page_result)
        
        total_time = time.time() - start_time
        
        # Final progress update
        if progress_callback:
            progress = ProcessingProgress(
                current_page=total_pages,
                total_pages=total_pages,
                status="complete",
                current_page_status="Klar!",
                elapsed_seconds=total_time,
            )
            progress_callback(progress)
        
        return OCRResult(
            filename=filename,
            total_pages=total_pages,
            pages=pages,
            processing_time=total_time,
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def ocr_image(image: Image.Image, page_number: int = 1, provider: str = DEFAULT_PROVIDER) -> OCRPage:
    """OCR a single image."""
    pipeline = OCRPipeline(provider=provider)
    return pipeline.ocr_single_page(image, page_number)


def ocr_document(
    images: list[Image.Image],
    filename: str = "document.pdf",
    progress_callback: Optional[Callable[[ProcessingProgress], None]] = None,
    provider: str = DEFAULT_PROVIDER,
) -> OCRResult:
    """OCR a complete document."""
    pipeline = OCRPipeline(provider=provider)
    return pipeline.process_document(images, filename, progress_callback)


# =============================================================================
# CLI TEST
# =============================================================================

if __name__ == "__main__":
    import sys
    import argparse
    from pdf_processor import pdf_to_images
    
    parser = argparse.ArgumentParser(description="Run OCR pipeline on a PDF.")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("--provider", choices=[PROVIDER_GEMINI, PROVIDER_REPLICATE], default=DEFAULT_PROVIDER, help="OCR provider")
    
    args = parser.parse_args()
    
    print(f"🔍 Processing: {args.pdf_path}")
    print(f"🤖 Provider: {args.provider}")
    
    try:
        # Convert PDF to images
        print("📄 Converting PDF to images...")
        images = pdf_to_images(args.pdf_path)
        print(f"   Found {len(images)} pages")
        
        # Process through OCR
        print("🔤 Running OCR...")
        
        def progress_cb(p: ProcessingProgress):
            print(f"   [{p.progress_percent}%] {p.current_page_status}")
        
        result = ocr_document(
            images,
            filename=args.pdf_path,
            progress_callback=progress_cb,
            provider=args.provider
        )
        
        # Show results
        print(f"\n✅ Complete!")
        print(f"   Total pages: {result.total_pages}")
        print(f"   Success rate: {result.success_rate:.0%}")
        print(f"   Processing time: {result.processing_time:.1f}s")
        print(f"   Total words: {result.total_words}")
        
        # Show failed pages errors
        if result.success_rate < 1.0:
            print("\n❌ Errors:")
            for page in result.pages:
                if not page.success:
                    print(f"   Page {page.page_number}: {page.error}")

        # Show first page preview
        if result.pages:
            first_page = result.pages[0]
            preview = first_page.text[:500] + "..." if len(first_page.text) > 500 else first_page.text
            print(f"\n📝 First page preview:\n{preview}")
            
    except OCRError as e:
        print(f"❌ OCR Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
