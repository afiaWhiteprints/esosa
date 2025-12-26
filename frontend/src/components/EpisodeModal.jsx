function EpisodeModal({ topic, episodeData, isLoading, onClose }) {
  const outline = episodeData?.outline || {}
  const hasContent = outline.title || episodeData?.topic

  const getPdfUrl = () => {
    if (!episodeData?.pdf_report) return null
    const filename = episodeData.pdf_report.split('/').pop().split('\\').pop()
    return `http://localhost:8000/output/${filename}`
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-pink-500 to-purple-500 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-pink-100 text-sm mb-1">Episode Draft</p>
              <h2 className="text-xl font-bold">{topic.title}</h2>
            </div>
            <button
              onClick={onClose}
              className="w-10 h-10 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-block mb-4">
                <div className="w-12 h-12 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
              </div>
              <p className="text-gray-600">Generating episode content...</p>
              <p className="text-pink-500 text-sm mt-2 font-medium">This may take 1-3 minutes. Feel free to leave and come back!</p>
            </div>
          )}

          {/* Error State */}
          {episodeData?.error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
              <p className="text-red-600">{episodeData.error}</p>
            </div>
          )}

          {/* Episode Content */}
          {!isLoading && hasContent && (
            <div className="space-y-6">
              {/* Episode Title & Description */}
              <div className="bg-pink-50 rounded-xl p-5">
                <h3 className="font-bold text-gray-800 text-lg mb-2">
                  {outline.title || episodeData.topic}
                </h3>
                {outline.description && (
                  <p className="text-gray-600">{outline.description}</p>
                )}
              </div>

              {/* Duration & Style */}
              <div className="flex gap-4">
                <div className="flex-1 bg-gray-50 rounded-xl p-4 text-center">
                  <p className="text-gray-500 text-sm">Duration</p>
                  <p className="font-bold text-gray-800">{episodeData.duration_minutes || 60} min</p>
                </div>
                <div className="flex-1 bg-gray-50 rounded-xl p-4 text-center">
                  <p className="text-gray-500 text-sm">Style</p>
                  <p className="font-bold text-gray-800 capitalize">{episodeData.host_style || 'Conversational'}</p>
                </div>
                <div className="flex-1 bg-gray-50 rounded-xl p-4 text-center">
                  <p className="text-gray-500 text-sm">Audience</p>
                  <p className="font-bold text-gray-800">{episodeData.target_audience || 'Gen Z'}</p>
                </div>
              </div>

              {/* Segments */}
              {outline.segments && outline.segments.length > 0 && (
                <div>
                  <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm">📋</span>
                    Episode Segments
                  </h4>
                  <div className="space-y-3">
                    {outline.segments.map((segment, i) => (
                      <div key={i} className="border border-gray-200 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-800">{segment.name}</span>
                          <span className="text-sm text-gray-500">{segment.duration_minutes} min</span>
                        </div>
                        {segment.talking_points && segment.talking_points.length > 0 && (
                          <ul className="space-y-1">
                            {segment.talking_points.map((point, j) => (
                              <li key={j} className="text-sm text-gray-600 flex gap-2">
                                <span className="text-pink-400">-</span>
                                {point}
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Talking Points */}
              {episodeData.talking_points && episodeData.talking_points.length > 0 && (
                <div>
                  <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-pink-100 text-pink-600 rounded-full flex items-center justify-center text-sm">💡</span>
                    Key Talking Points
                  </h4>
                  <ul className="space-y-2">
                    {episodeData.talking_points.map((point, i) => (
                      <li key={i} className="flex gap-3 text-gray-700">
                        <span className="font-bold text-pink-500">{i + 1}.</span>
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* SEO Keywords */}
              {outline.seo_keywords && outline.seo_keywords.length > 0 && (
                <div>
                  <h4 className="font-bold text-gray-800 mb-3">SEO Keywords</h4>
                  <div className="flex flex-wrap gap-2">
                    {outline.seo_keywords.map((keyword, i) => (
                      <span key={i} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer with Download Button */}
        {!isLoading && hasContent && (
          <div className="border-t border-gray-100 p-4 bg-gray-50 flex justify-end gap-3">
            <button
              onClick={onClose}
              className="px-5 py-2.5 text-gray-600 hover:text-gray-800 font-medium"
            >
              Close
            </button>
            {getPdfUrl() && (
              <a
                href={getPdfUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-medium hover:shadow-lg transition-shadow flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Download PDF
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default EpisodeModal
