# Enhanced Radiology AI Assistant - Architecture

## Overview

The enhanced system implements a complete workflow with JSON reports, ontology processing, editable reports, explainability, feedback logging, and continuous learning.

**Frontend:** React (Vite) - Modern, responsive UI  
**Backend:** FastAPI - RESTful API server  
**AI Modules:** Python modules for report generation and processing

## Workflow

```
User Uploads X-ray
        ↓
GPT Vision Generates Initial Report (JSON)
        ↓
Ontology Processor (RadLex + CheXpert Mapping)
        ↓
Editable Report (Human-in-the-Loop Corrections)
        ↓
Explainability (Finding → Evidence → Confidence)
        ↓
Feedback Logged (Original + Edited + Explanations)
        ↓
Continuous Learning (Rule Mining + Weak Classifier)
        ↓
Model Improves Over Time
```

## Module Structure

### 1. JSON Report Generator (`modules/json_report_generator.py`)

**Purpose:** Generate structured JSON reports with findings, evidence, and confidence scores.

**Key Functions:**
- `generate_json_report()` - Generates JSON-structured report from image
- `format_json_report_to_text()` - Converts JSON to human-readable text
- `_normalize_report_structure()` - Validates and normalizes report structure

**Output Format:**
```json
{
  "findings": [
    {
      "finding": "Cardiomegaly",
      "location": "cardiac silhouette",
      "evidence": "Enlarged cardiac silhouette...",
      "confidence": 0.85,
      "severity": "moderate"
    }
  ],
  "impression": "Overall clinical interpretation",
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "metadata": {
    "image_quality": "adequate",
    "view": "PA"
  }
}
```

### 2. Ontology Processor (`modules/ontology_processor.py`)

**Purpose:** Process reports using RadLex and CheXpert ontologies for validation and mapping.

**Key Classes:**
- `OntologyProcessor` - Main processor class

**Key Methods:**
- `map_findings_to_ontology()` - Maps findings to standard terminology
- `validate_findings()` - Validates findings against ontology
- `suggest_standard_terms()` - Suggests standard terms
- `get_ontology_statistics()` - Gets ontology coverage statistics

**Features:**
- RadLex term mapping
- CheXpert label matching
- Confidence calculation for mappings
- Validation warnings and suggestions

### 3. Explainability Engine (`modules/explainability.py`)

**Purpose:** Provides finding → evidence → confidence explanations.

**Key Classes:**
- `ExplainabilityEngine` - Main explainability engine

**Key Methods:**
- `generate_explanations()` - Generates explanations for all findings
- `generate_summary_explanation()` - Creates overall summary
- `format_explanation_for_display()` - Formats for UI display

**Explanation Structure:**
- Confidence level (high/medium/low)
- Evidence chain (location, visual, confidence)
- Reasoning (human-readable explanation)
- Key evidence terms

### 4. Feedback Logger (`modules/feedback_logger.py`)

**Purpose:** Logs original reports, edited reports, explanations, and user feedback.

**Key Classes:**
- `FeedbackLogger` - Enhanced logger class

**Key Methods:**
- `log_feedback()` - Logs comprehensive feedback
- `get_feedback_statistics()` - Gets feedback statistics

**Log Structure:**
- Original report (JSON)
- Edited report (JSON)
- Explanations
- User feedback
- Ontology mapping
- Edit counts and patterns

### 5. Continuous Learning Engine (`modules/continuous_learning.py`)

**Purpose:** Implements rule mining and weak classifier for model improvement.

**Key Classes:**
- `ContinuousLearningEngine` - Learning engine class

**Key Methods:**
- `mine_rules()` - Mines rules from feedback data
- `apply_rules_to_report()` - Applies learned rules to new reports
- `train_weak_classifier()` - Trains weak classifier
- `get_learning_statistics()` - Gets learning statistics

**Rule Types:**
- Edit patterns (common corrections)
- Confidence adjustments (learned confidence corrections)
- Finding associations (co-occurring findings)

