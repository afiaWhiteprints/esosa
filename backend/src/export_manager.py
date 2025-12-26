"""
Export Manager - Handle different export formats

Supports: JSON, Markdown, CSV
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging


class ExportManager:
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def export_research(self, data: Dict[str, Any], format: str = 'json') -> str:
        """Export research data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == 'json':
            return self._export_json(data, f"research_{timestamp}")
        elif format == 'markdown':
            return self._export_research_markdown(data, f"research_{timestamp}")
        elif format == 'csv':
            return self._export_research_csv(data, f"research_{timestamp}")
        else:
            self.logger.error(f"Unknown format: {format}")
            return ""

    def export_episode(self, data: Dict[str, Any], format: str = 'json') -> str:
        """Export episode data in specified format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == 'json':
            return self._export_json(data, f"episode_{timestamp}")
        elif format == 'markdown':
            return self._export_episode_markdown(data, f"episode_{timestamp}")
        else:
            self.logger.error(f"Unknown format: {format}")
            return ""

    def _export_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export as JSON"""
        filepath = Path(self.output_dir) / f"{filename}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"Exported JSON: {filepath}")
        return str(filepath)

    def _export_research_markdown(self, data: Dict[str, Any], filename: str) -> str:
        """Export research as Markdown"""
        filepath = Path(self.output_dir) / f"{filename}.md"

        md = []
        md.append(f"# Research Report")
        md.append(f"*Generated: {data.get('timestamp', 'N/A')}*\n")

        # Keywords
        keywords = data.get('search_keywords', [])
        if keywords:
            md.append(f"## Keywords")
            md.append(', '.join(keywords) + "\n")

        # Niche
        niche = data.get('podcast_niche', '')
        if niche:
            md.append(f"**Niche:** {niche}\n")

        # Platforms
        platforms = data.get('platforms_succeeded', [])
        if platforms:
            md.append(f"## Platforms Analyzed")
            for platform in platforms:
                md.append(f"- {platform.replace('_', ' ').title()}")
            md.append("")

        # Ranked Topics
        ranked_topics = data.get('ranked_topics', [])
        if ranked_topics:
            md.append(f"## Top Topics (Ranked)")
            for i, topic in enumerate(ranked_topics[:10], 1):
                md.append(f"### {i}. {topic.get('title', 'Untitled')}")
                md.append(f"**Score:** {topic.get('unified_score', 'N/A')} | **Platform:** {topic.get('source_platform', 'N/A')}\n")

                desc = topic.get('description', '')
                if desc:
                    md.append(desc + "\n")

                # Key points
                points = topic.get('key_points', [])
                if points:
                    md.append("**Key Points:**")
                    for point in points:
                        md.append(f"- {point}")
                    md.append("")

                # Unique angle
                angle = topic.get('unique_angle', '')
                if angle:
                    md.append(f"**Unique Angle:** {angle}\n")

        # Twitter Results
        twitter = data.get('twitter_results', {})
        if twitter and 'error' not in twitter:
            md.append(f"## Twitter Insights")

            engagement = twitter.get('engagement_analysis', {})
            if engagement:
                md.append(f"- **Tweets Analyzed:** {engagement.get('total_tweets', 0)}")
                md.append(f"- **Avg Likes:** {engagement.get('avg_likes', 0):.0f}")
                md.append(f"- **Avg Retweets:** {engagement.get('avg_retweets', 0):.0f}\n")

            trending = twitter.get('trending_topics', [])
            if trending:
                md.append("**Trending Topics:**")
                for topic in trending[:5]:
                    md.append(f"- {topic.get('topic', 'N/A')} ({topic.get('count', 0)} mentions)")
                md.append("")

        # TikTok Results
        tiktok = data.get('tiktok_results', {})
        if tiktok and 'error' not in tiktok:
            md.append(f"## TikTok Insights")

            md.append(f"- **Videos Analyzed:** {tiktok.get('videos_analyzed', 0)}")

            hashtags = tiktok.get('top_hashtags', [])
            if hashtags:
                md.append("\n**Top Hashtags:**")
                for tag in hashtags[:10]:
                    md.append(f"- #{tag}")
                md.append("")

        # Threads Results
        threads = data.get('threads_results', {})
        if threads and 'error' not in threads:
            md.append(f"## Threads Insights")
            md.append(f"- **Posts Analyzed:** {threads.get('posts_analyzed', 0)}\n")

        # Reddit Results
        reddit = data.get('reddit_results', {})
        if reddit and 'error' not in reddit:
            md.append(f"## Reddit Insights")

            md.append(f"- **Posts Analyzed:** {reddit.get('posts_analyzed', 0)}")

            subreddits = reddit.get('top_subreddits', [])
            if subreddits:
                md.append("\n**Top Subreddits:**")
                for sub in subreddits[:10]:
                    md.append(f"- r/{sub}")
                md.append("")

        # Cross-platform insights
        insights = data.get('cross_platform_insights', {})
        if insights and 'error' not in insights:
            md.append(f"## Cross-Platform Insights")

            engagement_comp = insights.get('engagement_comparison', {})
            if engagement_comp:
                highest = engagement_comp.get('highest_engagement_platform', '')
                if highest:
                    md.append(f"**Highest Engagement:** {highest.replace('_', ' ').title()}\n")

            common_themes = insights.get('topic_analysis', {}).get('common_themes', [])
            if common_themes:
                md.append("**Common Themes Across Platforms:**")
                for theme in common_themes:
                    md.append(f"- {theme}")
                md.append("")

        # Topic warnings
        warnings = data.get('topic_warnings', [])
        if warnings:
            md.append(f"## ⚠️ Previously Covered Topics")
            for warning in warnings[:3]:
                similarity = warning.get('similarity', 0) * 100
                md.append(f"- {warning.get('topic', 'N/A')} ({similarity:.0f}% similar)")
            md.append("")

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))

        self.logger.info(f"Exported Markdown: {filepath}")
        return str(filepath)

    def _export_research_csv(self, data: Dict[str, Any], filename: str) -> str:
        """Export ranked topics as CSV"""
        filepath = Path(self.output_dir) / f"{filename}.csv"

        ranked_topics = data.get('ranked_topics', [])
        if not ranked_topics:
            self.logger.warning("No ranked topics to export")
            return ""

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'rank', 'title', 'score', 'platform', 'relevance_score',
                'description', 'niche_alignment', 'unique_angle'
            ])

            writer.writeheader()

            for i, topic in enumerate(ranked_topics, 1):
                writer.writerow({
                    'rank': i,
                    'title': topic.get('title', ''),
                    'score': topic.get('unified_score', 0),
                    'platform': topic.get('source_platform', '').replace('_results', ''),
                    'relevance_score': topic.get('relevance_score', 0),
                    'description': topic.get('description', ''),
                    'niche_alignment': topic.get('niche_alignment', ''),
                    'unique_angle': topic.get('unique_angle', '')
                })

        self.logger.info(f"Exported CSV: {filepath}")
        return str(filepath)

    def _export_episode_markdown(self, data: Dict[str, Any], filename: str) -> str:
        """Export episode as Markdown"""
        filepath = Path(self.output_dir) / f"{filename}.md"

        md = []
        md.append(f"# {data.get('topic', 'Episode Outline')}")
        md.append(f"*Generated: {data.get('timestamp', 'N/A')}*\n")

        # Episode details
        md.append(f"**Duration:** {data.get('duration_minutes', 30)} minutes")
        md.append(f"**Style:** {data.get('host_style', 'conversational').title()}")
        md.append(f"**Audience:** {data.get('target_audience', 'general').title()}\n")

        # Outline
        outline = data.get('outline', {})
        if outline:
            md.append(f"## Episode Outline\n")

            title = outline.get('title', '')
            if title:
                md.append(f"**Title:** {title}\n")

            description = outline.get('description', '')
            if description:
                md.append(f"**Description:** {description}\n")

            # Segments
            segments = outline.get('segments', [])
            if segments:
                md.append(f"### Segments\n")
                for segment in segments:
                    seg_name = segment.get('name', 'Segment')
                    duration = segment.get('duration_minutes', 0)
                    md.append(f"#### {seg_name} ({duration} min)\n")

                    points = segment.get('talking_points', [])
                    if points:
                        for point in points:
                            md.append(f"- {point}")
                        md.append("")

        # Talking points
        talking_points = data.get('talking_points', [])
        if talking_points:
            md.append(f"## Talking Points\n")
            for point in talking_points:
                md.append(f"- {point}")
            md.append("")

        # Intro/Outro
        intro_outro = data.get('intro_outro', {})
        if intro_outro:
            intro = intro_outro.get('intro', '')
            if intro:
                md.append(f"## Intro\n")
                md.append(intro + "\n")

            outro = intro_outro.get('outro', '')
            if outro:
                md.append(f"## Outro\n")
                md.append(outro + "\n")

        # Show notes
        show_notes = data.get('show_notes', {})
        if show_notes:
            notes_text = show_notes.get('show_notes', '')
            if notes_text:
                md.append(f"## Show Notes\n")
                md.append(notes_text + "\n")

        # Social media
        social = data.get('social_media_content', {})
        if social:
            md.append(f"## Social Media Content\n")

            twitter = social.get('twitter', [])
            if twitter and twitter[0]:
                md.append(f"### Twitter/X\n")
                md.append(twitter[0] + "\n")

            linkedin = social.get('linkedin', [])
            if linkedin and linkedin[0]:
                md.append(f"### LinkedIn\n")
                md.append(linkedin[0] + "\n")

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))

        self.logger.info(f"Exported Markdown: {filepath}")
        return str(filepath)
