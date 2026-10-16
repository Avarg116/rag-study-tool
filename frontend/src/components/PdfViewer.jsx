import { ExternalLink, X } from 'lucide-react'
import './PdfViewer.css'

function PdfViewer({ source, onClose }) {
  const url = `/api/documents/${source.document_id}/file#page=${source.page_number}`

  return (
    <section className="viewer">
      <div className="viewer-bar">
        <a href={url} target="_blank">
          <ExternalLink size={16} /> Open PDF
        </a>
        <button onClick={onClose} title="Close"><X size={18} /></button>
      </div>
      <iframe key={url} src={url} />
    </section>
  )
}

export default PdfViewer
