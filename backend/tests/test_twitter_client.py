#!/usr/bin/env python3
"""
Twitter Client Test Script

This script tests the Twitter client functionality with a limited number of API requests.
It temporarily overrides the request limit to 10 for testing purposes.

Usage:
    python test_twitter_client.py

Requirements:
    - .env file with RAPIDAPI_KEY
    - Internet connection
    - Valid RapidAPI subscription for twitter241
"""

import sys
import os
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from twitter_client import TwitterClient
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

def print_separator(title: str):
    """Print a formatted separator"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_tweet_summary(tweets: List[Dict[str, Any]], title: str):
    """Print a summary of tweet results"""
    print(f"\n{title}:")
    print(f"📊 Total tweets: {len(tweets)}")
    
    if tweets:
        print(f"\n🐦 Sample tweets:")
        for i, tweet in enumerate(tweets[:3], 1):
            text = tweet.get('text', 'No text')[:80] + '...' if len(tweet.get('text', '')) > 80 else tweet.get('text', 'No text')
            likes = tweet.get('like_count', 0)
            retweets = tweet.get('retweet_count', 0)
            replies = tweet.get('reply_count', 0)
            
            print(f"  {i}. {likes:,} ❤️  {retweets:,} 🔄  {replies:,} 💬")
            print(f"     Text: {text}")
        
        # Show engagement stats
        total_likes = sum(t.get('like_count', 0) for t in tweets)
        total_retweets = sum(t.get('retweet_count', 0) for t in tweets)
        total_replies = sum(t.get('reply_count', 0) for t in tweets)
        total_quotes = sum(t.get('quote_count', 0) for t in tweets)
        
        print(f"\n📈 Engagement Summary:")
        print(f"   Total Likes: {total_likes:,}")
        print(f"   Total Retweets: {total_retweets:,}")
        print(f"   Total Replies: {total_replies:,}")
        print(f"   Total Quotes: {total_quotes:,}")
        print(f"   Avg Likes/Tweet: {total_likes//len(tweets) if tweets else 0:,}")

def test_basic_search():
    """Test basic keyword search functionality"""
    print_separator("TEST 1: Basic Keyword Search")
    
    try:
        # Initialize client and set test limit
        client = TwitterClient()
        # Temporarily override the session limit for testing
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        print(f"🧪 Testing with request limit: {client.max_requests_per_session}")
        
        # Test with a few Gen Z keywords
        test_keywords = ["Gen Z", "authentic", "real talk"]
        
        print(f"🔍 Searching for keywords: {test_keywords}")
        
        # Perform search
        start_time = time.time()
        tweets = client.search_tweets(
            keywords=test_keywords,
            max_results=50,
            days_back=7
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_tweet_summary(tweets, "Search Results")
        
        return tweets, client
        
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
        return [], None

def test_large_keyword_list():
    """Test search with large keyword list (chunk splitting)"""
    print_separator("TEST 2: Large Keyword List Search")
    
    try:
        # Initialize fresh client
        client = TwitterClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        # Large set of keywords to test chunking
        test_keywords = [
            "Gen Z", "authentic", "real talk", "mental health", "self care",
            "therapy", "healing", "growth", "mindset", "wellness",
            "faith", "spirituality", "purpose", "vulnerability", "mindfulness",
            "meditation", "anxiety", "depression", "motivation", "inspiration"
        ]
        
        print(f"🎯 Testing with {len(test_keywords)} keywords (chunk splitting)")
        
        start_time = time.time()
        tweets = client.search_tweets(
            keywords=test_keywords,
            max_results=30,
            days_back=3
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_tweet_summary(tweets, "Large Keyword Search Results")
        
        return tweets, client
        
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
        return [], None

def test_engagement_analysis():
    """Test engagement analysis functionality"""
    print_separator("TEST 3: Engagement Analysis")
    
    try:
        client = TwitterClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        # Search for content with good engagement potential
        test_keywords = ["viral", "trending", "breaking"]
        
        tweets = client.search_tweets(
            keywords=test_keywords,
            max_results=40,
            days_back=2
        )
        
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        if tweets:
            engagement_stats = client.analyze_engagement(tweets)
            
            print(f"\n📊 Engagement Analysis:")
            print(f"   Tweets analyzed: {engagement_stats.get('total_tweets', 0)}")
            print(f"   Average likes: {engagement_stats.get('avg_likes', 0):,.0f}")
            print(f"   Average retweets: {engagement_stats.get('avg_retweets', 0):,.0f}")
            print(f"   Average replies: {engagement_stats.get('avg_replies', 0):,.0f}")
            
            # Show top performing tweets
            top_tweets = engagement_stats.get('top_performing_tweets', [])[:3]
            if top_tweets:
                print(f"\n🏆 Top Performing Tweets:")
                for i, tweet in enumerate(top_tweets, 1):
                    likes = tweet.get('like_count', 0)
                    retweets = tweet.get('retweet_count', 0)
                    text = tweet.get('text', 'No text')[:60] + '...' if len(tweet.get('text', '')) > 60 else tweet.get('text', 'No text')
                    print(f"  {i}. {likes:,} ❤️  {retweets:,} 🔄")
                    print(f"     {text}")
            
            return engagement_stats
        else:
            print("❌ No tweets found for engagement analysis")
            return {}
            
    except Exception as e:
        print(f"❌ Test 3 failed: {str(e)}")
        return {}

def test_keyword_chunking():
    """Test keyword chunking functionality"""
    print_separator("TEST 4: Keyword Chunking Logic")
    
    try:
        client = TwitterClient()
        
        # Test with very long keywords to force chunking
        long_keywords = [
            "artificial intelligence and machine learning",
            "sustainable development and environmental protection",
            "mental health awareness and psychological wellbeing",
            "social media influence and digital marketing strategies",
            "cryptocurrency blockchain technology and decentralized finance",
            "climate change mitigation and renewable energy solutions",
            "remote work productivity and digital collaboration tools",
            "personal development and self improvement techniques"
        ]
        
        print(f"🔧 Testing keyword chunking with {len(long_keywords)} long keywords")
        
        # Test the chunking method directly
        chunks = client._split_keywords_for_search(long_keywords)
        
        print(f"📦 Keywords split into {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            chunk_text = ", ".join(chunk)
            print(f"   Chunk {i}: {len(chunk)} keywords ({len(chunk_text)} chars)")
            print(f"   Keywords: {chunk_text[:100]}{'...' if len(chunk_text) > 100 else ''}")
        
        return chunks
        
    except Exception as e:
        print(f"❌ Test 4 failed: {str(e)}")
        return []

def test_error_handling():
    """Test error handling with invalid inputs"""
    print_separator("TEST 5: Error Handling")
    
    try:
        client = TwitterClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        print("🧪 Testing error handling scenarios")
        
        # Test with empty keywords
        print("\n1. Testing empty keywords list...")
        tweets_empty = client.search_tweets(keywords=[], max_results=10)
        print(f"   Empty keywords result: {len(tweets_empty)} tweets")
        
        # Test with very large max_results
        print("\n2. Testing large max_results...")
        tweets_large = client.search_tweets(
            keywords=["test"], 
            max_results=1000,  # Should be handled gracefully
            days_back=1
        )
        print(f"   Large max_results result: {len(tweets_large)} tweets")
        
        # Test engagement analysis with empty list
        print("\n3. Testing engagement analysis with empty tweets...")
        empty_engagement = client.analyze_engagement([])
        print(f"   Empty engagement analysis: {len(empty_engagement)} metrics")
        
        return {
            'empty_keywords': len(tweets_empty),
            'large_results': len(tweets_large),
            'empty_engagement': len(empty_engagement)
        }
        
    except Exception as e:
        print(f"❌ Test 5 failed: {str(e)}")
        return {}

def save_test_results(results: Dict[str, Any]):
    """Save test results to JSON file"""
    try:
        output_file = "twitter_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        print(f"💾 Test results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")

def main():
    """Main test function"""
    print_separator("TWITTER CLIENT TEST SUITE")
    print("🧪 Testing Twitter client with 10 API request limit")
    print("⚠️  Make sure you have RAPIDAPI_KEY in your .env file")
    
    # Check for API key
    if not os.getenv('RAPIDAPI_KEY'):
        print("❌ RAPIDAPI_KEY not found in environment variables!")
        print("💡 Please add your RapidAPI key to the .env file")
        return
    
    test_results = {
        'test_timestamp': time.time(),
        'test_config': {
            'max_requests_per_session': 10,
            'keywords_tested': []
        },
        'test_1_basic_search': {},
        'test_2_large_keywords': {},
        'test_3_engagement_analysis': {},
        'test_4_keyword_chunking': {},
        'test_5_error_handling': {},
        'summary': {}
    }
    
    total_start_time = time.time()
    
    # Run tests
    print("🚀 Starting test sequence...")
    
    # Test 1: Basic Search
    tweets_1, client_1 = test_basic_search()
    test_results['test_1_basic_search'] = {
        'tweets_found': len(tweets_1),
        'success': len(tweets_1) > 0
    }
    
    # Test 2: Large Keyword List
    tweets_2, client_2 = test_large_keyword_list()
    test_results['test_2_large_keywords'] = {
        'tweets_found': len(tweets_2),
        'success': len(tweets_2) > 0
    }
    
    # Test 3: Engagement Analysis
    engagement = test_engagement_analysis()
    test_results['test_3_engagement_analysis'] = {
        'analysis_completed': len(engagement) > 0,
        'success': len(engagement) > 0
    }
    
    # Test 4: Keyword Chunking
    chunks = test_keyword_chunking()
    test_results['test_4_keyword_chunking'] = {
        'chunks_created': len(chunks),
        'success': len(chunks) > 0
    }
    
    # Test 5: Error Handling
    error_tests = test_error_handling()
    test_results['test_5_error_handling'] = {
        'tests_completed': len(error_tests),
        'success': len(error_tests) > 0
    }
    
    total_end_time = time.time()
    
    # Summary
    print_separator("TEST SUMMARY")
    successful_tests = sum(1 for test in ['test_1_basic_search', 'test_2_large_keywords', 'test_3_engagement_analysis', 'test_4_keyword_chunking', 'test_5_error_handling'] if test_results[test]['success'])
    
    print(f"✅ Tests passed: {successful_tests}/5")
    print(f"⏱️  Total test time: {total_end_time - total_start_time:.2f} seconds")
    print(f"📊 Total tweets found: {test_results['test_1_basic_search']['tweets_found'] + test_results['test_2_large_keywords']['tweets_found']}")
    print(f"📦 Keyword chunks created: {test_results['test_4_keyword_chunking']['chunks_created']}")
    
    # Add summary to results
    test_results['summary'] = {
        'tests_passed': f"{successful_tests}/5",
        'total_time_seconds': total_end_time - total_start_time,
        'all_tests_successful': successful_tests == 5
    }
    
    # Save results
    save_test_results(test_results)
    
    if successful_tests == 5:
        print("\n🎉 All tests passed! Twitter client is working correctly.")
    else:
        print(f"\n⚠️  {5 - successful_tests} test(s) failed. Check the error messages above.")
    
    print("\n💡 Next steps:")
    print("   • Review twitter_test_results.json for detailed results")
    print("   • Check your RapidAPI usage dashboard")
    print("   • Adjust rate limits if needed")
    print("   • Test with different keyword combinations")

if __name__ == "__main__":
    main()