## Application Files

### React Frontend (`frontend/`)

Modern React application with Vite:
- Image upload and preview
- Tabbed interface (Findings, Explanations, Ontology)
- Editable report interface
- Real-time API communication
- **No structured report section** (removed as requested)

**Usage:**
```bash
cd frontend
npm install
npm run dev
```

### FastAPI Backend (`backend/main.py`)

RESTful API server:
- `/api/generate-report` - Generate reports from images
- `/api/save-feedback` - Save user feedback
- `/api/learning-stats` - Get learning statistics
- `/api/rules` - Get mined rules

**Usage:**
```bash
cd backend
python main.py
# Or: uvicorn main:app --reload
```

### Legacy Streamlit Apps

- `app_enhanced.py` - Enhanced Streamlit version (legacy)
- `app.py` - Original Streamlit version (legacy)

## Data Flow

1. **Image Upload** → PIL Image object
2. **JSON Generation** → Structured report with findings
3. **Ontology Processing** → Mapped findings with RadLex/CheXpert terms
4. **Explainability** → Findings with explanations
5. **User Editing** → Edited report (optional)
6. **Feedback Logging** → Saved to `outputs/feedback_logs.json`
7. **Learning Data** → Saved to `outputs/learning_data.json`
8. **Rule Mining** → Rules extracted from feedback
9. **Rule Application** → Rules applied to future reports

## File Structure

```
radiology_ai_assistant v2/
├── backend/
│   └── main.py               # FastAPI backend server
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Styles
│   ├── package.json
│   └── vite.config.js
├── app.py                    # Original Streamlit app (legacy)
├── app_enhanced.py           # Enhanced Streamlit app (legacy)
├── modules/
│   ├── json_report_generator.py    # JSON report generation
│   ├── ontology_processor.py        # Ontology processing
│   ├── explainability.py            # Explainability engine
│   ├── feedback_logger.py           # Enhanced feedback logging
│   ├── continuous_learning.py       # Continuous learning
│   ├── report_generator.py          # Original text generator
│   ├── radlex_loader.py              # RadLex loader
│   ├── chexpert_simulator.py         # CheXpert simulator
│   └── report_evaluator.py           # Report evaluator
├── outputs/
│   ├── feedback_logs.json           # Feedback logs
│   ├── learning_data.json            # Learning data
│   └── logs.json                     # Original logs
└── assets/
    └── radlex_terms.json             # RadLex terminology
```

## Usage

### Running the React Application

#### Backend (Terminal 1)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run FastAPI server
cd backend
python main.py
# Backend runs on http://localhost:8000
```

#### Frontend (Terminal 2)
```bash
# Install Node.js dependencies
cd frontend
npm install

# Run React development server
npm run dev
# Frontend runs on http://localhost:3000
```

### Workflow Steps

1. **Upload Image** - User uploads X-ray image via React UI
2. **Generate Report** - Click "Generate Enhanced Report" (API call to backend)
3. **Review Findings** - View structured findings with confidence scores in Findings tab
4. **Check Explanations** - Review evidence chains and reasoning in Explanations tab
5. **View Ontology** - See RadLex/CheXpert mappings in Ontology tab
6. **Edit Report** - Enable editing and make corrections
7. **Save Feedback** - Click "Save Feedback" to log for continuous learning

**Note:** The structured report section has been removed from the UI as requested.

## Continuous Learning

The system learns from user feedback:

1. **Rule Mining** - Extracts patterns from edits
2. **Confidence Adjustment** - Learns confidence corrections
3. **Finding Associations** - Identifies co-occurring findings
4. **Weak Classifier** - Trains simple classifier on patterns
5. **Rule Application** - Applies learned rules to new reports

## Future Enhancements

- Integration with actual CheXpert model (currently simulated)
- Advanced ML models for confidence prediction
- Multi-user feedback aggregation
- Real-time rule updates
- Model versioning and A/B testing

