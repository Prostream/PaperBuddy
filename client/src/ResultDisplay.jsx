import { useRef, useState } from 'react'
import './ResultDisplay.css'
import { exportToPDF } from './utils/pdfExporter'

/**
 * ResultDisplay - Module D Main Component
 * 
 * Displays the complete result according to API_GUIDE layout:
 * 1. Header (Paper Title + Authors)
 * 2. Big Idea (Highlighted)
 * 3. How It Works (Steps) + Images
 * 4. Example & Why It Matters
 * 5. Glossary
 * 6. For Class Section
 * 7. Limitations & Accuracy Flags
 * 8. Export as PDF Button (Bottom)
 */
function ResultDisplay({ paperData, summary, images }) {
  const contentRef = useRef(null)
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)

  const handleExportPDF = async () => {
    if (!contentRef.current) return
    
    setIsExporting(true)
    setExportProgress(0)
    
    try {
      // Simulate progress updates with smoother increments
      const progressInterval = setInterval(() => {
        setExportProgress(prev => {
          if (prev >= 85) {
            clearInterval(progressInterval)
            return prev
          }
          // Gradually slow down as we approach completion
          const increment = prev < 50 ? 15 : prev < 75 ? 10 : 5
          return Math.min(prev + increment, 85)
        })
      }, 150)

      await exportToPDF(contentRef.current, paperData?.title || 'PaperBuddy Summary')
      
      clearInterval(progressInterval)
      setExportProgress(100)
      
      // Wait a moment to show 100% before hiding
      setTimeout(() => {
        setIsExporting(false)
        setExportProgress(0)
      }, 600)
    } catch (error) {
      console.error('PDF export failed:', error)
      alert('Failed to export PDF. Please try again.')
      setIsExporting(false)
      setExportProgress(0)
    }
  }

  // Safety check
  if (!paperData || !summary) {
    return (
      <div className="result-display error-state">
        <p>Missing required data. Please try submitting again.</p>
      </div>
    )
  }

  return (
    <div className="result-display">
      {/* Main content - this will be exported to PDF */}
      <main className="display-content" ref={contentRef}>
        {/* 1. Header (Paper Title + Authors) */}
        <header className="display-header">
          <h1 className="paper-title">{paperData.title}</h1>
          {paperData.authors && paperData.authors.length > 0 && (
            <div className="paper-authors">
              By {paperData.authors.join(', ')}
            </div>
          )}
        </header>

        {/* 2. Big Idea (Highlighted) */}
        {summary.big_idea && (
          <section className="big-idea-section">
            <h2 className="section-title">Big Idea</h2>
            <p className="big-idea-text">{summary.big_idea}</p>
          </section>
        )}

        {/* 3. How It Works (Steps) */}
        {summary.steps && summary.steps.length > 0 && (
          <section className="steps-section">
            <h2 className="section-title">How It Works</h2>
            <ol className="steps-list">
              {summary.steps.map((step, index) => (
                <li key={index} className="step-item">
                  {step}
                </li>
              ))}
            </ol>
          </section>
        )}

        {/* Images (2-5 images) */}
        {images && images.images && images.images.length > 0 && (
          <section className="images-section">
            <div className={`images-grid images-count-${images.images.length}`}>
              {images.images.map((image, index) => (
                <div key={index} className="image-card">
                  {image.url ? (
                    <img
                      src={image.url}
                      alt={image.description || image.key_point || `Illustration ${index + 1}`}
                      className="illustration-image"
                      onError={(e) => {
                        e.target.style.display = 'none'
                        e.target.nextSibling.style.display = 'flex'
                      }}
                    />
                  ) : null}
                  <div className="image-placeholder" style={{ display: image.url ? 'none' : 'flex' }}>
                    <span>🖼️</span>
                  </div>
                  {(image.description || image.key_point) && (
                    <p className="image-caption">
                      {image.description || image.key_point}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* 4. Example & Why It Matters */}
        {(summary.example || summary.why_it_matters) && (
          <section className="example-why-section">
            {summary.example && (
              <div className="example-block">
                <h3 className="block-title">Example</h3>
                <p className="block-text">{summary.example}</p>
              </div>
            )}
            {summary.why_it_matters && (
              <div className="why-block">
                <h3 className="block-title">Why It Matters</h3>
                <p className="block-text">{summary.why_it_matters}</p>
              </div>
            )}
          </section>
        )}

        {/* 5. Glossary */}
        {summary.glossary && summary.glossary.length > 0 && (
          <section className="glossary-section">
            <h2 className="section-title">Glossary</h2>
            <div className="glossary-container">
              <ul className="glossary-list">
                {summary.glossary.map((item, index) => (
                  <li key={index} className="glossary-item">
                    <span className="glossary-term">{item.term || 'Term'}:</span>
                    <span className="glossary-definition">{item.definition || 'Definition not available'}</span>
                  </li>
                ))}
              </ul>
            </div>
          </section>
        )}

        {/* 6. For Class Section */}
        {summary.for_class && (
          <section className="for-class-section">
            <h2 className="section-title">For Class</h2>
            
            {summary.for_class.prerequisites && summary.for_class.prerequisites.length > 0 && (
              <div className="class-block">
                <h3 className="block-title">Prerequisites</h3>
                <ul className="class-list">
                  {summary.for_class.prerequisites.map((prereq, index) => (
                    <li key={index}>{prereq}</li>
                  ))}
                </ul>
              </div>
            )}

            {summary.for_class.connections && summary.for_class.connections.length > 0 && (
              <div className="class-block">
                <h3 className="block-title">Connections</h3>
                <ul className="class-list">
                  {summary.for_class.connections.map((connection, index) => (
                    <li key={index}>{connection}</li>
                  ))}
                </ul>
              </div>
            )}

            {summary.for_class.discussion_questions && summary.for_class.discussion_questions.length > 0 && (
              <div className="class-block">
                <h3 className="block-title">Discussion Questions</h3>
                <ul className="class-list">
                  {summary.for_class.discussion_questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {/* 7. Limitations & Accuracy Flags */}
        {(summary.limitations || (summary.accuracy_flags && summary.accuracy_flags.length > 0)) && (
          <section className="limitations-section">
            {summary.limitations && (
              <div className="limitations-block">
                <h3 className="block-title">Limitations</h3>
                <p className="block-text">{summary.limitations}</p>
              </div>
            )}
            {summary.accuracy_flags && summary.accuracy_flags.length > 0 && (
              <div className="accuracy-flags-block">
                <h3 className="block-title">Accuracy Flags</h3>
                <ul className="flags-list">
                  {summary.accuracy_flags.map((flag, index) => (
                    <li key={index}>{flag}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </main>

      {/* 8. Export as PDF Button (Bottom) */}
      <div className="export-section">
        <button 
          className="export-pdf-btn"
          onClick={handleExportPDF}
          disabled={isExporting}
        >
          {isExporting ? 'Generating PDF...' : 'Export as PDF'}
        </button>
        
        {/* Loading Progress Bar */}
        {isExporting && (
          <div className="pdf-progress-container">
            <div className="pdf-progress-bar">
              <div 
                className="pdf-progress-fill"
                style={{ width: `${exportProgress}%` }}
              ></div>
            </div>
            <p className="pdf-progress-text">{exportProgress}%</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultDisplay

