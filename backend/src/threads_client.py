import requests
import os
import random
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
import time

load_dotenv()

class ThreadsClient:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if not self.rapidapi_key:
            raise ValueError("RapidAPI key not found in environment variables")
        
        # Using Threads API from RapidAPI
        self.base_url = "https://threads-api4.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "threads-api4.p.rapidapi.com"
        }
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Session-based rate limiting
        self.session_request_count = 0
        self.max_requests_per_session = 5

    def reset_session_counter(self):
        """Reset the session request counter for a new research session"""
        self.session_request_count = 0
        self.logger.info(f"🔄 Threads session counter reset. Ready for up to {self.max_requests_per_session} API requests.")

    def search_threads_by_keywords(self, 
                                   keywords: List[str], 
                                   count: int = 20, 
                                   use_random_keywords: bool = False, 
                                   random_keyword_count: int = 10) -> List[Dict[str, Any]]:
        """
        Search Threads posts by keywords
        
        Args:
            keywords: List of keywords to search for
            count: Number of posts to retrieve per keyword
            use_random_keywords: Whether to randomly select keywords
            random_keyword_count: Number of random keywords to select if use_random_keywords is True
            
        Returns:
            List of thread data dictionaries
        """
        all_threads = []
        
        # Apply random keyword selection if requested
        selected_keywords = keywords
        if use_random_keywords and len(keywords) > random_keyword_count:
            selected_keywords = random.sample(keywords, random_keyword_count)
            self.logger.info(f"🎲 Threads: Randomly selected {len(selected_keywords)} keywords from {len(keywords)} total: {selected_keywords}")
        elif use_random_keywords:
            self.logger.info(f"Threads: Using all {len(selected_keywords)} keywords (less than requested {random_keyword_count})")
        
        # Search for each keyword
        for keyword in selected_keywords:
            # Check if we've hit the request limit
            if self.session_request_count >= self.max_requests_per_session:
                self.logger.warning(f"🚫 Threads API request limit reached ({self.max_requests_per_session} requests). Stopping to preserve quota.")
                break
                
            try:
                # Use the search endpoint
                url = f"{self.base_url}/api/search/recent"
                params = {
                    "query": keyword,
                    "count": str(min(count, 50))  # API might have limits
                }
                
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                self.session_request_count += 1
                
                data = response.json()
                self.logger.info(f"Threads API response status: {response.status_code} for '{keyword}' (Request {self.session_request_count}/{self.max_requests_per_session})")
                
                # Parse response structure based on actual API format
                threads_data = []
                
                # Check if API call was successful
                if isinstance(data, dict) and data.get('status') == 'ok':
                    # Parse complex nested response structure
                    api_data = data.get('data', {})
                    if isinstance(api_data, dict) and 'searchResults' in api_data:
                        search_results = api_data.get('searchResults', {})
                        if isinstance(search_results, dict) and 'edges' in search_results:
                            edges = search_results.get('edges', [])
                            self.logger.info(f"🧵 Found {len(edges)} thread edges in API response for '{keyword}'")
                            
                            # Extract threads from edges structure
                            for edge in edges:
                                if isinstance(edge, dict) and 'node' in edge:
                                    node = edge.get('node', {})
                                    if isinstance(node, dict) and 'thread' in node:
                                        thread = node.get('thread', {})
                                        threads_data.append(thread)
                        else:
                            self.logger.warning(f"'searchResults' found but no 'edges' for '{keyword}'")
                    else:
                        self.logger.warning(f"No 'searchResults' key found in API data for '{keyword}'")
                else:
                    # API error
                    error_msg = data.get('error', 'Unknown error') if isinstance(data, dict) else 'Invalid response format'
                    self.logger.error(f"Threads API error for '{keyword}': {error_msg}")
                    continue
                
                for thread in threads_data:
                    # Skip non-dict items
                    if not isinstance(thread, dict):
                        self.logger.warning(f"Skipping non-dict thread data: {type(thread)} - {str(thread)[:100]}")
                        continue
                        
                    # Trust the API's search results - no additional filtering needed
                    thread_info = self._parse_thread_data(thread, keyword)
                    all_threads.append(thread_info)
                
                # Count how many threads we actually processed 
                processed_threads = len([t for t in all_threads if t.get('matched_keyword') == keyword])
                self.logger.info(f"✅ Processed {processed_threads} threads from {len(threads_data)} API results for '{keyword}'")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                # Still count failed requests against the limit
                self.session_request_count += 1
                self.logger.error(f"Error searching Threads for '{keyword}': {str(e)} (Request {self.session_request_count}/{self.max_requests_per_session})")
                continue
        
        # Remove duplicates
        unique_threads = self._remove_duplicates(all_threads)
        self.logger.info(f"📊 Threads session complete: Retrieved {len(unique_threads)} unique threads using {self.session_request_count}/{self.max_requests_per_session} API requests for keywords: {selected_keywords}")
        return unique_threads

    def search_threads_by_hashtag(self, hashtag: str, count: int = 20) -> List[Dict[str, Any]]:
        """
        Search Threads posts by hashtag
        
        Args:
            hashtag: Hashtag to search for (without #)
            count: Number of posts to retrieve
            
        Returns:
            List of thread data dictionaries
        """
        # Use the search endpoint with hashtag format
        return self.search_threads_by_keywords([f"#{hashtag}"], count)

    def get_trending_threads(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get trending Threads posts by searching for popular terms
        
        Args:
            count: Number of trending posts to retrieve
            
        Returns:
            List of thread data dictionaries
        """
        # Search for popular/trending terms
        trending_terms = ["trending", "viral", "popular", "breaking", "news"]
        
        # Get some threads from each trending term
        threads_per_term = max(1, count // len(trending_terms))
        all_threads = []
        
        for term in trending_terms:
            try:
                threads = self.search_threads_by_keywords([term], threads_per_term)
                for thread in threads:
                    thread['source'] = 'threads_trending'
                all_threads.extend(threads)
                
                if len(all_threads) >= count:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error getting trending threads for term '{term}': {str(e)}")
                continue
        
        # Sort by engagement and return top threads
        sorted_threads = sorted(all_threads, 
                               key=lambda x: x.get('like_count', 0) + x.get('reply_count', 0), 
                               reverse=True)
        
        result = sorted_threads[:count]
        self.logger.info(f"Retrieved {len(result)} trending-style threads")
        return result

    def analyze_engagement(self, threads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement metrics from Threads posts
        
        Args:
            threads: List of thread data
            
        Returns:
            Dictionary with engagement analysis
        """
        if not threads:
            return {}
        
        total_threads = len(threads)
        total_likes = sum(thread.get('like_count', 0) for thread in threads)
        total_replies = sum(thread.get('reply_count', 0) for thread in threads)
        total_reposts = sum(thread.get('repost_count', 0) for thread in threads)
        
        # Sort by total engagement
        sorted_threads = sorted(threads, 
                               key=lambda x: x.get('like_count', 0) + x.get('reply_count', 0) + x.get('repost_count', 0), 
                               reverse=True)
        
        return {
            'total_threads': total_threads,
            'total_likes': total_likes,
            'total_replies': total_replies,
            'total_reposts': total_reposts,
            'avg_likes': total_likes / total_threads if total_threads > 0 else 0,
            'avg_replies': total_replies / total_threads if total_threads > 0 else 0,
            'avg_reposts': total_reposts / total_threads if total_threads > 0 else 0,
            'top_performing_threads': sorted_threads[:5],
            'engagement_rate': (total_likes + total_replies + total_reposts) / total_threads if total_threads > 0 else 0
        }

    def filter_by_keywords(self, threads: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filter threads based on keyword matching in content
        
        Args:
            threads: List of thread data
            keywords: List of keywords to match against
            
        Returns:
            Filtered list of threads
        """
        filtered_threads = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for thread in threads:
            text = thread.get('text', '').lower()
            
            # Check if any keyword matches thread text
            text_match = any(keyword in text for keyword in keywords_lower)
            
            if text_match:
                thread['match_type'] = ['content']
                
                # Add matched keywords
                thread['matched_keywords'] = [
                    kw for kw in keywords 
                    if kw.lower() in text
                ]
                
                filtered_threads.append(thread)
        
        self.logger.info(f"Filtered {len(filtered_threads)} threads matching keywords from {len(threads)} total")
        return filtered_threads

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#(\w+)', text)
        return hashtags

    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        mentions = re.findall(r'@(\w+)', text)
        return mentions

    def _remove_duplicates(self, threads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate threads based on ID"""
        seen_ids = set()
        unique_threads = []
        
        for thread in threads:
            thread_id = thread.get('id')
            if thread_id and thread_id not in seen_ids:
                seen_ids.add(thread_id)
                unique_threads.append(thread)
        
        return unique_threads

    def _parse_thread_data(self, thread: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Parse thread data from API response into standardized format
        
        Args:
            thread: Raw thread data from API
            keyword: The keyword that matched this thread
            
        Returns:
            Standardized thread data dictionary
        """
        try:
            # Ensure we have a valid dictionary
            if not isinstance(thread, dict):
                self.logger.warning(f"Invalid thread data type: {type(thread)}")
                return self._create_empty_thread_data(keyword)
            
            # Handle Threads API nested structure: thread.thread_items[0].post
            thread_id = thread.get('id', '')
            
            # Extract the first thread item (main post)
            thread_items = thread.get('thread_items', [])
            if not thread_items:
                self.logger.warning(f"No thread_items found in thread {thread_id}")
                return self._create_empty_thread_data(keyword)
            
            # Get the main post
            post = thread_items[0].get('post', {})
            if not post:
                self.logger.warning(f"No post found in first thread_item for thread {thread_id}")
                return self._create_empty_thread_data(keyword)
            
            # Extract text from caption or text_post_app_info
            text = ""
            if 'caption' in post and post['caption']:
                text = post['caption'].get('text', '')
            elif 'text_post_app_info' in post:
                text_fragments = post['text_post_app_info'].get('text_fragments', {}).get('fragments', [])
                if text_fragments:
                    text = text_fragments[0].get('plaintext', '')
            
            # Author information
            user = post.get('user', {})
            author_name = user.get('username', '')
            
            # Engagement metrics
            like_count = post.get('like_count', 0)
            
            # Thread-specific metrics from text_post_app_info
            app_info = post.get('text_post_app_info', {})
            reply_count = app_info.get('direct_reply_count', 0)
            repost_count = app_info.get('repost_count', 0)
            
            # Thread URL (construct from code)
            code = post.get('code', '')
            thread_url = f"https://www.threads.net/@{author_name}/post/{code}" if code and author_name else ''
            
            # Create time
            created_at = post.get('taken_at', '')
            
            return {
                'id': str(thread_id),
                'text': text,
                'hashtags': self._extract_hashtags(text),
                'mentions': self._extract_mentions(text),
                'like_count': int(like_count) if like_count else 0,
                'reply_count': int(reply_count) if reply_count else 0,
                'repost_count': int(repost_count) if repost_count else 0,
                'created_at': created_at,
                'author': author_name,
                'thread_url': thread_url,
                'matched_keyword': keyword,
                'source': 'threads_search'
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing thread data: {str(e)}")
            return self._create_empty_thread_data(keyword)
    
    def _create_empty_thread_data(self, keyword: str) -> Dict[str, Any]:
        """Create empty thread data structure for error cases"""
        return {
            'id': 'unknown',
            'text': '',
            'hashtags': [],
            'mentions': [],
            'like_count': 0,
            'reply_count': 0,
            'repost_count': 0,
            'created_at': '',
            'author': 'unknown',
            'thread_url': '',
            'matched_keyword': keyword,
            'source': 'threads_search_error'
        }