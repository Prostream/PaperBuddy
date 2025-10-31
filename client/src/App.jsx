import { useState } from 'react'
import './App.css'

function App() {
  const [inputType, setInputType] = useState('abstract')
  const [courseTopic, setCourseTopic] = useState('CV')
  const [abstractText, setAbstractText] = useState('')
  const [paperUrl, setPaperUrl] = useState('')
  const [pdfFile, setPdfFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('type', inputType)
      formData.append('courseTopic', courseTopic)
      
      if (inputType === 'pdf' && pdfFile) {
        formData.append('file', pdfFile)
      } else if (inputType === 'url') {
        formData.append('url', paperUrl)
      } else if (inputType === 'abstract') {
        formData.append('abstract', abstractText)
      }

      const res = await fetch('http://localhost:5175/api/process', {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.error || `HTTP ${res.status}`)
      }

      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>PaperBuddy</h1>
        <p className="subtitle">Big ideas, tiny words.</p>
      </header>

      <form onSubmit={handleSubmit} className="input-form">
        <div className="form-section">
          <label>Input Type</label>
          <div className="input-type-selector">
            <button
              type="button"
              className={inputType === 'pdf' ? 'active' : ''}
              onClick={() => setInputType('pdf')}
            >
              PDF
            </button>
            <button
              type="button"
              className={inputType === 'url' ? 'active' : ''}
              onClick={() => setInputType('url')}
            >
              URL
            </button>
            <button
              type="button"
              className={inputType === 'abstract' ? 'active' : ''}
              onClick={() => setInputType('abstract')}
            >
              Abstract
            </button>
          </div>
        </div>

        <div className="form-section">
          <div className="input-wrapper">
            {inputType === 'pdf' && (
              <>
                <label>Upload PDF (≤20MB)</label>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setPdfFile(e.target.files[0])}
                  required
                />
              </>
            )}
            {inputType === 'url' && (
              <>
                <label>Paper URL</label>
                <input
                  type="url"
                  placeholder="https://arxiv.org/abs/..."
                  value={paperUrl}
                  onChange={(e) => setPaperUrl(e.target.value)}
                  required
                />
              </>
            )}
            {inputType === 'abstract' && (
              <>
                <label>Abstract Text</label>
                <textarea
                  placeholder="Paste the paper abstract here..."
                  value={abstractText}
                  onChange={(e) => setAbstractText(e.target.value)}
                  rows="6"
                  required
                />
              </>
            )}
          </div>
        </div>

        <div className="form-section">
          <label>Course Topic</label>
          <select
            value={courseTopic}
            onChange={(e) => setCourseTopic(e.target.value)}
          >
            <option value="CV">Computer Vision</option>
            <option value="NLP">Natural Language Processing</option>
            <option value="Systems">Systems</option>
          </select>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>

        {error && <div className="error">Error: {error}</div>}
      </form>

      {result && (
        <div className="result-container">
          <h2>Response:</h2>
          <pre className="result-json">{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}

export default App