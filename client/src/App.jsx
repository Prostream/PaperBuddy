import { useState } from 'react'
import './App.css'
import Homepage from './Homepage'
import { executeFullPipeline } from './api'
import ResultDisplay from './ResultDisplay'
import { useTheme } from './contexts/ThemeContext'

function App() {
  const { theme, toggleTheme } = useTheme()
  const [view, setView] = useState('home') // 'home' or 'app'
  const [inputType, setInputType] = useState('pdf')
  const [courseTopic, setCourseTopic] = useState('CV')

  // PDF upload
  const [pdfFile, setPdfFile] = useState(null)

  // URL input
  const [urlInput, setUrlInput] = useState('')

  // Manual input fields
  const [manualTitle, setManualTitle] = useState('')
  const [manualAuthors, setManualAuthors] = useState('')
  const [manualAbstract, setManualAbstract] = useState('')
  const [manualSections, setManualSections] = useState([{ heading: '', content: '' }])

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Handle dynamic sections for manual input
  const addSection = () => {
    setManualSections([...manualSections, { heading: '', content: '' }])
  }

  const removeSection = (index) => {
    if (manualSections.length > 1) {
      setManualSections(manualSections.filter((_, i) => i !== index))
    }
  }

  const updateSection = (index, field, value) => {
    const updatedSections = [...manualSections]
    updatedSections[index][field] = value
    setManualSections(updatedSections)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Prepare input based on type
      const input = {
        type: inputType,
        courseTopic: courseTopic
      }

      if (inputType === 'pdf') {
        if (!pdfFile) {
          throw new Error('Please select a PDF file')
        }
        input.data = pdfFile
      } else if (inputType === 'url') {
        if (!urlInput || !urlInput.trim()) {
          throw new Error('Please enter a URL')
        }
        input.data = urlInput.trim()
      } else if (inputType === 'manual') {
        // Validate required fields
        if (!manualTitle || !manualAuthors || !manualAbstract) {
          throw new Error('Please fill in all required fields')
        }

        input.data = {
          title: manualTitle,
          authors: manualAuthors,
          abstract: manualAbstract,
          sections: manualSections.filter(s => s.heading || s.content)
        }
      }

      // Execute full pipeline: Parse → Summarize → Generate Images
      const pipelineResult = await executeFullPipeline(input)
      setResult(pipelineResult)
    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  // Show homepage if view is 'home'
  if (view === 'home') {
    return <Homepage onGetStarted={() => setView('app')} />
  }

  return (
    <div className="app-container">
      <header>
        <div className="header-content">
          <div>
            <h1>PaperBuddy</h1>
            <p className="subtitle">Big ideas, tiny words.</p>
          </div>
          <div className="header-actions">
            <button
              className="theme-toggle"
              onClick={toggleTheme}
              aria-label="Toggle theme"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
            <button
              className="back-to-home"
              onClick={() => setView('home')}
            >
              ← Back to Home
            </button>
          </div>
        </div>
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
              Upload PDF
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
              className={inputType === 'manual' ? 'active' : ''}
              onClick={() => setInputType('manual')}
            >
              Manual Input
            </button>
          </div>
        </div>

        <div className="form-section">
          {inputType === 'pdf' && (
            <div className="input-wrapper">
              <label>Upload PDF (≤20MB)</label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setPdfFile(e.target.files[0])}
                required
              />
              <p className="helper-text">Upload a research paper in PDF format</p>
            </div>
          )}

          {inputType === 'url' && (
            <div className="input-wrapper">
              <label>Paper URL *</label>
              <input
                type="text"
                placeholder="Enter arXiv URL (e.g., https://arxiv.org/abs/1234.5678) or ACM URL"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                required
              />
              <p className="helper-text">Supported: arXiv.org and ACM Digital Library URLs</p>
            </div>
          )}

          {inputType === 'manual' && (
            <div className="manual-input-container">
              <div className="manual-field">
                <label>Paper Title *</label>
                <input
                  type="text"
                  placeholder="Enter the paper title"
                  value={manualTitle}
                  onChange={(e) => setManualTitle(e.target.value)}
                  required
                />
              </div>

              <div className="manual-field">
                <label>Authors *</label>
                <input
                  type="text"
                  placeholder="John Doe, Jane Smith, etc. (comma-separated)"
                  value={manualAuthors}
                  onChange={(e) => setManualAuthors(e.target.value)}
                  required
                />
                <p className="helper-text">Separate multiple authors with commas</p>
              </div>

              <div className="manual-field">
                <label>Abstract *</label>
                <textarea
                  placeholder="Enter the paper abstract"
                  value={manualAbstract}
                  onChange={(e) => setManualAbstract(e.target.value)}
                  rows="4"
                  required
                />
              </div>

              <div className="manual-field">
                <label>Sections (Optional)</label>
                <div className="sections-container">
                  {manualSections.map((section, index) => (
                    <div key={index} className="section-item">
                      <div className="section-inputs">
                        <input
                          type="text"
                          placeholder="Section heading (e.g., Introduction)"
                          value={section.heading}
                          onChange={(e) => updateSection(index, 'heading', e.target.value)}
                          className="section-heading"
                        />
                        <textarea
                          placeholder="Section content"
                          value={section.content}
                          onChange={(e) => updateSection(index, 'content', e.target.value)}
                          rows="3"
                          className="section-content"
                        />
                      </div>
                      {manualSections.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeSection(index)}
                          className="remove-section-btn"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={addSection}
                    className="add-section-btn"
                  >
                    + Add Section
                  </button>
                </div>
              </div>
            </div>
          )}
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
          <p className="helper-text">Select the paper's research domain to help generate better summaries</p>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Processing...' : 'Submit'}
        </button>

        {error && <div className="error">Error: {error}</div>}
      </form>

      {/* Module D: Result Display - Complete display with PDF export */}
      {result && result.paperData && result.summary && (
        <ResultDisplay
          paperData={result.paperData}
          summary={result.summary}
          images={result.images}
        />
      )}
    </div>
  )
}

export default App