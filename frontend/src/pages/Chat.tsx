import Footer from '@/components/Footer';
import TopBar from '@/components/TopBar';
import MessageBox from '@/components/MessageBox';
import chatExample from '@/mockup/chatExample';
import { useState, useEffect, useRef } from 'react';

interface Message {
    id: number;
    isChatBot: boolean;
    message: string;
}


function Chat() { 
    const [messages, setMessages] = useState<Message[]>(chatExample.messages);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    const handleSend = () => {
        if (inputValue.trim()) {
            const newMessage: Message = {
                id: Date.now(),
                isChatBot: false,
                message: inputValue
            };

            setMessages(prevMessages => [...prevMessages, newMessage]);
            setIsTyping(true);
        
            setTimeout(() => {
                const loadingMessage: Message = {
                    id: Date.now() + 1,
                    isChatBot: true,
                    message: '...'
                };

                setMessages(prevMessages => [...prevMessages, loadingMessage]);
            }, 500);
            
            //TODO: Inserire logica comunicazione BE

            setTimeout(() => {
                setMessages(prevMessages => {
                    // Rimuovi il messaggio con i puntini e aggiungero la risposta reale
                    const filteredMessages = prevMessages.filter(msg => msg.message !== '...');
                    const realResponse: Message = {
                        id: Date.now() + 2,
                        isChatBot: true,
                        message: 'Ecco la risposta del chatbot!'
                    };
                    return [...filteredMessages, realResponse];
                });
                setIsTyping(false);
            }, 2000);    
            
            setInputValue('');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    };
  return (
      <div className='h-screen bg-[#62405A] flex flex-col'>
            <TopBar />

            {/* Message Area */}
          <div className='flex-1 overflow-y-auto custom-scrollbar px-[30px] md:px-[100px] pt-2 py-5'>
              <div className='max-w-4xl mx-auto'>
                {
                    messages.map((message) => (
                        <MessageBox 
                            key={message.id} 
                            isChatBot={message.isChatBot} 
                            message={message.message} 
                        />
                    ))
                }
                  <div ref={messagesEndRef} />
              </div>
              <div className='h-[100px]'></div>
            </div>

            {/* Input area */}
          <div className='w-full bg-[#62405A] border-t border-white/10 px-5 py-5 z-10'>
              <div className='relative mx-auto max-w-[700px]'>
                    <input
                      className='w-full px-5 py-2 pr-12 rounded-full shadow-lg'
                        placeholder='Inizia a prenotare ...'
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                    />
                    <button
                        className='absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded-full transition-colors'
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
  )
}

export default Chat