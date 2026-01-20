from flask import Flask, render_template, request, jsonify
from services.storage_service import save_raw_content, save_summary
from services.summarizer_service import generate_summary
from services.knowledge_store import save_summary , fetch_summaries, fetch_keywords_and_subcategories
from services.promt_builder import build_testcase_prompt
from services.testcase_generator import generate_testcases
from services.export_prompt_builder import build_export_testcase_prompt
from services.exporter import export_to_excel

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

    text = data.get("text")
    keywords = data.get("keywords", [])
    subcategories = data.get("subcategories", [])

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = generate_summary(text)

    save_summary(
        summary=summary,
        keywords=keywords,
        subcategories=subcategories,
        raw_text=text
    )

    return jsonify({"status": "Knowledge stored successfully"})

@app.route("/query", methods=["POST"])
def query():
    data = request.json

    user_query = data.get("query")
    keywords = data.get("keywords", [])
    subcategories = data.get("subcategories", [])

    if not user_query:
        return jsonify({"error": "Query missing"}), 400

    summaries = fetch_summaries(keywords, subcategories)

    if not summaries:
        return jsonify({"error": "No relevant knowledge found"}), 404

    prompt = build_testcase_prompt(summaries, user_query)

    answer = generate_testcases(prompt)

    return jsonify({"response": answer})

@app.route("/export", methods=["POST"])
def export():
    data = request.json

    user_query = data.get("query")
    keywords = data.get("keywords", [])
    subcategories = data.get("subcategories", [])

    summaries = fetch_summaries(keywords, subcategories)
    prompt = build_export_testcase_prompt(summaries, user_query)

    response_json = generate_testcases(prompt)

    file_path = export_to_excel(response_json)

    return jsonify({
        "message": "Export successful",
        "file": file_path
    })

@app.route("/metadata", methods=["GET"])
def metadata():
    data = fetch_keywords_and_subcategories()
    return jsonify(data)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
