import os
from intent_classifier import IntentClassifier
from rule_engine import RuleEngine
from gemini_pdf_service import GeminiPDFService
from response_templates import ResponseTemplates

class ChatbotEngine:    
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.rule_engine = RuleEngine()
        try:
            self.gemini_pdf_service = GeminiPDFService()
        except Exception as e:
            print(f"Warning: Could not initialize Gemini PDF service: {e}")
            self.gemini_pdf_service = None
        self.templates = ResponseTemplates()
    
    def process_message(self, user_message):
        """
        Process user message through the chatbot pipeline:
        1. Classify intent using classical NLP
        2. Apply rule-based logic
        3. If PDF operation needed, call Gemini
        4. Format response using templates
        """
        if not user_message or not user_message.strip():
            return self.templates.get_generic_response("empty")
        
        # Step 1: Intent classification
        intent = self.intent_classifier.classify(user_message)
        
        # Step 2: Rule-based logic
        rule_result = self.rule_engine.apply_rules(intent, user_message)
        
        # Step 3: Check if we need Gemini for PDF operations
        if rule_result.get('requires_gemini'):
            if not self.gemini_pdf_service:
                return self.templates.get_generic_response("unknown") + "\n\nNote: Gemini API is not configured. Please set GEMINI_API_KEY environment variable to use PDF operations."
            
            pdf_result = self._handle_pdf_operation(
                operation=rule_result['operation'],
                query=user_message
            )
            # Step 4: Format response using templates
            return self.templates.format_pdf_response(
                operation=rule_result['operation'],
                result=pdf_result,
                query=user_message
            )
        else:
            # Step 4: Format response using templates (non-PDF)
            return self.templates.format_response(intent)
    
    def _handle_pdf_operation(self, operation, query):
        """
        Route PDF operations to Gemini service.
        For search: automatically searches ALL PDFs in uploads directory.
        """
        if operation == "search":
            # Search through ALL PDFs in uploads directory
            uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
            return self.gemini_pdf_service.search_all_pdfs(query, uploads_dir)
        else:
            return {"error": f"Unknown PDF operation: {operation}"}

