# Feature Checklist - What to Test in the App

## 🚀 Quick Start
1. Run the application: `python main.py`
2. Open browser: `http://localhost:5000`
3. You should see the Dashboard

---

## 📊 DASHBOARD (Home Page)

### ✅ Statistics Cards
- [ ] **Total Providers** - Shows count of all providers
- [ ] **Validated** - Count of validated providers (green)
- [ ] **Needs Review** - Count requiring review (yellow)
- [ ] **Pending** - Count pending validation (blue)
- [ ] **Percentage calculations** - Shows % for each status

### ✅ Quick Actions
- [ ] **Generate Test Data** button
  - Click to create 200 synthetic providers
  - Should show success message
  - Dashboard stats should update

- [ ] **Start Batch Validation** button
  - Validates all pending providers
  - Shows progress (if implemented)
  - Updates statistics after completion

- [ ] **Run Quality Assessment** button
  - Analyzes all providers
  - Shows quality metrics
  - Redirects to Quality page

- [ ] **View Prioritized Review List** button
  - Shows providers needing review
  - Redirects to Quality page

### ✅ Recent Batches Table
- [ ] **Batch Name** - Shows batch identifier
- [ ] **Total/Processed/Validated/Needs Review** columns
- [ ] **Status badges** - Color-coded (green/yellow/gray)
- [ ] **View button** - Links to Reports page

---

## 👥 PROVIDERS PAGE

### ✅ Provider List
- [ ] **Table display** - Shows all providers in table format
- [ ] **Pagination** - Navigate between pages (if >20 providers)
- [ ] **Status filter dropdown** - Filter by:
  - All
  - Pending
  - Validated
  - Needs Review

### ✅ Provider Information Displayed
- [ ] **Name** - First name, last name
- [ ] **Practice Name** - If available
- [ ] **NPI** - National Provider Identifier
- [ ] **Specialty** - Medical specialty
- [ ] **Phone** - Contact phone
- [ ] **City, State** - Location
- [ ] **Status badge** - Color-coded status

### ✅ Actions on Each Provider
- [ ] **View button** (eye icon)
  - Opens provider details modal
  - Shows full provider information
  - Displays validation results
  - Shows confidence scores

- [ ] **Validate button** (check icon)
  - Validates single provider
  - Shows success message
  - Updates provider status
  - Refreshes provider list

### ✅ Add Provider
- [ ] **Add Provider button** - Opens modal
- [ ] **Form fields**:
  - First Name* (required)
  - Last Name* (required)
  - Middle Name
  - NPI
  - Specialty
  - Practice Name
  - Phone
  - Email
  - Address Line 1
  - City
  - State
  - Zip Code
- [ ] **Submit** - Creates provider, shows success, refreshes list

### ✅ Upload PDF
- [ ] **Upload PDF button** - Opens upload modal
- [ ] **File selection** - Choose PDF file
- [ ] **Use VLM checkbox** - Toggle VLM extraction
- [ ] **Upload & Extract** - Processes PDF
- [ ] **Extracted data** - Shows in console/logs
- [ ] **Auto-populate form** - Fills Add Provider form with extracted data

---

## ✅ VALIDATION PAGE

### ✅ Batch Validation
- [ ] **Description text** - Explains what validation does
- [ ] **Start Batch Validation button**
  - Processes 200 providers
  - Shows progress indicator
  - Displays results after completion

### ✅ Validation Results Display
- [ ] **Success message** - Shows completion status
- [ ] **Statistics shown**:
  - Processed count
  - Validated count
  - Needs Review count
  - Average Confidence
  - Processing Time
- [ ] **View Detailed Report link** - Links to Reports page

### ✅ Progress Indicator
- [ ] **Progress bar** - Shows validation progress (if implemented)
- [ ] **Status text** - "Initializing...", "Processing...", etc.

---

## 📈 QUALITY ASSESSMENT PAGE

### ✅ Overall Quality Metrics
- [ ] **Run Quality Assessment button**
  - Analyzes all providers
  - Updates metrics display

### ✅ Metrics Cards:
- [ ] **Total Providers** - Count card
- [ ] **Validated** - Count and percentage
- [ ] **Needs Review** - Count
- [ ] **Average Confidence** - Percentage score

### ✅ Statistics Display
- [ ] **Total Discrepancies** - Number found
- [ ] **Total Issues** - Count of issues
- [ ] **Average Quality Score** - Overall score

### ✅ Prioritized Review List
- [ ] **Load Prioritized Providers button**
  - Generates prioritized list
  - Displays in table format

### ✅ Prioritized Table Columns
- [ ] **Priority** - Rank number with badge
- [ ] **Provider Name** - Full name
- [ ] **Specialty** - Medical specialty
- [ ] **Status** - Current status badge
- [ ] **Confidence** - Percentage score
- [ ] **Issues** - Count of issues

---

## 📄 REPORTS PAGE

