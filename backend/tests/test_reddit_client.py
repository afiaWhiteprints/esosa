#!/usr/bin/env python3
"""
Reddit Client Test Script

This script tests the Reddit client functionality with a limited number of API requests.
It temporarily overrides the request limit to 10 for testing purposes.

Usage:
    python test_reddit_client.py

Requirements:
    - .env file with RAPIDAPI_KEY
    - Internet connection
    - Valid RapidAPI subscription for reddit34
"""

import sys
import os
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from reddit_client import RedditClient
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

def print_post_summary(posts: List[Dict[str, Any]], title: str):
    """Print a summary of Reddit post results"""
    print(f"\n{title}:")
    print(f"📊 Total posts: {len(posts)}")
    
    if posts:
        print(f"\n📝 Sample Reddit posts:")
        for i, post in enumerate(posts[:3], 1):
            title_text = post.get('title', 'No title')[:80] + '...' if len(post.get('title', '')) > 80 else post.get('title', 'No title')
            text = post.get('text', 'No text')[:60] + '...' if len(post.get('text', '')) > 60 else post.get('text', 'No text')
            score = post.get('score', 0)
            upvotes = post.get('upvote_count', 0)
            downvotes = post.get('downvote_count', 0)
            comments = post.get('num_comments', 0)
            subreddit = post.get('subreddit', 'unknown')
            author = post.get('author', 'unknown')
            
            print(f"  {i}. r/{subreddit} by u/{author}")
            print(f"     Score: {score:,} | ⬆️ {upvotes:,} | ⬇️ {downvotes:,} | 💬 {comments:,}")
            print(f"     Title: {title_text}")
            if text and text != 'No text':
                print(f"     Text: {text}")
        
        # Show engagement stats
        total_score = sum(t.get('score', 0) for t in posts)
        total_upvotes = sum(t.get('upvote_count', 0) for t in posts)
        total_downvotes = sum(t.get('downvote_count', 0) for t in posts)
        total_comments = sum(t.get('num_comments', 0) for t in posts)
        
        print(f"\n📈 Reddit Engagement Summary:")
        print(f"   Total Score: {total_score:,}")
        print(f"   Total Upvotes: {total_upvotes:,}")
        print(f"   Total Downvotes: {total_downvotes:,}")
        print(f"   Total Comments: {total_comments:,}")
        print(f"   Avg Score/Post: {total_score//len(posts) if posts else 0:,}")
        print(f"   Avg Comments/Post: {total_comments//len(posts) if posts else 0:,}")

def test_basic_search():
    """Test basic keyword search functionality"""
    print_separator("TEST 1: Basic Keyword Search")
    
    try:
        # Initialize client and set test limit
        client = RedditClient()
        # Temporarily override the session limit for testing
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        print(f"🧪 Testing with request limit: {client.max_requests_per_session}")
        
        # Test with a few Gen Z keywords
        test_keywords = ["Gen Z", "authentic", "real talk"]
        
        print(f"🔍 Searching for keywords: {test_keywords}")
        
        # Perform search
        start_time = time.time()
        posts = client.search_posts(
            keywords=test_keywords,
            max_results=50,
            days_back=7
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_post_summary(posts, "Search Results")
        
        return posts, client
        
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
        return [], None

def test_large_keyword_list():
    """Test search with large keyword list (chunk splitting)"""
    print_separator("TEST 2: Large Keyword List Search")
    
    try:
        # Initialize fresh client
        client = RedditClient()
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
        posts = client.search_posts(
            keywords=test_keywords,
            max_results=30,
            days_back=3
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_post_summary(posts, "Large Keyword Search Results")
        
        return posts, client
        
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
        return [], None

def test_engagement_analysis():
    """Test engagement analysis functionality"""
    print_separator("TEST 3: Engagement Analysis")
    
    try:
        client = RedditClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        # Search for content with good engagement potential
        test_keywords = ["viral", "trending", "breaking"]
        
        posts = client.search_posts(
            keywords=test_keywords,
            max_results=40,
            days_back=2
        )
        
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        if posts:
            engagement_stats = client.analyze_engagement(posts)
            
            print(f"\n📊 Reddit Engagement Analysis:")
            print(f"   Posts analyzed: {engagement_stats.get('total_posts', 0)}")
            print(f"   Total score: {engagement_stats.get('total_score', 0):,.0f}")
            print(f"   Total upvotes: {engagement_stats.get('total_upvotes', 0):,.0f}")
            print(f"   Total downvotes: {engagement_stats.get('total_downvotes', 0):,.0f}")
            print(f"   Total comments: {engagement_stats.get('total_comments', 0):,.0f}")
            print(f"   Average score: {engagement_stats.get('avg_score', 0):,.0f}")
            print(f"   Average upvotes: {engagement_stats.get('avg_upvotes', 0):,.0f}")
            print(f"   Average downvotes: {engagement_stats.get('avg_downvotes', 0):,.0f}")
            print(f"   Average comments: {engagement_stats.get('avg_comments', 0):,.0f}")
            print(f"   Average upvote ratio: {engagement_stats.get('avg_upvote_ratio', 0):,.2f}")
            
            # Show top performing posts
            top_posts = engagement_stats.get('top_performing_posts', [])[:3]
            if top_posts:
                print(f"\n🏆 Top Performing Reddit Posts:")
                for i, post in enumerate(top_posts, 1):
                    score = post.get('score', 0)
                    upvotes = post.get('upvote_count', 0)
                    downvotes = post.get('downvote_count', 0)
                    comments = post.get('num_comments', 0)
                    title = post.get('title', 'No title')[:60] + '...' if len(post.get('title', '')) > 60 else post.get('title', 'No title')
                    subreddit = post.get('subreddit', 'unknown')
                    print(f"  {i}. r/{subreddit} | Score: {score:,} | ⬆️ {upvotes:,} | ⬇️ {downvotes:,} | 💬 {comments:,}")
                    print(f"     {title}")
            
            return engagement_stats
        else:
            print("❌ No posts found for engagement analysis")
            return {}
            
    except Exception as e:
        print(f"❌ Test 3 failed: {str(e)}")
        return {}

def test_keyword_chunking():
    """Test keyword chunking functionality"""
    print_separator("TEST 4: Keyword Chunking Logic")
    
    try:
        client = RedditClient()
        
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
        client = RedditClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        print("🧪 Testing error handling scenarios")
        
        # Test with empty keywords
        print("\n1. Testing empty keywords list...")
        posts_empty = client.search_posts(keywords=[], max_results=10)
        print(f"   Empty keywords result: {len(posts_empty)} posts")
        
        # Test with very large max_results
        print("\n2. Testing large max_results...")
        posts_large = client.search_posts(
            keywords=["test"], 
            max_results=1000,  # Should be handled gracefully
            days_back=1
        )
        print(f"   Large max_results result: {len(posts_large)} posts")
        
        # Test engagement analysis with empty list
        print("\n3. Testing engagement analysis with empty posts...")
        empty_engagement = client.analyze_engagement([])
        print(f"   Empty engagement analysis: {len(empty_engagement)} metrics")
        
        return {
            'empty_keywords': len(posts_empty),
            'large_results': len(posts_large),
            'empty_engagement': len(empty_engagement)
        }
        
    except Exception as e:
        print(f"❌ Test 5 failed: {str(e)}")
        return {}

def save_test_results(results: Dict[str, Any]):
    """Save test results to JSON file"""
    try:
        output_file = "reddit_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        print(f"💾 Test results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")

def main():
    """Main test function"""
    print_separator("REDDIT CLIENT TEST SUITE")
    print("🧪 Testing Reddit client with 10 API request limit")
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
    posts_1, client_1 = test_basic_search()
    test_results['test_1_basic_search'] = {
        'posts_found': len(posts_1),
        'success': len(posts_1) > 0
    }
    
    # Test 2: Large Keyword List
    posts_2, client_2 = test_large_keyword_list()
    test_results['test_2_large_keywords'] = {
        'posts_found': len(posts_2),
        'success': len(posts_2) > 0
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
    print(f"📊 Total posts found: {test_results['test_1_basic_search']['posts_found'] + test_results['test_2_large_keywords']['posts_found']}")
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
        print("\n🎉 All tests passed! Reddit client is working correctly.")
    else:
        print(f"\n⚠️  {5 - successful_tests} test(s) failed. Check the error messages above.")
    
    print("\n💡 Next steps:")
    print("   • Review reddit_test_results.json for detailed results")
    print("   • Check your RapidAPI usage dashboard")
    print("   • Adjust rate limits if needed")
    print("   • Test with different keyword combinations")

if __name__ == "__main__":
    main()
