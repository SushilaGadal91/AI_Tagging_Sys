
from techSpecAgent.figma_capture import capture_sync
from techSpecAgent.vision_to_tagging_update import extract_components_dict, update_tagging_rules_dictionary
from techSpecAgent.ac_loader import load_acceptance_criteria
from techSpecAgent.llm_mapper import map_to_spec
from techSpecAgent.spec_writer import write_excel
import os
from dotenv import load_dotenv
 
def main():
    load_dotenv()
    screenshot = capture_sync()
    image_path = screenshot
    tagging_rules_path = os.getenv("RULES_FILE")
    components_dict = extract_components_dict(image_path)
    update_tagging_rules_dictionary(components_dict, tagging_rules_path)
    print("Updated tagging rules dictionary from screenshot.")
    ac_text = load_acceptance_criteria()
    rows = map_to_spec(screenshot, ac_text)
    path = write_excel(rows)
    print(f"Tech Spec generated: {path}")
 
if __name__ == "__main__":
    main()