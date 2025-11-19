import json
import os
from pathlib import Path

def log_results(result_dict, log_path="outputs/logs.json"):
    """
    Log results to a JSON file.
    
    Args:
        result_dict: Dictionary containing results to log
        log_path: Path to the log file (default: outputs/logs.json)
        
    Raises:
        OSError: If the file cannot be written
        json.JSONEncodeError: If the data cannot be serialized to JSON
    """
    log_dir = Path(log_path).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    except json.JSONDecodeError:
        # If file exists but is corrupted, start fresh
        logs = []

    logs.append(result_dict)

    try:
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except (OSError, json.JSONEncodeError) as e:
        raise RuntimeError(f"Failed to write log file: {e}") from e
