from typing import Dict, List, Optional
from app.models import Provider, ValidationBatch
from app import db
from datetime import datetime
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

class DirectoryManagementAgent:
    """
    Agent responsible for directory management, report generation, and workflow management
    """
    
    def __init__(self):
        pass
    
    def create_validation_batch(self, batch_name: str, provider_ids: List[int]) -> ValidationBatch:
        """Create a new validation batch"""
        batch = ValidationBatch(
            batch_name=batch_name,
            total_providers=len(provider_ids),
            status='pending',
            started_at=None,
            completed_at=None
        )
        db.session.add(batch)
        db.session.commit()
        return batch
    
    def update_batch_progress(self, batch_id: int, processed: int, validated: int, 
                            needs_review: int, average_confidence: float):
        """Update batch processing progress"""
        batch = ValidationBatch.query.get(batch_id)
        if batch:
            batch.processed_providers = processed
            batch.validated_providers = validated
            batch.needs_review_count = needs_review
            batch.average_confidence = average_confidence
            
            if batch.processed_providers >= batch.total_providers:
                batch.status = 'completed'
                batch.completed_at = datetime.utcnow()
                if batch.started_at:
                    batch.processing_time_seconds = (batch.completed_at - batch.started_at).total_seconds()
            
            db.session.commit()
    
    def generate_validation_report(self, batch_id: int) -> Dict:
        """Generate validation report for a batch"""
        batch = ValidationBatch.query.get(batch_id)
        if not batch:
            return {'error': 'Batch not found'}
        
        # Get providers in batch (simplified - would track batch-provider relationship)
        providers = Provider.query.all()  # In production, filter by batch
        
        report = {
            'batch_id': batch.id,
            'batch_name': batch.batch_name,
            'total_providers': batch.total_providers,
            'processed_providers': batch.processed_providers,
            'validated_providers': batch.validated_providers,
            'needs_review_count': batch.needs_review_count,
            'average_confidence': batch.average_confidence,
            'processing_time_seconds': batch.processing_time_seconds,
            'status': batch.status,
            'started_at': batch.started_at.isoformat() if batch.started_at else None,
            'completed_at': batch.completed_at.isoformat() if batch.completed_at else None,
            'providers_needing_review': []
        }
        
        # Get providers needing review (limit to 50 for display, but show actual count)
        needs_review = Provider.query.filter_by(status='needs_review').limit(50).all()
        report['providers_needing_review'] = [p.to_dict() for p in needs_review]
        report['total_needs_review'] = batch.needs_review_count  # Actual count from batch
        
        return report
    
    def generate_pdf_report(self, batch_id: int, output_path: str) -> str:
        """Generate PDF report for validation batch"""
        try:
            batch = ValidationBatch.query.get(batch_id)
            if not batch:
                print(f"Batch {batch_id} not found")
                return None
            
            # Ensure directory exists
            import os
            dir_path = os.path.dirname(output_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            else:
                # If no directory in path, use current directory
                output_path = os.path.join('reports', os.path.basename(output_path))
                os.makedirs('reports', exist_ok=True)
            
            # Ensure .pdf extension
            if not output_path.endswith('.pdf'):
                output_path = output_path + '.pdf'
            
            print(f"Generating PDF at: {os.path.abspath(output_path)}")
            
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title = Paragraph(f"Provider Validation Report: {batch.batch_name}", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 0.2*inch))
            
            # Summary
            avg_confidence_str = f"{batch.average_confidence:.2%}" if batch.average_confidence else 'N/A'
            processing_time_str = f"{batch.processing_time_seconds:.2f} seconds" if batch.processing_time_seconds else 'N/A'
            
            summary_data = [
                ['Metric', 'Value'],
                ['Total Providers', str(batch.total_providers)],
                ['Processed', str(batch.processed_providers)],
                ['Validated', str(batch.validated_providers)],
                ['Needs Review', str(batch.needs_review_count)],
                ['Average Confidence', avg_confidence_str],
                ['Processing Time', processing_time_str]
            ]
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Providers needing review
            if batch.needs_review_count > 0:
                review_title = Paragraph("Providers Requiring Manual Review", styles['Heading2'])
                story.append(review_title)
                story.append(Spacer(1, 0.1*inch))
                
                needs_review = Provider.query.filter_by(status='needs_review').limit(10).all()
                
                for provider in needs_review:
                    provider_text = f"{provider.first_name} {provider.last_name} - {provider.specialty or 'N/A'}"
                    story.append(Paragraph(provider_text, styles['Normal']))
                    story.append(Spacer(1, 0.05*inch))
            
            # Build PDF
            doc.build(story)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"PDF generated successfully: {output_path} ({file_size} bytes)")
                return output_path
            else:
                print(f"PDF file was not created at: {output_path}")
                return None
                
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_email_template(self, provider: Provider, action_type: str = 'verification') -> str:
        """Generate email template for provider communication"""
        if action_type == 'verification':
            subject = f"Provider Information Verification Request - {provider.full_name}"
            body = f"""
Dear Dr. {provider.last_name},

We are reaching out to verify and update your provider information in our directory.

Please review the following information and confirm its accuracy:

Name: {provider.first_name} {provider.middle_name or ''} {provider.last_name}
Specialty: {provider.specialty or 'Not specified'}
Practice Name: {provider.practice_name or 'Not specified'}
Phone: {provider.phone or 'Not provided'}
Email: {provider.email or 'Not provided'}
Address: {provider.address_line1 or ''}, {provider.city or ''}, {provider.state or ''} {provider.zip_code or ''}

If any information is incorrect or needs updating, please reply to this email with the corrections.

Thank you for your cooperation.

Best regards,
Provider Directory Management Team
"""
        elif action_type == 'discrepancy':
            subject = f"Action Required: Provider Information Discrepancy - {provider.full_name}"
            body = f"""
Dear Dr. {provider.last_name},

We have identified discrepancies in your provider directory information that require your attention.

Please review and confirm the following information:

[Discrepancy details would be inserted here]

Please contact us at your earliest convenience to resolve these discrepancies.

Thank you,
Provider Directory Management Team
"""
        else:
            subject = f"Provider Directory Update - {provider.full_name}"
            body = f"""
Dear Dr. {provider.last_name},

This is a notification regarding your provider directory information.

[Additional details would be inserted here]

Thank you,
Provider Directory Management Team
"""
        
        return {
            'subject': subject,
            'body': body,
            'to': provider.email or 'email_not_available@example.com'
        }
    
    def create_workflow_queue(self, providers: List[Provider], priority_scores: Dict[int, float]) -> List[Dict]:
        """Create prioritized workflow queue for human reviewers"""
        queue = []
        
        for provider in providers:
            priority = priority_scores.get(provider.id, 0.5)
            queue.append({
                'provider': provider.to_dict(),
                'priority': priority,
                'status': provider.status,
                'created_at': provider.updated_at.isoformat() if provider.updated_at else None
            })
        
        # Sort by priority (descending)
        queue.sort(key=lambda x: x['priority'], reverse=True)
        
        return queue

