import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging
import requests
import time
load_dotenv()

class TwitterClient:
    def __init__(self):
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        if not self.rapidapi_key:
            raise ValueError("RapidAPI key not found in environment variables")
        
        self.base_url = "https://twitter241.p.rapidapi.com/search-v2"
        self.headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "twitter241.p.rapidapi.com"
        }

        self.session_request_count = 0
        self.max_requests_per_session = 5
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def reset_session_counter(self):
        """Reset the session request counter for a new research session"""
        self.session_request_count = 0
        self.logger.info(f"🔄 Twitter session counter reset. Ready for up to {self.max_requests_per_session} API requests.")

    def search_tweets(self, keywords: List[str], max_results: int = 100, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for tweets containing specified keywords
        
        Args:
            keywords: List of keywords to search for
            max_results: Maximum number of tweets to return
            days_back: Number of days to look back
            
        Returns:
            List of tweet data dictionaries
        """
        try:
            # Handle long keyword lists by splitting into multiple searches
            all_tweets = []
            
            # Split keywords into chunks that fit Twitter's 512 character limit
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
                
                chunk_tweets = []
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Debug: Log a sample of the response structure
                    if isinstance(response_data, dict) and 'result' in response_data:
                        self.logger.info(f"Sample response keys: {list(response_data.keys())}")
                        if 'timeline' in response_data['result']:
                            self.logger.info("Found timeline in result")
                    
                    # Handle different possible response structures
                    tweets_data = []
                    if isinstance(response_data, dict):
                        # Check for common Twitter API response structures
                        if 'result' in response_data:
                            # Handle the twitter241 API structure
                            result = response_data['result']
                            if isinstance(result, dict) and 'timeline' in result:
                                timeline = result['timeline']
                                if 'instructions' in timeline:
                                    for instruction in timeline['instructions']:
                                        if 'entries' in instruction:
                                            for entry in instruction['entries']:
                                                if 'content' in entry and 'itemContent' in entry['content']:
                                                    item_content = entry['content']['itemContent']
                                                    if 'tweet_results' in item_content:
                                                        tweet_result = item_content['tweet_results'].get('result', {})
                                                        if 'legacy' in tweet_result:
                                                            tweets_data.append(tweet_result['legacy'])
                        elif 'data' in response_data:
                            tweets_data = response_data['data']
                        elif 'results' in response_data:
                            tweets_data = response_data['results']
                        elif 'tweets' in response_data:
                            tweets_data = response_data['tweets']
                        else:
                            # Log the actual structure for debugging
                            self.logger.warning(f"Unexpected response structure: {list(response_data.keys())}")
                            tweets_data = []
                    elif isinstance(response_data, list):
                        tweets_data = response_data
                    
                    for tweet in tweets_data:
                        try:
                            # Handle different tweet data structures
                            tweet_id = tweet.get('id_str', tweet.get('id', 'unknown'))
                            author_screen_name = tweet.get('user', {}).get('screen_name', '')
                            tweet_info = {
                                'id': tweet_id,
                                'text': tweet.get('full_text', tweet.get('text', '')),
                                'created_at': tweet.get('created_at', ''),
                                'author_id': tweet.get('user_id_str', tweet.get('user', {}).get('id_str', 'unknown')),
                                'author': author_screen_name,
                                'tweet_url': f"https://x.com/{author_screen_name}/status/{tweet_id}" if author_screen_name and tweet_id != 'unknown' else '',
                                'retweet_count': tweet.get('retweet_count', 0),
                                'like_count': tweet.get('favorite_count', tweet.get('like_count', 0)),
                                'reply_count': tweet.get('reply_count', 0),
                                'quote_count': tweet.get('quote_count', 0)
                            }
                            chunk_tweets.append(tweet_info)
                        except Exception as e:
                            self.logger.warning(f"Error parsing tweet: {str(e)}")
                            continue
                else:
                    self.logger.error(f"API request failed with status {response.status_code}: {response.text}")
                
                all_tweets.extend(chunk_tweets)
                self.logger.info(f"Retrieved {len(chunk_tweets)} tweets from chunk")
                
                # Rate limiting
                time.sleep(1)
            
            # Remove duplicates and limit to max_results
            seen_ids = set()
            unique_tweets = []
            for tweet in all_tweets:
                if tweet['id'] not in seen_ids:
                    seen_ids.add(tweet['id'])
                    unique_tweets.append(tweet)
                    if len(unique_tweets) >= max_results:
                        break
            
            self.logger.info(f"Retrieved {len(unique_tweets)} total unique tweets for keywords: {keywords[:5]}...")
            return unique_tweets
            
        except Exception as e:
            self.logger.error(f"Error searching tweets: {str(e)}")
            return []


    def analyze_engagement(self, tweets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze engagement metrics from tweets
        
        Args:
            tweets: List of tweet data
            
        Returns:
            Dictionary with engagement analysis
        """
        if not tweets:
            return {}
        
        total_tweets = len(tweets)
        total_likes = sum(tweet['like_count'] for tweet in tweets)
        total_retweets = sum(tweet['retweet_count'] for tweet in tweets)
        total_replies = sum(tweet['reply_count'] for tweet in tweets)
        
        # Sort by engagement
        sorted_tweets = sorted(tweets, 
                             key=lambda x: x['like_count'] + x['retweet_count'] + x['reply_count'], 
                             reverse=True)
        
        return {
            'total_tweets': total_tweets,
            'total_likes': total_likes,
            'total_retweets': total_retweets,
            'total_replies': total_replies,
            'avg_likes': total_likes / total_tweets if total_tweets > 0 else 0,
            'avg_retweets': total_retweets / total_tweets if total_tweets > 0 else 0,
            'avg_replies': total_replies / total_tweets if total_tweets > 0 else 0,
            'top_performing_tweets': sorted_tweets[:5]
        }

    def _split_keywords_for_search(self, keywords: List[str]) -> List[List[str]]:
        """
        Split keywords into chunks that fit Twitter's search query length limit
        
        Args:
            keywords: List of keywords to split
            
        Returns:
            List of keyword chunks
        """
        MAX_QUERY_LENGTH = 480  # Leave buffer for " -is:retweet lang:en"
        chunks = []
        current_chunk = []
        current_length = 0
        
        for keyword in keywords:
            # Calculate length this keyword would add: '"keyword" OR '
            keyword_length = len(f'"{keyword}" OR ')
            
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
    
    def _get_metric(self, tweet: Dict[str, Any], *metric_names: str) -> int:
        """
        Extract metric value from tweet data, handling different possible structures
        
        Args:
            tweet: Tweet data dictionary
            *metric_names: Possible metric field names to check
            
        Returns:
            Metric value as integer, 0 if not found
        """
        # Check public_metrics first (Twitter API v2 structure)
        if 'public_metrics' in tweet:
            for metric_name in metric_names:
                if metric_name in tweet['public_metrics']:
                    return tweet['public_metrics'][metric_name]
        
        # Check direct fields (Twitter API v1.1 structure)
        for metric_name in metric_names:
            if metric_name in tweet:
                return tweet[metric_name]
        
        # Default to 0 if not found
        return 0