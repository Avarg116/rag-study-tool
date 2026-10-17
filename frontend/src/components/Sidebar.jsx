import { BookOpen, FileText, Plus, X } from 'lucide-react'
import ThemeToggle from './ThemeToggle'
import './Sidebar.css'

// the live demo is built with VITE_DEMO_MODE=true: no uploading or deleting
const demo = import.meta.env.VITE_DEMO_MODE === 'true'

function Sidebar({ documents, uploadingName, onUpload, onDelete, open, onClose, theme, onToggleTheme }) {
  return (
    <>
      {open && <div className="backdrop" onClick={onClose} />}
      <aside className={open ? 'sidebar open' : 'sidebar'}>
        <h3>
          <BookOpen size={18} /> RAG Study Tool
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
        </h3>
        <p className="label">Documents</p>
        {documents.length === 0 && !uploadingName && <p className="empty">No documents yet</p>}
        {documents.map((doc) => (
          <div className="doc" key={doc.id}>
            <FileText size={16} />
            <span>{doc.filename}</span>
            {!demo && <button onClick={() => onDelete(doc)} title="Delete"><X size={14} /></button>}
          </div>
        ))}
        {uploadingName && (
          <div className="doc pending">
            <FileText size={16} />
            <span>{uploadingName}</span>
            <small>Uploading...</small>
          </div>
        )}
        {!demo && (
          <label className="upload">
            <Plus size={16} /> Upload PDF
            <input type="file" accept=".pdf" onChange={onUpload} disabled={!!uploadingName} hidden />
          </label>
        )}
      </aside>
    </>
  )
}

export default Sidebar
