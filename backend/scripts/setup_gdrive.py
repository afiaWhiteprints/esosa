"""
First-time Google Drive setup

Run this after adding credentials.json to project root
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def setup_google_drive():
    print("=" * 50)
    print("GOOGLE DRIVE SETUP")
    print("=" * 50)

    # Check for credentials
    creds_file = project_root / 'credentials.json'
    if not creds_file.exists():
        print("\n❌ credentials.json not found!")
        print("\nSteps:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create project > Enable Drive API > Create OAuth Desktop credentials")
        print("3. Download credentials.json to project root")
        print("4. Run this script again")
        return

    print("\n✅ Found credentials.json")

    # Check if libraries installed
    try:
        from google.oauth2.credentials import Credentials
        print("✅ Google libraries installed")
    except ImportError:
        print("\n❌ Google libraries not installed")
        print("\nInstall with:")
        print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return

    # Try to authenticate
    print("\n🔐 Starting authentication...")
    print("Your browser will open. Grant Drive access.")

    try:
        from src.google_drive_sync import GoogleDriveSync

        gdrive = GoogleDriveSync(enabled=True)

        if gdrive.enabled and gdrive.service:
            print("\n✅ Authentication successful!")
            print(f"✅ Drive folder created: PodcastAssistant_Data")
            print(f"✅ token.json saved (auto-refreshes)")

            # Test upload
            print("\n📤 Testing upload...")
            test_file = project_root / 'output' / 'test.txt'
            test_file.parent.mkdir(exist_ok=True)
            test_file.write_text("Test file for Google Drive sync")

            file_id = gdrive.upload_file(str(test_file))
            if file_id:
                print("✅ Upload test successful!")
                test_file.unlink()

                # List files
                files = gdrive.list_files()
                print(f"\n📁 Files in Drive ({len(files)}):")
                for f in files[:5]:
                    size = int(f.get('size', 0)) / 1024
                    print(f"   - {f['name']} ({size:.1f} KB)")

                print("\n✅ Setup complete!")
                print("\nNext steps:")
                print("1. Add to .env: GDRIVE_ENABLED=true")
                print("2. Run your app normally")
                print("3. All saves will auto-sync to Drive")

        else:
            print("\n❌ Authentication failed")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    setup_google_drive()
    print("=" * 50)
