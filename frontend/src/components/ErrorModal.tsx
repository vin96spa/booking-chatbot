interface ErrorModalProps {
    isOpen: boolean;
    title: string;
    subtitle: string;
    errorMessage: string;
    onConfirm: () => void;
}

const ErrorModal: React.FC<ErrorModalProps> = ({ isOpen, title, subtitle, errorMessage, onConfirm }) => {
    if (!isOpen) return null;

    return (
        <>
            {/* Overlay scuro */}
            <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 animate-fadeIn" />

            {/* Modale */}
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-xl shadow-2xl max-w-md w-full animate-slideUp">
                    {/* Header con icona di errore */}
                    <div className="flex items-center justify-center pt-6 pb-4">
                        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                            <svg
                                className="w-8 h-8 text-red-600"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                                />
                            </svg>
                        </div>
                    </div>

                    {/* Body */}
                    <div className="px-6 pb-4">
                        <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
                            { title }
                        </h2>
                        <p className="text-gray-600 text-center mb-1">
                            { subtitle }
                        </p>
                        {errorMessage && (
                            <p className="text-sm text-gray-500 text-center mt-2">
                                Dettaglio: {errorMessage}
                            </p>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="px-6 pb-6">
                        <button
                            onClick={onConfirm}
                            className="w-full py-3 bg-[#62405A] hover:bg-[#4a2f44] text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[#62405A] focus:ring-offset-2"
                        >
                            Torna alla Dashboard
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default ErrorModal;