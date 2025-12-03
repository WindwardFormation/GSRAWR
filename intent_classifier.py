import re
from typing import Dict, List

class IntentClassifier:
    """
    Classical NLP-based intent classifier using pattern matching and keywords.
    """
    
    def __init__(self):
        # Define intent patterns using keywords and regex
        self.intent_patterns = {
            "pdf_search": {
                "keywords": ["search", "find", "where", "locate", "look for", "who", "what", "when", "why", "how", "checkup", "tell me", "true", "is", "are", "can", "does", "do"],
                "patterns": [
                    r"search",
                    r"find",
                    r"where",
                    r"what.*is",
                    r"who.*is",
                    r"how.*does",
                    r"tell me",
                ]
            },
            "greeting": {
                "keywords": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
                "patterns": [
                    r"^(hello|hi|hey)[\s!.,]*$",
                    r"good (morning|afternoon|evening)",
                ]
            },
            "goodbye": {
                "keywords": ["bye", "goodbye", "see you", "farewell", "exit"],
                "patterns": [
                    r"^(bye|goodbye|see you)[\s!.,]*$",
                ]
            },
            "help": {
                "keywords": ["help", "assist", "support", "what can you do"],
                "patterns": [
                    r"help",
                    r"what can you do",
                    r"how can you help",
                ]
            },
            "unknown": {
                "keywords": [],
                "patterns": []
            }
        }
    
    def classify(self, user_message: str) -> str:
        """
        Classify user intent using keyword matching and pattern recognition.
        Returns the intent label.
        """
        user_message_lower = user_message.lower().strip()
        
        # Score each intent
        intent_scores = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Keyword matching (weight: 2 points per keyword)
            for keyword in config["keywords"]:
                if keyword in user_message_lower:
                    score += 2
            
            # Pattern matching (weight: 5 points per match)
            for pattern in config["patterns"]:
                if re.search(pattern, user_message_lower, re.IGNORECASE):
                    score += 5
            
            intent_scores[intent] = score
        
        # Return intent with highest score, default to "unknown"
        best_intent = max(intent_scores, key=intent_scores.get)
        
        # Default to pdf_search for most queries (treat as search query)
        # Only return non-unknown if score > 0, and prioritize pdf_search for ambiguous queries
        if intent_scores[best_intent] > 0 and best_intent != "unknown":
            return best_intent
        
        # If unknown and not a clear greeting/help/goodbye, treat as search query
        # Check if it's clearly a greeting/goodbye/help first
        if intent_scores.get("greeting", 0) == 0 and intent_scores.get("goodbye", 0) == 0 and intent_scores.get("help", 0) == 0:
            # If it's a question or seems like a query, treat as pdf_search
            if any(word in user_message_lower for word in ["?", "what", "who", "when", "where", "why", "how", "is", "are", "can", "does", "do"]):
                return "pdf_search"
        
        return "unknown"

