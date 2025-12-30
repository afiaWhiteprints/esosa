import { useState, useEffect } from 'react'
import HomePage from './pages/HomePage'
import GuidePage from './pages/GuidePage'
import SettingsPage from './pages/SettingsPage'
import ChatModal from './components/ChatModal'
import LoginModal from './components/LoginModal'

function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [chatOpen, setChatOpen] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return localStorage.getItem('esosa_authenticated') === 'true'
  })

  useEffect(() => {
    if (isAuthenticated) {
      localStorage.setItem('esosa_authenticated', 'true')
    }
  }, [isAuthenticated])

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-pink-50 to-purple-100 pb-20 sm:pb-0">
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
              {/* Desktop Tabs */}
              <div className="hidden sm:flex gap-1 bg-pink-100 p-1 rounded-full">
                {['home', 'guide', 'settings'].map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${activeTab === tab
                      ? 'bg-white text-pink-600 shadow-sm'
                      : 'text-gray-600 hover:text-pink-600'
                      }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              {/* Chat Button (Desktop) */}
              <button
                onClick={() => setChatOpen(true)}
                className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-medium text-sm hover:shadow-lg hover:shadow-pink-500/30 transition-all"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Chat
              </button>

              {/* Mobile Chat Button */}
              <button
                onClick={() => setChatOpen(true)}
                className="sm:hidden w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full flex items-center justify-center shadow-lg shadow-pink-500/30"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Bottom Navigation */}
      <div className="sm:hidden fixed bottom-6 left-1/2 -translate-x-1/2 z-40 w-[90%] max-w-sm">
        <div className="bg-white/80 backdrop-blur-xl border border-pink-200 rounded-full shadow-2xl p-1.5 flex gap-1 items-center justify-around">
          {[
            { id: 'home', icon: '🏠', label: 'Home' },
            { id: 'guide', icon: '📖', label: 'Guide' },
            { id: 'settings', icon: '⚙️', label: 'Settings' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 rounded-full flex flex-col items-center gap-1 transition-all ${activeTab === tab.id
                ? 'bg-pink-500 text-white shadow-lg'
                : 'text-gray-500 hover:text-pink-500'
                }`}
            >
              <span className="text-xl">{tab.icon}</span>
              <span className="text-[10px] font-bold uppercase tracking-wider">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Content - Keep components mounted to preserve state */}
      <main className="max-w-6xl mx-auto px-4 py-6 sm:py-8">
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

      {/* Login Guard */}
      {!isAuthenticated && (
        <LoginModal onLogin={() => setIsAuthenticated(true)} />
      )}
    </div>
  )
}

export default App
