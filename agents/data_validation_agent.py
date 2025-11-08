from typing import Dict, List, Optional
from services.npi_service import NPIService
from services.web_scraper import WebScraper
from app.models import Provider, ValidationResult
from app import db
import time

class DataValidationAgent:
    """
    Agent responsible for validating provider contact information
    """
    
    def __init__(self, npi_api_key: Optional[str] = None):
        self.npi_service = NPIService(npi_api_key)
        self.web_scraper = WebScraper()
    
    def validate_provider_contact(self, provider: Provider) -> Dict:
        """Validate provider contact information"""
        results = {
            'provider_id': provider.id,
            'validations': [],
            'overall_confidence': 0.0,
            'discrepancies': []
        }
        
        provider_data = provider.to_dict()
        has_external_validation = False
        
        # 1. Validate against NPI registry
        try:
            npi_validation = self.npi_service.validate_provider(provider_data)
            
            if npi_validation.get('valid'):
                has_external_validation = True
                npi_data = npi_validation.get('npi_data', {})
                
                # Validate phone
                if npi_data.get('address', {}).get('phone'):
                    phone_result = self._validate_field(
                        provider, 'phone',
                        provider.phone,
                        npi_data['address']['phone'],
                        'npi',
                        npi_validation.get('confidence', 0.8)
                    )
                    results['validations'].append(phone_result)
                
                # Validate address
                npi_address = npi_data.get('address', {})
                if npi_address.get('line1'):
                    address_result = self._validate_address(
                        provider,
                        npi_address,
                        'npi',
                        npi_validation.get('confidence', 0.8)
                    )
                    results['validations'].append(address_result)
        except Exception as e:
            # NPI validation failed, continue with data quality checks
            pass
        
        # 2. Web scraping validation (if practice name or website available)
        if provider.practice_name:
            # Try to construct website URL (simplified)
            website_url = self._construct_website_url(provider)
            if website_url:
                try:
                    scraped_data = self.web_scraper.scrape_provider_website(website_url, provider.full_name)
                    web_validation = self.web_scraper.validate_contact_info(provider_data, scraped_data)
                    
                    # Add web scraping validations
                    for field, score in web_validation.get('field_scores', {}).items():
                        if field == 'phone' and scraped_data.get('phone'):
                            phone_result = self._validate_field(
                                provider, 'phone',
                                provider.phone,
                                scraped_data['phone'],
                                'web_scrape',
                                score
                            )
                            results['validations'].append(phone_result)
                            has_external_validation = True
                        
                        elif field == 'email' and scraped_data.get('email'):
                            email_result = self._validate_field(
                                provider, 'email',
                                provider.email,
                                scraped_data['email'],
                                'web_scrape',
                                score
                            )
                            results['validations'].append(email_result)
                            has_external_validation = True
                except Exception:
                    # Web scraping failed, continue
                    pass
        
        # 3. Data Quality Validation (always run, even without external sources)
        # This ensures we always have validation results
        quality_validations = self._validate_data_quality(provider)
        results['validations'].extend(quality_validations)
        
        # Calculate overall confidence
        if results['validations']:
            results['overall_confidence'] = sum(v['confidence_score'] for v in results['validations']) / len(results['validations'])
        else:
            # Default confidence if no validations
            results['overall_confidence'] = 0.5
        
        # Collect discrepancies
        results['discrepancies'] = [
            v for v in results['validations']
            if v['status'] == 'discrepancy'
        ]
        
        return results
    
    def _validate_data_quality(self, provider: Provider) -> List[Dict]:
        """Validate data quality based on completeness and format"""
        validations = []
        confidence_scores = []
        
        # Check required fields completeness
        required_fields = {
            'first_name': provider.first_name,
            'last_name': provider.last_name,
            'phone': provider.phone,
            'address_line1': provider.address_line1,
            'city': provider.city,
            'state': provider.state,
            'zip_code': provider.zip_code
        }
        
        present_count = sum(1 for v in required_fields.values() if v)
        total_count = len(required_fields)
        completeness_score = present_count / total_count
        
        # Validate phone format
        if provider.phone:
            phone_valid = self._validate_phone_format(provider.phone)
            phone_confidence = 0.8 if phone_valid else 0.5
            validations.append({
                'field_name': 'phone_format',
                'original_value': provider.phone,
                'validated_value': provider.phone if phone_valid else 'Invalid format',
                'confidence_score': phone_confidence,
                'source': 'format_validation',
                'status': 'validated' if phone_valid else 'needs_review',
                'discrepancy_reason': None if phone_valid else 'Phone format may be invalid'
            })
            confidence_scores.append(phone_confidence)
        
        # Validate email format
        if provider.email:
            email_valid = self._validate_email_format(provider.email)
            email_confidence = 0.8 if email_valid else 0.5
            validations.append({
                'field_name': 'email_format',
                'original_value': provider.email,
                'validated_value': provider.email if email_valid else 'Invalid format',
                'confidence_score': email_confidence,
                'source': 'format_validation',
                'status': 'validated' if email_valid else 'needs_review',
                'discrepancy_reason': None if email_valid else 'Email format may be invalid'
            })
            confidence_scores.append(email_confidence)
        
        # Validate zip code format
        if provider.zip_code:
            zip_valid = self._validate_zip_format(provider.zip_code)
            zip_confidence = 0.7 if zip_valid else 0.4
            validations.append({
                'field_name': 'zip_code_format',
                'original_value': provider.zip_code,
                'validated_value': provider.zip_code if zip_valid else 'Invalid format',
                'confidence_score': zip_confidence,
                'source': 'format_validation',
                'status': 'validated' if zip_valid else 'needs_review',
                'discrepancy_reason': None if zip_valid else 'Zip code format may be invalid'
            })
            confidence_scores.append(zip_confidence)
        
        # Overall completeness validation
        completeness_confidence = 0.5 + (completeness_score * 0.3)  # 0.5 to 0.8
        validations.append({
            'field_name': 'data_completeness',
            'original_value': f'{present_count}/{total_count} fields',
            'validated_value': f'{completeness_score:.0%} complete',
            'confidence_score': completeness_confidence,
            'source': 'quality_check',
            'status': 'validated' if completeness_score >= 0.8 else 'needs_review',
            'discrepancy_reason': None if completeness_score >= 0.8 else f'Only {completeness_score:.0%} of required fields present'
        })
        
        return validations
    
    def _validate_phone_format(self, phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
        # Check if it's 10 or 11 digits
        return bool(re.match(r'^\+?1?\d{10}$', cleaned))
    
    def _validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_zip_format(self, zip_code: str) -> bool:
        """Validate zip code format"""
        import re
        # US zip code: 5 digits or 5+4 format
        return bool(re.match(r'^\d{5}(-\d{4})?$', zip_code))
    
    def _validate_field(self, provider: Provider, field_name: str, 
                       original_value: Optional[str], validated_value: Optional[str],
                       source: str, base_confidence: float) -> Dict:
        """Validate a single field"""
        if not validated_value:
            return {
                'field_name': field_name,
                'original_value': original_value,
                'validated_value': None,
                'confidence_score': 0.3,
                'source': source,
                'status': 'needs_review'
            }
        
        if not original_value:
            # New value found
            return {
                'field_name': field_name,
                'original_value': None,
                'validated_value': validated_value,
                'confidence_score': 0.8,
                'source': source,
                'status': 'validated'
            }
        
        # Normalize for comparison
        orig_norm = self._normalize_value(original_value)
        valid_norm = self._normalize_value(validated_value)
        
        if orig_norm == valid_norm:
            confidence = base_confidence
            status = 'validated'
            discrepancy_reason = None
        else:
            confidence = 0.5
            status = 'discrepancy'
            discrepancy_reason = f'Mismatch: original="{original_value}", validated="{validated_value}"'
        
        return {
            'field_name': field_name,
            'original_value': original_value,
            'validated_value': validated_value,
            'confidence_score': confidence,
            'source': source,
            'status': status,
            'discrepancy_reason': discrepancy_reason
        }
    
    def _validate_address(self, provider: Provider, address_data: Dict,
                         source: str, base_confidence: float) -> Dict:
        """Validate address"""
        original_address = {
            'line1': provider.address_line1,
            'city': provider.city,
            'state': provider.state,
            'zip_code': provider.zip_code
        }
        
        validated_address = {
            'line1': address_data.get('line1', ''),
            'city': address_data.get('city', ''),
            'state': address_data.get('state', ''),
            'zip_code': address_data.get('zip_code', '')
        }
        
        # Compare addresses
        matches = 0
        total = 0
        
        for key in ['line1', 'city', 'state', 'zip_code']:
            if validated_address[key]:
                total += 1
                if original_address[key] and self._normalize_value(original_address[key]) == self._normalize_value(validated_address[key]):
                    matches += 1
        
        confidence = (matches / total * base_confidence) if total > 0 else 0.3
        status = 'validated' if matches == total and total > 0 else 'discrepancy'
        
        discrepancy_reason = None
        if status == 'discrepancy':
            discrepancy_reason = f"Address mismatch: {matches}/{total} fields match"
        
        return {
            'field_name': 'address',
            'original_value': str(original_address),
            'validated_value': str(validated_address),
            'confidence_score': confidence,
            'source': source,
            'status': status,
            'discrepancy_reason': discrepancy_reason
        }
    
    def _normalize_value(self, value: Optional[str]) -> str:
        """Normalize value for comparison"""
        if not value:
            return ''
        return value.strip().upper().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    
    def _construct_website_url(self, provider: Provider) -> Optional[str]:
        """Construct potential website URL (simplified - in production would use search)"""
        # This is a placeholder - in production, would use Google search API
        # or other methods to find provider websites
        return None
    
    def save_validation_results(self, provider: Provider, validation_results: Dict):
        """Save validation results to database"""
        for validation in validation_results.get('validations', []):
            result = ValidationResult(
                provider_id=provider.id,
                validation_type='contact',
                field_name=validation['field_name'],
                original_value=validation.get('original_value'),
                validated_value=validation.get('validated_value'),
                confidence_score=validation['confidence_score'],
                source=validation.get('source'),
                status=validation.get('status', 'pending'),
                discrepancy_reason=validation.get('discrepancy_reason')
            )
            db.session.add(result)
        
        # Update provider status based on validation results
        overall_confidence = validation_results.get('overall_confidence', 0.0)
        discrepancies = validation_results.get('discrepancies', [])
        validations = validation_results.get('validations', [])
        
        # Always update status if we have validation results (which we should now)
        if validations:
            # Check if there are format issues or major discrepancies
            has_format_issues = any(
                v.get('status') == 'needs_review' and 'format' in v.get('field_name', '')
                for v in validations
            )
            
            # Check completeness
            completeness_validation = next(
                (v for v in validations if v.get('field_name') == 'data_completeness'),
                None
            )
            is_complete = completeness_validation and completeness_validation.get('status') == 'validated'
            
            # Determine status based on confidence and data quality
            if overall_confidence >= 0.75 and not has_format_issues and is_complete:
                provider.status = 'validated'
            elif overall_confidence >= 0.6 and not has_format_issues:
                # Good data quality, mark as validated
                provider.status = 'validated'
            elif discrepancies or has_format_issues or overall_confidence < 0.5:
                provider.status = 'needs_review'
            else:
                # Medium confidence, good enough to validate
                provider.status = 'validated'
        else:
            # No validations performed (shouldn't happen now), keep as pending
            provider.status = 'pending'
        
        db.session.commit()

