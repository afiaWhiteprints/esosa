import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Import established modules
from src.podcast_assistant import PodcastAssistant
from src.config_manager import ConfigManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Podcast Assistant API", description="API for Esosa's Podcast Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from output directory
output_dir = os.path.join(os.path.dirname(__file__), "output")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
app.mount("/output", StaticFiles(directory=output_dir), name="output")

# Initialize Assistant
try:
    assistant = PodcastAssistant()
    logger.info("Podcast Assistant initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Podcast Assistant: {str(e)}")
    assistant = None

# --- Pydantic Models for Request Bodies ---

class ChatRequest(BaseModel):
    message: str

class ResearchRequest(BaseModel):
    keywords: List[str]
    niche: Optional[str] = ""
    description: Optional[str] = ""
    days_back: Optional[int] = 7

class EpisodeRequest(BaseModel):
    topic: str
    duration_minutes: Optional[int] = 30
    host_style: Optional[str] = "conversational"
    target_audience: Optional[str] = "general"
    talking_points: Optional[List[str]] = None

class InterviewRequest(BaseModel):
    guest_name: str
    guest_background: Optional[str] = ""
    guest_expertise: Optional[str] = ""
    topic: str
    duration_minutes: Optional[int] = 30

class ConfigUpdateRequest(BaseModel):
    research: Optional[Dict[str, Any]] = None
    episode: Optional[Dict[str, Any]] = None
    general: Optional[Dict[str, Any]] = None

# --- API Endpoints ---

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "assistant_ready": assistant is not None}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not assistant:
        return {"response": "I'm having trouble starting up. Please try again in a moment.", "error": True}

    try:
        response = assistant.chat(request.message)
        return {"response": response}
    except Exception as e:
        error_str = str(e).lower()
        logger.error(f"Chat error: {str(e)}")

        # Return user-friendly messages for common errors
        if "rate limit" in error_str or "quota" in error_str or "429" in error_str:
            return {"response": "I'm a bit overwhelmed right now! Too many requests. Please wait a minute and try again.", "error": True}
        elif "api key" in error_str or "authentication" in error_str or "401" in error_str:
            return {"response": "There's an issue with my configuration. Please contact support.", "error": True}
        elif "timeout" in error_str or "timed out" in error_str:
            return {"response": "That took too long to process. Could you try asking in a simpler way?", "error": True}
        elif "connection" in error_str or "network" in error_str:
            return {"response": "I'm having trouble connecting to my brain. Please check your internet and try again.", "error": True}
        else:
            return {"response": "Oops! Something went wrong on my end. Please try again in a moment.", "error": True}

@app.post("/api/research")
async def research_topics(request: ResearchRequest):
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    try:
        # Load config defaults
        config = ConfigManager(config_file="src/files/config.yaml")
        research_config = config.get_research_config()

        # Use request values or fall back to config
        keywords = request.keywords if request.keywords else research_config['keywords']
        niche = request.niche if request.niche else research_config['niche']
        description = request.description if request.description else research_config['description']
        days_back = request.days_back if request.days_back else research_config['days_back']

        logger.info(f"Starting research with {len(keywords)} keywords")

        results = assistant.research_topics_multi_platform(
            keywords=keywords,
            podcast_niche=niche,
            podcast_description=description,
            days_back=days_back,
            include_tiktok=research_config['tiktok_enabled'],
            include_threads=research_config['threads_enabled'],
            include_reddit=research_config['reddit_enabled'],
            max_tweets=research_config['twitter_max_tweets'],
            max_tiktoks=research_config['tiktok_max_videos'],
            max_threads=research_config['threads_max_posts'],
            max_reddit_posts=research_config['reddit_max_posts']
        )
        
        if 'error' in results:
             raise HTTPException(status_code=500, detail=results['error'])
             
        return results
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/episode")
async def generate_episode(request: EpisodeRequest):
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    try:
        # Load config defaults
        config = ConfigManager(config_file="src/files/config.yaml")
        episode_config = config.get_episode_config()

        # Use request values or fall back to config
        topic = request.topic if request.topic else episode_config['topic']
        talking_points = request.talking_points if request.talking_points else episode_config['talking_points']
        duration = request.duration_minutes if request.duration_minutes else episode_config['duration_minutes']
        style = request.host_style if request.host_style else episode_config['host_style']
        audience = request.target_audience if request.target_audience else episode_config['target_audience']

        logger.info(f"Generating episode for topic: {topic or 'Auto-generated'}")

        results = assistant.generate_episode_content(
            topic=topic if topic else None,  # None triggers auto-generation
            talking_points=talking_points if talking_points else None,
            duration_minutes=duration,
            host_style=style,
            target_audience=audience
        )
        
        if 'error' in results:
             raise HTTPException(status_code=500, detail=results['error'])
             
        return results
    except Exception as e:
        logger.error(f"Episode generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview")
