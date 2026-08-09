PYTHON ?= python3
VENV ?= .venv
APP_HOST ?= 0.0.0.0
APP_PORT ?= 8000
OLLAMA_BASE_URL ?= http://localhost:11434
OLLAMA_MODEL ?= qwen2.5:0.5b

.PHONY: venv run test-ollama

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

run:
	$(VENV)/bin/uvicorn app.main:app --host $(APP_HOST) --port $(APP_PORT)

test-ollama:
	curl -s $(OLLAMA_BASE_URL)/api/tags
	@echo
	curl -s $(OLLAMA_BASE_URL)/api/generate \
		-H "Content-Type: application/json" \
		-d '{"model":"$(OLLAMA_MODEL)","prompt":"Reply with one short sentence about private AI.","stream":false}'
	@echo
