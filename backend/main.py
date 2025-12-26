#!/usr/bin/env python3
"""
Personal Podcast Assistant - Config-Based Version

A comprehensive tool that analyzes social media platforms to:
1. Research trending topics and keywords
2. Analyze audience engagement patterns
3. Generate podcast episode ideas and talking points
4. Create detailed episode outlines and scripts
5. Generate interview questions and prep materials

Supports multiple platforms: Twitter/X, Reddit, TikTok, and Threads.

This version uses a config.yaml file instead of command line arguments.
Edit config.yaml to customize your settings, then run:
    python main.py

For help setting up the config file, run:
    python main.py --create-sample-config
"""

import sys
import os
from typing import Dict, Any
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.podcast_assistant import PodcastAssistant
from src.config_manager import ConfigManager
from dotenv import load_dotenv
load_dotenv()

def print_summary(data: Dict[str, Any], data_type: str) -> None:
    """Print a summary of the results"""
    print(f"\n{'='*60}")
    print(f"PODCAST ASSISTANT - {data_type.upper()} RESULTS")
    print(f"{'='*60}")
    
    # Handle case where data might be a string (error condition)
    if isinstance(data, str):
        print(f"❌ Error: {data}")
        return
    
    if not isinstance(data, dict):
        print(f"❌ Invalid data format: {type(data)}")
        return
    
    if data_type == "research":
        # Calculate total posts across all platforms
        total_posts = (
            data.get('posts_analyzed', 0) or
            data.get('tweets_analyzed', 0) +
            data.get('reddit_posts_analyzed', 0) +
            data.get('tiktok_posts_analyzed', 0) +
            data.get('threads_posts_analyzed', 0)
        )
        print(f"📊 Analyzed {total_posts} social media posts")
        print(f"🔍 Found {len(data.get('trending_topics', []))} trending topics")
        print(f"🎯 Generated {len(data.get('ai_topic_suggestions', {}).get('topics', []))} AI topic suggestions")
        print(f"📅 Created {len(data.get('content_calendar', []))} content calendar items")
        
        # Show top trending topics
        if data.get('trending_topics'):
            print("\n🔥 TOP TRENDING TOPICS:")
            for i, topic in enumerate(data['trending_topics'][:5], 1):
                post_count = topic.get('post_count', topic.get('tweet_count', 0))
                print(f"  {i}. {topic['topic']} ({post_count} posts, {topic.get('total_engagement', 0)} engagement)")
        
        # Show AI suggestions
        if data.get('ai_topic_suggestions', {}).get('topics'):
            print("\n🤖 AI TOPIC SUGGESTIONS:")
            for i, topic in enumerate(data['ai_topic_suggestions']['topics'][:5], 1):
                print(f"  {i}. {topic.get('title', 'No title')} (Score: {topic.get('relevance_score', 'N/A')}/10)")
                if topic.get('unique_angle'):
                    print(f"     Angle: {topic['unique_angle'][:80]}...")
    
    elif data_type == "episode":
        print(f"📝 Topic: {data.get('topic', 'N/A')}")
        print(f"⏱️  Duration: {data.get('duration_minutes', 'N/A')} minutes")
        print(f"🎙️ Style: {data.get('host_style', 'N/A')}")
        print(f"👥 Audience: {data.get('target_audience', 'N/A')}")
        
        if data.get('talking_points'):
            print(f"\n💬 TALKING POINTS ({len(data['talking_points'])}):")
            for i, point in enumerate(data['talking_points'][:7], 1):
                print(f"  {i}. {point}")
        
        if data.get('outline', {}).get('segments'):
            print(f"\n📋 EPISODE SEGMENTS ({len(data['outline']['segments'])}):")
            for i, segment in enumerate(data['outline']['segments'], 1):
                print(f"  {i}. {segment.get('name', 'Unnamed')} ({segment.get('duration_minutes', '?')} min)")
    
    elif data_type == "interview":
        guest_name = data.get('guest_info', {}).get('name', 'Unknown')
        print(f"👤 Guest: {guest_name}")
        print(f"📝 Topic: {data.get('interview_topic', 'N/A')}")
        print(f"⏱️  Duration: {data.get('interview_length', 'N/A')} minutes")
        print(f"❓ Questions generated: {len(data.get('questions', []))}")
        
        if data.get('questions'):
            print("\n❓ SAMPLE QUESTIONS:")
            categories = {}
            for q in data['questions']:
                if 'error' not in q:
                    cat = q.get('category', 'General')
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append(q.get('question', 'No question'))
            
            for category, questions in list(categories.items())[:3]:
                print(f"\n  📋 {category}:")
                for i, question in enumerate(questions[:2], 1):
                    print(f"    {i}. {question[:100]}...")
    
    elif data_type == "competition":
        content_analyzed = data.get('content_analyzed', data.get('tweets_analyzed', 0))
        print(f"📊 Content analyzed: {content_analyzed} social media posts")
        print(f"🔍 Trending topics found: {len(data.get('trending_topics', []))}")
        print(f"🔑 Keywords extracted: {len(data.get('popular_keywords', []))}")
        
        if data.get('recommendations'):
            print("\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(data['recommendations'][:4], 1):
                print(f"  {i}. {rec}")

def print_file_outputs(data: Dict[str, Any]) -> None:
    """Print information about generated files"""
    files_generated = []
    
    if data.get('json_report'):
        files_generated.append(f"📄 JSON Report: {data['json_report']}")
    
    if data.get('pdf_report'):
        files_generated.append(f"📋 PDF Report: {data['pdf_report']}")
    
    if data.get('pdf_error'):
        files_generated.append(f"⚠️  PDF Error: {data['pdf_error']}")
    
    if files_generated:
        print(f"\n{'='*40}")
        print("📁 GENERATED FILES:")
        for file_info in files_generated:
            print(f"  {file_info}")
        print(f"{'='*40}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Podcast Assistant (Config-based)')
    parser.add_argument('--create-sample-config', action='store_true',
                       help='Create a sample config.yaml file')
    parser.add_argument('--show-config', action='store_true',
                       help='Show current configuration')
    parser.add_argument('--config-file', default='src/files/config.yaml',
                       help='Path to config file (default: src/files/config.yaml)')
    parser.add_argument('--chat', action='store_true',
                       help='Start an interactive chat session with the assistant')
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.create_sample_config:
        try:
            config_manager = ConfigManager('non-existent-file')  # Will fail gracefully
        except:
            pass
        
        # Create sample config using the ConfigManager
        try:
            dummy_config = ConfigManager.__new__(ConfigManager)  # Create instance without init
            dummy_config.create_sample_config('config_sample.yaml')
            print("✅ Sample configuration created: config_sample.yaml")
            print("📝 Copy this to config.yaml and customize it for your needs")
            return
        except Exception as e:
            print(f"❌ Error creating sample config: {str(e)}")
            return
    
    # Load configuration
    try:
        config_manager = ConfigManager(args.config_file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {args.config_file}")
        print("💡 Run with --create-sample-config to create a sample configuration file")
        return
    except Exception as e:
        print(f"❌ Error loading configuration: {str(e)}")
        return
    
    # Show config if requested
    if args.show_config:
        config_manager.print_current_config()
        return
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        print("❌ Configuration Issues:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Please fix these issues in your config.yaml file")
        return
    
    # Check for environment file
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your API keys. See .env.example for template.")
        return
    
    try:
        # Initialize assistant
        print("🚀 Initializing Podcast Assistant...")
        assistant = PodcastAssistant()
        
        # Get configuration
        general_config = config_manager.get_general_config()
        output_config = config_manager.get_output_config()
        
        # Override mode if --chat flag is present
        if args.chat:
            mode = 'chat'
        else:
            mode = general_config['mode']
        
        print(f"📋 Mode: {mode.title()}")
        print(f"📁 Output Directory: {output_config['directory']}")
        
        # Execute based on mode
        if mode == 'research':
            config = config_manager.get_research_config()
            
            if config['keyword_selection'] == 'random':
                print(f"🔍 Researching topics with randomly selected keywords:")
                print(f"🎲 Selected: {', '.join(config['keywords'])}")
                print(f"📚 (From {len(config['all_keywords'])} total available)")
            else:
                print(f"🔍 Researching topics for all keywords: {', '.join(config['keywords'])}")
            
            print(f"📊 Analyzing up to {config['max_tweets']} social media posts...")
            
            results = assistant.research_topics(
                keywords=config['keywords'],
                podcast_niche=config['niche'],
                podcast_description=config['description'],
                max_tweets=config['max_tweets'],
                days_back=config['days_back'],
                generate_pdf=config['generate_pdf']
            )
            
            if 'error' in results:
                print(f"❌ Error: {results['error']}")
                return
            
            if general_config['verbosity'] in ['summary', 'full']:
                print_summary(results, 'research')
            
            print_file_outputs(results)
        
        elif mode == 'episode':
            config = config_manager.get_episode_config()
            print(f"📝 Generating episode content for: {config['topic']}")
            print(f"⏱️  Target duration: {config['duration_minutes']} minutes")
            
            results = assistant.generate_episode_content(
                topic=config['topic'],
                talking_points=config['talking_points'] if config['talking_points'] else None,
                duration_minutes=config['duration_minutes'],
                host_style=config['host_style'],
                target_audience=config['target_audience'],
                generate_pdf=config['generate_pdf']
            )
            
            if 'error' in results:
                print(f"❌ Error: {results['error']}")
                return
            
            if general_config['verbosity'] in ['summary', 'full']:
                print_summary(results, 'episode')
            
            print_file_outputs(results)
        
        elif mode == 'interview':
            config = config_manager.get_interview_config()
            guest_name = config['guest_info']['name']
            print(f"🎤 Preparing interview with {guest_name}")
            print(f"📝 Topic: {config['topic']}")
            
            results = assistant.create_interview_prep(
                guest_info=config['guest_info'],
                interview_topic=config['topic'],
                interview_length=config['duration_minutes'],
                generate_pdf=config['generate_pdf']
            )
            
            if 'error' in results:
                print(f"❌ Error: {results['error']}")
                return
            
            if general_config['verbosity'] in ['summary', 'full']:
                print_summary(results, 'interview')
            
            print_file_outputs(results)
        
        elif mode == 'competition':
            config = config_manager.get_competition_config()
            print(f"🔍 Analyzing competition for: {', '.join(config['keywords'])}")
            
            results = assistant.analyze_competition(config['keywords'])
            
            if 'error' in results:
                print(f"❌ Error: {results['error']}")
                return
            
            if general_config['verbosity'] in ['summary', 'full']:
                print_summary(results, 'competition')
            
            # Note: PDF generation for competition analysis not implemented yet
            if results.get('json_report'):
                print(f"\n📄 Results saved to: {results['json_report']}")
        
        elif mode == 'research_to_episode':
            research_config = config_manager.get_research_config()
            episode_config = config_manager.get_episode_config()
            
            print(f"🔍 Starting Research-to-Episode workflow...")
            
            if research_config['keyword_selection'] == 'random':
                print(f"🎲 Randomly selected keywords: {', '.join(research_config['keywords'])}")
                print(f"📚 (From {len(research_config['all_keywords'])} total available)")
            else:
                print(f"📊 Using all keywords: {', '.join(research_config['keywords'])}")
            
            print(f"🎙️ Style: {episode_config['host_style']} for {episode_config['target_audience']}")
            
            results = assistant.create_research_to_episode_workflow(
                keywords=research_config['keywords'],
                podcast_niche=research_config['niche'],
                podcast_description=research_config['description'],
                max_tweets=research_config['max_tweets'],
                duration_minutes=episode_config['duration_minutes'],
                host_style=episode_config['host_style'],
                target_audience=episode_config['target_audience'],
                days_back=research_config['days_back'],
                tiktok_days_back=research_config['tiktok_days_back'],
                threads_days_back=research_config['threads_days_back'],
                reddit_days_back=research_config['reddit_days_back'],
                include_tiktok=research_config['tiktok_enabled'],
                include_threads=research_config['threads_enabled'],
                include_reddit=research_config['reddit_enabled'],
                tiktok_max_videos=research_config['tiktok_max_videos'],
                threads_max_posts=research_config['threads_max_posts'],
                reddit_max_posts=research_config['reddit_max_posts'],
                tiktok_regions=research_config['tiktok_regions'],
                use_random_tiktok_keywords=research_config['tiktok_use_random_keywords'],
                random_tiktok_keyword_count=research_config['tiktok_random_keyword_count'],
                use_random_threads_keywords=research_config['threads_use_random_keywords'],
                random_threads_keyword_count=research_config['threads_random_keyword_count'],
                use_random_reddit_keywords=research_config['reddit_use_random_keywords'],
                random_reddit_keyword_count=research_config['reddit_random_keyword_count'],
                generate_pdf=research_config['generate_pdf']
            )
            
            if 'error' in results:
                print(f"❌ Error: {results['error']}")
                return
            
            # Show results from both phases
            print(f"\n🎯 AI-SELECTED EPISODE TOPIC: {results.get('selected_topic', 'Unknown')}")
            
            if general_config['verbosity'] in ['summary', 'full']:
                print_summary(results['research_results'], 'research')
                print_summary(results['episode_results'], 'episode')
            
            print_file_outputs(results['research_results'])
            print_file_outputs(results['episode_results'])
        
        elif mode == 'chat':
            print("\n" + "="*60)
            print("💬 PODCAST ASSISTANT CHAT")
            print("="*60)
            print("Type 'exit' or 'quit' to end the conversation.")
            print("Ask me anything about your podcast, research, or content ideas.")
            print("="*60)
            
            while True:
                try:
                    user_input = input("\n👤 You: ")
                    if user_input.lower() in ['exit', 'quit', 'bye', 'stop']:
                        print("\n🤖 Assistant: Goodbye! Good luck with your podcast! 👋")
                        break
                    
                    if not user_input.strip():
                        continue
                    
                    print("\n🤖 Assistant Thinking...", end="\r")
                    response = assistant.chat(user_input)
                    # Clear "Thinking..." line if possible, otherwise just print
                    print(" " * 30, end="\r")
                    print(f"🤖 Assistant: {response}")
                    
                except KeyboardInterrupt:
                    print("\n\n🤖 Assistant: Chat ended. Goodbye! 👋")
                    break
                except Exception as e:
                    print(f"\n❌ Error during chat: {str(e)}")
                    break
            
            # Special case for chat mode: don't show the generic success message below
            return
        
        print(f"\n✅ {mode.replace('_', '-to-').title()} operation completed successfully!")
        
        # Show next steps
        print(f"\n💡 Next Steps:")
        print(f"   • Review the generated files in the '{output_config['directory']}' directory")
        print(f"   • Modify config.yaml to run different operations")
        print(f"   • Use --show-config to view current settings")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Please check:")
        print("   • Your .env file contains valid API keys")
        print("   • You have internet connection")
        print("   • Your API keys have proper permissions")
        print("   • Your config.yaml file is properly formatted")

if __name__ == '__main__':
    main()