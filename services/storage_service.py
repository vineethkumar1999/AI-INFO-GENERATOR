import os

BASE_PATH = "data"


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_raw_content(keyword, subcategory, content):
    path = os.path.join(BASE_PATH, keyword, subcategory)
    ensure_dir(path)

    raw_file = os.path.join(path, "raw.txt")

    with open(raw_file, "a", encoding="utf-8") as f:
        f.write(content + "\n\n")


def save_summary(keyword, subcategory, summary):
    path = os.path.join(BASE_PATH, keyword, subcategory)
    ensure_dir(path)

    summary_file = os.path.join(path, "summary.txt")

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)


def load_summary(keyword, subcategory):
    summary_file = os.path.join(
        BASE_PATH, keyword, subcategory, "summary.txt"
    )

    if not os.path.exists(summary_file):
        return None

    with open(summary_file, "r", encoding="utf-8") as f:
        return f.read()
