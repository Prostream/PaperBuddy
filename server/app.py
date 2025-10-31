from flask import Flask, jsonify
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


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5175"))
    app.run(host="0.0.0.0", port=port)