# Ollama Setup Guide

This project uses Ollama to run LLMs locally for PDF parsing - **completely free, no API costs**.

## Installation

### macOS

```bash
brew install ollama
```

### Linux / WSL

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Download installer from: <https://ollama.com/download>

## Setup

### 1. Start Ollama service

```bash
ollama serve
```

### 2. Pull a model (choose one)

**Recommended - Fast & Lightweight (3B parameters):**

```bash
ollama pull llama3.2:3b
```

**Better Quality - Larger (8B parameters):**

```bash
ollama pull llama3.1:8b
```

**Highest Quality - Slow (70B parameters):**

```bash
ollama pull llama3.1:70b
```

### 3. Test it works

```bash
ollama run llama3.2:3b "Extract JSON from this: Name is John, Age 30"
```

## Usage in Pipeline

The pipeline automatically uses Ollama (default model: `llama3.2:3b`).

To change the model, edit `pdf_parser.py`:

```python
def parse_pdf_with_ollama(text_content: str, model: str = "llama3.1:8b"):
```

## Troubleshooting

### Error: "Ollama not running"

- Start Ollama: `ollama serve` (run in separate terminal)

**Slow performance:**

- Use smaller model: `llama3.2:3b` instead of `llama3.1:8b`
- Reduce PDF text length in `pdf_parser.py` (currently 4000 chars)

**Model not found:**

- Pull model first: `ollama pull llama3.2:3b`

## System Requirements

- **llama3.2:3b**: ~2GB RAM, fast on most laptops
- **llama3.1:8b**: ~8GB RAM, good balance
- **llama3.1:70b**: ~40GB RAM, requires powerful hardware

## API Endpoint

Ollama runs locally on: `http://localhost:11434`

No internet connection needed after models are downloaded.
