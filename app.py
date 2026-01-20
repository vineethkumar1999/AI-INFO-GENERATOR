from flask import Flask, render_template, request, jsonify
from services.storage_service import save_raw_content, save_summary
from services.summarizer_service import summarize


app = Flask(__name__)

def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v not in (None, "")]
    if isinstance(value, str):
        v = value.strip()
        return [v] if v else []
    return [value]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    keywords = _as_list(data.get("keyword"))
    subcategories = _as_list(data.get("subcategory"))
    query = data.get("query")

    return jsonify({
        "status": "received",
        "keyword": keywords,
        "subcategory": subcategories,
        "query": query,
        "message": "This will later go through summarizer + GPT"
    })

@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.json

    keywords = _as_list(data.get("keyword"))
    subcategories = _as_list(data.get("subcategory"))
    content = data.get("content")

    # 1. Create summary once
    summary = summarize(content)

    # 2. Store for every keyword x subcategory combination
    stored = []
    for keyword in keywords:
        for subcategory in subcategories:
            save_raw_content(keyword, subcategory, content)
            save_summary(keyword, subcategory, summary)
            stored.append({"keyword": keyword, "subcategory": subcategory})

    return jsonify({
        "status": "stored",
        "keyword": keywords,
        "subcategory": subcategories,
        "stored": stored
    })


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
