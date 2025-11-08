from flask import Blueprint, render_template, request, jsonify, send_file, session
from app import db
from app.models import Provider, ValidationResult, ValidationBatch
from agents.data_validation_agent import DataValidationAgent
from agents.enrichment_agent import InformationEnrichmentAgent
from agents.quality_assurance_agent import QualityAssuranceAgent
from agents.directory_management_agent import DirectoryManagementAgent
from services.pdf_extractor import PDFExtractor
from services.synthetic_data import generate_provider_dataset, save_providers_to_json
from config import Config
from datetime import datetime
import os
import json
import time
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

# Initialize agents
data_validation_agent = DataValidationAgent(Config.NPI_API_KEY)
enrichment_agent = InformationEnrichmentAgent(Config.NPI_API_KEY)
qa_agent = QualityAssuranceAgent(Config.CONFIDENCE_THRESHOLD)
directory_agent = DirectoryManagementAgent()
pdf_extractor = PDFExtractor(Config.OPENAI_API_KEY)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@bp.route('/')
def index():
    """Dashboard home page"""
    total_providers = Provider.query.count()
    validated_count = Provider.query.filter_by(status='validated').count()
    needs_review_count = Provider.query.filter_by(status='needs_review').count()
    pending_count = Provider.query.filter_by(status='pending').count()
    
    # Get recent batches
    recent_batches = ValidationBatch.query.order_by(ValidationBatch.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                         total_providers=total_providers,
                         validated_count=validated_count,
                         needs_review_count=needs_review_count,
                         pending_count=pending_count,
                         recent_batches=[b.to_dict() for b in recent_batches])

@bp.route('/providers')
def providers():
    """Provider list page"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', 'all')
    
    query = Provider.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    providers = query.order_by(Provider.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('providers.html', providers=providers, status_filter=status_filter)

@bp.route('/api/providers', methods=['GET'])
def api_get_providers():
    """API endpoint to get providers"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Provider.query
    if status:
        query = query.filter_by(status=status)
    
    providers = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'providers': [p.to_dict() for p in providers.items],
        'total': providers.total,
        'pages': providers.pages,
        'current_page': page
    })

@bp.route('/api/providers', methods=['POST'])
def api_create_provider():
    """API endpoint to create a provider"""
    data = request.json
    
    provider = Provider(
        npi=data.get('npi'),
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        middle_name=data.get('middle_name'),
        specialty=data.get('specialty'),
        practice_name=data.get('practice_name'),
        phone=data.get('phone'),
        email=data.get('email'),
        address_line1=data.get('address_line1'),
        address_line2=data.get('address_line2'),
        city=data.get('city'),
        state=data.get('state'),
        zip_code=data.get('zip_code'),
        license_number=data.get('license_number'),
        license_state=data.get('license_state'),
        board_certifications=data.get('board_certifications'),
        education=data.get('education'),
        insurance_networks=data.get('insurance_networks'),
        affiliations=data.get('affiliations'),
        status='pending'
    )
    
    db.session.add(provider)
    db.session.commit()
    
    return jsonify(provider.to_dict()), 201

@bp.route('/api/providers/<int:provider_id>', methods=['GET'])
def api_get_provider(provider_id):
    """API endpoint to get a single provider"""
    provider = Provider.query.get_or_404(provider_id)
    validations = ValidationResult.query.filter_by(provider_id=provider_id).all()
    
    return jsonify({
        'provider': provider.to_dict(),
        'validations': [v.to_dict() for v in validations]
    })

@bp.route('/api/providers/<int:provider_id>/validate', methods=['POST'])
def api_validate_provider(provider_id):
    """API endpoint to validate a single provider"""
    provider = Provider.query.get_or_404(provider_id)
    
    # Run validation
    validation_results = data_validation_agent.validate_provider_contact(provider)
    data_validation_agent.save_validation_results(provider, validation_results)
    
    # Run enrichment
    enrichment_results = enrichment_agent.enrich_provider_info(provider)
    enrichment_agent.save_enrichment_results(provider, enrichment_results)
    
    # Get updated provider
    provider = Provider.query.get(provider_id)
    
    return jsonify({
        'provider': provider.to_dict(),
        'validation_results': validation_results,
        'enrichment_results': enrichment_results
    })

