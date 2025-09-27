# booking-chatbot
A chatbot that recreates all the worst chlichés of customer service: endless waits, repetitive answers and pointless redirects. Instead of making you angry, it will make you laugh in a pleasantly frustrating way.

## Setup
Clone this project in a local folder.
Installing Docker Desktop and digit the following command in the prompt:
`docker-compose up --build`.

Finally, open your browser to this link: [http://localhost:5173/]

## Technologies used
- UI/UX Design: Figma
- Back-End: FastAPI
- Front-End: React + Tailwind
- AI Models: Gemini ('gemini-2.0-flash-exp') for tests + OpenAI ('gpt-4o-mini') in production
- Music Effects: Web Audio API
- Music: Uppbeat [https://uppbeat.io/track/kevin-macleod/long-stroll]
- Deployment: Railway (BE) + Vercel (FE)

## Features
The application lets users chat with an AI booking service that intentionally never reaches users' goal.<br>
It does so by parsing system prompts to AI model for each interaction.<br>

## API
<img width="467" height="47" alt="image" src="https://github.com/user-attachments/assets/008cad59-e1a2-4805-ac58-8a15a62bcea5" />
<br>It returns new chat session ID<br>


<img width="469" height="51" alt="image" src="https://github.com/user-attachments/assets/add30a65-24f8-4f51-89d2-a61d4697b011" />
<br>It sends user message to AI model and returns AI response<br>


<img width="464" height="51" alt="image" src="https://github.com/user-attachments/assets/9da3c37c-6d2b-4c47-97f3-7be1aaa89857" />
<br>It removes chat session with its message history<br>






