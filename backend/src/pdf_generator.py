from typing import Dict, Any, List
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import json
import logging

class PDFGenerator:
    # Brand colors for Filtered Therapy
    BRAND_PRIMARY = HexColor('#6B4E71')      # Deep purple
    BRAND_SECONDARY = HexColor('#9B7EA1')    # Light purple
    BRAND_ACCENT = HexColor('#E8B4BC')       # Soft pink
    BRAND_DARK = HexColor('#2D2D2D')         # Dark gray
    BRAND_LIGHT = HexColor('#F5F0F6')        # Light purple tint

    def __init__(self, output_directory: str = 'output'):
        self.output_directory = output_directory
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _setup_custom_styles(self):
        """Setup custom paragraph styles with Filtered Therapy branding"""
        # Main title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=28,
            spaceAfter=6,
            spaceBefore=20,
            textColor=self.BRAND_PRIMARY,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Brand subtitle
        self.styles.add(ParagraphStyle(
            name='BrandSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=30,
            textColor=self.BRAND_SECONDARY,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceBefore=25,
            spaceAfter=15,
            textColor=self.BRAND_PRIMARY,
            fontName='Helvetica-Bold',
            borderPadding=(10, 0, 10, 0)
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
            textColor=self.BRAND_SECONDARY,
            fontName='Helvetica-Bold'
        ))

        # Topic title style
        self.styles.add(ParagraphStyle(
            name='TopicTitle',
            parent=self.styles['Heading3'],
            fontSize=13,
            spaceBefore=12,
            spaceAfter=6,
            textColor=self.BRAND_PRIMARY,
            fontName='Helvetica-Bold',
            leftIndent=5
        ))

        # Body text style (override existing)
        self.styles['BodyText'].fontSize = 11
        self.styles['BodyText'].spaceAfter = 8
        self.styles['BodyText'].textColor = self.BRAND_DARK
        self.styles['BodyText'].leading = 16
        self.styles['BodyText'].fontName = 'Helvetica'

        # Key points style
        self.styles.add(ParagraphStyle(
            name='KeyPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=5,
            textColor=self.BRAND_DARK,
            bulletIndent=10,
            leading=14
        ))

        # Highlight box text
        self.styles.add(ParagraphStyle(
            name='HighlightText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.BRAND_DARK,
            backColor=self.BRAND_LIGHT,
            borderPadding=10
        ))

        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.BRAND_SECONDARY,
            alignment=TA_CENTER
        ))

    def _create_section_divider(self):
        """Create a styled horizontal divider"""
        return HRFlowable(
            width="100%",
            thickness=2,
            color=self.BRAND_ACCENT,
            spaceBefore=10,
            spaceAfter=15
        )

    def _create_header(self, story: List, title: str, subtitle: str = "Filtered Therapy Podcast"):
        """Create a branded header for the document"""
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Paragraph(subtitle, self.styles['BrandSubtitle']))
        story.append(self._create_section_divider())

    def _create_info_table(self, data: List[List[str]], col_widths: List[float] = None) -> Table:
        """Create a styled info table"""
        if col_widths is None:
            col_widths = [2*inch, 4.5*inch]

        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.BRAND_LIGHT),
            ('TEXTCOLOR', (0, 0), (0, -1), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_DARK),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.BRAND_ACCENT),
            ('LINEBELOW', (0, -1), (-1, -1), 1, self.BRAND_PRIMARY),
        ]))
        return table

    def _create_data_table(self, data: List[List[str]], col_widths: List[float] = None) -> Table:
        """Create a styled data table with header row"""
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.BRAND_LIGHT]),
            ('LINEBELOW', (0, 0), (-1, 0), 2, self.BRAND_ACCENT),
            ('LINEBELOW', (0, 1), (-1, -2), 0.5, HexColor('#E0E0E0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table

    def generate_research_pdf(self, research_data: Dict[str, Any]) -> str:
        """Generate PDF report for topic research results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"filtered_therapy_research_{timestamp}.pdf"
        filepath = os.path.join(self.output_directory, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=40)

        story = []

        # Branded header
        self._create_header(story, "Research Report", "Filtered Therapy - Content Research")

        # Executive summary
        total_posts = (
            research_data.get('posts_analyzed', 0) or
            (research_data.get('tweets_analyzed', 0) +
            research_data.get('reddit_posts_analyzed', 0) +
            research_data.get('tiktok_posts_analyzed', 0) +
            research_data.get('threads_posts_analyzed', 0))
        )

        # Get active platforms
        active_platforms = [p for p in ['Twitter', 'Reddit', 'TikTok', 'Threads']
                          if research_data.get(f'{p.lower()}_posts_analyzed', 0) > 0 or
                          research_data.get(f'{p.lower()}_data', {})]

        # Truncate keywords for display
        keywords = research_data.get('search_keywords', [])
        keywords_display = ', '.join(keywords[:5])
        if len(keywords) > 5:
            keywords_display += f' (+{len(keywords) - 5} more)'

        summary_data = [
            ['Keywords', keywords_display],
            ['Niche', research_data.get('podcast_niche', 'Gen Z Culture')],
            ['Posts Analyzed', str(total_posts)],
            ['Platforms', ', '.join(active_platforms) or 'Multi-platform'],
            ['Topics Found', str(len(research_data.get('trending_topics', [])))],
            ['Generated', research_data.get('timestamp', datetime.now().isoformat())[:16].replace('T', ' ')]
        ]

        story.append(Paragraph("Overview", self.styles['SectionHeader']))
        story.append(self._create_info_table(summary_data))
        story.append(Spacer(1, 25))

        # AI Topic Suggestions
        if research_data.get('ai_topic_suggestions', {}).get('topics'):
            story.append(Paragraph("AI-Generated Episode Ideas", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            for i, topic in enumerate(research_data['ai_topic_suggestions']['topics'][:6], 1):
                title = topic.get('title', 'Untitled Topic')
                story.append(Paragraph(f"{i}. {title}", self.styles['TopicTitle']))

                desc = topic.get('description', '')
                if desc:
                    story.append(Paragraph(desc, self.styles['BodyText']))

                relevance = topic.get('relevance_score', 'N/A')
                story.append(Paragraph(f"<b>Relevance:</b> {relevance}/10", self.styles['BodyText']))

                if topic.get('key_points'):
                    for point in topic['key_points'][:3]:
                        story.append(Paragraph(f"  {point}", self.styles['KeyPoint']))

                story.append(Spacer(1, 12))

        # Trending Topics
        if research_data.get('trending_topics'):
            story.append(PageBreak())
            story.append(Paragraph("Trending Topics", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            trending_data = [['Topic', 'Posts', 'Engagement', 'Avg']]
            for topic in research_data['trending_topics'][:10]:
                topic_name = topic.get('topic', 'Unknown')
                if len(topic_name) > 25:
                    topic_name = topic_name[:22] + '...'
                trending_data.append([
                    topic_name,
                    str(topic.get('post_count', topic.get('tweet_count', 0))),
                    str(topic.get('total_engagement', 0)),
                    str(round(topic.get('avg_engagement', 0), 1))
                ])

            story.append(self._create_data_table(trending_data,
                         col_widths=[2.5*inch, 1*inch, 1.2*inch, 1*inch]))
            story.append(Spacer(1, 25))

        # Content Calendar Suggestions
        if research_data.get('content_calendar'):
            story.append(Paragraph("Content Calendar", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            for suggestion in research_data['content_calendar'][:6]:
                week = suggestion.get('week', '?')
                topic = suggestion.get('topic', 'No topic')
                story.append(Paragraph(f"Week {week}: {topic}", self.styles['TopicTitle']))

                priority = suggestion.get('priority', 'Medium')
                format_type = suggestion.get('suggested_format', 'Standard Episode')
                story.append(Paragraph(f"<b>Priority:</b> {priority.title()}  |  <b>Format:</b> {format_type}",
                                     self.styles['BodyText']))

                reason = suggestion.get('reason', '')
                if reason:
                    story.append(Paragraph(reason, self.styles['KeyPoint']))
                story.append(Spacer(1, 10))

        # Sentiment Analysis
        if research_data.get('sentiment_analysis'):
            story.append(PageBreak())
            story.append(Paragraph("Audience Sentiment", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            sentiment = research_data['sentiment_analysis']
            sentiment_data = [
                ['Posts Analyzed', str(sentiment.get('total_analyzed', 0))],
                ['Positive', f"{sentiment.get('positive_percentage', 0):.1f}%"],
                ['Negative', f"{sentiment.get('negative_percentage', 0):.1f}%"],
                ['Neutral', f"{sentiment.get('neutral_percentage', 0):.1f}%"],
                ['Overall', sentiment.get('overall_sentiment', 'Mixed').title()]
            ]

            story.append(self._create_info_table(sentiment_data))

        # Footer
        story.append(Spacer(1, 30))
        story.append(self._create_section_divider())
        story.append(Paragraph("Generated by ESOSA - Podcast Research Assistant",
                             self.styles['Footer']))

        # Build PDF
        doc.build(story)
        self.logger.info(f"Research PDF generated: {filepath}")
        return filepath

    def generate_episode_pdf(self, episode_data: Dict[str, Any]) -> str:
        """Generate PDF for episode content"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic = episode_data.get('topic', 'Episode')
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_'))[:30]
        filename = f"filtered_therapy_episode_{safe_topic}_{timestamp}.pdf"
        filepath = os.path.join(self.output_directory, filename)

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=40)

        story = []

        # Branded header with episode topic
        self._create_header(story, episode_data.get('topic', 'Episode Plan'),
                          "Filtered Therapy - Episode Blueprint")

        # Episode details
        details_data = [
            ['Topic', episode_data.get('topic', 'N/A')],
            ['Duration', f"{episode_data.get('duration_minutes', 30)} minutes"],
            ['Style', episode_data.get('host_style', 'Conversational').title()],
            ['Audience', episode_data.get('target_audience', 'Gen Z')],
            ['Created', episode_data.get('timestamp', datetime.now().isoformat())[:16].replace('T', ' ')]
        ]

        story.append(Paragraph("Episode Details", self.styles['SectionHeader']))
        story.append(self._create_info_table(details_data))
        story.append(Spacer(1, 25))

        # Episode outline
        if episode_data.get('outline', {}).get('segments'):
            story.append(Paragraph("Episode Structure", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            for i, segment in enumerate(episode_data['outline']['segments'], 1):
                name = segment.get('name', 'Unnamed Segment')
                duration = segment.get('duration_minutes', '?')
                story.append(Paragraph(f"{i}. {name} ({duration} min)", self.styles['TopicTitle']))

                if segment.get('talking_points'):
                    for point in segment['talking_points']:
                        story.append(Paragraph(f"  {point}", self.styles['KeyPoint']))

                story.append(Spacer(1, 10))

        # Talking points
        if episode_data.get('talking_points'):
            story.append(PageBreak())
            story.append(Paragraph("Key Talking Points", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            for i, point in enumerate(episode_data['talking_points'], 1):
                story.append(Paragraph(f"{i}. {point}", self.styles['BodyText']))
                story.append(Spacer(1, 6))

        # Show notes
        if episode_data.get('show_notes', {}).get('show_notes'):
            story.append(PageBreak())
            story.append(Paragraph("Show Notes", self.styles['SectionHeader']))
            story.append(self._create_section_divider())

            show_notes_text = episode_data['show_notes']['show_notes']
            paragraphs = show_notes_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Handle markdown-style headers
                    clean_para = para.strip()
                    if clean_para.startswith('##'):
                        clean_para = clean_para.lstrip('#').strip()
                        story.append(Paragraph(clean_para, self.styles['Subtitle']))
                    elif clean_para.startswith('#'):
                        clean_para = clean_para.lstrip('#').strip()
                        story.append(Paragraph(clean_para, self.styles['TopicTitle']))
                    elif clean_para.startswith('-') or clean_para.startswith('*'):
                        story.append(Paragraph(f"  {clean_para[1:].strip()}", self.styles['KeyPoint']))
                    else:
                        story.append(Paragraph(clean_para, self.styles['BodyText']))
                    story.append(Spacer(1, 6))

        # Footer
        story.append(Spacer(1, 30))
        story.append(self._create_section_divider())
        story.append(Paragraph("Generated by ESOSA - Podcast Research Assistant",
                             self.styles['Footer']))

        # Build PDF
        doc.build(story)
        self.logger.info(f"Episode PDF generated: {filepath}")
        return filepath

    def generate_interview_pdf(self, interview_data: Dict[str, Any]) -> str:
        """Generate PDF for interview preparation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        guest_name = interview_data.get('guest_info', {}).get('name', 'Guest').replace(' ', '_')
        filename = f"interview_prep_{guest_name}_{timestamp}.pdf"
        filepath = os.path.join(self.output_directory, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        guest_name_display = interview_data.get('guest_info', {}).get('name', 'Unknown Guest')
        story.append(Paragraph(f"Interview Preparation: {guest_name_display}", 
                             self.styles['CustomTitle']))
        story.append(Spacer(1, 30))
        
        # Interview details
        guest_info = interview_data.get('guest_info', {})
        details_data = [
            ['Guest Name', guest_info.get('name', 'N/A')],
            ['Expertise', guest_info.get('expertise', 'N/A')],
            ['Background', guest_info.get('background', 'N/A')],
            ['Interview Topic', interview_data.get('interview_topic', 'N/A')],
            ['Duration', f"{interview_data.get('interview_length', 'N/A')} minutes"]
        ]
        
        details_table = Table(details_data, colWidths=[2*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#E6E6FA')),
            ('TEXTCOLOR', (0, 0), (-1, -1), black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(Paragraph("Interview Details", self.styles['Heading1']))
        story.append(Spacer(1, 12))
        story.append(details_table)
        story.append(Spacer(1, 20))
        
        # Questions by category
        if interview_data.get('questions'):
            story.append(Paragraph("❓ Interview Questions", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            # Group questions by category
            categories = {}
            for q in interview_data['questions']:
                if 'error' not in q:
                    cat = q.get('category', 'General')
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(q.get('question', 'No question'))
            
            for category, questions in categories.items():
                story.append(Paragraph(f"📋 {category}", self.styles['Subtitle']))
                story.append(Spacer(1, 8))
                
                for i, question in enumerate(questions, 1):
                    story.append(Paragraph(f"{i}. {question}", self.styles['Normal']))
                    story.append(Spacer(1, 6))
                
                story.append(Spacer(1, 15))
        
        # Preparation notes
        if interview_data.get('preparation_notes'):
            story.append(PageBreak())
            story.append(Paragraph("📋 Preparation Notes", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            for i, note in enumerate(interview_data['preparation_notes'], 1):
                story.append(Paragraph(f"{i}. {note}", self.styles['KeyPoint']))
                story.append(Spacer(1, 8))
        
        # Build PDF
        doc.build(story)
        self.logger.info(f"Interview PDF generated: {filepath}")
        return filepath

    def generate_social_media_analysis_pdf(self, analysis_data: Dict[str, Any]) -> str:
        """Generate PDF for comprehensive social media analysis across platforms"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"social_media_analysis_{timestamp}.pdf"
        filepath = os.path.join(self.output_directory, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title page
        story.append(Paragraph("Social Media Analysis Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Platform breakdown
        platforms = ['twitter', 'reddit', 'tiktok', 'threads']
        platform_data = [['Platform', 'Posts Analyzed', 'Engagement Rate', 'Top Keywords']]
        
        for platform in platforms:
            platform_info = analysis_data.get(f'{platform}_data', {})
            posts_count = platform_info.get('posts_analyzed', 0)
            if posts_count > 0:
                engagement = platform_info.get('avg_engagement', 0)
                keywords = ', '.join(platform_info.get('top_keywords', [])[:3])
                platform_data.append([
                    platform.title(),
                    str(posts_count),
                    f"{engagement:.1f}%" if engagement else "N/A",
                    keywords or "N/A"
                ])
        
        if len(platform_data) > 1:  # Has data beyond header
            story.append(Paragraph("📊 Platform Analysis Overview", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            platform_table = Table(platform_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2.5*inch])
            platform_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4169E1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#F0F8FF'), HexColor('#FFFFFF')])
            ]))
            
            story.append(platform_table)
            story.append(Spacer(1, 20))
        
        # Cross-platform trending topics
        if analysis_data.get('cross_platform_topics'):
            story.append(Paragraph("🔥 Cross-Platform Trending Topics", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            for i, topic in enumerate(analysis_data['cross_platform_topics'][:8], 1):
                story.append(Paragraph(f"{i}. {topic.get('topic', 'Unknown Topic')}", 
                                     self.styles['TopicTitle']))
                
                platforms_mentioned = topic.get('platforms', [])
                if platforms_mentioned:
                    story.append(Paragraph(f"<b>Platforms:</b> {', '.join(platforms_mentioned)}", 
                                         self.styles['Normal']))
                
                total_mentions = topic.get('total_mentions', 0)
                if total_mentions:
                    story.append(Paragraph(f"<b>Total Mentions:</b> {total_mentions}", 
                                         self.styles['Normal']))
                
                story.append(Spacer(1, 12))
        
        # Platform-specific insights
        for platform in platforms:
            platform_insights = analysis_data.get(f'{platform}_insights', {})
            if platform_insights:
                story.append(PageBreak())
                story.append(Paragraph(f"📱 {platform.title()} Insights", self.styles['Heading1']))
                story.append(Spacer(1, 12))
                
                # Top posts
                if platform_insights.get('top_posts'):
                    story.append(Paragraph("🔝 Top Performing Posts", self.styles['Subtitle']))
                    story.append(Spacer(1, 8))
                    
                    for i, post in enumerate(platform_insights['top_posts'][:5], 1):
                        story.append(Paragraph(f"{i}. {post.get('text', 'No content')[:200]}...", 
                                             self.styles['Normal']))
                        story.append(Paragraph(f"<b>Engagement:</b> {post.get('engagement', 'N/A')}", 
                                             self.styles['Normal']))
                        story.append(Spacer(1, 8))
                
                # Trending hashtags/keywords
                if platform_insights.get('trending_hashtags'):
                    story.append(Spacer(1, 15))
                    story.append(Paragraph("📈 Trending Hashtags/Keywords", self.styles['Subtitle']))
                    story.append(Spacer(1, 8))
                    
                    hashtags_text = ', '.join(platform_insights['trending_hashtags'][:10])
                    story.append(Paragraph(hashtags_text, self.styles['Normal']))
                    story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        self.logger.info(f"Social media analysis PDF generated: {filepath}")
        return filepath