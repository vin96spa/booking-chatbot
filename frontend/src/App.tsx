import './App.css'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import NotFound from './pages/NotFound'
import { Routes, Route } from 'react-router-dom'

function App() {

  return (
    <>
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/chat" element={<Chat />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
    </>
  )
}

export default App
