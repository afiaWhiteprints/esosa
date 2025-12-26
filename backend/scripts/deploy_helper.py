"""
Pre-deployment checklist and helper
"""

import os
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent

def check_environment():
    """Check if environment is ready for deployment"""
    print("\n🔍 ENVIRONMENT CHECK")
    print("-" * 50)

    # Check .env exists
    env_file = project_root / '.env'
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found (may use environment variables)")

    # Check required env vars
    required_vars = ['GEMINI_API_KEY', 'RAPIDAPI_KEY']
    missing = []

    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} set")
        else:
            print(f"❌ {var} missing")
            missing.append(var)

    # Check optional vars
    if os.getenv('GDRIVE_ENABLED') == 'true':
        print("✅ Google Drive sync enabled")
        if (project_root / 'credentials.json').exists():
            print("   ✅ credentials.json found")
        else:
            print("   ⚠️  credentials.json missing (required for Drive)")
    else:
        print("⚠️  Google Drive sync disabled")

    return len(missing) == 0

def check_output_dir():
    """Check output directory"""
    print("\n📁 OUTPUT DIRECTORY CHECK")
    print("-" * 50)

    output_dir = project_root / 'output'
    if not output_dir.exists():
        print("⚠️  No output/ directory (no data to backup)")
        return False

    files = list(output_dir.rglob('*'))
    if not files:
        print("⚠️  output/ directory is empty")
        return False

    print(f"✅ Found {len(files)} files in output/")

    # Show key files
    history = output_dir / 'topic_history.json'
    sessions = output_dir / 'sessions_index.json'

    if history.exists():
        print("   ✅ topic_history.json")
    if sessions.exists():
        print("   ✅ sessions_index.json")

    return True

def run_backup():
    """Run backup script"""
    print("\n💾 BACKUP")
    print("-" * 50)

    backup_script = project_root / 'scripts' / 'backup.py'
    if not backup_script.exists():
        print("❌ backup.py not found")
        return False

    print("Running backup...")
    os.system(f'python "{backup_script}"')
    return True

def show_gdrive_status():
    """Show Google Drive sync status"""
    print("\n☁️  GOOGLE DRIVE STATUS")
    print("-" * 50)

    if os.getenv('GDRIVE_ENABLED') != 'true':
        print("Google Drive sync is DISABLED")
        print("\nTo enable:")
        print("1. Set GDRIVE_ENABLED=true in .env")
        print("2. Run: python scripts/setup_gdrive.py")
        return

    try:
        sys.path.insert(0, str(project_root / 'src'))
        from google_drive_sync import GoogleDriveSync

        gdrive = GoogleDriveSync(enabled=True)
        if gdrive.enabled:
            print("✅ Google Drive sync is ACTIVE")
            files = gdrive.list_files()
            print(f"   Files in Drive: {len(files)}")
            print("\n   Your data will auto-sync on every save")
        else:
            print("⚠️  Google Drive configured but not working")
            print("   Run: python scripts/setup_gdrive.py")

    except Exception as e:
        print(f"⚠️  Google Drive check failed: {str(e)}")

def main():
    print("=" * 50)
    print("PRE-DEPLOYMENT CHECKLIST")
    print("=" * 50)

    # Run checks
    env_ok = check_environment()
    has_data = check_output_dir()
    show_gdrive_status()

    # Recommendation
    print("\n📋 RECOMMENDATIONS")
    print("-" * 50)

    if not env_ok:
        print("❌ Fix missing environment variables before deploying")
        return

    if has_data:
        print("✅ You have data to backup")
        response = input("\nRun backup now? (yes/no): ").lower().strip()
        if response == 'yes':
            run_backup()
    else:
        print("⚠️  No data to backup (first deployment)")

    # Final checklist
    print("\n✅ DEPLOYMENT CHECKLIST")
    print("-" * 50)
    print("[ ] Backup created (if you have data)")
    print("[ ] Environment variables set in Render")
    print("[ ] .gitignore updated (no secrets committed)")
    print("[ ] Google Drive setup (optional)")
    print("\nReady to deploy!")

if __name__ == '__main__':
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed")

    main()
    print("=" * 50)
