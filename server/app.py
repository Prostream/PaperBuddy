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
            return jsonify({
                "ok": True,
                "message": "PDF received (processing not implemented yet)",
                "filename": file.filename,
                "courseTopic": course_topic
            })
        elif input_type == "url":
            url = request.form.get("url")
            if not url:
                return jsonify({"error": "URL required"}), 400
            # TODO: Fetch and process URL
            return jsonify({
                "ok": True,
                "message": "URL received (processing not implemented yet)",
                "url": url,
                "courseTopic": course_topic
            })
        elif input_type == "abstract":
            abstract = request.form.get("abstract")
            if not abstract:
                return jsonify({"error": "Abstract required"}), 400
            # TODO: Process abstract
            return jsonify({
                "ok": True,
                "message": "Abstract received (processing not implemented yet)",
                "abstractLength": len(abstract),
                "courseTopic": course_topic
            })
        else:
            return jsonify({"error": "Invalid input type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5175"))
    app.run(host="0.0.0.0", port=port)