from techSpecAgent.figma_capture import capture_sync
from techSpecAgent.ac_loader import load_acceptance_criteria
from techSpecAgent.llm_mapper import map_to_spec
from techSpecAgent.spec_writer import write_excel
from dotenv import load_dotenv

def main():
    load_dotenv()
    screenshot = capture_sync()
    ac_text = load_acceptance_criteria()
    rows = map_to_spec(screenshot, ac_text)
    path = write_excel(rows)
    print(f"[SUCCESS] Tech Spec generated: {path}")

if __name__ == "__main__":
    main()