### ✅ Validation Batches Table
- [ ] **Batch Name** - Identifier
- [ ] **Total Providers** - Count
- [ ] **Processed** - Number processed
- [ ] **Validated** - Number validated
- [ ] **Needs Review** - Count needing review
- [ ] **Average Confidence** - Percentage
- [ ] **Status** - Color-coded badge
- [ ] **Actions**:
  - [ ] **PDF Download** - Downloads report PDF
  - [ ] **Details** - Opens batch details modal

### ✅ Batch Details Modal
- [ ] **Batch Information** - All batch details
- [ ] **Statistics table** - Complete metrics
- [ ] **Providers Needing Review** - List of providers

---

## 🔍 DETAILED FEATURES TO TEST

### 1. Provider Details Modal
**How to access**: Click eye icon on any provider

**What to check**:
- [ ] Provider Information section:
  - Name, NPI, Specialty, Practice
  - Phone, Email, Address
- [ ] Validation Results section:
  - Field name
  - Confidence score (percentage)
  - Status (validated/discrepancy)
- [ ] **If no validations**: Shows "No validation results yet"

### 2. Single Provider Validation
**How to test**: Click check icon on a provider

**What happens**:
- [ ] Confirmation dialog appears
- [ ] Validation runs (may take a few seconds)
- [ ] Success message displayed
- [ ] Provider status updates
- [ ] Page refreshes with updated data

### 3. Batch Validation Process
**How to test**: 
1. Generate test data first (200 providers)
2. Go to Validation page
3. Click "Start Batch Validation"

**What to observe**:
- [ ] Progress indicator appears
- [ ] Processing happens (may take 1-2 minutes)
- [ ] Results displayed:
  - Processed: 200
  - Validated: X number
  - Needs Review: Y number
  - Average Confidence: Z%
  - Processing Time: ~X seconds

### 4. PDF Extraction
**How to test**:
1. Go to Providers page
2. Click "Upload PDF"
3. Select a PDF file (or create a test PDF)
4. Check "Use VLM" if you have OpenAI API key
5. Click "Upload & Extract"

**What to check**:
- [ ] Success message with confidence score
- [ ] Extracted data shown (in alert or console)
- [ ] Add Provider form auto-populated
- [ ] Can review and edit before submitting

### 5. Quality Assessment
**How to test**:
1. Go to Quality Assessment page
2. Click "Run Quality Assessment"

**What to check**:
- [ ] Metrics cards update with:
  - Total Providers
  - Validated count and percentage
  - Needs Review count
  - Average Confidence
- [ ] Statistics section shows:
  - Total Discrepancies
  - Total Issues
  - Average Quality Score

### 6. Prioritized Review List
**How to test**:
1. Go to Quality Assessment page
2. Click "Load Prioritized Providers"

