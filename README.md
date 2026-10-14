# RAG Study Tool

A simple RAG (retrieval-augmented generation) demo built from scratch, without LangChain.

`rag.py` splits `notes.txt` into chunks, embeds them with `all-MiniLM-L6-v2`, finds the
chunks closest to a question with cosine similarity, and asks the model to answer using
only those chunks.

## Run it

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set your Anthropic API key, then run the script:

```
$env:ANTHROPIC_API_KEY="your-key"
python rag.py
```
