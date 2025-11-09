# Quick Start Guide

## 5-Minute Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create directories
python setup.py

# 3. Run the application
python main.py

# 4. Open browser
# Navigate to: http://localhost:5000
```

## Demo Workflow

### Step 1: Generate Test Data
1. Click "Generate Test Data" on Dashboard
2. Creates 200 synthetic providers with realistic errors

### Step 2: Run Batch Validation
1. Go to "Validation" page
2. Click "Start Batch Validation"
3. Watch progress (processes 200 providers)
4. View results with confidence scores

### Step 3: Review Quality
1. Go to "Quality Assessment" page
2. Click "Run Quality Assessment"
3. View metrics and prioritized review list

### Step 4: Generate Report
1. Go to "Reports" page
2. Click "PDF" button on any batch
3. Download validation report

## Key Features to Demo

### Flow 1: Automated Contact Validation
- **What**: Validates 200 providers automatically
- **Time**: Under 5 minutes
- **Result**: Confidence scores, discrepancy flags, validation report

### Flow 2: PDF Extraction
- **What**: Upload scanned PDF, extract structured data
- **Accuracy**: 85%+ with VLM, 70%+ with OCR
- **Use Case**: New provider onboarding

###  Flow 3: Quality Assessment
- **What**: Assesses entire directory quality
- **Output**: Metrics, prioritized review list, recommendations

## API Keys (Optional)

The system works without API keys but with limited functionality:

- **No OpenAI Key**: PDF extraction uses OCR (lower accuracy)
- **No Google Maps Key**: Location verification skipped
- **NPI API**: Free, no key needed

## Troubleshooting

### Port Already in Use
```bash
# Change port in main.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database Errors
```bash
# Delete database and restart
rm provider_directory.db
python main.py
```

### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

## Performance Metrics

- **200 providers validated in < 5 minutes**
-  **80%+ validation accuracy**
-  **85%+ PDF extraction accuracy**
-  **500+ providers/hour throughput**

## Next Steps

1. Review `ARCHITECTURE.md` for system design
2. Check `README.md` for detailed documentation
3. Run `python demo.py` to see all flows
4. Explore the web interface at `http://localhost:5000`

