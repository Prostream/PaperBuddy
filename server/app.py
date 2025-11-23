from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "http://localhost:5173")}})


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
        "endpoints": ["/api/health", "/api/version", "/api/info"],
    })


@app.post("/api/process")
def process():
    try:
        input_type = request.form.get("type")
        course_topic = request.form.get("courseTopic")

        if input_type == "pdf":
            if "file" not in request.files:
                return jsonify({"error": "No file provided"}), 400
            file = request.files["file"]
            # TODO: Process PDF file
            # Module A (Person 1) will implement PDF parsing logic here
            return jsonify({
                "ok": True,
                "message": "PDF received (processing not implemented yet)",
                "filename": file.filename,
                "courseTopic": course_topic
            })
        elif input_type == "manual":
            manual_data = request.form.get("manualData")
            if not manual_data:
                return jsonify({"error": "Manual data required"}), 400
            # Parse the JSON string
            import json
            paper_data = json.loads(manual_data)
            # TODO: Validate and process manual input
            # Module A (Person 1) will implement validation logic here
            return jsonify({
                "ok": True,
                "message": "Manual input received (processing not implemented yet)",
                "data": {
                    "title": paper_data.get("title"),
                    "authors": paper_data.get("authors"),
                    "abstract": paper_data.get("abstract")[:100] + "..." if len(paper_data.get("abstract", "")) > 100 else paper_data.get("abstract"),
                    "sections_count": len(paper_data.get("sections", []))
                },
                "courseTopic": course_topic
            })
        else:
            return jsonify({"error": "Invalid input type. Must be 'pdf' or 'manual'"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5175"))
    app.run(host="0.0.0.0", port=port)