"""
JSON Report Generator Module
Generates structured radiology reports in JSON format with findings, evidence, and confidence scores.
"""
import json
import base64
from io import BytesIO
from typing import Optional, Callable, Dict, List, Any
from PIL import Image


def encode_image(image: Image.Image, max_size: int = 512) -> str:
    """
    Convert PIL Image to a resized base64 string for OpenAI vision models.
    """
    width, height = image.size
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    buffered = BytesIO()
    image.save(buffered, format="JPEG", quality=80, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def generate_json_report(
    image: Image.Image,
    api_key: str,
    model_name: str = "gpt-4o",
    temperature: float = 0.2,
    max_tokens: int = 2048,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """
    Generate a structured radiology report in JSON format using OpenAI GPT model with vision support.
    
    Returns a dictionary with:
    - findings: List of findings with evidence and confidence
    - impression: Overall clinical impression
    - recommendations: Clinical recommendations
    - metadata: Report metadata
    """
    if not api_key:
        raise ValueError("OPENAI_API_KEY is required to generate a radiology report.")

    try:
        from openai import OpenAI, OpenAIError, RateLimitError
    except ImportError as exc:
        raise ImportError("OpenAI library not installed. Run: pip install openai") from exc

    img_b64 = encode_image(image)
    client = OpenAI(api_key=api_key)

    if progress_callback:
        progress_callback("Generating structured JSON report with OpenAI GPT model...")

    # System prompt for JSON-structured output
    system_prompt = """You are a senior radiologist. Analyze the chest X-ray image and generate a structured JSON report.

The report must follow this exact JSON schema:
{
  "findings": [
    {
      "finding": "string (e.g., 'Cardiomegaly', 'Pleural Effusion')",
      "location": "string (e.g., 'right lower lobe', 'bilateral')",
      "evidence": "string (detailed description of visual evidence)",
      "confidence": float (0.0 to 1.0, where 1.0 is highest confidence),
      "severity": "string (e.g., 'mild', 'moderate', 'severe')"
    }
  ],
  "impression": "string (overall clinical interpretation)",
  "recommendations": [
    "string (clinical recommendation 1)",
    "string (clinical recommendation 2)"
  ],
  "metadata": {
    "image_quality": "string (e.g., 'adequate', 'suboptimal')",
    "view": "string (e.g., 'PA', 'AP', 'lateral')",
    "technique": "string (brief description)"
  }
}

Important:
- Each finding must include specific visual evidence from the image
- Confidence scores should reflect certainty based on image clarity and findings
- Use standard radiological terminology
- Return ONLY valid JSON, no additional text"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ],
                },
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"} if "gpt-4" in model_name.lower() or "o1" in model_name.lower() else None,
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            report_json = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            report_json = json.loads(response_text)
        
        # Validate and normalize structure
        return _normalize_report_structure(report_json)
        
    except RateLimitError as e:
        raise RuntimeError(
            "OpenAI API reported 'insufficient_quota' or rate limiting. "
            "Please check your OpenAI plan/billing status or wait before retrying."
        ) from e
    except OpenAIError as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response from model: {e}\nResponse: {response_text[:500]}") from e


def _normalize_report_structure(report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and validate the report structure to ensure all required fields exist.
    """
    normalized = {
        "findings": [],
        "impression": "",
        "recommendations": [],
        "metadata": {}
    }
    
    # Normalize findings
    if "findings" in report and isinstance(report["findings"], list):
        for finding in report["findings"]:
            if isinstance(finding, dict):
                normalized_finding = {
                    "finding": finding.get("finding", ""),
                    "location": finding.get("location", ""),
                    "evidence": finding.get("evidence", ""),
                    "confidence": float(finding.get("confidence", 0.5)),
                    "severity": finding.get("severity", "unknown")
                }
                normalized["findings"].append(normalized_finding)
    
    # Normalize impression
    normalized["impression"] = report.get("impression", "")
    
    # Normalize recommendations
    if "recommendations" in report:
        if isinstance(report["recommendations"], list):
            normalized["recommendations"] = report["recommendations"]
        elif isinstance(report["recommendations"], str):
            normalized["recommendations"] = [report["recommendations"]]
    
    # Normalize metadata
    if "metadata" in report and isinstance(report["metadata"], dict):
        normalized["metadata"] = report["metadata"]
    
    return normalized


def format_json_report_to_text(report_json: Dict[str, Any]) -> str:
    """
    Convert JSON report to human-readable text format.
    """
    text = "=== RADIOLOGY REPORT ===\n\n"
    
    # Findings
    text += "FINDINGS:\n"
    if report_json.get("findings"):
        for i, finding in enumerate(report_json["findings"], 1):
            text += f"\n{i}. {finding.get('finding', 'Unknown')}"
            if finding.get('location'):
                text += f" - Location: {finding['location']}"
            if finding.get('severity'):
                text += f" - Severity: {finding['severity']}"
            text += f"\n   Confidence: {finding.get('confidence', 0):.1%}"
            if finding.get('evidence'):
                text += f"\n   Evidence: {finding['evidence']}"
            text += "\n"
    else:
        text += "No significant findings detected.\n"
    
    # Impression
    text += "\nIMPRESSION:\n"
    text += report_json.get("impression", "No impression provided.") + "\n"
    
    # Recommendations
    if report_json.get("recommendations"):
        text += "\nRECOMMENDATIONS:\n"
        for i, rec in enumerate(report_json["recommendations"], 1):
            text += f"{i}. {rec}\n"
    
    # Metadata
    if report_json.get("metadata"):
        text += "\nMETADATA:\n"
        for key, value in report_json["metadata"].items():
            text += f"- {key}: {value}\n"
    
    return text

