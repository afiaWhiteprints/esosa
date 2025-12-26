from typing import List, Dict, Any, Optional
import pandas as pd
from collections import Counter
import re
from datetime import datetime, timedelta, timezone
import logging

class TopicAnalyzer:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_keywords_from_posts(self, posts: List[Dict[str, Any]], min_frequency: int = 3) -> List[Dict[str, Any]]:
        """
        Extract trending keywords from social media posts
        
        Args:
            posts: List of social media post data (tweets, reddit posts, etc.)
            min_frequency: Minimum frequency for a keyword to be considered
            
        Returns:
            List of keyword dictionaries with frequency and context
        """
        if not posts:
            return []
        
        # Extract text from posts (handle different text field names)
        all_text = " ".join([self._extract_post_text(post) for post in posts])
        
        # Clean and extract keywords
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 
            'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'https', 'com',
            'www', 'http', 'twitter', 'tweet', 'retweet', 'like', 'follow', 'this',
            'that', 'with', 'have', 'will', 'from', 'they', 'been', 'said', 'each',
            'make', 'most', 'over', 'such', 'very', 'what', 'your'
        }
        
        filtered_words = [word for word in words if word not in stop_words]
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        # Filter by minimum frequency and create result
        keywords = []
        for word, count in word_counts.most_common():
            if count >= min_frequency:
                keywords.append({
                    'keyword': word,
                    'frequency': count,
                    'relevance_score': count / len(posts)
                })
        
        self.logger.info(f"Extracted {len(keywords)} keywords from {len(posts)} social media posts")
        return keywords

    def identify_trending_topics(self, posts: List[Dict[str, Any]], time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """
        Identify topics that are trending within a specific time window
        
        Args:
            posts: List of social media post data
            time_window_hours: Time window to analyze for trends
            
        Returns:
            List of trending topic dictionaries
        """
        if not posts:
            return []
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(posts)
        # Handle different timestamp field names
        timestamp_field = self._get_timestamp_field(posts[0])
        df['created_at'] = pd.to_datetime(df[timestamp_field], format='mixed', utc=True)
        
        # Filter to time window (use timezone-aware datetime)
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        recent_posts = df[df['created_at'] >= cutoff_time]
        
        if recent_posts.empty:
            return []
        
        # Extract hashtags and mentions
        hashtags = []
        mentions = []
        
        for _, post in recent_posts.iterrows():
            text = self._extract_post_text(post)
            hashtags.extend(re.findall(r'#(\w+)', text))
            mentions.extend(re.findall(r'@(\w+)', text))
        
        # Count engagement for trending topics
        hashtag_engagement = Counter()
        for _, post in recent_posts.iterrows():
            post_text = self._extract_post_text(post)
            post_hashtags = re.findall(r'#(\w+)', post_text)
            for hashtag in post_hashtags:
                engagement = self._get_post_engagement(post)
                hashtag_engagement[hashtag] += engagement
        
        # Create trending topics list
        trending = []
        for hashtag, engagement in hashtag_engagement.most_common(10):
            post_count = sum(1 for _, post in recent_posts.iterrows() if f'#{hashtag}' in self._extract_post_text(post))
            trending.append({
                'topic': hashtag,
                'post_count': post_count,
                'tweet_count': post_count,  # Keep for backward compatibility
                'total_engagement': engagement,
                'avg_engagement': engagement / post_count if post_count > 0 else 0,
                'trend_strength': (post_count * engagement) / len(recent_posts)
            })
        
        self.logger.info(f"Identified {len(trending)} trending topics")
        return trending

    def analyze_sentiment_patterns(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze sentiment patterns in social media posts (basic keyword-based approach)
        
        Args:
            posts: List of social media post data
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not posts:
            return {}
        
        positive_words = {
            'good', 'great', 'awesome', 'amazing', 'love', 'excellent', 'perfect',
            'wonderful', 'fantastic', 'best', 'incredible', 'outstanding', 'brilliant',
            'happy', 'excited', 'thrilled', 'delighted', 'pleased', 'satisfied'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'disgusting',
            'pathetic', 'useless', 'disappointing', 'frustrated', 'angry', 'sad',
            'upset', 'annoyed', 'furious', 'devastated', 'concerned', 'worried'
        }
        
        sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for post in posts:
            text = self._extract_post_text(post).lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                sentiment_scores['positive'] += 1
            elif neg_count > pos_count:
                sentiment_scores['negative'] += 1
            else:
                sentiment_scores['neutral'] += 1
        
        total = len(posts)
        return {
            'total_analyzed': total,
            'positive_percentage': (sentiment_scores['positive'] / total) * 100,
            'negative_percentage': (sentiment_scores['negative'] / total) * 100,
            'neutral_percentage': (sentiment_scores['neutral'] / total) * 100,
            'overall_sentiment': max(sentiment_scores, key=sentiment_scores.get)
        }

    def find_content_gaps(self, posts: List[Dict[str, Any]], target_keywords: List[str]) -> Dict[str, Any]:
        """
        Identify content gaps and opportunities based on social media analysis
        
        Args:
            posts: List of social media post data
            target_keywords: Keywords related to podcast niche
            
        Returns:
            Dictionary with gap analysis
        """
        if not posts or not target_keywords:
            return {}
        
        # Extract keywords from posts
        extracted_keywords = self.extract_keywords_from_posts(posts)
        extracted_words = {kw['keyword'] for kw in extracted_keywords}
        
        # Find gaps
        missing_keywords = set(target_keywords) - extracted_words
        covered_keywords = set(target_keywords) & extracted_words
        
        # Find related topics that might be trending
        all_keywords = [kw['keyword'] for kw in extracted_keywords[:20]]
        
        return {
            'target_keywords': target_keywords,
            'covered_keywords': list(covered_keywords),
            'missing_keywords': list(missing_keywords),
            'coverage_percentage': (len(covered_keywords) / len(target_keywords)) * 100,
            'trending_related': all_keywords,
            'content_opportunities': list(missing_keywords)[:5],
            'recommendations': self._generate_gap_recommendations(missing_keywords, all_keywords)
        }

    def _generate_gap_recommendations(self, missing_keywords: set, trending_keywords: List[str]) -> List[str]:
        """
        Generate recommendations based on content gaps
        
        Args:
            missing_keywords: Keywords not covered in current content
            trending_keywords: Currently trending keywords
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if missing_keywords:
            recommendations.append(f"Consider creating content around: {', '.join(list(missing_keywords)[:3])}")
        
        if trending_keywords:
            recommendations.append(f"Leverage trending topics: {', '.join(trending_keywords[:3])}")
        
        recommendations.append("Monitor competitor content for additional opportunities")
        recommendations.append("Engage with trending conversations to increase visibility")
        
        return recommendations

    def generate_content_calendar_suggestions(self, 
                                            trending_topics: List[Dict[str, Any]], 
                                            keywords: List[Dict[str, Any]],
                                            days_ahead: int = 30) -> List[Dict[str, Any]]:
        """
        Generate content calendar suggestions based on analysis
        
        Args:
            trending_topics: List of trending topics
            keywords: List of extracted keywords
            days_ahead: Number of days to plan ahead
            
        Returns:
            List of content suggestions with timing
        """
        suggestions = []
        
        # Combine trending topics and high-frequency keywords
        all_topics = []
        
        for topic in trending_topics[:10]:
            all_topics.append({
                'content': topic['topic'],
                'priority': 'high',
                'reason': f"Trending with {topic.get('post_count', topic.get('tweet_count', 0))} mentions"
            })
        
        for keyword in keywords[:15]:
            if keyword['frequency'] > 5:
                all_topics.append({
                    'content': keyword['keyword'],
                    'priority': 'medium',
                    'reason': f"High frequency: {keyword['frequency']} mentions"
                })
        
        # If no topics, return empty list
        if not all_topics:
            return []
        
        # Distribute suggestions over the time period
        weeks_in_period = max(1, days_ahead // 7)
        suggestions_per_week = max(1, len(all_topics) // weeks_in_period) if weeks_in_period > 0 else len(all_topics)
        
        for i, topic in enumerate(all_topics):
            week_number = (i // suggestions_per_week) + 1
            suggestions.append({
                'week': week_number,
                'topic': topic['content'],
                'priority': topic['priority'],
                'reason': topic['reason'],
                'suggested_format': self._suggest_content_format(topic['content'])
            })
        
        return suggestions[:max(1, days_ahead // 2)]  # Reasonable number of suggestions

    def _suggest_content_format(self, topic: str) -> str:
        """
        Suggest content format based on topic
        
        Args:
            topic: The topic to suggest format for
            
        Returns:
            Suggested content format
        """
        topic_lower = topic.lower()
        
        if any(word in topic_lower for word in ['how', 'tutorial', 'guide', 'tips']):
            return 'How-to/Tutorial Episode'
        elif any(word in topic_lower for word in ['interview', 'discussion', 'talk']):
            return 'Interview/Discussion Episode'
        elif any(word in topic_lower for word in ['news', 'update', 'latest']):
            return 'News/Update Episode'
        elif any(word in topic_lower for word in ['review', 'analysis', 'breakdown']):
            return 'Review/Analysis Episode'
        else:
            return 'Deep-dive Discussion Episode'

    def _extract_post_text(self, post: Dict[str, Any]) -> str:
        """
        Extract text content from different types of social media posts
        
        Args:
            post: Social media post data
            
        Returns:
            Text content of the post
        """
        # Handle different text field names across platforms
        text_fields = ['text', 'title', 'content', 'body', 'description']
        
        for field in text_fields:
            if field in post and post[field]:
                return str(post[field])
        
        # Fallback - return empty string if no text found
        return ""

    def _get_timestamp_field(self, post: Dict[str, Any]) -> str:
        """
        Get the appropriate timestamp field name for different platforms
        
        Args:
            post: Social media post data
            
        Returns:
            Name of the timestamp field
        """
        timestamp_fields = ['created_at', 'timestamp', 'date', 'created', 'published_at']
        
        for field in timestamp_fields:
            if field in post:
                return field
        
        # Default fallback
        return 'created_at'

    def _get_post_engagement(self, post: Dict[str, Any]) -> int:
        """
        Calculate engagement metrics for different types of posts
        
        Args:
            post: Social media post data
            
        Returns:
            Total engagement score
        """
        engagement = 0
        
        # Twitter-style metrics
        engagement += post.get('like_count', 0)
        engagement += post.get('retweet_count', 0)
        engagement += post.get('reply_count', 0)
        engagement += post.get('quote_count', 0)
        
        # Reddit-style metrics
        engagement += post.get('score', 0)
        engagement += post.get('ups', 0)
        engagement += post.get('num_comments', 0)
        
        # TikTok-style metrics
        engagement += post.get('digg_count', 0)  # likes on TikTok
        engagement += post.get('share_count', 0)
        engagement += post.get('comment_count', 0)
        engagement += post.get('play_count', 0) // 100  # Scale down view counts
        
        # Generic metrics
        engagement += post.get('likes', 0)
        engagement += post.get('shares', 0)
        engagement += post.get('comments', 0)
        engagement += post.get('views', 0) // 100  # Scale down view counts
        
        return engagement

    # Backward compatibility methods
    def extract_keywords_from_tweets(self, tweets: List[Dict[str, Any]], min_frequency: int = 3) -> List[Dict[str, Any]]:
        """Backward compatibility wrapper for extract_keywords_from_posts"""
        return self.extract_keywords_from_posts(tweets, min_frequency)

    def analyze_tweet_sentiment_patterns(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Backward compatibility wrapper for analyze_sentiment_patterns"""
        return self.analyze_sentiment_patterns(tweets)