"""
Analytics Module
Generates comprehensive analytics with realistic admin metrics.
"""
import json
from typing import Dict, List, Any
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta


class AnalyticsEngine:
    """
    Generates simple analytics reports from feedback logs and learning data.
    """
    
    def __init__(self, feedback_log_path: str = "outputs/feedback_logs.json",
                 learning_data_path: str = "outputs/learning_data.json"):
        """
        Initialize the analytics engine.
        
        Args:
            feedback_log_path: Path to feedback logs JSON file
            learning_data_path: Path to learning data JSON file
        """
        # Ensure paths are relative to project root
        if not Path(feedback_log_path).is_absolute():
            # Try to find project root (parent of modules directory)
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            self.feedback_log_path = project_root / feedback_log_path
            self.learning_data_path = project_root / learning_data_path
        else:
            self.feedback_log_path = Path(feedback_log_path)
            self.learning_data_path = Path(learning_data_path)
    
    def _load_feedback_logs(self) -> List[Dict[str, Any]]:
        """Load feedback logs."""
        try:
            if self.feedback_log_path.exists():
                with open(self.feedback_log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def _load_learning_data(self) -> List[Dict[str, Any]]:
        """Load learning data."""
        try:
            if self.learning_data_path.exists():
                with open(self.learning_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """
        Generate simple analytics report with standard summary statistics.
        
        Returns:
            Dictionary containing summary statistics
        """
        feedback_logs = self._load_feedback_logs()
        learning_data = self._load_learning_data()
        
        return {
            "summary": self._generate_summary(feedback_logs, learning_data),
            "admin_dashboard": self._generate_admin_dashboard(feedback_logs, learning_data)
        }
    
    def _generate_summary(self, feedback_logs: List[Dict], learning_data: List[Dict]) -> Dict[str, Any]:
        """Generate simple summary statistics."""
        total_reports = len(feedback_logs)
        reports_with_edits = sum(1 for log in feedback_logs if log.get("has_edits", False))
        total_edits = sum(log.get("edit_count", 0) for log in feedback_logs)
        
        # Count total findings
        total_findings = sum(
            len(log.get("original_report", {}).get("findings", [])) 
            for log in feedback_logs
        )
        
        # Count unique images
        unique_images = len(set(log.get("image_name", log.get("image", "")) for log in feedback_logs))
        
        return {
            "total_reports": total_reports,
            "reports_with_edits": reports_with_edits,
            "total_edits": total_edits,
            "total_findings": total_findings,
            "unique_images": unique_images,
            "total_learning_entries": len(learning_data)
        }
    
    def _generate_admin_dashboard(self, feedback_logs: List[Dict], learning_data: List[Dict]) -> Dict[str, Any]:
        """
        Generate comprehensive admin-level dashboard with realistic metrics.
        
        Returns:
            Dictionary with admin dashboard metrics
        """
        total_reports = len(feedback_logs)
        manual_edits = sum(1 for log in feedback_logs if log.get("has_edits", False))
        fully_automated = total_reports - manual_edits
        
        # Calculate rates
        automation_rate = (fully_automated / total_reports * 100) if total_reports > 0 else 0
        manual_intervention_rate = (manual_edits / total_reports * 100) if total_reports > 0 else 0
        
        # Time-based statistics
        now = datetime.now()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        def parse_timestamp(ts):
            """Parse timestamp string to datetime."""
            if not ts:
                return None
            try:
                if isinstance(ts, str):
                    # Handle ISO format with or without timezone
                    ts_clean = ts.replace('Z', '+00:00')
                    # Remove microseconds if present for compatibility
                    if '.' in ts_clean and '+' in ts_clean:
                        parts = ts_clean.split('+')
                        if '.' in parts[0]:
                            time_part = parts[0].split('.')[0]
                            ts_clean = f"{time_part}+{parts[1]}"
                    return datetime.fromisoformat(ts_clean)
                return None
            except (ValueError, AttributeError, TypeError):
                return None
        
        # Filter logs by time period
        today_logs = [
            log for log in feedback_logs
            if parse_timestamp(log.get("timestamp")) and 
            parse_timestamp(log.get("timestamp")).date() == today
        ]
        week_logs = [
            log for log in feedback_logs
            if parse_timestamp(log.get("timestamp")) and 
            parse_timestamp(log.get("timestamp")).date() >= week_ago
        ]
        month_logs = [
            log for log in feedback_logs
            if parse_timestamp(log.get("timestamp")) and 
            parse_timestamp(log.get("timestamp")).date() >= month_ago
        ]
        
        # Performance metrics
        total_findings = sum(
            len(log.get("original_report", {}).get("findings", [])) 
            for log in feedback_logs
        )
        avg_findings_per_report = total_findings / total_reports if total_reports > 0 else 0
        
        # Quality metrics - average confidence
        all_confidences = []
        for log in feedback_logs:
            findings = log.get("original_report", {}).get("findings", [])
            for finding in findings:
                if isinstance(finding, dict) and "confidence" in finding:
                    all_confidences.append(finding["confidence"])
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        # Manual intervention details
        manual_interventions = []
        for log in feedback_logs:
            if log.get("has_edits", False):
                manual_interventions.append({
                    "timestamp": log.get("timestamp", ""),
                    "image": log.get("image_name", log.get("image", "Unknown")),
                    "edit_count": log.get("edit_count", 0)
                })
        
        # Sort by timestamp (most recent first)
        manual_interventions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "operations_breakdown": {
                "total_operations": total_reports,
                "automated_operations": fully_automated,
                "manual_interventions": manual_edits,
                "automation_rate": round(automation_rate, 1),
                "manual_intervention_rate": round(manual_intervention_rate, 1)
            },
            "time_period_stats": {
                "today": {
                    "total": len(today_logs),
                    "automated": len([log for log in today_logs if not log.get("has_edits", False)]),
                    "manual": len([log for log in today_logs if log.get("has_edits", False)])
                },
                "this_week": {
                    "total": len(week_logs),
                    "automated": len([log for log in week_logs if not log.get("has_edits", False)]),
                    "manual": len([log for log in week_logs if log.get("has_edits", False)])
                },
                "this_month": {
                    "total": len(month_logs),
                    "automated": len([log for log in month_logs if not log.get("has_edits", False)]),
                    "manual": len([log for log in month_logs if log.get("has_edits", False)])
                }
            },
            "performance_metrics": {
                "average_findings_per_report": round(avg_findings_per_report, 1),
                "average_confidence_score": round(avg_confidence * 100, 1),
                "total_findings_detected": total_findings,
                "reports_per_day_avg": round(len(week_logs) / 7, 1) if week_logs else 0
            },
            "manual_interventions": {
                "total_interventions": manual_edits,
                "average_edits_per_intervention": round(
                    sum(log.get("edit_count", 0) for log in feedback_logs if log.get("has_edits", False)) / manual_edits,
                    1
                ) if manual_edits > 0 else 0,
                "recent_interventions": manual_interventions[:10]  # Most recent 10
            }
        }
