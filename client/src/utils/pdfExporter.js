/**
 * PDF Exporter Utility - Module D
 * 
 * Exports the result renderer content to PDF using jspdf and html2canvas
 * 
 * Note: This requires jspdf and html2canvas to be installed:
 * npm install jspdf html2canvas
 */

/**
 * Convert image URL to base64 using CORS proxy to avoid CORS issues
 * @param {string} url - Image URL to convert
 * @param {number} imageIndex - Image index for progress logging (optional)
 * @param {number} totalImages - Total number of images (optional)
 * @returns {Promise<string|null>} Base64 data URL or null if conversion failed
 */
async function imageToBase64(url, imageIndex = null, totalImages = null) {
  const progressPrefix = imageIndex !== null && totalImages !== null 
    ? `[Image ${imageIndex}/${totalImages}]` 
    : ''
  
  try {
    // Use CORS proxy to bypass CORS restrictions
    const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`
    
    const response = await fetch(proxyUrl, {
      method: 'GET',
      headers: {
        'Accept': 'image/*'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const blob = await response.blob()
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  } catch (error) {
    // Silently try fallback - only log if both fail
    // Try alternative proxy (fallback mechanism)
    try {
      if (imageIndex !== null) {
        console.log(`${progressPrefix} Primary proxy failed, trying fallback proxy...`)
      }
      
      const altProxyUrl = `https://corsproxy.io/?${encodeURIComponent(url)}`
      const response = await fetch(altProxyUrl)
      if (response.ok) {
        const blob = await response.blob()
        return new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onloadend = () => {
            if (imageIndex !== null) {
              console.log(`${progressPrefix} Successfully converted via fallback proxy`)
            }
            resolve(reader.result)
          }
          reader.onerror = reject
          reader.readAsDataURL(blob)
        })
      }
    } catch (e) {
      // Only log error if both proxies failed
      console.warn(`${progressPrefix} Both proxy services failed. Primary: ${error.message}, Fallback: ${e.message}`)
    }
    return null
  }
}

