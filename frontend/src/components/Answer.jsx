import Markdown from 'react-markdown'
import './Answer.css'

function Answer({ result, activeSource, onOpenSource }) {
  return (
    <div className="answer">
      <Markdown>{result.answer}</Markdown>
      <p className="label">Sources</p>
      {result.sources.map((source, i) => (
        <div
          className={source === activeSource ? 'source active' : 'source'}
          key={i}
          onClick={() => onOpenSource(source)}
        >
          <span className="number">{i + 1}</span>
          {source.filename}
          <span className="page">page {source.page_number}</span>
        </div>
      ))}
    </div>
  )
}

export default Answer
