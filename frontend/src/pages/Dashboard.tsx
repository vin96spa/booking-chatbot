import ticketImage from "@/assets/images/ticket.png";
import { useNavigate } from "react-router-dom";

function Dashboard() {
	let navigate = useNavigate();

	const goToChat = () => {
		navigate("/chat");
	};

	return (
		<>
			<div className="fixed inset-0 bg-[linear-gradient(to_bottom,#62405A,#7B3F6D,#AC3557,#4E74A8,#9B658E)] bg-cover bg-no-repeat bg-center" />

			<div className="fixed inset-0 overflow-hidden flex flex-col items-center justify-center">
				<div className="flex gap-12 justify-center items-center">
					<div className="flex flex-col items-center">
						<h1 className="text-[#C2FEBD] text-3xl md:text-4xl font-bold mb-4 text-center">
							EasyReserve
						</h1>
						<div className="bg-[#FFFFFF12] rounded-full p-6 lg:p-[110px] mb-4">
							<img
								className="w-[200px] h-[200px] md:w-[250px] md:h-[250px] object-contain"
								alt="logo"
								src="./logo.png"
							/>
						</div>
						<img
							alt="ticket"
							src={ticketImage}
							className="w-12 sm:w-14 lg:w-24 h-auto object-contain relative top-[-30px] md:top-[-35px] lg:top-[-55px] rotate-[-25deg]"
						/>
					</div>
					<div className="hidden md:flex md:max-w-[500px] flex-col text-white gap-6">
						<p className="text-2xl">
							L'<b className="text-[#FEC5CA]">Operatore</b> che ti semplifica le
							prenotazioni.
						</p>
						<p className="text-2xl">
							Un unico punto di accesso digitale per le tue prenotazioni. Sempre
							disponibile, sempre aggiornato.
						</p>
						<p className="text-2xl">Che aspetti, provalo!</p>
						<button
							className="button-bg rounded-[12px] w-[200px] h-[45px] self-center"
							onClick={goToChat}
						>
							Prenota con me
						</button>
					</div>
				</div>
				<div className="md:hidden mt-8">
					<button
						className="text-white button-bg rounded-[12px] w-[200px] h-[55px]"
						onClick={goToChat}
					>
						Prenota con me
					</button>
				</div>
			</div>
		</>
	);
}

export default Dashboard;
