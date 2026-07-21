# Ollama Model Mapper

A small Python script that maps your local [Ollama](https://ollama.com) models to their underlying blob files, and optionally creates symlinks so you can use those same weights with other LLM engines (LM Studio, llama.cpp, etc.) without duplicating gigabytes of data on disk.

## Why

Ollama stores model weights as content-addressed blobs (e.g. `sha256-89b...`) under `~/.ollama/models/blobs`, with no human-readable filename. Other tools expect a `.gguf` file named after the model. This script bridges the gap by reading Ollama's manifests and creating symlinks with proper names, pointing back to the original blobs — no extra disk space used.

## Requirements

- Python 3.8+
- No external dependencies (only the standard library: `json`, `os`, `pathlib`)
- Ollama installed locally with at least one pulled model

## Usage

```bash
python3 ollama_mapper.py
```

The script will:

1. Scan `~/.ollama/models/manifests/registry.ollama.ai/library` and print a table mapping each `model:tag` to its blob filename.
2. Ask if you want to create symlinks to share these models with other engines.
3. If you answer yes, ask for a destination folder (defaults to `~/LLM Models`).

For each model, two symlinks are created in the destination folder:

- A flat one: `<model>-<tag>.gguf`
- An LM Studio–compatible one, following its expected repo layout: `lmstudio-community/<model>-<tag>-GGUF/<model>-<tag>.gguf`

Both point to the same original blob, so re-running the script is safe — existing links are simply overwritten.

### Example

```
MODEL (TAG)                    | BLOB FILE (GGUF)
---------------------------------------------------------------------------------------------------
llama3:latest                  | sha256-89b...

Do you want to create symlinks to share these models with other engines (LM Studio, llama.cpp, etc.)? [y/N]: y
Destination folder [~/LLM Models]: 
Link created: ~/LLM Models/llama3-latest.gguf -> ~/.ollama/models/blobs/sha256-89b...
Link created: ~/LLM Models/lmstudio-community/llama3-latest-GGUF/llama3-latest.gguf -> ~/.ollama/models/blobs/sha256-89b...

2 link(s) created in ~/LLM Models
```

## Platform notes

Symlinks are used instead of copying files, so this only works on filesystems/OSes that support them (macOS, Linux, and Windows with the appropriate permissions/developer mode).

## License

MIT
