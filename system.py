from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DB_PATH = "./vector_db"

import threading
PROMPT_TXT_PATH = "prompt.txt"
class CorporateChatbot:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(
                f"Vektör veritabanı bulunamadı: {DB_PATH}. "
                "Lütfen önce 'python ingest.py' komutunu çalıştırın."
            )
        self.db = Chroma(persist_directory=DB_PATH, embedding_function=self.embeddings)
        collection_count = self.db._collection.count()
        if collection_count == 0:
            raise ValueError("Vektör veritabanı boş. Lütfen doküman ekleyin.")
        logger.info(f"📚 Veritabanında {collection_count} vektör bulundu")
        self.retriever = self.db.as_retriever(search_kwargs={"k": 3})
        self.current_model = "gpt-oss:120b-cloud"  # Varsayılan model
        self.llm = ChatOllama(
            model=self.current_model,
            temperature=0.1
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key='answer'
        )
        self._prompt_lock = threading.Lock()
        self.protected_prompt = """
CEVAP FORMATI:
- ASLA markdown kullanma (**, ##, ***, - gibi işaretler YASAK)
- Düz metin yaz
- Listeler için numaralama yap (1. 2. 3.)
- Kısa ve öz cevap ver, maksimum 100 kelime

Bağlam: {context}

Soru: {question}

Cevap:"""
        self.editable_prompt = self._load_editable_prompt()
        self.qa_chain = self._build_chain()

    def _load_editable_prompt(self):
        if os.path.exists(PROMPT_TXT_PATH):
            with open(PROMPT_TXT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def _save_editable_prompt(self, new_prompt_text):
        with self._prompt_lock:
            with open(PROMPT_TXT_PATH, "w", encoding="utf-8") as f:
                f.write(new_prompt_text)

    def _get_full_prompt(self):
        return self.editable_prompt + "\n" + self.protected_prompt

    def _build_chain(self):
        PROMPT = PromptTemplate(
            template=self._get_full_prompt(),
            input_variables=["context", "question"]
        )
        return ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )

    def update_prompt(self, new_prompt_text):
        self.editable_prompt = new_prompt_text
        self._save_editable_prompt(new_prompt_text)
        self.qa_chain = self._build_chain()
        return True

    def get_editable_prompt(self):
        return self.editable_prompt

    def update_model(self, new_model):
        """Yeni bir model adıyla LLM'i günceller"""
        self.current_model = new_model
        self.llm = ChatOllama(
            model=self.current_model,
            temperature=0.1
        )
        self.qa_chain = self._build_chain()
        logger.info(f"✅ Model güncellendi: {new_model}")
        return True

    def get_current_model(self):
        """Mevcut modeli döndürür"""
        return self.current_model

    def ask(self, query):
        result = self.qa_chain.invoke({"question": query})
        answer = result["answer"]
        return {"answer": answer, "sources": []}
        return {"answer": answer, "sources": []}