export async function exportToPDF(element, filename = 'PaperBuddy Summary') {
  // Track if we need to restore dark mode after export
  const currentTheme = document.documentElement.getAttribute('data-theme')
  const wasDarkMode = currentTheme === 'dark'
  
  try {
    // Dynamic import to handle cases where packages aren't installed yet
    const html2canvas = (await import('html2canvas')).default
    const jsPDF = (await import('jspdf')).default

    console.log('📄 Starting PDF generation...')

    // Step 0: Force light mode for PDF export (even if page is in dark mode)
    if (wasDarkMode) {
      console.log('🌓 Temporarily switching to light mode for PDF export...')
      document.documentElement.setAttribute('data-theme', 'light')
      // Wait for CSS transitions and DOM updates
      await new Promise(resolve => setTimeout(resolve, 300))
    }

    // Step 1: Find all images and convert them to base64
    const images = element.querySelectorAll('img')
    const totalImages = images.length
    
    if (totalImages > 0) {
      console.log(`🖼️  Found ${totalImages} image${totalImages > 1 ? 's' : ''} to process`)
    }
    
    const imagePromises = Array.from(images).map(async (img, index) => {
      const imageNum = index + 1
      const progressPrefix = `[${imageNum}/${totalImages}]`
      
      // Skip if already base64 or blob
      if (img.src.startsWith('data:') || img.src.startsWith('blob:')) {
        console.log(`${progressPrefix} ✓ Already in base64 format, skipping conversion`)
        return
      }

      console.log(`${progressPrefix} Converting image...`)

      // Wait for image to be visible/loaded in the page first
      if (!img.complete || img.naturalHeight === 0) {
        await new Promise((resolve) => {
          let resolved = false
          const timeout = setTimeout(() => {
            if (!resolved) {
              resolved = true
              resolve()
            }
          }, 5000)

          img.onload = () => {
            if (!resolved) {
              resolved = true
              clearTimeout(timeout)
              resolve()
            }
          }
          
          img.onerror = () => {
            if (!resolved) {
              resolved = true
              clearTimeout(timeout)
              resolve()
            }
          }

          if (img.complete && img.naturalHeight > 0) {
            if (!resolved) {
              resolved = true
              clearTimeout(timeout)
              resolve()
            }
          }
        })
      }

      // Convert to base64 using proxy
      try {
        const base64 = await imageToBase64(img.src, imageNum, totalImages)
        if (base64) {
          img.src = base64
          console.log(`${progressPrefix} ✓ Successfully converted to base64`)
        } else {
          console.warn(`${progressPrefix} ⚠️  Conversion failed, will attempt to use original URL in PDF`)
        }
      } catch (e) {
        console.warn(`${progressPrefix} ⚠️  Conversion error:`, e.message)
      }
    })
    
    await Promise.all(imagePromises)
    
    if (totalImages > 0) {
      console.log(`✓ All ${totalImages} image${totalImages > 1 ? 's' : ''} processed`)
    }

    // Step 2: Wait for DOM to update with base64 images
    console.log('⏳ Preparing content for PDF capture...')
    await new Promise(resolve => setTimeout(resolve, 300))

    // Step 3: Use html2canvas to capture the element
    console.log('📸 Capturing page content...')
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: false, // We already converted to base64, no need for CORS
      allowTaint: false, // Safe since we're using base64
      logging: false,
      backgroundColor: '#ffffff',
      width: element.scrollWidth,
      height: element.scrollHeight,
      imageTimeout: 10000,
    })
    
    console.log(`✓ Canvas created (${canvas.width} x ${canvas.height} pixels)`)

    // A4 dimensions in mm (210 x 297)
    const pdfWidth = 210
    const pdfHeight = 297
    
    // Create PDF in portrait mode
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    })

    // Get canvas dimensions
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    
    // Calculate scaling to fit A4 width (with margins)
    const margin = 10 // 10mm margin on each side
    const contentWidth = pdfWidth - (margin * 2)
    const contentHeight = pdfHeight - (margin * 2)
    
    // Convert pixels to mm (assuming 96 DPI, 1 inch = 25.4mm)
    const pixelsPerMm = 96 / 25.4
    const imgWidthMm = imgWidth / pixelsPerMm
    const imgHeightMm = imgHeight / pixelsPerMm
    
    // Calculate scaling ratio to fit width
    const widthRatio = contentWidth / imgWidthMm
    const heightRatio = contentHeight / imgHeightMm
    const ratio = Math.min(widthRatio, heightRatio)
    
    // Calculate final dimensions
    const scaledWidth = imgWidthMm * ratio
    const scaledHeight = imgHeightMm * ratio

    // Add image to PDF
    const imgData = canvas.toDataURL('image/png', 0.95)
    
    // If content fits on one page
    if (scaledHeight <= contentHeight) {
      const x = (pdfWidth - scaledWidth) / 2 // Center horizontally
      pdf.addImage(imgData, 'PNG', x, margin, scaledWidth, scaledHeight)
    } else {
      // Content spans multiple pages
      let yOffset = margin
      let sourceY = 0
      const pageHeight = contentHeight
      const sourceHeight = imgHeight / ratio

      while (sourceY < imgHeight) {
        // Create a temporary canvas for this page
        const pageCanvas = document.createElement('canvas')
        pageCanvas.width = imgWidth
        pageCanvas.height = Math.min(sourceHeight, imgHeight - sourceY)
        const pageCtx = pageCanvas.getContext('2d')
        
        // Draw the portion of the image for this page
        pageCtx.drawImage(
          canvas,
          0, sourceY, imgWidth, pageCanvas.height, // Source
          0, 0, imgWidth, pageCanvas.height // Destination
        )
        
        const pageImgData = pageCanvas.toDataURL('image/png', 0.95)
        const pageHeightMm = pageCanvas.height / pixelsPerMm * ratio
        
        const x = (pdfWidth - scaledWidth) / 2
        pdf.addImage(pageImgData, 'PNG', x, yOffset, scaledWidth, pageHeightMm)
        
        sourceY += pageCanvas.height
        yOffset = margin // Reset for next page
        
        if (sourceY < imgHeight) {
          pdf.addPage()
        }
      }
    }

    // Save PDF
    console.log('💾 Generating PDF file...')
    pdf.save(`${filename}.pdf`)
    console.log(`✅ PDF "${filename}.pdf" generated successfully!`)

    // Restore original theme if it was dark mode
    if (wasDarkMode) {
      console.log('🌓 Restoring dark mode...')
      document.documentElement.setAttribute('data-theme', 'dark')
      // Small delay to ensure smooth transition
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  } catch (error) {
    console.error('PDF export error:', error)
    
    // Restore original theme even if export failed
    if (wasDarkMode) {
      console.log('🌓 Restoring dark mode after error...')
      document.documentElement.setAttribute('data-theme', 'dark')
    }
    
    // Provide helpful error message
    if (error.message && error.message.includes('Cannot find module')) {
      throw new Error(
        'PDF export libraries not installed. Please run: npm install jspdf html2canvas'
      )
    }
    throw error
  }
}
