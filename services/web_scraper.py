import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import re
import time
from urllib.parse import urljoin, urlparse

class WebScraper:
    """
    Service for scraping provider information from websites
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_provider_website(self, url: str, provider_name: str) -> Dict:
        """Scrape provider information from their website"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract contact information
            phone_pattern = re.compile(r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
            
            text = soup.get_text()
            
            # Find phone numbers
            phones = phone_pattern.findall(text)
            phone = phones[0] if phones else None
            
            # Find email
            emails = email_pattern.findall(text)
            email = emails[0] if emails else None
            
            # Try to find address in structured format
            address = self._extract_address(soup, text)
            
            # Extract specialties/services
            specialties = self._extract_specialties(soup, text)
            
            return {
                'phone': phone,
                'email': email,
                'address': address,
                'specialties': specialties,
                'website_url': url,
                'confidence': 0.7 if phone or email else 0.4
            }
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return {
                'phone': None,
                'email': None,
                'address': None,
                'specialties': [],
                'website_url': url,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _extract_address(self, soup: BeautifulSoup, text: str) -> Optional[Dict]:
        """Extract address from webpage"""
        # Look for common address patterns
        address_patterns = [
            r'(\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way|Circle|Cir)[\s,]+[\w\s,]+(?:CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|AZ|MA|TN|IN|MO|MD|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|IA|AR|UT|NV|MS|KS|NM|NE|WV|ID|HI|NH|ME|RI|MT|DE|SD|ND|AK|VT|WY|DC)[\s,]+(?:\d{5}(?:-\d{4})?))',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Parse the address
                addr_str = matches[0]
                parts = addr_str.split(',')
                if len(parts) >= 2:
                    return {
                        'line1': parts[0].strip(),
                        'city': parts[1].strip() if len(parts) > 1 else '',
                        'state': parts[2].strip()[:2] if len(parts) > 2 else '',
                        'zip_code': parts[2].strip().split()[-1] if len(parts) > 2 else ''
                    }
        
        return None
    
    def _extract_specialties(self, soup: BeautifulSoup, text: str) -> List[str]:
        """Extract medical specialties from webpage"""
        # Common medical specialties to look for
        common_specialties = [
            'Cardiology', 'Dermatology', 'Endocrinology', 'Gastroenterology',
            'Hematology', 'Infectious Disease', 'Nephrology', 'Neurology',
            'Oncology', 'Pulmonology', 'Rheumatology', 'Urology',
            'Family Medicine', 'Internal Medicine', 'Pediatrics', 'Psychiatry',
            'Surgery', 'Orthopedics', 'Ophthalmology', 'Otolaryngology'
        ]
        
        found_specialties = []
        text_lower = text.lower()
        
        for specialty in common_specialties:
            if specialty.lower() in text_lower:
                found_specialties.append(specialty)
        
        return found_specialties
    
    def search_google_business(self, provider_name: str, city: str = None, state: str = None) -> Optional[Dict]:
        """Search for provider on Google Business (simulated - would use Google Maps API in production)"""
        # This is a placeholder - in production, use Google Maps API
        # For now, return None to indicate not found
        return None
    
    def validate_contact_info(self, provider_data: Dict, scraped_data: Dict) -> Dict:
        """Compare provider data with scraped data"""
        discrepancies = []
        confidence_scores = {}
        
        # Phone validation
        original_phone = provider_data.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        scraped_phone = scraped_data.get('phone', '').replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        if original_phone and scraped_phone:
            if original_phone == scraped_phone:
                confidence_scores['phone'] = 0.95
            else:
                confidence_scores['phone'] = 0.5
                discrepancies.append('Phone number mismatch')
        elif scraped_phone:
            confidence_scores['phone'] = 0.8  # Found new phone
        else:
            confidence_scores['phone'] = 0.3  # No phone found
        
        # Email validation
        original_email = provider_data.get('email', '').lower()
        scraped_email = scraped_data.get('email', '').lower()
        
        if original_email and scraped_email:
            if original_email == scraped_email:
                confidence_scores['email'] = 0.95
            else:
                confidence_scores['email'] = 0.5
                discrepancies.append('Email mismatch')
        elif scraped_email:
            confidence_scores['email'] = 0.8
        else:
            confidence_scores['email'] = 0.3
        
        # Address validation
        if scraped_data.get('address'):
            confidence_scores['address'] = 0.7
        else:
            confidence_scores['address'] = 0.3
        
        overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
        
        return {
            'confidence': overall_confidence,
            'field_scores': confidence_scores,
            'discrepancies': discrepancies,
            'scraped_data': scraped_data
        }

