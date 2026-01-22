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

def save_summary(keyword, subcategory, summary,added_by):
    keyword = keyword.lower().strip()
    subcategory = subcategory.lower().strip()

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
                    "added_by": added_by,
                    "created_at": datetime.utcnow()
                }
            }
        },
        upsert=True
    )

def fetch_summaries(keywords, subcategories):
    logger.info(f"fetch_summaries called")
    logger.info(f"Keywords received: {keywords}")
    logger.info(f"Subcategories received: {subcategories}")

    if not keywords or not subcategories:
        logger.warning("Empty keywords or subcategories list")
        return []

    # Normalize to lowercase for matching
    keywords = [k.lower() for k in keywords]
    subcategories = [s.lower() for s in subcategories]

    query = {
        "keyword": {"$in": keywords},
        "subcategory": {"$in": subcategories}
    }

    logger.info(f"Mongo query: {query}")

    cursor = collection.find(query)

    summaries = []

    for doc in cursor:
        logger.info(
            f"Matched doc: keyword={doc.get('keyword')}, "
            f"subcategory={doc.get('subcategory')}"
        )
        for s in doc.get("summaries", []):
            summaries.append(s.get("summary"))

    logger.info(f"Total summaries fetched: {len(summaries)}")

    return summaries

def fetch_keywords_and_subcategories():
    cursor = collection.find({}, {"keyword": 1, "subcategory": 1})

    mapping = {}
    for doc in cursor:
        k = doc["keyword"]
        s = doc["subcategory"]
        mapping.setdefault(k, set()).add(s)

    return {k: list(v) for k, v in mapping.items()}


