"""
Demo script to showcase the Provider Directory Management System
This script demonstrates the key flows and capabilities
"""
from app import create_app, db
from app.models import Provider, ValidationBatch
from agents.data_validation_agent import DataValidationAgent
from agents.enrichment_agent import InformationEnrichmentAgent
from agents.quality_assurance_agent import QualityAssuranceAgent
from agents.directory_management_agent import DirectoryManagementAgent
from services.synthetic_data import generate_provider_dataset
from services.pdf_extractor import PDFExtractor
from config import Config
import time

def demo_flow_1():
    """Flow 1: Automated Provider Contact Information Validation"""
    print("\n" + "="*60)
    print("FLOW 1: Automated Provider Contact Information Validation")
    print("="*60)
    
    app = create_app(Config)
    with app.app_context():
        # Generate synthetic data
        print("\n1. Generating 50 synthetic provider profiles...")
        providers_data = generate_provider_dataset(count=50, error_rate=0.4)
        
        providers = []
        for p_data in providers_data:
            provider = Provider(**p_data, status='pending')
            db.session.add(provider)
            providers.append(provider)
        db.session.commit()
        print(f"   ✓ Created {len(providers)} providers")
        
        # Create batch
        print("\n2. Creating validation batch...")
        directory_agent = DirectoryManagementAgent()
        batch = directory_agent.create_validation_batch(
            "Demo_Batch_Flow1",
            [p.id for p in providers[:20]]  # Validate first 20
        )
        from datetime import datetime
        batch.started_at = datetime.utcnow()
        batch.status = 'processing'
        db.session.commit()
        print(f"   ✓ Batch created: {batch.batch_name}")
        
        # Run validation
        print("\n3. Running validation agent...")
        data_validation_agent = DataValidationAgent(Config.NPI_API_KEY)
        enrichment_agent = InformationEnrichmentAgent(Config.NPI_API_KEY)
        
        validated = 0
        needs_review = 0
        confidence_scores = []
        
        start_time = time.time()
        for provider in providers[:20]:
            # Validate
            validation_results = data_validation_agent.validate_provider_contact(provider)
            data_validation_agent.save_validation_results(provider, validation_results)
            
            # Enrich
            enrichment_results = enrichment_agent.enrich_provider_info(provider)
            enrichment_agent.save_enrichment_results(provider, enrichment_results)
            
            confidence_scores.append(validation_results.get('overall_confidence', 0.5))
            
            provider = Provider.query.get(provider.id)
            if provider.status == 'validated':
                validated += 1
            elif provider.status == 'needs_review':
                needs_review += 1
        
        processing_time = time.time() - start_time
        
        # Update batch
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        directory_agent.update_batch_progress(batch.id, 20, validated, needs_review, avg_confidence)
        
        print(f"\n4. Validation Results:")
        print(f"   - Processed: 20 providers")
        print(f"   - Validated: {validated} providers")
        print(f"   - Needs Review: {needs_review} providers")
        print(f"   - Average Confidence: {avg_confidence:.2%}")
        print(f"   - Processing Time: {processing_time:.2f} seconds")
        
        # Generate report
        print("\n5. Generating validation report...")
        report = directory_agent.generate_validation_report(batch.id)
        print(f"   ✓ Report generated for batch: {report['batch_name']}")

def demo_flow_2():
    """Flow 2: New Provider Credential Verification and Onboarding"""
    print("\n" + "="*60)
    print("FLOW 2: New Provider Credential Verification")
    print("="*60)
    
    app = create_app(Config)
    with app.app_context():
        # Create new provider
        print("\n1. Creating new provider application...")
        new_provider = Provider(
            first_name="John",
            last_name="Smith",
            specialty="Cardiology",
            practice_name="Heart Care Associates",
            phone="555-1234",
            email="john.smith@heartcare.com",
            address_line1="123 Medical Center Dr",
            city="Boston",
            state="MA",
            zip_code="02115",
            status='pending'
        )
        db.session.add(new_provider)
        db.session.commit()
        print(f"   ✓ Provider created: {new_provider.full_name}")
        
        # Enrichment agent searches for credentials
        print("\n2. Information Enrichment Agent searching for credentials...")
        enrichment_agent = InformationEnrichmentAgent(Config.NPI_API_KEY)
        enrichment_results = enrichment_agent.enrich_provider_info(new_provider)
        enrichment_agent.save_enrichment_results(new_provider, enrichment_results)
        
        print(f"   - Enriched fields: {enrichment_results.get('enriched_fields', [])}")
        print(f"   - New information found: {len(enrichment_results.get('new_information', {}))} items")
        
        # Quality assurance
        print("\n3. Quality Assurance Agent assessing provider...")
        qa_agent = QualityAssuranceAgent(Config.CONFIDENCE_THRESHOLD)
        assessment = qa_agent.assess_provider_quality(new_provider)
        
        print(f"   - Overall Confidence: {assessment['overall_confidence']:.2%}")
        print(f"   - Quality Score: {assessment['quality_score']:.2%}")
        print(f"   - Status: {assessment['status']}")
        print(f"   - Issues: {len(assessment['issues'])}")
        if assessment['recommendations']:
            print(f"   - Recommendations:")
            for rec in assessment['recommendations']:
                print(f"     • {rec}")
        
        # Generate email
        print("\n4. Generating verification email...")
        directory_agent = DirectoryManagementAgent()
        email = directory_agent.generate_email_template(new_provider, 'verification')
        print(f"   ✓ Email template generated")
        print(f"   Subject: {email['subject']}")

def demo_flow_3():
    """Flow 3: Provider Directory Quality Assessment"""
    print("\n" + "="*60)
    print("FLOW 3: Provider Directory Quality Assessment")
    print("="*60)
    
    app = create_app(Config)
    with app.app_context():
        # Get all providers
        providers = Provider.query.all()
        print(f"\n1. Assessing {len(providers)} providers...")
        
        # Quality assessment
        qa_agent = QualityAssuranceAgent(Config.CONFIDENCE_THRESHOLD)
        report = qa_agent.generate_quality_report(providers)
        
        print(f"\n2. Quality Report:")
        print(f"   - Total Providers: {report['total_providers']}")
        print(f"   - Validated: {report['validated_count']} ({report['validation_rate']:.1f}%)")
        print(f"   - Needs Review: {report['needs_review_count']}")
        print(f"   - Average Confidence: {report['average_confidence']:.2%}")
        print(f"   - Average Quality Score: {report['average_quality_score']:.2%}")
        print(f"   - Total Discrepancies: {report['total_discrepancies']}")
        print(f"   - Total Issues: {report['total_issues']}")
        
        # Prioritize for review
        print("\n3. Prioritizing providers for review...")
        needs_review = Provider.query.filter_by(status='needs_review').all()
        prioritized = qa_agent.prioritize_providers_for_review(needs_review, limit=10)
        
        print(f"   - Top 10 providers needing review:")
        for i, item in enumerate(prioritized[:10], 1):
            p = item['provider']
            assessment = item['assessment']
            print(f"     {i}. {p['full_name']} - Priority: {item['priority_score']:.1f}, "
                  f"Confidence: {assessment['overall_confidence']:.2%}")

def main():
    """Run all demo flows"""
    print("\n" + "="*60)
    print("PROVIDER DIRECTORY MANAGEMENT SYSTEM - DEMO")
    print("="*60)
    
    try:
        demo_flow_1()
        demo_flow_2()
        demo_flow_3()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("="*60)
        print("\nAccess the web interface at: http://localhost:5000")
        print("Run: python main.py")
        
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

