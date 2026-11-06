import os
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from huggingface_hub import InferenceClient

APP_NAME = "X5 AI Studio API"
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_PROVIDER = os.getenv("HF_PROVIDER", "fal-ai")
APP_API_KEY = os.getenv("APP_API_KEY", "")
MAX_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_MODELS = {"Qwen/Qwen-Image-Edit"}

origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
app = FastAPI(title=APP_NAME, version="1.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-App-Key"],
)

@app.get("/")
def root():
    return {"service": APP_NAME, "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME, "configured": bool(HF_TOKEN)}

@app.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form("Qwen/Qwen-Image-Edit"),
    x_app_key: Optional[str] = Header(default=None, alias="X-App-Key"),
):
    if APP_API_KEY and x_app_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Chave da aplicação inválida.")
    if not HF_TOKEN:
        raise HTTPException(status_code=503, detail="Backend sem HF_TOKEN. Configure o token no ambiente do servidor.")
    if model not in ALLOWED_MODELS:
        raise HTTPException(status_code=400, detail="Modelo não habilitado nesta versão.")
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Formato não suportado. Envie PNG, JPG ou WEBP.")
    if not prompt.strip() or len(prompt) > 4000:
        raise HTTPException(status_code=400, detail="O prompt deve conter entre 1 e 4000 caracteres.")

    raw = await image.read()
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Imagem vazia ou maior que 10 MB.")

    try:
        client = InferenceClient(provider=HF_PROVIDER, api_key=HF_TOKEN, timeout=300)
        edited = client.image_to_image(
            raw,
            prompt=prompt.strip(),
            model=model,
        )
        output = BytesIO()
        edited.save(output, format="PNG")
        return Response(
            content=output.getvalue(),
            media_type="image/png",
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
    except Exception as exc:
        # Avoid returning credentials or internal request headers to the browser.
        message = str(exc)[:700]
        raise HTTPException(status_code=502, detail=f"Falha na inferência ({HF_PROVIDER}): {message}")
