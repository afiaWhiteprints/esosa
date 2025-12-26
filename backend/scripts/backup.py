"""
Simple backup script - Run before deploying to Render

Creates a timestamped zip of the output directory
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_output():
    # Paths relative to project root
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'output'
    backup_dir = project_root / 'backups'

    # Create backups directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)

    if not output_dir.exists():
        print(f"❌ No {output_dir}/ directory found. Nothing to backup.")
        return

    # Check if output has files
    files = list(output_dir.rglob('*'))
    if not files:
        print(f"❌ {output_dir}/ is empty. Nothing to backup.")
        return

    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = backup_dir / backup_name

    print(f"📦 Creating backup: {backup_name}.zip")
    shutil.make_archive(str(backup_path), 'zip', output_dir)

    # Get backup size
    backup_file = f"{backup_path}.zip"
    size_mb = os.path.getsize(backup_file) / (1024 * 1024)

    print(f"✅ Backup created: {backup_file}")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Files: {len(files)}")

    # List recent backups
    backups = sorted(backup_dir.glob('backup_*.zip'), reverse=True)
    print(f"\n📚 Recent backups ({len(backups)} total):")
    for backup in backups[:5]:
        size = backup.stat().st_size / (1024 * 1024)
        date = backup.stem.replace('backup_', '')
        print(f"   - {backup.name} ({size:.2f} MB)")

    # Clean up old backups (keep last 10)
    if len(backups) > 10:
        print(f"\n🧹 Cleaning up old backups (keeping 10 most recent)...")
        for old_backup in backups[10:]:
            old_backup.unlink()
            print(f"   Deleted: {old_backup.name}")

if __name__ == '__main__':
    print("=" * 50)
    print("BACKUP OUTPUT DIRECTORY")
    print("=" * 50)
    backup_output()
    print("=" * 50)
