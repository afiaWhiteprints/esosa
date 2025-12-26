"""
Restore script - Restore from a backup

Extracts a backup zip to the output directory
"""

import os
import shutil
from pathlib import Path

def list_backups():
    project_root = Path(__file__).parent.parent
    backup_dir = project_root / 'backups'

    if not backup_dir.exists():
        print("❌ No backups directory found.")
        return []

    backups = sorted(backup_dir.glob('backup_*.zip'), reverse=True)
    return backups

def restore_backup(backup_file=None):
    project_root = Path(__file__).parent.parent
    output_dir = project_root / 'output'

    backups = list_backups()

    if not backups:
        print("❌ No backups found.")
        return

    # If no backup specified, use most recent
    if not backup_file:
        backup_file = backups[0]
        print(f"Using most recent backup: {backup_file.name}")
    else:
        backup_file = Path(backup_file)

    if not backup_file.exists():
        print(f"❌ Backup file not found: {backup_file}")
        return

    # Confirm before restoring
    print(f"\n⚠️  This will replace the current output directory with:")
    print(f"   {backup_file.name}")
    print(f"   Size: {backup_file.stat().st_size / (1024 * 1024):.2f} MB")

    response = input("\nContinue? (yes/no): ").lower().strip()
    if response != 'yes':
        print("❌ Restore cancelled.")
        return

    # Backup current output if it exists
    if output_dir.exists():
        print("\n📦 Backing up current output before restore...")
        temp_backup = project_root / 'backups' / f"pre_restore_{Path(backup_file).stem}"
        shutil.make_archive(str(temp_backup), 'zip', output_dir)
        print(f"   Current output saved to: {temp_backup}.zip")

    # Clear output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # Extract backup
    print(f"\n📂 Restoring from {backup_file.name}...")
    shutil.unpack_archive(backup_file, output_dir)

    # Count restored files
    files = list(output_dir.rglob('*'))
    print(f"✅ Restore complete!")
    print(f"   Files restored: {len(files)}")

if __name__ == '__main__':
    print("=" * 50)
    print("RESTORE FROM BACKUP")
    print("=" * 50)

    backups = list_backups()
    if backups:
        print("\nAvailable backups:")
        for i, backup in enumerate(backups, 1):
            size = backup.stat().st_size / (1024 * 1024)
            print(f"{i}. {backup.name} ({size:.2f} MB)")

        print("\n")
        restore_backup()
    else:
        print("No backups found.")

    print("=" * 50)
