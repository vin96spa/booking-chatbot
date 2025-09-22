import { motion } from "framer-motion";
interface MessageBoxProps {
	isChatBot: boolean;
	message: string;
}
const MessageBox: React.FC<MessageBoxProps> = ({ isChatBot, message }) => {
	const isLoading = message === "...";

	return (
		<motion.div
			className="w-full"
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.3, ease: "easeOut" }}
		>
			{isChatBot ? (
				<div className="flex gap-6 mt-2">
					<motion.img
						src="./logo.png"
						alt="chatbot"
						className="w-10 h-10 self-center"
						initial={{ scale: 0 }}
						animate={{ scale: 1 }}
						transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
					/>
					<motion.div
						className="bg-[#FEC5CA] min-w-[200px] max-w-[700px] rounded-tl-lg rounded-tr-lg    rounded-bl-lg text-left p-3 shadow-lg shadow-black/30 break-words whitespace-break-spaces"
						initial={{ scale: 0.8 }}
						animate={{ scale: 1 }}
						transition={{ delay: 0.2, type: "spring", stiffness: 150 }}
					>
						{isLoading ? (
							<div className="flex gap-1">
								<motion.span
									className="w-2 h-2 bg-gray-600 rounded-full"
									animate={{ y: [-3, 3, -3] }}
									transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
								/>
								<motion.span
									className="w-2 h-2 bg-gray-600 rounded-full"
									animate={{ y: [-3, 3, -3] }}
									transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
								/>
								<motion.span
									className="w-2 h-2 bg-gray-600 rounded-full"
									animate={{ y: [-3, 3, -3] }}
									transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
								/>
							</div>
						) : (
							message
						)}
					</motion.div>
				</div>
			) : (
				<motion.div
					className="flex justify-end mt-4"
					initial={{ x: 50 }}
					animate={{ x: 0 }}
					transition={{ type: "spring", stiffness: 100 }}
				>
					<div className="mt-2 bg-[#ECE8E8] min-w-[200px] max-w-[700px] rounded-tl-lg rounded-tr-lg rounded-bl-lg text-left p-3 shadow-lg shadow-black/30 break-words">
						{message}
					</div>
				</motion.div>
			)}
		</motion.div>
	);
};

export default MessageBox;
