import yaml
import os
import random
from typing import Dict, Any, List, Optional
import logging


class ConfigManager:
    def __init__(self, config_file: str = 'files/config.yaml', api_config_file: str = 'files/api_config.yaml'):
        self.config_file = config_file
        self.api_config_file = api_config_file
        self.config = {}
        self.api_config = {}

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.load_config()
        self.load_api_config()

    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.error(f"Config file not found: {self.config_file}")
                raise FileNotFoundError(f"Configuration file '{self.config_file}' not found")

            with open(self.config_file, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file) or {}

            self.logger.info(f"Configuration loaded from {self.config_file}")

        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            raise

    def load_api_config(self) -> None:
        """Load API configuration from YAML file"""
        try:
            if not os.path.exists(self.api_config_file):
                self.logger.warning(f"API config file not found: {self.api_config_file}")
                self.api_config = {}
                return

            with open(self.api_config_file, 'r', encoding='utf-8') as file:
                raw_config = yaml.safe_load(file) or {}

            # Replace environment variable placeholders
            self.api_config = self._replace_env_vars(raw_config)

            self.logger.info(f"API configuration loaded from {self.api_config_file}")

        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing API YAML config: {str(e)}")
            self.api_config = {}
        except Exception as e:
            self.logger.error(f"Error loading API config: {str(e)}")
            self.api_config = {}

    def _replace_env_vars(self, config: Any) -> Any:
        """Recursively replace ${VAR} placeholders with environment variables"""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            var_name = config[2:-1]
            return os.getenv(var_name, config)
        return config

    def get_api_config(self, platform: str) -> Dict[str, Any]:
        """Get API configuration for a specific platform"""
        return self.api_config.get(platform, {})

    def get_research_config(self) -> Dict[str, Any]:
        """Get research-specific configuration"""
        research_config = self.config.get('research', {})
        
        # Get keyword selection settings from config
        use_random_keywords = research_config.get('use_random_keywords', True)
        keyword_count = research_config.get('random_keyword_count', 10)
        
        # Parse all keywords
        all_keywords = self._parse_keywords(research_config.get('keywords', ''))
        
        # Select keywords (random or all)
        if use_random_keywords and len(all_keywords) > keyword_count:
            selected_keywords = random.sample(all_keywords, keyword_count)
            self.logger.info(f"🎲 Randomly selected {len(selected_keywords)} keywords from {len(all_keywords)} total: {selected_keywords}")
        else:
            selected_keywords = all_keywords
            if use_random_keywords:
                self.logger.info(f"Using all {len(selected_keywords)} keywords (less than requested {keyword_count})")
        
        # Get platform configurations
        twitter_config = research_config.get('twitter', {})
        tiktok_config = research_config.get('tiktok', {})
        threads_config = research_config.get('threads', {})
        reddit_config = research_config.get('reddit', {})

        return {
            'keywords': selected_keywords,
            'all_keywords': all_keywords,  # Keep reference to full list
            'niche': research_config.get('niche', ''),
            'description': research_config.get('description', ''),
            'max_tweets': research_config.get('max_tweets', 100),
            'days_back': research_config.get('days_back', 7),
            'generate_pdf': research_config.get('generate_pdf', True),
            'use_random_keywords': use_random_keywords,
            'random_keyword_count': keyword_count,
            'keyword_selection': 'random' if use_random_keywords else 'all',
            # Twitter settings
            'twitter_enabled': twitter_config.get('enabled', True),
            'twitter_max_tweets': twitter_config.get('max_tweets', 5),
            'twitter_days_back': twitter_config.get('days_back', 7),
            'twitter_use_random_keywords': twitter_config.get('use_random_keywords', False),
            'twitter_random_keyword_count': twitter_config.get('random_keyword_count', 10),
            # TikTok settings
            'tiktok_enabled': tiktok_config.get('enabled', True),
            'tiktok_max_videos': tiktok_config.get('max_videos', 5),
            'tiktok_regions': tiktok_config.get('regions', ['us', 'ng']),
            'tiktok_days_back': tiktok_config.get('days_back', 7),
            'tiktok_use_random_keywords': tiktok_config.get('use_random_keywords', False),
            'tiktok_random_keyword_count': tiktok_config.get('random_keyword_count', 10),
            # Threads settings
            'threads_enabled': threads_config.get('enabled', True),
            'threads_max_posts': threads_config.get('max_posts', 5),
            'threads_days_back': threads_config.get('days_back', 7),
            'threads_use_random_keywords': threads_config.get('use_random_keywords', False),
            'threads_random_keyword_count': threads_config.get('random_keyword_count', 10),
            # Reddit settings
            'reddit_enabled': reddit_config.get('enabled', True),
            'reddit_max_posts': reddit_config.get('max_posts', 5),
            'reddit_days_back': reddit_config.get('days_back', 7),
            'reddit_use_random_keywords': reddit_config.get('use_random_keywords', False),
            'reddit_random_keyword_count': reddit_config.get('random_keyword_count', 10)
        }

    def get_episode_config(self) -> Dict[str, Any]:
        """Get episode generation configuration"""
        episode_config = self.config.get('episode', {})
        
        return {
            'topic': episode_config.get('topic', ''),
            'talking_points': episode_config.get('talking_points', []),
            'duration_minutes': episode_config.get('duration_minutes', 30),
            'host_style': episode_config.get('host_style', 'conversational'),
            'target_audience': episode_config.get('target_audience', 'general'),
            'generate_pdf': episode_config.get('generate_pdf', True)
        }

    def get_interview_config(self) -> Dict[str, Any]:
        """Get interview preparation configuration"""
        interview_config = self.config.get('interview', {})
        if not interview_config:
            # Return default empty config if interview section is not present
            return {
                'guest_info': {
                    'name': '',
                    'expertise': '',
                    'background': '',
                    'twitter_handle': ''
                },
                'topic': '',
                'duration_minutes': 30,
                'generate_pdf': True
            }
        
        guest_config = interview_config.get('guest', {})
        
        return {
            'guest_info': {
                'name': guest_config.get('name', ''),
                'expertise': guest_config.get('expertise', ''),
                'background': guest_config.get('background', ''),
                'twitter_handle': guest_config.get('twitter_handle', '')
            },
            'topic': interview_config.get('topic', ''),
            'duration_minutes': interview_config.get('duration_minutes', 30),
            'generate_pdf': interview_config.get('generate_pdf', True)
        }

    def get_competition_config(self) -> Dict[str, Any]:
        """Get competitive analysis configuration"""
        competition_config = self.config.get('competition', {})
        
        return {
            'keywords': self._parse_keywords(competition_config.get('keywords', '')),
            'generate_pdf': competition_config.get('generate_pdf', True)
        }

    def get_output_config(self) -> Dict[str, Any]:
        """Get output configuration"""
        output_config = self.config.get('output', {})
        
        return {
            'directory': output_config.get('directory', 'output'),
            'format': output_config.get('format', 'pdf'),
            'include_timestamps': output_config.get('include_timestamps', True)
        }

    def get_general_config(self) -> Dict[str, Any]:
        """Get general configuration"""
        general_config = self.config.get('general', {})
        podcast_config = general_config.get('podcast', {})
        
        return {
            'mode': general_config.get('mode', 'research'),
            'podcast': {
                'name': podcast_config.get('name', 'Your Podcast'),
                'host_name': podcast_config.get('host_name', 'Your Host'),
                'website': podcast_config.get('website', '')
            },
            'verbosity': general_config.get('verbosity', 'summary')
        }

    def _parse_keywords(self, keywords_str: str) -> List[str]:
        """Parse comma-separated keywords string into list"""
        if not keywords_str:
            return []
        return [keyword.strip() for keyword in keywords_str.split(',') if keyword.strip()]

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        mode = self.get_general_config()['mode']
        
        if mode == 'research':
            research_config = self.get_research_config()
            if not research_config['keywords']:
                issues.append("Research mode requires keywords to be specified")
        
        elif mode == 'episode':
            episode_config = self.get_episode_config()
            if not episode_config['topic']:
                issues.append("Episode mode requires a topic to be specified")
        
        elif mode == 'interview':
            # Only validate if interview section exists in config
            if 'interview' not in self.config:
                issues.append("Interview mode requires 'interview' section in config file. Uncomment and fill the interview section.")
            else:
                interview_config = self.get_interview_config()
                if not interview_config['guest_info']['name']:
                    issues.append("Interview mode requires guest name to be specified")
                if not interview_config['topic']:
                    issues.append("Interview mode requires interview topic to be specified")
        
        elif mode == 'competition':
            # Only validate if competition section exists in config
            if 'competition' not in self.config:
                issues.append("Competition mode requires 'competition' section in config file. Uncomment and fill the competition section.")
            else:
                competition_config = self.get_competition_config()
                if not competition_config['keywords']:
                    issues.append("Competition mode requires keywords to be specified")
        
        elif mode == 'research_to_episode':
            research_config = self.get_research_config()
            if not research_config['keywords']:
                issues.append("Research-to-episode mode requires keywords to be specified")
        
        elif mode == 'chat':
            pass  # Chat mode is always valid
        
        else:
            issues.append(f"Invalid mode '{mode}'. Must be one of: research, episode, interview, competition, research_to_episode, chat")
        
        return issues

    def update_config(self, section: str, key: str, value: Any) -> None:
        """Update a specific configuration value"""
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
        self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")
            raise

    def create_sample_config(self, output_file: str = 'config_sample.yaml') -> None:
        """Create a sample configuration file"""
        sample_config = {
            'research': {
                'keywords': 'AI,technology,startups',
                'niche': 'Technology',
                'description': 'A podcast about emerging technologies and their impact',
                'max_tweets': 100,
                'generate_pdf': True
            },
            'episode': {
                'topic': 'The Future of Artificial Intelligence',
                'talking_points': [],
                'duration_minutes': 30,
                'host_style': 'conversational',
                'target_audience': 'general',
                'generate_pdf': True
            },
            'output': {
                'directory': 'output',
                'format': 'pdf',
                'include_timestamps': True
            },
            'general': {
                'mode': 'research',
                'podcast': {
                    'name': 'Your Podcast Name',
                    'host_name': 'Your Name',
                    'website': 'https://yourpodcast.com'
                },
                'verbosity': 'summary'
            }
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                yaml.dump(sample_config, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Sample configuration created: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Error creating sample config: {str(e)}")
            raise

    def print_current_config(self) -> None:
        """Print current configuration in a readable format"""
        mode = self.get_general_config()['mode']
        
        print("=" * 50)
        print("CURRENT PODCAST ASSISTANT CONFIGURATION")
        print("=" * 50)
        
        general = self.get_general_config()
        print(f"Mode: {mode.title()}")
        print(f"Podcast: {general['podcast']['name']}")
        print(f"Host: {general['podcast']['host_name']}")
        print(f"Verbosity: {general['verbosity']}")
        print()
        
        if mode == 'research' or mode == 'research_to_episode':
            config = self.get_research_config()
            print(f"{mode.replace('_', '-').upper()} SETTINGS:")
            if config['keyword_selection'] == 'random':
                print(f"  Keyword Selection: Random ({config['random_keyword_count']} from {len(config['all_keywords'])})")
                print(f"  Current Selection: {', '.join(config['keywords'][:5])}{'...' if len(config['keywords']) > 5 else ''}")
            else:
                print(f"  Keyword Selection: All keywords")
                print(f"  Keywords: {', '.join(config['keywords'][:5])}{'...' if len(config['keywords']) > 5 else ''}")
            print(f"  Niche: {config['niche']}")
            print(f"  Max Tweets: {config['max_tweets']}")
            print(f"  Generate PDF: {config['generate_pdf']}")
            if config['description']:
                print(f"  Description: {config['description'][:100]}...")
            
            # Show platform configurations
            print("\n  PLATFORM INTEGRATIONS:")
            print(f"    Twitter: {'✅ Enabled' if config['twitter_enabled'] else '❌ Disabled'} (Max: {config['twitter_max_tweets']} tweets)")
            if config['twitter_enabled']:
                print(f"      Random Keywords: {'Yes' if config['twitter_use_random_keywords'] else 'No'}")

            print(f"    TikTok: {'✅ Enabled' if config['tiktok_enabled'] else '❌ Disabled'} (Max: {config['tiktok_max_videos']} videos)")
            if config['tiktok_enabled']:
                print(f"      Regions: {', '.join(config['tiktok_regions'])}")
                print(f"      Random Keywords: {'Yes' if config['tiktok_use_random_keywords'] else 'No'}")

            print(f"    Threads: {'✅ Enabled' if config['threads_enabled'] else '❌ Disabled'} (Max: {config['threads_max_posts']} posts)")
            if config['threads_enabled']:
                print(f"      Random Keywords: {'Yes' if config['threads_use_random_keywords'] else 'No'}")

            print(f"    Reddit: {'✅ Enabled' if config['reddit_enabled'] else '❌ Disabled'} (Max: {config['reddit_max_posts']} posts)")
            if config['reddit_enabled']:
                print(f"      Random Keywords: {'Yes' if config['reddit_use_random_keywords'] else 'No'}")
        
        elif mode == 'episode':
            config = self.get_episode_config()
            print("EPISODE SETTINGS:")
            print(f"  Topic: {config['topic']}")
            print(f"  Duration: {config['duration_minutes']} minutes")
            print(f"  Style: {config['host_style']}")
            print(f"  Audience: {config['target_audience']}")
            print(f"  Generate PDF: {config['generate_pdf']}")
            if config['talking_points']:
                print(f"  Talking Points: {len(config['talking_points'])} specified")
        
        elif mode == 'interview':
            if 'interview' in self.config:
                config = self.get_interview_config()
                print("INTERVIEW SETTINGS:")
                print(f"  Guest: {config['guest_info']['name']}")
                print(f"  Expertise: {config['guest_info']['expertise']}")
                print(f"  Topic: {config['topic']}")
                print(f"  Duration: {config['duration_minutes']} minutes")
                print(f"  Generate PDF: {config['generate_pdf']}")
            else:
                print("INTERVIEW SETTINGS: Not configured (section commented out)")
        
        elif mode == 'competition':
            if 'competition' in self.config:
                config = self.get_competition_config()
                print("COMPETITION ANALYSIS SETTINGS:")
                print(f"  Keywords: {', '.join(config['keywords'])}")
                print(f"  Generate PDF: {config['generate_pdf']}")
            else:
                print("COMPETITION SETTINGS: Not configured (section commented out)")
        
        output = self.get_output_config()
        print(f"\nOUTPUT:")
        print(f"  Directory: {output['directory']}")
        print(f"  Format: {output['format']}")
        print(f"  Timestamps: {output['include_timestamps']}")
        print("=" * 50)