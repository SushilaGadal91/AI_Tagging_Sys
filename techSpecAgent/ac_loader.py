import os, requests
from dotenv import load_dotenv

load_dotenv()

def load_acceptance_criteria() -> str:
    doc_url = os.getenv("AC_GOOGLE_DOC_EXPORT_URL")
    local_file = os.getenv("AC_LOCAL_FILE")
    if doc_url:
        resp = requests.get(doc_url, timeout=30)
        resp.raise_for_status()
        return resp.text
    if local_file and os.path.exists(local_file):
        with open(local_file, "r", encoding="utf-8") as f:
            return f.read()
    raise RuntimeError("Provide AC_GOOGLE_DOC_EXPORT_URL or AC_LOCAL_FILE in .env")