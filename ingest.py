"""
ingest.py — Load, chunk, and embed FAU policy documents into ChromaDB
Run once (or re-run to refresh): python ingest.py
"""

import os
import glob
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_DIR = "chroma_db"
DATA_DIRS = ["data/policies", "data/academics", "data/campus_life"]
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def load_documents():
    docs = []
    for data_dir in DATA_DIRS:
        for txt_path in glob.glob(os.path.join(data_dir, "**", "*.txt"), recursive=True):
            if os.path.basename(txt_path).upper() == "README.TXT":
                continue
            try:
                loader = TextLoader(txt_path, encoding="utf-8")
                loaded = loader.load()
                # Tag each doc with its source folder category
                category = os.path.basename(data_dir)
                for doc in loaded:
                    doc.metadata["category"] = category
                    doc.metadata["filename"] = os.path.basename(txt_path)
                docs.extend(loaded)
            except Exception as e:
                print(f"  [WARN] Could not load {txt_path}: {e}")

        for pdf_path in glob.glob(os.path.join(data_dir, "**", "*.pdf"), recursive=True):
            try:
                loader = PyPDFLoader(pdf_path)
                loaded = loader.load()
                category = os.path.basename(data_dir)
                for doc in loaded:
                    doc.metadata["category"] = category
                    doc.metadata["filename"] = os.path.basename(pdf_path)
                docs.extend(loaded)
            except Exception as e:
                print(f"  [WARN] Could not load {pdf_path}: {e}")

    return docs


def main():
    print("Loading documents...")
    docs = load_documents()
    print(f"  Loaded {len(docs)} documents")

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"  Created {len(chunks)} chunks")

    print(f"Loading embedding model ({EMBED_MODEL})...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"Embedding and storing in ChromaDB at ./{CHROMA_DIR}/ ...")
    # Wipe and recreate so re-runs don't duplicate
    import shutil
    if os.path.exists(CHROMA_DIR):
        shutil.rmtree(CHROMA_DIR)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectorstore.persist()
    print(f"Done! {len(chunks)} chunks embedded and saved to {CHROMA_DIR}/")


if __name__ == "__main__":
    main()
