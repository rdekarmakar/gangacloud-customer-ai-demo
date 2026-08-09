import os
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from requests import RequestException


BASE_DIR = Path(__file__).resolve().parent
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))

app = FastAPI(
    title="GangaCloud Private AI API Demo",
    description="A lightweight FastAPI wrapper around a local Ollama model.",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=4000)
    model: str | None = Field(default=None, description="Optional Ollama model override.")


class AskResponse(BaseModel):
    question: str
    answer: str
    model: str


class HealthResponse(BaseModel):
    status: str
    ollama_base_url: str
    default_model: str


class ModelsResponse(BaseModel):
    models: list[str]


def json_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def ollama_get(path: str) -> Any:
    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}{path}",
            timeout=min(10, OLLAMA_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
        return response.json()
    except RequestException:
        raise OllamaUnavailableError
    except ValueError:
        raise OllamaBadResponseError


def ollama_generate(question: str, model: str) -> str:
    payload = {
        "model": model,
        "prompt": question,
        "stream": False,
        # Keep the demo modest for small VMs. Customers can tune this later.
        "options": {"num_predict": 256},
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
    except RequestException:
        raise OllamaUnavailableError
    except ValueError:
        raise OllamaBadResponseError

    if not isinstance(data, dict):
        raise OllamaBadResponseError

    answer = data.get("response")
    if not isinstance(answer, str):
        raise OllamaBadResponseError
    return answer.strip()


class OllamaUnavailableError(Exception):
    pass


class OllamaBadResponseError(Exception):
    pass


@app.exception_handler(OllamaUnavailableError)
async def ollama_unavailable_handler(_request, _exc):
    return json_error(
        503,
        "ollama_unavailable",
        "Ollama is not reachable from the FastAPI app. Confirm it is running locally.",
    )


@app.exception_handler(OllamaBadResponseError)
async def ollama_bad_response_handler(_request, _exc):
    return json_error(
        502,
        "ollama_bad_response",
        "Ollama returned an unexpected response.",
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        ollama_base_url=OLLAMA_BASE_URL,
        default_model=OLLAMA_MODEL,
    )


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "name": "GangaCloud Private AI API Demo",
        "description": "FastAPI calling local Ollama on a private GangaCloud Ubuntu VM.",
        "endpoints": {
            "health": "GET /health",
            "ask_post": "POST /ask",
            "ask_get": "GET /ask?q=...",
            "models": "GET /models",
            "demo": "GET /demo",
        },
    }


@app.get("/demo", include_in_schema=False)
def demo_page() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/ask", response_model=AskResponse)
def ask_post(request: AskRequest) -> AskResponse:
    model = request.model or OLLAMA_MODEL
    answer = ollama_generate(request.question, model)
    return AskResponse(question=request.question, answer=answer, model=model)


@app.get("/ask", response_model=AskResponse)
def ask_get(q: str = Query(..., min_length=1, max_length=4000)) -> AskResponse:
    answer = ollama_generate(q, OLLAMA_MODEL)
    return AskResponse(question=q, answer=answer, model=OLLAMA_MODEL)


@app.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    data = ollama_get("/api/tags")
    if not isinstance(data, dict):
        raise OllamaBadResponseError

    model_names = [
        item["name"]
        for item in data.get("models", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    ]
    return ModelsResponse(models=model_names)
