"""
Google Drive sync for automatic backups

Setup:
1. Create project at https://console.cloud.google.com
2. Enable Google Drive API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json to project root
5. Set GDRIVE_ENABLED=true in .env
"""

import os
import io
import json
from pathlib import Path
from typing import Optional
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class GoogleDriveSync:
    def __init__(self, enabled: bool = False):
        self.enabled = enabled and GDRIVE_AVAILABLE
        self.service = None
        self.folder_id = None

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        if not GDRIVE_AVAILABLE and enabled:
            self.logger.warning("Google Drive sync requested but google-auth libraries not installed")
            self.logger.warning("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            self.enabled = False

        if self.enabled:
            self._authenticate()
            self._setup_folder()

    def _authenticate(self):
        """Authenticate with Google Drive"""
        creds = None
        token_file = 'token.json'
        creds_file = 'credentials.json'

        # Load existing token
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(creds_file):
                    self.logger.error("credentials.json not found. Please download from Google Cloud Console")
                    self.enabled = False
                    return

                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save token
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
        self.logger.info("✅ Google Drive authenticated")

    def _setup_folder(self):
        """Create or find the PodcastAssistant folder in Drive"""
        if not self.service:
            return

        folder_name = 'PodcastAssistant_Data'

        # Search for existing folder
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        folders = results.get('files', [])

        if folders:
            self.folder_id = folders[0]['id']
            self.logger.info(f"Using existing Drive folder: {folder_name}")
        else:
            # Create folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            self.folder_id = folder.get('id')
            self.logger.info(f"Created Drive folder: {folder_name}")

    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file to Google Drive"""
        if not self.enabled or not self.service:
            return None

        try:
            file_name = os.path.basename(file_path)

            # Check if file already exists
            query = f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id)').execute()
            existing = results.get('files', [])

            file_metadata = {'name': file_name, 'parents': [self.folder_id]}
            media = MediaFileUpload(file_path, resumable=True)

            if existing:
                # Update existing file
                file = self.service.files().update(
                    fileId=existing[0]['id'],
                    media_body=media
                ).execute()
                self.logger.info(f"☁️  Updated in Drive: {file_name}")
            else:
                # Create new file
                file = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                self.logger.info(f"☁️  Uploaded to Drive: {file_name}")

            return file.get('id')

        except Exception as e:
            self.logger.error(f"Failed to upload {file_path}: {str(e)}")
            return None

    def download_file(self, file_name: str, destination: str) -> bool:
        """Download a file from Google Drive"""
        if not self.enabled or not self.service:
            return False

        try:
            # Find file
            query = f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])

            if not files:
                self.logger.warning(f"File not found in Drive: {file_name}")
                return False

            file_id = files[0]['id']

            # Download
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            # Write to destination
            with open(destination, 'wb') as f:
                f.write(fh.getvalue())

            self.logger.info(f"⬇️  Downloaded from Drive: {file_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to download {file_name}: {str(e)}")
            return False

    def sync_folder(self, local_folder: str):
        """Sync entire folder to Google Drive"""
        if not self.enabled:
            return

        local_path = Path(local_folder)
        if not local_path.exists():
            return

        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                self.upload_file(str(file_path))

    def list_files(self):
        """List all files in Drive folder"""
        if not self.enabled or not self.service:
            return []

        try:
            query = f"'{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime, size)'
            ).execute()
            return results.get('files', [])
        except Exception as e:
            self.logger.error(f"Failed to list files: {str(e)}")
            return []
