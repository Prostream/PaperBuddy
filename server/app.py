from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "http://localhost:5173")}})

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
            "/api/parse/manual",
            "/api/summarize",
            "/api/images/generate"
        ],
    })


# ============================================================================
# MODULE A: PDF/Manual Input Parsing (Person 1)
# ============================================================================

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
            ]
        }

    TODO (Person 1):
        1. Install: pip install PyPDF2
        2. Extract text from PDF
        3. Parse metadata (title, authors)
        4. Extract abstract
        5. Split into sections
        6. Return structured data
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

        # TODO: Implement PDF parsing logic here
        # Example implementation:
        # import PyPDF2
        # pdf_reader = PyPDF2.PdfReader(file)
        # text = extract_text_from_pdf(pdf_reader)
        # paper_data = parse_paper_structure(text)

        # Mock response for now
        return jsonify({
            "title": f"[TODO] Parsed from {file.filename}",
            "authors": ["Author 1", "Author 2"],
            "abstract": "This is a placeholder abstract. Person 1 should implement PDF parsing.",
            "sections": [
                {"heading": "Introduction", "content": "TODO: Extract from PDF"},
                {"heading": "Methods", "content": "TODO: Extract from PDF"}
            ],
            "courseTopic": course_topic
        })

    except Exception as e:
        return jsonify({"error": f"PDF parsing failed: {str(e)}"}), 500


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

        # TODO: Implement thorough validation
        # - Check title length
        # - Validate author names
        # - Check abstract length
        # - Validate section structure

        # Parse authors
        authors = [a.strip() for a in authors_str.split(",") if a.strip()]

        # Filter valid sections
        valid_sections = [
            s for s in sections
            if s.get("heading") or s.get("content")
        ]

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

        # TODO: Implement LLM summarization
        # Example implementation:
        # import openai
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        #
        # prompt = f"""
        # You are an expert teacher explaining complex papers to 5-year-olds.
        # Course topic: {course_topic}
        #
        # Paper: {title}
        # Authors: {', '.join(authors)}
        # Abstract: {abstract}
        #
        # Provide a kid-friendly summary in JSON format with:
        # - big_idea (one sentence, ≤12 words)
        # - steps (3-5 bullet points)
        # - example (real-world analogy)
        # - why_it_matters
        # - limitations
        # - glossary (key terms)
        # - for_class (prereqs, connections, questions)
        # - accuracy_flags (uncertainties)
        # """
        #
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}],
        #     response_format={"type": "json_object"}
        # )
        # summary = json.loads(response.choices[0].message.content)

        # Mock response for now
        return jsonify({
            "big_idea": "Computers learn to see like humans do",
            "steps": [
                "Feed lots of pictures to computer",
                "Computer finds patterns in pictures",
                "Computer learns what things look like",
                "Computer can now recognize new things"
            ],
            "example": "Like teaching a kid to recognize dogs by showing many dog photos",
            "why_it_matters": "Helps self-driving cars see pedestrians and stop signs",
            "limitations": "Gets confused by weird lighting or unusual angles",
            "glossary": [
                {"term": "Neural Network", "definition": "A computer brain made of many tiny helpers"},
                {"term": "Training", "definition": "Teaching the computer by showing examples"}
            ],
            "for_class": {
                "prerequisites": ["Basic machine learning", "Linear algebra"],
                "connections": ["Relates to CNNs and computer vision"],
                "discussion_questions": [
                    "How is this different from traditional vision?",
                    "What are the ethical implications?"
                ]
            },
            "accuracy_flags": [
                "TODO: Person 2 should implement LLM API call",
                "This is placeholder data"
            ]
        })

    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500


# ============================================================================
# MODULE C: Image Generation (Person 3)
# ============================================================================

@app.post("/api/images/generate")
def generate_images():
    """
    Module C - Generate kid-style illustrations

    Input (JSON):
        {
            "key_points": [str],      # 3-5 key concepts to illustrate
            "style": str              # Optional: "pastel" | "colorful" | "simple"
        }

    Output (JSON):
        {
            "images": [
                {
                    "url": str,           # Image URL or base64
                    "description": str,   # What this image shows
                    "key_point": str      # Which key point it illustrates
                },
                ...
            ]
        }

    TODO (Person 3):
        1. Install: pip install openai (for DALL-E)
           or: pip install replicate (for Stable Diffusion)
        2. Set up API key in .env
        3. For each key point:
           - Construct kid-friendly prompt
           - Add style keywords: "pastel", "cute", "simple", "colorful"
           - Call image generation API
           - Handle rate limits
        4. Implement fallback for failures:
           - Return placeholder image URL
           - Or generate simple colored rectangle
        5. Return array of images
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        key_points = data.get("key_points", [])
        style = data.get("style", "pastel")

        if not key_points:
            return jsonify({"error": "key_points are required"}), 400

        # Limit to 5 images max
        key_points = key_points[:5]

        # TODO: Implement image generation
        # Example implementation:
        # import openai
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        #
        # images = []
        # for point in key_points:
        #     prompt = f"kid-friendly {style} illustration: {point}, simple, cute, colorful"
        #     try:
        #         response = openai.Image.create(
        #             prompt=prompt,
        #             n=1,
        #             size="512x512"
        #         )
        #         images.append({
        #             "url": response.data[0].url,
        #             "description": point,
        #             "key_point": point
        #         })
        #     except Exception as e:
        #         # Fallback: use placeholder
        #         images.append({
        #             "url": "https://via.placeholder.com/512/cccccc/ffffff?text=Image+Failed",
        #             "description": f"Failed to generate: {point}",
        #             "key_point": point
        #         })

        # Mock response for now
        mock_images = []
        for i, point in enumerate(key_points):
            mock_images.append({
                "url": f"https://via.placeholder.com/512/pastel{i}/ffffff?text=TODO+Person+3",
                "description": f"Placeholder for: {point}",
                "key_point": point
            })

        return jsonify({
            "images": mock_images,
            "note": "TODO: Person 3 should implement image generation API"
        })

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