"""
Continuous Learning Module
Implements rule mining and weak classifier for model improvement over time.
"""
import json
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from collections import defaultdict, Counter
import re


class ContinuousLearningEngine:
    """
    Implements continuous learning through rule mining and weak classifier updates.
    """
    
    def __init__(self, learning_data_path: str = "outputs/learning_data.json"):
        """
        Initialize the continuous learning engine.
        
        Args:
            learning_data_path: Path to learning data JSON file
        """
        self.learning_data_path = Path(learning_data_path)
        self.rules = []
        self.patterns = defaultdict(list)
        self.confidence_adjustments = {}
    
    def load_learning_data(self) -> List[Dict[str, Any]]:
        """Load learning data from file."""
        try:
            if self.learning_data_path.exists():
                with open(self.learning_data_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return []
    
    def mine_rules(self, min_support: int = 2) -> List[Dict[str, Any]]:
        """
        Mine rules from feedback data.
        
        Args:
            min_support: Minimum number of occurrences for a rule to be considered
            
        Returns:
            List of mined rules
        """
        learning_data = self.load_learning_data()
        
        if not learning_data:
            return []
        
        # Extract edit patterns
        edit_patterns = self._extract_edit_patterns(learning_data)
        
        # Extract confidence patterns
        confidence_patterns = self._extract_confidence_patterns(learning_data)
        
        # Extract finding patterns
        finding_patterns = self._extract_finding_patterns(learning_data)
        
        # Combine into rules
        rules = []
        
        # Rule: Common edits
        for pattern, count in edit_patterns.items():
            if count >= min_support:
                rules.append({
                    "type": "edit_pattern",
                    "pattern": pattern,
                    "support": count,
                    "confidence": self._calculate_rule_confidence(pattern, learning_data)
                })
        
        # Rule: Confidence adjustments
        for pattern, adjustment in confidence_patterns.items():
            if abs(adjustment) > 0.1:  # Significant adjustment
                rules.append({
                    "type": "confidence_adjustment",
                    "pattern": pattern,
                    "adjustment": round(adjustment, 2),
                    "support": self._count_pattern_occurrences(pattern, learning_data)
                })
        
        # Rule: Finding associations
        for pattern, associations in finding_patterns.items():
            if len(associations) >= min_support:
                rules.append({
                    "type": "finding_association",
                    "pattern": pattern,
                    "associations": associations,
                    "support": len(associations)
                })
        
        self.rules = sorted(rules, key=lambda x: x.get("support", 0), reverse=True)
        return self.rules
    
    def _extract_edit_patterns(self, learning_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract common edit patterns from learning data.
        """
        patterns = Counter()
        
        for entry in learning_data:
            if not entry.get("has_edits", False):
                continue
            
            original = entry.get("original_findings", [])
            edited = entry.get("edited_findings", [])
            
            # Find what was changed
            for orig_f, edit_f in zip(original, edited):
                if orig_f != edit_f:
                    # Pattern: original -> edited
                    pattern = f"{orig_f.get('finding', '')} -> {edit_f.get('finding', '')}"
                    patterns[pattern] += 1
        
        return dict(patterns)
    
    def _extract_confidence_patterns(self, learning_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract patterns in confidence adjustments.
        """
        adjustments = defaultdict(list)
        
        for entry in learning_data:
            original = entry.get("original_findings", [])
            edited = entry.get("edited_findings", [])
            explanations = entry.get("explanations", [])
            
            for orig_f, edit_f in zip(original, edited):
                finding_name = orig_f.get("finding", "")
                orig_conf = orig_f.get("confidence", 0.5)
                edit_conf = edit_f.get("confidence", 0.5)
                
                if abs(orig_conf - edit_conf) > 0.1:
                    adjustment = edit_conf - orig_conf
                    adjustments[finding_name] = adjustments[finding_name] + [adjustment]
        
        # Average adjustments
        avg_adjustments = {}
        for pattern, values in adjustments.items():
            avg_adjustments[pattern] = sum(values) / len(values)
        
        return avg_adjustments
    
    def _extract_finding_patterns(self, learning_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract patterns in finding associations.
        """
        associations = defaultdict(set)
        
        for entry in learning_data:
            findings = entry.get("original_findings", [])
            finding_names = [f.get("finding", "") for f in findings if f.get("finding")]
            
            # Find co-occurrences
            for i, name1 in enumerate(finding_names):
                for name2 in finding_names[i+1:]:
                    associations[name1].add(name2)
                    associations[name2].add(name1)
        
        return {k: list(v) for k, v in associations.items()}
    
    def _calculate_rule_confidence(self, pattern: str, learning_data: List[Dict[str, Any]]) -> float:
        """
        Calculate confidence for a rule pattern.
        """
        # Simple confidence calculation based on frequency
        pattern_count = self._count_pattern_occurrences(pattern, learning_data)
        total_entries = len([e for e in learning_data if e.get("has_edits", False)])
        
        if total_entries == 0:
            return 0.0
        
        return round(pattern_count / total_entries, 2)
    
    def _count_pattern_occurrences(self, pattern: str, learning_data: List[Dict[str, Any]]) -> int:
        """Count occurrences of a pattern in learning data."""
        count = 0
        for entry in learning_data:
            if pattern in str(entry):
                count += 1
        return count
    
    def apply_rules_to_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply learned rules to improve a new report.
        
        Args:
            report: Original report dictionary
            
        Returns:
            Improved report with rules applied
        """
        if not self.rules:
            self.mine_rules()
        
        improved_report = report.copy()
        improved_findings = []
        
        for finding in report.get("findings", []):
            improved_finding = finding.copy()
            
            # Apply confidence adjustments
            finding_name = finding.get("finding", "")
            for rule in self.rules:
                if rule["type"] == "confidence_adjustment":
                    if finding_name.lower() in rule["pattern"].lower():
                        current_conf = improved_finding.get("confidence", 0.5)
                        adjustment = rule.get("adjustment", 0)
                        new_conf = max(0.0, min(1.0, current_conf + adjustment))
                        improved_finding["confidence"] = round(new_conf, 2)
                        improved_finding["confidence_adjusted"] = True
                        improved_finding["adjustment_reason"] = f"Based on learned pattern: {rule['pattern']}"
            
            improved_findings.append(improved_finding)
        
        improved_report["findings"] = improved_findings
        improved_report["rules_applied"] = len([r for r in self.rules if self._rule_applies(report, r)])
        
        return improved_report
    
    def _rule_applies(self, report: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if a rule applies to a report."""
        if rule["type"] == "confidence_adjustment":
            findings = report.get("findings", [])
            for finding in findings:
                if rule["pattern"].lower() in finding.get("finding", "").lower():
                    return True
        return False
    
    def train_weak_classifier(self, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train a weak classifier based on feedback patterns.
        
        Returns:
            Classifier parameters
        """
        if not learning_data:
            return {}
        
        # Simple weak classifier: pattern-based confidence adjustment
        classifier = {
            "confidence_thresholds": {},
            "finding_weights": {},
            "evidence_weights": {}
        }
        
        # Analyze confidence patterns
        confidence_by_finding = defaultdict(list)
        for entry in learning_data:
            findings = entry.get("original_findings", [])
            for finding in findings:
                finding_name = finding.get("finding", "")
                confidence = finding.get("confidence", 0.5)
                confidence_by_finding[finding_name].append(confidence)
        
        # Calculate average confidence per finding
        for finding_name, confidences in confidence_by_finding.items():
            avg_conf = sum(confidences) / len(confidences)
            classifier["confidence_thresholds"][finding_name] = round(avg_conf, 2)
        
        # Analyze evidence patterns
        evidence_patterns = defaultdict(int)
        for entry in learning_data:
            findings = entry.get("original_findings", [])
            for finding in findings:
                evidence = finding.get("evidence", "").lower()
                # Extract key terms
                key_terms = re.findall(r'\b\w{4,}\b', evidence)
                for term in key_terms[:5]:  # Top 5 terms
                    evidence_patterns[term] += 1
        
        # Weight evidence terms by frequency
        total = sum(evidence_patterns.values())
        if total > 0:
            for term, count in evidence_patterns.items():
                classifier["evidence_weights"][term] = round(count / total, 3)
        
        return classifier
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the learning process.
        """
        learning_data = self.load_learning_data()
        rules = self.mine_rules()
        
        return {
            "total_learning_entries": len(learning_data),
            "total_rules_mined": len(rules),
            "rules_by_type": {
                rule_type: len([r for r in rules if r["type"] == rule_type])
                for rule_type in ["edit_pattern", "confidence_adjustment", "finding_association"]
            },
            "high_confidence_rules": len([r for r in rules if r.get("confidence", 0) >= 0.7]),
            "entries_with_edits": len([e for e in learning_data if e.get("has_edits", False)])
        }

