import { useState, useEffect } from 'react';

interface FooterProps {
  onHeightChange?: (height: number) => void;
}

function Footer({ onHeightChange }: FooterProps) {
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Notifica il parent quando cambia l'altezza del footer
    if (onHeightChange) {
      const isMobile = window.innerWidth < 768;
      if (isMobile) {
        onHeightChange(isOpen ? 80 : 0);
      } else {
        onHeightChange(60);
      }
    }
  }, [isOpen, onHeightChange]);

  return (
    <footer className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden absolute -top-[97px] right-[16px] bg-gray-300 opacity-70 hover:bg-gray-400 text-gray-800 w-10 h-6 rounded-t-lg transition-all duration-300 flex items-center justify-center shadow-md"
        aria-label={isOpen ? "Chiudi informazioni footer" : "Mostra informazioni footer"}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={3}
          stroke="currentColor"
          className={`w-4 h-4 transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 15.75l7.5-7.5 7.5 7.5" />
        </svg>
      </button>

      <div className={`
        bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 text-gray-800
        transition-all duration-300 ease-in-out overflow-hidden
        ${isOpen ? 'max-h-40' : 'max-h-0 md:max-h-40'}
      `}>
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center px-6 py-4 gap-2 md:gap-0">
          <div className="text-center text-sm md:text-base">
            &copy; 2025 Vincenzo Spagnolo
          </div>
          <div className="text-center text-xs md:text-sm">
            Music from <span className="font-semibold">Uppbeat</span> (free for Creators!): <br />
            <cite>
              <a
                className="text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                href="https://uppbeat.io/t/kevin-macleod/long-stroll"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Long Stroll by Kevin MacLeod on Uppbeat"
              >
                https://uppbeat.io/t/kevin-macleod/long-stroll
              </a>
            </cite>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;