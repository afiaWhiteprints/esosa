#!/usr/bin/env python3
"""
TikTok Client Test Script

This script tests the TikTok client functionality with a limited number of API requests.
It temporarily overrides the request limit to 10 for testing purposes.

Usage:
    python test_tiktok_client.py

Requirements:
    - .env file with RAPIDAPI_KEY
    - Internet connection
    - Valid RapidAPI subscription for tiktok-scraper7
"""

import sys
import os
from typing import List, Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tiktok_client import TikTokClient
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

def print_video_summary(videos: List[Dict[str, Any]], title: str):
    """Print a summary of video results"""
    print(f"\n{title}:")
    print(f"📊 Total videos: {len(videos)}")
    
    if videos:
        print(f"\n🎬 Sample videos:")
        for i, video in enumerate(videos[:3], 1):
            caption = video.get('caption', 'No caption')[:60] + '...' if len(video.get('caption', '')) > 60 else video.get('caption', 'No caption')
            likes = video.get('like_count', 0)
            author = video.get('author', 'Unknown')
            region = video.get('region', 'Unknown')
            
            print(f"  {i}. @{author} ({region.upper()}) - {likes:,} likes")
            print(f"     Caption: {caption}")
        
        # Show engagement stats
        total_likes = sum(v.get('like_count', 0) for v in videos)
        total_shares = sum(v.get('share_count', 0) for v in videos)
        total_comments = sum(v.get('comment_count', 0) for v in videos)
        
        print(f"\n📈 Engagement Summary:")
        print(f"   Total Likes: {total_likes:,}")
        print(f"   Total Shares: {total_shares:,}")
        print(f"   Total Comments: {total_comments:,}")
        print(f"   Avg Likes/Video: {total_likes//len(videos) if videos else 0:,}")

