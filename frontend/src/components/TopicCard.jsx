import { useState } from 'react'

function TopicCard({ topic, onDraftEpisode }) {
  const [expanded, setExpanded] = useState(false)

  const platformIcons = {
    twitter: 'X',
    tiktok: '♪',
    threads: '@',
    reddit: '◉'
  }

  const platformColors = {
    twitter: 'bg-gray-900 text-white',
    tiktok: 'bg-black text-white',
    threads: 'bg-gray-800 text-white',
    reddit: 'bg-orange-500 text-white'
  }

  const hasSources = Object.values(topic.sources || {}).some(arr => arr && arr.length > 0)

  // Cap relevance score at 100
  const relevanceScore = Math.min(Math.round((topic.relevanceScore || 0.8) * 100), 100)

  return (
    <div className="bg-white rounded-2xl border border-pink-100 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
      <div className="p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            {/* Relevance Score Badge */}
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs px-2 py-1 bg-pink-100 text-pink-700 rounded-full">
                {relevanceScore}% relevant
              </span>
            </div>

            {/* Title */}
            <h3 className="text-xl font-bold text-gray-800 mb-2">{topic.title}</h3>

            {/* Description */}
            {topic.description && (
              <p className="text-gray-600 text-sm leading-relaxed">{topic.description}</p>
            )}
          </div>

          {/* Draft Episode Button */}
          <button
            onClick={onDraftEpisode}
            className="flex-shrink-0 bg-gradient-to-r from-pink-500 to-purple-500 text-white px-5 py-2.5 rounded-full font-medium text-sm hover:shadow-lg hover:shadow-pink-500/30 transition-all hover:-translate-y-0.5"
          >
            Draft Episode
          </button>
        </div>

        {/* Sources Toggle */}
        {hasSources && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-4 flex items-center gap-2 text-sm text-pink-600 hover:text-pink-700"
          >
            <svg
              className={`w-4 h-4 transition-transform ${expanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
            {expanded ? 'Hide sources' : 'View sources'}
          </button>
        )}
      </div>

      {/* Expanded Sources Section */}
      {expanded && hasSources && (
        <div className="border-t border-pink-100 bg-pink-50/50 p-6">
          <p className="text-xs text-gray-500 mb-4 uppercase tracking-wide font-medium">
            Inspired by these posts
          </p>
          <div className="space-y-4">
            {Object.entries(topic.sources || {}).map(([platform, posts]) => {
              if (!posts || posts.length === 0) return null

              return (
                <div key={platform}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${platformColors[platform]}`}>
                      {platformIcons[platform]}
                    </span>
                    <span className="text-sm font-medium text-gray-700 capitalize">{platform}</span>
                  </div>
                  <div className="space-y-2 pl-8">
                    {posts.map((post, i) => {
                      const postText = typeof post === 'string' ? post : post.text || post.title || ''
                      const postUrl = typeof post === 'object' ? post.url : null
                      const postAuthor = typeof post === 'object' ? post.author : null

                      return (
                        <div
                          key={i}
                          className="text-sm bg-white rounded-lg p-3 border border-pink-100"
                        >
                          <p className="text-gray-600 mb-2">{postText}</p>
                          <div className="flex items-center gap-3 text-xs">
                            {postAuthor && (
                              <span className="text-gray-400">@{postAuthor}</span>
                            )}
                            {postUrl && (
                              <a
                                href={postUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-pink-500 hover:text-pink-600 hover:underline flex items-center gap-1"
                              >
                                View post
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default TopicCard
