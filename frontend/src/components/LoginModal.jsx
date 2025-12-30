import React, { useState } from 'react';

const LoginModal = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [isShaking, setIsShaking] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);

  // Uses SHA-256 hash from environment variables
  const TARGET_HASH = import.meta.env.VITE_ACCESS_HASH;

  const hashString = async (string) => {
    const utf8 = new TextEncoder().encode(string.toLowerCase());
    const hashBuffer = await crypto.subtle.digest('SHA-256', utf8);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isVerifying) return;

    setIsVerifying(true);
    const inputHash = await hashString(password);

    if (inputHash === TARGET_HASH) {
      onLogin();
    } else {
      setError(true);
      setIsShaking(true);
      setTimeout(() => setIsShaking(false), 500);
      setPassword('');
      setIsVerifying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-white/60 backdrop-blur-xl animate-in fade-in duration-700">
      {/* Soft Background Glows */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-pink-100/40 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-purple-100/40 rounded-full blur-[120px]" />
      </div>

      <div className={`relative w-[90%] max-w-md p-1 bg-gradient-to-br from-pink-100 via-white to-purple-100 rounded-[2rem] shadow-xl transition-all duration-300 font-sans ${isShaking ? 'animate-[shake_0.5s_ease-in-out]' : ''}`}>
        <div className="bg-white/90 backdrop-blur-3xl rounded-[1.9rem] p-8 sm:p-12 flex flex-col items-center text-center">

          <h1 className="text-2xl font-bold text-gray-900 mb-4 tracking-tight">
            Reserved for Esosa and whoever else she invites
          </h1>
          <p className="text-gray-500 text-sm mb-10">
            Type secret word to enter
          </p>

          <form onSubmit={handleSubmit} className="w-full space-y-5">
            <div className="relative group">
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError(false);
                }}
                placeholder="..."
                className={`w-full px-8 py-5 bg-gray-50/50 border border-gray-100 rounded-[1.2rem] outline-none transition-all focus:bg-white focus:border-pink-300 focus:ring-4 focus:ring-pink-500/5 text-center text-xl tracking-widest placeholder:text-gray-200 ${error ? 'border-red-300 bg-red-50/50' : ''
                  }`}
                autoFocus
              />
              {error && (
                <p className="mt-2 text-red-500 text-xs font-semibold">
                  That is not it. Try again.
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isVerifying}
              className={`w-full py-5 bg-pink-500 text-white rounded-[1.2rem] font-bold text-lg shadow-lg hover:bg-pink-600 shadow-pink-500/20 active:translate-y-0.5 transition-all duration-300 ${isVerifying ? 'opacity-70 cursor-not-allowed' : ''
                }`}
            >
              {isVerifying ? 'Verifying...' : 'Enter'}
            </button>
          </form>

          <div className="mt-12 flex flex-col items-center gap-4">
            <p className="text-[11px] text-gray-400 leading-relaxed max-w-[280px]">
              If you made it here, checkout{' '}
              <a
                href="https://open.spotify.com/show/5pPPICiOEUsuK8Aq9bmdqQ?si=29e20eb9f03e4ba3"
                target="_blank"
                rel="noopener noreferrer"
                className="text-pink-500 hover:text-pink-600 font-medium underline underline-offset-4 transition-colors"
              >
                Filtered Therapy
              </a>
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-8px); }
          50% { transform: translateX(8px); }
          75% { transform: translateX(-8px); }
        }
      `}</style>
    </div>
  );
};

export default LoginModal;
