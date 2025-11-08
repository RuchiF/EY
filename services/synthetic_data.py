from faker import Faker
import random
import json
from typing import List, Dict

fake = Faker()

# Medical specialties
MEDICAL_SPECIALTIES = [
    'Cardiology', 'Dermatology', 'Endocrinology', 'Family Medicine',
    'Gastroenterology', 'Hematology', 'Internal Medicine', 'Neurology',
    'Oncology', 'Orthopedics', 'Pediatrics', 'Psychiatry',
    'Pulmonology', 'Rheumatology', 'Surgery', 'Urology',
    'Ophthalmology', 'Otolaryngology', 'Anesthesiology', 'Emergency Medicine'
]

# US States
US_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

def generate_provider_profile(include_errors: bool = False) -> Dict:
    """Generate a synthetic provider profile"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    middle_name = fake.first_name() if random.random() > 0.5 else None
    
    state = random.choice(US_STATES)
    city = fake.city()
    zip_code = fake.zipcode()
    
    # Generate phone (sometimes with errors)
    if include_errors and random.random() > 0.7:
        phone = fake.phone_number()[:-1]  # Incomplete phone
    else:
        phone = fake.phone_number()
    
    # Generate email (sometimes with errors)
    if include_errors and random.random() > 0.7:
        email = f"{first_name.lower()}.{last_name.lower()}@invalid"  # Invalid domain
    else:
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
    
    # Generate address (sometimes outdated)
    address_line1 = fake.street_address()
    if include_errors and random.random() > 0.6:
        # Use old address format
        address_line1 = f"{random.randint(100, 9999)} Old Street"
    
    # Generate NPI (10 digits)
    npi = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    # Generate license number
    license_number = ''.join([random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(8)])
    
    # Specialty
    specialty = random.choice(MEDICAL_SPECIALTIES)
    
    # Practice name
    practice_name = f"{city} {specialty} Associates" if random.random() > 0.3 else None
    
    # Board certifications
    num_certs = random.randint(0, 3)
    board_certifications = []
    if num_certs > 0:
        cert_boards = ['ABIM', 'ABFM', 'ABP', 'ABMS', 'ABPN']
        board_certifications = random.sample(cert_boards, min(num_certs, len(cert_boards)))
    
    # Education
    education = []
    num_edu = random.randint(1, 3)
    for _ in range(num_edu):
        if random.random() > 0.5:
            education.append(f"{fake.company()} Medical School")
        else:
            education.append(f"{fake.state()} University School of Medicine")
    
    # Insurance networks
    networks = ['Medicare', 'Medicaid']
    if random.random() > 0.3:
        networks.append('Blue Cross Blue Shield')
    if random.random() > 0.5:
        networks.append('Aetna')
    if random.random() > 0.5:
        networks.append('UnitedHealthcare')
    
    return {
        'npi': npi,
        'first_name': first_name,
        'last_name': last_name,
        'middle_name': middle_name,
        'specialty': specialty,
        'practice_name': practice_name,
        'phone': phone,
        'email': email,
        'address_line1': address_line1,
        'address_line2': fake.secondary_address() if random.random() > 0.7 else None,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'license_number': license_number,
        'license_state': state,
        'board_certifications': board_certifications,
        'education': education,
        'insurance_networks': networks,
        'affiliations': [f"{city} Hospital"] if random.random() > 0.5 else []
    }

def generate_provider_dataset(count: int = 200, error_rate: float = 0.4) -> List[Dict]:
    """Generate a dataset of provider profiles"""
    providers = []
    
    for i in range(count):
        include_errors = random.random() < error_rate
        provider = generate_provider_profile(include_errors=include_errors)
        providers.append(provider)
    
    return providers

def save_providers_to_json(providers: List[Dict], filename: str = 'synthetic_providers.json'):
    """Save providers to JSON file"""
    with open(filename, 'w') as f:
        json.dump(providers, f, indent=2)
    return filename

def load_providers_from_json(filename: str = 'synthetic_providers.json') -> List[Dict]:
    """Load providers from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