def test_basic_search():
    """Test basic keyword search functionality"""
    print_separator("TEST 1: Basic Keyword Search")
    
    try:
        # Initialize client and set test limit
        client = TikTokClient()
        # Temporarily override the session limit for testing
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        print(f"🧪 Testing with request limit: {client.max_requests_per_session}")
        
        # Test with a few Gen Z keywords
        test_keywords = ["Gen Z", "authentic", "real talk"]
        regions = ["us", "ng"]
        
        print(f"🔍 Searching for keywords: {test_keywords}")
        print(f"🌍 Regions: {regions}")
        
        # Perform search
        start_time = time.time()
        videos = client.search_videos_by_keywords(
            keywords=test_keywords,
            count=20,  # Per keyword per region
            regions=regions,
            use_random_keywords=False,
            random_keyword_count=5
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_video_summary(videos, "Search Results")
        
        return videos, client
        
    except Exception as e:
        print(f"❌ Test 1 failed: {str(e)}")
        return [], None

def test_random_keywords():
    """Test random keyword selection"""
    print_separator("TEST 2: Random Keyword Selection")
    
    try:
        # Initialize fresh client
        client = TikTokClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        # Larger set of keywords to test randomization
        test_keywords = [
            "Gen Z", "authentic", "real talk", "mental health", "self care",
            "therapy", "healing", "growth", "mindset", "wellness",
            "faith", "spirituality", "purpose", "vulnerability"
        ]
        
        print(f"🎲 Testing random selection from {len(test_keywords)} keywords")
        
        start_time = time.time()
        videos = client.search_videos_by_keywords(
            keywords=test_keywords,
            count=15,
            regions=["us"],  # Single region to conserve requests
            use_random_keywords=True,
            random_keyword_count=3  # Only select 3 random keywords
        )
        end_time = time.time()
        
        print(f"⏱️  Search completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print_video_summary(videos, "Random Keyword Results")
        
        return videos, client
        
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
        return [], None

def test_hashtag_trends(client: TikTokClient = None):
    """Test hashtag trend analysis"""
    print_separator("TEST 3: Hashtag Trends Analysis")
    
    try:
        if not client:
            client = TikTokClient()
            client.max_requests_per_session = 10
            client.reset_session_counter()
        else:
            # Continue with existing session
            print(f"🔄 Continuing with existing session ({client.session_request_count}/{client.max_requests_per_session} requests used)")
        
        # Test hashtag trends for a couple keywords
        keywords = ["authentic", "healing"]
        
        print(f"#️⃣ Analyzing hashtag trends for: {keywords}")
        
        start_time = time.time()
        hashtag_trends = client.get_hashtag_trends(keywords)
        end_time = time.time()
        
        print(f"⏱️  Analysis completed in {end_time - start_time:.2f} seconds")
        print(f"🔢 Total API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        print(f"\n#️⃣ Top Trending Hashtags ({len(hashtag_trends)}):")
        for i, hashtag in enumerate(hashtag_trends[:8], 1):
            name = hashtag.get('hashtag', 'Unknown')
            count = hashtag.get('count', 0)
            engagement = hashtag.get('total_engagement', 0)
            print(f"  {i}. #{name} - Used {count} times, {engagement:,} total engagement")
        
        return hashtag_trends
        
    except Exception as e:
        print(f"❌ Test 3 failed: {str(e)}")
        return []

def test_engagement_analysis():
    """Test engagement analysis functionality"""
    print_separator("TEST 4: Engagement Analysis")
    
    try:
        client = TikTokClient()
        client.max_requests_per_session = 10
        client.reset_session_counter()
        
        # Search for content with good engagement potential
        test_keywords = ["viral", "trending"]
        
        videos = client.search_videos_by_keywords(
            keywords=test_keywords,
            count=25,
            regions=["us"],
            use_random_keywords=False,
            random_keyword_count=5
        )
        
        print(f"🔢 API Requests used: {client.session_request_count}/{client.max_requests_per_session}")
        
        if videos:
            engagement_stats = client.analyze_engagement(videos)
            
            print(f"\n📊 Engagement Analysis:")
            print(f"   Videos analyzed: {engagement_stats.get('total_videos', 0)}")
            print(f"   Average likes: {engagement_stats.get('avg_likes', 0):,.0f}")
            print(f"   Average comments: {engagement_stats.get('avg_comments', 0):,.0f}")
            print(f"   Average shares: {engagement_stats.get('avg_shares', 0):,.0f}")
            print(f"   Engagement rate: {engagement_stats.get('engagement_rate', 0):.4f}")
            
            # Show top performing videos
            top_videos = engagement_stats.get('top_performing_videos', [])[:3]
            if top_videos:
                print(f"\n🏆 Top Performing Videos:")
                for i, video in enumerate(top_videos, 1):
                    likes = video.get('like_count', 0)
                    caption = video.get('caption', 'No caption')[:50] + '...' if len(video.get('caption', '')) > 50 else video.get('caption', 'No caption')
                    author = video.get('author', 'Unknown')
                    print(f"  {i}. @{author} - {likes:,} likes")
                    print(f"     {caption}")
            
            return engagement_stats
        else:
            print("❌ No videos found for engagement analysis")
            return {}
            
    except Exception as e:
        print(f"❌ Test 4 failed: {str(e)}")
        return {}

def save_test_results(results: Dict[str, Any]):
    """Save test results to JSON file"""
    try:
        output_file = "tiktok_test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        print(f"💾 Test results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {str(e)}")

def main():
    """Main test function"""
    print_separator("TIKTOK CLIENT TEST SUITE")
    print("🧪 Testing TikTok client with 10 API request limit")
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
            'regions_tested': ['us', 'ng'],
            'keywords_tested': []
        },
        'test_1_basic_search': {},
        'test_2_random_keywords': {},
        'test_3_hashtag_trends': {},
        'test_4_engagement_analysis': {},
        'summary': {}
    }
    
    total_start_time = time.time()
    
    # Run tests
    print("🚀 Starting test sequence...")
    
    # Test 1: Basic Search
    videos_1, client_1 = test_basic_search()
    test_results['test_1_basic_search'] = {
        'videos_found': len(videos_1),
        'success': len(videos_1) > 0
    }
    
    # Test 2: Random Keywords
    videos_2, client_2 = test_random_keywords()
    test_results['test_2_random_keywords'] = {
        'videos_found': len(videos_2),
        'success': len(videos_2) > 0
    }
    
    # Test 3: Hashtag Trends (reuse client to test session limits)
    hashtags = test_hashtag_trends(client_2)
    test_results['test_3_hashtag_trends'] = {
        'hashtags_found': len(hashtags),
        'success': len(hashtags) > 0
    }
    
    # Test 4: Engagement Analysis
    engagement = test_engagement_analysis()
    test_results['test_4_engagement_analysis'] = {
        'analysis_completed': len(engagement) > 0,
        'success': len(engagement) > 0
    }
    
    total_end_time = time.time()
    
    # Summary
    print_separator("TEST SUMMARY")
    successful_tests = sum(1 for test in ['test_1_basic_search', 'test_2_random_keywords', 'test_3_hashtag_trends', 'test_4_engagement_analysis'] if test_results[test]['success'])
    
    print(f"✅ Tests passed: {successful_tests}/4")
    print(f"⏱️  Total test time: {total_end_time - total_start_time:.2f} seconds")
    print(f"📊 Total videos found: {test_results['test_1_basic_search']['videos_found'] + test_results['test_2_random_keywords']['videos_found']}")
    print(f"#️⃣ Total hashtags analyzed: {test_results['test_3_hashtag_trends']['hashtags_found']}")
    
    # Add summary to results
    test_results['summary'] = {
        'tests_passed': f"{successful_tests}/4",
        'total_time_seconds': total_end_time - total_start_time,
        'all_tests_successful': successful_tests == 4
    }
    
    # Save results
    save_test_results(test_results)
    
    if successful_tests == 4:
        print("\n🎉 All tests passed! TikTok client is working correctly.")
    else:
        print(f"\n⚠️  {4 - successful_tests} test(s) failed. Check the error messages above.")
    
    print("\n💡 Next steps:")
    print("   • Review tiktok_test_results.json for detailed results")
    print("   • Check your RapidAPI usage dashboard")
    print("   • Adjust rate limits if needed")

if __name__ == "__main__":
    main()