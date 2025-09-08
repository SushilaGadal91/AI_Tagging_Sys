import os, json
from dotenv import load_dotenv

load_dotenv()
def load_rules() -> dict:
    path = os.getenv("RULES_FILE", "./config/tagging_rules.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
