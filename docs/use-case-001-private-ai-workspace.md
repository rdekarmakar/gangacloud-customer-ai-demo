# Use Case 001 — Private AI Workspace on GangaCloud

## What this proves

A GangaCloud customer can run a private AI assistant on their own Ubuntu VM using FastAPI and Ollama.

## Tested environment

- GangaCloud Starter VM
- Ubuntu 24.04
- 1 vCPU
- 1 GB RAM
- 25 GB disk
- 2 GB swap
- Private IP only
- SSH ProxyJump access

## Tested successfully

- SSH access through ProxyJump
- Internet and DNS from VM
- Docker installation
- Ollama installation
- qwen2.5:0.5b local model
- FastAPI app
- Interactive browser UI at /demo
- Access through SSH tunnel

## Limitations

- Tiny model only
- Not suitable for production LLM hosting
- No public IPv4 yet
- No authentication in demo app
- Access through SSH tunnel only

## Product positioning

GangaCloud Starter VM is suitable for Linux, Docker, private development, small apps, and tiny AI experiments.

Larger AI Workspace plans are needed for serious local AI workloads.
