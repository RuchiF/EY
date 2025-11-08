"""
Setup script for Provider Directory Management System
"""
import os

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'reports']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == '__main__':
    print("Setting up Provider Directory Management System...")
    create_directories()
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. (Optional) Create .env file with API keys")
    print("3. Run the application: python main.py")
    print("4. Access the dashboard at http://localhost:5000")

