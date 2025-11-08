from typing import Dict, List, Optional
from services.npi_service import NPIService
from services.web_scraper import WebScraper
from app.models import Provider
from app import db
import json

class InformationEnrichmentAgent:
    """
    Agent responsible for enriching provider information from public sources
    """
    
    def __init__(self, npi_api_key: Optional[str] = None):
        self.npi_service = NPIService(npi_api_key)
        self.web_scraper = WebScraper()
    
    def enrich_provider_info(self, provider: Provider) -> Dict:
        """Enrich provider information from multiple sources"""
        enrichment_results = {
            'provider_id': provider.id,
            'enriched_fields': [],
            'new_information': {},
            'confidence_scores': {}
        }
        
        provider_data = provider.to_dict()
        
        # 1. Enrich from NPI registry
        npi_data = None
        if provider.npi:
            npi_result = self.npi_service.search_by_npi(provider.npi)
            if npi_result:
                npi_data = self.npi_service.extract_provider_info(npi_result)
        else:
            # Try to find by name
            matches = self.npi_service.search_by_name(
                provider.first_name,
                provider.last_name,
                provider.state
            )
            if matches:
                npi_data = self.npi_service.extract_provider_info(matches[0])
        
        if npi_data:
            enrichment_results = self._merge_npi_data(provider, npi_data, enrichment_results)
        
        # 2. Enrich from web scraping
        if provider.practice_name:
            website_url = self._find_provider_website(provider)
            if website_url:
                scraped_data = self.web_scraper.scrape_provider_website(website_url, provider.full_name)
                enrichment_results = self._merge_scraped_data(provider, scraped_data, enrichment_results)
        
        # 3. Enrich specialties and taxonomies
        if npi_data and npi_data.get('taxonomies'):
            enrichment_results = self._enrich_specialties(provider, npi_data['taxonomies'], enrichment_results)
        
        return enrichment_results
    
    def _merge_npi_data(self, provider: Provider, npi_data: Dict, results: Dict) -> Dict:
        """Merge NPI data into provider record"""
        # Update NPI if missing
        if not provider.npi and npi_data.get('npi'):
            provider.npi = npi_data['npi']
            results['enriched_fields'].append('npi')
            results['new_information']['npi'] = npi_data['npi']
            results['confidence_scores']['npi'] = 0.95
        
        # Update address if missing or incomplete
        npi_address = npi_data.get('address', {})
        if npi_address:
            if not provider.address_line1 and npi_address.get('line1'):
                provider.address_line1 = npi_address['line1']
                results['enriched_fields'].append('address_line1')
                results['new_information']['address_line1'] = npi_address['line1']
                results['confidence_scores']['address'] = 0.9
            
            if not provider.city and npi_address.get('city'):
                provider.city = npi_address['city']
                results['enriched_fields'].append('city')
            
            if not provider.state and npi_address.get('state'):
                provider.state = npi_address['state']
                results['enriched_fields'].append('state')
            
            if not provider.zip_code and npi_address.get('zip_code'):
                provider.zip_code = npi_address['zip_code']
                results['enriched_fields'].append('zip_code')
            
            if not provider.phone and npi_address.get('phone'):
                provider.phone = npi_address['phone']
                results['enriched_fields'].append('phone')
                results['new_information']['phone'] = npi_address['phone']
                results['confidence_scores']['phone'] = 0.85
        
        # Update name components if missing
        if not provider.middle_name and npi_data.get('middle_name'):
            provider.middle_name = npi_data['middle_name']
            results['enriched_fields'].append('middle_name')
        
        return results
    
    def _merge_scraped_data(self, provider: Provider, scraped_data: Dict, results: Dict) -> Dict:
        """Merge scraped web data into provider record"""
        if not provider.phone and scraped_data.get('phone'):
            provider.phone = scraped_data['phone']
            results['enriched_fields'].append('phone')
            results['new_information']['phone'] = scraped_data['phone']
            results['confidence_scores']['phone'] = 0.7
        
        if not provider.email and scraped_data.get('email'):
            provider.email = scraped_data['email']
            results['enriched_fields'].append('email')
            results['new_information']['email'] = scraped_data['email']
            results['confidence_scores']['email'] = 0.7
        
        if scraped_data.get('specialties'):
            current_specialty = provider.specialty or ''
            new_specialties = [s for s in scraped_data['specialties'] if s not in current_specialty]
            if new_specialties:
                if provider.specialty:
                    provider.specialty = f"{provider.specialty}, {', '.join(new_specialties)}"
                else:
                    provider.specialty = ', '.join(new_specialties)
                results['enriched_fields'].append('specialty')
                results['new_information']['specialty'] = provider.specialty
                results['confidence_scores']['specialty'] = 0.6
        
        return results
    
    def _enrich_specialties(self, provider: Provider, taxonomies: List[str], results: Dict) -> Dict:
        """Enrich specialties from taxonomies"""
        if taxonomies:
            # Use primary taxonomy if specialty is missing
            if not provider.specialty and taxonomies:
                provider.specialty = taxonomies[0]
                results['enriched_fields'].append('specialty')
                results['new_information']['specialty'] = taxonomies[0]
                results['confidence_scores']['specialty'] = 0.9
            
            # Store all taxonomies as additional info
            if len(taxonomies) > 1:
                if not provider.affiliations:
                    provider.affiliations = []
                provider.affiliations.extend(taxonomies[1:])
        
        return results
    
    def _find_provider_website(self, provider: Provider) -> Optional[str]:
        """Find provider website (simplified - would use search API in production)"""
        # Placeholder - in production would use Google Search API
        return None
    
    def save_enrichment_results(self, provider: Provider, enrichment_results: Dict):
        """Save enriched data to provider record"""
        db.session.commit()
        return enrichment_results

