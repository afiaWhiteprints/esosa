import { useState, useEffect } from 'react'

function SettingsPage() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState(null)

  // Research Form state
  const [keywords, setKeywords] = useState('')
  const [niche, setNiche] = useState('')
  const [description, setDescription] = useState('')
  const [daysBack, setDaysBack] = useState(7)
  const [useRandomKeywords, setUseRandomKeywords] = useState(true)
  const [randomKeywordCount, setRandomKeywordCount] = useState(10)

  // Platform toggles and settings
  const [twitterEnabled, setTwitterEnabled] = useState(true)
  const [twitterMaxTweets, setTwitterMaxTweets] = useState(5)
  const [tiktokEnabled, setTiktokEnabled] = useState(true)
  const [tiktokMaxVideos, setTiktokMaxVideos] = useState(5)
  const [tiktokRegions, setTiktokRegions] = useState('us, ng')
  const [threadsEnabled, setThreadsEnabled] = useState(true)
  const [threadsMaxPosts, setThreadsMaxPosts] = useState(5)
  const [redditEnabled, setRedditEnabled] = useState(true)
  const [redditMaxPosts, setRedditMaxPosts] = useState(5)

  // Episode settings
  const [episodeDuration, setEpisodeDuration] = useState(60)
  const [hostStyle, setHostStyle] = useState('conversational')
  const [targetAudience, setTargetAudience] = useState('Gen Z')

  // Podcast info
  const [podcastName, setPodcastName] = useState('')
  const [hostName, setHostName] = useState('')
  const [website, setWebsite] = useState('')

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/config`)
      const data = await res.json()
      setConfig(data)

      // Populate research form
      setKeywords(data.research?.all_keywords?.join(', ') || data.research?.keywords?.join(', ') || '')
      setNiche(data.research?.niche || '')
      setDescription(data.research?.description || '')
      setDaysBack(data.research?.days_back || 7)
      setUseRandomKeywords(data.research?.use_random_keywords !== false)
      setRandomKeywordCount(data.research?.random_keyword_count || 10)

      // Platform settings
      setTwitterEnabled(data.research?.twitter_enabled !== false)
      setTwitterMaxTweets(data.research?.twitter_max_tweets || 5)
      setTiktokEnabled(data.research?.tiktok_enabled !== false)
      setTiktokMaxVideos(data.research?.tiktok_max_videos || 5)
      setTiktokRegions(data.research?.tiktok_regions?.join(', ') || 'us, ng')
      setThreadsEnabled(data.research?.threads_enabled !== false)
      setThreadsMaxPosts(data.research?.threads_max_posts || 5)
      setRedditEnabled(data.research?.reddit_enabled !== false)
      setRedditMaxPosts(data.research?.reddit_max_posts || 5)

      // Episode settings
      setEpisodeDuration(data.episode?.duration_minutes || 60)
      setHostStyle(data.episode?.host_style || 'conversational')
      setTargetAudience(data.episode?.target_audience || 'Gen Z')

      // Podcast info
      setPodcastName(data.general?.podcast?.name || '')
      setHostName(data.general?.podcast?.host_name || '')
      setWebsite(data.general?.podcast?.website || '')
    } catch (err) {
      console.error('Failed to load config:', err)
      setMessage({ type: 'error', text: 'Failed to load settings. Is the backend running?' })
    } finally {
      setLoading(false)
    }
  }

  const saveConfig = async () => {
    setSaving(true)
    setMessage(null)

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          research: {
            keywords: keywords.split(',').map(k => k.trim()).filter(k => k),
            niche,
            description,
            days_back: daysBack,
            use_random_keywords: useRandomKeywords,
            random_keyword_count: randomKeywordCount,
            twitter_enabled: twitterEnabled,
            twitter_max_tweets: twitterMaxTweets,
            tiktok_enabled: tiktokEnabled,
            tiktok_max_videos: tiktokMaxVideos,
            tiktok_regions: tiktokRegions.split(',').map(r => r.trim()).filter(r => r),
            threads_enabled: threadsEnabled,
            threads_max_posts: threadsMaxPosts,
            reddit_enabled: redditEnabled,
            reddit_max_posts: redditMaxPosts
          },
          episode: {
            duration_minutes: episodeDuration,
            host_style: hostStyle,
            target_audience: targetAudience
          },
          general: {
            podcast_name: podcastName,
            host_name: hostName,
            website: website
          }
        })
      })

      if (res.ok) {
        setMessage({ type: 'success', text: 'Settings saved successfully!' })
      } else {
        throw new Error('Failed to save')
      }
    } catch (err) {
      console.error('Failed to save config:', err)
      setMessage({ type: 'error', text: 'Failed to save settings.' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="text-center py-16">
        <div className="inline-block w-8 h-8 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
        <p className="text-gray-500 mt-4">Loading settings...</p>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Settings</h1>
        <p className="text-gray-600">Configure your podcast research and episode preferences</p>
      </div>

      {/* Message */}
      {message && (
        <div className={`mb-6 p-4 rounded-xl ${
          message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      <div className="space-y-8">
        {/* Podcast Info */}
        <section className="bg-white rounded-2xl border border-pink-100 p-6">
          <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-pink-100 rounded-lg flex items-center justify-center text-pink-600">FT</span>
            Podcast Information
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Podcast Name
              </label>
              <input
                type="text"
                value={podcastName}
                onChange={(e) => setPodcastName(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Filtered Therapy"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Host Name
              </label>
              <input
                type="text"
                value={hostName}
                onChange={(e) => setHostName(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Esosa Mitchell"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Podcast Website/Link
              </label>
              <input
                type="url"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="https://open.spotify.com/show/..."
              />
            </div>
          </div>
        </section>

        {/* Research Settings */}
        <section className="bg-white rounded-2xl border border-pink-100 p-6">
          <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-pink-100 rounded-lg flex items-center justify-center">&#128269;</span>
            Research Settings
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keywords (comma-separated)
              </label>
              <textarea
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="Gen Z, mental health, relationships, self-awareness..."
              />
              <p className="text-xs text-gray-500 mt-1">These keywords are used to search social media platforms</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Podcast Niche
                </label>
                <input
                  type="text"
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                  placeholder="Gen Z Culture and Authenticity"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Days to Look Back
                </label>
                <input
                  type="number"
                  value={daysBack}
                  onChange={(e) => setDaysBack(parseInt(e.target.value))}
                  min={1}
                  max={30}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Podcast Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                placeholder="A Gen Z centered podcast about culture, self-awareness, faith, and real-life chaos..."
              />
            </div>

            {/* Keyword Selection */}
            <div className="bg-pink-50 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <label className="text-sm font-medium text-gray-700">
                  Random Keyword Selection
                </label>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useRandomKeywords}
                    onChange={(e) => setUseRandomKeywords(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
              {useRandomKeywords && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">
                    Number of keywords to randomly select each session
                  </label>
                  <input
                    type="number"
                    value={randomKeywordCount}
                    onChange={(e) => setRandomKeywordCount(parseInt(e.target.value))}
                    min={1}
                    max={50}
                    className="w-24 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                  />
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Platform Settings */}
        <section className="bg-white rounded-2xl border border-pink-100 p-6">
          <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">&#127760;</span>
            Platforms
          </h2>

          <div className="space-y-4">
            {/* Twitter */}
            <div className={`p-4 rounded-xl border ${twitterEnabled ? 'bg-pink-50 border-pink-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center ${twitterEnabled ? 'bg-gray-900 text-white' : 'bg-gray-300 text-white'}`}>X</span>
                  <span className={twitterEnabled ? 'text-gray-800 font-medium' : 'text-gray-500'}>Twitter/X</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={twitterEnabled}
                    onChange={(e) => setTwitterEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
              {twitterEnabled && (
                <div className="pl-11">
                  <label className="block text-xs text-gray-600 mb-1">Max tweets to analyze</label>
                  <input
                    type="number"
                    value={twitterMaxTweets}
                    onChange={(e) => setTwitterMaxTweets(parseInt(e.target.value))}
                    min={5}
                    max={100}
                    className="w-24 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                  />
                </div>
              )}
            </div>

            {/* TikTok */}
            <div className={`p-4 rounded-xl border ${tiktokEnabled ? 'bg-pink-50 border-pink-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center ${tiktokEnabled ? 'bg-black text-white' : 'bg-gray-300 text-white'}`}>&#9834;</span>
                  <span className={tiktokEnabled ? 'text-gray-800 font-medium' : 'text-gray-500'}>TikTok</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={tiktokEnabled}
                    onChange={(e) => setTiktokEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
              {tiktokEnabled && (
                <div className="pl-11 space-y-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Max videos to analyze</label>
                    <input
                      type="number"
                      value={tiktokMaxVideos}
                      onChange={(e) => setTiktokMaxVideos(parseInt(e.target.value))}
                      min={5}
                      max={50}
                      className="w-24 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Regions (comma-separated, e.g., us, ng, uk)</label>
                    <input
                      type="text"
                      value={tiktokRegions}
                      onChange={(e) => setTiktokRegions(e.target.value)}
                      className="w-48 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                      placeholder="us, ng"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Threads */}
            <div className={`p-4 rounded-xl border ${threadsEnabled ? 'bg-pink-50 border-pink-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center ${threadsEnabled ? 'bg-gray-800 text-white' : 'bg-gray-300 text-white'}`}>@</span>
                  <span className={threadsEnabled ? 'text-gray-800 font-medium' : 'text-gray-500'}>Threads</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={threadsEnabled}
                    onChange={(e) => setThreadsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
              {threadsEnabled && (
                <div className="pl-11">
                  <label className="block text-xs text-gray-600 mb-1">Max posts to analyze</label>
                  <input
                    type="number"
                    value={threadsMaxPosts}
                    onChange={(e) => setThreadsMaxPosts(parseInt(e.target.value))}
                    min={5}
                    max={50}
                    className="w-24 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                  />
                </div>
              )}
            </div>

            {/* Reddit */}
            <div className={`p-4 rounded-xl border ${redditEnabled ? 'bg-pink-50 border-pink-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className={`w-8 h-8 rounded-full flex items-center justify-center ${redditEnabled ? 'bg-orange-500 text-white' : 'bg-gray-300 text-white'}`}>&#9673;</span>
                  <span className={redditEnabled ? 'text-gray-800 font-medium' : 'text-gray-500'}>Reddit</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={redditEnabled}
                    onChange={(e) => setRedditEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-pink-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-pink-500"></div>
                </label>
              </div>
              {redditEnabled && (
                <div className="pl-11">
                  <label className="block text-xs text-gray-600 mb-1">Max posts to analyze</label>
                  <input
                    type="number"
                    value={redditMaxPosts}
                    onChange={(e) => setRedditMaxPosts(parseInt(e.target.value))}
                    min={5}
                    max={50}
                    className="w-24 px-3 py-2 border border-pink-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm"
                  />
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Episode Settings */}
        <section className="bg-white rounded-2xl border border-pink-100 p-6">
          <h2 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">&#127908;</span>
            Episode Defaults
          </h2>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  value={episodeDuration}
                  onChange={(e) => setEpisodeDuration(parseInt(e.target.value))}
                  min={15}
                  max={180}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Host Style
                </label>
                <select
                  value={hostStyle}
                  onChange={(e) => setHostStyle(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                >
                  <option value="conversational">Conversational</option>
                  <option value="professional">Professional</option>
                  <option value="casual">Casual</option>
                  <option value="educational">Educational</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Audience
                </label>
                <input
                  type="text"
                  value={targetAudience}
                  onChange={(e) => setTargetAudience(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
                  placeholder="Gen Z"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Save Button */}
        <div className="flex justify-end pb-8">
          <button
            onClick={saveConfig}
            disabled={saving}
            className="px-8 py-3 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-medium hover:shadow-lg transition-shadow disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsPage
