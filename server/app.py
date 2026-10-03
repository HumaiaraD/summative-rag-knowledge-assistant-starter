from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from rag_service import answer_question

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": Config.CLIENT_ORIGIN}})


@app.get("/api/health")
def health():
    """Confirm that the backend is running."""
    return jsonify(
        {
            "status": "ok",
            "message": "Backend is running.",
        }
    ), 200


@app.post("/api/ask")
def ask_question():
    """
    Receive a question from the frontend and return an answer with sources.

    TODO:
    - Read JSON from the request body.
    - Validate that the question exists and is not blank.
    - Call answer_question(question).
    - Return the result as JSON.
    - Return a helpful error response if the question is missing.
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required."}), 400

    # TODO:
    # Replace this starter response by calling answer_question(question).
    #
    # Expected return shape:
    # {
    #     "answer": "...",
    #     "sources": [...]
    # }
    #
    # Example:
    # result = answer_question(question)
    # return jsonify(result), 200

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    question = data.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Question is required."}), 400

    result = answer_question(question.strip())

    return jsonify(result), 200

    # return jsonify(
    #     {
    #         "error": (
    #             "The /api/ask route is connected, but the RAG workflow is not implemented yet. "
    #             "Complete the TODO in server/app.py."
    #         ),
    #         "sources": [],
    #     }
    # ), 501


if __name__ == "__main__":
    app.run(debug=True, port=5555)
