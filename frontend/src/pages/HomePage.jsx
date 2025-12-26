import { useState, useEffect } from 'react'
import TopicCard from '../components/TopicCard'
import EpisodeModal from '../components/EpisodeModal'

function HomePage() {
  // Load saved topics from localStorage on init
  const [isLoading, setIsLoading] = useState(false)
  const [topics, setTopics] = useState(() => {
    const saved = localStorage.getItem('podcastTopics')
    return saved ? JSON.parse(saved) : []
  })
  const [error, setError] = useState(null)
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [episodeData, setEpisodeData] = useState(null)
  const [episodeLoading, setEpisodeLoading] = useState(false)

  // Save topics to localStorage whenever they change
  useEffect(() => {
    if (topics.length > 0) {
      localStorage.setItem('podcastTopics', JSON.stringify(topics))
    }
  }, [topics])

  const generateIdeas = () => {
    setIsLoading(true)
    setError(null)
    setTopics([])

    fetch('http://localhost:8000/api/research', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keywords: [],
        niche: "",
        description: "",
        days_back: 7
      })
    })
      .then(res => res.json())
      .then(data => {
        console.log('Research data:', data)

        // Extract topics with their sources
        const extractedTopics = extractTopicsWithSources(data)
        setTopics(extractedTopics)
        setIsLoading(false)
      })
      .catch(err => {
        console.error('Research error:', err)
        setError(err.message || 'Failed to generate ideas')
        setIsLoading(false)
      })
  }

  const extractTopicsWithSources = (data) => {
    const topics = []

    // Get AI-generated topics
    const aiTopics = data.ranked_topics || data.ai_topic_suggestions?.topics || []

    // Get source posts from different platforms (use sample_posts with URLs)
    const twitterPosts = data.twitter_results?.sample_posts || data.twitter_results?.trending_topics || []
    const tiktokPosts = data.tiktok_results?.sample_posts || data.tiktok_results?.sample_captions || []
    const threadsPosts = data.threads_results?.sample_posts || []
    const redditPosts = data.reddit_results?.sample_posts || data.reddit_results?.sample_titles || []

    aiTopics.slice(0, 8).forEach((topic, index) => {
      // Get relevance score and normalize to 0-1 scale
      let relevanceScore = topic.relevance_score || topic.score || 8

      // Handle different scales: 1-10, 0-100, or 0-1
      if (relevanceScore > 10) {
        // It's a percentage (0-100), convert to 0-1
        relevanceScore = relevanceScore / 100
      } else if (relevanceScore > 1) {
        // It's on 1-10 scale, convert to 0-1
        relevanceScore = relevanceScore / 10
      }
      // Else it's already 0-1, keep as is

      relevanceScore = Math.min(Math.max(relevanceScore, 0), 1) // Clamp between 0 and 1

      topics.push({
        id: index,
        title: topic.title || topic.topic || `Topic ${index + 1}`,
        description: topic.description || topic.reasoning || '',
        relevanceScore: relevanceScore,
        sources: {
          twitter: twitterPosts.slice(index * 2, index * 2 + 2),
          tiktok: tiktokPosts.slice(index, index + 1),
          threads: threadsPosts.slice(index, index + 1),
          reddit: redditPosts.slice(index, index + 1)
        }
      })
    })

    return topics
  }

  const handleDraftEpisode = (topic) => {
    setSelectedTopic(topic)
    setEpisodeLoading(true)
    setEpisodeData(null)

    fetch('http://localhost:8000/api/episode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic.title,
        duration_minutes: 60,
        host_style: "conversational",
        target_audience: "Gen Z"
      })
    })
      .then(res => res.json())
      .then(data => {
        console.log('Episode data:', data)
        setEpisodeData(data)
        setEpisodeLoading(false)
      })
      .catch(err => {
        console.error('Episode error:', err)
        setEpisodeLoading(false)
        setEpisodeData({ error: err.message })
      })
  }

  const closeEpisodeModal = () => {
    setSelectedTopic(null)
    setEpisodeData(null)
  }

  return (
    <div>
      {/* Hero Section */}
      {topics.length === 0 && !isLoading && (
        <div className="text-center py-16">
          <div className="inline-flex items-center gap-2 bg-pink-100 text-pink-600 px-4 py-2 rounded-full text-sm mb-6">
            <span className="w-2 h-2 bg-pink-500 rounded-full animate-pulse"></span>
            Esosa's Podcast Assistant
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Find Your Next <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-500 to-purple-500">Podcast Topic</span>
          </h1>
          <p className="text-gray-600 max-w-xl mx-auto mb-8">
            Discover trending topics across Twitter, TikTok, Threads, and Reddit.
            Get curated ideas tailored for your podcast.
          </p>

          <button
            onClick={generateIdeas}
            disabled={isLoading}
            className="bg-gradient-to-r from-pink-500 to-purple-500 text-white px-8 py-4 rounded-full font-semibold text-lg shadow-lg shadow-pink-500/30 hover:shadow-xl hover:shadow-pink-500/40 hover:-translate-y-0.5 transition-all disabled:opacity-50"
          >
            Generate Podcast Ideas
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-16">
          <div className="inline-block mb-6">
            <div className="w-16 h-16 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Researching trends...</h2>
          <p className="text-gray-500 mb-2">Scanning Twitter, TikTok, Threads & Reddit</p>
          <p className="text-pink-500 text-sm font-medium">This may take 1-3 minutes. Feel free to leave and come back!</p>
          <div className="flex justify-center gap-2 mt-4">
            {['Twitter', 'TikTok', 'Threads', 'Reddit'].map((platform, i) => (
              <span
                key={platform}
                className="px-3 py-1 bg-white rounded-full text-sm text-gray-600 shadow-sm animate-pulse"
                style={{ animationDelay: `${i * 0.2}s` }}
              >
                {platform}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={generateIdeas}
            className="text-red-600 underline hover:no-underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Topics Grid */}
      {topics.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Podcast Ideas</h2>
              <p className="text-gray-500">{topics.length} topics discovered</p>
            </div>
            <button
              onClick={generateIdeas}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-pink-100 text-pink-600 rounded-full hover:bg-pink-200 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>

          <div className="grid gap-6">
            {topics.map(topic => (
              <TopicCard
                key={topic.id}
                topic={topic}
                onDraftEpisode={() => handleDraftEpisode(topic)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Episode Modal */}
      {selectedTopic && (
        <EpisodeModal
          topic={selectedTopic}
          episodeData={episodeData}
          isLoading={episodeLoading}
          onClose={closeEpisodeModal}
        />
      )}
    </div>
  )
}

export default HomePage
