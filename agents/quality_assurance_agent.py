from typing import Dict, List, Optional
from app.models import Provider, ValidationResult
from app import db
from sqlalchemy import func
import statistics

class QualityAssuranceAgent:
    """
    Agent responsible for quality assurance, discrepancy detection, and confidence scoring
    """
    
    def __init__(self, confidence_threshold: float = 0.80):
        self.confidence_threshold = confidence_threshold
    
    def assess_provider_quality(self, provider: Provider) -> Dict:
        """Assess overall quality of provider data"""
        # Get all validation results for this provider
        validations = ValidationResult.query.filter_by(provider_id=provider.id).all()
        
        if not validations:
            return {
                'provider_id': provider.id,
                'overall_confidence': 0.5,
                'quality_score': 0.5,
                'status': 'needs_validation',
                'issues': ['No validation data available'],
                'recommendations': ['Run validation process']
            }
        
        # Calculate overall confidence
        confidence_scores = [v.confidence_score for v in validations]
        overall_confidence = statistics.mean(confidence_scores) if confidence_scores else 0.5
        
        # Identify discrepancies
        discrepancies = [v for v in validations if v.status == 'discrepancy']
        
        # Calculate quality score (0-1)
        quality_score = self._calculate_quality_score(provider, validations, overall_confidence)
        
        # Identify issues
        issues = self._identify_issues(provider, validations, discrepancies)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(provider, issues, overall_confidence)
        
        # Determine status
        if overall_confidence >= self.confidence_threshold and not discrepancies:
            status = 'validated'
        elif discrepancies or overall_confidence < 0.6:
            status = 'needs_review'
        else:
            status = 'needs_manual_verification'
        
        return {
            'provider_id': provider.id,
            'overall_confidence': overall_confidence,
            'quality_score': quality_score,
            'status': status,
            'issues': issues,
            'recommendations': recommendations,
            'discrepancy_count': len(discrepancies),
            'validation_count': len(validations)
        }
    
    def _calculate_quality_score(self, provider: Provider, validations: List[ValidationResult],
                                 overall_confidence: float) -> float:
        """Calculate comprehensive quality score"""
        score = overall_confidence
        
        # Penalize missing critical fields
        critical_fields = ['phone', 'address_line1', 'city', 'state', 'zip_code']
        missing_fields = []
        
        if not provider.phone:
            missing_fields.append('phone')
        if not provider.address_line1:
            missing_fields.append('address')
        if not provider.city:
            missing_fields.append('city')
        if not provider.state:
            missing_fields.append('state')
        
        # Reduce score for missing fields
        score -= len(missing_fields) * 0.1
        
        # Penalize low confidence validations
        low_confidence = [v for v in validations if v.confidence_score < 0.6]
        score -= len(low_confidence) * 0.05
        
        return max(0.0, min(1.0, score))
    
    def _identify_issues(self, provider: Provider, validations: List[ValidationResult],
                        discrepancies: List[ValidationResult]) -> List[str]:
        """Identify data quality issues"""
        issues = []
        
        # Missing critical information
        if not provider.phone:
            issues.append('Missing phone number')
        if not provider.email:
            issues.append('Missing email address')
        if not provider.address_line1:
            issues.append('Missing address')
        if not provider.npi:
            issues.append('Missing NPI number')
        if not provider.license_number:
            issues.append('Missing license number')
        
        # Discrepancies
        for disc in discrepancies:
            issues.append(f"Discrepancy in {disc.field_name}: {disc.discrepancy_reason}")
        
        # Low confidence validations
        low_confidence = [v for v in validations if v.confidence_score < 0.6]
        if low_confidence:
            issues.append(f"{len(low_confidence)} fields with low confidence scores")
        
        return issues
    
    def _generate_recommendations(self, provider: Provider, issues: List[str],
                                 overall_confidence: float) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        
        if 'Missing phone number' in issues:
            recommendations.append('Contact provider to obtain phone number')
        
        if 'Missing email address' in issues:
            recommendations.append('Search provider website for email address')
        
        if 'Missing address' in issues:
            recommendations.append('Verify address with NPI registry or state licensing board')
        
        if 'Missing NPI number' in issues:
            recommendations.append('Search NPI registry by provider name and location')
        
        if 'Discrepancy' in str(issues):
            recommendations.append('Manual review required to resolve discrepancies')
        
        if overall_confidence < 0.7:
            recommendations.append('Additional validation sources recommended')
        
        if not recommendations:
            recommendations.append('Data quality is acceptable')
        
        return recommendations
    
    def prioritize_providers_for_review(self, providers: List[Provider], 
                                       limit: int = 50) -> List[Dict]:
        """Prioritize providers that need manual review"""
        prioritized = []
        
        for provider in providers:
            assessment = self.assess_provider_quality(provider)
            
            # Calculate priority score (higher = more urgent)
            priority_score = 0
            
            # High priority for low confidence
            if assessment['overall_confidence'] < 0.6:
                priority_score += 10
            
            # High priority for many discrepancies
            priority_score += assessment['discrepancy_count'] * 2
            
            # High priority for missing critical fields
            priority_score += len(assessment['issues']) * 1.5
            
            # High priority for providers with member complaints (if tracked)
            # This would be integrated with member complaint system
            
            prioritized.append({
                'provider': provider.to_dict(),
                'assessment': assessment,
                'priority_score': priority_score
            })
        
        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized[:limit]
    
    def generate_quality_report(self, providers: List[Provider]) -> Dict:
        """Generate overall quality assessment report"""
        total_providers = len(providers)
        
        assessments = [self.assess_provider_quality(p) for p in providers]
        
        # Calculate statistics
        confidence_scores = [a['overall_confidence'] for a in assessments]
        quality_scores = [a['quality_score'] for a in assessments]
        
        validated_count = sum(1 for a in assessments if a['status'] == 'validated')
        needs_review_count = sum(1 for a in assessments if a['status'] == 'needs_review')
        
        total_discrepancies = sum(a['discrepancy_count'] for a in assessments)
        total_issues = sum(len(a['issues']) for a in assessments)
        
        return {
            'total_providers': total_providers,
            'validated_count': validated_count,
            'needs_review_count': needs_review_count,
            'validation_rate': (validated_count / total_providers * 100) if total_providers > 0 else 0,
            'average_confidence': statistics.mean(confidence_scores) if confidence_scores else 0,
            'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
            'total_discrepancies': total_discrepancies,
            'total_issues': total_issues,
            'providers_by_status': {
                'validated': validated_count,
                'needs_review': needs_review_count,
                'needs_validation': total_providers - validated_count - needs_review_count
            }
        }

