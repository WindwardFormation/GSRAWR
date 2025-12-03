# Setup Guide

## Quick Start

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Gemini API Key

You need a Gemini API key from Google AI Studio: https://makersuite.google.com/app/apikey

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Run the Application

```bash
python app.py
```

Open your browser and go to: `http://localhost:5000`

## Adding PDF Files

Place PDF files in the `uploads/` directory

