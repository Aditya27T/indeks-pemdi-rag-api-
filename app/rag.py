import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Settings
PDF_PATH = os.getenv("PDF_PATH", "/data/2026permenpanrb008.pdf")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "4"))
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

# Global variables
vector_store = None
retriever = None

def init_rag():
    global vector_store, retriever
    
    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    import chromadb
    chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    
    vector_store = Chroma(
        client=chroma_client,
        collection_name="pemdi_docs",
        embedding_function=embeddings
    )
    
    # Check if documents are already indexed
    collection = chroma_client.get_or_create_collection("pemdi_docs")
    count = collection.count()
    
    if count == 0:
        print(f"Index is empty. Ingesting PDF from {PDF_PATH}...")
        try:
            loader = PyPDFLoader(PDF_PATH)
            pages = loader.load()
            
            # Use custom separators as suggested
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["Indikator", "Pasal", "BAB", "\n\n", "\n", " ", ""]
            )
            
            # Prepare passages with prefix
            docs = text_splitter.split_documents(pages)
            for doc in docs:
                doc.page_content = f"passage: {doc.page_content}"
                
            print(f"Split into {len(docs)} chunks. Indexing into ChromaDB...")
            vector_store.add_documents(docs)
            print("Indexing completed!")
        except Exception as e:
            print(f"Error during ingestion: {e}")
            raise e
    else:
        print(f"Found {count} chunks in ChromaDB. Skipping ingestion.")
        
    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})

def get_retriever():
    return retriever

def get_documents_count():
    try:
        import chromadb
        chroma_client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = chroma_client.get_collection("pemdi_docs")
        return collection.count()
    except:
        return 0
