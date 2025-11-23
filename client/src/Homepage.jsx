import './Homepage.css'

function Homepage({ onGetStarted }) {
  return (
    <div className="homepage">
      <div className="hero-section">
        <h1 className="project-title">PaperBuddy</h1>
        <p className="tagline">Big ideas, tiny words.</p>
        <p className="description">
          Transform complex research papers into kid-friendly explanations with AI-powered summaries and illustrations.
        </p>
        <button className="cta-button" onClick={onGetStarted}>
          Get Started
        </button>
      </div>

      <div className="workflow-section">
        <h2>How It Works</h2>
        <div className="workflow-steps">
          <div className="step-card">
            <div className="step-number">1</div>
            <h3>Input</h3>
            <p>Upload PDF or manually enter paper details</p>
          </div>
          <div className="step-card">
            <div className="step-number">2</div>
            <h3>Parse</h3>
            <p>Extract title, authors, and content</p>
          </div>
          <div className="step-card">
            <div className="step-number">3</div>
            <h3>Summarize</h3>
            <p>LLM creates kid-friendly explanation</p>
          </div>
          <div className="step-card">
            <div className="step-number">4</div>
            <h3>Illustrate</h3>
            <p>Generate colorful visuals</p>
          </div>
          <div className="step-card">
            <div className="step-number">5</div>
            <h3>Export</h3>
            <p>Download as one-page PDF</p>
          </div>
        </div>
      </div>

      <div className="tech-stack-section">
        <h2>Technology Stack</h2>
        <div className="tech-columns">
          <div className="tech-column">
            <h3>Frontend</h3>
            <ul>
              <li>React 19.1 - UI framework</li>
              <li>Vite 7.1 - Build tool</li>
              <li>html2pdf.js - PDF generation</li>
            </ul>
          </div>
          <div className="tech-column">
            <h3>Backend</h3>
            <ul>
              <li>Flask 3.0 - Python web framework</li>
              <li>Flask-CORS - Cross-origin support</li>
              <li>pdf.js - PDF parsing</li>
            </ul>
          </div>
          <div className="tech-column">
            <h3>APIs</h3>
            <ul>
              <li>LLM API - Summarization</li>
              <li>Image Gen API - Illustrations</li>
              <li>arXiv/ACM - Paper metadata</li>
            </ul>
          </div>
        </div>
      </div>

      <footer className="homepage-footer">
        <p>A course project focused on simplicity and end-to-end learning.</p>
      </footer>
    </div>
  )
}

export default Homepage
