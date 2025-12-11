from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import re
import io
import requests
from PyPDF2 import PdfReader
from llm_summarizer import LLMSummarizer

load_dotenv()

app = Flask(__name__)
# Allow all origins for deployment (you can restrict this in production if needed)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# Configure max file size (20MB)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024


# ============================================================================
# Health & Info Routes
# ============================================================================

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "paperbuddy-server"})


@app.get("/api/version")
def version():
    return jsonify({"version": os.getenv("APP_VERSION", "0.1.0")})


@app.get("/api/info")
def info():
    return jsonify({
        "name": "PaperBuddy API",
        "description": "Lightweight API for summarizing papers in a kid-friendly way.",
        "endpoints": [
            "/api/health",
            "/api/version",
            "/api/info",
            "/api/parse/pdf",
            "/api/parse/url",
            "/api/parse/manual",
            "/api/summarize",
            "/api/images/generate"
        ],
    })


# ============================================================================
# MODULE A: PDF/Manual Input Parsing (Person 1)
# ============================================================================

def extract_text_from_pdf(pdf_reader):
    """Extract all text from PDF pages"""
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def parse_paper_structure(text):
    """Parse paper text into structured format"""
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    # Try to extract title (usually first non-empty line or from metadata)
    title = ""
    authors = []
    abstract = ""
    sections = []
    
    # Common section headings patterns
    section_patterns = [
        r'^\d+\.?\s*(Introduction|Abstract|Background|Related Work|Method|Methodology|Methods|Approach|Implementation|Results|Evaluation|Discussion|Conclusion|References|Acknowledgments?)$',
        r'^(Introduction|Abstract|Background|Related Work|Method|Methodology|Methods|Approach|Implementation|Results|Evaluation|Discussion|Conclusion|References|Acknowledgments?)$',
        r'^[A-Z][A-Z\s]+$'  # All caps headings
    ]
    
    current_section = None
    current_content = []
    in_abstract = False
    abstract_started = False
    
    for i, line in enumerate(lines):
        # Try to identify title (usually first few lines, longer than 10 chars)
        if not title and len(line) > 10 and len(line) < 200:
            # Skip common prefixes
            if not line.lower().startswith(('abstract', 'introduction', 'keywords', 'author')):
                title = line
                continue
        
        # Try to identify authors (lines with "and" or commas, before abstract)
        if not authors and ('and' in line.lower() or ',' in line) and len(line) < 300:
            # Check if it looks like author names
            if any(keyword not in line.lower() for keyword in ['abstract', 'introduction', 'university', 'department']):
                author_candidates = re.split(r',\s*and\s*|,\s*|\s+and\s+', line)
                if len(author_candidates) >= 1:
                    authors = [a.strip() for a in author_candidates if a.strip() and len(a.strip()) > 2]
                    if authors:
                        continue
        
        # Identify abstract section
        if re.match(r'^Abstract\s*:?$', line, re.IGNORECASE):
            in_abstract = True
            abstract_started = True
            continue
        
        # Collect abstract content
        if in_abstract:
            # Check if we've hit a section heading (end of abstract)
            is_section = any(re.match(pattern, line, re.IGNORECASE) for pattern in section_patterns)
            if is_section and abstract_started and len(abstract) > 50:
                in_abstract = False
                # Continue to process this line as a section heading
            else:
                if abstract:
                    abstract += " "
                abstract += line
                continue
        
        # Identify section headings
        is_section_heading = False
        for pattern in section_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                is_section_heading = True
                break
        
        if is_section_heading:
            # Save previous section
            if current_section and current_content:
                sections.append({
                    "heading": current_section,
                    "content": " ".join(current_content).strip()
                })
            # Start new section
            current_section = line
            current_content = []
        else:
            # Add to current section or create default
            if not current_section:
                current_section = "Content"
            current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections.append({
            "heading": current_section,
            "content": " ".join(current_content).strip()
        })
    
    # Fallback: if no sections found, create one with all content
    if not sections and text:
        sections.append({
            "heading": "Content",
            "content": text[:5000]  # Limit content length
        })
    
    # Clean up title
    if not title or len(title) < 5:
        title = "Untitled Paper"
    
    # Clean up authors
    if not authors:
        authors = ["Unknown"]
    
    # Clean up abstract
    if not abstract:
        # Try to find abstract in first few paragraphs
        first_paragraphs = text[:2000].split('\n\n')
        for para in first_paragraphs[:3]:
            if len(para) > 100 and 'abstract' not in para.lower():
                abstract = para[:500]
                break
        if not abstract:
            abstract = "No abstract found."
    
    return {
        "title": title,
        "authors": authors[:10],  # Limit to 10 authors
        "abstract": abstract[:2000],  # Limit abstract length
        "sections": sections[:20]  # Limit to 20 sections
    }


@app.post("/api/parse/pdf")
def parse_pdf():
    """
    Module A - Parse PDF file

    Input:
        - file: PDF file (multipart/form-data)
        - courseTopic: CV | NLP | Systems

    Output (JSON):
        {
            "title": str,
            "authors": [str],
            "abstract": str,
            "sections": [
                {"heading": str, "content": str},
                ...
            ],
            "courseTopic": str
        }
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        course_topic = request.form.get("courseTopic", "CV")

        # Validate file
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        if not file.filename.endswith(".pdf"):
            return jsonify({"error": "File must be a PDF"}), 400

        # Read PDF file
        try:
            pdf_reader = PdfReader(io.BytesIO(file.read()))
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                return jsonify({"error": "Encrypted PDF files are not supported"}), 400
            
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_reader)
            
            if not text or len(text.strip()) < 50:
                return jsonify({"error": "Could not extract text from PDF. The file might be scanned or corrupted."}), 400
            
            # Parse paper structure
            paper_data = parse_paper_structure(text)
            paper_data["courseTopic"] = course_topic
            
            return jsonify(paper_data)
            
        except Exception as pdf_error:
            return jsonify({"error": f"Failed to parse PDF: {str(pdf_error)}"}), 400

    except Exception as e:
        return jsonify({"error": f"PDF parsing failed: {str(e)}"}), 500


def fetch_arxiv_metadata(arxiv_id):
    """Fetch metadata from arXiv API"""
    try:
        # Remove 'arxiv:' prefix if present
        arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '').strip()
        
        # Try different URL formats
        api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        # Parse XML response
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        
        # Namespace
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        entry = root.find('atom:entry', ns)
        if entry is None:
            return None
        
        title = entry.find('atom:title', ns)
        title_text = title.text.strip().replace('\n', ' ') if title is not None else "Untitled"
        
        authors = []
        for author in entry.findall('atom:author', ns):
            name = author.find('atom:name', ns)
            if name is not None:
                authors.append(name.text.strip())
        
        summary = entry.find('atom:summary', ns)
        abstract_text = summary.text.strip().replace('\n', ' ') if summary is not None else ""
        
        return {
            "title": title_text,
            "authors": authors,
            "abstract": abstract_text
        }
    except Exception as e:
        print(f"Error fetching arXiv metadata: {e}")
        return None


def fetch_acm_metadata(acm_url):
    """Fetch metadata from ACM Digital Library"""
    try:
        # ACM doesn't have a public API, so we'll try to extract from the page
        response = requests.get(acm_url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Try to extract metadata from HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_elem = soup.find('h1', class_='citation__title') or soup.find('h1')
        title = title_elem.get_text(strip=True) if title_elem else "Untitled"
        
        authors = []
        author_elems = soup.find_all('a', class_='author-name') or soup.find_all('span', class_='author')
        for elem in author_elems[:10]:
            author_name = elem.get_text(strip=True)
            if author_name:
                authors.append(author_name)
        
        abstract_elem = soup.find('div', class_='abstractSection') or soup.find('div', {'id': 'abstract'})
        abstract = abstract_elem.get_text(strip=True) if abstract_elem else ""
        
        return {
            "title": title,
            "authors": authors if authors else ["Unknown"],
            "abstract": abstract
        }
    except Exception as e:
        print(f"Error fetching ACM metadata: {e}")
        return None


@app.post("/api/parse/url")
def parse_url():
    """
    Module A - Parse paper from URL (arXiv/ACM)

    Input (JSON):
        {
            "url": str,
            "courseTopic": str
        }

    Output (JSON):
        {
            "title": str,
            "authors": [str],
            "abstract": str,
            "sections": [],
            "courseTopic": str
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        url = data.get("url", "").strip()
        course_topic = data.get("courseTopic", "CV")
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Detect URL type
        metadata = None
        
        if "arxiv.org" in url or "arxiv.org/abs/" in url or "arxiv.org/pdf/" in url:
            # Extract arXiv ID
            arxiv_id_match = re.search(r'arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+|[a-z-]+\/[0-9]+)', url)
            if arxiv_id_match:
                arxiv_id = arxiv_id_match.group(1)
                metadata = fetch_arxiv_metadata(arxiv_id)
            else:
                return jsonify({"error": "Invalid arXiv URL format"}), 400
        
        elif "dl.acm.org" in url or "acm.org" in url:
            metadata = fetch_acm_metadata(url)
        
        else:
            return jsonify({"error": "Unsupported URL. Please provide an arXiv or ACM Digital Library URL."}), 400
        
        if not metadata:
            return jsonify({"error": "Could not fetch metadata from URL"}), 400
        
        # Return standardized structure
        return jsonify({
            "title": metadata.get("title", "Untitled"),
            "authors": metadata.get("authors", ["Unknown"]),
            "abstract": metadata.get("abstract", "No abstract available."),
            "sections": [],  # URL parsing doesn't extract sections
            "courseTopic": course_topic
        })

    except Exception as e:
        return jsonify({"error": f"URL parsing failed: {str(e)}"}), 500


@app.post("/api/parse/manual")
def parse_manual():
    """
    Module A - Validate manual input

    Input (JSON):
        {
            "title": str,
            "authors": str (comma-separated),
            "abstract": str,
            "sections": [{"heading": str, "content": str}],
            "courseTopic": str
        }

    Output (JSON):
        {
            "title": str,
            "authors": [str],
            "abstract": str,
            "sections": [{"heading": str, "content": str}]
        }

    TODO (Person 1):
        1. Validate required fields
        2. Parse authors string into array
        3. Validate section format
        4. Return standardized structure
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract fields
        title = data.get("title", "").strip()
        authors_str = data.get("authors", "").strip()
        abstract = data.get("abstract", "").strip()
        sections = data.get("sections", [])
        course_topic = data.get("courseTopic", "CV")

        # Basic validation
        if not title:
            return jsonify({"error": "Title is required"}), 400
        if not authors_str:
            return jsonify({"error": "Authors are required"}), 400
        if not abstract:
            return jsonify({"error": "Abstract is required"}), 400

        # Enhanced validation
        if len(title) > 500:
            return jsonify({"error": "Title is too long (max 500 characters)"}), 400
        
        if len(abstract) > 5000:
            return jsonify({"error": "Abstract is too long (max 5000 characters)"}), 400
        
        if len(abstract) < 50:
            return jsonify({"error": "Abstract is too short (min 50 characters)"}), 400

        # Parse authors
        authors = [a.strip() for a in authors_str.split(",") if a.strip()]

        if len(authors) == 0:
            return jsonify({"error": "At least one author is required"}), 400
        
        if len(authors) > 20:
            return jsonify({"error": "Too many authors (max 20)"}), 400
        
        # Validate author names
        for author in authors:
            if len(author) < 2:
                return jsonify({"error": "Author names must be at least 2 characters"}), 400
            if len(author) > 100:
                return jsonify({"error": f"Author name too long: {author}"}), 400

        # Validate and clean sections
        valid_sections = []
        for s in sections:
            if not isinstance(s, dict):
                continue
            
            heading = s.get("heading", "").strip()
            content = s.get("content", "").strip()
            
            if heading or content:
                if len(heading) > 200:
                    heading = heading[:200]
                if len(content) > 10000:
                    content = content[:10000]
                
                valid_sections.append({
                    "heading": heading or "Untitled Section",
                    "content": content
                })
        
        # Limit sections
        valid_sections = valid_sections[:30]

        # Return standardized structure
        return jsonify({
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "sections": valid_sections,
            "courseTopic": course_topic
        })

    except Exception as e:
        return jsonify({"error": f"Manual input validation failed: {str(e)}"}), 500


# ============================================================================
# MODULE B: LLM Summarization (Person 2)
# ============================================================================

@app.post("/api/summarize")
def summarize():
    """
    Module B - Generate Like-I'm-Five summary using LLM

    Input (JSON):
        {
            "title": str,
            "authors": [str],
            "abstract": str,
            "sections": [{"heading": str, "content": str}],
            "courseTopic": str
        }

    Output (JSON):
        {
            "big_idea": str,              # One sentence core idea (≤12 words)
            "steps": [str],               # 3-5 steps explaining the method
            "example": str,               # Real-world example
            "why_it_matters": str,        # Why this research is important
            "limitations": str,           # What doesn't work well
            "glossary": [                 # Technical terms explained
                {"term": str, "definition": str}
            ],
            "for_class": {                # Teaching context
                "prerequisites": [str],   # What students need to know first
                "connections": [str],     # How it relates to other topics
                "discussion_questions": [str]
            },
            "accuracy_flags": [str]       # Uncertainties or caveats
        }

    TODO (Person 2):
        1. Install: pip install openai (or anthropic)
        2. Set up API key in .env: OPENAI_API_KEY=sk-xxx
        3. Construct prompt for LLM:
           - Like-I'm-Five style
           - Short sentences (≤12 words)
           - Force JSON output
           - Include course topic context
        4. Call LLM API
        5. Parse and validate JSON response
        6. Handle errors/retries
        7. Return structured summary
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No paper data provided"}), 400

        # Extract paper data
        title = data.get("title", "")
        authors = data.get("authors", [])
        abstract = data.get("abstract", "")
        sections = data.get("sections", [])
        course_topic = data.get("courseTopic", "CV")

        if not title or not abstract:
            return jsonify({"error": "Title and abstract are required"}), 400

        # Use LLMSummarizer to generate kid-friendly summary
        summarizer = LLMSummarizer(backend="openai")
        summary = summarizer.summarize(
            title=title,
            authors=authors,
            abstract=abstract,
            sections=sections,
            course_topic=course_topic
        )

        return jsonify(summary)

    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500


# ============================================================================
# MODULE C: Image Generation (Person 3)
# ============================================================================

@app.post("/api/images/generate")
def generate_images():
    """
    Module C - Generate kid-style illustrations

    Supports multiple backends:
    - placeholder: Local colored images (no API key)
    - openai: DALL-E 3 (requires OPENAI_API_KEY in .env)

    Input:  {"key_points": [str], "style": str}
    Output: {"images": [{url, description, key_point, backend}]}
    """
    try:
        from image_generator import ImageGenerator

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        key_points = data.get("key_points", [])
        style = data.get("style", "pastel")

        if not key_points:
            return jsonify({"error": "key_points are required"}), 400

        # Determine backend: use OpenAI if key exists, otherwise placeholder
        backend = "openai" if os.getenv("OPENAI_API_KEY") else "placeholder"

        # Generate images
        generator = ImageGenerator(backend=backend)
        images = generator.generate_images(key_points, style, max_images=5)

        return jsonify({"images": images, "backend": backend})

    except Exception as e:
        return jsonify({"error": f"Image generation failed: {str(e)}"}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(413)
def file_too_large(_):
    return jsonify({"error": "File too large. Maximum size is 20MB"}), 413


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5175"))
    app.run(host="0.0.0.0", port=port, debug=True)