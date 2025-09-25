function Footer() {
  return (
    <footer className="bg-gradient-to-r from-gray-300 via-gray-200 to-gray-300 text-gray-800">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center px-6 py-4 gap-2 md:gap-0">
        <div className="text-center text-sm md:text-base">
          © 2025 Vincenzo Spagnolo
        </div>
        <div className="text-center text-xs md:text-sm">
          Music from <span className="font-semibold">Uppbeat</span> (free for Creators!): <br />
          <a 
            className="text-blue-600 hover:text-blue-800 transition-colors" 
            href="https://uppbeat.io/t/kevin-macleod/long-stroll"
            target="_blank" 
            rel="noopener noreferrer"
          >
            https://uppbeat.io/t/kevin-macleod/long-stroll
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
