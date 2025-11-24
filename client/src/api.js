/**
 * API Client for PaperBuddy
 *
 * This file contains all API calls organized by module.
 * Each team member can focus on their respective module's endpoints.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5175'

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generic fetch wrapper with error handling
 */
async function apiRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || `HTTP ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error)
    throw error
  }
}

// ============================================================================
// MODULE A: Parse Input (Person 1)
// ============================================================================

/**
 * Parse PDF file
 * @param {File} pdfFile - The PDF file to parse
 * @param {string} courseTopic - CV | NLP | Systems
 * @returns {Promise<Object>} Parsed paper data
 */
export async function parsePDF(pdfFile, courseTopic = 'CV') {
  const formData = new FormData()
  formData.append('file', pdfFile)
  formData.append('courseTopic', courseTopic)

  return apiRequest('/api/parse/pdf', {
    method: 'POST',
    body: formData
  })
}

/**
 * Parse URL (arXiv/ACM)
 * @param {string} url - The paper URL
 * @param {string} courseTopic - CV | NLP | Systems
 * @returns {Promise<Object>} Parsed paper data
 */
export async function parseURL(url, courseTopic = 'CV') {
  return apiRequest('/api/parse/url', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, courseTopic })
  })
}

/**
 * Parse manual input
 * @param {Object} manualData - { title, authors, abstract, sections, courseTopic }
 * @returns {Promise<Object>} Validated paper data
 */
export async function parseManual(manualData) {
  return apiRequest('/api/parse/manual', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(manualData)
  })
}

// ============================================================================
// MODULE B: Summarize (Person 2)
// ============================================================================

/**
 * Generate Like-I'm-Five summary using LLM
 * @param {Object} paperData - { title, authors, abstract, sections, courseTopic }
 * @returns {Promise<Object>} Summary with big_idea, steps, example, etc.
 */
export async function summarizePaper(paperData) {
  return apiRequest('/api/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(paperData)
  })
}

// ============================================================================
// MODULE C: Generate Images (Person 3)
// ============================================================================

/**
 * Generate kid-style illustrations
 * @param {Array<string>} keyPoints - 3-5 key concepts to illustrate
 * @param {string} style - "pastel" | "colorful" | "simple"
 * @returns {Promise<Object>} Array of generated images
 */
export async function generateImages(keyPoints, style = 'pastel') {
  return apiRequest('/api/images/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key_points: keyPoints, style })
  })
}

// ============================================================================
// FULL PIPELINE (Module D integration - Person 4)
// ============================================================================

/**
 * Execute full pipeline: Parse → Summarize → Generate Images
 * @param {Object} input - { type: 'pdf' | 'manual', data: File | Object, courseTopic: string }
 * @returns {Promise<Object>} { paperData, summary, images }
 */
export async function executeFullPipeline(input) {
  try {
    // Step 1: Parse input (Module A)
    console.log('Step 1: Parsing input...')
    let paperData

    if (input.type === 'pdf') {
      paperData = await parsePDF(input.data, input.courseTopic)
    } else if (input.type === 'url') {
      paperData = await parseURL(input.data, input.courseTopic)
    } else if (input.type === 'manual') {
      paperData = await parseManual({
        ...input.data,
        courseTopic: input.courseTopic
      })
    } else {
      throw new Error('Invalid input type')
    }

    console.log('✓ Paper data parsed:', paperData)

    // Step 2: Generate summary (Module B)
    console.log('Step 2: Generating summary...')
    const summary = await summarizePaper(paperData)
    console.log('✓ Summary generated:', summary)

    // Step 3: Generate images (Module C)
    console.log('Step 3: Generating images...')
    const keyPoints = summary.steps || []
    const images = await generateImages(keyPoints)
    console.log('✓ Images generated:', images)

    // Return all data for final rendering (Module D)
    return {
      paperData,
      summary,
      images
    }
  } catch (error) {
    console.error('Pipeline error:', error)
    throw error
  }
}

// ============================================================================
// Health Check
// ============================================================================

/**
 * Check API health
 */
export async function checkHealth() {
  return apiRequest('/api/health')
}

/**
 * Get API info
 */
export async function getAPIInfo() {
  return apiRequest('/api/info')
}
