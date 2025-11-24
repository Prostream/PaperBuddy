# Module A Implementation Documentation

## 1. PyPDF2 Usage

**PyPDF2** is a Python library for reading and manipulating PDF files.

### Installation
PyPDF2 has been added to `server/requirements.txt`. Install it using:
```bash
pip install -r server/requirements.txt
```

### Usage in Code
```python
from PyPDF2 import PdfReader  # Import library

# Read PDF file
pdf_reader = PdfReader(io.BytesIO(file.read()))

# Extract text
for page in pdf_reader.pages:
    text += page.extract_text() + "\n"
```

**Location**: `server/app.py` line 9 (import), line 225 (usage)

---

## 2. URL Parsing Implementation Details

### arXiv URL Parsing
**arXiv** is a preprint server that provides free access to academic papers.

**Implementation**:
1. Use arXiv official API: `http://export.arxiv.org/api/query`
2. Extract paper ID from URL (e.g., `1234.5678`)
3. Call API to get XML-formatted metadata
4. Parse XML to extract title, authors, abstract

**Example URLs**:
- `https://arxiv.org/abs/1234.5678`
- `https://arxiv.org/pdf/1234.5678.pdf`

**Code Location**: `server/app.py` lines 250-291 `fetch_arxiv_metadata()` function

### ACM Digital Library URL Parsing
**ACM** is a top academic organization in computer science. ACM Digital Library contains a large collection of computer science papers.

**Implementation**:
1. Use `requests` library to fetch webpage HTML
2. Use `BeautifulSoup` to parse HTML
3. Extract title, authors, abstract using CSS selectors

**Example URL**:
- `https://dl.acm.org/doi/10.1145/1234567.1234568`

**Code Location**: `server/app.py` lines 294-327 `fetch_acm_metadata()` function

---

## 3. What are arXiv/ACM URLs?

### arXiv
- **Full Name**: Archive (arXiv.org)
- **Nature**: Free preprint server
- **Fields**: Physics, Mathematics, Computer Science, Biology, etc.
- **Features**: Papers are immediately public after upload, no peer review required
- **URL Format**: `https://arxiv.org/abs/[PaperID]` or `https://arxiv.org/pdf/[PaperID].pdf`

**Examples**:
```
https://arxiv.org/abs/1706.03762  (Transformer paper)
https://arxiv.org/abs/2010.11929  (ViT paper)
```

### ACM Digital Library
- **Full Name**: Association for Computing Machinery Digital Library
- **Nature**: Academic paper database in computer science
- **Fields**: Computer Science, Software Engineering, Artificial Intelligence, etc.
- **Features**: Contains peer-reviewed formally published papers
- **URL Format**: `https://dl.acm.org/doi/10.1145/[numbers]`

**Examples**:
```
https://dl.acm.org/doi/10.1145/3448016.3452834
```

---

## 4. What are CV/NLP/Systems?

These are **Course Topic** options that help the system better understand paper content and generate appropriate summaries.

### CV - Computer Vision
- **Research Areas**: Image recognition, object detection, image generation, etc.
- **Example Papers**: YOLO, ResNet, GAN, etc.
- **Applications**: Autonomous driving, face recognition, medical image analysis

### NLP - Natural Language Processing
- **Research Areas**: Text understanding, machine translation, dialogue systems, etc.
- **Example Papers**: BERT, GPT, Transformer, etc.
- **Applications**: Intelligent customer service, translation software, text analysis

### Systems
- **Research Areas**: Operating systems, distributed systems, database systems, etc.
- **Example Papers**: MapReduce, Spark, Kubernetes, etc.
- **Applications**: Cloud computing, big data processing, system optimization

**Role in Project**: 
- Helps LLM (Module B) generate "Like I'm Five" style summaries that better fit the domain
- Provides domain-specific term explanations and teaching suggestions

**Location**: 
- Frontend: `client/src/App.jsx` lines 219-226
- Backend: All parsing APIs accept `courseTopic` parameter

---

## 5. Project Tech Stack

### Backend Tech Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| **Flask** | 3.0.3 | Python web framework, provides REST API |
| **Flask-CORS** | 4.0.1 | Handles cross-origin requests (frontend calling backend) |
| **PyPDF2** | 3.0.1 | PDF file parsing |
| **beautifulsoup4** | 4.12.3 | HTML parsing (ACM URL) |
| **requests** | 2.31.0 | HTTP requests (arXiv API, ACM webpages) |
| **python-dotenv** | 1.0.1 | Environment variable management |

### Frontend Tech Stack
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.1 | UI framework |
| **Vite** | 7.1 | Build tool and development server |
| **JavaScript (ES6+)** | - | Programming language |

### Data Flow
```
User Input (PDF/URL/Manual)
    ↓
[Module A] Parse → Structured data (title, authors, abstract, sections)
    ↓
[Module B] LLM Summarize → kid-friendly summary
    ↓
[Module C] Image Generation → illustrations
    ↓
[Module D] Frontend Display + PDF Export
```

---

## 6. Installation and Testing Steps

### Step 1: Install Backend Dependencies
```bash
cd server
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
cd server
python app.py
```
Server will start at `http://localhost:5175`

### Step 3: Install Frontend Dependencies (if needed)
```bash
cd client
npm install
```

### Step 4: Start Frontend Development Server
```bash
cd client
npm run dev
```
Frontend will start at `http://localhost:5174` (or another port if 5173 is in use)

### Step 5: Test API Endpoints
You can use `curl` or browser to test:
- Health check: `http://localhost:5175/api/health`
- API info: `http://localhost:5175/api/info`
