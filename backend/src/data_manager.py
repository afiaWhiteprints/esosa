import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class DataManager:
    def __init__(self, data_dir: str = 'output', enable_gdrive: bool = None):
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, 'topic_history.json')
        self.sessions_file = os.path.join(data_dir, 'sessions_index.json')

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        os.makedirs(data_dir, exist_ok=True)
        self._init_history()
        self._init_sessions_index()

        # Initialize Google Drive sync if enabled
        if enable_gdrive is None:
            enable_gdrive = os.getenv('GDRIVE_ENABLED', 'false').lower() == 'true'

        self.gdrive_sync = None
        if enable_gdrive:
            try:
                from .google_drive_sync import GoogleDriveSync
                self.gdrive_sync = GoogleDriveSync(enabled=True)
                if self.gdrive_sync.enabled:
                    self.logger.info("✅ Google Drive sync enabled")
            except Exception as e:
                self.logger.warning(f"Google Drive sync not available: {str(e)}")

    def _init_history(self):
        """Initialize topic history file if it doesn't exist"""
        if not os.path.exists(self.history_file):
            self._save_json(self.history_file, {'topics': [], 'last_updated': datetime.now().isoformat()})

    def _init_sessions_index(self):
        """Initialize sessions index file"""
        if not os.path.exists(self.sessions_file):
            self._save_json(self.sessions_file, {'sessions': []})

    def save_session(self, session_data: Dict[str, Any], session_type: str) -> str:
        """Save a research session and index it"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{session_type}_{timestamp}.json"
        filepath = os.path.join(self.data_dir, filename)

        # Add metadata
        session_data['_metadata'] = {
            'session_type': session_type,
            'timestamp': datetime.now().isoformat(),
            'filename': filename
        }

        self._save_json(filepath, session_data)

        # Update sessions index
        self._update_sessions_index(filename, session_type, session_data)

        # Sync to Google Drive if enabled
        if self.gdrive_sync and self.gdrive_sync.enabled:
            self.gdrive_sync.upload_file(filepath)
            self.gdrive_sync.upload_file(self.sessions_file)
            self.gdrive_sync.upload_file(self.history_file)

        self.logger.info(f"Session saved: {filepath}")
        return filepath

    def load_session(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a previous session by filename"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def list_sessions(self, session_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent sessions"""
        index = self._load_json(self.sessions_file)
        sessions = index.get('sessions', [])

        if session_type:
            sessions = [s for s in sessions if s['type'] == session_type]

        # Sort by timestamp, most recent first
        sessions.sort(key=lambda x: x['timestamp'], reverse=True)

        return sessions[:limit]

    def add_topic_to_history(self, topic: str, episode_date: Optional[str] = None):
        """Mark a topic as covered"""
        history = self._load_json(self.history_file)

        history['topics'].append({
            'topic': topic,
            'episode_date': episode_date or datetime.now().isoformat(),
            'added_at': datetime.now().isoformat()
        })

        history['last_updated'] = datetime.now().isoformat()
        self._save_json(self.history_file, history)

        # Sync to Google Drive if enabled
        if self.gdrive_sync and self.gdrive_sync.enabled:
            self.gdrive_sync.upload_file(self.history_file)

        self.logger.info(f"Topic added to history: {topic}")

    def check_topic_covered(self, topic: str, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Check if topic was already covered (simple string matching)"""
        history = self._load_json(self.history_file)

        matches = []
        topic_lower = topic.lower()
        topic_words = set(topic_lower.split())

        for item in history['topics']:
            covered_topic = item['topic'].lower()
            covered_words = set(covered_topic.split())

            # Simple word overlap calculation
            if topic_words and covered_words:
                overlap = len(topic_words & covered_words)
                total = len(topic_words | covered_words)
                similarity = overlap / total if total > 0 else 0

                if similarity >= similarity_threshold:
                    matches.append({
                        **item,
                        'similarity': similarity
                    })

        return matches

    def get_topic_history(self) -> List[Dict[str, Any]]:
        """Get all covered topics"""
        history = self._load_json(self.history_file)
        return history.get('topics', [])

    def deduplicate_topics(self, topics: List[Dict[str, Any]], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Remove duplicate topics across platforms"""
        if not topics:
            return []

        unique_topics = []
        seen_topics = []

        for topic in topics:
            title = topic.get('title', '').lower()
            title_words = set(title.split())

            is_duplicate = False
            for seen in seen_topics:
                seen_words = set(seen.split())

                if title_words and seen_words:
                    overlap = len(title_words & seen_words)
                    total = len(title_words | seen_words)
                    similarity = overlap / total if total > 0 else 0

                    if similarity >= threshold:
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_topics.append(topic)
                seen_topics.append(title)

        removed = len(topics) - len(unique_topics)
        if removed > 0:
            self.logger.info(f"Removed {removed} duplicate topics")

        return unique_topics

    def rank_topics(self, platform_results: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Unified topic ranking across all platforms"""
        all_topics = []

        # Collect topics from all platforms
        for platform, results in platform_results.items():
            if 'error' in results:
                continue

            ai_suggestions = results.get('ai_topic_suggestions', {})
            topics = ai_suggestions.get('topics', [])

            for topic in topics:
                topic_copy = topic.copy()
                topic_copy['source_platform'] = platform

                # Get engagement metrics for this platform
                engagement = results.get('engagement_analysis', {})

                if platform == 'twitter_results':
                    avg_engagement = engagement.get('avg_likes', 0) + engagement.get('avg_retweets', 0)
                elif platform == 'tiktok_results':
                    avg_engagement = engagement.get('avg_likes', 0) + engagement.get('avg_shares', 0)
                elif platform == 'threads_results':
                    avg_engagement = engagement.get('avg_likes', 0)
                elif platform == 'reddit_results':
                    avg_engagement = engagement.get('avg_upvotes', 0)
                else:
                    avg_engagement = 0

                topic_copy['platform_engagement'] = avg_engagement
                all_topics.append(topic_copy)

        # Deduplicate
        unique_topics = self.deduplicate_topics(all_topics)

        # Calculate unified score
        for topic in unique_topics:
            relevance = topic.get('relevance_score', 5)
            engagement = topic.get('platform_engagement', 0)

            # Normalize engagement (0-10 scale)
            engagement_normalized = min(10, engagement / 100) if engagement > 0 else 0

            # Weighted score: 60% relevance, 40% engagement
            unified_score = (relevance * 0.6) + (engagement_normalized * 0.4)
            topic['unified_score'] = round(unified_score, 2)

        # Sort by unified score
        ranked_topics = sorted(unique_topics, key=lambda x: x.get('unified_score', 0), reverse=True)

        self.logger.info(f"Ranked {len(ranked_topics)} unique topics")
        return ranked_topics

    def _update_sessions_index(self, filename: str, session_type: str, session_data: Dict[str, Any]):
        """Update the sessions index"""
        index = self._load_json(self.sessions_file)

        # Extract key info for index
        session_info = {
            'filename': filename,
            'type': session_type,
            'timestamp': datetime.now().isoformat(),
            'keywords': session_data.get('search_keywords', []),
            'platforms': session_data.get('platforms_succeeded', [])
        }

        index['sessions'].append(session_info)
        self._save_json(self.sessions_file, index)

    def _save_json(self, filepath: str, data: Dict[str, Any]):
        """Save JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_json(self, filepath: str) -> Dict[str, Any]:
        """Load JSON file"""
        if not os.path.exists(filepath):
            return {}
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get basic usage statistics"""
        sessions = self.list_sessions(limit=1000)
        history = self.get_topic_history()

        # Count sessions by type
        session_types = {}
        for session in sessions:
            stype = session['type']
            session_types[stype] = session_types.get(stype, 0) + 1

        return {
            'total_sessions': len(sessions),
            'sessions_by_type': session_types,
            'topics_covered': len(history),
            'last_session': sessions[0] if sessions else None
        }

    def sync_all_to_drive(self):
        """Manually sync all files to Google Drive"""
        if not self.gdrive_sync or not self.gdrive_sync.enabled:
            self.logger.warning("Google Drive sync not enabled")
            return False

        self.logger.info("Syncing all files to Google Drive...")
        self.gdrive_sync.sync_folder(self.data_dir)
        self.logger.info("✅ Sync complete")
        return True

    def restore_from_drive(self):
        """Restore all files from Google Drive"""
        if not self.gdrive_sync or not self.gdrive_sync.enabled:
            self.logger.warning("Google Drive sync not enabled")
            return False

        self.logger.info("Restoring files from Google Drive...")
        files = self.gdrive_sync.list_files()

        restored = 0
        for file_info in files:
            filename = file_info['name']
            destination = os.path.join(self.data_dir, filename)
            if self.gdrive_sync.download_file(filename, destination):
                restored += 1

        self.logger.info(f"✅ Restored {restored} files from Google Drive")
        return True
