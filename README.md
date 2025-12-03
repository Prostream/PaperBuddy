# PaperBuddy: Read Papers Like I’m Five

**Team 10:** Chunzhang Liu, Peixin Yuan, Yao Qin, Ziyong Liu  
**Goal:** Turn dense academic papers into simple, friendly summaries a five-year-old could understand — for faster learning and easier teaching.

---

## What It Does
PaperBuddy is a lightweight web app that:
- Accepts a **PDF**, **paper URL**, or **abstract text**
- Generates a “**Like I’m Five**” summary in short, simple sentences
- Creates **kid-style illustrations** for key ideas
- Builds a mini **glossary** and **classroom box** (“Why it matters”, “Prerequisites”, etc.)
- Lets users **export** the summary as a neat one-page PDF

---

## Tech Stack
| Layer | Tech | Description |
|-------|------|-------------|
| Frontend | **React** | Simple UI, PDF upload, display & export |
| Backend | **Flask (Python)** | REST API: parse PDF, summarize, generate images |
| LLM | Hosted API (e.g., OpenAI) | Summarize with safe "child-friendly" tone |

---

## Documentation

Detailed documentation is available in the [docs](docs/) folder:

- [API Guide](docs/API_GUIDE.md) - Complete API documentation for all modules
- [Module A Implementation](docs/MODULE_A_EXPLANATION.md) - PDF/URL parsing details
- [Module B Implementation](docs/MODULE_B_README.md) - LLM summarization guide
- [Test Results](docs/TEST_RESULTS.md) - Testing documentation and results

---

## Quick Start

### Backend Setup
```bash
cd server
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd client
npm install
npm run dev
```

Visit `http://localhost:5174` to use the application.
