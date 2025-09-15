declare module "@/mockup/chatExample" {
    interface Message {
        id: number;
        isChatBot: boolean;
        message: string;
    }

    const chatExample: {
        messages: Message[];
    };

    export default chatExample;
}