**What to check**:
- [ ] Table displays providers
- [ ] Sorted by priority (highest first)
- [ ] Shows:
  - Priority rank (#1, #2, etc.)
  - Provider name and specialty
  - Status badge
  - Confidence percentage
  - Number of issues

---

## 🎯 TESTING SCENARIOS

### Scenario 1: Complete Workflow
1. [ ] **Start Fresh**: Clear database or start new
2. [ ] **Generate Data**: Create 200 test providers
3. [ ] **Run Validation**: Validate all providers
4. [ ] **Check Results**: Review validation results
5. [ ] **Quality Assessment**: Run quality check
6. [ ] **Review Prioritized**: Check prioritized list
7. [ ] **Generate Report**: Download PDF report

### Scenario 2: Single Provider
1. [ ] **Add Provider**: Manually add one provider
2. [ ] **View Details**: Check provider information
3. [ ] **Validate**: Run validation on single provider
4. [ ] **Check Results**: See validation results
5. [ ] **Generate Email**: Get email template (if implemented)

### Scenario 3: PDF Processing
1. [ ] **Upload PDF**: Upload a provider document
2. [ ] **Extract Data**: See extracted information
3. [ ] **Review Data**: Check accuracy
4. [ ] **Add to Directory**: Submit provider

### Scenario 4: Data Quality
1. [ ] **Generate Data**: Create providers with errors
2. [ ] **Run Assessment**: Check quality metrics
3. [ ] **View Issues**: See what needs fixing
4. [ ] **Prioritize**: Check prioritized list
5. [ ] **Take Action**: Validate or update providers

---

## 🔧 TECHNICAL FEATURES TO VERIFY

### Database Operations
- [ ] **Provider Creation**: New providers saved to database
- [ ] **Status Updates**: Provider status changes persist
- [ ] **Validation Results**: Results saved and retrievable
- [ ] **Batch Tracking**: Batches created and tracked

### API Endpoints (Check Browser Console/Network Tab)
- [ ] `GET /api/providers` - Returns provider list
- [ ] `POST /api/providers` - Creates new provider
- [ ] `GET /api/providers/<id>` - Gets single provider
- [ ] `POST /api/providers/<id>/validate` - Validates provider
- [ ] `POST /api/batch/validate` - Runs batch validation
- [ ] `GET /api/batch/<id>` - Gets batch details
- [ ] `POST /api/quality/assess` - Runs quality assessment
- [ ] `GET /api/quality/prioritize` - Gets prioritized list
- [ ] `POST /api/upload/pdf` - Uploads and extracts PDF
- [ ] `POST /api/synthetic/generate` - Generates test data

### UI/UX Features
- [ ] **Responsive Design**: Works on different screen sizes
- [ ] **Loading States**: Shows loading indicators
- [ ] **Error Handling**: Displays error messages
- [ ] **Success Messages**: Confirms successful actions
- [ ] **Modal Dialogs**: Opens and closes properly
- [ ] **Form Validation**: Required fields enforced
- [ ] **Navigation**: All menu links work
- [ ] **Status Badges**: Color-coded correctly

---

## 📱 RESPONSIVE FEATURES

### Desktop View
- [ ] **Sidebar Navigation**: Visible and functional
- [ ] **Table Layout**: Providers displayed in table
- [ ] **Modal Dialogs**: Properly sized and centered
- [ ] **Statistics Cards**: 4 cards in a row

### Mobile View (if applicable)
- [ ] **Responsive Layout**: Adapts to smaller screens
- [ ] **Touch-Friendly**: Buttons and links easy to tap
- [ ] **Readable Text**: Font sizes appropriate

---

## 🐛 ERROR SCENARIOS TO TEST

### Missing Data
- [ ] **Empty Database**: App handles no providers gracefully
- [ ] **Missing Fields**: Forms handle optional fields
- [ ] **Invalid Input**: Form validation works

### API Failures
- [ ] **NPI API Down**: System handles gracefully (shows error or uses fallback)
- [ ] **Network Issues**: Error messages displayed
- [ ] **Invalid PDF**: Error message for bad files

### Edge Cases
- [ ] **Very Long Names**: Text displays properly
- [ ] **Special Characters**: Handled correctly
- [ ] **Large Batches**: System handles 200+ providers
- [ ] **Concurrent Requests**: Multiple validations (if applicable)

---

## 📊 METRICS TO OBSERVE

### Performance Metrics
- [ ] **Page Load Time**: Dashboard loads quickly
- [ ] **Validation Speed**: 200 providers in ~5 minutes
- [ ] **PDF Extraction**: Completes in reasonable time
- [ ] **Database Queries**: Fast response times

### Accuracy Metrics
- [ ] **Validation Accuracy**: Check confidence scores
- [ ] **PDF Extraction**: Verify extracted data accuracy
- [ ] **Status Updates**: Correct status assignments

---

## ✅ QUICK TEST CHECKLIST (5 Minutes)

If you only have 5 minutes, test these essential features:

1. [ ] **Dashboard loads** - See statistics
2. [ ] **Generate test data** - Creates 200 providers
3. [ ] **View providers** - See provider list
4. [ ] **View provider details** - Click eye icon
5. [ ] **Run batch validation** - Process providers
6. [ ] **Check results** - See validation outcomes
7. [ ] **Quality assessment** - Run quality check
8. [ ] **Download report** - Get PDF report

---

## 🎬 DEMO FLOW (For Presentation)

### Recommended Demo Sequence:

1. **Show Dashboard** (30 sec)
   - Point out statistics
   - Explain current state

2. **Generate Test Data** (30 sec)
   - Click "Generate Test Data"
   - Show 200 providers created
   - Statistics update

3. **Run Batch Validation** (2 min)
   - Go to Validation page
   - Start batch validation
   - Show progress (if available)
   - Display results

4. **Show Provider Details** (1 min)
   - Go to Providers page
   - Click on a provider
   - Show validation results
   - Point out confidence scores

5. **Quality Assessment** (1 min)
   - Go to Quality page
   - Run assessment
   - Show metrics
   - Display prioritized list

6. **Generate Report** (30 sec)
   - Go to Reports page
   - Download PDF report
   - Show report contents

**Total Demo Time**: ~6 minutes

---

## 💡 TIPS FOR TESTING

1. **Start Fresh**: Clear database before major tests
2. **Use Test Data**: Generate synthetic data for consistent testing
3. **Check Console**: Browser console shows API calls and errors
4. **Network Tab**: Monitor API requests and responses
5. **Take Screenshots**: Capture results for documentation
6. **Note Issues**: Document any bugs or unexpected behavior

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: No providers showing
**Solution**: Generate test data first

### Issue: Validation not working
**Solution**: Check browser console for errors, verify NPI API is accessible

### Issue: PDF extraction fails
**Solution**: Ensure PDF file is valid, check if Poppler is installed (for pdf2image)

### Issue: Slow performance
**Solution**: Normal for batch validation (200 providers takes time), check database size

### Issue: Page not loading
**Solution**: Check if Flask app is running, verify port 5000 is available

---

## 📝 NOTES

- All features are functional but some may have limitations without API keys
- NPI API is free and works without authentication
- PDF extraction works better with OpenAI API key (VLM) but has OCR fallback
- Google Maps API is optional for location verification
- System works in demo mode without all API keys

---

**Happy Testing! 🎉**

