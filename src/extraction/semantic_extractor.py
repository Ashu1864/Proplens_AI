import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.Client(Settings())

def chunk_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def semantic_embed_pdf(pdf_path, collection_name):
    collection = client.get_or_create_collection(name=collection_name)
    with pdfplumber.open(pdf_path) as pdf:
        documents, metadatas, ids = [], [], []
        chunk_id = 0
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for chunk in chunk_text(text):
                embedding = embedding_model.encode(chunk).tolist()
                documents.append(chunk)
                metadatas.append({"source": pdf_path, "page": i + 1})
                ids.append(f"{collection_name}_page{i+1}_chunk{chunk_id}")
                chunk_id += 1

        collection.add(documents=documents, metadatas=metadatas, ids=ids)
