# GangaCloud Customer AI Demo

This is a small production-style demo showing how a customer can run a private AI API on a GangaCloud Ubuntu VM with FastAPI and local Ollama.

The app exposes a lightweight HTTP API that calls Ollama on `localhost`. It does not require a public IPv4 address, authentication, a database, or Docker Compose.

## What this demo proves

- A private GangaCloud customer VM can host an AI API without exposing Ollama to the public internet.
- FastAPI can provide a clean customer-facing API while Ollama stays bound to the VM.
- Access can happen through SSH ProxyJump and local SSH tunnels.
- A small model such as `qwen2.5:0.5b` can run on a constrained VM for simple demos and smoke tests.

## VM requirements

Tested minimum VM:

- Ubuntu VM
- 1 vCPU
- 1 GB RAM
- 25 GB disk
- 2 GB swap
- Ollama listening at `http://localhost:11434`
- SSH access through ProxyJump

This size is intentionally small. It is suitable for a lightweight customer demo, not for high-throughput or multi-user AI workloads.

## Install Ollama

On the GangaCloud Ubuntu VM:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Confirm Ollama is running:

```bash
curl http://localhost:11434/api/tags
```

If needed, start or restart the service:

```bash
sudo systemctl enable ollama
sudo systemctl restart ollama
```

## Pull the tested model

```bash
ollama pull qwen2.5:0.5b
```

Quick direct test:

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:0.5b","prompt":"Reply with one short sentence about private AI.","stream":false}'
```

## Run the FastAPI app

Clone or copy this repo to the VM, then run:

```bash
make venv
make run
```

By default the app listens on `0.0.0.0:8000` and calls Ollama at `http://localhost:11434`.

Configuration is read from environment variables:

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:0.5b
export OLLAMA_TIMEOUT_SECONDS=45
export APP_HOST=0.0.0.0
export APP_PORT=8000
make run
```

## API endpoints

- `GET /health` returns app health and active Ollama settings.
- `GET /` returns basic demo metadata.
- `POST /ask` accepts JSON such as `{"question":"What is private AI?"}`.
- `GET /ask?q=...` is a simple browser-friendly ask endpoint.
- `GET /models` lists local Ollama models from `/api/tags`.

If Ollama is unavailable, the API returns a clean JSON error with HTTP `503`.

## Access through SSH tunnel

The VM has no public IPv4, so keep the app private and tunnel to it.

From your laptop:

```bash
ssh -J ubuntu@<PROXMOX_PUBLIC_IP> \
  -L 8000:localhost:8000 \
  ubuntu@<VM_PRIVATE_IP>
```

Keep that SSH session open. In another local terminal:

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/ask?q=Explain%20private%20AI%20in%20one%20sentence"
```

To test Ollama directly through a tunnel:

```bash
ssh -J ubuntu@<PROXMOX_PUBLIC_IP> \
  -L 11434:localhost:11434 \
  ubuntu@<VM_PRIVATE_IP>
```

Then:

```bash
curl http://localhost:11434/api/tags
```

## Limitations of the 1 GB VM

- Use small models only. `qwen2.5:0.5b` is the tested baseline.
- Expect slower responses than a larger AI workspace.
- Keep prompts short and request small outputs.
- Avoid concurrent traffic during demos.
- Swap helps stability but does not make the VM suitable for heavy inference.
- First responses may be slower while the model loads.

## Recommended larger AI workspace specs

For smoother customer demos and more realistic private AI workloads, use:

- 4+ vCPU
- 8 GB RAM minimum for small models
- 16 GB or more RAM for larger local models
- 50 GB or more disk
- GPU-enabled VM for larger models, lower latency, or concurrent users

## Local development

If you run the API on your laptop, Ollama must also be reachable locally or through a tunnel:

```bash
make venv
make run
```

See [curl-examples.md](curl-examples.md) for ready-to-run requests.
