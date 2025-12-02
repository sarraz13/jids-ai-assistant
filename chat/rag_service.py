import os
import faiss
import numpy as np
from typing import List, Optional
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .models import Document, DocumentChunk

# Configuration - using smaller dimension for local embeddings
EMBED_DIM = 384  # Smaller for local embeddings
INDEX_PATH = os.path.join(settings.BASE_DIR, "faiss_index.bin")

# Global variables - initialize as None
_index = None
_embeddings = None

def get_embeddings():
    """Get or create embeddings instance - with fallback"""
    global _embeddings
    if _embeddings is None:
        try:
            from langchain_openai import OpenAIEmbeddings
            _embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        except Exception as e:
            print(f"OpenAI embeddings failed: {e}. Using local fallback.")
            _embeddings = None
    return _embeddings

def load_index():
    """Load FAISS index from disk or create new one"""
    global _index
    if _index is None:
        if os.path.exists(INDEX_PATH):
            print("📁 Loading FAISS index from disk...")
            _index = faiss.read_index(INDEX_PATH)
        else:
            print("🆕 Creating new FAISS index...")
            _index = faiss.IndexFlatL2(EMBED_DIM)
    return _index

def save_index():
    """Save FAISS index to disk"""
    index = load_index()
    if index is not None:
        faiss.write_index(index, INDEX_PATH)
        print("💾 FAISS index saved to disk")

def simple_text_embedding(text: str) -> List[float]:
    """Improved local embedding using multiple text features"""
    import string
    import hashlib
    import re
    
    text = text.lower().strip()
    
    # Create a more sophisticated embedding
    embedding = [0.0] * EMBED_DIM
    
    # 1. Word frequency features (first 20 dimensions)
    words = re.findall(r'\b\w+\b', text)
    word_freq = {}
    for word in words[:50]:  # First 50 words only
        if len(word) > 2:  # Ignore very short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Distribute word frequencies across dimensions
    for i, (word, freq) in enumerate(list(word_freq.items())[:20]):
        if i < 20:
            embedding[i] = min(freq / 10.0, 1.0)
    
    # 2. Character distribution (next 26 dimensions)
    for char in string.ascii_lowercase:
        idx = 20 + (ord(char) - ord('a'))
        if idx < EMBED_DIM:
            embedding[idx] = text.count(char) / max(len(text), 1)
    
    # 3. Text length and structure features
    if len(text) > 0:
        embedding[46] = min(len(text) / 1000.0, 1.0)  # Normalized length
        embedding[47] = len(words) / 100.0  # Word count
        embedding[48] = len(set(words)) / max(len(words), 1)  # Vocabulary diversity
    
    # 4. Semantic keywords (positions 49-100)
    keywords = {
        'django': 49, 'python': 50, 'framework': 51, 'web': 52, 
        'development': 53, 'database': 54, 'admin': 55, 'interface': 56,
        'component': 57, 'reusable': 58, 'pluggability': 59, 'rapid': 60
    }
    
    for keyword, position in keywords.items():
        if position < EMBED_DIM:
            embedding[position] = text.count(keyword) / 10.0
    
    # 5. Hash-based deterministic component (remainder)
    text_hash = hashlib.md5(text.encode()).hexdigest()
    for i in range(100, EMBED_DIM):
        if i < EMBED_DIM:
            # Use different parts of hash for different dimensions
            hash_part = int(text_hash[(i-100)*2 % 32:(i-100)*2 % 32 + 2], 16)
            embedding[i] = (hash_part / 255.0) * 0.5  # Scale down
    
    # Normalize the embedding
    norm = (sum(x*x for x in embedding) ** 0.5) or 1
    embedding = [x / norm for x in embedding]
    
    return embedding

def index_document(title: str, text: str) -> Document:
    """
    Index a document using LOCAL embeddings only (no API calls)
    """
    # Create Document record
    document = Document.objects.create(title=title)
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    
    # Use local embeddings (no API calls)
    chunk_embeddings = [simple_text_embedding(chunk) for chunk in chunks]
    
    # Add to FAISS index and create DocumentChunk records
    index = load_index()
    
    for i, (chunk_text, embedding) in enumerate(zip(chunks, chunk_embeddings)):
        # Add to FAISS
        vector_id = index.ntotal
        embedding_array = np.array([embedding], dtype='float32')
        index.add(embedding_array)
        
        # Create database record
        DocumentChunk.objects.create(
            document=document,
            text=chunk_text,
            vector_id=vector_id
        )
    
    # Save index
    save_index()
    
    print(f"✅ Indexed {len(chunks)} chunks for document: {title}")
    return document

def search_docs(query: str, k: int = 4) -> List[str]:
    """
    Search for relevant document chunks with LOCAL embeddings
    """
    # Always load index first
    index = load_index()
    
    if index.ntotal == 0:
        print("❌ FAISS index is empty")
        return []
    
    print(f"🔍 Searching with index: {index.ntotal} vectors")
    
    # Generate query embedding locally
    query_embedding = simple_text_embedding(query)
    query_array = np.array([query_embedding], dtype='float32')
    
    # Search in FAISS
    distances, indices = index.search(query_array, k)
    
    print(f"   FAISS Results - Indices: {indices[0]}")
    print(f"   FAISS Results - Distances: {distances[0]}")
    
    # Get chunk texts from database
    results = []
    for vector_id in indices[0]:
        if vector_id != -1:  # -1 means no result
            try:
                chunk = DocumentChunk.objects.get(vector_id=vector_id)
                results.append(chunk.text)
                print(f"✅ Found chunk for vector_id {vector_id}")
            except DocumentChunk.DoesNotExist:
                print(f"❌ No chunk found for vector_id {vector_id}")
                continue
    
    print(f"📊 Final search results: {len(results)} chunks")
    return results

def get_index_stats():
    """Get statistics about the FAISS index"""
    index = load_index()
    return {
        "total_vectors": index.ntotal,
        "vector_dimension": index.d,
        "documents_count": Document.objects.count(),
        "chunks_count": DocumentChunk.objects.count()
    }