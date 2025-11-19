"""
Explainability Module
Provides finding → evidence → confidence explanations for AI-generated reports.
"""
from typing import Dict, List, Any, Tuple
import json


class ExplainabilityEngine:
    """
    Generates explanations for AI findings, linking findings to evidence and confidence scores.
    """
    
    def __init__(self):
        """Initialize the explainability engine."""
        self.explanation_templates = {
            "high_confidence": "Strong visual evidence supports this finding with clear radiographic features.",
            "medium_confidence": "Moderate visual evidence present, but some features may be subtle or partially obscured.",
            "low_confidence": "Limited visual evidence; findings may be subtle or require additional views for confirmation."
        }
    
    def generate_explanations(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate explanations for each finding.
        
        Args:
            findings: List of findings with evidence and confidence
            
        Returns:
            List of findings with added explanations
        """
        explained_findings = []
        
        for finding in findings:
            explanation = self._explain_finding(finding)
            finding_with_explanation = finding.copy()
            finding_with_explanation["explanation"] = explanation
            explained_findings.append(finding_with_explanation)
        
        return explained_findings
    
    def _explain_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate explanation for a single finding.
        """
        confidence = finding.get("confidence", 0.5)
        evidence = finding.get("evidence", "")
        finding_name = finding.get("finding", "")
        location = finding.get("location", "")
        
        # Determine confidence level
        if confidence >= 0.7:
            confidence_level = "high"
            template = self.explanation_templates["high_confidence"]
        elif confidence >= 0.4:
            confidence_level = "medium"
            template = self.explanation_templates["medium_confidence"]
        else:
            confidence_level = "low"
            template = self.explanation_templates["low_confidence"]
        
        # Build evidence chain
        evidence_chain = self._build_evidence_chain(finding)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(finding, confidence_level, evidence)
        
        explanation = {
            "confidence_level": confidence_level,
            "confidence_score": confidence,
            "evidence_chain": evidence_chain,
            "reasoning": reasoning,
            "template": template,
            "key_evidence": self._extract_key_evidence(evidence)
        }
        
        return explanation
    
    def _build_evidence_chain(self, finding: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Build a chain of evidence supporting the finding.
        """
        evidence = finding.get("evidence", "")
        finding_name = finding.get("finding", "")
        location = finding.get("location", "")
        
        chain = []
        
        # Add location evidence
        if location:
            chain.append({
                "type": "location",
                "description": f"Finding located in: {location}",
                "relevance": "high"
            })
        
        # Add visual evidence
        if evidence:
            chain.append({
                "type": "visual",
                "description": evidence,
                "relevance": "high"
            })
        
        # Add confidence-based evidence
        confidence = finding.get("confidence", 0.5)
        if confidence >= 0.7:
            chain.append({
                "type": "confidence",
                "description": "High confidence based on clear radiographic features",
                "relevance": "high"
            })
        
        return chain
    
    def _generate_reasoning(self, finding: Dict[str, Any], confidence_level: str, evidence: str) -> str:
        """
        Generate human-readable reasoning for the finding.
        """
        finding_name = finding.get("finding", "")
        location = finding.get("location", "")
        severity = finding.get("severity", "")
        
        reasoning_parts = []
        
        reasoning_parts.append(f"The AI identified '{finding_name}'")
        
        if location:
            reasoning_parts.append(f"in the {location}")
        
        if severity:
            reasoning_parts.append(f"with {severity} severity")
        
        reasoning_parts.append(f"based on {confidence_level} confidence ({finding.get('confidence', 0):.1%})")
        
        if evidence:
            reasoning_parts.append(f"supported by: {evidence[:100]}...")
        
        return " ".join(reasoning_parts)
    
    def _extract_key_evidence(self, evidence: str) -> List[str]:
        """
        Extract key evidence phrases from the evidence text.
        """
        if not evidence:
            return []
        
        # Simple extraction - look for common radiological phrases
        key_phrases = [
            "increased", "decreased", "enlarged", "opacity", "effusion",
            "consolidation", "atelectasis", "pneumothorax", "edema",
            "cardiomegaly", "blunting", "collapse", "device"
        ]
        
        evidence_lower = evidence.lower()
        found_phrases = [phrase for phrase in key_phrases if phrase in evidence_lower]
        
        return found_phrases[:5]  # Return top 5 key phrases
    
    def generate_summary_explanation(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an overall explanation summary for all findings.
        """
        total_findings = len(findings)
        high_confidence_count = sum(1 for f in findings if f.get("confidence", 0) >= 0.7)
        avg_confidence = sum(f.get("confidence", 0) for f in findings) / total_findings if total_findings > 0 else 0
        
        summary = {
            "total_findings": total_findings,
            "high_confidence_findings": high_confidence_count,
            "average_confidence": round(avg_confidence, 2),
            "overall_reliability": "high" if avg_confidence >= 0.7 else "medium" if avg_confidence >= 0.4 else "low",
            "key_findings": [
                {
                    "finding": f.get("finding", ""),
                    "confidence": f.get("confidence", 0),
                    "location": f.get("location", "")
                }
                for f in sorted(findings, key=lambda x: x.get("confidence", 0), reverse=True)[:3]
            ]
        }
        
        return summary
    
    def format_explanation_for_display(self, explanation: Dict[str, Any]) -> str:
        """
        Format explanation for human-readable display.
        """
        lines = []
        
        lines.append(f"**Confidence Level:** {explanation['confidence_level'].upper()}")
        lines.append(f"**Confidence Score:** {explanation['confidence_score']:.1%}")
        lines.append("")
        lines.append("**Evidence Chain:**")
        for i, evidence in enumerate(explanation['evidence_chain'], 1):
            lines.append(f"  {i}. [{evidence['type'].upper()}] {evidence['description']}")
        lines.append("")
        lines.append(f"**Reasoning:** {explanation['reasoning']}")
        
        if explanation.get('key_evidence'):
            lines.append("")
            lines.append(f"**Key Evidence Terms:** {', '.join(explanation['key_evidence'])}")
        
        return "\n".join(lines)

