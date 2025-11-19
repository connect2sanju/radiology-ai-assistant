# Radiology AI Assistant

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)

An AI-powered radiology report generation system that analyzes chest X-ray images using OpenAI's GPT-4o vision model, generates structured medical reports with explainability, and implements continuous learning from user feedback.

## 🎯 Features

- **🤖 AI-Powered Analysis**: Automated chest X-ray analysis using GPT-4o vision model
- **📝 Structured Reports**: JSON-based reports with findings, impressions, and recommendations
- **🔍 Explainability**: Evidence chains and confidence scores for each finding
- **✏️ Editable Reports**: Human-in-the-loop corrections with change tracking
- **📊 Comprehensive Analytics**: Real-time statistics and performance monitoring
- **🧠 Continuous Learning**: Rule mining and model improvement from feedback
- **🏥 Medical Ontology**: RadLex and CheXpert integration for standardized terminology
- **💾 Feedback Logging**: Complete audit trail of original and edited reports

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- React 18+ with Vite
- Modern CSS with glassmorphism design
- Axios for API communication

**Backend:**
- FastAPI (Python 3.11+)
- OpenAI GPT-4o Vision API
- Uvicorn ASGI server

**Core Modules:**
- Report generation with structured JSON output
- Ontology processing (RadLex/CheXpert)
- Explainability engine
- Continuous learning system
- Analytics engine

### System Flow

```
User Upload → GPT-4o Analysis → JSON Report
                ↓
    Ontology Mapping (RadLex/CheXpert)
                ↓
    Explainability (Evidence Chains)
                ↓
    User Review & Edit
                ↓
    Feedback Logging → Continuous Learning
```

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18+ and npm
- **OpenAI API Key**: Required for GPT-4o access

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd radiology_ai_assistant\ v2
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env  # If available, or create .env manually
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_api_key_here
# OPENAI_MODEL=gpt-4o
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage

### Generating a Report

1. **Upload Image**: Click "Choose X-Ray Image" and select a chest X-ray (JPEG/PNG)
2. **Generate Report**: Click "🔬 Generate Radiology Report"
3. **Review Findings**: Navigate through tabs:
   - **📝 Report**: Clinical impression and recommendations
   - **🔍 Findings**: Detailed findings with confidence scores
   - **🧠 Explainability**: Evidence chains and reasoning
4. **Edit if Needed**: Click "✏️ Edit Report" to make corrections
5. **Save Feedback**: Click "💾 Save Changes" to log feedback for learning

### Viewing Analytics

- **Summary Statistics**: Always visible at the top of the page
- **Admin Dashboard**: Collapsible panel at the bottom with:
  - Operations breakdown (Automated vs Manual)
  - Activity by time period (Today/Week/Month)
  - Performance metrics
  - Manual intervention details

## 📁 Project Structure

```
radiology_ai_assistant v2/
├── backend/
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── main.jsx           # React entry point
│   │   └── index.css          # Styles
│   ├── package.json
│   └── vite.config.js
├── modules/
│   ├── json_report_generator.py    # GPT-4o report generation
│   ├── ontology_processor.py        # RadLex/CheXpert mapping
│   ├── explainability.py            # Evidence chains & confidence
│   ├── continuous_learning.py       # Rule mining & improvement
│   ├── feedback_logger.py           # Feedback storage
│   ├── analytics.py                  # Analytics engine
│   ├── chexpert_simulator.py        # CheXpert label simulation
│   ├── report_evaluator.py          # Accuracy evaluation
│   ├── radlex_loader.py             # RadLex term loading
│   └── mimic_cxr_loader.py          # MIMIC-CXR dataset loader
├── assets/
│   └── radlex_terms.json            # RadLex ontology terms
├── outputs/
│   ├── feedback_logs.json           # Feedback entries
│   └── learning_data.json            # Learning data
├── config.py                        # Configuration
├── requirements.txt                 # Python dependencies
├── PROJECT_REPORT.md                # Comprehensive project report
└── ARCHITECTURE.md                  # Architecture documentation
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
```

### Optional Assets

- `assets/radlex_terms.json`: RadLex medical terminology ontology
- `mimic-cxr.csv`: MIMIC-CXR dataset for validation (optional)

## 📊 API Endpoints

### POST `/api/generate-report`
Generate a radiology report from an uploaded X-ray image.

**Request:** Multipart form data with image file  
**Response:** JSON report with findings, explanations, and ontology mapping

### POST `/api/save-feedback`
Save user feedback and edited reports for continuous learning.

**Request:** JSON with original and edited reports  
**Response:** Success confirmation with edit count

### GET `/api/analytics`
Get comprehensive analytics and statistics.

**Response:** Analytics report with summary and admin dashboard data

### GET `/api/rules`
Get learned rules from the continuous learning system.

**Response:** List of learned rules and patterns

### GET `/api/health`
Health check endpoint.

**Response:** System status

Interactive API documentation available at `/docs` (Swagger UI).

## 🧪 Key Features Explained

### Explainability
Each finding includes:
- **Confidence Score**: 0-100% confidence level
- **Evidence Chain**: Visual and location-based evidence
- **Reasoning**: Human-readable explanation
- **Confidence Level**: High/Medium/Low classification

### Continuous Learning
The system learns from user feedback:
- **Rule Mining**: Identifies common correction patterns
- **Weak Classifier**: Applies learned rules to new reports
- **Model Improvement**: Accuracy improves over time

### Ontology Integration
- **RadLex Mapping**: Standardized medical terminology
- **CheXpert Validation**: Chest X-ray label validation
- **Term Standardization**: Consistent medical language

## 📈 Analytics

The system provides comprehensive analytics:

- **Summary Statistics**: Total reports, findings, images, edits
- **Operations Breakdown**: Automated vs manual operations
- **Time Period Stats**: Today, this week, this month
- **Performance Metrics**: Average confidence, findings per report
- **Manual Interventions**: Intervention tracking and history

## 🔒 Security & Privacy

- **API Keys**: Store securely in `.env` file (never commit)
- **Data Storage**: Currently uses JSON files (consider database for production)
- **CORS**: Configured for local development (update for production)
- **HIPAA Compliance**: Consider additional measures for production use

## 🚀 Deployment

### Production Considerations

1. **Backend**:
   - Use production ASGI server (Gunicorn with Uvicorn workers)
   - Set up reverse proxy (Nginx)
   - Configure HTTPS
   - Secure environment variables

2. **Frontend**:
   - Build production bundle: `npm run build`
   - Serve static files via Nginx or CDN
   - Configure CORS for production domain

3. **Database**:
   - Consider replacing JSON files with database
   - Implement proper backup strategies
   - Set up monitoring and logging

## 📚 Documentation

- **[PROJECT_REPORT.md](./PROJECT_REPORT.md)**: Comprehensive end-to-end project report
- **[ARCHITECTURE.md](./ARCHITECTURE.md)**: Detailed architecture documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o vision model
- RadLex for medical terminology ontology
- CheXpert for chest X-ray label standardization
- MIMIC-CXR dataset (optional, for validation)

## 📧 Contact

For questions, issues, or contributions, please open an issue in the repository.

---

**Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: 2024
