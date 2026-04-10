import os
import sys
from langchain_community.document_loaders import (
    PyPDFLoader, 
    DirectoryLoader, 
    TextLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "./data/" 
DB_PATH = "./vector_db"

FILE_LOADERS = {
    "pdf": (PyPDFLoader, "*.pdf"),
    "txt": (TextLoader, "*.txt"),
    "docx": (Docx2txtLoader, "*.docx"),
}

def create_vector_db():

    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"📁 '{DATA_PATH}' klasörü oluşturuldu. Lütfen dokümanlarınızı bu klasöre ekleyin.")
        sys.exit(1)
    
    all_documents = []
    
    print("📂 Dokümanlar yükleniyor...")
    
    for file_type, (loader_cls, glob_pattern) in FILE_LOADERS.items():
        try:
            loader = DirectoryLoader(
                DATA_PATH, 
                glob=glob_pattern, 
                loader_cls=loader_cls,
                show_progress=True
            )
            docs = loader.load()
            if docs:
                print(f"  📄 {len(docs)} adet {file_type.upper()} dosyası yüklendi")
                all_documents.extend(docs)
        except Exception as e:
            print(f"  ⚠️ {file_type.upper()} dosyaları yüklenirken hata: {e}")
    
    if not all_documents:
        print(f"❌ '{DATA_PATH}' klasöründe desteklenen doküman bulunamadı.")
        print("   Desteklenen formatlar: PDF, TXT, DOCX")
        sys.exit(1)
    
    print(f"\n📚 Toplam {len(all_documents)} doküman yüklendi.")
    
    # Metin bölme
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=250,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    texts = text_splitter.split_documents(all_documents)

    print(f"📄 Toplam {len(texts)} parça oluşturuldu.")

    print("🦙 Ollama embedding modeli yükleniyor...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print("💾 Vektör veritabanı oluşturuluyor...")
    
    if os.path.exists(DB_PATH):
        import shutil
        shutil.rmtree(DB_PATH)
        print("🗑️ Eski veritabanı temizlendi.")
    
    db = Chroma.from_documents(texts, embeddings, persist_directory=DB_PATH)
    print(f"✅ İşlem tamamlandı! Veritabanı hazır. ({len(texts)} vektör kaydedildi)")

if __name__ == "__main__":
    create_vector_db()
