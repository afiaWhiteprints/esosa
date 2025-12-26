import requests
import os
import random
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
import time

load_dotenv()

class TikTokClient:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if not self.rapidapi_key:
            raise ValueError("RapidAPI key not found in environment variables")
        
        # Using TikTok Scraper API from RapidAPI - adjust based on your chosen API
        self.base_url = "https://tiktok-scraper7.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "tiktok-scraper7.p.rapidapi.com"
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Session-based rate limiting
        self.session_request_count = 0
        self.max_requests_per_session = 5

    def reset_session_counter(self):
        """Reset the session request counter for a new research session"""
        self.session_request_count = 0
        self.logger.info(f"🔄 TikTok session counter reset. Ready for up to {self.max_requests_per_session} API requests.")

    def search_videos_by_hashtag(self, hashtag: str, count: int = 20, regions: List[str] = ["us", "ng"]) -> List[Dict[str, Any]]:
        """
        Search TikTok videos by hashtag using the search endpoint with # prefix
        
        Args:
            hashtag: Hashtag to search for (without #)
            count: Number of videos to retrieve
            regions: List of region codes to search in
            
        Returns:
            List of video data dictionaries
        """
        # Use the search endpoint with hashtag format since dedicated hashtag endpoint doesn't exist
        return self.search_videos_by_keywords([f"#{hashtag}"], count, regions)

    def search_videos_by_keywords(self, keywords: List[str], count: int = 20, regions: List[str] = ["us", "ng"], 
                                use_random_keywords: bool = False, random_keyword_count: int = 10) -> List[Dict[str, Any]]:
        """
        Search TikTok videos by keywords using the feed/search endpoint
        
        Args:
            keywords: List of keywords to search for
            count: Number of videos to retrieve per keyword per region
            regions: List of region codes (default: ["us", "ng"] for US and Nigeria)
            use_random_keywords: Whether to randomly select keywords
            random_keyword_count: Number of random keywords to select if use_random_keywords is True
            
        Returns:
            List of video data dictionaries
        """
        all_videos = []
        
        # Apply random keyword selection if requested
        selected_keywords = keywords
        if use_random_keywords and len(keywords) > random_keyword_count:
            selected_keywords = random.sample(keywords, random_keyword_count)
            self.logger.info(f"🎲 TikTok: Randomly selected {len(selected_keywords)} keywords from {len(keywords)} total: {selected_keywords}")
        elif use_random_keywords:
            self.logger.info(f"TikTok: Using all {len(selected_keywords)} keywords (less than requested {random_keyword_count})")
        
        # Search across regions and keywords
        for region in regions:
            self.logger.info(f"🌍 Searching TikTok region: {region.upper()}")
            for keyword in selected_keywords:
                # Check if we've hit the request limit
                if self.session_request_count >= self.max_requests_per_session:
                    self.logger.warning(f"🚫 TikTok API request limit reached ({self.max_requests_per_session} requests). Stopping to preserve quota.")
                    break
                
                try:
                    # Use the correct endpoint structure from documentation
                    url = f"{self.base_url}/feed/search"
                    params = {
                        "keywords": keyword,
                        "region": region,
                        "count": str(min(count, 50)),  # API might have limits
                        "cursor": "0",
                        "publish_time": "0",  # All time
                        "sort_type": "0"  # Default sort
                    }
                    
                    response = requests.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    self.session_request_count += 1
                    
                    data = response.json()
                    self.logger.info(f"TikTok API response status: {response.status_code} for '{keyword}' in {region} (Request {self.session_request_count}/{self.max_requests_per_session})")
                    
                    # Parse response structure based on actual API format
                    videos_data = []
                    
                    # Check if API call was successful
                    if isinstance(data, dict) and data.get('code') == 0:
                        # Success response format: {"code": 0, "msg": "success", "data": {"videos": [...], "cursor": "...", "hasMore": true}}
                        api_data = data.get('data', {})
                        if isinstance(api_data, dict) and 'videos' in api_data:
                            videos_data = api_data.get('videos', [])
                            self.logger.info(f"📹 Found {len(videos_data)} raw videos in API response for '{keyword}' in {region}")
                        else:
                            self.logger.warning(f"No 'videos' key found in API data for '{keyword}' in {region}")
                    else:
                        # API error
                        error_msg = data.get('msg', 'Unknown error') if isinstance(data, dict) else 'Invalid response format'
                        self.logger.error(f"TikTok API error for '{keyword}' in {region}: {error_msg}")
                        continue
                    
                    for video in videos_data:
                        # Skip non-dict items (API might return mixed types)
                        if not isinstance(video, dict):
                            self.logger.warning(f"Skipping non-dict video data: {type(video)} - {str(video)[:100]}")
                            continue
                            
                        # Trust the API's search results - if it returned the video for our keyword, it's relevant
                        # No need to double-filter since TikTok's search algorithm is more sophisticated
                        video_info = self._parse_video_data(video, keyword)
                        video_info['region'] = region  # Add region info
                        all_videos.append(video_info)
                    
                    # Count how many videos we actually processed 
                    processed_videos = len([v for v in all_videos if v.get('matched_keyword') == keyword and v.get('region') == region])
                    self.logger.info(f"✅ Processed {processed_videos} videos from {len(videos_data)} API results for '{keyword}' in {region}")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    # Still count failed requests against the limit to avoid quota issues
                    self.session_request_count += 1
                    self.logger.error(f"Error searching TikTok for '{keyword}' in {region}: {str(e)} (Request {self.session_request_count}/{self.max_requests_per_session})")
                    continue
            
            # Break outer loop if we've reached the request limit
            if self.session_request_count >= self.max_requests_per_session:
                self.logger.warning(f"🚫 TikTok API request limit reached. Processed {self.session_request_count} requests across regions.")
                break
        
        # Remove duplicates
        unique_videos = self._remove_duplicates(all_videos)
        self.logger.info(f"📊 TikTok session complete: Retrieved {len(unique_videos)} unique videos using {self.session_request_count}/{self.max_requests_per_session} API requests for keywords: {selected_keywords}")
        return unique_videos

    def get_trending_videos(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get trending TikTok videos by searching for popular terms
        
        Args:
            count: Number of trending videos to retrieve
            
        Returns:
            List of video data dictionaries
        """
        # Since there may not be a dedicated trending endpoint, search for popular terms
        trending_terms = ["fyp", "foryou", "viral", "trending", "foryoupage"]
        
        # Get some videos from each trending term
        videos_per_term = max(1, count // len(trending_terms))
        all_videos = []
        
        for term in trending_terms:
            try:
                videos = self.search_videos_by_keywords([term], videos_per_term)
                for video in videos:
                    video['source'] = 'tiktok_trending'
                all_videos.extend(videos)
                
                if len(all_videos) >= count:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error getting trending videos for term '{term}': {str(e)}")
                continue
        
        # Sort by engagement and return top videos
        sorted_videos = sorted(all_videos, 
                             key=lambda x: x.get('like_count', 0) + x.get('play_count', 0), 
                             reverse=True)
        
        result = sorted_videos[:count]
        self.logger.info(f"Retrieved {len(result)} trending-style videos")
        return result

    def filter_by_keywords(self, videos: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filter videos based on keyword matching in captions and hashtags
        
        Args:
            videos: List of video data
            keywords: List of keywords to match against
            
        Returns:
            Filtered list of videos
        """
        filtered_videos = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for video in videos:
            caption = video.get('caption', '').lower()
            hashtags = [tag.lower() for tag in video.get('hashtags', [])]
            
            # Check if any keyword matches caption or hashtags
            caption_match = any(keyword in caption for keyword in keywords_lower)
            hashtag_match = any(
                any(keyword in hashtag for keyword in keywords_lower) 
                for hashtag in hashtags
            )
            
            if caption_match or hashtag_match:
                video['match_type'] = []
                if caption_match:
                    video['match_type'].append('caption')
                if hashtag_match:
                    video['match_type'].append('hashtag')
                
                # Add matched keywords
                video['matched_keywords'] = [
                    kw for kw in keywords 
                    if kw.lower() in caption or any(kw.lower() in tag for tag in hashtags)
                ]
                
                filtered_videos.append(video)
        
        self.logger.info(f"Filtered {len(filtered_videos)} videos matching keywords from {len(videos)} total")
        return filtered_videos

    def analyze_engagement(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement metrics from TikTok videos
        
        Args:
            videos: List of video data
            
        Returns:
            Dictionary with engagement analysis
        """
        if not videos:
            return {}
        
        total_videos = len(videos)
        total_likes = sum(video.get('like_count', 0) for video in videos)
        total_comments = sum(video.get('comment_count', 0) for video in videos)
        total_shares = sum(video.get('share_count', 0) for video in videos)
        total_plays = sum(video.get('play_count', 0) for video in videos)
        
        # Sort by total engagement
        sorted_videos = sorted(videos, 
                             key=lambda x: x.get('like_count', 0) + x.get('comment_count', 0) + x.get('share_count', 0), 
                             reverse=True)
        
        return {
            'total_videos': total_videos,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_plays': total_plays,
            'avg_likes': total_likes / total_videos if total_videos > 0 else 0,
            'avg_comments': total_comments / total_videos if total_videos > 0 else 0,
            'avg_shares': total_shares / total_videos if total_videos > 0 else 0,
            'avg_plays': total_plays / total_videos if total_videos > 0 else 0,
            'top_performing_videos': sorted_videos[:5],
            'engagement_rate': (total_likes + total_comments + total_shares) / total_plays if total_plays > 0 else 0
        }

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags

    def _is_relevant_video(self, video: Dict[str, Any], keywords: List[str]) -> bool:
        """Check if video is relevant based on keywords"""
        try:
            if not isinstance(video, dict):
                return False
                
            caption = video.get('desc', '').lower()
            keywords_lower = [kw.lower() for kw in keywords]
            
            return any(keyword in caption for keyword in keywords_lower)
        except Exception as e:
            self.logger.warning(f"Error checking video relevance: {str(e)}")
            return False

    def _remove_duplicates(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate videos based on ID"""
        seen_ids = set()
        unique_videos = []
        
        for video in videos:
            video_id = video.get('id')
            if video_id and video_id not in seen_ids:
                seen_ids.add(video_id)
                unique_videos.append(video)
        
        return unique_videos

    def get_hashtag_trends(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Get trending hashtags related to keywords
        
        Args:
            keywords: List of keywords to find related hashtags for
            
        Returns:
            List of trending hashtag data
        """
        hashtag_data = []
        
        for keyword in keywords:
            # Check if we've already hit the rate limit
            if self.session_request_count >= self.max_requests_per_session:
                self.logger.warning(f"🚫 Cannot get hashtag trends for '{keyword}': Session rate limit already reached ({self.session_request_count}/{self.max_requests_per_session})")
                break
                
            try:
                # Search videos for the keyword and collect hashtags
                videos = self.search_videos_by_keywords([keyword], count=30)
                
                # Count hashtag frequencies
                hashtag_counts = {}
                for video in videos:
                    for hashtag in video.get('hashtags', []):
                        hashtag_lower = hashtag.lower()
                        if hashtag_lower not in hashtag_counts:
                            hashtag_counts[hashtag_lower] = {
                                'hashtag': hashtag,
                                'count': 0,
                                'total_engagement': 0
                            }
                        hashtag_counts[hashtag_lower]['count'] += 1
                        hashtag_counts[hashtag_lower]['total_engagement'] += (
                            video.get('like_count', 0) + 
                            video.get('comment_count', 0) + 
                            video.get('share_count', 0)
                        )
                
                # Sort by popularity and engagement
                sorted_hashtags = sorted(
                    hashtag_counts.values(),
                    key=lambda x: (x['count'], x['total_engagement']),
                    reverse=True
                )
                
                hashtag_data.extend(sorted_hashtags[:10])  # Top 10 per keyword
                
            except Exception as e:
                self.logger.error(f"Error getting hashtag trends for '{keyword}': {str(e)}")
                continue
        
        # Remove duplicates and return top overall hashtags
        unique_hashtags = self._remove_duplicate_hashtags(hashtag_data)
        return unique_hashtags[:20]  # Top 20 overall

    def _remove_duplicate_hashtags(self, hashtags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate hashtags"""
        seen_hashtags = set()
        unique_hashtags = []
        
        for hashtag_data in hashtags:
            hashtag = hashtag_data['hashtag'].lower()
            if hashtag not in seen_hashtags:
                seen_hashtags.add(hashtag)
                unique_hashtags.append(hashtag_data)
        
        return unique_hashtags

    def _parse_video_data(self, video: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Parse video data from API response into standardized format
        
        Args:
            video: Raw video data from API
            keyword: The keyword that matched this video
            
        Returns:
            Standardized video data dictionary
        """
        try:
            # Ensure we have a valid dictionary
            if not isinstance(video, dict):
                self.logger.warning(f"Invalid video data type: {type(video)}")
                return self._create_empty_video_data(keyword)
            
            # Handle different possible response structures
            video_id = video.get('id') or video.get('video_id') or video.get('aweme_id', '')
        
            # Description/caption - could be in different fields
            caption = (video.get('desc') or 
                    video.get('description') or 
                    video.get('video_description') or 
                    video.get('title', ''))
            
            # Author information
            author_info = video.get('author') or video.get('user') or {}
            author_name = (author_info.get('uniqueId') or 
                        author_info.get('unique_id') or 
                        author_info.get('username') or 
                        author_info.get('nickname', ''))
            
            # Statistics - try different possible structures
            stats = video.get('stats') or video.get('statistics') or {}
            like_count = (stats.get('diggCount') or 
                        stats.get('like_count') or 
                        stats.get('digg_count') or 
                        stats.get('likes', 0))
            
            comment_count = (stats.get('commentCount') or 
                            stats.get('comment_count') or 
                            stats.get('comments', 0))
            
            share_count = (stats.get('shareCount') or 
                        stats.get('share_count') or 
                        stats.get('shares', 0))
            
            play_count = (stats.get('playCount') or 
                        stats.get('play_count') or 
                        stats.get('views') or 
                        stats.get('view_count', 0))
            
            # Video URL
            video_data = video.get('video') or {}
            video_url = (video_data.get('playAddr') or 
                        video_data.get('play_url') or 
                        video_data.get('downloadAddr') or '')
            
            # Create time
            created_at = video.get('createTime') or video.get('create_time') or video.get('published_at', '')
            
            return {
                'id': str(video_id),
                'caption': caption,
                'hashtags': self._extract_hashtags(caption),
                'like_count': int(like_count) if like_count else 0,
                'comment_count': int(comment_count) if comment_count else 0,
                'share_count': int(share_count) if share_count else 0,
                'play_count': int(play_count) if play_count else 0,
                'created_at': created_at,
                'author': author_name,
                'video_url': video_url,
                'matched_keyword': keyword,
                'source': 'tiktok_search'
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing video data: {str(e)}")
            return self._create_empty_video_data(keyword)
    
    def _create_empty_video_data(self, keyword: str) -> Dict[str, Any]:
        """Create empty video data structure for error cases"""
        return {
            'id': 'unknown',
            'caption': '',
            'hashtags': [],
            'like_count': 0,
            'comment_count': 0,
            'share_count': 0,
            'play_count': 0,
            'created_at': '',
            'author': 'unknown',
            'video_url': '',
            'matched_keyword': keyword,
            'source': 'tiktok_search_error'
        }