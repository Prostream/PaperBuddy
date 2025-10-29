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
if __name__ == '__main__':
port = int(os.getenv('PORT', '5175'))
app.run(host='0.0.0.0', port=port)