import './DeleteDialog.css'

function DeleteDialog({ doc, onCancel, onConfirm }) {
  return (
    <div className="dialog-backdrop" onClick={onCancel}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <h4>Delete this document?</h4>
        <p>"{doc.filename}" and its search data will be removed.</p>
        <div className="dialog-buttons">
          <button className="danger" onClick={onConfirm}>Delete</button>
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    </div>
  )
}

export default DeleteDialog
