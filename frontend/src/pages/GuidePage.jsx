function GuidePage() {
  const steps = [
    {
      number: '01',
      title: 'Generate Ideas',
      description: 'Click the "Generate Podcast Ideas" button to scan Twitter, TikTok, Threads, and Reddit for trending topics relevant to your podcast.',
      icon: '🔍',
      color: 'from-pink-500 to-rose-500'
    },
    {
      number: '02',
      title: 'Explore Topics',
      description: 'Browse through curated topic suggestions. Each topic shows relevance score and source posts that inspired it.',
      icon: '💡',
      color: 'from-purple-500 to-indigo-500'
    },
    {
      number: '03',
      title: 'Draft Episode',
      description: 'Click "Draft Episode" on any topic to generate a complete episode outline with segments, talking points, and show notes.',
      icon: '📝',
      color: 'from-pink-500 to-purple-500'
    },
    {
      number: '04',
      title: 'Download & Record',
      description: 'Download your episode draft as a PDF and use it as your recording guide. Everything you need in one document.',
      icon: '🎙️',
      color: 'from-orange-500 to-pink-500'
    }
  ]

  const features = [
    {
      title: 'Multi-Platform Research',
      description: 'We scan Twitter, TikTok, Threads, and Reddit to find what your audience is talking about.',
      icon: '🌐',
      span: 'col-span-2'
    },
    {
      title: 'AI-Powered',
      description: 'Smart topic curation tailored for Gen Z culture and Filtered Therapy\'s unique voice.',
      icon: '🤖',
      span: 'col-span-1'
    },
    {
      title: 'Chat Assistant',
      description: 'Need help brainstorming? Click the chat bubble anytime to bounce ideas off your AI assistant.',
      icon: '💬',
      span: 'col-span-1'
    },
    {
      title: 'Customizable',
      description: 'Adjust keywords, platforms, and preferences in Settings to fine-tune your research.',
      icon: '⚙️',
      span: 'col-span-2'
    }
  ]

  const tips = [
    'Run research at least once a week to stay on top of trends',
    'Check the source posts to understand context and angles',
    'Use the chat to refine topic ideas before drafting',
    'Save your favorite episode drafts for future reference'
  ]

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-12">
        <span className="inline-block px-4 py-2 bg-purple-100 text-purple-600 rounded-full text-sm font-medium mb-4">
          How to Use
        </span>
        <h1 className="text-3xl font-bold text-gray-800 mb-4">
          Your Podcast Research Assistant
        </h1>
        <p className="text-gray-600 max-w-xl mx-auto">
          From trending topics to episode drafts in minutes. Here's how to get the most out of your assistant.
        </p>
      </div>

      {/* Steps */}
      <div className="grid md:grid-cols-2 gap-6 mb-16">
        {steps.map((step, index) => (
          <div
            key={index}
            className="bg-white rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${step.color} flex items-center justify-center text-2xl`}>
                {step.icon}
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-400 font-medium mb-1">STEP {step.number}</div>
                <h3 className="font-bold text-gray-800 mb-2">{step.title}</h3>
                <p className="text-gray-600 text-sm">{step.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bento Grid Features */}
      <div className="mb-16">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Features</h2>
        <div className="grid grid-cols-3 gap-4">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`${feature.span} bg-gradient-to-br from-gray-50 to-white rounded-2xl p-6 border border-gray-100`}
            >
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="font-bold text-gray-800 mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-gradient-to-br from-pink-500 to-purple-500 rounded-2xl p-8 text-white">
        <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
          <span>✨</span> Pro Tips
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          {tips.map((tip, index) => (
            <div
              key={index}
              className="flex items-start gap-3 bg-white/10 rounded-xl p-4"
            >
              <span className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center text-sm flex-shrink-0">
                {index + 1}
              </span>
              <p className="text-sm text-pink-50">{tip}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-12 text-center">
        <p className="text-gray-500 mb-4">Ready to start?</p>
        <div className="flex gap-4 justify-center">
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); window.scrollTo(0, 0); }}
            className="px-6 py-3 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-medium hover:shadow-lg transition-shadow"
          >
            Go to Home
          </a>
        </div>
      </div>
    </div>
  )
}

export default GuidePage
