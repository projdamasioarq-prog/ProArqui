import os
from io import BytesIO
from typing import Optional

import httpx
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

APP_NAME = "X5 AI Studio API"
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL", "").strip()
APP_API_KEY = os.getenv("APP_API_KEY", "")
MAX_BYTES = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}

origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
app = FastAPI(title=APP_NAME, version="1.0.0")
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
    return {"status": "ok", "service": APP_NAME, "configured": bool(HF_TOKEN and HF_ENDPOINT_URL)}

@app.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    model: str = Form("Qwen/Qwen-Image-Edit"),
    strength: float = Form(0.55),
    aspect_ratio: str = Form("original"),
    x_app_key: Optional[str] = Header(default=None, alias="X-App-Key"),
):
    if APP_API_KEY and x_app_key != APP_API_KEY:
        raise HTTPException(status_code=401, detail="Chave da aplicação inválida.")
    if not HF_TOKEN:
        raise HTTPException(status_code=503, detail="Backend sem HF_TOKEN. Configure o token nas variáveis de ambiente.")
    if not HF_ENDPOINT_URL:
        raise HTTPException(status_code=503, detail="Configure HF_ENDPOINT_URL com a URL de inferência compatível com edição de imagens.")
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Formato não suportado. Envie PNG, JPG ou WEBP.")
    if not prompt.strip() or len(prompt) > 4000:
        raise HTTPException(status_code=400, detail="O prompt deve conter entre 1 e 4000 caracteres.")
    if not 0.1 <= strength <= 1:
        raise HTTPException(status_code=400, detail="Intensidade fora do intervalo permitido.")
    if aspect_ratio not in {"original", "1:1", "4:3", "16:9", "3:4"}:
        raise HTTPException(status_code=400, detail="Proporção inválida.")

    raw = await image.read()
    if not raw or len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Imagem vazia ou maior que 10 MB.")

    # O endpoint configurado deve aceitar multipart/form-data com os campos
    # image e prompt. Consulte a documentação do provedor/modelo escolhido.
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "prompt": prompt.strip(),
        "model": model,
        "strength": str(strength),
        "aspect_ratio": aspect_ratio,
    }
    files = {"image": (image.filename or "input.png", raw, image.content_type)}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
            upstream = await client.post(HF_ENDPOINT_URL, headers=headers, data=data, files=files)
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="O provedor de IA excedeu o tempo limite.")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao acessar o provedor: {str(exc)}")

    if upstream.status_code >= 400:
        detail = upstream.text[:1200] or "O provedor recusou a solicitação."
        raise HTTPException(status_code=502, detail=f"Provedor de IA ({upstream.status_code}): {detail}")
    content_type = upstream.headers.get("content-type", "application/octet-stream")
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=502, detail="O provedor não retornou um arquivo de imagem. Confira o endpoint configurado.")
    return Response(
        content=upstream.content,
        media_type=content_type,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )
