# Module B - LLM Summarization (Person 2)

## Status

All features are implemented and ready to use.

## Created Files

1. **`server/llm_summarizer.py`** - Core LLM summarization module
2. **`server/test_summarize.py`** - Test script
3. **`server/.env.example`** - Environment variable configuration example

## Modified Files

1. **`server/app.py`**
   - Added 1 import line: `from llm_summarizer import LLMSummarizer`
   - Replaced mock data with real LLM calls (reduced ~50 lines of commented code)

2. **`server/requirements.txt`**
   - Enabled `openai>=1.12.0` dependency

## How to Use

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file (or copy `.env.example`):

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API Key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

> Get API Key at: https://platform.openai.com/api-keys

### 3. Start Server

```bash
python app.py
```

Server will start at `http://localhost:5175`.

### 4. Test Functionality

Run the test script in another terminal:

```bash
python test_summarize.py
```

Or test using curl:

```bash
curl -X POST http://localhost:5175/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Attention Is All You Need",
    "authors": ["Vaswani et al."],
    "abstract": "The Transformer architecture...",
    "sections": [],
    "courseTopic": "NLP"
  }'
```

## Features

### Automatic Fallback
- Returns mock data if `OPENAI_API_KEY` is not configured
- Falls back to mock data if API call fails

### Smart Retry
- API timeout: Automatic retry up to 3 times (exponential backoff)
- Rate limit: Automatic delayed retry
- JSON parsing failure: Automatic retry

### Output Format
Returns Like-I'm-Five style JSON:

```json
{
  "big_idea": "Core idea in one sentence (≤12 words)",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "example": "Real-world analogy",
  "why_it_matters": "Why it's important",
  "limitations": "Limitations",
  "glossary": [
    {"term": "Term", "definition": "Simple explanation"}
  ],
  "for_class": {
    "prerequisites": ["Prerequisite knowledge"],
    "connections": ["Related topics"],
    "discussion_questions": ["Discussion question?"]
  },
  "accuracy_flags": ["Uncertain parts"]
}
```

## API Endpoint

### POST `/api/summarize`

**Request Body:**
```json
{
  "title": "Paper title",
  "authors": ["Author 1", "Author 2"],
  "abstract": "Abstract content",
  "sections": [
    {"heading": "Section title", "content": "Section content"}
  ],
  "courseTopic": "CV | NLP | Systems"
}
```

**Response:** See output format above

## Configuration Options

Adjustable in `llm_summarizer.py`:

- `max_retries`: Maximum retry attempts (default: 3)
- `timeout`: API timeout in seconds (default: 60)
- `model`: OpenAI model (default: `gpt-4o`)
- `temperature`: Generation temperature (default: 0.7)
- `max_tokens`: Maximum tokens (default: 2000)

## Implementation Locations

| File | Lines | Description |
|------|-------|-------------|
| `server/llm_summarizer.py` | 1-438 | Complete LLM module implementation |
| `server/app.py` | 10 | Import statement |
| `server/app.py` | 573-583 | API call (11 lines) |

## Completion Checklist

- [x] Create standalone `llm_summarizer.py` module
- [x] Implement OpenAI GPT-4o integration
- [x] Design Like-I'm-Five style prompt
- [x] Add error handling and retry logic
- [x] Implement mock fallback
- [x] JSON output validation and repair
- [x] Update `requirements.txt`
- [x] Minimize changes to `app.py` (only 12 lines modified)
- [x] Create test script
- [x] Create configuration example file

## Design Principles

1. **Low Intrusion**: Only added 1 import line and replaced 1 function body in `app.py`
2. **Standalone Module**: All logic encapsulated in `llm_summarizer.py`
3. **Fault Tolerance**: Automatic fallback and retry mechanisms
4. **Easy to Test**: Provides standalone test script
5. **Clear Documentation**: Detailed comments and docstrings

## Integration with Other Modules

- **Module A (Person 1)**: Receives output from `parse/pdf` or `parse/manual`
- **Module C (Person 3)**: Extracts `term` from `glossary` as `key_points`
- **Module D (Person 4)**: Frontend calls `executeFullPipeline()` which automatically includes this module

## Troubleshooting

If you encounter issues:
1. Check if `OPENAI_API_KEY` is correctly configured
2. Review server log output
3. Run `test_summarize.py` to check if mock mode works
4. Verify `openai` package is installed: `pip list | grep openai`

---

**Person 2's work is complete!**
