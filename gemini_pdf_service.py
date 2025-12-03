import os
import PyPDF2
from typing import Dict, Any, Optional
import google.generativeai as genai

class GeminiPDFService:
    """
    Gemini API integration - ONLY used for PDF search operations:
    - Matches PDF filenames/titles to query for relevance prioritization
    - Searches PDFs one by one in order of relevance
    - Stops early when information is found (early stopping)
    - Processes long PDFs in chunks instead of truncating
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini API client.
        API key can be provided via environment variable GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Try to initialize with available models (newer models first)
                model_names = ['gemini-2.5-flash']
                self.model = None
                
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        print(f"✓ Initialized Gemini model: {model_name}")
                        break
                    except Exception:
                        continue
                
                if not self.model:
                    raise Exception(f"Could not initialize any Gemini model. Tried: {', '.join(model_names)}")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini API: {e}")
                self.model = None
        else:
            print("Warning: GEMINI_API_KEY not set. PDF operations will not work.")
    
    def _read_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}\n")
                
                return "\n".join(text_content)
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _find_all_pdfs(self, uploads_dir: str) -> list:
        """Find all PDF files in the uploads directory."""
        pdf_files = []
        if os.path.exists(uploads_dir):
            for file in os.listdir(uploads_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(uploads_dir, file))
        return pdf_files
    
    def _match_pdfs_by_title(self, pdf_files: list, query: str) -> list:
        """Sort PDFs by relevance to query based on filename matching."""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        scored_pdfs = []
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            filename_lower = filename.lower()
            filename_no_ext = filename_lower.replace('.pdf', '')
            
            # Score based on keyword matches in filename
            score = 0
            
            # Check for exact phrase match
            if query_lower in filename_no_ext:
                score += 100
            
            # Check for word matches
            filename_words = set(filename_no_ext.replace('_', ' ').replace('-', ' ').split())
            common_words = query_words.intersection(filename_words)
            score += len(common_words) * 10
            
            # Check for partial word matches
            for qword in query_words:
                for fword in filename_words:
                    if qword in fword or fword in qword:
                        score += 5
            
            scored_pdfs.append((score, pdf_path))
        
        # Sort by score (highest first) and return paths
        scored_pdfs.sort(key=lambda x: x[0], reverse=True)
        return [pdf_path for _, pdf_path in scored_pdfs]
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 50000, overlap: int = 5000) -> list:
        """Split long text into overlapping chunks to avoid truncation."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary if not last chunk
            if end < len(text):
                # Look for sentence endings within the last 2000 chars
                last_period = chunk.rfind('.', -2000)
                last_newline = chunk.rfind('\n', -2000)
                break_point = max(last_period, last_newline)
                
                if break_point > start + chunk_size // 2:  # Only break if we get at least half a chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk)
            
            # Move start with overlap
            start = end - overlap
        
        return chunks
    
    def _search_single_pdf(self, pdf_path: str, query: str) -> Dict[str, Any]:
        """Search a single PDF and return results."""
        try:
            pdf_text = self._read_pdf(pdf_path)
            pdf_name = os.path.basename(pdf_path)
            
            # If PDF is too long, process in chunks
            max_chunk_size = 50000
            chunks = self._split_text_into_chunks(pdf_text, max_chunk_size)
            
            # Search each chunk
            for chunk_idx, chunk in enumerate(chunks):
                prompt = f"""You are analyzing a PDF document. The user wants to search for: "{query}"

PDF Content (Part {chunk_idx + 1} of {len(chunks)}):
{chunk}

Task: Search through this PDF content and find information related to "{query}".
- If you find relevant information, provide a one line answer with inline citations in APA 7th edition formatting.
- If no relevant information is found in this chunk, respond with "NO_RELEVANT_INFO".
- Do not use any formatting, bullet points, or line breaks."""

                response = self.model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Check if we found relevant information
                if result_text.upper() != "NO_RELEVANT_INFO" and len(result_text) > 20:
                    # Found information - check if it's complete
                    return {
                        "success": True,
                        "query": query,
                        "results": result_text,
                        "pdf_path": pdf_path,
                        "pdf_name": pdf_name,
                        "chunk_searched": chunk_idx + 1,
                        "total_chunks": len(chunks),
                        "found_in_chunk": True,
                        "operation": "search"
                    }
            
            # No relevant info found in this PDF
            return {
                "success": False,
                "found_in_pdf": False,
                "pdf_name": pdf_name,
                "operation": "search"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pdf_name": os.path.basename(pdf_path),
                "operation": "search"
            }
    
    def search_all_pdfs(self, query: str, uploads_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for information across PDFs in the uploads directory.
        - First matches PDF filenames to query for relevance
        - Searches PDFs one by one in order of relevance
        - Stops early when information is found
        - Processes long PDFs in chunks
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API not initialized. Please set GEMINI_API_KEY environment variable.",
                "operation": "search"
            }
        
        # Determine uploads directory
        if not uploads_dir:
            uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        
        # Find all PDFs
        all_pdf_files = self._find_all_pdfs(uploads_dir)
        
        if not all_pdf_files:
            return {
                "success": False,
                "error": "No PDF files found in the uploads directory.",
                "operation": "search"
            }
        
        # Match PDFs by title/filename to prioritize relevant ones
        matched_pdfs = self._match_pdfs_by_title(all_pdf_files, query)
        
        # Search PDFs one by one, stopping when we find information
        pdfs_searched = 0
        searched_pdf_names = []
        
        for pdf_path in matched_pdfs:
            pdf_name = os.path.basename(pdf_path)
            searched_pdf_names.append(pdf_name)
            pdfs_searched += 1
            
            # Search this PDF
            result = self._search_single_pdf(pdf_path, query)
            
            # If we found relevant information, return immediately
            if result.get("success") and result.get("found_in_chunk"):
                result["pdfs_searched"] = pdfs_searched
                result["pdfs_total"] = len(all_pdf_files)
                return result
            
            # If there was an error reading this PDF, continue to next one
            if result.get("error"):
                print(f"Warning: Error searching {pdf_name}: {result.get('error')}")
                continue
        
        # If we searched all PDFs and found nothing
        return {
            "success": False,
            "query": query,
            "error": "No relevant information found in any of the PDF documents.",
            "pdfs_searched": pdfs_searched,
            "pdfs_total": len(all_pdf_files),
            "searched_pdf_names": searched_pdf_names,
            "operation": "search"
        }

