# X5 AI Studio

Aplicação de edição de imagens por IA. Frontend estático para GitHub Pages e backend FastAPI separado, com token Hugging Face mantido somente no servidor.

## Estrutura
- `index.html`, `assets/`: interface web.
- `backend/main.py`: API de edição com Hugging Face Inference Providers.
- `backend/requirements.txt`: dependências do backend.
- `render.yaml`: configuração inicial para deploy do backend no Render.
- `.github/workflows/pages.yml`: publicação automática do frontend no GitHub Pages.

## Publicação

### 1. GitHub Pages
1. No repositório, abra **Settings → Pages**.
2. Em Build and deployment, selecione **GitHub Actions**.
3. O workflow publica a raiz do repositório. URL esperada: `https://projdamasioarq-prog.github.io/ProArqui/`.

### 2. Backend
1. Crie um serviço web no Render apontando para este repositório.
2. Configure **Root Directory** como `backend`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Configure as variáveis `HF_TOKEN` (token Hugging Face com permissão Inference Providers), `HF_MODEL` (padrão `Qwen/Qwen-Image-Edit`), `HF_PROVIDER` (padrão `auto`) e `ALLOWED_ORIGINS` (URL do GitHub Pages).
6. Opcional: configure `APP_API_KEY` e informe a mesma chave em Settings dentro do X5.

**Nunca coloque HF_TOKEN no JavaScript, no GitHub Pages ou em commits.**

### 3. Conectar a interface
Abra o X5 → Settings → informe a URL pública do backend e, se configurada, a chave da aplicação.

## Notas
- O modelo padrão é Qwen Image Edit via Hugging Face Inference Providers; disponibilidade, provedor, permissões e custos dependem da conta e do modelo.
- Os presets de estilo são instruções de prompt, não pesos LoRA. LoRAs reais exigem um endpoint/modelo que os carregue explicitamente.
- GitHub Pages hospeda somente o frontend; não executa Python nem mantém segredos.
- O backend valida formato e tamanho do arquivo e limita parâmetros para reduzir abuso.
