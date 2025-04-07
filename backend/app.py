from flask import Flask, request, jsonify
from backend.recommender import recommend_assessments 
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 SHL Recommender API is running!"

@app.route("/recommend", methods=["POST"])
def get_recommendations():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing 'query' field"}), 400

    results = recommend_assessments(query)  

    return jsonify({"recommendations": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
