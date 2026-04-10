from fastapi import FastAPI, HTTPException, Body, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from system import CorporateChatbot
import uvicorn
import logging
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


env_key = os.getenv("ADMIN_API_KEY")
if env_key:
    ADMIN_API_KEY = env_key
else:
    ADMIN_API_KEY = secrets.token_hex(16)


app = FastAPI(
    title="Kurumsal RAG Asistanı API",
    description="Kurumsal dokümanlar üzerinde RAG tabanlı soru-cevap sistemi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    bot = CorporateChatbot()
    logger.info("✅ Chatbot başarıyla başlatıldı")
except Exception as e:
    logger.error(f"❌ Chatbot başlatılamadı: {e}")
    bot = None

class QueryRequest(BaseModel):
    question: str

class PromptUpdateRequest(BaseModel):
    new_prompt: str

class ModelUpdateRequest(BaseModel):
    new_model: str

# Header üzerinden API Key kontrolü
def verify_admin_key(x_api_key: str = Header(None)):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Geçersiz veya eksik API anahtarı")
    return True

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/health")
def health_check():
    return {
        "status": "healthy" if bot else "unhealthy",
        "database": "connected" if bot else "disconnected"
    }

@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Soru boş olamaz.")
    
    try:
        logger.info(f"📩 Yeni soru: {request.question[:50]}...")
        response = bot.ask(request.question)
        return {
            "response": response["answer"],
            "sources": response["sources"]
        }
    except Exception as e:
        logger.error(f"❌ Hata oluştu: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")

# Sadece Admin Key ile erişilebilir
@app.post("/admin/update-prompt")
async def update_prompt(request: PromptUpdateRequest, authorized: bool = Depends(verify_admin_key)):
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    if not request.new_prompt or not request.new_prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt boş olamaz.")
    try:
        bot.update_prompt(request.new_prompt)
        logger.info("✅ Sistem promptu güncellendi (admin)")
        return {"status": "success", "message": "Sistem promptu güncellendi."}
    except Exception as e:
        logger.error(f"❌ Prompt güncellenirken hata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Herkes okuyabilir (Mevcut promptu görmek için)
@app.get("/admin/current-prompt")
async def get_current_prompt():
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    return {"prompt": bot.get_editable_prompt()}

# Admin: Modeli değiştir
@app.post("/admin/update-model")
async def update_model(request: ModelUpdateRequest, authorized: bool = Depends(verify_admin_key)):
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    if not request.new_model or not request.new_model.strip():
        raise HTTPException(status_code=400, detail="Model adı boş olamaz.")
    try:
        bot.update_model(request.new_model)
        logger.info(f"✅ Model güncellendi (admin): {request.new_model}")
        return {"status": "success", "message": f"Model '{request.new_model}' olarak güncellendi."}
    except Exception as e:
        logger.error(f"❌ Model güncellenirken hata: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mevcut modeli öğren
@app.get("/admin/current-model")
async def get_current_model():
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    return {"model": bot.get_current_model()}

# Hafıza temizleme (Opsiyonel admin koruması eklenebilir) :D
@app.post("/admin/clear-memory")
async def clear_memory():
    if not bot:
        raise HTTPException(status_code=503, detail="Chatbot servisi kullanılamıyor.")
    try:
        bot.memory.clear()
        logger.info("🧹 Sohbet hafızası temizlendi")
        return {"status": "success", "message": "Sohbet hafızası temizlendi."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)