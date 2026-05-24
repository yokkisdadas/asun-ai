import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL ve SUPABASE_KEY .env icinde tanimli olmali.")

app = FastAPI(
    title="Asun AI API",
    version="1.0.0",
    description="FastAPI tabanli, Supabase REST entegrasyonuna hazir API"
)


class MessageCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    content: str = Field(..., min_length=1, max_length=4000)


def supabase_headers() -> dict:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


@app.get("/")
async def root():
    return {
        "ok": True,
        "name": "Asun AI API",
        "message": "API calisiyor."
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/messages")
async def get_messages(limit: int = 20):
    url = f"{SUPABASE_URL}/rest/v1/messages"
    params = {
        "select": "*",
        "order": "created_at.desc",
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, headers=supabase_headers(), params=params)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Supabase veri cekme hatasi: {response.text}"
        )

    return response.json()


@app.post("/messages")
async def create_message(payload: MessageCreate):
    url = f"{SUPABASE_URL}/rest/v1/messages"
    body = {
        "username": payload.username,
        "content": payload.content,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(url, headers=supabase_headers(), json=body)

    if response.status_code >= 400:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Supabase kayit hatasi: {response.text}"
        )

    data = response.json()
    return {
        "ok": True,
        "message": "Kayit basarili.",
        "data": data,
    }
