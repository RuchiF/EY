from datetime import datetime
from app import db
from sqlalchemy import JSON

class Provider(db.Model):
    __tablename__ = 'providers'
    
    id = db.Column(db.Integer, primary_key=True)
    npi = db.Column(db.String(10), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100), nullable=True)
    specialty = db.Column(db.String(200), nullable=True)
    practice_name = db.Column(db.String(200), nullable=True)
    
    # Contact Information
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    address_line1 = db.Column(db.String(200), nullable=True)
    address_line2 = db.Column(db.String(200), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    zip_code = db.Column(db.String(10), nullable=True)
    
    # Professional Details
    license_number = db.Column(db.String(50), nullable=True)
    license_state = db.Column(db.String(2), nullable=True)
    board_certifications = db.Column(JSON, nullable=True)
    education = db.Column(JSON, nullable=True)
    
    # Network Information
    insurance_networks = db.Column(JSON, nullable=True)
    affiliations = db.Column(JSON, nullable=True)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, validated, needs_review, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    validations = db.relationship('ValidationResult', backref='provider', lazy=True, cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        """Get full name of provider"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)
    
    def to_dict(self):
        return {
            'id': self.id,
            'npi': self.npi,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'middle_name': self.middle_name,
            'full_name': f"{self.first_name} {self.middle_name or ''} {self.last_name}".strip(),
            'specialty': self.specialty,
            'practice_name': self.practice_name,
            'phone': self.phone,
            'email': self.email,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code
            },
            'license_number': self.license_number,
            'license_state': self.license_state,
            'board_certifications': self.board_certifications or [],
            'education': self.education or [],
            'insurance_networks': self.insurance_networks or [],
            'affiliations': self.affiliations or [],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ValidationResult(db.Model):
    __tablename__ = 'validation_results'
    
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    
    # Validation Details
    validation_type = db.Column(db.String(50), nullable=False)  # contact, credential, quality
    field_name = db.Column(db.String(100), nullable=False)
    original_value = db.Column(db.Text, nullable=True)
    validated_value = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(200), nullable=True)  # npi, web_scrape, google_maps, etc.
    
    # Status
    status = db.Column(db.String(50), default='pending')  # validated, discrepancy, needs_review
    discrepancy_reason = db.Column(db.Text, nullable=True)
    
    # Metadata
    validated_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'validation_type': self.validation_type,
            'field_name': self.field_name,
            'original_value': self.original_value,
            'validated_value': self.validated_value,
            'confidence_score': self.confidence_score,
            'source': self.source,
            'status': self.status,
            'discrepancy_reason': self.discrepancy_reason,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'notes': self.notes
        }

class ValidationBatch(db.Model):
    __tablename__ = 'validation_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_name = db.Column(db.String(200), nullable=False)
    total_providers = db.Column(db.Integer, default=0)
    processed_providers = db.Column(db.Integer, default=0)
    validated_providers = db.Column(db.Integer, default=0)
    needs_review_count = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Results
    average_confidence = db.Column(db.Float, nullable=True)
    processing_time_seconds = db.Column(db.Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_name': self.batch_name,
            'total_providers': self.total_providers,
            'processed_providers': self.processed_providers,
            'validated_providers': self.validated_providers,
            'needs_review_count': self.needs_review_count,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'average_confidence': self.average_confidence,
            'processing_time_seconds': self.processing_time_seconds,
            'progress_percentage': (self.processed_providers / self.total_providers * 100) if self.total_providers > 0 else 0
        }

