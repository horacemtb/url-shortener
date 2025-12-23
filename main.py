from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import sqlite3
import string
import random
from typing import Dict
from database import Database
import contextlib
import uvicorn

app = FastAPI(
    title="URL Shortener Service",
    description="A simple URL shortening service with SQLite backend",
    version="1.0.0"
)

db = Database()

class URLRequest(BaseModel):
    url: HttpUrl

class URLStatsResponse(BaseModel):
    short_id: str
    full_url: str
    clicks: int
    short_url: str

def generate_short_id(length: int = 6) -> str:
    """Generate a unique short id"""
    chars = string.ascii_letters + string.digits
    while True:
        short_id = ''.join(random.choices(chars, k=length))
        if not url_exists(short_id):
            return short_id

def url_exists(short_id: str) -> bool:
    """Check if a short id already exists"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM urls WHERE short_id = ?", (short_id,))
        return cursor.fetchone() is not None

def get_base_url() -> str:
    """Get base URL"""
    return "http://127.0.0.1:8000"

@app.post("/shorten", response_model=Dict[str, str])
def shorten_url(request: URLRequest):
    """Create a short URL for provided long URL"""
    short_id = generate_short_id()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO urls (short_id, full_url) VALUES (?, ?)",
            (short_id, str(request.url))
        )
        conn.commit()
    
    return {"short_url": f"{get_base_url()}/{short_id}"}

@app.get("/health")
def health_check():
    """Health probe endpoint"""
    return {"status": "healthy"}

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    """Redirect to original URL using short id"""
    with db.get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE urls SET clicks = clicks + 1 WHERE short_id = ? RETURNING full_url",
            (short_id,)
        )
        result = cursor.fetchone()
        conn.commit()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Short URL '{short_id}' not found"
            )
        
        return RedirectResponse(url=result[0])

@app.get("/stats/{short_id}", response_model=URLStatsResponse)
def get_url_stats(short_id: str):
    """Get stats for shortened URL"""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT short_id, full_url, clicks FROM urls WHERE short_id = ?",
            (short_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Short URL '{short_id}' not found"
            )
        
        return URLStatsResponse(
            short_id=result[0],
            full_url=result[1],
            clicks=result[2],
            short_url=f"{get_base_url()}/{result[0]}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)