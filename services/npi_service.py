import requests
import time
from typing import Dict, Optional, List

class NPIService:
    """
    Service for interacting with the NPI Registry API
    """
    
    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()
    
    def search_by_npi(self, npi: str) -> Optional[Dict]:
        """Search for provider by NPI number"""
        try:
            params = {
                'version': '2.1',
                'number': npi
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('result_count', 0) > 0:
                return data['results'][0]
            return None
        except Exception as e:
            print(f"Error searching NPI {npi}: {str(e)}")
            return None
    
    def search_by_name(self, first_name: str, last_name: str, state: Optional[str] = None) -> List[Dict]:
        """Search for providers by name"""
        try:
            params = {
                'version': '2.1',
                'first_name': first_name,
                'last_name': last_name
            }
            
            if state:
                params['state'] = state
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get('results', [])
        except Exception as e:
            print(f"Error searching by name {first_name} {last_name}: {str(e)}")
            return []
    
    def extract_provider_info(self, npi_data: Dict) -> Dict:
        """Extract structured provider information from NPI response"""
        if not npi_data:
            return {}
        
        basic_info = npi_data.get('basic', {})
        addresses = npi_data.get('addresses', [])
        practice_locations = npi_data.get('practiceLocations', [])
        taxonomies = npi_data.get('taxonomies', [])
        
        # Get primary address
        primary_address = None
        for addr in addresses:
            if addr.get('address_purpose') == 'LOCATION':
                primary_address = addr
                break
        
        # Get primary taxonomy (specialty)
        primary_specialty = None
        if taxonomies:
            primary_specialty = taxonomies[0].get('desc', '')
        
        return {
            'npi': npi_data.get('number', ''),
            'first_name': basic_info.get('first_name', ''),
            'last_name': basic_info.get('last_name', ''),
            'middle_name': basic_info.get('middle_name', ''),
            'credential': basic_info.get('credential', ''),
            'gender': basic_info.get('gender', ''),
            'enumeration_type': basic_info.get('enumeration_type', ''),
            'specialty': primary_specialty,
            'address': {
                'line1': primary_address.get('address_1', '') if primary_address else '',
                'line2': primary_address.get('address_2', '') if primary_address else '',
                'city': primary_address.get('city', '') if primary_address else '',
                'state': primary_address.get('state', '') if primary_address else '',
                'zip_code': primary_address.get('postal_code', '') if primary_address else '',
                'phone': primary_address.get('telephone_number', '') if primary_address else ''
            } if primary_address else {},
            'taxonomies': [t.get('desc', '') for t in taxonomies],
            'practice_locations': practice_locations
        }
    
    def validate_provider(self, provider_data: Dict) -> Dict:
        """Validate provider data against NPI registry"""
        npi = provider_data.get('npi')
        if not npi:
            # Try to find by name
            first_name = provider_data.get('first_name', '')
            last_name = provider_data.get('last_name', '')
            state = provider_data.get('state')
            
            matches = self.search_by_name(first_name, last_name, state)
            if matches:
                npi_data = matches[0]
                npi = npi_data.get('number')
            else:
                return {
                    'valid': False,
                    'confidence': 0.0,
                    'message': 'Provider not found in NPI registry'
                }
        else:
            npi_data = self.search_by_npi(npi)
        
        if not npi_data:
            return {
                'valid': False,
                'confidence': 0.0,
                'message': 'Provider not found in NPI registry'
            }
        
        extracted_info = self.extract_provider_info(npi_data)
        
        # Compare with provided data
        discrepancies = []
        confidence_score = 1.0
        
        # Check name match
        if provider_data.get('first_name', '').upper() != extracted_info.get('first_name', '').upper():
            discrepancies.append('First name mismatch')
            confidence_score -= 0.2
        
        if provider_data.get('last_name', '').upper() != extracted_info.get('last_name', '').upper():
            discrepancies.append('Last name mismatch')
            confidence_score -= 0.2
        
        # Check address
        if provider_data.get('address_line1') and extracted_info.get('address', {}).get('line1'):
            if provider_data.get('address_line1', '').upper() not in extracted_info.get('address', {}).get('line1', '').upper():
                discrepancies.append('Address mismatch')
                confidence_score -= 0.1
        
        return {
            'valid': True,
            'confidence': max(0.0, confidence_score),
            'npi_data': extracted_info,
            'discrepancies': discrepancies,
            'message': 'Provider found in NPI registry'
        }

