import { useNavigate } from "react-router-dom";
import { config, api } from "@/config/api";

function TopBar() {
	let navigate = useNavigate();

	const clearSession = async () => {
		await api.delete(`${config.endpoints.closeChat}/${localStorage.getItem("chat_session_id")}`);
		localStorage.removeItem("chat_session_id");
	};

	const goToDashboard = () => {
		clearSession();
		navigate("/dashboard");
	};

	return (
		<header className="bg-[#6F092F] text-[#F5F5F5] shadow-md">
			<div className="max-w-6xl mx-auto flex justify-between items-center px-6 py-3 md:py-4">
				<div className="flex items-center gap-3 md:gap-4">
					<img
						className="w-10 h-10 md:w-12 md:h-12"
						alt="logo"
						src="./logo.png"
					/>
					<h1 className="text-white text-lg md:text-2xl font-bold">
						EasyReserve
					</h1>
				</div>

				<button
					className="bg-[#F5F5F5] text-[#6F092F] font-semibold text-sm md:text-base px-4 py-2 rounded-full shadow hover:bg-gray-200 transition-colors"
					onClick={goToDashboard}
				>
					Chiudi Chat
				</button>
			</div>
		</header>
	);
}

export default TopBar;
