import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage.jsx'
import DashboardPage from './pages/DashboardPage.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <div className="orb orb-purple" />
      <div className="orb orb-teal" />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/creator/:handle" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  )
}
