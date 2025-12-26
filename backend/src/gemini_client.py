from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import json
import re

load_dotenv()


def clean_json_response(text: str) -> str:
    """Clean markdown code blocks and extract JSON from response text."""
    text = text.strip()

    # Remove markdown code blocks using regex (handles ```json, ```, with newlines)
    # Pattern matches ```json or ``` at start, and ``` at end
    pattern = r'^```(?:json)?\s*\n?(.*?)\n?```$'
    match = re.match(pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    # Also handle cases where only the start or end marker exists
    if text.startswith('```json'):
        text = text[7:].strip()
    elif text.startswith('```'):
        text = text[3:].strip()

    if text.endswith('```'):
        text = text[:-3].strip()

    return text


class GeminiError(Exception):
    """Custom exception for Gemini failures to trigger fallback"""
    pass


class GeminiClient:
    def __init__(self, prompt_manager=None):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash'

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Load prompt manager
        if prompt_manager:
            self.prompt_manager = prompt_manager
        else:
            from .prompt_manager import PromptManager
            self.prompt_manager = PromptManager()

    def analyze_tweets_for_topics(self,
                                    tweets: List[Dict[str, Any]],
                                    reddit_posts: List[Dict[str, Any]],
                                    tiktok_posts: List[Dict[str, Any]],
                                    threads_posts: List[Dict[str, Any]],
                                    podcast_niche: str = "",
                                    podcast_description: str = "",
                                    target_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Analyze tweets to extract potential podcast topics

        Args:
            tweets: List of tweet data
            reddit_posts: List of Reddit post data
            tiktok_posts: List of TikTok post data
            threads_posts: List of Threads post data
            podcast_niche: The podcast's niche/domain
            podcast_description: Detailed description of the podcast
            target_keywords: List of target keywords for the podcast

        Returns:
            Dictionary with topic suggestions
        """
        if not tweets:
            return {"topics": [], "analysis": "No tweets to analyze"}

        tweet_texts = [tweet['text'] for tweet in tweets[:20]]
        reddit_texts = [post['title'] for post in reddit_posts[:20]]
        tiktok_texts = [post['text'] for post in tiktok_posts[:20]]
        threads_texts = [post['text'] for post in threads_posts[:20]]

        combined_text = "\n".join(tweet_texts + reddit_texts + tiktok_texts + threads_texts)

        context_info = []
        if podcast_niche:
            context_info.append(f"Podcast Niche: {podcast_niche}")
        if podcast_description:
            context_info.append(f"Podcast Description: {podcast_description}")
        if target_keywords:
            context_info.append(f"Target Keywords: {', '.join(target_keywords)}")

        context_section = "\n".join(context_info) if context_info else "Podcast Niche: General"

        # Use prompt template
        prompt = self.prompt_manager.format_analyze_topics(context_section, combined_text)

        try:
            response_text = self.generate_content(prompt)
            self.logger.info(f"Response length: {len(response_text)} chars")

            try:
                clean_text = clean_json_response(response_text)
                result = json.loads(clean_text)
                self.logger.info(f"Successfully parsed JSON response")
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse JSON response: {e}. Raw text: {response_text[:300]}...")
                result = {
                    "topics": [],
                    "analysis": response_text,
                    "error": "Could not parse structured response"
                }

            topics_count = len(result.get('topics', []))
            self.logger.info(f"Generated {topics_count} topic suggestions")

            if topics_count == 0:
                self.logger.warning("No topic suggestions generated. This might indicate an issue with the prompt or API response.")

            return result

        except Exception as e:
            self.logger.error(f"Error analyzing tweets: {str(e)}")
            return {"error": str(e), "topics": []}

    def generate_episode_outline(self, topic: str, talking_points: List[str] = None, duration_minutes: int = 30) -> Dict[str, Any]:
        """
        Generate a detailed episode outline for a given topic

        Args:
            topic: The main topic for the episode
            talking_points: Optional list of specific points to cover
            duration_minutes: Target episode duration in minutes

        Returns:
            Dictionary with episode outline
        """
        talking_points_text = ""
        if talking_points:
            talking_points_text = f"\nSpecific talking points to include:\n" + "\n".join(f"- {point}" for point in talking_points)

        prompt = f"""
        Create a detailed podcast episode outline for the following topic:

        Topic: {topic}
        Target Duration: {duration_minutes} minutes
        {talking_points_text}

        Please provide a comprehensive outline including:
        1. Episode title (catchy and SEO-friendly)
        2. Brief episode description
        3. Detailed segment breakdown with time allocations
        4. Key talking points for each segment
        5. Potential questions to explore
        6. Call-to-action ideas
        7. SEO keywords for the episode

        Format as JSON:
        {{
            "title": "Episode Title",
            "description": "Episode description",
            "duration_minutes": {duration_minutes},
            "segments": [
                {{
                    "name": "Segment Name",
                    "duration_minutes": 5,
                    "talking_points": ["point1", "point2"],
                    "questions": ["question1", "question2"]
                }}
            ],
            "call_to_action": "CTA text",
            "seo_keywords": ["keyword1", "keyword2"],
            "prep_notes": "Additional preparation notes"
        }}
        """

        try:
            response_text = self.generate_content(prompt)
            self.logger.info(f"response length: {len(response_text)} chars")
            try:
                clean_text = clean_json_response(response_text)
                result = json.loads(clean_text)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse episode outline JSON: {e}")
                result = {
                    "title": topic,
                    "outline": response_text,
                    "error": "Could not parse structured response"
                }

            self.logger.info(f"Generated outline for topic: {topic}")
            return result

        except Exception as e:
            self.logger.error(f"Error generating outline: {str(e)}")
            return {"error": str(e)}

    def generate_talking_points(self, topic: str, audience_level: str = "general", perspective: str = "") -> List[str]:
        """
        Generate specific talking points for a topic

        Args:
            topic: The topic to generate talking points for
            audience_level: Target audience level (beginner, intermediate, advanced, general)
            perspective: Specific perspective or angle to take

        Returns:
            List of talking points
        """
        prompt = f"""
        Generate 8-10 specific talking points for a podcast discussion on: {topic}

        Audience Level: {audience_level}
        {f"Perspective/Angle: {perspective}" if perspective else ""}

        Make the talking points:
        - Engaging and discussion-worthy
        - Appropriate for the audience level
        - Varied in depth and approach
        - Include both factual and opinion-based points
        - Actionable where possible

        Return as a simple list, one point per line, starting with a dash.
        """

        try:
            response_text = self.generate_content(prompt)
            self.logger.info(f"response length: {len(response_text)} chars")
            talking_points = [
                line.strip().lstrip('- ').strip()
                for line in response_text.split('\n')
                if line.strip() and line.strip().startswith('-')
            ]

            self.logger.info(f"Generated {len(talking_points)} talking points for: {topic}")
            return talking_points

        except Exception as e:
            self.logger.error(f"Error generating talking points: {str(e)}")
            return []

    def generate_content(self, prompt: str, temperature: float = 0.7, system_message: str = None) -> str:
        """
        Generic method to generate content using Gemini API

        Args:
            prompt: The user prompt to send to the AI
            temperature: Temperature for response generation (0.0 to 2.0)
            system_message: System message to set AI behavior

        Returns:
            Generated content string
        """
        try:
            # Use prompt manager's system message if none provided
            if system_message is None:
                system_message = self.prompt_manager.get_system_message()

            full_prompt = f"{system_message}\n\n{prompt}"

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature
                )
            )

            content = response.text
            self.logger.info(f"Generated content successfully, length: {len(content)} chars")
            return content

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise GeminiError(f"Gemini API error: {str(e)}")

    def synthesize_content(self, tweets: List[Dict[str, Any]], custom_prompt: str) -> str:
        """
        Custom content synthesis with user-defined prompt

        Args:
            tweets: List of tweet data
            custom_prompt: Custom prompt for content generation

        Returns:
            Generated content string
        """
        if not tweets:
            return "No content to synthesize"

        tweet_texts = [tweet['text'] for tweet in tweets[:30]]
        combined_text = "\n".join(tweet_texts)

        full_prompt = f"""
        {custom_prompt}

        Based on these social media posts:
        {combined_text}
        """

        return self.generate_content(full_prompt)
