# X5 AI Studio

Aplicação independente de edição de imagens por IA. Frontend estático no GitHub Pages e API FastAPI separada. O token Hugging Face fica somente no servidor.

## Estrutura
- `index.html`, `assets/`: interface web.
- `backend/main.py`: API de edição com Hugging Face Inference Providers.
- `backend/requirements.txt`: dependências.
- `render.yaml`: configuração inicial de deploy no Render.
- `.github/workflows/pages.yml`: publicação automática do frontend.

## 1. GitHub Pages
1. Abra **Settings → Pages** neste repositório.
2. Em **Build and deployment**, selecione **GitHub Actions**.
3. O workflow publica a raiz do repositório.
4. URL esperada: `https://projdamasioarq-prog.github.io/ProArqui/`.

## 2. Backend
1. Crie um serviço web no Render apontando para este repositório.
2. Defina **Root Directory** como `backend`.
3. Build: `pip install -r requirements.txt`.
4. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
5. Configure `HF_TOKEN` como variável secreta e `HF_PROVIDER=fal-ai`.
6. Opcionalmente configure `APP_API_KEY` com uma chave longa e aleatória.
7. Configure `ALLOWED_ORIGINS=https://projdamasioarq-prog.github.io`.

A API usa `huggingface_hub.InferenceClient.image_to_image` com o modelo `Qwen/Qwen-Image-Edit`. O provedor precisa oferecer esse modelo e a conta precisa ter acesso/permissão de Inference Providers. Consulte a documentação do modelo e dos provedores antes de escolher outro provedor.

**Nunca coloque HF_TOKEN no JavaScript, no GitHub Pages ou em commits.**

## 3. Conectar a interface
Abra o X5 → Configurações → informe a URL pública do backend e, se configurada, a chave da aplicação.

## Limitações desta versão
- O modelo Qwen Image Edit é o motor de edição. Disponibilidade, filas e custos dependem do provedor/conta.
- Os botões de estilo são presets de prompt, não pesos LoRA. LoRAs reais exigem suporte explícito do endpoint.
- GitHub Pages hospeda somente o frontend; não executa Python nem guarda segredos.
- O controle de intensidade e proporção está reservado para integração com modelos que aceitem esses parâmetros. O modelo padrão mantém a proporção de entrada conforme o comportamento do provedor.
