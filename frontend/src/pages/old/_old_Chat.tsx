import Footer from "@/components/Footer";
import TopBar from "@/components/TopBar";
import MessageBox from "@/components/MessageBox";
import { useState, useEffect, useRef } from "react";
import {
	ChatService,
	ChatMessage,
	ChatEvent,
} from "@/services/old/_old_chatService";

function Chat() {
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);
	const [currentTypingMessage, setCurrentTypingMessage] = useState("");
	const [isWaiting, setIsWaiting] = useState(false);
	const [waitingMessage, setWaitingMessage] = useState("");
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const chatService = useRef(new ChatService());

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, currentTypingMessage]);

	useEffect(() => {
		// Cleanup al dismount
		return () => {
			chatService.current.cancelCurrentRequest();
		};
	}, []);

	const handleSend = async () => {
		if (!inputValue.trim() || isTyping || isWaiting) return;

		const userMessage: ChatMessage = {
			id: Date.now(),
			isChatBot: false,
			message: inputValue.trim(),
			timestamp: Date.now(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsTyping(true);
		setCurrentTypingMessage("");

		try {
			await chatService.current.sendMessage(
				userMessage.message,
				handleChatEvent
			);
		} catch (error) {
			console.error("Send message error:", error);
			handleChatEvent({
				type: "error",
				data: "Errore di connessione. Riprova.",
			});
		}
	};

	const handleChatEvent = (event: ChatEvent) => {
		console.log("Chat event:", event);

		switch (event.type) {
			case "session_id":
				console.log("Session ID ricevuto:", event.data);
				break;

			case "typing":
				setIsTyping(true);
				setCurrentTypingMessage(event.data);
				break;

			case "message":
				// Messaggio completo ricevuto
				const completeMessage: ChatMessage = {
					id: Date.now(),
					isChatBot: true,
					message: event.data,
					timestamp: Date.now(),
				};
				setMessages((prev) => [...prev, completeMessage]);
				setCurrentTypingMessage("");
				break;

			case "message_chunk":
				// Accumula i chunk del messaggio
				setCurrentTypingMessage((prev) => prev + event.data);
				break;

			case "waiting_start":
				setIsWaiting(true);
				setIsTyping(false);
				setCurrentTypingMessage("");
				setWaitingMessage(getWaitingMessage(event.data));
				break;

			case "waiting_end":
				setIsWaiting(false);
				setWaitingMessage("");
				break;

			case "done":
				// Fine dello streaming
				setIsTyping(false);
				setIsWaiting(false);

				// Se c'è un messaggio accumulato, salvalo
				if (currentTypingMessage.trim()) {
					const finalMessage: ChatMessage = {
						id: Date.now(),
						isChatBot: true,
						message: currentTypingMessage.trim(),
						timestamp: Date.now(),
					};
					setMessages((prev) => [...prev, finalMessage]);
					setCurrentTypingMessage("");
				}
				break;

			case "error":
				setIsTyping(false);
				setIsWaiting(false);
				setCurrentTypingMessage("");

				const errorMessage: ChatMessage = {
					id: Date.now(),
					isChatBot: true,
					message: event.data,
					timestamp: Date.now(),
				};
				setMessages((prev) => [...prev, errorMessage]);
				break;
		}
	};

	const getWaitingMessage = (waitingType: string): string => {
		const waitingMessages = {
			transfer: "Trasferimento in corso...",
			"transfer_assistenza tecnica": "Trasferimento ad assistenza tecnica...",
			"transfer_servizio clienti": "Trasferimento a servizio clienti...",
			default: "In attesa...",
		};

		return (
			waitingMessages[waitingType as keyof typeof waitingMessages] ||
			waitingMessages.default
		);
	};

	const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter") {
			e.preventDefault();
			handleSend();
		}
	};

	const clearChat = async () => {
		try {
			await chatService.current.clearSession();
			setMessages([]);
			setCurrentTypingMessage("");
			setIsTyping(false);
			setIsWaiting(false);
		} catch (error) {
			console.error("Error clearing chat:", error);
		}
	};

	return (
		<>
			<div className="fixed top-0 left-0 right-0 z-20">
				<TopBar />
			</div>

			<div className="min-h-screen bg-[#62405A] pt-[68px] md:pt-[72px] pb-[140px] md:pb-[150px]">
				{/* Message Area */}
				<div className="h-full overflow-y-auto custom-scrollbar px-[30px] md:px-[100px] py-5">
					<div className="max-w-4xl mx-auto">
						{/* Session Info */}
						<div className="mb-4 text-center">
							<span className="text-white/50 text-sm">
								Session:{" "}
								{chatService.current.getSessionId() || "Nessuna sessione"}
							</span>
							{messages.length > 0 && (
								<button
									onClick={clearChat}
									className="ml-4 text-white/70 hover:text-white text-sm underline"
								>
									Nuova Chat
								</button>
							)}
						</div>

						{/* Messages */}
						{messages.map((message) => (
							<MessageBox
								key={message.id}
								isChatBot={message.isChatBot}
								message={message.message}
							/>
						))}

						{/* Current typing message */}
						{(isTyping || currentTypingMessage) && (
							<MessageBox
								isChatBot={true}
								message={currentTypingMessage || "L'operatore sta scrivendo..."}
							/>
						)}

						{/* Waiting indicator */}
						{isWaiting && (
							<div className="flex justify-center my-4">
								<div className="bg-white/10 text-white px-4 py-2 rounded-full">
									{waitingMessage}
									<span className="ml-2 animate-pulse">⏳</span>
								</div>
							</div>
						)}

						<div ref={messagesEndRef} />
					</div>
				</div>
			</div>

			{/* Input area */}
			<div className="fixed bottom-0 left-0 right-0">
				<div className="bg-[#62405A] border-t border-white/10 px-5 py-4">
					<div className="relative mx-auto max-w-[700px]">
						<input
							className="w-full px-5 py-2 pr-12 rounded-full shadow-lg disabled:opacity-50"
							placeholder={
								isWaiting
									? "In attesa..."
									: isTyping
									? "L'operatore sta rispondendo..."
									: "Inizia a prenotare ..."
							}
							type="text"
							value={inputValue}
							onChange={(e) => setInputValue(e.target.value)}
							onKeyPress={handleKeyPress}
							disabled={isTyping || isWaiting}
						/>
						<button
							className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
							type="submit"
							onClick={handleSend}
							disabled={!inputValue.trim() || isTyping || isWaiting}
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
								strokeWidth={1.5}
								stroke="currentColor"
								className="w-5 h-5 text-gray-600"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
								/>
							</svg>
						</button>
					</div>
				</div>
				<Footer />
			</div>
		</>
	);
}

export default Chat;
