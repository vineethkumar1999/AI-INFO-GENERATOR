from pymongo import MongoClient
from config.config import MONGO_URI, DB_NAME, COLLECTION_NAME
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_summary(summary, keywords, subcategories, raw_text):
    document = {
        "summary": summary,
        "keywords": keywords,
        "subcategories": subcategories,
        "raw_text": raw_text,
        "created_at": datetime.utcnow()
    }
    collection.insert_one(document)


def fetch_summaries(keywords, subcategories):
    query = {
        "keywords": {"$in": keywords},
        "subcategories": {"$in": subcategories}
    }

    documents = collection.find(query)

    summaries = []
    for doc in documents:
        summaries.append(doc["summary"])

    return summaries


def fetch_keywords_and_subcategories():
    documents = collection.find({}, {"keywords": 1, "subcategories": 1})

    keyword_map = {}

    for doc in documents:
        for kw in doc.get("keywords", []):
            if kw not in keyword_map:
                keyword_map[kw] = set()

            for sub in doc.get("subcategories", []):
                keyword_map[kw].add(sub)

    # Convert sets to lists for JSON
    return {
        k: list(v) for k, v in keyword_map.items()
    }


