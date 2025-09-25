import Footer from "@/components/Footer";
import TopBar from "@/components/TopBar";
import MessageBox from "@/components/MessageBox";
import ErrorModal from "@/components/ErrorModal";
import chatExample from "@/mockup/chatExample";
import { useState, useEffect, useRef } from "react";
import { config, api } from "@/config/api";
import { useNavigate } from "react-router-dom";
// importa musica
import waitingMusic from "@/assets/music/waiting-music.mp3";

interface Message {
	id: number;
	isChatBot: boolean;
	message: string;
}

interface ResponseInterface {
	data: {
		content: string;
		role: string;
		transfer: boolean;
		waiting: boolean;
	}
}

// Classe per gestire Web Audio API
class WebAudioManager {
	private audioContext: AudioContext | null = null;
	private source: AudioBufferSourceNode | null = null;
	private gainNode: GainNode | null = null;
	private analyser: AnalyserNode | null = null;
	private buffer: AudioBuffer | null = null;
	private isPlaying: boolean = false;
	
	// Nodi per effetti audio
	private lowPassFilter: BiquadFilterNode | null = null;
	private highPassFilter: BiquadFilterNode | null = null;
	private compressor: DynamicsCompressorNode | null = null;

	async init() {
		if (!this.audioContext) {
			this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();

			// Crea i nodi audio
			this.gainNode = this.audioContext.createGain();
			this.analyser = this.audioContext.createAnalyser();
			this.compressor = this.audioContext.createDynamicsCompressor();
			this.lowPassFilter = this.audioContext.createBiquadFilter();
			this.highPassFilter = this.audioContext.createBiquadFilter();

			// Configura i filtri per un suono più morbido
			this.lowPassFilter.type = 'lowpass';
			this.lowPassFilter.frequency.value = 2000;

			this.highPassFilter.type = 'highpass';
			this.highPassFilter.frequency.value = 100;

			// Configura il compressore
			this.compressor.threshold.value = -20;
			this.compressor.knee.value = 10;
			this.compressor.ratio.value = 4;
			this.compressor.attack.value = 0.003;
			this.compressor.release.value = 0.25;

			// Configura l'analyser
			this.analyser.fftSize = 256;
			this.analyser.smoothingTimeConstant = 0.8;
		}
	}

	async loadAudio(url: string) {
		if (!this.audioContext) await this.init();

		try {
			const response = await fetch(url);
			const arrayBuffer = await response.arrayBuffer();
			this.buffer = await this.audioContext!.decodeAudioData(arrayBuffer);
		} catch (error) {
			console.error('Errore nel caricamento audio:', error);
		}
	}

	private createSource(): AudioBufferSourceNode | null {
		if (!this.buffer || !this.audioContext) return null;

		// Crea un nuovo source node
		const source = this.audioContext.createBufferSource();
		source.buffer = this.buffer;
		source.loop = true;

		// Connetti la catena audio
		source
			.connect(this.highPassFilter!)
			.connect(this.lowPassFilter!)
			.connect(this.compressor!)
			.connect(this.gainNode!)
			.connect(this.analyser!)
			.connect(this.audioContext.destination);

		return source;
	}

	async playMusic(fadeInDuration: number = 1000, telephoneEffect: boolean = false) {
		await this.play(fadeInDuration, telephoneEffect);
	}

	private async play(fadeInDuration: number, telephoneEffect: boolean) {
		if (this.isPlaying || !this.buffer || !this.audioContext) return;


		// Crea e configura il source
		this.source = this.createSource();
		if (!this.source) return;

		const now = this.audioContext.currentTime;

		// Applica effetto telefono se richiesto
		if (telephoneEffect && this.lowPassFilter && this.highPassFilter) {
			this.lowPassFilter.frequency.value = 1200;
			this.highPassFilter.frequency.value = 400;
		} else if (this.lowPassFilter && this.highPassFilter) {
			this.lowPassFilter.frequency.value = 2000;
			this.highPassFilter.frequency.value = 100;
		}

		// Fade in
		this.gainNode!.gain.cancelScheduledValues(now);
		this.gainNode!.gain.setValueAtTime(0, now);
		this.gainNode!.gain.linearRampToValueAtTime(0.3, now + fadeInDuration / 1000);

		// Effetto di "apertura" del filtro
		if (!telephoneEffect && this.lowPassFilter) {
			this.lowPassFilter.frequency.cancelScheduledValues(now);
			this.lowPassFilter.frequency.setValueAtTime(500, now);
			this.lowPassFilter.frequency.exponentialRampToValueAtTime(2000, now + fadeInDuration / 1000);
		}

		// Avvia la riproduzione
		const offset = 1000 % this.buffer.duration;
		this.source.start(0, offset);
		this.isPlaying = true;
	}

