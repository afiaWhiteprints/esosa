import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import requests
import time
load_dotenv()

class RedditClient:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if not self.rapidapi_key:
            raise ValueError("RapidAPI key not found in environment variables")
        
        self.base_url = "https://reddit34.p.rapidapi.com/getSearchPosts"
        self.headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "reddit34.p.rapidapi.com"
        }

        self.session_request_count = 0
        self.max_requests_per_session = 5
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def reset_session_counter(self):
        """Reset the session request counter for a new research session"""
        self.session_request_count = 0
        self.logger.info(f"🔄 Reddit session counter reset. Ready for up to {self.max_requests_per_session} API requests.")

    def search_reddit_by_keywords(self, keywords: List[str], count: int = 100,
                                   use_random_keywords: bool = False,
                                   random_keyword_count: int = 10) -> List[Dict[str, Any]]:
        """
        Search Reddit posts by keywords (wrapper for search_posts with random keyword support)

        Args:
            keywords: List of keywords to search for
            count: Maximum number of posts to return
            use_random_keywords: Whether to randomly select keywords
            random_keyword_count: Number of keywords to randomly select

        Returns:
            List of post data dictionaries
        """
        import random as rand
        search_keywords = keywords
        if use_random_keywords and len(keywords) > random_keyword_count:
            search_keywords = rand.sample(keywords, random_keyword_count)
            self.logger.info(f"🎲 Randomly selected {len(search_keywords)} Reddit keywords")

        return self.search_posts(search_keywords, count)

    def get_trending_posts(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get trending/hot posts from Reddit

        Args:
            count: Number of trending posts to return

        Returns:
            List of trending post data
        """
        # Search for general trending content
        trending_keywords = ["trending", "viral", "popular"]
        return self.search_posts(trending_keywords, count)

    def search_posts(self, keywords: List[str], max_results: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for posts containing specified keywords
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of posts to return
            days_back: Number of days to look back
            
        Returns:
            List of post data dictionaries
        """
        try:
            # Handle long keyword lists by splitting into multiple searches
            all_posts = []
            
            # Split keywords into chunks that fit Reddit API query limits
            keyword_chunks = self._split_keywords_for_search(keywords)
            
            for chunk in keyword_chunks:
                # Create search query for this chunk - simplified format
                query = " ".join(chunk)  # Simple space-separated keywords
                
                # Calculate results per chunk
                results_per_chunk = max_results // len(keyword_chunks)
                if len(keyword_chunks) == 1:
                    results_per_chunk = max_results
                
                self.logger.info(f"Searching with query chunk ({len(query)} chars): {query[:100]}...")
                
                querystring = {
                    "type": "Top",
                    "count": str(min(results_per_chunk, 100)),
                    "query": query
                }
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=querystring,
                    timeout=30
                )
                
                self.session_request_count += 1
                self.logger.info(f"API request {self.session_request_count}/{self.max_requests_per_session}")
                
                chunk_posts = []
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Debug: Log response structure
                    self.logger.info(f"Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
                    
                    # Handle Reddit API response structure
                    posts_data = []
                    if isinstance(response_data, dict):
                        # Check for Reddit API structure: {"success": true, "data": {"posts": [...]}}
                        if response_data.get('success') and 'data' in response_data:
                            data = response_data['data']
                            if 'posts' in data and isinstance(data['posts'], list):
                                posts_data = data['posts']
                                self.logger.info(f"Found {len(posts_data)} posts in Reddit API response")
                        # Fallback: check for direct posts array
                        elif 'posts' in response_data:
                            posts_data = response_data['posts']
                        # Fallback: check for data array
                        elif 'data' in response_data and isinstance(response_data['data'], list):
                            posts_data = response_data['data']
                        else:
                            # Log the actual structure for debugging
                            self.logger.warning(f"Unexpected response structure: {list(response_data.keys())}")
                            posts_data = []
                    elif isinstance(response_data, list):
                        posts_data = response_data
                    
                    for post_item in posts_data:
                        try:
                            # Reddit posts have structure: {"kind": "t3", "data": {...}}
                            post_data = post_item
                            if isinstance(post_item, dict) and 'data' in post_item:
                                post_data = post_item['data']
                            
                            # Extract Reddit post information
                            post_info = {
                                'id': post_data.get('id', 'unknown'),
                                'title': post_data.get('title', ''),
                                'text': post_data.get('selftext', ''),
                                'author': post_data.get('author', 'unknown'),
                                'subreddit': post_data.get('subreddit', 'unknown'),
                                'created_at': post_data.get('created_utc', 0),
                                'upvote_count': post_data.get('ups', 0),
                                'downvote_count': post_data.get('downs', 0),
                                'score': post_data.get('score', 0),
                                'num_comments': post_data.get('num_comments', 0),
                                'permalink': post_data.get('permalink', ''),
                                'url': post_data.get('url', ''),
                                'upvote_ratio': post_data.get('upvote_ratio', 0.0),
                                'is_video': post_data.get('is_video', False),
                                'over_18': post_data.get('over_18', False)
                            }
                            chunk_posts.append(post_info)
                        except Exception as e:
                            self.logger.warning(f"Error parsing Reddit post: {str(e)}")
                            continue
                else:
                    self.logger.error(f"API request failed with status {response.status_code}: {response.text}")
                
                all_posts.extend(chunk_posts)
                self.logger.info(f"Retrieved {len(chunk_posts)} posts from chunk")
                
                # Rate limiting
                time.sleep(1)
            
            # Remove duplicates and limit to max_results
            seen_ids = set()
            unique_posts = []
            for post in all_posts:
                if post['id'] not in seen_ids:
                    seen_ids.add(post['id'])
                    unique_posts.append(post)
                    if len(unique_posts) >= max_results:
                        break
            
            self.logger.info(f"Retrieved {len(unique_posts)} total unique posts for keywords: {keywords[:5]}...")
            return unique_posts
            
        except Exception as e:
            self.logger.error(f"Error searching posts: {str(e)}")
            return []


    def analyze_engagement(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement metrics from Reddit posts
        
        Args:
            posts: List of Reddit post data
            
        Returns:
            Dictionary with engagement analysis
        """
        if not posts:
            return {}
        
        total_posts = len(posts)
        total_upvotes = sum(post.get('upvote_count', 0) for post in posts)
        total_downvotes = sum(post.get('downvote_count', 0) for post in posts)
        total_score = sum(post.get('score', 0) for post in posts)
        total_comments = sum(post.get('num_comments', 0) for post in posts)
        
        # Calculate average upvote ratio
        upvote_ratios = [post.get('upvote_ratio', 0.0) for post in posts if post.get('upvote_ratio', 0.0) > 0]
        avg_upvote_ratio = sum(upvote_ratios) / len(upvote_ratios) if upvote_ratios else 0.0
        
        # Sort by total engagement (score + comments)
        sorted_posts = sorted(posts, 
                             key=lambda x: x.get('score', 0) + x.get('num_comments', 0), 
                             reverse=True)
        
        return {
            'total_posts': total_posts,
            'total_upvotes': total_upvotes,
            'total_downvotes': total_downvotes,
            'total_score': total_score,
            'total_comments': total_comments,
            'avg_upvotes': total_upvotes / total_posts if total_posts > 0 else 0,
            'avg_downvotes': total_downvotes / total_posts if total_posts > 0 else 0,
            'avg_score': total_score / total_posts if total_posts > 0 else 0,
            'avg_comments': total_comments / total_posts if total_posts > 0 else 0,
            'avg_upvote_ratio': avg_upvote_ratio,
            'top_performing_posts': sorted_posts[:5]
        }

    def _split_keywords_for_search(self, keywords: List[str]) -> List[List[str]]:
        """
        Split keywords into chunks that fit Reddit API search query length limit
        
        Args:
            keywords: List of keywords to split
            
        Returns:
            List of keyword chunks
        """
        MAX_QUERY_LENGTH = 100  # Reduce chunk size for better Reddit search results  
        chunks = []
        current_chunk = []
        current_length = 0
        
        for keyword in keywords:
            # Calculate length this keyword would add (space-separated)
            keyword_length = len(keyword) + 1  # +1 for space
            
            # If adding this keyword would exceed limit, start new chunk
            if current_length + keyword_length > MAX_QUERY_LENGTH and current_chunk:
                chunks.append(current_chunk)
                current_chunk = [keyword]
                current_length = keyword_length
            else:
                current_chunk.append(keyword)
                current_length += keyword_length
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        self.logger.info(f"Split {len(keywords)} keywords into {len(chunks)} search chunks")
        return chunks
    
    def _get_metric(self, post: Dict[str, Any], *metric_names: str) -> int:
        """
        Extract metric value from post data, handling different possible structures
        
        Args:
            post: Post data dictionary
            *metric_names: Possible metric field names to check
            
        Returns:
            Metric value as integer, 0 if not found
        """
        # Check public_metrics first (Twitter API v2 structure)
        if 'public_metrics' in post:
            for metric_name in metric_names:
                if metric_name in post['public_metrics']:
                    return post['public_metrics'][metric_name]
        
        # Check direct fields (Twitter API v1.1 structure)
        for metric_name in metric_names:
            if metric_name in post:
                return post[metric_name]
        
        # Default to 0 if not found
        return 0