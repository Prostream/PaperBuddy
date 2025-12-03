# PaperBuddy API Guide

This is the API development guide for the PaperBuddy project, using **RESTful API architecture** with independent module development.

## Table of Contents

- [Overall Architecture](#overall-architecture)
- [API Routes Overview](#api-routes-overview)
- [Module A: Input Parsing](#module-a-input-parsing-person-1)
- [Module B: LLM Summarization](#module-b-llm-summarization-person-2)
- [Module C: Image Generation](#module-c-image-generation-person-3)
- [Module D: Frontend Integration](#module-d-frontend-integration--pdf-export-person-4)
- [Testing Guide](#testing-guide)

---

## Overall Architecture

### Data Flow

```
Input (PDF/URL/Manual)
    ↓
[Module A] /api/parse/pdf or /api/parse/manual or /api/parse/url
    ↓ (returns paperData)
[Module B] /api/summarize
    ↓ (returns summary)
[Module C] /api/images/generate
    ↓ (returns images)
[Module D] Frontend Rendering + PDF Export
```

### Tech Stack

- **Backend**: Flask 3.0 (Python)
- **Frontend**: React 19.1 + Vite 7.1
- **State Management**: React useState (no Redux/Vuex needed)
- **Data Transfer**: JSON format

---

## API Routes Overview

| Route | Method | Owner | Function |
|-------|--------|-------|----------|
| `/api/parse/pdf` | POST | Person 1 | Parse PDF file |
| `/api/parse/url` | POST | Person 1 | Parse paper URL (arXiv/ACM) |
| `/api/parse/manual` | POST | Person 1 | Validate manual input |
| `/api/summarize` | POST | Person 2 | LLM-generate summary |
| `/api/images/generate` | POST | Person 3 | Generate illustrations |

---

## Module A: Input Parsing (Person 1)

### Responsibilities
- Parse PDF files to extract structured data
- Parse paper URLs (arXiv, ACM Digital Library)
- Validate and standardize manual input data

### Route 1: `/api/parse/pdf`

**Request Format**:
```http
POST /api/parse/pdf
Content-Type: multipart/form-data

file: <PDF file>
courseTopic: CV | NLP | Systems
```

**Response Format**:
```json
{
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "abstract": "Abstract content...",
  "sections": [
    {
      "heading": "Introduction",
      "content": "Section content..."
    }
  ],
  "courseTopic": "CV"
}
```

**TODO Checklist**:
1. [x] Install dependency: `pip install PyPDF2`
2. [x] Read PDF file content
3. [x] Extract metadata (title, authors)
4. [x] Identify abstract section
5. [x] Split content by sections
6. [x] Error handling (corrupted files, unsupported formats)

**Implementation Location**: `server/app.py` lines 51-113

---

### Route 2: `/api/parse/url`

**Request Format**:
```http
POST /api/parse/url
Content-Type: application/json

{
  "url": "https://arxiv.org/abs/1234.5678",
  "courseTopic": "NLP"
}
```

**Response Format**: Same as `/api/parse/pdf`

**Supported URLs**:
- arXiv: `https://arxiv.org/abs/[paper-id]` or `https://arxiv.org/pdf/[paper-id].pdf`
- ACM Digital Library: `https://dl.acm.org/doi/10.1145/[numbers]`

**TODO Checklist**:
1. [x] Implement arXiv API integration
2. [x] Implement ACM web scraping
3. [x] Extract metadata from APIs/HTML
4. [x] Error handling (invalid URLs, API failures)

**Implementation Location**: `server/app.py` lines 250-327

---

### Route 3: `/api/parse/manual`

**Request Format**:
```http
POST /api/parse/manual
Content-Type: application/json

{
  "title": "Paper Title",
  "authors": "Author 1, Author 2, Author 3",
  "abstract": "Abstract content",
  "sections": [
    {"heading": "Introduction", "content": "..."}
  ],
  "courseTopic": "NLP"
}
```

**Response Format**: Same as above (standardized)

**TODO Checklist**:
1. [x] Basic field validation (title, authors, abstract required)
2. [x] Deep validation (length limits, format checks)
3. [x] Parse authors string to array
4. [x] Clean and standardize sections
5. [x] Return unified format

**Implementation Location**: `server/app.py` lines 116-190

---

## Module B: LLM Summarization (Person 2)

### Responsibilities
- Use LLM to generate Like-I'm-Five style summaries
- Extract key concepts and teaching aids

### Route: `/api/summarize`

**Request Format**:
```http
POST /api/summarize
Content-Type: application/json

{
  "title": "Paper Title",
  "authors": ["Author 1"],
  "abstract": "Abstract...",
  "sections": [...],
  "courseTopic": "Systems"
}
```

**Response Format**:
```json
{
  "big_idea": "Core idea in one sentence (≤12 words)",
  "steps": [
    "Step 1: Simple description",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "example": "Real-world example explanation",
  "why_it_matters": "Why it's important",
  "limitations": "Limitations",
  "glossary": [
    {"term": "Term 1", "definition": "Simple explanation"}
  ],
  "for_class": {
    "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
    "connections": ["Related to XX topic"],
    "discussion_questions": ["Question 1?", "Question 2?"]
  },
  "accuracy_flags": ["Uncertain parts"]
}
```

**TODO Checklist**:
1. [x] Install dependency: `pip install openai`
2. [x] Set API key: add `OPENAI_API_KEY=sk-xxx` in `.env`
3. [x] Design prompt template:
   - Like-I'm-Five tone
   - Short sentences (≤12 words)
   - Force JSON output
   - Include courseTopic context
4. [x] Call LLM API
5. [x] Parse and validate JSON response
6. [x] Error handling and retry logic
7. [x] Timeout handling (recommended 60 seconds)

**Prompt Example**:
```python
prompt = f"""
You are an expert teacher explaining research papers to 5-year-olds.

Course Topic: {course_topic}
Paper Title: {title}
Abstract: {abstract}

Create a kid-friendly summary in JSON format:
{{
  "big_idea": "one sentence (≤12 words)",
  "steps": ["step1", "step2", "step3"],
  "example": "real-world analogy",
  ...
}}

Use simple words. Keep sentences short.
"""
```

**Implementation Location**: `server/app.py` lines 197-320

---

## Module C: Image Generation (Person 3)

### Responsibilities
- Generate kid-friendly illustrations based on key concepts
- Handle image generation failures with fallback

### Route: `/api/images/generate`

**Request Format**:
```http
POST /api/images/generate
Content-Type: application/json

{
  "key_points": [
    "Key concept 1",
    "Key concept 2",
    "Key concept 3"
  ],
  "style": "pastel"
}
```

**Response Format**:
```json
{
  "images": [
    {
      "url": "https://... or base64 string",
      "description": "Image description",
      "key_point": "Corresponding key concept"
    }
  ]
}
```

**TODO Checklist**:
1. [x] Choose image generation API:
   - DALL-E 3: `pip install openai`
   - Stable Diffusion: `pip install replicate`
2. [x] Set API key
3. [x] Generate prompt for each key_point:
   - Add style keywords (pastel, cute, colorful)
   - Keep kid-friendly style
4. [x] Call image generation API
5. [x] Handle rate limiting (limit to 3-5 images)
6. [x] Implement fallback:
   - Return placeholder URL on failure
   - Or return simple colored rectangles
7. [x] Return image array

**Prompt Example**:
```python
prompt = f"kid-friendly pastel illustration: {key_point}, simple, cute, colorful, children's book style"
```

**Implementation Location**: `server/app.py` lines 327-421

---

## Module D: Frontend Integration & PDF Export (Person 4)

### Responsibilities
- Integrate all API calls
- Design final display page
- Implement PDF export functionality
- Global layout and styling

### Frontend API Calls

All API calls are wrapped in `client/src/api.js`:

```javascript
import { executeFullPipeline } from './api'

// Execute full pipeline
const result = await executeFullPipeline({
  type: 'pdf',        // or 'manual' or 'url'
  data: pdfFile,      // or manualData object or url string
  courseTopic: 'CV'
})

// result contains:
// - paperData: parsed paper data
// - summary: LLM-generated summary
// - images: generated image array
```

### Display Page Structure

Recommended final page layout:

```
┌─────────────────────────────────────┐
│  Header (Paper Title + Authors)     │
├─────────────────────────────────────┤
│  Big Idea (highlighted)              │
├─────────────────────────────────────┤
│  How It Works (Steps)                │
│  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ IMG1 │  │ IMG2 │  │ IMG3 │       │
│  └──────┘  └──────┘  └──────┘       │
├─────────────────────────────────────┤
│  Example & Why It Matters            │
├─────────────────────────────────────┤
│  Glossary (term definitions)         │
├─────────────────────────────────────┤
│  For Class Section                   │
│  - Prerequisites                     │
│  - Connections                       │
│  - Discussion Questions              │
├─────────────────────────────────────┤
│  Limitations & Accuracy Flags        │
├─────────────────────────────────────┤
│  [ Export as PDF ] Button            │
└─────────────────────────────────────┘
```

### PDF Export Implementation

1. [x] Install dependency: `npm install html2pdf.js`
2. [x] Create export function:

```javascript
import html2pdf from 'html2pdf.js'

const exportToPDF = () => {
  const element = document.getElementById('final-result')

  const options = {
    margin: 0.5,
    filename: 'paper-summary.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }

  html2pdf().set(options).from(element).save()
}
```

3. [x] Optimize print styles:

```css
@media print {
  /* Hide navigation and buttons */
  .no-print { display: none; }

  /* Adjust fonts and spacing */
  body { font-size: 12pt; }
}
```

### TODO Checklist
1. [x] Implement complete rendering component (ResultDisplay.jsx)
2. [x] Add Light/Dark mode toggle
3. [x] Implement PDF export functionality
4. [x] Optimize mobile responsiveness
5. [x] Add print styles
6. [x] Implement global loading state
7. [x] Error handling UI

**Implementation Locations**:
- `client/src/App.jsx` (main application)
- `client/src/api.js` (API calls)
- `client/src/ResultDisplay.jsx` (display component)

---

## Testing Guide

### 1. Test Each Module Independently

**Module A Testing**:
```bash
# Test PDF parsing
curl -X POST http://localhost:5175/api/parse/pdf \
  -F "file=@test.pdf" \
  -F "courseTopic=CV"

# Test URL parsing
curl -X POST http://localhost:5175/api/parse/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://arxiv.org/abs/1706.03762", "courseTopic": "NLP"}'
```

**Module B Testing**:
```bash
curl -X POST http://localhost:5175/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Paper",
    "authors": ["Alice"],
    "abstract": "This is a test abstract",
    "sections": [],
    "courseTopic": "NLP"
  }'
```

**Module C Testing**:
```bash
curl -X POST http://localhost:5175/api/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "key_points": ["Neural networks", "Training data"],
    "style": "pastel"
  }'
```

### 2. Frontend Integration Testing

```bash
# Start backend
cd server
python app.py

# Start frontend (in another terminal)
cd client
npm run dev

# Visit http://localhost:5174
```

### 3. Mock Data Testing

Before implementing real APIs, test with mock data:

```javascript
// Temporarily add in api.js
export async function parsePDF(pdfFile, courseTopic) {
  // Return mock data for testing
  return {
    title: "Mock Paper Title",
    authors: ["Mock Author"],
    abstract: "Mock abstract...",
    sections: []
  }
}
```

---

## Environment Variable Configuration

### Backend `.env` File

```bash
# server/.env
PORT=5175
APP_VERSION=0.1.0
CORS_ORIGIN=http://localhost:5174

# Person 2: LLM API Key
OPENAI_API_KEY=sk-xxxxxxxx

# Person 3: Image Generation API Key (if using DALL-E, same as above)
# If using other services:
# REPLICATE_API_TOKEN=r8_xxxxxxxx
```

### Frontend `.env` File

```bash
# client/.env
VITE_API_URL=http://localhost:5175
```

---

## FAQ

### Q1: How to debug APIs?

Use Flask's debug mode (already enabled):
```python
app.run(debug=True)
```

View backend logs:
```bash
cd server
python app.py
# All requests will be printed in the terminal
```

### Q2: How to handle CORS errors?

Verify:
1. Flask-CORS is configured (already done)
2. Frontend API URL is correct
3. Backend service is running

### Q3: How to quickly test a single endpoint?

Use `curl` or Postman, or in browser DevTools:

```javascript
fetch('http://localhost:5175/api/health')
  .then(r => r.json())
  .then(console.log)
```

### Q4: What if images are too large and slow response?

Recommendations:
1. Limit number of images (3-5)
2. Use smaller dimensions (512x512)
3. Return URLs instead of base64
4. Implement image caching

---

## Integration Timeline Suggestion

### Week 1: Independent Development
- Each person implements their API endpoint
- Test with mock data
- Complete basic functionality

### Week 2: Interface Integration
- Unify JSON schema
- Test API call chain
- Fix bugs

### Week 3: Integration and Optimization
- Person 4 integrates all modules
- Optimize UI/UX
- Implement PDF export

### Week 4: Testing and Demo
- End-to-end testing
- Prepare demo materials
- Fix final issues

---

## Communication

When encountering issues:
1. Check this document and code comments
2. Review TODOs in `server/app.py`
3. Discuss in team chat
4. Update this document

---

**Happy Coding!**
