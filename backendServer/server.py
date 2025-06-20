from flask import Flask, request, jsonify
from flask_cors import CORS
from run_rag import run_rag

app = Flask(__name__)
CORS(app)  # Allows React frontend to make requests

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get("query", "")
    answer = run_rag(question)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
