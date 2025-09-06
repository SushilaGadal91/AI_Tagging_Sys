# Generic Agentic Tech Spec Generator (AC + Figma)

This project is **generic**. It reads your Acceptance Criteria, captures a screenshot from Figma, and—using a **configurable rules file**—maps KPIs to Adobe tagging and writes an Excel Tech Spec.

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
# Fill FIGMA_FILE_URL and OPENAI_API_KEY in .env
python run.py
```

## Make it yours

- Put your AC in `acceptance_criteria.txt` (or provide a Google Doc export URL in `.env`).
- Edit `config/tagging_rules.json` to control how **Adobe Values** are named.
- Output goes to `output/techspec.xlsx` (sheet: "Reporting Requirement").
