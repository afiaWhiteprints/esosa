"""
Prompt Manager - Load and format AI prompts from templates

Allows customization of AI behavior without changing code
"""

import yaml
import os
from typing import Dict, Any
import logging


class PromptManager:
    def __init__(self, prompts_file: str = 'src/files/prompts.yaml'):
        self.prompts_file = prompts_file
        self.prompts = {}

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.load_prompts()

    def load_prompts(self):
        """Load prompts from YAML file"""
        if not os.path.exists(self.prompts_file):
            self.logger.warning(f"Prompts file not found: {self.prompts_file}")
            self.prompts = self._default_prompts()
            return

        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f) or {}
            self.logger.info(f"Loaded prompts from {self.prompts_file}")
        except Exception as e:
            self.logger.error(f"Error loading prompts: {str(e)}")
            self.prompts = self._default_prompts()

    def get_system_message(self) -> str:
        """Get the system message for AI"""
        return self.prompts.get('system_message', 'You are a helpful podcast assistant.')

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get a prompt template and format it with provided values"""
        prompt_data = self.prompts.get(prompt_name, {})
        template = prompt_data.get('prompt', '')

        if not template:
            self.logger.warning(f"Prompt not found: {prompt_name}")
            return ""

        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing template variable in {prompt_name}: {e}")
            return template

    def format_analyze_topics(self, context_section: str, combined_text: str) -> str:
        """Format the analyze topics prompt"""
        return self.get_prompt(
            'analyze_topics',
            context_section=context_section,
            combined_text=combined_text
        )

    def format_generate_outline(self, topic: str, duration_minutes: int, talking_points_text: str = "") -> str:
        """Format the generate outline prompt"""
        return self.get_prompt(
            'generate_outline',
            topic=topic,
            duration_minutes=duration_minutes,
            talking_points_text=talking_points_text
        )

    def format_generate_talking_points(self, topic: str, audience_level: str = "general", perspective_text: str = "") -> str:
        """Format the generate talking points prompt"""
        return self.get_prompt(
            'generate_talking_points',
            topic=topic,
            audience_level=audience_level,
            perspective_text=perspective_text
        )

    def format_generate_script(self, topic: str, host_style: str, target_audience: str, outline_json: str) -> str:
        """Format the generate script prompt"""
        return self.get_prompt(
            'generate_script',
            topic=topic,
            host_style=host_style,
            target_audience=target_audience,
            outline_json=outline_json
        )

    def format_generate_intro(self, podcast_name: str, episode_title: str, host_name: str) -> str:
        """Format the generate intro prompt"""
        return self.get_prompt(
            'generate_intro',
            podcast_name=podcast_name,
            episode_title=episode_title,
            host_name=host_name
        )

    def format_generate_outro(self, podcast_name: str, episode_title: str, host_name: str, takeaways_text: str = "") -> str:
        """Format the generate outro prompt"""
        return self.get_prompt(
            'generate_outro',
            podcast_name=podcast_name,
            episode_title=episode_title,
            host_name=host_name,
            takeaways_text=takeaways_text
        )

    def format_generate_interview_questions(self, guest_name: str, guest_background: str,
                                           guest_expertise: str, topic: str, interview_length: int) -> str:
        """Format the generate interview questions prompt"""
        return self.get_prompt(
            'generate_interview_questions',
            guest_name=guest_name,
            guest_background=guest_background,
            guest_expertise=guest_expertise,
            topic=topic,
            interview_length=interview_length
        )

    def format_generate_show_notes(self, sections_text: str, key_points_text: str = "", resources_text: str = "") -> str:
        """Format the generate show notes prompt"""
        return self.get_prompt(
            'generate_show_notes',
            sections_text=sections_text,
            key_points_text=key_points_text,
            resources_text=resources_text
        )

    def format_generate_social_media(self, title: str, key_points: str) -> str:
        """Format the generate social media prompt"""
        return self.get_prompt(
            'generate_social_media',
            title=title,
            key_points=key_points
        )

    def format_generate_segment_script(self, segment_name: str, duration_minutes: int,
                                      talking_points: str, questions: str, host_style: str) -> str:
        """Format the generate segment script prompt"""
        return self.get_prompt(
            'generate_segment_script',
            segment_name=segment_name,
            duration_minutes=duration_minutes,
            talking_points=talking_points,
            questions=questions,
            host_style=host_style
        )

    def format_custom_synthesis(self, custom_prompt: str, combined_text: str) -> str:
        """Format the custom synthesis prompt"""
        return self.get_prompt(
            'custom_synthesis',
            custom_prompt=custom_prompt,
            combined_text=combined_text
        )

    def format_chat_assistant(self, user_input: str) -> str:
        """Format the chat assistant prompt"""
        return self.get_prompt(
            'chat_assistant',
            user_input=user_input
        )

    def _default_prompts(self) -> Dict[str, Any]:
        """Return minimal default prompts if file not found"""
        return {
            'system_message': 'You are a helpful podcast assistant.',
            'analyze_topics': {
                'prompt': 'Analyze these posts and suggest podcast topics: {combined_text}'
            }
        }
