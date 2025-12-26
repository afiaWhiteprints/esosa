from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import logging

from .twitter_client import TwitterClient
from .gemini_client import GeminiClient, GeminiError
from .openrouter_client import OpenRouterClient, OpenRouterError
from .topic_analyzer import TopicAnalyzer
from .script_generator import ScriptGenerator
from .pdf_generator import PDFGenerator
from .tiktok_client import TikTokClient
from .threads_client import ThreadsClient
from .reddit_client import RedditClient
from .data_manager import DataManager
from .export_manager import ExportManager
from .prompt_manager import PromptManager


class PodcastAssistant:
    def __init__(self):
        """Initialize the Podcast Assistant with all necessary clients"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Initialize managers
        self.prompt_manager = PromptManager()
        self.export_manager = ExportManager()
        self.data_manager = DataManager()

        self.twitter_client = TwitterClient()

        # Initialize both AI clients for runtime fallback
        self.openrouter_client = None
        self.gemini_client = None
        self.ai_client = None

        # Try Gemini first (primary)
        try:
            self.gemini_client = GeminiClient(prompt_manager=self.prompt_manager)
            self.ai_client = self.gemini_client
            self.logger.info("Primary AI client: Gemini")
        except ValueError as e:
            self.logger.warning(f"Gemini not available: {str(e)}")

        # Initialize OpenRouter as fallback (or primary if Gemini unavailable)
        try:
            self.openrouter_client = OpenRouterClient(prompt_manager=self.prompt_manager)
            if self.ai_client is None:
                self.ai_client = self.openrouter_client
                self.logger.info("Primary AI client: OpenRouter (Gemini unavailable)")
            else:
                self.logger.info("Fallback AI client: OpenRouter ready")
        except ValueError as e:
            self.logger.warning(f"OpenRouter not available: {str(e)}")

        if self.ai_client is None:
            raise ValueError("No AI client available. Please configure OpenRouter or Gemini API keys.")

        self.topic_analyzer = TopicAnalyzer()
        self.script_generator = ScriptGenerator(self.ai_client)
        self.pdf_generator = PDFGenerator()

        # Initialize TikTok client (optional - only if RapidAPI key is available)
        try:
            self.tiktok_client = TikTokClient()
            self.tiktok_enabled = True
        except ValueError as e:
            self.logger.warning(f"TikTok integration disabled: {str(e)}")
            self.tiktok_client = None
            self.tiktok_enabled = False

        # Initialize Threads client (optional - only if RapidAPI key is available)
        try:
            self.threads_client = ThreadsClient()
            self.threads_enabled = True
        except ValueError as e:
            self.logger.warning(f"Threads integration disabled: {str(e)}")
            self.threads_client = None
            self.threads_enabled = False

        # Initialize Reddit client (optional - only if Reddit credentials are available)
        try:
            self.reddit_client = RedditClient()
            self.reddit_enabled = True
        except ValueError as e:
            self.logger.warning(f"Reddit integration disabled: {str(e)}")
            self.reddit_client = None
            self.reddit_enabled = False

        # Configuration
        self.config = {
            'default_tweet_count': 10,
            'default_episode_duration': 30,
            'output_directory': 'output'
        }

        # Ensure output directory exists
        os.makedirs(self.config['output_directory'], exist_ok=True)

    def _switch_to_fallback_client(self):
        """Switch to OpenRouter if Gemini fails"""
        if self.openrouter_client and self.ai_client != self.openrouter_client:
            self.logger.warning("🔄 Switching to OpenRouter as fallback AI client")
            self.ai_client = self.openrouter_client
            self.script_generator = ScriptGenerator(self.ai_client)
            return True
        return False

    def _call_ai_method(self, method_name: str, *args, **kwargs):
        """Call an AI client method with automatic fallback to OpenRouter on failure"""
        try:
            method = getattr(self.ai_client, method_name)
            return method(*args, **kwargs)
        except GeminiError as e:
            self.logger.warning(f"Gemini failed: {str(e)[:100]}")
            if self._switch_to_fallback_client():
                self.logger.info("Retrying with OpenRouter...")
                method = getattr(self.ai_client, method_name)
                return method(*args, **kwargs)
            else:
                raise

    def research_topics(self,
                       keywords: List[str],
                       podcast_niche: str = "",
                       podcast_description: str = "",
                       max_tweets: int = None,
                       days_back: int = 7,
                       generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Complete topic research workflow

        Args:
            keywords: List of keywords to search for
            podcast_niche: The podcast's niche/domain
            podcast_description: Detailed description of the podcast
            days_back: Number of days to look back for content
            max_tweets: Maximum number of tweets to analyze
            
        Returns:
            Dictionary with complete research results
        """
        max_tweets = max_tweets or self.config['default_tweet_count']

        self.logger.info(f"Starting topic research for keywords: {keywords}")

        # Step 1: Gather tweets
        tweets = self.twitter_client.search_tweets(keywords, max_tweets, days_back)
        if not tweets:
            return {"error": "No tweets found for the given keywords"}
        
        # Step 2: Analyze engagement
        engagement_analysis = self.twitter_client.analyze_engagement(tweets)
        
        # Step 3: Extract trending topics and keywords
        trending_topics = self.topic_analyzer.identify_trending_topics(tweets)
        extracted_keywords = self.topic_analyzer.extract_keywords_from_tweets(tweets)
        
        # Step 4: Analyze sentiment
        sentiment_analysis = self.topic_analyzer.analyze_sentiment_patterns(tweets)
        
        # Step 5: Find content gaps
        gap_analysis = self.topic_analyzer.find_content_gaps(tweets, keywords)
        
        # Step 6: Generate AI-powered topic suggestions (with fallback)
        try:
            ai_topics = self.ai_client.analyze_tweets_for_topics(
                tweets=tweets,
                reddit_posts=[],
                tiktok_posts=[],
                threads_posts=[],
                podcast_niche=podcast_niche,
                podcast_description=podcast_description,
                target_keywords=keywords
            )
        except GeminiError:
            if self._switch_to_fallback_client():
                ai_topics = self.ai_client.analyze_tweets_for_topics(
                    tweets=tweets,
                    reddit_posts=[],
                    tiktok_posts=[],
                    threads_posts=[],
                    podcast_niche=podcast_niche,
                    podcast_description=podcast_description,
                    target_keywords=keywords
                )
            else:
                ai_topics = {"topics": [], "error": "AI analysis failed"}
        
        # Step 7: Create content calendar suggestions
        calendar_suggestions = self.topic_analyzer.generate_content_calendar_suggestions(
            trending_topics, extracted_keywords
        )
        
        research_results = {
            'search_keywords': keywords,
            'podcast_niche': podcast_niche,
            'tweets_analyzed': len(tweets),
            'engagement_analysis': engagement_analysis,
            'trending_topics': trending_topics,
            'extracted_keywords': extracted_keywords[:20],  # Top 20
            'sentiment_analysis': sentiment_analysis,
            'content_gaps': gap_analysis,
            'ai_topic_suggestions': ai_topics,
            'content_calendar': calendar_suggestions,
            'sample_posts': [{'text': t.get('text', '')[:150], 'url': t.get('tweet_url', ''), 'author': t.get('author', '')} for t in tweets[:5]],
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        json_file = self._save_results(research_results, 'topic_research')
        
        # Generate PDF if requested
        pdf_file = None
        if generate_pdf:
            try:
                pdf_file = self.pdf_generator.generate_research_pdf(research_results)
                research_results['pdf_report'] = pdf_file
            except Exception as e:
                self.logger.error(f"Failed to generate PDF: {str(e)}")
                research_results['pdf_error'] = str(e)
        
        research_results['json_report'] = json_file
        self.logger.info("Topic research completed successfully")
        return research_results

    def research_topics_multi_platform(self,
                                     keywords: List[str],
                                     podcast_niche: str = "",
                                     podcast_description: str = "",
                                     max_tweets: int = None,
                                     max_tiktoks: int = 20,
                                     max_threads: int = 20,
                                     max_reddit_posts: int = 20,
                                     days_back: int = 7,
                                     tiktok_days_back: int = 7,
                                     threads_days_back: int = 7,
                                     reddit_days_back: int = 7,
                                     include_tiktok: bool = True,
                                     include_threads: bool = True,
                                     include_reddit: bool = True,
                                     tiktok_regions: List[str] = ["us", "ng"],
                                     use_random_tiktok_keywords: bool = False,
                                     random_tiktok_keyword_count: int = 10,
                                     use_random_threads_keywords: bool = False,
                                     random_threads_keyword_count: int = 10,
                                     use_random_reddit_keywords: bool = False,
                                     random_reddit_keyword_count: int = 10,
                                     generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Research topics across multiple platforms (Twitter + TikTok + Threads + Reddit)
        
        Args:
            keywords: List of keywords to search for
            podcast_niche: The podcast's niche/domain
            podcast_description: Detailed description of the podcast
            max_tweets: Maximum number of tweets to analyze
            max_tiktoks: Maximum number of TikTok videos to analyze
            max_threads: Maximum number of Threads posts to analyze
            max_reddit_posts: Maximum number of Reddit posts to analyze
            include_tiktok: Whether to include TikTok data
            include_threads: Whether to include Threads data
            include_reddit: Whether to include Reddit data
            tiktok_regions: List of regions to search in TikTok (e.g., ["us", "ng"])
            use_random_tiktok_keywords: Whether to randomly select keywords for TikTok
            random_tiktok_keyword_count: Number of random keywords to select for TikTok
            use_random_threads_keywords: Whether to randomly select keywords for Threads
            random_threads_keyword_count: Number of random keywords to select for Threads
            use_random_reddit_keywords: Whether to randomly select keywords for Reddit
            random_reddit_keyword_count: Number of random keywords to select for Reddit
            generate_pdf: Whether to generate PDF report
            
        Returns:
            Dictionary with multi-platform research results
        """
        self.logger.info(f"Starting multi-platform research for keywords: {keywords}")
        
        # Track which platforms succeeded/failed
        platforms_attempted = ['twitter']
        platforms_succeeded = []
        platform_errors = {}
        
        # Step 1: Twitter research (with error handling)
        twitter_results = {}
        try:
            self.logger.info("🐦 Starting Twitter research...")
            twitter_results = self.research_topics(
                keywords=keywords,
                podcast_niche=podcast_niche,
                podcast_description=podcast_description,
                max_tweets=max_tweets,
                days_back=days_back,
                generate_pdf=False  # We'll generate PDF later with combined data
            )
            
            if 'error' in twitter_results:
                self.logger.warning(f"Twitter research failed: {twitter_results['error']}")
                platform_errors['twitter'] = twitter_results['error']
                twitter_results = {'error': twitter_results['error']}
            else:
                platforms_succeeded.append('twitter')
                self.logger.info("✅ Twitter research completed successfully")
                
        except Exception as e:
            error_msg = f"Twitter research encountered an exception: {str(e)}"
            self.logger.error(error_msg)
            platform_errors['twitter'] = error_msg
            twitter_results = {'error': error_msg}
        
        # Step 2: TikTok research (if enabled and requested)
        tiktok_results = {}
        if include_tiktok and self.tiktok_enabled:
            platforms_attempted.append('tiktok')
            try:
                self.logger.info("🎵 Starting TikTok research...")
                # Reset session counter for new research session
                self.tiktok_client.reset_session_counter()
                self.logger.info(f"Gathering TikTok data for {len(keywords)} keywords...")
                
                # Get TikTok videos matching keywords
                tiktok_videos = self.tiktok_client.search_videos_by_keywords(
                    keywords=keywords, 
                    count=max_tiktoks,
                    regions=tiktok_regions,
                    use_random_keywords=use_random_tiktok_keywords,
                    random_keyword_count=random_tiktok_keyword_count
                )
                
                # Filter videos by keyword relevance
                filtered_videos = self.tiktok_client.filter_by_keywords(tiktok_videos, keywords)
                
                # Analyze TikTok engagement
                tiktok_engagement = self.tiktok_client.analyze_engagement(filtered_videos)
                
                # Get trending hashtags
                trending_hashtags = self.tiktok_client.get_hashtag_trends(keywords)
                
                # Convert TikTok data to similar format as Twitter for AI analysis
                tiktok_text_data = self._convert_tiktok_to_text_format(filtered_videos)
                
                # Analyze TikTok content with AI (with fallback)
                if tiktok_text_data:
                    try:
                        ai_tiktok_analysis = self.ai_client.analyze_tweets_for_topics(
                            tweets=[],
                            reddit_posts=[],
                            tiktok_posts=tiktok_text_data,
                            threads_posts=[],
                            podcast_niche=podcast_niche,
                            podcast_description=podcast_description,
                            target_keywords=keywords
                        )
                    except GeminiError:
                        if self._switch_to_fallback_client():
                            ai_tiktok_analysis = self.ai_client.analyze_tweets_for_topics(
                                tweets=[],
                                reddit_posts=[],
                                tiktok_posts=tiktok_text_data,
                                threads_posts=[],
                                podcast_niche=podcast_niche,
                                podcast_description=podcast_description,
                                target_keywords=keywords
                            )
                        else:
                            ai_tiktok_analysis = {"topics": [], "error": "AI analysis failed"}
                else:
                    ai_tiktok_analysis = {"topics": [], "analysis": "No TikTok content to analyze"}
                
                tiktok_results = {
                    'videos_analyzed': len(filtered_videos),
                    'total_videos_found': len(tiktok_videos),
                    'engagement_analysis': tiktok_engagement,
                    'trending_hashtags': trending_hashtags,
                    'ai_topic_suggestions': ai_tiktok_analysis,
                    'sample_captions': [v.get('caption', '')[:100] + '...' for v in filtered_videos[:5]],
                    'sample_posts': [{'text': v.get('caption', '')[:150], 'url': v.get('video_url', ''), 'author': v.get('author', '')} for v in filtered_videos[:5]],
                    'top_hashtags': [ht['hashtag'] for ht in trending_hashtags[:10]]
                }
                
                platforms_succeeded.append('tiktok')
                self.logger.info(f"✅ TikTok research completed: {len(filtered_videos)} relevant videos found")
                
            except Exception as e:
                error_msg = f"TikTok research encountered an exception: {str(e)}"
                self.logger.error(error_msg)
                platform_errors['tiktok'] = error_msg
                tiktok_results = {'error': error_msg}
        elif include_tiktok and not self.tiktok_enabled:
            platforms_attempted.append('tiktok')
            error_msg = 'TikTok integration not available (missing RapidAPI key)'
            platform_errors['tiktok'] = error_msg
            tiktok_results = {'error': error_msg}
            self.logger.warning(error_msg)
        
        # Step 3: Threads research (if enabled and requested)
        threads_results = {}
        if include_threads and self.threads_enabled:
            platforms_attempted.append('threads')
            try:
                self.logger.info("🧵 Starting Threads research...")
                # Reset session counter for new research session
                self.threads_client.reset_session_counter()
                self.logger.info(f"Gathering Threads data for {len(keywords)} keywords...")
                
                # Get Threads posts matching keywords
                threads_posts = self.threads_client.search_threads_by_keywords(
                    keywords=keywords, 
                    count=max_threads,
                    use_random_keywords=use_random_threads_keywords,
                    random_keyword_count=random_threads_keyword_count
                )
                
                # Analyze Threads engagement
                threads_engagement = self.threads_client.analyze_engagement(threads_posts)
                
                # Convert Threads data to similar format as Twitter for AI analysis
                threads_text_data = self._convert_threads_to_text_format(threads_posts)
                
                # Analyze Threads content with AI (with fallback)
                if threads_text_data:
                    try:
                        ai_threads_analysis = self.ai_client.analyze_tweets_for_topics(
                            tweets=[],
                            reddit_posts=[],
                            tiktok_posts=[],
                            threads_posts=threads_text_data,
                            podcast_niche=podcast_niche,
                            podcast_description=podcast_description,
                            target_keywords=keywords
                        )
                    except GeminiError:
                        if self._switch_to_fallback_client():
                            ai_threads_analysis = self.ai_client.analyze_tweets_for_topics(
                                tweets=[],
                                reddit_posts=[],
                                tiktok_posts=[],
                                threads_posts=threads_text_data,
                                podcast_niche=podcast_niche,
                                podcast_description=podcast_description,
                                target_keywords=keywords
                            )
                        else:
                            ai_threads_analysis = {"topics": [], "error": "AI analysis failed"}
                else:
                    ai_threads_analysis = {"topics": [], "analysis": "No Threads content to analyze"}
                
                threads_results = {
                    'posts_analyzed': len(threads_posts),
                    'engagement_analysis': threads_engagement,
                    'ai_topic_suggestions': ai_threads_analysis,
                    'sample_posts': [{'text': p.get('text', '')[:150], 'url': p.get('thread_url', ''), 'author': p.get('author', '')} for p in threads_posts[:5]],
                    'top_hashtags': [tag for post in threads_posts for tag in post.get('hashtags', [])][:10]
                }
                
                platforms_succeeded.append('threads')
                self.logger.info(f"✅ Threads research completed: {len(threads_posts)} posts found")
                
            except Exception as e:
                error_msg = f"Threads research encountered an exception: {str(e)}"
                self.logger.error(error_msg)
                platform_errors['threads'] = error_msg
                threads_results = {'error': error_msg}
        elif include_threads and not self.threads_enabled:
            platforms_attempted.append('threads')
            error_msg = 'Threads integration not available (missing RapidAPI key)'
            platform_errors['threads'] = error_msg
            threads_results = {'error': error_msg}
            self.logger.warning(error_msg)
        
        # Step 4: Reddit research (if enabled and requested)
        reddit_results = {}
        if include_reddit and self.reddit_enabled:
            platforms_attempted.append('reddit')
            try:
                self.logger.info("🔴 Starting Reddit research...")
                # Reset session counter for new research session
                self.reddit_client.reset_session_counter()
                self.logger.info(f"Gathering Reddit data for {len(keywords)} keywords...")
                
                # Get Reddit posts matching keywords
                reddit_posts = self.reddit_client.search_reddit_by_keywords(
                    keywords=keywords, 
                    count=max_reddit_posts,
                    use_random_keywords=use_random_reddit_keywords,
                    random_keyword_count=random_reddit_keyword_count
                )
                
                # Analyze Reddit engagement
                reddit_engagement = self.reddit_client.analyze_engagement(reddit_posts)
                
                # Convert Reddit data to similar format as Twitter for AI analysis
                reddit_text_data = self._convert_reddit_to_text_format(reddit_posts)
                
                # Analyze Reddit content with AI (with fallback)
                if reddit_text_data:
                    try:
                        ai_reddit_analysis = self.ai_client.analyze_tweets_for_topics(
                            tweets=[],
                            reddit_posts=reddit_text_data,
                            tiktok_posts=[],
                            threads_posts=[],
                            podcast_niche=podcast_niche,
                            podcast_description=podcast_description,
                            target_keywords=keywords
                        )
                    except GeminiError:
                        if self._switch_to_fallback_client():
                            ai_reddit_analysis = self.ai_client.analyze_tweets_for_topics(
                                tweets=[],
                                reddit_posts=reddit_text_data,
                                tiktok_posts=[],
                                threads_posts=[],
                                podcast_niche=podcast_niche,
                                podcast_description=podcast_description,
                                target_keywords=keywords
                            )
                        else:
                            ai_reddit_analysis = {"topics": [], "error": "AI analysis failed"}
                else:
                    ai_reddit_analysis = {"topics": [], "analysis": "No Reddit content to analyze"}
                
                # Get trending subreddits
                trending_posts = self.reddit_client.get_trending_posts(count=20)
                
                reddit_results = {
                    'posts_analyzed': len(reddit_posts),
                    'total_trending_posts': len(trending_posts),
                    'engagement_analysis': reddit_engagement,
                    'ai_topic_suggestions': ai_reddit_analysis,
                    'sample_titles': [p.get('title', '')[:100] + '...' for p in reddit_posts[:5]],
                    'sample_posts': [{'text': p.get('title', '')[:150], 'url': f"https://reddit.com{p.get('permalink', '')}" if p.get('permalink') else '', 'author': p.get('author', ''), 'subreddit': p.get('subreddit', '')} for p in reddit_posts[:5]],
                    'top_subreddits': list(set([p.get('subreddit', '') for p in reddit_posts]))[:10]
                }
                
                platforms_succeeded.append('reddit')
                self.logger.info(f"✅ Reddit research completed: {len(reddit_posts)} posts found")
                
            except Exception as e:
                error_msg = f"Reddit research encountered an exception: {str(e)}"
                self.logger.error(error_msg)
                platform_errors['reddit'] = error_msg
                reddit_results = {'error': error_msg}
        elif include_reddit and not self.reddit_enabled:
            platforms_attempted.append('reddit')
            error_msg = 'Reddit integration not available (missing Reddit API credentials)'
            platform_errors['reddit'] = error_msg
            reddit_results = {'error': error_msg}
            self.logger.warning(error_msg)
        
        # Check if we have any successful results
        if not platforms_succeeded:
            error_msg = f"All platforms failed: {platform_errors}"
            self.logger.error(error_msg)
            return {
                'error': error_msg,
                'platform_errors': platform_errors,
                'platforms_attempted': platforms_attempted,
                'platforms_succeeded': platforms_succeeded
            }
        
        # Step 5: Combine and synthesize cross-platform insights
        self.logger.info(f"🎯 Successfully gathered data from: {', '.join(platforms_succeeded)}")
        if platform_errors:
            self.logger.warning(f"⚠️  Platform failures: {', '.join(platform_errors.keys())}")
        
        # Rank topics across all platforms
        platform_data = {
            'twitter_results': twitter_results,
            'tiktok_results': tiktok_results,
            'threads_results': threads_results,
            'reddit_results': reddit_results
        }
        ranked_topics = self.data_manager.rank_topics(platform_data)

        combined_results = {
            'search_keywords': keywords,
            'podcast_niche': podcast_niche,
            'podcast_description': podcast_description,
            'platforms_attempted': platforms_attempted,
            'platforms_succeeded': platforms_succeeded,
            'platform_errors': platform_errors,
            'platforms_analyzed': platforms_succeeded,  # Only successful ones
            'twitter_results': twitter_results,
            'tiktok_results': tiktok_results,
            'threads_results': threads_results,
            'reddit_results': reddit_results,
            'cross_platform_insights': self._generate_cross_platform_insights(
                twitter_results, tiktok_results, threads_results, reddit_results
            ),
            'ranked_topics': ranked_topics,
            'timestamp': datetime.now().isoformat()
        }

        # Check for previously covered topics
        if ranked_topics:
            top_topic = ranked_topics[0]
            matches = self.data_manager.check_topic_covered(top_topic.get('title', ''))
            if matches:
                self.logger.warning(f"⚠️  Top topic '{top_topic['title']}' may have been covered before:")
                for match in matches[:3]:
                    self.logger.warning(f"   - {match['topic']} (similarity: {match['similarity']:.0%})")
                combined_results['topic_warnings'] = matches

        # Generate PDF with combined data
        if generate_pdf:
            try:
                pdf_file = self.pdf_generator.generate_research_pdf(combined_results)
                combined_results['pdf_report'] = pdf_file
            except Exception as e:
                self.logger.error(f"Failed to generate PDF: {str(e)}")
                combined_results['pdf_error'] = str(e)

        # Save combined results with data manager
        json_file = self.data_manager.save_session(combined_results, 'multi_platform_research')
        combined_results['json_report'] = json_file

        # Export in additional formats (Markdown, CSV)
        try:
            md_file = self.export_manager.export_research(combined_results, 'markdown')
            combined_results['markdown_report'] = md_file
        except Exception as e:
            self.logger.error(f"Failed to export Markdown: {str(e)}")

        try:
            csv_file = self.export_manager.export_research(combined_results, 'csv')
            combined_results['csv_report'] = csv_file
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {str(e)}")
        
        success_platforms = ', '.join(platforms_succeeded)
        total_platforms = len(platforms_attempted)
        success_count = len(platforms_succeeded)
        
        if platform_errors:
            self.logger.info(f"✅ Multi-platform research completed with partial success: {success_count}/{total_platforms} platforms succeeded ({success_platforms})")
        else:
            self.logger.info(f"✅ Multi-platform research completed successfully: {success_platforms}")
        return combined_results

    def chat(self, user_input: str) -> str:
        """
        Interactive chat with the podcast assistant for QA and clarification.
        
        Args:
            user_input: The user's message/question
            
        Returns:
            AI response string
        """
        # Format the prompt using the prompt manager
        prompt = self.prompt_manager.format_chat_assistant(user_input)
        
        # Call the AI client
        return self._call_ai_method('generate_content', prompt)

    def _convert_tiktok_to_text_format(self, tiktok_videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert TikTok video data to Twitter-like format for AI analysis"""
        converted_data = []
        
        for video in tiktok_videos:
            # Combine caption and hashtags as "text"
            caption = video.get('caption', '')
            hashtags = video.get('hashtags', [])
            combined_text = f"{caption} {' '.join(['#' + tag for tag in hashtags])}"
            
            converted_item = {
                'id': video.get('id', ''),
                'text': combined_text,
                'created_at': video.get('created_at', ''),
                'author_id': video.get('author', ''),
                'like_count': video.get('like_count', 0),
                'retweet_count': video.get('share_count', 0),  # Map shares to retweets
                'reply_count': video.get('comment_count', 0),
                'quote_count': 0,  # TikTok doesn't have quotes
                'platform': 'tiktok'
            }
            converted_data.append(converted_item)
        
        return converted_data

    def _convert_threads_to_text_format(self, threads_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Threads post data to Twitter-like format for AI analysis"""
        converted_data = []
        
        for post in threads_posts:
            # Use the text directly from Threads posts
            text = post.get('text', '')
            hashtags = post.get('hashtags', [])
            combined_text = f"{text} {' '.join(['#' + tag for tag in hashtags])}"
            
            converted_item = {
                'id': post.get('id', ''),
                'text': combined_text,
                'created_at': post.get('created_at', ''),
                'author_id': post.get('author', ''),
                'like_count': post.get('like_count', 0),
                'retweet_count': post.get('repost_count', 0),  # Map reposts to retweets
                'reply_count': post.get('reply_count', 0),
                'quote_count': 0,  # Threads doesn't have quotes
                'platform': 'threads'
            }
            converted_data.append(converted_item)
        
        return converted_data

    def _convert_reddit_to_text_format(self, reddit_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Reddit post data to Twitter-like format for AI analysis"""
        converted_data = []
        
        for post in reddit_posts:
            # Combine title and selftext as "text"
            title = post.get('title', '')
            selftext = post.get('selftext', '')
            combined_text = f"{title}. {selftext}" if selftext else title
            
            converted_item = {
                'id': post.get('id', ''),
                'text': combined_text,
                'created_at': post.get('created_at', ''),
                'author_id': post.get('author', ''),
                'like_count': post.get('upvote_count', 0),
                'retweet_count': 0,  # Reddit doesn't have retweets/shares
                'reply_count': post.get('comment_count', 0),
                'quote_count': 0,  # Reddit doesn't have quotes
                'platform': 'reddit'
            }
            converted_data.append(converted_item)
        
        return converted_data

    def _generate_cross_platform_insights(self, 
                                        twitter_results: Dict[str, Any], 
                                        tiktok_results: Dict[str, Any],
                                        threads_results: Dict[str, Any],
                                        reddit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights by comparing data across all platforms"""
        insights = {}
        
        # Collect all available platforms
        available_platforms = []
        platform_data = {}
        
        if 'error' not in twitter_results and twitter_results:
            available_platforms.append('twitter')
            platform_data['twitter'] = twitter_results
            
        if 'error' not in tiktok_results and tiktok_results:
            available_platforms.append('tiktok')
            platform_data['tiktok'] = tiktok_results
            
        if 'error' not in threads_results and threads_results:
            available_platforms.append('threads')
            platform_data['threads'] = threads_results
            
        if 'error' not in reddit_results and reddit_results:
            available_platforms.append('reddit')
            platform_data['reddit'] = reddit_results
        
        if len(available_platforms) >= 2:
            # Compare engagement patterns across platforms
            engagement_comparison = {}
            for platform in available_platforms:
                engagement = platform_data[platform].get('engagement_analysis', {})
                if platform == 'twitter':
                    avg_engagement = engagement.get('avg_likes', 0) + engagement.get('avg_retweets', 0)
                elif platform == 'tiktok':
                    avg_engagement = engagement.get('avg_likes', 0) + engagement.get('avg_shares', 0)
                elif platform == 'threads':
                    avg_engagement = engagement.get('avg_likes', 0) + engagement.get('avg_reposts', 0)
                elif platform == 'reddit':
                    avg_engagement = engagement.get('avg_upvotes', 0) + engagement.get('avg_comments', 0)
                else:
                    avg_engagement = 0
                
                engagement_comparison[platform] = avg_engagement
            
            # Find highest engagement platform
            highest_engagement_platform = max(engagement_comparison.keys(), 
                                            key=lambda x: engagement_comparison[x])
            
            insights['engagement_comparison'] = {
                'platform_engagement': engagement_comparison,
                'highest_engagement_platform': highest_engagement_platform,
                'available_platforms': available_platforms
            }
            
            # Compare topic themes across platforms
            all_topics = {}
            for platform in available_platforms:
                topics = platform_data[platform].get('ai_topic_suggestions', {}).get('topics', [])
                all_topics[platform] = [t.get('title', '') for t in topics[:3]]
            
            # Find common themes across platforms
            common_themes = self._find_cross_platform_themes(all_topics)
            
            insights['topic_analysis'] = {
                'platform_topics': all_topics,
                'common_themes': common_themes,
                'unique_perspectives': self._find_unique_platform_perspectives(all_topics)
            }
            
            # Hashtag/keyword trends comparison
            hashtag_data = {}
            if 'twitter' in available_platforms:
                hashtag_data['twitter'] = [topic.get('topic', '') for topic in twitter_results.get('trending_topics', [])][:5]
            if 'tiktok' in available_platforms:
                hashtag_data['tiktok'] = [ht.get('hashtag', '') for ht in tiktok_results.get('trending_hashtags', [])][:5]
            if 'threads' in available_platforms:
                hashtag_data['threads'] = threads_results.get('top_hashtags', [])[:5]
            if 'reddit' in available_platforms:
                hashtag_data['reddit'] = reddit_results.get('top_subreddits', [])[:5]
            
            insights['trending_analysis'] = hashtag_data
            
            # Platform-specific insights
            insights['platform_recommendations'] = self._generate_platform_recommendations(available_platforms, platform_data)
            
        else:
            insights['error'] = f'Insufficient data for cross-platform analysis. Available platforms: {available_platforms}'
        
        return insights

    def _find_cross_platform_themes(self, all_topics: Dict[str, List[str]]) -> List[str]:
        """Find common themes across all platforms"""
        if not all_topics or len(all_topics) < 2:
            return []
        
        # Extract keywords from all platform topics
        platform_keywords = {}
        for platform, topics in all_topics.items():
            keywords = set()
            for topic in topics:
                if topic:
                    keywords.update(topic.lower().split())
            platform_keywords[platform] = keywords
        
        # Find common keywords across at least 2 platforms
        common_themes = set()
        platforms = list(platform_keywords.keys())
        
        for i, platform1 in enumerate(platforms):
            for j, platform2 in enumerate(platforms[i+1:], i+1):
                overlap = platform_keywords[platform1] & platform_keywords[platform2]
                common_themes.update(overlap)
        
        return list(common_themes)[:8]  # Top 8 common themes

    def _find_unique_platform_perspectives(self, all_topics: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Find unique perspectives for each platform"""
        if not all_topics:
            return {}
        
        unique_perspectives = {}
        
        # Get all keywords from all platforms combined
        all_keywords = set()
        platform_keywords = {}
        
        for platform, topics in all_topics.items():
            keywords = set()
            for topic in topics:
                if topic:
                    keywords.update(topic.lower().split())
            platform_keywords[platform] = keywords
            all_keywords.update(keywords)
        
        # Find unique keywords for each platform
        for platform, keywords in platform_keywords.items():
            other_platform_keywords = set()
            for other_platform, other_keywords in platform_keywords.items():
                if other_platform != platform:
                    other_platform_keywords.update(other_keywords)
            
            unique_keywords = keywords - other_platform_keywords
            unique_perspectives[platform] = list(unique_keywords)[:5]  # Top 5 unique
        
        return unique_perspectives

    def _generate_platform_recommendations(self, available_platforms: List[str], platform_data: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Generate recommendations for each platform based on their strengths"""
        recommendations = {}
        
        if 'twitter' in available_platforms:
            twitter_engagement = platform_data['twitter'].get('engagement_analysis', {})
            recommendations['twitter'] = f"Focus on real-time conversations and trending topics. Average engagement: {twitter_engagement.get('avg_likes', 0):.0f} likes"
        
        if 'tiktok' in available_platforms:
            tiktok_engagement = platform_data['tiktok'].get('engagement_analysis', {})
            recommendations['tiktok'] = f"Create visual content around trending audio/hashtags. Average engagement: {tiktok_engagement.get('avg_likes', 0):.0f} likes"
        
        if 'threads' in available_platforms:
            threads_engagement = platform_data['threads'].get('engagement_analysis', {})
            recommendations['threads'] = f"Share authentic, personal takes on trending topics. Average engagement: {threads_engagement.get('avg_likes', 0):.0f} likes"
        
        if 'reddit' in available_platforms:
            reddit_engagement = platform_data['reddit'].get('engagement_analysis', {})
            recommendations['reddit'] = f"Engage in community discussions with detailed insights. Average engagement: {reddit_engagement.get('avg_upvotes', 0):.0f} upvotes"
        
        return recommendations

    def _find_topic_overlap(self, twitter_topics: List[Dict], tiktok_topics: List[Dict]) -> List[str]:
        """Find overlapping themes between Twitter and TikTok topics (legacy function)"""
        twitter_keywords = set()
        tiktok_keywords = set()
        
        for topic in twitter_topics:
            title = topic.get('title', '').lower()
            twitter_keywords.update(title.split())
        
        for topic in tiktok_topics:
            title = topic.get('title', '').lower()
            tiktok_keywords.update(title.split())
        
        overlap = twitter_keywords & tiktok_keywords
        return list(overlap)[:5]  # Top 5 overlapping terms

    def generate_episode_content(self, 
                                topic: str = None,
                                research_data: Dict[str, Any] = None,
                                talking_points: List[str] = None,
                                duration_minutes: int = None,
                                host_style: str = "conversational",
                                target_audience: str = "general",
                                generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Generate complete episode content including outline and script
        
        Args:
            topic: Main episode topic (optional - will be generated from research if not provided)
            research_data: Previous research results to base episode on
            talking_points: Specific points to cover
            duration_minutes: Target episode duration
            host_style: Hosting style
            target_audience: Target audience
            generate_pdf: Whether to generate PDF report
            
        Returns:
            Dictionary with complete episode content
        """
        duration_minutes = duration_minutes or self.config['default_episode_duration']
        
        # If no topic provided, generate one from research data
        if not topic and research_data:
            topic = self._select_top_topic_from_research(research_data)
            self.logger.info(f"Generated topic from research data: {topic}")
        elif not topic:
            topic = "Podcast Episode Topic"  # Fallback
        
        self.logger.info(f"Generating episode content for topic: {topic}")

        # Step 1: Generate detailed outline (with fallback)
        try:
            outline = self.ai_client.generate_episode_outline(
                topic, talking_points, duration_minutes
            )
        except GeminiError:
            if self._switch_to_fallback_client():
                outline = self.ai_client.generate_episode_outline(
                    topic, talking_points, duration_minutes
                )
            else:
                return {"error": "Failed to generate episode outline"}

        if 'error' in outline:
            return outline

        # Step 2: Generate additional talking points if needed (with fallback)
        if not talking_points:
            try:
                talking_points = self.ai_client.generate_talking_points(
                    topic, target_audience
                )
            except GeminiError:
                if self._switch_to_fallback_client():
                    talking_points = self.ai_client.generate_talking_points(
                        topic, target_audience
                    )
                else:
                    talking_points = []
        
        # Step 3: Generate full script
        script = self.script_generator.generate_full_script(
            topic, outline, host_style, target_audience
        )
        
        # Step 4: Generate intro/outro
        intro_outro = self.script_generator.generate_intro_outro(
            episode_title=topic,
            key_takeaways=talking_points[:3] if talking_points else []
        )
        
        # Step 5: Generate show notes
        show_notes = self.script_generator.generate_show_notes(
            script.get('script_sections', []),
            talking_points
        )
        
        # Step 6: Generate social media content
        social_content = self.script_generator.create_social_media_content({
            'title': topic,
            'key_points': talking_points[:3] if talking_points else []
        })
        
        episode_content = {
            'topic': topic,
            'duration_minutes': duration_minutes,
            'host_style': host_style,
            'target_audience': target_audience,
            'outline': outline,
            'talking_points': talking_points,
            'full_script': script,
            'intro_outro': intro_outro,
            'show_notes': show_notes,
            'social_media_content': social_content,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results with data manager
        json_file = self.data_manager.save_session(episode_content, 'episode_content')

        # Mark topic as covered in history
        self.data_manager.add_topic_to_history(topic)

        # Generate PDF if requested
        pdf_file = None
        if generate_pdf:
            try:
                pdf_file = self.pdf_generator.generate_episode_pdf(episode_content)
                episode_content['pdf_report'] = pdf_file
            except Exception as e:
                self.logger.error(f"Failed to generate PDF: {str(e)}")
                episode_content['pdf_error'] = str(e)

        # Export as Markdown
        try:
            md_file = self.export_manager.export_episode(episode_content, 'markdown')
            episode_content['markdown_report'] = md_file
        except Exception as e:
            self.logger.error(f"Failed to export Markdown: {str(e)}")

        episode_content['json_report'] = json_file
        self.logger.info("Episode content generation completed")
        return episode_content

    def create_interview_prep(self, 
                            guest_info: Dict[str, str],
                            interview_topic: str,
                            interview_length: int = 30,
                            generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Create interview preparation materials
        
        Args:
            guest_info: Dictionary with guest information
            interview_topic: Interview topic/theme
            interview_length: Interview duration in minutes
            
        Returns:
            Dictionary with interview preparation materials
        """
        self.logger.info(f"Creating interview prep for guest: {guest_info.get('name', 'Unknown')}")
        
        # Generate interview questions
        questions = self.script_generator.create_interview_questions(
            guest_info, interview_topic, interview_length
        )
        
        # Generate background research if Twitter handle provided
        background_research = {}
        if 'twitter_handle' in guest_info:
            tweets = self.twitter_client.search_tweets([guest_info['twitter_handle']], 50)
            if tweets:
                background_research = {
                    'recent_activity': tweets[:10],
                    'engagement_analysis': self.twitter_client.analyze_engagement(tweets)
                }
        
        # Generate intro/outro for interview
        intro_outro = self.script_generator.generate_intro_outro(
            episode_title=f"Interview with {guest_info.get('name', 'Guest')}",
            host_name="Your Name Here"
        )
        
        interview_prep = {
            'guest_info': guest_info,
            'interview_topic': interview_topic,
            'interview_length': interview_length,
            'questions': questions,
            'background_research': background_research,
            'intro_outro': intro_outro,
            'preparation_notes': self._generate_interview_prep_notes(guest_info, interview_topic),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        json_file = self._save_results(interview_prep, 'interview_prep')
        
        # Generate PDF if requested
        pdf_file = None
        if generate_pdf:
            try:
                pdf_file = self.pdf_generator.generate_interview_pdf(interview_prep)
                interview_prep['pdf_report'] = pdf_file
            except Exception as e:
                self.logger.error(f"Failed to generate PDF: {str(e)}")
                interview_prep['pdf_error'] = str(e)
        
        interview_prep['json_report'] = json_file
        self.logger.info("Interview preparation completed")
        return interview_prep

    def analyze_competition(self, competitor_keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze competitor content and find opportunities
        
        Args:
            competitor_keywords: Keywords related to competitors
            
        Returns:
            Dictionary with competitive analysis
        """
        self.logger.info(f"Analyzing competition for keywords: {competitor_keywords}")
        
        # Search for competitor-related content
        tweets = self.twitter_client.search_tweets(competitor_keywords, 200)
        
        if not tweets:
            return {"error": "No competitor content found"}
        
        # Analyze competitor content
        trending_topics = self.topic_analyzer.identify_trending_topics(tweets)
        keywords = self.topic_analyzer.extract_keywords_from_tweets(tweets)
        sentiment = self.topic_analyzer.analyze_sentiment_patterns(tweets)
        
        # Find content gaps and opportunities
        gaps = self.topic_analyzer.find_content_gaps(tweets, competitor_keywords)
        
        # Generate competitive insights using AI
        competitive_insights = self.ai_client.synthesize_content(
            tweets,
            """Analyze this competitor content and provide insights on:
            1. Content themes and topics they're covering
            2. Gaps in their content strategy
            3. Opportunities for differentiation
            4. Audience engagement patterns
            5. Content format preferences
            
            Provide actionable recommendations for competing effectively."""
        )
        
        analysis = {
            'competitor_keywords': competitor_keywords,
            'content_analyzed': len(tweets),
            'trending_topics': trending_topics,
            'popular_keywords': keywords[:15],
            'sentiment_analysis': sentiment,
            'content_gaps': gaps,
            'ai_insights': competitive_insights,
            'recommendations': self._generate_competitive_recommendations(trending_topics, gaps),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save results
        self._save_results(analysis, 'competitive_analysis')
        
        self.logger.info("Competitive analysis completed")
        return analysis

    def _save_results(self, results: Dict[str, Any], result_type: str) -> str:
        """
        Save results to JSON file
        
        Args:
            results: Results dictionary to save
            result_type: Type of results (for filename)
            
        Returns:
            Filename of saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result_type}_{timestamp}.json"
        filepath = os.path.join(self.config['output_directory'], filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str, ensure_ascii=False)
            
            self.logger.info(f"Results saved to: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            return ""

    def _generate_interview_prep_notes(self, guest_info: Dict[str, str], topic: str) -> List[str]:
        """Generate preparation notes for interview"""
        notes = []
        notes.append(f"Review guest's background in {guest_info.get('expertise', 'their field')}")
        notes.append(f"Research recent developments in {topic}")
        notes.append("Prepare follow-up questions based on guest responses")
        notes.append("Test audio equipment before interview")
        notes.append("Send questions to guest 24-48 hours in advance")
        return notes

    def _generate_competitive_recommendations(self, 
                                           trending_topics: List[Dict[str, Any]], 
                                           gaps: Dict[str, Any]) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []
        
        if trending_topics:
            recommendations.append(f"Consider covering trending topic: {trending_topics[0]['topic']}")
        
        if gaps.get('content_opportunities'):
            opportunities = gaps['content_opportunities'][:2]
            recommendations.append(f"Explore underserved topics: {', '.join(opportunities)}")
        
        recommendations.append("Develop unique perspective or format to differentiate")
        recommendations.append("Engage with trending conversations to increase visibility")
        recommendations.append("Monitor competitor posting schedules for optimal timing")
        
        return recommendations

    def _select_top_topic_from_research(self, research_data: Dict[str, Any]) -> str:
        """Select the best topic from research data"""
        # Try to get the highest scoring AI topic suggestion
        ai_topics = research_data.get('ai_topic_suggestions', {}).get('topics', [])
        if ai_topics:
            # Sort by relevance score and return the top one
            sorted_topics = sorted(ai_topics, key=lambda x: x.get('relevance_score', 0), reverse=True)
            if sorted_topics:
                return sorted_topics[0].get('title', 'Generated Topic')
        
        # Fallback to trending topics
        trending = research_data.get('trending_topics', [])
        if trending:
            return f"The Truth About {trending[0]['topic']}"
        
        # Final fallback
        return "Real Talk: What Gen Z Really Thinks"

    def create_research_to_episode_workflow(self,
                                          keywords: List[str],
                                          podcast_niche: str = "",
                                          podcast_description: str = "",
                                          max_tweets: int = None,
                                          duration_minutes: int = None,
                                          host_style: str = "conversational",
                                          target_audience: str = "general",
                                          days_back: int = 7,
                                          tiktok_days_back: int = 7,
                                          threads_days_back: int = 7,
                                          reddit_days_back: int = 7,
                                          include_tiktok: bool = True,
                                          include_threads: bool = True,
                                          include_reddit: bool = True,
                                          tiktok_max_videos: int = 50,
                                          threads_max_posts: int = 30,
                                          reddit_max_posts: int = 30,
                                          tiktok_regions: List[str] = ["us", "ng"],
                                          use_random_tiktok_keywords: bool = False,
                                          random_tiktok_keyword_count: int = 10,
                                          use_random_threads_keywords: bool = False,
                                          random_threads_keyword_count: int = 10,
                                          use_random_reddit_keywords: bool = False,
                                          random_reddit_keyword_count: int = 10,
                                          generate_pdf: bool = True) -> Dict[str, Any]:
        """
        Complete workflow: Research topics -> Generate episode content
        
        Args:
            keywords: Keywords to research
            podcast_niche: Podcast niche
            podcast_description: Podcast description
            max_tweets: Maximum tweets to analyze
            duration_minutes: Episode duration
            host_style: Hosting style
            target_audience: Target audience
            include_tiktok: Whether to include TikTok data
            include_threads: Whether to include Threads data
            include_reddit: Whether to include Reddit data
            tiktok_max_videos: Maximum number of TikTok videos to analyze
            threads_max_posts: Maximum number of Threads posts to analyze
            reddit_max_posts: Maximum number of Reddit posts to analyze
            tiktok_regions: List of regions to search in TikTok
            use_random_tiktok_keywords: Whether to randomly select keywords for TikTok
            random_tiktok_keyword_count: Number of random keywords for TikTok
            use_random_threads_keywords: Whether to randomly select keywords for Threads
            random_threads_keyword_count: Number of random keywords for Threads
            use_random_reddit_keywords: Whether to randomly select keywords for Reddit
            random_reddit_keyword_count: Number of random keywords for Reddit
            generate_pdf: Generate PDF reports
            
        Returns:
            Dictionary with both research and episode content
        """
        self.logger.info("Starting research-to-episode workflow")
        
        # Step 1: Research topics (multi-platform)
        research_results = self.research_topics_multi_platform(
            keywords=keywords,
            podcast_niche=podcast_niche,
            podcast_description=podcast_description,
            max_tweets=max_tweets,
            max_tiktoks=tiktok_max_videos,
            max_threads=threads_max_posts,
            max_reddit_posts=reddit_max_posts,
            days_back=days_back,
            tiktok_days_back=tiktok_days_back,
            threads_days_back=threads_days_back,
            reddit_days_back=reddit_days_back,
            include_tiktok=include_tiktok,
            include_threads=include_threads,
            include_reddit=include_reddit,
            tiktok_regions=tiktok_regions,
            use_random_tiktok_keywords=use_random_tiktok_keywords,
            random_tiktok_keyword_count=random_tiktok_keyword_count,
            use_random_threads_keywords=use_random_threads_keywords,
            random_threads_keyword_count=random_threads_keyword_count,
            use_random_reddit_keywords=use_random_reddit_keywords,
            random_reddit_keyword_count=random_reddit_keyword_count,
            generate_pdf=generate_pdf
        )
        
        # Check if research failed completely (no platforms succeeded)
        if 'error' in research_results and not research_results.get('platforms_succeeded'):
            self.logger.error("Research-to-episode workflow failed: All platforms failed during research phase")
            return research_results
        
        # Log partial success if some platforms failed
        if research_results.get('platform_errors'):
            failed_platforms = ', '.join(research_results['platform_errors'].keys())
            successful_platforms = ', '.join(research_results.get('platforms_succeeded', []))
            self.logger.warning(f"⚠️  Research had partial failures: {failed_platforms} failed, but continuing with data from {successful_platforms}")
        
        # Step 2: Generate episode content based on research
        episode_results = self.generate_episode_content(
            topic=None,  # Let AI select topic from research
            research_data=research_results,
            duration_minutes=duration_minutes,
            host_style=host_style,
            target_audience=target_audience,
            generate_pdf=generate_pdf
        )
        
        # Combine results
        workflow_results = {
            'workflow_type': 'research_to_episode',
            'research_results': research_results,
            'episode_results': episode_results,
            'selected_topic': episode_results.get('topic'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save combined results with data manager
        json_file = self.data_manager.save_session(workflow_results, 'research_to_episode_workflow')
        workflow_results['json_report'] = json_file

        self.logger.info("Research-to-episode workflow completed successfully")
        return workflow_results

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()

    def update_configuration(self, new_config: Dict[str, Any]) -> None:
        """Update configuration"""
        self.config.update(new_config)
        self.logger.info("Configuration updated")

    def mark_topic_covered(self, topic: str, episode_date: Optional[str] = None):
        """Mark a topic as covered in history"""
        self.data_manager.add_topic_to_history(topic, episode_date)

    def list_previous_sessions(self, session_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """List previous research sessions"""
        return self.data_manager.list_sessions(session_type, limit)

    def load_previous_session(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a previous session by filename"""
        return self.data_manager.load_session(filename)

    def get_topic_history(self) -> List[Dict[str, Any]]:
        """Get all covered topics"""
        return self.data_manager.get_topic_history()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.data_manager.get_usage_stats()

    def chat(self, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """
        Chat with the assistant for brainstorming, ideation, and help

        Args:
            message: User's message
            conversation_history: Previous conversation [{"role": "user/assistant", "content": "..."}]

        Returns:
            Assistant's response
        """
        if conversation_history is None:
            conversation_history = []

        # Build conversation context
        system_msg = self.prompt_manager.get_system_message()

        conversation_text = ""
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                label = "You" if role == "assistant" else "User"
                conversation_text += f"{label}: {content}\n\n"

        full_prompt = conversation_text + f"User: {message}\n\nAssistant:"

        try:
            response = self.ai_client.generate_content(
                prompt=full_prompt,
                temperature=0.8,  # Slightly more creative for brainstorming
                system_message=system_msg
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Chat error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"