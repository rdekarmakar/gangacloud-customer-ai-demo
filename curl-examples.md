# Curl Examples

These examples assume the FastAPI app is reachable on `http://localhost:8000`.

## Health check

```bash
curl http://localhost:8000/health
```

## Ask endpoint

GET:

```bash
curl "http://localhost:8000/ask?q=What%20is%20private%20AI%3F"
```

POST:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Explain private AI in one sentence."}'
```

## Ollama direct tunnel test

When tunneling Ollama itself from the VM to your laptop:

```bash
ssh -J ubuntu@<PROXMOX_PUBLIC_IP> \
  -L 11434:localhost:11434 \
  ubuntu@<VM_PRIVATE_IP>
```

Then, from another local terminal:

```bash
curl http://localhost:11434/api/tags
```

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:0.5b","prompt":"Say hello from a private VM.","stream":false}'
```
