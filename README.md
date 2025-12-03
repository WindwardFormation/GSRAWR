# GSRAWR - Document Assistant Chatbot

A Flask-based web chatbot that uses **Classical NLP** for intent classification and rule-based responses, with **Gemini API** exclusively for PDF document operations.

## Architecture

```
User → Chatbot → (Classical NLP)
                  ↓ intent classification
                  ↓ rule-based logic
                  ↓ your own templates
              BUT can call Gemini ONLY to:
                  ✓ search inside PDFs
                  ✓ extract relevant text
                  ✓ summarize content
                  ✓ lookup facts inside your documents
              Then YOU format the final response
```

## Features

- **Classical NLP Intent Classification**: Uses pattern matching and keyword recognition (no LLM)
- **Rule-Based Logic**: Determines actions based on classified intents
- **Template-Based Responses**: All responses formatted using predefined templates
- **Gemini PDF Operations**:
  - 🔍 Search inside PDFs
  - 📄 Extract relevant text
  - 📋 Summarize content
  - 🔎 Lookup facts

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Gemini API Key

Set your Gemini API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

Or create a `.env` file (not recommended for production):
```
GEMINI_API_KEY=your-api-key-here
```

### 3. Create Uploads Directory (Optional)

Create an `uploads/` directory to store PDF files:

```bash
mkdir uploads
```

### 4. Run the Application

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

## Usage

### Example Queries

- **Search**: "Search for machine learning in document.pdf"
- **Extract**: "Extract information about Python from file.pdf"
- **Summarize**: "Summarize report.pdf" or "Summarize report.pdf focusing on results"
- **Lookup**: "Lookup 'What is the main conclusion?' in paper.pdf"
- **Greeting**: "Hello", "Hi", "Hey"
- **Help**: "Help", "What can you do?"

### PDF File Paths

You can specify PDF files in your queries:
- By filename if the file is in the `uploads/` directory
- By relative or absolute path

## Project Structure

```
GSRAWR/
├── app.py                 # Flask application entry point
├── chatbot.py            # Main chatbot engine orchestrator
├── intent_classifier.py  # Classical NLP intent classification
├── rule_engine.py        # Rule-based logic engine
├── gemini_pdf_service.py # Gemini API integration (PDF operations only)
├── response_templates.py # Template-based response formatting
├── templates/
│   └── index.html       # Chatbot web interface
├── uploads/             # Directory for PDF files (optional)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How It Works

1. **Intent Classification**: User message is analyzed using classical NLP (keyword matching, regex patterns)
2. **Rule Application**: Rules determine if Gemini is needed (only for PDF operations)
3. **PDF Operations**: If needed, Gemini API is called to process PDF files
4. **Response Formatting**: Final response is formatted using templates (no LLM generation for responses)

## API Endpoints

- `GET /`: Web interface
- `POST /chat`: Send message and receive response
  ```json
  {
    "message": "Search for information in document.pdf"
  }
  ```

## Dependencies

- Flask: Web framework
- PyPDF2: PDF text extraction
- google-generativeai: Gemini API client
- Werkzeug: WSGI utilities

## Notes

- Gemini API is **only** used for PDF operations, not for generating chatbot responses
- All chatbot responses are template-based
- Intent classification uses classical NLP (pattern matching), not LLMs
- PDF files should be placed in the `uploads/` directory or specified with full paths