@bp.route('/api/batch/validate', methods=['POST'])
def api_batch_validate():
    """API endpoint to validate multiple providers"""
    try:
        data = request.json or {}
        provider_ids = data.get('provider_ids', [])
        batch_name = data.get('batch_name', f'Batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        
        if not provider_ids:
            # Get all pending providers
            providers = Provider.query.filter_by(status='pending').all()
            provider_ids = [p.id for p in providers]
        
        if not provider_ids:
            return jsonify({
                'error': 'No providers to validate',
                'batch_id': None
            }), 400
        
        # Create batch
        batch = directory_agent.create_validation_batch(batch_name, provider_ids)
        batch.started_at = datetime.utcnow()
        batch.status = 'processing'
        db.session.commit()
        
        # Process providers (in production, this would be async)
        processed = 0
        validated = 0
        needs_review = 0
        confidence_scores = []
        errors = []
        
        start_time = time.time()
        
        for provider_id in provider_ids[:200]:  # Limit to 200 for demo
            try:
                provider = Provider.query.get(provider_id)
                if not provider:
                    continue
                
                # Validate
                validation_results = data_validation_agent.validate_provider_contact(provider)
                data_validation_agent.save_validation_results(provider, validation_results)
                
                # Enrich
                enrichment_results = enrichment_agent.enrich_provider_info(provider)
                enrichment_agent.save_enrichment_results(provider, enrichment_results)
                
                # Update counts
                processed += 1
                confidence = validation_results.get('overall_confidence', 0.5)
                confidence_scores.append(confidence)
                
                # Refresh provider from database
                db.session.refresh(provider)
                if provider.status == 'validated':
                    validated += 1
                elif provider.status == 'needs_review':
                    needs_review += 1
                
                # Update batch progress periodically
                if processed % 10 == 0:
                    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
                    directory_agent.update_batch_progress(batch.id, processed, validated, needs_review, avg_confidence)
                    
            except Exception as e:
                errors.append(f"Provider {provider_id}: {str(e)}")
                processed += 1  # Count as processed even if failed
                confidence_scores.append(0.3)  # Low confidence for errors
                continue
        
        # Final update - ensure batch is marked as completed
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Update batch with final results
        batch = ValidationBatch.query.get(batch.id)
        if batch:
            batch.processed_providers = processed
            batch.validated_providers = validated
            batch.needs_review_count = needs_review
            batch.average_confidence = avg_confidence
            batch.status = 'completed'
            batch.completed_at = datetime.utcnow()
            if batch.started_at:
                batch.processing_time_seconds = (batch.completed_at - batch.started_at).total_seconds()
            db.session.commit()
        
        processing_time = time.time() - start_time
        
        return jsonify({
            'batch_id': batch.id,
            'batch_name': batch_name,
            'processed': processed,
            'validated': validated,
            'needs_review': needs_review,
            'average_confidence': avg_confidence,
            'processing_time_seconds': processing_time,
            'errors': errors[:5] if errors else []  # Return first 5 errors if any
        })
        
    except Exception as e:
        # If batch was created, mark it as failed
        if 'batch' in locals() and batch:
            batch.status = 'failed'
            db.session.commit()
        
        return jsonify({
            'error': f'Batch validation failed: {str(e)}',
            'batch_id': batch.id if 'batch' in locals() else None
        }), 500

@bp.route('/api/batch', methods=['GET'])
def api_get_batches():
    """API endpoint to get all batches"""
    batches = ValidationBatch.query.order_by(ValidationBatch.created_at.desc()).limit(10).all()
    return jsonify({
        'batches': [b.to_dict() for b in batches]
    })

@bp.route('/api/batch/<int:batch_id>', methods=['GET'])
def api_get_batch(batch_id):
    """API endpoint to get batch details"""
    batch = ValidationBatch.query.get_or_404(batch_id)
    return jsonify(directory_agent.generate_validation_report(batch_id))

@bp.route('/api/batch/<int:batch_id>/fix', methods=['POST'])
def api_fix_batch(batch_id):
    """API endpoint to fix stuck batches by recalculating status"""
    batch = ValidationBatch.query.get_or_404(batch_id)
    
    # Recalculate counts from actual provider statuses
    if batch.status == 'processing':
        # Count providers that were likely in this batch (all providers)
        all_providers = Provider.query.all()
        validated_count = Provider.query.filter_by(status='validated').count()
        needs_review_count = Provider.query.filter_by(status='needs_review').count()
        pending_count = Provider.query.filter_by(status='pending').count()
        
        # Get validation results to calculate average confidence
        all_validations = ValidationResult.query.all()
        if all_validations:
            avg_confidence = sum(v.confidence_score for v in all_validations) / len(all_validations)
        else:
            avg_confidence = 0.5
        
        # Update batch
        batch.processed_providers = len(all_providers)
        batch.validated_providers = validated_count
        batch.needs_review_count = needs_review_count
        batch.average_confidence = avg_confidence
        batch.status = 'completed'
        batch.completed_at = datetime.utcnow()
        if batch.started_at:
            batch.processing_time_seconds = (batch.completed_at - batch.started_at).total_seconds()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Batch status updated',
            'batch': batch.to_dict()
        })
    
    return jsonify({
        'success': False,
        'message': 'Batch is not in processing status'
    }), 400

