import os
import json
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    @staticmethod
    def find_react_files(repo_path: str) -> List[str]:
        react_files = []
        extensions = ['.jsx', '.tsx', '.js', '.ts']
        repo_path = Path(repo_path)
        
        for ext in extensions:
            for file_path in repo_path.rglob(f'*{ext}'):
                if any(skip in str(file_path) for skip in ['node_modules', 'build', 'dist', '.git']):
                    continue
                react_files.append(str(file_path))
        return react_files
    
    @staticmethod
    def read_file_content(file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""
    
    @staticmethod
    def save_json(data: Dict, output_path: str):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved results to {output_path}")
        except Exception as e:
            logger.error(f"Error saving to {output_path}: {e}")