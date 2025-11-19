"""
Enhanced Feedback Logger Module
Logs original reports, edited reports, explanations, and user feedback for continuous learning.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class FeedbackLogger:
    """
    Enhanced logger that tracks original reports, edits, explanations, and feedback.
    """
    
    def __init__(self, log_dir: str = "outputs"):
        """
        Initialize the feedback logger.
        
        Args:
            log_dir: Directory to store log files
        """
        # Ensure paths are relative to project root
        if not Path(log_dir).is_absolute():
            # Try to find project root (parent of modules directory)
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            self.log_dir = project_root / log_dir
        else:
            self.log_dir = Path(log_dir)
        
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_log_path = self.log_dir / "feedback_logs.json"
        self.learning_data_path = self.log_dir / "learning_data.json"
    
    def log_feedback(
        self,
        image_name: str,
        original_report: Dict[str, Any],
        edited_report: Optional[Dict[str, Any]] = None,
        explanations: Optional[List[Dict[str, Any]]] = None,
        user_feedback: Optional[Dict[str, Any]] = None,
        ontology_mapping: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log comprehensive feedback including original, edited, and explanations.
        
        Args:
            image_name: Name of the image file
            original_report: Original AI-generated report (JSON)
            edited_report: Human-edited version of the report (optional)
            explanations: List of explanations for findings (optional)
            user_feedback: User feedback on the report (optional)
            ontology_mapping: Ontology mapping results (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Dictionary with logged entry information
        """
        timestamp = datetime.now().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "image": image_name,
            "original_report": original_report,
            "edited_report": edited_report,
            "explanations": explanations or [],
            "user_feedback": user_feedback or {},
            "ontology_mapping": ontology_mapping or {},
            "metadata": metadata or {},
            "has_edits": edited_report is not None,
            "edit_count": self._count_edits(original_report, edited_report) if edited_report else 0
        }
        
        # Load existing logs
        logs = self._load_logs()
        
        # Check if this is an update to an existing entry (same image, recent timestamp)
        # Update existing entry if it exists and was created recently (within last hour)
        existing_entry_index = None
        for i, existing_log in enumerate(logs):
            if existing_log.get("image") == image_name:
                # Check if this is a recent entry (within last hour) without edits
                if not existing_log.get("has_edits", False):
                    existing_entry_index = i
                    break
        
        if existing_entry_index is not None:
            # Update existing entry instead of creating duplicate
            logs[existing_entry_index] = entry
        else:
            # Create new entry
            logs.append(entry)
        
        # Save logs
        self._save_logs(logs)
        
        # Also save to learning data for continuous learning
        self._save_learning_data(entry)
        
        return entry
    
    def _count_edits(self, original: Dict[str, Any], edited: Dict[str, Any]) -> int:
        """
        Count the number of edits made to the report.
        """
        edit_count = 0
        
        # Compare findings
        original_findings = original.get("findings", [])
        edited_findings = edited.get("findings", [])
        
        if len(original_findings) != len(edited_findings):
            edit_count += abs(len(original_findings) - len(edited_findings))
        
        # Compare individual findings
        for orig_f, edit_f in zip(original_findings, edited_findings):
            if orig_f != edit_f:
                edit_count += 1
        
        # Compare impression
        if original.get("impression") != edited.get("impression"):
            edit_count += 1
        
        # Compare recommendations
        if original.get("recommendations") != edited.get("recommendations"):
            edit_count += 1
        
        return edit_count
    
    def _load_logs(self) -> List[Dict[str, Any]]:
        """Load existing feedback logs."""
        try:
            if self.feedback_log_path.exists():
                with open(self.feedback_log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def _save_logs(self, logs: List[Dict[str, Any]]):
        """Save feedback logs."""
        try:
            with open(self.feedback_log_path, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
        except (OSError, json.JSONEncodeError) as e:
            raise RuntimeError(f"Failed to write feedback log file: {e}") from e
    
    def _save_learning_data(self, entry: Dict[str, Any]):
        """
        Save entry to learning data file for continuous learning.
        """
        learning_entry = {
            "timestamp": entry["timestamp"],
            "image": entry["image"],
            "original_findings": entry["original_report"].get("findings", []),
            "edited_findings": entry.get("edited_report", {}).get("findings", []),
            "explanations": entry.get("explanations", []),
            "user_feedback": entry.get("user_feedback", {}),
            "ontology_mapping": entry.get("ontology_mapping", {}),
            "has_edits": entry.get("has_edits", False),
            "edit_count": entry.get("edit_count", 0)
        }
        
        # Load existing learning data
        learning_data = self._load_learning_data()
        learning_data.append(learning_entry)
        
        # Save learning data
        try:
            with open(self.learning_data_path, "w", encoding="utf-8") as f:
                json.dump(learning_data, f, indent=2, ensure_ascii=False)
        except (OSError, json.JSONEncodeError) as e:
            raise RuntimeError(f"Failed to write learning data file: {e}") from e
    
    def _load_learning_data(self) -> List[Dict[str, Any]]:
        """Load existing learning data."""
        try:
            if self.learning_data_path.exists():
                with open(self.learning_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged feedback.
        """
        logs = self._load_logs()
        
        if not logs:
            return {
                "total_entries": 0,
                "entries_with_edits": 0,
                "total_edits": 0,
                "average_edits_per_entry": 0
            }
        
        entries_with_edits = sum(1 for log in logs if log.get("has_edits", False))
        total_edits = sum(log.get("edit_count", 0) for log in logs)
        
        return {
            "total_entries": len(logs),
            "entries_with_edits": entries_with_edits,
            "total_edits": total_edits,
            "average_edits_per_entry": round(total_edits / len(logs), 2) if logs else 0,
            "edit_rate": round(entries_with_edits / len(logs), 2) if logs else 0
        }

