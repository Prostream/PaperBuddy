from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGIN", "http://localhost:5173")}})
@app.get('/api/health')
def health():
return jsonify({"ok": True, "service": "paperbuddy-server"})

@app.get('/api/papers')
def list_papers():
    sample_papers = [
        {
            "id": "2301.00001",
            "title": "Attention Is All You Need",
            "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
            "year": 2017,
            "url": "https://arxiv.org/abs/1706.03762"
        },
        {
            "id": "2301.00002",
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee"],
            "year": 2018,
            "url": "https://arxiv.org/abs/1810.04805"
        }
    ]
    return jsonify({"items": sample_papers})
if __name__ == '__main__':
port = int(os.getenv('PORT', '5175'))
app.run(host='0.0.0.0', port=port)