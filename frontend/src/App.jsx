import { useState } from 'react'
import HomePage from './pages/HomePage'
import GuidePage from './pages/GuidePage'
import SettingsPage from './pages/SettingsPage'
import ChatModal from './components/ChatModal'

function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [chatOpen, setChatOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-pink-50 to-purple-100">
      {/* Navigation */}
      <nav className="bg-white/90 backdrop-blur-md border-b border-pink-200 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-purple-500 rounded-lg flex items-center justify-center">
                <span className="text-white text-sm">FT</span>
              </div>
              <span className="font-bold text-gray-800">Filtered Therapy</span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex gap-1 bg-pink-100 p-1 rounded-full">
                {['home', 'guide', 'settings'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                      activeTab === tab
                        ? 'bg-white text-pink-600 shadow-sm'
                        : 'text-gray-600 hover:text-pink-600'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              {/* Chat Button in Nav */}
              <button
                onClick={() => setChatOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-medium text-sm hover:shadow-lg hover:shadow-pink-500/30 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Chat
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content - Keep components mounted to preserve state */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className={activeTab === 'home' ? '' : 'hidden'}>
          <HomePage />
        </div>
        <div className={activeTab === 'guide' ? '' : 'hidden'}>
          <GuidePage />
        </div>
        <div className={activeTab === 'settings' ? '' : 'hidden'}>
          <SettingsPage />
        </div>
      </main>

      {/* Chat Modal */}
      {chatOpen && <ChatModal onClose={() => setChatOpen(false)} />}
    </div>
  )
}

export default App
