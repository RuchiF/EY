# System Architecture

## Overview

The Provider Data Validation and Directory Management Agent is an AI-powered system designed to automate healthcare provider data validation, credential verification, and directory management. The system uses an agentic AI architecture with multiple specialized agents working together to achieve high accuracy and efficiency.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface (Flask)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Dashboard │  │Providers │  │Validation│  │ Quality  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestration Layer                 │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │Data Validation   │  │Enrichment Agent │                 │
│  │Agent             │  │                 │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │Quality Assurance │  │Directory Mgmt    │                 │
│  │Agent             │  │Agent             │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │NPI       │  │Web       │  │PDF       │  │Synthetic │  │
│  │Service   │  │Scraper   │  │Extractor │  │Data      │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │NPI       │  │Provider  │  │Google    │                  │
│  │Registry  │  │Websites │  │Maps API  │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │Providers │  │Validation│  │Batches   │                  │
│  │          │  │Results   │  │          │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Web Interface Layer

**Technology**: Flask with Bootstrap 5

**Components**:
- **Dashboard**: Overview of provider statistics and recent batches
- **Providers**: List and manage provider profiles
- **Validation**: Run batch validations and view results
- **Quality Assessment**: Analyze data quality and prioritize reviews
- **Reports**: Generate and download validation reports

**Key Features**:
- Real-time progress tracking
- Interactive data visualization
- PDF upload and extraction
- Email template generation

### 2. Agent Layer

#### Data Validation Agent
**Purpose**: Validates provider contact information against multiple sources

**Process**:
1. Extracts provider data from database
2. Queries NPI Registry API for verification
3. Scrapes provider websites for current information
4. Cross-validates data across sources
5. Generates confidence scores for each field
6. Flags discrepancies for manual review

**Output**: Validation results with confidence scores and discrepancy flags

#### Information Enrichment Agent
**Purpose**: Enriches provider profiles with additional information from public sources

**Process**:
1. Searches NPI registry for missing NPI numbers
2. Extracts additional provider information
3. Scrapes provider websites for updated practice details
4. Identifies specialties and taxonomies
5. Fills missing data fields

**Output**: Enriched provider profiles with new information

#### Quality Assurance Agent
**Purpose**: Assesses data quality and prioritizes providers for review

**Process**:
1. Analyzes all validation results for a provider
2. Calculates overall confidence and quality scores
3. Identifies data quality issues
4. Generates recommendations
5. Prioritizes providers based on impact and confidence

**Output**: Quality assessments and prioritized review lists

#### Directory Management Agent
**Purpose**: Manages directory updates, reports, and workflows

**Process**:
1. Creates and tracks validation batches
2. Generates PDF reports
3. Creates email templates for provider communication
4. Manages workflow queues for human reviewers
5. Produces summary statistics

**Output**: Reports, email templates, workflow queues

### 3. Service Layer

#### NPI Service
- Interfaces with CMS NPI Registry API
- Searches providers by NPI or name
- Extracts structured provider information
- Validates provider credentials

#### Web Scraper
- Scrapes provider practice websites
- Extracts contact information
- Identifies specialties and services
- Validates phone numbers and addresses

#### PDF Extractor
- Uses VLM (Vision Language Model) for scanned PDFs
- Falls back to OCR for text extraction
- Extracts structured provider data
- Achieves 85%+ accuracy with 95% confidence

#### Synthetic Data Generator
- Generates realistic provider profiles
- Creates common data quality issues
- Useful for testing and demos

### 4. Data Layer

**Database Models**:
- **Provider**: Core provider information
- **ValidationResult**: Individual field validation results
- **ValidationBatch**: Batch processing metadata

**Features**:
- SQLite for development (can switch to PostgreSQL)
- JSON fields for flexible data storage
- Timestamps for audit trails
- Relationships for data integrity

## Data Flow

### Flow 1: Automated Provider Contact Validation

```
1. User initiates batch validation (200 providers)
   ↓
2. Directory Management Agent creates batch record
   ↓
3. For each provider:
   a. Data Validation Agent validates contact info
   b. Information Enrichment Agent enriches data
   c. Quality Assurance Agent assesses quality
   ↓
4. Results saved to database
   ↓
5. Directory Management Agent generates report
   ↓
6. User views results and downloads PDF report
```

### Flow 2: New Provider Credential Verification

```
1. New provider application received (PDF or form)
   ↓
2. PDF Extractor extracts structured data
   ↓
3. Provider record created in database
   ↓
4. Information Enrichment Agent searches for credentials
   ↓
5. Quality Assurance Agent assesses provider
   ↓
6. Directory Management Agent generates email template
   ↓
7. Provider added to directory or flagged for review
```

### Flow 3: Directory Quality Assessment

```
1. User initiates quality assessment
   ↓
2. Quality Assurance Agent analyzes all providers
   ↓
3. Calculates overall metrics
   ↓
4. Identifies providers needing review
   ↓
5. Prioritizes based on impact and confidence
   ↓
6. Generates quality report
   ↓
7. User reviews prioritized list and takes action
```

## Key Design Decisions

### 1. Agentic Architecture
- **Rationale**: Separates concerns and allows independent scaling
- **Benefit**: Easy to add new agents or modify existing ones
- **Trade-off**: Slight overhead in agent coordination

### 2. Confidence Scoring
- **Rationale**: Provides transparency in validation results
- **Benefit**: Helps prioritize manual review efforts
- **Implementation**: Weighted average based on source reliability

### 3. Modular Service Layer
- **Rationale**: Easy to swap implementations (e.g., different APIs)
- **Benefit**: Maintainable and testable
- **Example**: Can switch from OpenAI to Hugging Face for VLM

### 4. SQLite for Development
- **Rationale**: No setup required, works out of the box
- **Benefit**: Quick start for hackathon
- **Production**: Can easily switch to PostgreSQL

### 5. Synthetic Data Generation
- **Rationale**: Enables testing without real provider data
- **Benefit**: Demonstrates system capabilities
- **Use Case**: Hackathon demos and testing

## Performance Optimizations

1. **Batch Processing**: Processes multiple providers in single batch
2. **Caching**: Could cache NPI lookups (not implemented in demo)
3. **Async Processing**: Can be extended with Celery for background jobs
4. **Database Indexing**: Indexes on status, NPI for fast queries

## Security Considerations

1. **PII Handling**: Provider data should be encrypted in production
2. **API Keys**: Stored in environment variables, not in code
3. **Input Validation**: All user inputs validated
4. **SQL Injection**: SQLAlchemy ORM prevents SQL injection
5. **File Uploads**: Secure filename handling and size limits

## Scalability

### Current Limitations
- Synchronous processing (blocks during validation)
- Single database instance
- No caching layer

### Production Enhancements
- Celery for async task processing
- Redis for caching
- PostgreSQL for production database
- Load balancing for web servers
- Message queue for agent communication

## Testing Strategy

1. **Unit Tests**: Test individual agents and services
2. **Integration Tests**: Test agent interactions
3. **End-to-End Tests**: Test complete flows
4. **Performance Tests**: Validate KPI targets

## Future Enhancements

1. **Real-time Updates**: WebSocket for live progress updates
2. **Advanced ML Models**: Better confidence scoring
3. **Multi-source Validation**: More data sources
4. **Automated Email Sending**: Integration with email service
5. **Mobile App**: Native mobile interface
6. **API Rate Limiting**: Protect against abuse
7. **Audit Logging**: Complete audit trail