	stop(fadeOutDuration: number = 800) {
		if (!this.isPlaying || !this.source || !this.audioContext || !this.gainNode) return;

		const now = this.audioContext.currentTime;

		// Fade out
		this.gainNode.gain.cancelScheduledValues(now);
		this.gainNode.gain.setValueAtTime(this.gainNode.gain.value, now);
		this.gainNode.gain.linearRampToValueAtTime(0, now + fadeOutDuration / 1000);

		// Effetto di "chiusura" del filtro
		if (this.lowPassFilter) {
			this.lowPassFilter.frequency.cancelScheduledValues(now);
			this.lowPassFilter.frequency.setValueAtTime(this.lowPassFilter.frequency.value, now);
			this.lowPassFilter.frequency.exponentialRampToValueAtTime(200, now + fadeOutDuration / 1000);
		}

		// Ferma l'audio dopo il fade
		this.source.stop(now + fadeOutDuration / 1000);

		this.isPlaying = false;
		this.source = null;
	}

	getFrequencyData(): Uint8Array {
		if (!this.analyser) return new Uint8Array(128);

		const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
		this.analyser.getByteFrequencyData(dataArray);
		return dataArray;
	}

	cleanup() {
		if (this.source && this.isPlaying) {
			this.source.stop();
		}
		if (this.audioContext && this.audioContext.state !== 'closed') {
			this.audioContext.close();
		}
	}
}

// Hook personalizzato per Web Audio nel chat
const useWebAudioChat = () => {
	const audioManagerRef = useRef<WebAudioManager | null>(null);
	const [isAudioReady, setIsAudioReady] = useState(false);

	useEffect(() => {
		// Inizializza audio manager
		const initAudio = async () => {
			audioManagerRef.current = new WebAudioManager();
			await audioManagerRef.current.init();

			// Carica i file audio
			await audioManagerRef.current.loadAudio(waitingMusic);

			setIsAudioReady(true);
		};

		initAudio();

		// Cleanup
		return () => {
			if (audioManagerRef.current) {
				audioManagerRef.current.cleanup();
			}
		};
	}, []);

	const playWaiting = () => {
		if (audioManagerRef.current && isAudioReady) {
			audioManagerRef.current.playMusic(1000, false);
		}
	};

	const playTransfer = () => {
		if (audioManagerRef.current && isAudioReady) {
			audioManagerRef.current.playMusic(800, true);
		}
	};

	const stopAudio = () => {
		if (audioManagerRef.current) {
			audioManagerRef.current.stop();
		}
	};

	const getFrequencyData = () => {
		if (audioManagerRef.current) {
			return audioManagerRef.current.getFrequencyData();
		}
		return new Uint8Array(128);
	};

	return {
		playWaiting,
		playTransfer,
		stopAudio,
		getFrequencyData,
		isAudioReady
	};
};

