import re
import os
from typing import Dict, Any

class RuleEngine:
    """
    Rule-based logic engine that determines:
    - What action to take based on intent
    - Whether Gemini is needed (only for PDF operations)
    - What parameters to extract
    """
    
    def __init__(self):
        # Map intents to operations
        self.intent_to_operation = {
            "pdf_search": "search",
            "pdf_extract": "extract",
            "pdf_summarize": "summarize",
            "pdf_lookup": "lookup",
        }
    
    def apply_rules(self, intent: str, user_message: str) -> Dict[str, Any]:
        """
        Apply rule-based logic to determine:
        - requires_gemini: bool - whether to call Gemini
        - operation: str - what PDF operation to perform
        - pdf_path: str - path to PDF file (if specified)
        """
        result = {
            "requires_gemini": False,
            "operation": None,
            "pdf_path": None,
            "intent": intent,
            "metadata": {}
        }
        
        # PDF-related intents require Gemini
        if intent.startswith("pdf_"):
            operation = self.intent_to_operation.get(intent)
            if operation:
                result["requires_gemini"] = True
                result["operation"] = operation
                result["pdf_path"] = self._extract_pdf_path(user_message)
        
        # Extract additional metadata
        result["metadata"] = self._extract_metadata(user_message, intent)
        
        return result
    
    def _extract_pdf_path(self, user_message: str) -> str:
        """
        Extract PDF file path from user message using pattern matching.
        Looks for patterns like: "file.pdf", "/path/to/file.pdf", "in document.pdf"
        """
        # Pattern 1: Filename with .pdf extension
        pdf_pattern = r'([\w\s\-_/\\]+\.pdf)'
        matches = re.findall(pdf_pattern, user_message, re.IGNORECASE)
        
        if matches:
            pdf_path = matches[-1].strip()  # Take the last match
            
            # Check if it's an absolute path or relative
            if os.path.isabs(pdf_path):
                if os.path.exists(pdf_path):
                    return pdf_path
            else:
                # Check in uploads directory
                uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
                potential_path = os.path.join(uploads_dir, pdf_path)
                if os.path.exists(potential_path):
                    return potential_path
                
                # Check if file exists relative to current directory
                if os.path.exists(pdf_path):
                    return os.path.abspath(pdf_path)
        
        return None
    
    def _extract_metadata(self, user_message: str, intent: str) -> Dict[str, Any]:
        """
        Extract additional metadata from user message.
        Can extract things like page numbers, sections, etc.
        """
        metadata = {}
        
        # Extract page numbers
        page_pattern = r'page\s+(\d+)'
        page_match = re.search(page_pattern, user_message, re.IGNORECASE)
        if page_match:
            metadata["page"] = int(page_match.group(1))
        
        # Extract section names
        section_pattern = r'section\s+["\']?([^"\']+)["\']?'
        section_match = re.search(section_pattern, user_message, re.IGNORECASE)
        if section_match:
            metadata["section"] = section_match.group(1).strip()
        
        return metadata

