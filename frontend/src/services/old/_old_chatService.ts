import { config, api } from "@/config/api";

export interface ChatMessage {
	id: number;
	isChatBot: boolean;
	message: string;
	timestamp?: number;
}

export interface ChatEvent {
	type:
		| "session_id"
		| "typing"
		| "message"
		| "message_chunk"
		| "waiting_start"
		| "waiting_end"
		| "done"
		| "error";
	data: string;
}

export class ChatService {
	private sessionId: string | null = null;
	private abortController: AbortController | null = null;

	constructor() {
		// Recupera session_id dal localStorage se presente
		this.sessionId = localStorage.getItem("chat_session_id");
	}

	/**
	 * Invia un messaggio al chatbot e gestisce la risposta streaming
	 */
	async sendMessage(
		message: string,
		onEvent: (event: ChatEvent) => void
	): Promise<void> {
		try {
			// Annulla la richiesta precedente se ancora in corso
			if (this.abortController) this.abortController.abort();
			this.abortController = new AbortController();

			if (!response.ok) {
				throw new Error(`HTTP ${response.status}: ${response.statusText}`);
			}

			const reader = response.body?.getReader();
			if (!reader) throw new Error("No response body");

			const decoder = new TextDecoder();
			let buffer = "";

			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				buffer += decoder.decode(value, { stream: true });

				// Processa tutte le linee complete
				const lines = buffer.split("\n");
				buffer = lines.pop() || "";

				for (const line of lines) {
					if (line.startsWith("data: ")) {
						try {
							const eventData: ChatEvent = JSON.parse(line.slice(6));

							// Aggiorna session_id se presente
							if (eventData.type === "session_id")
								this.setSessionId(eventData.data);

							onEvent(eventData);

							if (eventData.type === "done") return;
						} catch (err) {
							console.warn("Error parsing SSE data:", err);
						}
					}
				}
			}
		} catch (err) {
			if (err instanceof Error && err.name === "AbortError") {
				console.log("Request aborted");
				return;
			}

			console.error("Chat error:", err);
			onEvent({ type: "error", data: "Errore di connessione. Riprova." });
		}
	}

	/**
	 * Salva il session_id
	 */
	private setSessionId(sessionId: string): void {
		this.sessionId = sessionId;
		localStorage.setItem("chat_session_id", sessionId);
	}

	/**
	 * Ottieni il session_id corrente
	 */
	getSessionId(): string | null {
		return this.sessionId;
	}

	/**
	 * Cancella la sessione corrente
	 */
	async clearSession(): Promise<void> {
		if (!this.sessionId) return;

		try {
			await fetch(`${config.API_URL}/api/sessions/${this.sessionId}`, {
				method: "DELETE",
			});
		} catch (err) {
			console.error("Error clearing session:", err);
		}

		this.sessionId = null;
		localStorage.removeItem("chat_session_id");
	}

	/**
	 * Annulla la richiesta corrente
	 */
	cancelCurrentRequest(): void {
		if (this.abortController) {
			this.abortController.abort();
			this.abortController = null;
		}
	}

	/**
	 * Ottieni informazioni sulla sessione corrente
	 */
	async getSessionInfo(): Promise<any> {
		if (!this.sessionId) throw new Error("No active session");

		const response = await fetch(
			`${config.API_URL}/api/sessions/${this.sessionId}`
		);
		if (!response.ok) throw new Error(`HTTP ${response.status}`);

		return response.json();
	}
}
