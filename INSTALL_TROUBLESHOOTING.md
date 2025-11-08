# Installation Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: NumPy/Pandas Compilation Error (GCC Version)

**Error**: `NumPy requires GCC >= 8.4` but system has older GCC

**Solution 1: Use Pre-built Wheels (Recommended)**
```bash
# Install using pip with --only-binary flag
pip install --only-binary :all: -r requirements.txt
```

**Solution 2: Install Minimal Requirements First**
```bash
# Install core packages first
pip install -r requirements-minimal.txt

# Then install pandas/numpy separately (they should use pre-built wheels)
pip install pandas numpy
```

**Solution 3: Use Conda (If Available)**
```bash
# Conda has pre-compiled packages
conda install pandas numpy -c conda-forge
pip install -r requirements.txt --no-deps
pip install -r requirements.txt --no-deps  # Install remaining packages
```

**Solution 4: Update pip and use latest versions**
```bash
# Update pip first
python -m pip install --upgrade pip

# Try installing with --upgrade flag
pip install --upgrade -r requirements.txt
```

### Issue 2: Port Already in Use

**Error**: `Address already in use`

**Solution**:
```python
# Edit main.py, change port
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Issue 3: Database Locked

**Error**: `database is locked`

**Solution**:
```bash
# Delete database and restart
rm provider_directory.db  # Linux/Mac
del provider_directory.db  # Windows
python main.py
```

### Issue 4: Missing System Dependencies

**For PDF Processing (pdf2image)**:
- **Windows**: Install Poppler from https://github.com/oschwartz10612/poppler-windows/releases
- **Mac**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

**For OCR (pytesseract)**:
- **Windows**: Install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### Issue 5: Import Errors After Installation

**Solution**: Verify installation
```bash
# Check if packages are installed
pip list | grep flask
pip list | grep pandas

# Reinstall if needed
pip install --force-reinstall flask pandas
```

### Issue 6: SSL Certificate Errors

**Solution**:
```bash
# Update certificates
pip install --upgrade certifi

# Or use trusted hosts
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## Step-by-Step Installation for Windows

1. **Update pip**:
```bash
python -m pip install --upgrade pip
```

2. **Install core packages first**:
```bash
pip install flask flask-cors sqlalchemy flask-sqlalchemy requests beautifulsoup4
```

3. **Install data processing packages** (use pre-built wheels):
```bash
pip install pandas numpy --only-binary :all:
```

4. **Install remaining packages**:
```bash
pip install -r requirements.txt
```

## Alternative: Install Without Optional Dependencies

If you only need core functionality:

```bash
# Install minimal requirements
pip install -r requirements-minimal.txt

# The system will work but with limited features:
# - No PDF extraction (needs pdf2image, pillow, pytesseract)
# - No advanced ML features (needs scikit-learn)
# - No plotting (needs matplotlib)
# - Synthetic data generator will work (needs faker only)
```

## Verify Installation

```bash
# Test imports
python -c "import flask; print('Flask OK')"
python -c "import pandas; print('Pandas OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK')"
```

## Getting Help

If issues persist:
1. Check Python version: `python --version` (should be 3.9+)
2. Check pip version: `pip --version`
3. Try creating a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

