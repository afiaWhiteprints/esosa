from typing import List, Dict, Any, Optional, Union
import json
from .gemini_client import GeminiClient
from .openrouter_client import OpenRouterClient
import logging

class ScriptGenerator:
    def __init__(self, ai_client: Optional[Union[GeminiClient, OpenRouterClient]] = None):
        if ai_client:
            self.ai_client = ai_client
        else:
            # Try Gemini first, fallback to OpenRouter
            try:
                self.ai_client = GeminiClient()
            except ValueError:
                self.ai_client = OpenRouterClient()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_full_script(self, 
                           topic: str, 
                           outline: Dict[str, Any], 
                           host_style: str = "conversational",
                           target_audience: str = "general") -> Dict[str, Any]:
        """
        Generate a complete podcast script based on topic and outline
        
        Args:
            topic: Main episode topic
            outline: Episode outline from AI client (Gemini or OpenRouter)
            host_style: Hosting style (conversational, professional, casual, educational)
            target_audience: Target audience description
            
        Returns:
            Dictionary with complete script
        """
        prompt = f"""
        Create a complete podcast script for the following episode:
        
        Topic: {topic}
        Host Style: {host_style}
        Target Audience: {target_audience}
        
        Episode Outline:
        {json.dumps(outline, indent=2)}
        
        Generate a full script including:
        1. Opening/Introduction (with hook)
        2. Segment transitions
        3. Detailed talking points with natural flow
        4. Questions and discussion prompts
        5. Sponsor break placements (if applicable)
        6. Closing/Call-to-action
        7. Timing cues for each section
        
        Make the script sound natural and {host_style}. Include [PAUSE], [EMPHASIS], and [TRANSITION] cues.
        
        Format as JSON:
        {{
            "episode_title": "Title",
            "total_duration": "30 minutes",
            "script_sections": [
                {{
                    "section_name": "Opening",
                    "duration": "2 minutes",
                    "script": "Full script text with cues",
                    "notes": "Direction notes for host"
                }}
            ],
            "production_notes": "Additional notes for editing"
        }}
        """
        
        try:
            response_text = self.ai_client.generate_content(prompt)
            try:
                # Clean up the response text - remove markdown code blocks
                clean_text = response_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                script = json.loads(clean_text)
            except json.JSONDecodeError:
                script = {
                    "episode_title": topic,
                    "script_raw": response_text,
                    "error": "Could not parse structured response"
                }
            
            self.logger.info(f"Generated full script for: {topic}")
            return script
            
        except Exception as e:
            self.logger.error(f"Error generating script: {str(e)}")
            return {"error": str(e)}

    def create_segment_scripts(self, segments: List[Dict[str, Any]], host_style: str = "conversational") -> List[Dict[str, Any]]:
        """
        Create detailed scripts for individual segments
        
        Args:
            segments: List of segment dictionaries from outline
            host_style: Hosting style
            
        Returns:
            List of segment scripts
        """
        segment_scripts = []
        
        for i, segment in enumerate(segments):
            prompt = f"""
            Create a detailed script for this podcast segment:
            
            Segment: {segment.get('name', f'Segment {i+1}')}
            Duration: {segment.get('duration_minutes', 5)} minutes
            Talking Points: {segment.get('talking_points', [])}
            Questions: {segment.get('questions', [])}
            Host Style: {host_style}
            
            Generate natural, flowing dialogue that covers all talking points.
            Include timing cues, emphasis marks, and transition phrases.
            Make it sound {host_style} and engaging.
            
            Provide the script as natural speaking text with [CUE] markers for:
            - [PAUSE] for natural breaks
            - [EMPHASIS] for important points  
            - [TRANSITION] for moving between topics
            """
            
            try:
                response_text = self.ai_client.generate_content(prompt)
                segment_scripts.append({
                    "segment_name": segment.get('name', f'Segment {i+1}'),
                    "duration": segment.get('duration_minutes', 5),
                    "script": response_text,
                    "talking_points_covered": segment.get('talking_points', [])
                })
                
            except Exception as e:
                self.logger.error(f"Error generating segment script: {str(e)}")
                segment_scripts.append({
                    "segment_name": segment.get('name', f'Segment {i+1}'),
                    "error": str(e)
                })
        
        self.logger.info(f"Generated scripts for {len(segment_scripts)} segments")
        return segment_scripts

    def generate_intro_outro(self, 
                           podcast_name: str = "Your Podcast",
                           episode_title: str = "",
                           host_name: str = "Your Host",
                           key_takeaways: List[str] = None) -> Dict[str, str]:
        """
        Generate intro and outro scripts
        
        Args:
            podcast_name: Name of the podcast
            episode_title: Title of the episode
            host_name: Host's name
            key_takeaways: Key points from the episode
            
        Returns:
            Dictionary with intro and outro scripts
        """
        # Generate Intro
        intro_prompt = f"""
        Create an engaging podcast intro for:
        
        Podcast: {podcast_name}
        Episode: {episode_title}
        Host: {host_name}
        
        Make it:
        - Energetic and welcoming
        - Include a hook that makes people want to listen
        - 30-45 seconds when spoken
        - Natural and conversational
        
        Include [MUSIC FADE] and [PAUSE] cues where appropriate.
        """
        
        # Generate Outro
        takeaways_text = ""
        if key_takeaways:
            takeaways_text = f"\nKey takeaways to recap:\n" + "\n".join(f"- {takeaway}" for takeaway in key_takeaways)
        
        outro_prompt = f"""
        Create a compelling podcast outro for:
        
        Podcast: {podcast_name}
        Episode: {episode_title}
        Host: {host_name}
        {takeaways_text}
        
        Include:
        - Brief recap of key points
        - Call to action (subscribe, rate, review)
        - Teaser for next episode (if applicable)
        - Thank you to listeners
        - 45-60 seconds when spoken
        
        Include [MUSIC FADE IN] cues.
        """
        
        try:
            intro_response = self.ai_client.generate_content(intro_prompt)
            outro_response = self.ai_client.generate_content(outro_prompt)
            
            return {
                "intro": intro_response,
                "outro": outro_response
            }
            
        except Exception as e:
            self.logger.error(f"Error generating intro/outro: {str(e)}")
            return {
                "intro": f"Welcome to {podcast_name}! I'm {host_name}.",
                "outro": f"Thanks for listening to {podcast_name}!",
                "error": str(e)
            }

    def create_interview_questions(self, 
                                 guest_info: Dict[str, str], 
                                 topic: str, 
                                 interview_length: int = 30) -> List[Dict[str, Any]]:
        """
        Generate interview questions for a guest
        
        Args:
            guest_info: Dictionary with guest information
            topic: Interview topic/theme
            interview_length: Interview duration in minutes
            
        Returns:
            List of question dictionaries
        """
        guest_name = guest_info.get('name', 'Guest')
        guest_background = guest_info.get('background', '')
        guest_expertise = guest_info.get('expertise', '')
        
        prompt = f"""
        Create interview questions for a {interview_length}-minute podcast interview:
        
        Guest: {guest_name}
        Background: {guest_background}
        Expertise: {guest_expertise}
        Topic: {topic}
        
        Generate 15-20 questions that:
        - Flow naturally from general to specific
        - Include warm-up questions
        - Cover the guest's expertise and background
        - Explore the main topic thoroughly
        - Include follow-up question suggestions
        - End with forward-looking questions
        
        Categorize questions as:
        - Warm-up (2-3 questions)
        - Background/Journey (3-4 questions) 
        - Topic Deep-dive (8-10 questions)
        - Personal/Future (2-3 questions)
        
        Format as a list with question categories.
        """
        
        try:
            response_text = self.ai_client.generate_content(prompt)
            
            # Parse the response to extract questions
            questions = []
            current_category = "General"
            
            for line in response_text.split('\n'):
                line = line.strip()
                if line and ':' in line and not line.startswith('Q') and not line.startswith('-'):
                    # This might be a category header
                    current_category = line.replace(':', '').strip()
                elif line and (line.startswith('-') or line.startswith('Q') or line.startswith('•')):
                    # This is a question
                    clean_question = line.lstrip('- Q•').strip()
                    if clean_question:
                        questions.append({
                            'category': current_category,
                            'question': clean_question,
                            'follow_up_notes': 'Adapt based on guest response'
                        })
            
            self.logger.info(f"Generated {len(questions)} interview questions")
            return questions
            
        except Exception as e:
            self.logger.error(f"Error generating interview questions: {str(e)}")
            return [{"error": str(e)}]

    def generate_show_notes(self, 
                          script_sections: List[Dict[str, Any]], 
                          key_points: List[str] = None,
                          resources: List[str] = None) -> Dict[str, Any]:
        """
        Generate show notes from script sections
        
        Args:
            script_sections: List of script sections
            key_points: Additional key points to highlight
            resources: List of resources/links mentioned
            
        Returns:
            Dictionary with formatted show notes
        """
        sections_text = "\n".join([
            f"Section: {section.get('section_name', 'Unknown')}\n{section.get('script', '')[:500]}..."
            for section in script_sections[:5]  # Limit to avoid token limits
        ])
        
        key_points_text = ""
        if key_points:
            key_points_text = f"\nAdditional key points:\n" + "\n".join(f"- {point}" for point in key_points)
        
        resources_text = ""
        if resources:
            resources_text = f"\nResources mentioned:\n" + "\n".join(f"- {resource}" for resource in resources)
        
        prompt = f"""
        Create professional show notes based on this podcast script:
        
        {sections_text}
        {key_points_text}
        {resources_text}
        
        Generate show notes including:
        1. Episode summary (2-3 sentences)
        2. Key topics covered (bulleted list)
        3. Timestamps for major sections
        4. Key takeaways/quotes
        5. Resources and links mentioned
        6. Contact information for guest (if interview)
        7. Call to action
        
        Format for easy reading and sharing.
        """
        
        try:
            response_text = self.ai_client.generate_content(prompt)
            
            return {
                "show_notes": response_text,
                "generated_at": "timestamp",
                "sections_analyzed": len(script_sections)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating show notes: {str(e)}")
            return {"error": str(e)}

    def create_social_media_content(self, episode_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate social media content for episode promotion
        
        Args:
            episode_info: Dictionary with episode information
            
        Returns:
            Dictionary with platform-specific content
        """
        title = episode_info.get('title', 'New Episode')
        key_points = episode_info.get('key_points', [])
        
        prompt = f"""
        Create social media promotion content for this podcast episode:
        
        Title: {title}
        Key Points: {key_points}
        
        Generate content for:
        1. Twitter/X (3 different tweets, under 280 chars each)
        2. LinkedIn (professional post, 1-2 paragraphs)
        3. Instagram (engaging caption with hashtags)
        4. Facebook (casual, conversation-starting post)
        
        Make each platform's content appropriate for that audience.
        Include relevant hashtags and call-to-actions.
        """
        
        try:
            response_text = self.ai_client.generate_content(prompt)
            
            # This would need parsing logic for different platforms
            # For now, return the raw response
            return {
                "twitter": [response_text[:280]],  # Truncate for Twitter
                "linkedin": [response_text],
                "instagram": [response_text],
                "facebook": [response_text],
                "raw_content": response_text
            }
            
        except Exception as e:
            self.logger.error(f"Error generating social media content: {str(e)}")
            return {"error": str(e)}