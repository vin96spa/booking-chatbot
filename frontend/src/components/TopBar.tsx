import { useNavigate } from 'react-router-dom'

function TopBar() {

    let navigate = useNavigate();

    const goToDashboard = () => {
        navigate('/dashboard')
    }
  return (
    <>  
      <div className='flex bg-[#6F092F] h-auto px-[20px] py-[10px] md:px-[40px] md:py-[10px]'>
            <div className='flex-1 flex gap-3 md:gap-6 items-center'>
                  <img className='w-8 h-8 md:w-12 md:h-12' alt='logo' src='./logo.png' />
                  <h1 className='text-[#C2FEBD] text-base md:text-2xl font-bold'>EasyReserve</h1>
            </div>
              <button className='self-center bg-[#ECE8E8] text-black font-bold text-base md:text-lg rounded-full w-auto h-auto px-[8px] py-[4px]' onClick={goToDashboard}>Chiudi Chat</button>
        </div>
    </>

  )
}

export default TopBar