function Chat() {
	let navigate = useNavigate();
	const [messages, setMessages] = useState<Message[]>(chatExample.messages);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);
	const [isWaiting, setIsWaiting] = useState(false);
	const [isTransfer, setIsTransfer] = useState(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const hasCreatedSession = useRef(false);

	// Stati per la modale di errore
	const [showErrorModal, setShowErrorModal] = useState(false);
	const [sessionErrorMessage, setSessionErrorMessage] = useState("");
	const [errorModalTitle, setErrorModalTitle] = useState("");
	const [errorModalSubtitle, setErrorModalSubtitle] = useState("");

	const { playWaiting, playTransfer, stopAudio, isAudioReady } = useWebAudioChat();

	useEffect(() => {
		if (!isAudioReady) return;

		if (isTransfer) {
			playTransfer();
		} else if (isWaiting) {
			playWaiting();
		} else {
			stopAudio();
		}
	}, [isWaiting, isTransfer, isAudioReady]);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		if (hasCreatedSession.current) return;

		const createSession = async () => {
			hasCreatedSession.current = true;

			try {
				const response = await api.get(config.endpoints.startChat);
				if (response.data?.session_id) {
					localStorage.setItem("chat_session_id", response.data.session_id);
				} else {
					throw new Error("Session ID non ricevuto");
				}
			} catch (error: any) {
				console.error("Errore nella creazione della sessione:", error);

				// Determina il messaggio di errore
				let errorMsg = "Errore di connessione";

				if (error.response) {
					// Errore dal server
					errorMsg = error.response.data?.message ||
						`Errore del server (${error.response.status})`;
				} else if (error.request) {
					// Nessuna risposta dal server
					errorMsg = "Il server non risponde. Verifica la connessione.";
				} else {
					// Altro tipo di errore
					errorMsg = error.message || "Errore sconosciuto";
				}

				setSessionErrorMessage(errorMsg);
				setShowErrorModal(true);
				setErrorModalTitle("Errore di Connessione");
				setErrorModalSubtitle("Non è stato possibile creare la sessione di chat.");
			}
		};

		createSession();
	}, []);

	useEffect(() => {
		if (messages.length > 2) {
			scrollToBottom();
		}
	}, [messages]);

	const handleErrorModalConfirm = () => {
		// Pulisci eventuali dati di sessione
		localStorage.removeItem("chat_session_id");
		setErrorModalTitle("");
		setErrorModalSubtitle("");

		// Naviga alla dashboard
		navigate("/dashboard");
	};

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

		// Richiede la risposta del bot
		api
			.post(config.endpoints.chat, {
				session_id: localStorage.getItem("chat_session_id"),
				message: newMessage.message,
			})
			.then(function (response: ResponseInterface) {

				if (response.data.waiting) {
					setIsWaiting(true);
					setIsTransfer(false);

					const waitingMessage: Message = {
						id: Date.now() + 10,
						isChatBot: true,
						message: "Ti metto in attesa...",
					};

					setMessages((prevMessages) => {
						const filteredMessages = prevMessages.filter(
							(msg) => msg.message !== "..."
						);
						return [...filteredMessages, waitingMessage];
					});

					setTimeout(() => {
						setIsTransfer(false);
						setIsWaiting(false);

						const operatorMessage: Message = {
							id: Date.now() + 11,
							isChatBot: true,
							message: "Eccomi, dove eravamo rimasti?",
						};

						setMessages((prevMessages) => [...prevMessages, operatorMessage]);
					}, 10000);
					return;
				} else if (response.data.transfer) {
					setIsWaiting(false);
					setIsTransfer(true);

					const transferMessage: Message = {
						id: Date.now() + 10,
						isChatBot: true,
						message: "Ti sto trasferendo ad un operatore, attendi...",
					};

					setMessages((prevMessages) => {
						const filteredMessages = prevMessages.filter(
							(msg) => msg.message !== "..."
						);
						return [...filteredMessages, transferMessage];
					});

					setTimeout(() => {
						setIsTransfer(false);
						setIsWaiting(false);


						const operatorMessage: Message = {
							id: Date.now() + 11,
							isChatBot: true,
							message: "Operatore connesso. Come posso aiutarti?",
						};

						setMessages((prevMessages) => [...prevMessages, operatorMessage]);
					}, 25000);
					return;
				} else {
					setIsWaiting(false);
					setIsTransfer(false);
				}

				let aiMsg = response.data.content;
				if (aiMsg == "") throw new Error("Empty response data");

				aiMsg = aiMsg.replaceAll("\n*", "");
				const botMessage: Message = {
					id: Date.now(),
					isChatBot: true,
					message: aiMsg,
				};

				setTimeout(() => {
					setMessages((prevMessages) => {
						const filteredMessages = prevMessages.filter(
							(msg) => msg.message !== "..."
						);

						return [...filteredMessages, botMessage];
					});
					setIsTyping(false);

					if (!response.data.waiting && !response.data.transfer) {
						setIsWaiting(false);
						setIsTransfer(false);
					}
				}, 600);
			})
			.catch(function (error: any) {
				console.error(error);
				// Caso Too Many Requests (limite API raggiunto)
				if (error.status === 429) {
					setErrorModalTitle("Attenzione!");
					setErrorModalSubtitle("Limite token raggiunto. Riprova più tardi.");
					setShowErrorModal(true);
				} else {
					setTimeout(() => {
						const errorMessage: Message = {
							id: Date.now() + 2,
							isChatBot: true,
							message: error.response?.data?.detail,
						};

						setMessages((prevMessages) => {
							const filteredMessages = prevMessages.filter(
								(msg) => msg.message !== "..."
							);
							return [...filteredMessages, errorMessage];
						});
					}, 1000);
				}

				setIsWaiting(false);
				setIsTransfer(false);
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

			<ErrorModal
				isOpen={showErrorModal}
				title={errorModalTitle}
				subtitle={errorModalSubtitle}
				errorMessage={sessionErrorMessage}
				onConfirm={handleErrorModalConfirm}
			/>

			<div className="fixed top-0 left-0 right-0 z-20">
				<TopBar />
			</div>

			<div className="fixed top-[52px] md:top-[68px] bottom-[140px] md:bottom-[130px] left-0 right-0 bg-[#62405A] pb-2">
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

						{/* Indicatore visivo dello stato audio */}
						{(isWaiting || isTransfer) && (
							<div className="flex items-center justify-center mt-4 mb-2">
								<div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full">
									<div className="flex gap-1">
										{[...Array(4)].map((_, i) => (
											<div
												key={i}
												className="w-1 h-4 bg-white/70 animate-pulse"
												style={{
													animationDelay: `${i * 150}ms`,
													height: isTransfer ? '16px' : '12px'
												}}
											/>
										))}
									</div>
									<span className="text-white/80 text-sm">
										{isTransfer ? "Trasferimento in corso..." : "In attesa..."}
									</span>
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
							className="w-full px-5 py-2 pr-12 rounded-full shadow-lg"
							placeholder="Inizia a prenotare ..."
							type="text"
							value={inputValue}
							onChange={(e) => setInputValue(e.target.value)}
							onKeyPress={handleKeyPress}
							disabled={isTransfer || isWaiting}
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