@bp.route('/api/batch/<int:batch_id>/report', methods=['GET'])
def api_get_batch_report(batch_id):
    """API endpoint to generate and download PDF report"""
    try:
        batch = ValidationBatch.query.get(batch_id)
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
        
        output_path = os.path.join('reports', f'batch_{batch_id}_report.pdf')
        os.makedirs('reports', exist_ok=True)
        
        # Generate PDF
        pdf_path = directory_agent.generate_pdf_report(batch_id, output_path)
        
        if pdf_path and os.path.exists(pdf_path):
            # Verify it's actually a PDF file and has content
            if pdf_path.endswith('.pdf') and os.path.getsize(pdf_path) > 0:
                # Use absolute path for send_file
                abs_path = os.path.abspath(pdf_path)
                return send_file(
                    abs_path, 
                    as_attachment=True, 
                    download_name=f'validation_report_{batch_id}.pdf',
                    mimetype='application/pdf'
                )
            else:
                return jsonify({
                    'error': 'Generated file is not a valid PDF',
                    'message': 'PDF file is empty or invalid'
                }), 500
        else:
            # Return JSON error instead of HTML
            return jsonify({
                'error': 'PDF generation failed',
                'message': f'Could not generate PDF for batch {batch_id}. Check server logs for details.',
                'batch_id': batch_id
            }), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF Generation Error: {error_details}")
        # Return JSON error, not HTML
        return jsonify({
            'error': 'PDF generation error',
            'message': str(e),
            'batch_id': batch_id
        }), 500

@bp.route('/api/quality/assess', methods=['POST'])
def api_assess_quality():
    """API endpoint to assess provider quality"""
    data = request.json
    provider_id = data.get('provider_id')
    
    if provider_id:
        provider = Provider.query.get_or_404(provider_id)
        assessment = qa_agent.assess_provider_quality(provider)
        return jsonify(assessment)
    else:
        # Assess all providers
        providers = Provider.query.all()
        report = qa_agent.generate_quality_report(providers)
        return jsonify(report)

@bp.route('/api/quality/prioritize', methods=['GET'])
def api_prioritize_review():
    """API endpoint to get prioritized list for review"""
    providers = Provider.query.filter_by(status='needs_review').all()
    prioritized = qa_agent.prioritize_providers_for_review(providers, limit=50)
    return jsonify({'prioritized': prioritized})

@bp.route('/api/providers/<int:provider_id>/email', methods=['GET'])
def api_generate_email(provider_id):
    """API endpoint to generate email template"""
    provider = Provider.query.get_or_404(provider_id)
    action_type = request.args.get('type', 'verification')
    email = directory_agent.generate_email_template(provider, action_type)
    return jsonify(email)

@bp.route('/api/upload/pdf', methods=['POST'])
def api_upload_pdf():
    """API endpoint to upload and extract data from PDF"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Extract data
        use_vlm = request.form.get('use_vlm', 'true').lower() == 'true'
        extraction_result = pdf_extractor.extract_from_pdf(filepath, use_vlm=use_vlm)
        
        # Clean up file
        os.remove(filepath)
        
        if extraction_result.get('success'):
            return jsonify(extraction_result)
        else:
            return jsonify({'error': extraction_result.get('error', 'Extraction failed')}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('/api/synthetic/generate', methods=['POST'])
def api_generate_synthetic():
    """API endpoint to generate synthetic provider data"""
    data = request.json
    count = data.get('count', 200)
    error_rate = data.get('error_rate', 0.4)
    
    providers_data = generate_provider_dataset(count, error_rate)
    
    # Save to database
    created = []
    for p_data in providers_data:
        provider = Provider(**p_data, status='pending')
        db.session.add(provider)
        created.append(provider)
    
    db.session.commit()
    
    return jsonify({
        'created': len(created),
        'providers': [p.to_dict() for p in created[:10]]  # Return first 10
    })

@bp.route('/validation')
def validation():
    """Validation page"""
    return render_template('validation.html')

@bp.route('/quality')
def quality():
    """Quality assessment page"""
    return render_template('quality.html')

@bp.route('/reports')
def reports():
    """Reports page"""
    batches = ValidationBatch.query.order_by(ValidationBatch.created_at.desc()).all()
    return render_template('reports.html', batches=[b.to_dict() for b in batches])

