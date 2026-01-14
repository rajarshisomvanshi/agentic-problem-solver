import os
from pathlib import Path
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class OCRService:
    def __init__(self):
        self._model = genai.GenerativeModel("gemini-2.0-flash")

    async def extract_text(self, file_path: str) -> str:
        """
        Extracts text from a file (PDF or Image).
        - PDFs: Uses pypdf for fast local extraction.
        - Images: Uses Gemini Flash for OCR.
        """
        path = Path(file_path)
        if not path.exists():
            return f"[Error: File not found: {file_path}]"

        extension = path.suffix.lower()

        try:
            if extension == ".pdf":
                return self._extract_from_pdf(path)
            elif extension in [".jpg", ".jpeg", ".png", ".webp", ".heic"]:
                return await self._extract_from_image(path)
            else:
                return f"[Error: Unsupported file type for OCR: {extension}]"
        except Exception as e:
            return f"[Error extracting text from {path.name}: {str(e)}]"

    def _extract_from_pdf(self, path: Path) -> str:
        print(f"Extracting text from PDF: {path}")
        try:
            reader = PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF Extraction failed: {e}")

    async def _extract_from_image(self, path: Path) -> str:
        print(f"Extracting text from Image (OCR): {path}")
        try:
            # Check file size for Gemini (limit is usually high, but good to be safe)
            # We use the upload_file API for images as well or pass directly if small?
            # Flash accepts image parts directly.
            
            # For simplicity and speed with Flash, we can upload or pass bytes.
            # Local file path is supported by our updated llm.py approach using genai.upload_file
            # But here we want a specific prompt.
            
            myfile = genai.upload_file(path)
            
            response = await self._model.generate_content_async(
                [myfile, "Extract all text from this image verbatim. If there is no text, describe the image content briefly."]
            )
            return response.text.strip()
        except Exception as e:
             raise Exception(f"Gemini OCR failed: {e}")

ocr_service = OCRService()
