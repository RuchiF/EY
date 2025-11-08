# Provider Data Validation and Directory Management Agent

An AI-powered system for automating healthcare provider data validation, credential verification, and directory management for healthcare payers.

## Features

- **Automated Data Validation**: Web scraping and API integration for contact information verification
- **Credential Verification**: Cross-reference with NPI registry and state licensing boards
- **PDF Processing**: VLM-based extraction from unstructured/scanned PDFs
- **Quality Assurance**: Confidence scoring and discrepancy detection
- **Directory Management**: Automated updates and report generation
- **Interactive Dashboard**: Web-based UI for monitoring and managing provider data

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── routes.py          # Flask routes
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS files
├── agents/
│   ├── __init__.py
│   ├── data_validation_agent.py
│   ├── enrichment_agent.py
│   ├── quality_assurance_agent.py
│   └── directory_management_agent.py
├── services/
│   ├── __init__.py
│   ├── npi_service.py
│   ├── pdf_extractor.py
│   ├── web_scraper.py
│   └── synthetic_data.py
├── config.py
├── main.py
└── requirements.txt
```

## Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables (optional):**
   - Create a `.env` file in the project root
   - Add your API keys (optional - system works without them but with limited functionality):
```
OPENAI_API_KEY=your_openai_key
GOOGLE_MAPS_API_KEY=your_google_maps_key
NPI_API_KEY=your_npi_key
```

4. **Run setup script to create directories:**
```bash
python setup.py
```

5. **Run the application:**
```bash
python main.py
```

6. **Access the dashboard:**
   - Open your browser and navigate to `http://localhost:5000`

### Quick Start Demo

Run the demo script to see the system in action:
```bash
python demo.py
```

This will demonstrate all three key flows:
- Flow 1: Automated Provider Contact Validation
- Flow 2: New Provider Credential Verification
- Flow 3: Directory Quality Assessment

## Key Features

### Flow 1: Automated Provider Contact Validation
- Validates 200 provider profiles automatically
- Cross-references with NPI registry and web sources
- Generates confidence scores and action reports

### Flow 2: New Provider Credential Verification
- Processes credential applications
- Verifies licenses and certifications
- Generates onboarding reports

### Flow 3: Directory Quality Assessment
- Weekly assessment of entire directory
- Identifies data gaps and inconsistencies
- Prioritizes providers for manual review

## Target KPIs

- **Validation Accuracy**: 80%+ success rate
- **Processing Speed**: 100 providers in under 5 minutes
- **PDF Extraction**: 85%+ accuracy with 95% confidence
- **Throughput**: 500+ validations per hour

## Technologies

- **Python 3.9+** - Core programming language
- **Flask** - Web framework for the dashboard
- **SQLAlchemy** - Database ORM for data management
- **OpenAI API** - Vision Language Model for PDF extraction
- **BeautifulSoup / Requests** - Web scraping for provider websites
- **NPI Registry API** - CMS provider verification
- **ReportLab** - PDF report generation
- **Bootstrap 5** - Modern UI framework

## Key Features Implemented

### ✅ Data Validation Agent
- Automated web scraping of provider practice websites
- Cross-referencing with NPI registry
- Phone number and address validation
- Confidence scoring for each data element

### ✅ Information Enrichment Agent
- Searches public sources for additional provider information
- Analyzes provider websites for updated practice information
- Identifies network gaps
- Creates standardized provider profiles

### ✅ Quality Assurance Agent
- Compares provider information across multiple sources
- Flags providers with suspicious information
- Tracks data quality metrics
- Prioritizes providers for manual verification

### ✅ Directory Management Agent
- Generates updated provider directory entries
- Creates automated alerts
- Produces summary reports
- Manages workflow queues for human reviewers

### ✅ PDF Extraction
- VLM-based extraction from scanned PDFs
- OCR fallback for unstructured documents
- 85%+ accuracy target with 95% confidence scoring

## Usage Examples

### Generate Synthetic Test Data
1. Go to Dashboard
2. Click "Generate Test Data" button
3. System creates 200 synthetic provider profiles with realistic errors

### Run Batch Validation
1. Navigate to Validation page
2. Click "Start Batch Validation"
3. System validates 200 providers automatically
4. View results and download reports

### Upload and Extract PDF
1. Go to Providers page
2. Click "Upload PDF"
3. Select a provider document (PDF)
4. System extracts structured data automatically
5. Review and add to directory

### Quality Assessment
1. Navigate to Quality Assessment page
2. Click "Run Quality Assessment"
3. View overall metrics and prioritized review list
4. Export reports for management

## API Endpoints

- `GET /api/providers` - List providers
- `POST /api/providers` - Create provider
- `GET /api/providers/<id>` - Get provider details
- `POST /api/providers/<id>/validate` - Validate single provider
- `POST /api/batch/validate` - Run batch validation
- `GET /api/batch/<id>` - Get batch details
- `POST /api/quality/assess` - Run quality assessment
- `GET /api/quality/prioritize` - Get prioritized review list
- `POST /api/upload/pdf` - Upload and extract PDF
- `POST /api/synthetic/generate` - Generate synthetic data

## Performance Targets

- ✅ **Validation Accuracy**: 80%+ success rate
- ✅ **Processing Speed**: 100 providers in under 5 minutes
- ✅ **PDF Extraction**: 85%+ accuracy with 95% confidence
- ✅ **Throughput**: 500+ validations per hour

## Project Structure

```
.
├── app/                    # Flask application
│   ├── models.py          # Database models
│   ├── routes.py          # API routes and views
│   └── templates/         # HTML templates
├── agents/                 # AI agents
│   ├── data_validation_agent.py
│   ├── enrichment_agent.py
│   ├── quality_assurance_agent.py
│   └── directory_management_agent.py
├── services/               # External services
│   ├── npi_service.py
│   ├── pdf_extractor.py
│   ├── web_scraper.py
│   └── synthetic_data.py
├── config.py              # Configuration
├── main.py                # Application entry point
├── demo.py                # Demo script
└── requirements.txt       # Dependencies
```

## Notes

- The system works without API keys but with limited functionality
- NPI Registry API is free and doesn't require authentication
- Google Maps API requires API key for location verification
- OpenAI API key needed for VLM-based PDF extraction (falls back to OCR if not available)
- All data is stored in SQLite database by default (can be changed to PostgreSQL)

