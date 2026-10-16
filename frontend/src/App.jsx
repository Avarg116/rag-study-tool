import { useEffect, useState } from 'react'
import { ArrowUp, LoaderCircle, Menu, Search } from 'lucide-react'
import Sidebar from './components/Sidebar'
import Answer from './components/Answer'
import PdfViewer from './components/PdfViewer'
import DeleteDialog from './components/DeleteDialog'
import ThemeToggle from './components/ThemeToggle'
import './App.css'

function App() {
  const [documents, setDocuments] = useState([])
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploadingName, setUploadingName] = useState(null)
  const [viewer, setViewer] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [toDelete, setToDelete] = useState(null)
  const [theme, setTheme] = useState(
    localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
  )

  // switch the colors and remember the choice
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('theme', theme)
  }, [theme])

  function toggleTheme() {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  async function loadDocuments() {
    const res = await fetch('/api/documents/')
    if (res.ok) setDocuments(await res.json())
  }

  useEffect(() => {
    loadDocuments()

    function onKeyDown(e) {
      if (e.key === 'Escape') {
        setViewer(null)
        setToDelete(null)
        setMenuOpen(false)
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [])

  async function uploadFile(e) {
    const file = e.target.files[0]
    e.target.value = ''
    setUploadingName(file.name)
    const form = new FormData()
    form.append('file', file)
    const res = await fetch('/api/documents/upload', { method: 'POST', body: form })
    if (!res.ok) alert((await res.json()).detail)
    await loadDocuments()
    setUploadingName(null)
  }

  async function deleteDocument() {
    setDocuments(documents.filter((doc) => doc.id !== toDelete.id))
    setToDelete(null)
    await fetch(`/api/documents/${toDelete.id}`, { method: 'DELETE' })
    loadDocuments()
  }

  async function ask(text) {
    setQuestion(text)
    setLoading(true)
    setResult(null)
    setViewer(null)
    const res = await fetch('/api/query/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text }),
    })
    if (res.ok) setResult(await res.json())
    else alert('Something went wrong')
    setLoading(false)
  }

  return (
    <div className="app">
      <Sidebar
        documents={documents}
        uploadingName={uploadingName}
        onUpload={uploadFile}
        onDelete={setToDelete}
        open={menuOpen}
        onClose={() => setMenuOpen(false)}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* on phones */}
      <header className="mobile-header">
        <button onClick={() => setMenuOpen(true)}><Menu size={20} /></button>
        RAG Study Tool
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </header>

      <main className="main">
        <h1>Ask your notes</h1>
        <p className="subtitle">Answers come only from your uploaded PDFs, with the page they came from.</p>
        <form onSubmit={(e) => { e.preventDefault(); ask(question) }}>
          <Search size={18} className="search-icon" />
          <input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask anything about your notes..." />
          <button disabled={loading || !question.trim()} title="Ask">
            {loading ? <LoaderCircle size={18} className="spin" /> : <ArrowUp size={18} />}
          </button>
        </form>

        {!result && !loading && documents.length === 0 && (
          <p className="hint">Upload a PDF from the sidebar to get started.</p>
        )}

        {loading && (
          <div className="skeleton">
            <p className="status">Searching your notes...</p>
            <div /><div /><div />
          </div>
        )}

        {result && <Answer result={result} activeSource={viewer} onOpenSource={setViewer} />}
      </main>

      {viewer && <PdfViewer source={viewer} onClose={() => setViewer(null)} />}

      {toDelete && <DeleteDialog doc={toDelete} onCancel={() => setToDelete(null)} onConfirm={deleteDocument} />}
    </div>
  )
}

export default App
