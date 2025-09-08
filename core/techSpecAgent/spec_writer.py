import os, pandas as pd
from dotenv import load_dotenv

load_dotenv()
OUTPUT_DIR = os.getenv("OUTPUT_DIR")

def write_excel(rows:list)->str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.DataFrame([
        {"KPI Requirement": r.get("kpi_requirement",""),
         "Adobe Variables": r.get("adobe_variables",""),
         "Adobe Values": r.get("adobe_values","")}
        for r in rows
    ])
    out_path = os.path.join(OUTPUT_DIR, "techspec.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Reporting Requirement")
    return out_path
