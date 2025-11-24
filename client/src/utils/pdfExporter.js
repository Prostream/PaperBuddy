/**
 * PDF Exporter Utility - Module D
 * 
 * Exports the result renderer content to PDF using jspdf and html2canvas
 * 
 * Note: This requires jspdf and html2canvas to be installed:
 * npm install jspdf html2canvas
 */

/**
 * Export content to PDF
 * @param {HTMLElement} element - The DOM element to export
 * @param {string} filename - The filename for the PDF (without .pdf extension)
 */
export async function exportToPDF(element, filename = 'PaperBuddy Summary') {
  try {
    // Dynamic import to handle cases where packages aren't installed yet
    const html2canvas = (await import('html2canvas')).default
    const jsPDF = (await import('jspdf')).default

    // Show loading indicator (optional - you can add a toast/loading state)
    console.log('Generating PDF...')

    // Configure html2canvas options for better quality
    const canvas = await html2canvas(element, {
      scale: 2, // Higher quality
      useCORS: true, // Handle cross-origin images
      logging: false,
      backgroundColor: '#ffffff',
      width: element.scrollWidth,
      height: element.scrollHeight,
    })

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
    // Scale factor: 96 pixels per inch = 96/25.4 pixels per mm
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
    const imgData = canvas.toDataURL('image/png', 0.95) // 0.95 quality for smaller file size
    
    // If content fits on one page
    if (scaledHeight <= contentHeight) {
      const x = (pdfWidth - scaledWidth) / 2 // Center horizontally
      pdf.addImage(imgData, 'PNG', x, margin, scaledWidth, scaledHeight)
    } else {
      // Content spans multiple pages
      let yOffset = margin
      let sourceY = 0
      const pageHeight = contentHeight
      const sourceHeight = imgHeight / ratio // Height in pixels for each page

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
    pdf.save(`${filename}.pdf`)
    console.log('PDF generated successfully!')
  } catch (error) {
    console.error('PDF export error:', error)
    
    // Provide helpful error message
    if (error.message && error.message.includes('Cannot find module')) {
      throw new Error(
        'PDF export libraries not installed. Please run: npm install jspdf html2canvas'
      )
    }
    throw error
  }
}

