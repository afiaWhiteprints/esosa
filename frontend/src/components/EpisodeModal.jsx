function EpisodeModal({ topic, episodeData, isLoading, onClose }) {
  const outline = episodeData?.outline || {}
  const hasContent = outline.title || episodeData?.topic

  const getPdfUrl = () => {
    if (!episodeData?.pdf_report) return null
    const filename = episodeData.pdf_report.split('/').pop().split('\\').pop()
    return `${import.meta.env.VITE_API_URL}/output/${filename}`
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="bg-white rounded-t-[2.5rem] sm:rounded-2xl shadow-2xl w-full max-w-3xl h-[95vh] sm:max-h-[90vh] overflow-hidden flex flex-col animate-slide-up sm:animate-fade-in">
        {/* Header */}
        <div className="bg-gradient-to-r from-pink-500 to-purple-500 p-6 sm:p-7 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-pink-100 text-[10px] sm:text-sm font-bold uppercase tracking-widest mb-1">Episode Draft</p>
              <h2 className="text-lg sm:text-2xl font-black leading-tight">{topic.title}</h2>
            </div>
            <button
              onClick={onClose}
              className="w-10 h-10 sm:w-12 sm:h-12 rounded-full bg-white/20 hover:bg-white/30 flex items-center justify-center transition-colors active:scale-90 flex-shrink-0 ml-4"
            >
              <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-8 bg-gray-50/30">
          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-20 px-4">
              <div className="inline-block mb-6">
                <div className="w-16 h-16 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
              </div>
              <p className="text-lg font-bold text-gray-800">Drafting your episode...</p>
              <p className="text-pink-500 text-sm mt-3 font-medium">Sit tight, this takes a moment ✨</p>
            </div>
          )}

          {/* Error State */}
          {episodeData?.error && (
            <div className="bg-red-50 border border-red-100 rounded-[2rem] p-8 text-center mx-4">
              <div className="text-4xl mb-4">⚠️</div>
              <p className="text-red-600 font-bold">{episodeData.error}</p>
            </div>
          )}

          {/* Episode Content */}
          {!isLoading && hasContent && (
            <div className="space-y-8 pb-32 sm:pb-8">
              {/* Episode Title & Description */}
              <div className="bg-white rounded-[2rem] p-6 sm:p-8 border border-pink-100 shadow-sm">
                <h3 className="font-black text-gray-800 text-xl sm:text-2xl mb-4 leading-tight">
                  {outline.title || episodeData.topic}
                </h3>
                {outline.description && (
                  <p className="text-gray-600 text-sm sm:text-base leading-relaxed">{outline.description}</p>
                )}
              </div>

              {/* Stats Cards - Stack on Mobile */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  { label: 'Duration', value: `${episodeData.duration_minutes || 60} min`, icon: '⏱️' },
                  { label: 'Style', value: episodeData.host_style || 'Conversational', icon: '🎙️' },
                  { label: 'Audience', value: episodeData.target_audience || 'Gen Z', icon: '👥' }
                ].map((stat, i) => (
                  <div key={i} className="bg-white border border-pink-50 rounded-2xl p-4 flex sm:flex-col items-center sm:justify-center gap-4 sm:gap-1 text-left sm:text-center shadow-sm">
                    <span className="text-2xl sm:mb-2">{stat.icon}</span>
                    <div>
                      <p className="text-gray-400 text-[10px] font-bold uppercase tracking-widest">{stat.label}</p>
                      <p className="font-black text-gray-800 text-sm sm:text-base capitalize">{stat.value}</p>
                    </div>
                  </div>
                ))}
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
