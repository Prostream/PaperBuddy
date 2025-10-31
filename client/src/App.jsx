import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [health, setHealth] = useState(null)
  const [papers, setPapers] = useState([])
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('/api/health')
        if (!res.ok) throw new Error('Failed to fetch /api/health')
        const data = await res.json()
        setHealth(data)
      } catch (err) {
        setErrorMessage(err.message)
      }
    }

    const fetchPapers = async () => {
      try {
        const res = await fetch('/api/papers')
        if (!res.ok) throw new Error('Failed to fetch /api/papers')
        const data = await res.json()
        setPapers(Array.isArray(data.items) ? data.items : [])
      } catch (err) {
        setErrorMessage(err.message)
      }
    }

    fetchHealth()
    fetchPapers()
  }, [])

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <div className="card">
        <h2>Server</h2>
        <pre>{health ? JSON.stringify(health, null, 2) : 'Loading...'}</pre>
        {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
      </div>
      <div className="card">
        <h2>Sample Papers</h2>
        {papers.length === 0 ? (
          <p>No papers loaded.</p>
        ) : (
          <ul>
            {papers.map((p) => (
              <li key={p.id}>
                <a href={p.url} target="_blank" rel="noreferrer">
                  {p.title}
                </a>{' '}
                — {Array.isArray(p.authors) ? p.authors.join(', ') : ''} ({p.year})
              </li>
            ))}
          </ul>
        )}
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
