from pymongo import MongoClient
from config.config import MONGO_URI, DB_NAME, COLLECTION_NAME
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

import logging

logger = logging.getLogger(__name__)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_summary(keyword, subcategory, summary):
    logger.info(f"Saving summary for [{keyword} :: {subcategory}]")

    collection.update_one(
        {
            "keyword": keyword,
            "subcategory": subcategory
        },
        {
            "$push": {
                "summaries": {
                    "summary": summary,
                    "created_at": datetime.utcnow()
                }
            }
        },
        upsert=True
    )

def fetch_summaries(keywords, subcategories):
    logger.info(f"Fetching summaries for keywords={keywords}, subcategories={subcategories}")

    cursor = collection.find({
        "keyword": {"$in": keywords},
        "subcategory": {"$in": subcategories}
    })

    summaries = []
    for doc in cursor:
        for s in doc.get("summaries", []):
            summaries.append(s["summary"])

    return summaries

def fetch_keywords_and_subcategories():
    cursor = collection.find({}, {"keyword": 1, "subcategory": 1})

    mapping = {}
    for doc in cursor:
        k = doc["keyword"]
        s = doc["subcategory"]
        mapping.setdefault(k, set()).add(s)

    return {k: list(v) for k, v in mapping.items()}


