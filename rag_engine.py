"""
AIChat Pro — RAG Engine (Simple & Robust Version)
Custom RAG implementation without complex LangChain chains
"""

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from groq import Groq

from config import config


class RAGEngine:
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY not found.")
        
        # FREE local embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Groq client (direct API, no LangChain)
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
        
        self.vectorstore = None
        self.chat_history: List[dict] = []
        
        os.makedirs(config.DOCS_DIR, exist_ok=True)
        os.makedirs(config.VECTORSTORE_DIR, exist_ok=True)
    
    def load_documents(self, file_paths: List[str]) -> int:
        """Load and index documents"""
        documents = []
        
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            
            try:
                if ext == ".pdf":
                    loader = PyPDFLoader(path)
                elif ext in [".txt", ".md"]:
                    loader = TextLoader(path, encoding="utf-8")
                else:
                    continue
                
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"⚠️ Error loading {path}: {e}")
        
        if not documents:
            raise ValueError("No documents loaded.")
        
        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(documents)
        
        # Build vector store
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        self.vectorstore.save_local(config.VECTORSTORE_DIR)
        
        return len(chunks)
    
    def load_existing(self) -> bool:
        """Try to load existing vector store"""
        try:
            if os.path.exists(f"{config.VECTORSTORE_DIR}/index.faiss"):
                self.vectorstore = FAISS.load_local(
                    config.VECTORSTORE_DIR,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
        except Exception as e:
            print(f"⚠️ Could not load existing vectorstore: {e}")
        return False
    
    def query(self, question: str) -> dict:
        """Query documents using RAG"""
        if self.vectorstore is None:
            raise ValueError("❌ No documents loaded. Please upload files first.")
        
        # Step 1: Retrieve relevant chunks
        docs = self.vectorstore.similarity_search(question, k=4)
        
        if not docs:
            return {
                "answer": "I couldn't find relevant information in the documents.",
                "sources": []
            }
        
        # Step 2: Build context
        context = "\n\n".join([
            f"[Source: {os.path.basename(d.metadata.get('source', 'Unknown'))}"
            f" | Page {d.metadata.get('page', 'N/A')}]\n{d.page_content}"
            for d in docs
        ])
        
        # Step 3: Build messages with history
        messages = [
            {
                "role": "system",
                "content": (
                    "You are AIChat Pro, a helpful assistant that answers questions "
                    "based on the provided document context. "
                    "Use only the information from the context to answer. "
                    "If the answer is not in the context, politely say so. "
                    "Cite the source when relevant."
                )
            }
        ]
        
        # Add recent chat history
        for msg in self.chat_history[-6:]:
            messages.append(msg)
        
        # Add current question with context
        messages.append({
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        })
        
        # Step 4: Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS,
        )
        
        answer = response.choices[0].message.content
        
        # Save to history
        self.chat_history.append({"role": "user", "content": question})
        self.chat_history.append({"role": "assistant", "content": answer})
        
        # Build sources list
        sources = [
            {
                "page": doc.metadata.get("page", "N/A"),
                "source": doc.metadata.get("source", "N/A"),
                "content": doc.page_content[:200] + "...",
            }
            for doc in docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
        }
    
    def clear(self):
        """Clear vectorstore and history"""
        self.vectorstore = None
        self.chat_history = []
        
        if os.path.exists(config.VECTORSTORE_DIR):
            for f in os.listdir(config.VECTORSTORE_DIR):
                try:
                    os.remove(os.path.join(config.VECTORSTORE_DIR, f))
                except Exception:
                    pass