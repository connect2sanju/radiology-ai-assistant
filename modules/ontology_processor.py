"""
Ontology Processor Module
Processes reports using RadLex and CheXpert ontologies for validation and mapping.
"""
from typing import Dict, List, Tuple, Any
import json


class OntologyProcessor:
    """
    Processes radiology reports using RadLex and CheXpert ontologies.
    Maps findings to standard terminology and validates against known conditions.
    """
    
    def __init__(self, radlex_terms: Dict[str, List[str]], chexpert_labels: List[str]):
        """
        Initialize the ontology processor.
        
        Args:
            radlex_terms: Dictionary mapping condition names to RadLex keywords
            chexpert_labels: List of CheXpert label names
        """
        self.radlex_terms = radlex_terms
        self.chexpert_labels = chexpert_labels
        self._build_reverse_mapping()
    
    def _build_reverse_mapping(self):
        """Build reverse mapping from keywords to conditions."""
        self.keyword_to_condition = {}
        for condition, keywords in self.radlex_terms.items():
            for keyword in keywords:
                self.keyword_to_condition[keyword.lower()] = condition
    
    def map_findings_to_ontology(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map report findings to RadLex/CheXpert ontology terms.
        
        Args:
            findings: List of finding dictionaries from JSON report
            
        Returns:
            List of findings with ontology mappings added
        """
        mapped_findings = []
        
        for finding in findings:
            finding_name = finding.get("finding", "").lower()
            evidence = finding.get("evidence", "").lower()
            combined_text = f"{finding_name} {evidence}"
            
            # Find matching RadLex terms
            matched_conditions = []
            matched_keywords = []
            
            for condition, keywords in self.radlex_terms.items():
                for keyword in keywords:
                    if keyword.lower() in combined_text:
                        if condition not in matched_conditions:
                            matched_conditions.append(condition)
                        matched_keywords.append(keyword)
            
            # Check CheXpert labels
            chexpert_matches = []
            for label in self.chexpert_labels:
                if label.lower() in combined_text:
                    chexpert_matches.append(label)
            
            # Create enhanced finding
            enhanced_finding = finding.copy()
            enhanced_finding["ontology_mapping"] = {
                "radlex_conditions": matched_conditions,
                "radlex_keywords": list(set(matched_keywords)),
                "chexpert_labels": chexpert_matches,
                "mapping_confidence": self._calculate_mapping_confidence(
                    matched_conditions, chexpert_matches, finding.get("confidence", 0.5)
                )
            }
            
            mapped_findings.append(enhanced_finding)
        
        return mapped_findings
    
    def _calculate_mapping_confidence(
        self, 
        radlex_matches: List[str], 
        chexpert_matches: List[str],
        original_confidence: float
    ) -> float:
        """
        Calculate confidence in ontology mapping.
        """
        # Base confidence on original finding confidence
        base_confidence = original_confidence
        
        # Boost if both RadLex and CheXpert match
        if radlex_matches and chexpert_matches:
            base_confidence = min(1.0, base_confidence + 0.2)
        elif radlex_matches or chexpert_matches:
            base_confidence = min(1.0, base_confidence + 0.1)
        
        return round(base_confidence, 2)
    
    def validate_findings(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate findings against ontology and flag potential issues.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        for finding in findings:
            finding_name = finding.get("finding", "")
            ontology = finding.get("ontology_mapping", {})
            
            # Check if finding maps to known ontology terms
            if not ontology.get("radlex_conditions") and not ontology.get("chexpert_labels"):
                validation_results["warnings"].append(
                    f"Finding '{finding_name}' does not map to standard RadLex/CheXpert terms"
            )
            
            # Check confidence thresholds
            confidence = finding.get("confidence", 0.5)
            if confidence < 0.3:
                validation_results["warnings"].append(
                    f"Low confidence ({confidence:.1%}) for finding '{finding_name}'"
                )
            elif confidence > 0.9 and not ontology.get("radlex_conditions"):
                validation_results["suggestions"].append(
                    f"High confidence finding '{finding_name}' - consider verifying ontology mapping"
                )
        
        if validation_results["warnings"]:
            validation_results["valid"] = False
        
        return validation_results
    
    def suggest_standard_terms(self, finding_text: str) -> List[str]:
        """
        Suggest standard RadLex/CheXpert terms based on finding text.
        """
        suggestions = []
        finding_lower = finding_text.lower()
        
        # Check against all RadLex terms
        for condition, keywords in self.radlex_terms.items():
            for keyword in keywords:
                if keyword.lower() in finding_lower:
                    if condition not in suggestions:
                        suggestions.append(condition)
        
        # Check against CheXpert labels
        for label in self.chexpert_labels:
            if label.lower() in finding_lower:
                if label not in suggestions:
                    suggestions.append(label)
        
        return suggestions
    
    def get_ontology_statistics(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about ontology coverage.
        """
        total_findings = len(findings)
        radlex_mapped = sum(1 for f in findings if f.get("ontology_mapping", {}).get("radlex_conditions"))
        chexpert_mapped = sum(1 for f in findings if f.get("ontology_mapping", {}).get("chexpert_labels"))
        
        avg_confidence = sum(f.get("confidence", 0) for f in findings) / total_findings if total_findings > 0 else 0
        
        return {
            "total_findings": total_findings,
            "radlex_coverage": radlex_mapped / total_findings if total_findings > 0 else 0,
            "chexpert_coverage": chexpert_mapped / total_findings if total_findings > 0 else 0,
            "average_confidence": round(avg_confidence, 2),
            "mapped_findings": radlex_mapped + chexpert_mapped
        }

