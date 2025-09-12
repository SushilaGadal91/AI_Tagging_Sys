import os
import requests
import json
import base64
from dotenv import load_dotenv
 
load_dotenv()
 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
VISION_API_URL = "https://api.openai.com/v1/chat/completions"
 
def extract_text_from_image(image_path: str, prompt: str = "Extract all visible text from this image.") -> str:
    """
    Sends an image to OpenAI Vision LLM and returns the extracted text.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required in .env")
    if not OPENAI_MODEL:
        raise RuntimeError("OPENAI_MODEL is required in .env")
    with open(image_path, "rb") as img_file:
        image_data = img_file.read()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    b64_image = base64.b64encode(image_data).decode("utf-8")
    data = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
                ]
            }
        ],
        "max_tokens": 1024
    }
    response = requests.post(VISION_API_URL, headers=headers, json=data)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("[OpenAI API Error]", response.status_code, response.text)
        raise
    result = response.json()
    return result["choices"][0]["message"]["content"]
 
def extract_components_dict(image_path: str) -> dict:
    prompt = (
        "Extract all UI component names and their visible labels from this image. "
        "Return the result as a JSON object where each key is the component's label in lowercase, "
        "and each value is the component's label in PascalCase. Example: {\"bill\": \"Bill\"}"
    )
    text = extract_text_from_image(image_path, prompt=prompt)
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        json_str = text[start:end]
        components = json.loads(json_str)
    except Exception as e:
        print("[ERROR] Could not parse JSON from LLM output:", e)
        print("Raw LLM output:\n", text)
        raise
    return components
 
def update_tagging_rules_dictionary(new_dict: dict, tagging_rules_path: str):
    with open(tagging_rules_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['dictionary'] = new_dict
    with open(tagging_rules_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Updated 'dictionary' in {tagging_rules_path}")
 
if __name__ == "__main__":
    image_path = os.path.join("OUTPUT_DIR", "figma_screen.png")
    tagging_rules_path = os.path.join("config", "tagging_rules.json")
    components_dict = extract_components_dict(image_path)
    update_tagging_rules_dictionary(components_dict, tagging_rules_path)