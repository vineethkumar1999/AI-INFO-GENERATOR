from flask import Flask, render_template, request, jsonify
from services.storage_service import save_raw_content, save_summary
from services.summarizer_service import generate_summary
from services.knowledge_store import save_summary , fetch_summaries, fetch_keywords_and_subcategories
from services.promt_builder import build_testcase_prompt
from services.testcase_generator import generate_testcases
from services.export_prompt_builder import build_export_testcase_prompt
from services.exporter import export_to_excel
from flask import send_file
from services.Auth_service import verify_user
import logging
import os

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


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
    try:
        data = request.json

        keywords = _as_list(data.get("keyword"))
        subcategories = _as_list(data.get("subcategory"))
        user_query = data.get("query")

        app.logger.info(
            f"Generate called | keywords={keywords} | subcategories={subcategories}"
        )

        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        # 1. Fetch summaries from MongoDB
        summaries = fetch_summaries(keywords, subcategories)

        if not summaries:
            return jsonify({
                "error": "No knowledge found for selected keywords/subcategories"
            }), 404

        app.logger.info(f"Fetched {len(summaries)} summaries")

        # 2. Build normal (non-testcase) prompt
        prompt = build_testcase_prompt(
            summaries=summaries,
            user_query=user_query
        )


        response = generate_summary(prompt)

        app.logger.info("Normal GPT response generated")

        return jsonify({
            "response": response
        })

    except Exception as e:
        app.logger.exception("Generate failed")
        return jsonify({"error": str(e)}), 500



@app.route("/ingest", methods=["POST"])
def ingest():
    try:
        if not session.get("authenticated"):
            return jsonify({"error": "Not authenticated"}), 401
        
        data = request.json
        keyword = data.get("keyword")
        subcategory = data.get("subcategory")
        text = data.get("content")

        app.logger.info(f"Ingest called for [{keyword} :: {subcategory}]")

        if not keyword or not subcategory or not text:
            app.logger.warning("Ingest failed due to missing fields")
            return jsonify({"error": "Keyword, subcategory and content are required"}), 400

        summary = generate_summary(text)
        app.logger.info("Summary generated successfully")
        added_by = session.get("username")
        if not added_by:
            return jsonify({"error": "User not authenticated"}), 401

        save_summary(keyword, subcategory, summary, added_by)
        app.logger.info("Summary saved to MongoDB")

        return jsonify({"status": "Knowledge stored successfully"})

    except Exception as e:
        app.logger.exception("Error during ingest")
        return jsonify({"error": str(e)}), 500


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

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if verify_user(username, password):
        session["authenticated"] = True
        session["username"] = username
        return jsonify({"status": "authenticated"})

    return jsonify({"error": "Invalid credentials"}), 401



@app.route("/metadata", methods=["GET"])
def metadata():
    data = fetch_keywords_and_subcategories()
    return jsonify(data)


@app.route("/download", methods=["GET"])
def download():
    file_path = request.args.get("file")
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
