# booking-chatbot
A chatbot that recreates all the worst chlichés of customer service: endless waits, repetitive answers and pointless redirects. Instead of making you angry, it will make you laugh in a pleasantly frustrating way.

## Setup
Clone this project in a local folder. <br>
Install Docker Desktop and digit the following command in the prompt:
`docker-compose up --build`.<br>
Create a .env file inside booking-chatbot/backend;
Create or use an OPENAI API KEY from [OpenAI API](https://platform.openai.com/api-keys);
Put your key in the .env file as follows:

    `OPENAI_API_KEY=your_key`
<br>
Finally, open your browser to this link: [localhost:5173](http://localhost:5173/)

## Technologies used
- UI/UX Design: Figma
- Back-End: FastAPI
- Front-End: React + Tailwind
- AI Models: Gemini (`gemini-2.0-flash-exp`) for tests + OpenAI (`gpt-4o-mini`) in production
- Music Effects: Web Audio API
- Music: [Uppbeat](https://uppbeat.io/track/kevin-macleod/long-stroll)
- Deployment: Railway (BE) + Vercel (FE)

## Features
The application lets users chat with an AI booking service that intentionally never reaches users' goal. It does so by parsing system prompts to AI model for each interaction.<br>
The system chooses randomly 1 between 5 system prompts of increasing frustration level for the user. Then it sends the system prompt to the model alongside the user message. <br>
The model responds accordingly, adjusting the frustration level of its answer based on the system prompt.<br>
Front-End simulates waitings and transfers with a timeout and a typical call-center music, triggered by specific keywords in the model's answer.<br>
During the interaction, the chatbot will present two different personalities: the first one is more formal and professional while the second one is more funny and unpredictable.
<br><br>
<img width="1702" height="1038" alt="immagine" src="https://github.com/user-attachments/assets/50e6540e-f254-47a2-b728-2307b2ee686d" />
<br>
*Users can start a new chat by clicking "Prenota ora" button on the initial page.*
<br><br>
<img width="1702" height="1038" alt="immagine" src="https://github.com/user-attachments/assets/aad4363c-bf4a-437f-a7d0-49fbdbd48cb8" />
<br>
*Users can close the chat by clicking on "Chiudi chat" button in the top right. This will also delete the current session from the system. No data about the chat and the session will be saved.*

## API
<img width="467" height="47" alt="image" src="https://github.com/user-attachments/assets/008cad59-e1a2-4805-ac58-8a15a62bcea5" />
<br>It returns new chat session ID.<br><br>
<img width="469" height="51" alt="image" src="https://github.com/user-attachments/assets/add30a65-24f8-4f51-89d2-a61d4697b011" />
<br>It sends user message to AI model and returns AI response.<br><br>
<img width="464" height="51" alt="image" src="https://github.com/user-attachments/assets/9da3c37c-6d2b-4c47-97f3-7be1aaa89857" />
<br>It removes chat session with its message history.






