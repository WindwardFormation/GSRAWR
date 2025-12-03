from typing import Dict, Any
import random

class ResponseTemplates:
    """
    Template-based response formatting.
    Formats responses using predefined templates - no LLM generation for responses.
    """
    
    def __init__(self):
        self.templates = {
            "greeting": [
                "Hello! I'm your document assistant chatbot. I can search through all your PDF documents automatically. Just ask me any question!",
                "Hi there! I automatically search through all available PDF documents to answer your questions. What would you like to know?",
                "Greetings! Ask me any question and I'll search through my document database to find the answer for you.",
            ],
            "goodbye": [
                "Goodbye! Have a great day!",
                "See you later! Feel free to come back if you need help with documents.",
                "Farewell! Take care!",
            ],
            "help": """I'm a chatbot that can help you search for nutritional facts! 
            Just ask me any question and I'll search through my documents to find the answer!""",
            "empty": "I didn't receive a message. Please type something!",
            "unknown": "I'm not sure I understand. Could you rephrase that?"
        }
    
    def format_response(self, intent: str) -> str:
        """
        Format a non-PDF response using templates.
        """
        if intent in self.templates:
            template = self.templates[intent]
            
            # If it's a list, pick one randomly or cycle
            if isinstance(template, list):
                return random.choice(template)
                
            return template
        
        return self.templates["unknown"]
    
    def format_pdf_response(self, operation: str, result: Dict[str, Any], query: str) -> str:
        """
        Format PDF operation response using templates.
        """
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown error occurred")
            return f"❌ Error performing {operation} operation: {error_msg}"
        
        # Format based on operation type
        if operation == "search":
            response_text = result.get("results", "No results found.")
            # Don't show PDF paths to users - keep it private
        else:
            response_text = f"Operation completed: {operation}\n\n{result}"
        
        return response_text
    
    def get_generic_response(self, response_type: str) -> str:
        """Get a generic response by type."""
        return self.templates.get(response_type, self.templates["unknown"])

