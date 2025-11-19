import json
from pathlib import Path

def load_radlex_terms(filepath: str) -> dict:
    """
    Load RadLex terms from a JSON file.
    
    Args:
        filepath: Path to the JSON file containing RadLex terms
        
    Returns:
        Dictionary of RadLex terms
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"RadLex terms file not found: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in RadLex terms file: {e}") from e
