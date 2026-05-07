import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import TweaksPanel from './components/TweaksPanel'
import DashboardScreen from './screens/DashboardScreen'
import TicketFormScreen from './screens/TicketFormScreen'
import ProcessingScreen from './screens/ProcessingScreen'
import ResolutionScreen from './screens/ResolutionScreen'
import HistoryScreen from './screens/HistoryScreen'
import { SAMPLE_TICKETS } from './data'

export default function App() {
  const [screen, setScreen] = useState('dashboard')
  const [ticket, setTicket] = useState(null)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState(SAMPLE_TICKETS)
  const [demo, setDemo] = useState(true)
  const [hue, setHue] = useState(250)
  const [speed, setSpeed] = useState('normal')

  function handleSubmit(t) {
    setTicket(t)
    setScreen('pipeline')
  }

  function handleDone(r) {
    setResult(r)
    const newTicket = {
      id: r.ticket_id || `TICKET-${String(history.length + 1).padStart(4, '0')}`,
      subject: ticket?.subject || ticket?.description?.slice(0, 40),
      category: ticket?.category || 'unknown',
      status: r.escalated ? 'escalated' : 'resolved',
      priority: r.priority || 'medium',
      time: 'just now',
    }
    setHistory(h => [newTicket, ...h])
    setScreen('resolution')
  }

  function handleNewTicket() {
    setTicket(null)
    setResult(null)
    setScreen('ticket')
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Sidebar screen={screen} setScreen={setScreen} recentTickets={history} />
      <main style={{ flex: 1, overflowY: 'auto', background: 'oklch(0.97 0.005 240)' }}>
        {screen === 'dashboard'  && <DashboardScreen tickets={history} setScreen={setScreen} />}
        {screen === 'ticket'     && <TicketFormScreen onSubmit={handleSubmit} />}
        {screen === 'pipeline'   && <ProcessingScreen ticket={ticket} onDone={handleDone} />}
        {screen === 'resolution' && <ResolutionScreen ticket={ticket} result={result} onNewTicket={handleNewTicket} />}
        {screen === 'history'    && <HistoryScreen tickets={history} />}
      </main>
      <TweaksPanel demo={demo} setDemo={setDemo} hue={hue} setHue={setHue} speed={speed} setSpeed={setSpeed} />
    </div>
  )
}
