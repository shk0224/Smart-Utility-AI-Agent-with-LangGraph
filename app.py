"""FastAPI entry point. Start with: python app.py"""
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from backend import run_utility_agent

app = FastAPI(title="Smart Utility AI Agent")
BASE_DIR = Path(__file__).resolve().parent


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.post("/api/ask")
def ask(request: QuestionRequest):
    try:
        return run_utility_agent(request.question)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
