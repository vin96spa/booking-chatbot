import Footer from "@/components/Footer";
import TopBar from "@/components/TopBar";
import MessageBox from "@/components/MessageBox";
import chatExample from "@/mockup/chatExample";
import { useState, useEffect, useRef } from "react";
import { config, api } from "@/config/api";

interface Message {
	id: number;
	isChatBot: boolean;
	message: string;
}

function Chat() {
	const [messages, setMessages] = useState<Message[]>(chatExample.messages);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);
	const [isWaiting] = useState(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const hasCreatedSession = useRef(false);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		if (hasCreatedSession.current) return;

		const createSession = async () => {
			console.log("create session");
			hasCreatedSession.current = true;
			const response = await api.get(config.endpoints.startChat);
			console.log(response.data);
			localStorage.setItem("chat_session_id", response.data);
		};

		createSession();
	}, []);

	useEffect(() => {
		if (messages.length > 2) {
			scrollToBottom();
		}
	}, [messages]);

	const handleSend = () => {
		if (!inputValue.trim() || isTyping || isWaiting) return;

		const newMessage: Message = {
			id: Date.now(),
			isChatBot: false,
			message: inputValue,
		};

		setMessages((prevMessages) => [...prevMessages, newMessage]);
		setIsTyping(true);

		setTimeout(() => {
			const loadingMessage: Message = {
				id: Date.now() + 1,
				isChatBot: true,
				message: "...",
			};

			setMessages((prevMessages) => [...prevMessages, loadingMessage]);
		}, 500);

		//TODO: Inserire logica comunicazione BE
		api
			.post(config.endpoints.chat, {
				session_id: localStorage.getItem("chat_session_id"),
				message: newMessage.message,
			})
			.then(function (response) {
				if (response.data.content == "") throw new Error("Empty response data");

				const botMessage: Message = {
					id: Date.now(),
					isChatBot: true,
					message: response.data.content,
				};

				setTimeout(() => {
					setMessages((prevMessages) => {
						const filteredMessages = prevMessages.filter(
							(msg) => msg.message !== "..."
						);

						return [...filteredMessages, botMessage];
					});
					setIsTyping(false);
				}, 600);
			})
			.catch(function (error: Error) {
				console.error(error);
				setMessages((prevMessages) => {
					const filteredMessages = prevMessages.filter(
						(msg) => msg.message !== "..."
					);

					const errorMessage: Message = {
						id: Date.now() + 2,
						isChatBot: true,
						message:
							"Il servizio è momentaneamente non disponibile. Riprovare più tardi.",
					};

					return [...filteredMessages, errorMessage];
				});
			})
			.finally(() => {
				setIsTyping(false);
			});

		setInputValue("");
	};

	const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter") {
			e.preventDefault();
			handleSend();
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
						{messages.map((message) => (
							<MessageBox
								key={message.id}
								isChatBot={message.isChatBot}
								message={message.message}
							/>
						))}
						<div ref={messagesEndRef} />
					</div>
				</div>
			</div>

			{/* Input area */}
			<div className="fixed bottom-0 left-0 right-0">
				<div className="bg-[#62405A] border-t border-white/10 px-5 py-4">
					<div className="relative mx-auto max-w-[700px]">
						<input
							className="w-full px-5 py-2 pr-12 rounded-full shadow-lg"
							placeholder="Inizia a prenotare ..."
							type="text"
							value={inputValue}
							onChange={(e) => setInputValue(e.target.value)}
							onKeyPress={handleKeyPress}
						/>
						<button
							className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded-full transition-colors"
							type="submit"
							onClick={handleSend}
							disabled={!inputValue.trim()}
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
