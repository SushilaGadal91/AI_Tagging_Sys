import os, base64, json, requests
from dotenv import load_dotenv
from rules_loader import load_rules

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_VAR = os.getenv("DEFAULT_ADOBE_VARIABLE", "eVar27")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def encode_image(path:str)->str:
    with open(path, "rb") as f:
        import base64
        return base64.b64encode(f.read()).decode("utf-8")

def map_to_spec(screenshot_path:str, acceptance_text:str):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in .env")
    system = open("prompts/mapper_system.md","r",encoding="utf-8").read()
    rules = load_rules()
    # Ensure variable default from env if not provided in rules
    rules.setdefault("variable", DEFAULT_VAR)

    img_b64 = encode_image(screenshot_path)

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
      "model": OPENAI_MODEL,
      "messages": [
        {"role":"system","content": system},
        {"role":"user","content": [
            {"type":"text","text": "AC (Acceptance Criteria):\n"+acceptance_text},
            {"type":"text","text": "RULES (JSON):\n"+json.dumps(rules)},
            {"type":"image_url","image_url":{"url": f"data:image/png;base64,{img_b64}"}}
        ]}
      ],
      "temperature": 0.2
    }
    r = requests.post(OPENAI_URL, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"].strip()
    try:
        data = json.loads(content)
        assert isinstance(data, list)
    except Exception:
        data = [{
            "kpi_requirement":"LLM_PARSE_ERROR",
            "adobe_variables": rules.get("variable", DEFAULT_VAR),
            "adobe_values": content[:2000]
        }]
    # sanitize defaults
    for row in data:
        row.setdefault("adobe_variables", rules.get("variable", DEFAULT_VAR))
    return data
