import os
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import PyPDF2
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create directory for vector store
VECTOR_STORE_DIR = Path("vector_store")
VECTOR_STORE_DIR.mkdir(exist_ok=True)

# Store conversation history
conversation_history = []
qa_chain = None

class Question(BaseModel):
    question: str

class ApiKey(BaseModel):
    api_key: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/set-api-key")
async def set_api_key(api_key: ApiKey):
    # Save API key to .env file
    with open(".env", "w") as f:
        f.write(f"OPENAI_API_KEY={api_key.api_key}")
    load_dotenv()
    return {"status": "success"}

@app.get("/check-api-key")
async def check_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    return {"hasKey": bool(api_key)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(str(file_path))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Split text into chunks
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        texts = text_splitter.split_text(text)

        # Create embeddings and store in Chroma
        embeddings = HuggingFaceEmbeddings()
        vector_store = Chroma.from_texts(
            texts, 
            embeddings,
            persist_directory=str(VECTOR_STORE_DIR)
        )
        vector_store.persist()

        # Initialize QA chain
        global qa_chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            ChatOpenAI(temperature=0),
            vector_store.as_retriever(),
            return_source_documents=True
        )

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_question(question: Question):
    if not qa_chain:
        raise HTTPException(status_code=400, detail="Upload een document eerst")

    try:
        # Get answer from QA chain
        result = qa_chain({"question": question.question, "chat_history": conversation_history})
        answer = result["answer"]

        # Update conversation history
        conversation_history.append((question.question, answer))

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summarize")
async def generate_summary():
    if not qa_chain:
        raise HTTPException(status_code=400, detail="Upload een document eerst")

    try:
        result = qa_chain({
            "question": "Maak een korte en duidelijke samenvatting van dit document.",
            "chat_history": []
        })
        return {"summary": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-faq")
async def generate_faq():
    if not qa_chain:
        raise HTTPException(status_code=400, detail="Upload een document eerst")

    try:
        result = qa_chain({
            "question": "Genereer een lijst met 5 veel voorkomende vragen en antwoorden over dit document.",
            "chat_history": []
        })
        return {"faq": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)