async def prepare_interview(request: InterviewRequest):
    if not assistant:
        raise HTTPException(status_code=503, detail="Assistant not initialized")

    try:
        guest_info = {
            "name": request.guest_name,
            "background": request.guest_background,
            "expertise": request.guest_expertise
        }

        results = assistant.create_interview_prep(
            guest_info=guest_info,
            interview_topic=request.topic,
            interview_length=request.duration_minutes
        )

        if 'error' in results:
             raise HTTPException(status_code=500, detail=results['error'])

        return results
    except Exception as e:
        logger.error(f"Interview prep error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config():
    try:
        config = ConfigManager(config_file="src/files/config.yaml")
        research_config = config.get_research_config()
        episode_config = config.get_episode_config()
        general_config = config.get_general_config()

        return {
            "research": research_config,
            "episode": episode_config,
            "general": general_config
        }
    except Exception as e:
        logger.error(f"Config read error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    try:
        config = ConfigManager(config_file="src/files/config.yaml")

        if request.research:
            # Update research settings
            if 'keywords' in request.research:
                keywords_str = ', '.join(request.research['keywords'])
                config.update_config('research', 'keywords', keywords_str)
            if 'niche' in request.research:
                config.update_config('research', 'niche', request.research['niche'])
            if 'description' in request.research:
                config.update_config('research', 'description', request.research['description'])
            if 'days_back' in request.research:
                config.update_config('research', 'days_back', request.research['days_back'])
            if 'use_random_keywords' in request.research:
                config.update_config('research', 'use_random_keywords', request.research['use_random_keywords'])
            if 'random_keyword_count' in request.research:
                config.update_config('research', 'random_keyword_count', request.research['random_keyword_count'])

            # Ensure platform sections exist
            if 'research' not in config.config:
                config.config['research'] = {}

            # Twitter settings
            if 'twitter' not in config.config['research']:
                config.config['research']['twitter'] = {}
            if 'twitter_enabled' in request.research:
                config.config['research']['twitter']['enabled'] = request.research['twitter_enabled']
            if 'twitter_max_tweets' in request.research:
                config.config['research']['twitter']['max_tweets'] = request.research['twitter_max_tweets']

            # TikTok settings
            if 'tiktok' not in config.config['research']:
                config.config['research']['tiktok'] = {}
            if 'tiktok_enabled' in request.research:
                config.config['research']['tiktok']['enabled'] = request.research['tiktok_enabled']
            if 'tiktok_max_videos' in request.research:
                config.config['research']['tiktok']['max_videos'] = request.research['tiktok_max_videos']
            if 'tiktok_regions' in request.research:
                config.config['research']['tiktok']['regions'] = request.research['tiktok_regions']

            # Threads settings
            if 'threads' not in config.config['research']:
                config.config['research']['threads'] = {}
            if 'threads_enabled' in request.research:
                config.config['research']['threads']['enabled'] = request.research['threads_enabled']
            if 'threads_max_posts' in request.research:
                config.config['research']['threads']['max_posts'] = request.research['threads_max_posts']

            # Reddit settings
            if 'reddit' not in config.config['research']:
                config.config['research']['reddit'] = {}
            if 'reddit_enabled' in request.research:
                config.config['research']['reddit']['enabled'] = request.research['reddit_enabled']
            if 'reddit_max_posts' in request.research:
                config.config['research']['reddit']['max_posts'] = request.research['reddit_max_posts']

        if request.episode:
            if 'duration_minutes' in request.episode:
                config.update_config('episode', 'duration_minutes', request.episode['duration_minutes'])
            if 'host_style' in request.episode:
                config.update_config('episode', 'host_style', request.episode['host_style'])
            if 'target_audience' in request.episode:
                config.update_config('episode', 'target_audience', request.episode['target_audience'])

        if request.general:
            # Ensure general section exists
            if 'general' not in config.config:
                config.config['general'] = {}
            if 'podcast' not in config.config['general']:
                config.config['general']['podcast'] = {}

            if 'podcast_name' in request.general:
                config.config['general']['podcast']['name'] = request.general['podcast_name']
            if 'host_name' in request.general:
                config.config['general']['podcast']['host_name'] = request.general['host_name']
            if 'website' in request.general:
                config.config['general']['podcast']['website'] = request.general['website']

        config.save_config()
        logger.info("Config updated successfully")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Config update error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)
