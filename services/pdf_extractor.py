import os
import json
from typing import Dict, List, Optional
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import io
import base64

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class PDFExtractor:
    """
    Service for extracting information from PDFs, including scanned documents
    Uses VLM (Vision Language Model) for better accuracy
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        self.openai_client = None
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=openai_api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def extract_from_pdf(self, pdf_path: str, use_vlm: bool = True) -> Dict:
        """Extract provider information from PDF"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            if not images:
                return {
                    'success': False,
                    'error': 'Could not extract images from PDF',
                    'data': {}
                }
            
            # Extract text from all pages
            extracted_text = []
            extracted_data = {}
            
            for i, image in enumerate(images):
                if use_vlm and self.openai_client:
                    # Use VLM for better extraction
                    page_data = self._extract_with_vlm(image)
                    if page_data:
                        extracted_data.update(page_data)
                else:
                    # Fallback to OCR
                    page_text = pytesseract.image_to_string(image)
                    extracted_text.append(page_text)
            
            if not use_vlm or not self.openai_client:
                # Parse OCR text
                full_text = '\n'.join(extracted_text)
                extracted_data = self._parse_ocr_text(full_text)
            
            return {
                'success': True,
                'data': extracted_data,
                'confidence': 0.85 if use_vlm else 0.70,
                'pages_processed': len(images)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _extract_with_vlm(self, image: Image.Image) -> Optional[Dict]:
        """Extract structured data using Vision Language Model"""
        if not self.openai_client:
            return None
        
        try:
            # Convert image to base64
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Prepare prompt for structured extraction
            prompt = """Extract provider information from this document. Return a JSON object with the following fields:
            - first_name
            - last_name
            - middle_name (if available)
            - npi (National Provider Identifier, if available)
            - phone
            - email
            - address_line1
            - address_line2 (if available)
            - city
            - state
            - zip_code
            - specialty
            - license_number
            - license_state
            - practice_name
            - board_certifications (as array)
            - education (as array)
            
            If a field is not found, set it to null. Return only valid JSON."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                extracted_json = json.loads(json_match.group())
                return extracted_json
            
            return None
        except Exception as e:
            print(f"Error in VLM extraction: {e}")
            return None
    
    def _parse_ocr_text(self, text: str) -> Dict:
        """Parse OCR text to extract provider information"""
        import re
        
        data = {}
        
        # Extract phone
        phone_pattern = r'(\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone'] = phones[0]
        
        # Extract email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text)
        if emails:
            data['email'] = emails[0]
        
        # Extract NPI
        npi_pattern = r'NPI[:\s]*(\d{10})'
        npi_match = re.search(npi_pattern, text, re.IGNORECASE)
        if npi_match:
            data['npi'] = npi_match.group(1)
        
        # Extract name (look for common patterns)
        name_patterns = [
            r'Name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Provider[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'Dr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                name_parts = match.group(1).split()
                if len(name_parts) >= 2:
                    data['first_name'] = name_parts[0]
                    data['last_name'] = name_parts[-1]
                    if len(name_parts) > 2:
                        data['middle_name'] = ' '.join(name_parts[1:-1])
                break
        
        # Extract address
        address_pattern = r'(\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr)[\s,]+[\w\s,]+(?:[A-Z]{2})[\s,]+(?:\d{5}(?:-\d{4})?))'
        addr_match = re.search(address_pattern, text, re.IGNORECASE)
        if addr_match:
            addr_str = addr_match.group(1)
            parts = addr_str.split(',')
            if len(parts) >= 2:
                data['address_line1'] = parts[0].strip()
                data['city'] = parts[1].strip()
                if len(parts) >= 3:
                    state_zip = parts[2].strip().split()
                    if len(state_zip) >= 2:
                        data['state'] = state_zip[0]
                        data['zip_code'] = state_zip[1]
        
        # Extract specialty
        specialty_keywords = ['Specialty', 'Specialization', 'Practice']
        for keyword in specialty_keywords:
            pattern = f'{keyword}[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
            match = re.search(pattern, text)
            if match:
                data['specialty'] = match.group(1)
                break
        
        # Extract license
        license_pattern = r'License[:\s]*([A-Z0-9]+)'
        license_match = re.search(license_pattern, text, re.IGNORECASE)
        if license_match:
            data['license_number'] = license_match.group(1)
        
        return data
    
    def extract_from_image(self, image_path: str, use_vlm: bool = True) -> Dict:
        """Extract information from image file"""
        try:
            image = Image.open(image_path)
            
            if use_vlm and self.openai_client:
                extracted_data = self._extract_with_vlm(image)
                return {
                    'success': True,
                    'data': extracted_data or {},
                    'confidence': 0.85
                }
            else:
                text = pytesseract.image_to_string(image)
                extracted_data = self._parse_ocr_text(text)
                return {
                    'success': True,
                    'data': extracted_data,
                    'confidence': 0.70
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }

