import os
import PyPDF2
from typing import Dict, Any, Optional
import google.generativeai as genai

class GeminiPDFService:
    """
    Gemini API integration - ONLY used for PDF operations:
    - Search inside PDFs
    - Extract relevant text
    - Summarize content
    - Lookup facts inside documents
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
    
    def search_in_pdf(self, pdf_path: str, query: str) -> Dict[str, Any]:
        """
        Search for information inside a PDF using Gemini.
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API not initialized. Please set GEMINI_API_KEY environment variable.",
                "operation": "search"
            }
        
        try:
            pdf_text = self._read_pdf(pdf_path)
            
            prompt = f"""You are analyzing a PDF document. The user wants to search for: "{query}"

PDF Content:
{pdf_text[:50000]}  # Limit to ~50k chars to avoid token limits

Task: Search through the PDF content and identify:
1. Where the information related to "{query}" appears (page numbers, sections)
2. Relevant excerpts or passages
3. Context around the found information

Provide a one line answer with the attached in line citation with APA 7th edition formatting. Do not use any formatting or bullet points"""

            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "query": query,
                "pdf_path": pdf_path,
                "results": response.text,
                "operation": "search"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "search"
            }
    
    def extract_relevant_text(self, pdf_path: str, query: str) -> Dict[str, Any]:
        """
        Extract relevant text from PDF based on query using Gemini.
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API not initialized. Please set GEMINI_API_KEY environment variable.",
                "operation": "extract"
            }
        
        try:
            pdf_text = self._read_pdf(pdf_path)
            
            prompt = f"""You are extracting specific information from a PDF document.

User's request: "{query}"

PDF Content:
{pdf_text[:50000]}

Task: Extract the most relevant text passages that directly relate to the user's request. 
Provide:
1. The extracted text excerpts
2. Page numbers where they appear
3. Brief context if needed

Focus on accuracy and relevance to the user's query."""

            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "query": query,
                "pdf_path": pdf_path,
                "extracted_text": response.text,
                "operation": "extract"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "extract"
            }
    
    def summarize_content(self, pdf_path: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Summarize PDF content using Gemini.
        If query is provided, create a focused summary related to that topic.
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API not initialized. Please set GEMINI_API_KEY environment variable.",
                "operation": "summarize"
            }
        
        try:
            pdf_text = self._read_pdf(pdf_path)
            
            if query:
                prompt = f"""Summarize the PDF document with a focus on: "{query}"

PDF Content:
{pdf_text[:50000]}

Task: Create a concise summary that highlights information related to "{query}". 
Include key points, main findings, and relevant details."""
            else:
                prompt = f"""Summarize the following PDF document:

PDF Content:
{pdf_text[:50000]}

Task: Create a comprehensive summary including:
1. Main topics and themes
2. Key points and findings
3. Important details
4. Overall document structure"""

            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "summary": response.text,
                "focus": query if query else "general",
                "operation": "summarize"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "summarize"
            }
    
    def lookup_facts(self, pdf_path: str, query: str) -> Dict[str, Any]:
        """
        Lookup specific facts or information in the PDF using Gemini.
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API not initialized. Please set GEMINI_API_KEY environment variable.",
                "operation": "lookup"
            }
        
        try:
            pdf_text = self._read_pdf(pdf_path)
            
            prompt = f"""Look up facts and information related to: "{query}"

PDF Content:
{pdf_text[:50000]}

Task: Find and extract factual information related to "{query}" from the PDF.
Provide:
1. Direct answers to the query
2. Supporting facts and evidence
3. Page references where available
4. Any related information that might be relevant

Be precise and cite specific information from the document."""

            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "query": query,
                "pdf_path": pdf_path,
                "facts": response.text,
                "operation": "lookup"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "operation": "lookup"
            }

