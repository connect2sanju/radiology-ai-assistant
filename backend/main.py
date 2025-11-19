"""
FastAPI Backend Server for Radiology AI Assistant
Provides REST API endpoints for the React frontend.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import io
from PIL import Image
import json
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.radlex_loader import load_radlex_terms
from modules.json_report_generator import generate_json_report, format_json_report_to_text
from modules.ontology_processor import OntologyProcessor
from modules.explainability import ExplainabilityEngine
from modules.feedback_logger import FeedbackLogger
from modules.continuous_learning import ContinuousLearningEngine
from modules.chexpert_simulator import simulate_chexpert_labels
from modules.report_evaluator import compare_labels_with_report
from modules.analytics import AnalyticsEngine
from config import OPENAI_API_KEY, OPENAI_MODEL

app = FastAPI(title="Radiology AI Assistant API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ReportEditRequest(BaseModel):
    original_report: Dict[str, Any]
    edited_report: Dict[str, Any]
    explanations: Optional[Dict[str, Any]] = None
    ontology_mapping: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    image_name: str
    original_report: Dict[str, Any]
    edited_report: Optional[Dict[str, Any]] = None
    explanations: Optional[Dict[str, Any]] = None
    ontology_mapping: Optional[Dict[str, Any]] = None
    user_feedback: Optional[Dict[str, Any]] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Radiology AI Assistant API", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "openai_configured": bool(OPENAI_API_KEY)
    }


@app.post("/api/generate-report")
async def generate_report(file: UploadFile = File(...)):
    """
    Generate enhanced radiology report from uploaded X-ray image.
    
    Returns:
        - JSON report with findings, ontology mapping, and explanations
    """
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # Load RadLex terms and CheXpert labels
        # Path relative to project root (parent of backend)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        radlex_path = os.path.join(project_root, "assets", "radlex_terms.json")
        radlex_terms = load_radlex_terms(radlex_path)
        chexpert_labels = simulate_chexpert_labels(file.filename or "uploaded_image.jpg")
        
        # Step 1: Generate JSON Report
        original_report = generate_json_report(
            image=image,
            api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL
        )
        
        # Step 2: Ontology Processing
        ontology_processor = OntologyProcessor(radlex_terms, chexpert_labels)
        mapped_findings = ontology_processor.map_findings_to_ontology(
            original_report.get("findings", [])
        )
        validation_results = ontology_processor.validate_findings(mapped_findings)
        ontology_stats = ontology_processor.get_ontology_statistics(mapped_findings)
        
        # Update report with mapped findings
        original_report["findings"] = mapped_findings
        ontology_mapping = {
            "validation": validation_results,
            "statistics": ontology_stats
        }
        
        # Step 3: Explainability
        explainability_engine = ExplainabilityEngine()
        explained_findings = explainability_engine.generate_explanations(mapped_findings)
        explanation_summary = explainability_engine.generate_summary_explanation(explained_findings)
        
        explanations = {
            "findings": explained_findings,
            "summary": explanation_summary
        }
        
        # Step 4: Apply Continuous Learning Rules
        learning_engine = ContinuousLearningEngine()
        improved_report = learning_engine.apply_rules_to_report(original_report)
        
        # Step 5: Calculate Accuracy Metrics
        from modules.report_evaluator import compare_labels_with_report
        from modules.json_report_generator import format_json_report_to_text
        
        # Get report text for comparison
        report_text = format_json_report_to_text(improved_report)
        
        # Compare with CheXpert labels
        matched_labels, missed_labels = compare_labels_with_report(
            chexpert_labels, 
            report_text, 
            radlex_terms
        )
        
        # Calculate accuracy
        total_labels = len(chexpert_labels)
        accuracy = len(matched_labels) / total_labels if total_labels > 0 else 1.0
        
        # Calculate additional metrics
        precision = len(matched_labels) / len(improved_report.get("findings", [])) if improved_report.get("findings") else 0
        recall = len(matched_labels) / total_labels if total_labels > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        accuracy_metrics = {
            "accuracy": round(accuracy, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1_score, 3),
            "matched_labels": matched_labels,
            "missed_labels": missed_labels,
            "total_labels": total_labels,
            "total_findings": len(improved_report.get("findings", []))
        }
        
        # Format text version (without structured report section)
        text_report = format_json_report_to_text(improved_report)
        
        # Automatically log the report generation for analytics
        try:
            from modules.feedback_logger import FeedbackLogger
            feedback_logger = FeedbackLogger()
            feedback_logger.log_feedback(
                image_name=file.filename or "uploaded_image.jpg",
                original_report=improved_report,
                edited_report=None,  # No edits yet
                explanations=explanations,
                ontology_mapping=ontology_mapping,
                user_feedback={},
                metadata={"auto_logged": True}
            )
        except Exception as log_error:
            # Don't fail the request if logging fails
            print(f"Warning: Failed to log report for analytics: {log_error}")
        
        return {
            "success": True,
            "report": improved_report,
            "text_report": text_report,
            "explanations": explanations,
            "ontology_mapping": ontology_mapping,
            "accuracy_metrics": accuracy_metrics,
            "image_name": file.filename or "uploaded_image.jpg"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@app.post("/api/save-feedback")
async def save_feedback(feedback: FeedbackRequest):
    """
    Save feedback for continuous learning.
    """
    try:
        # Validate that edited_report is provided if saving feedback
        if not feedback.edited_report:
            raise HTTPException(
                status_code=400, 
                detail="No edited report provided. Please make edits before saving."
            )
        
        feedback_logger = FeedbackLogger()
        
        entry = feedback_logger.log_feedback(
            image_name=feedback.image_name,
            original_report=feedback.original_report,
            edited_report=feedback.edited_report,
            explanations=feedback.explanations,
            ontology_mapping=feedback.ontology_mapping,
            user_feedback=feedback.user_feedback
        )
        
        return {
            "success": True,
            "message": "Feedback saved successfully",
            "entry_id": entry.get("timestamp"),
            "edit_count": entry.get("edit_count", 0),
            "has_edits": entry.get("has_edits", False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")


@app.get("/api/learning-stats")
async def get_learning_stats():
    """
    Get continuous learning statistics.
    """
    try:
        learning_engine = ContinuousLearningEngine()
        stats = learning_engine.get_learning_statistics()
        
        feedback_logger = FeedbackLogger()
        feedback_stats = feedback_logger.get_feedback_statistics()
        
        return {
            "success": True,
            "learning_stats": stats,
            "feedback_stats": feedback_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/api/rules")
async def get_rules():
    """
    Get mined rules from continuous learning.
    """
    try:
        learning_engine = ContinuousLearningEngine()
        rules = learning_engine.mine_rules()
        
        return {
            "success": True,
            "rules": rules,
            "count": len(rules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting rules: {str(e)}")


@app.get("/api/analytics")
async def get_analytics():
    """
    Get comprehensive analytics report.
    """
    try:
        from modules.analytics import AnalyticsEngine
        import os
        
        # Ensure analytics uses correct path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        feedback_log_path = os.path.join(project_root, "outputs", "feedback_logs.json")
        learning_data_path = os.path.join(project_root, "outputs", "learning_data.json")
        
        analytics_engine = AnalyticsEngine(
            feedback_log_path=feedback_log_path,
            learning_data_path=learning_data_path
        )
        report = analytics_engine.generate_analytics_report()
        
        return {
            "success": True,
            "analytics": report,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

