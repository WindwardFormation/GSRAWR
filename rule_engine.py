from typing import Dict, Any

class RuleEngine:
    """
    Rule-based logic engine that determines:
    - What action to take based on intent
    - Whether Gemini is needed (only for PDF search operations)
    """
    
    def __init__(self):
        # Map intents to operations
        self.intent_to_operation = {
            "pdf_search": "search"
        }
    
    def apply_rules(self, intent: str, user_message: str) -> Dict[str, Any]:
        """
        Apply rule-based logic to determine:
        - requires_gemini: bool - whether to call Gemini
        - operation: str - what PDF operation to perform
        """
        result = {
            "requires_gemini": False,
            "operation": None
        }
        
        # PDF-related intents require Gemini
        if intent.startswith("pdf_"):
            operation = self.intent_to_operation.get(intent)
            if operation:
                result["requires_gemini"] = True
                result["operation"] = operation
        
        return result

