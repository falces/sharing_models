import json
import os
from pathlib import Path

def get_model_mapping():
    # Detect the base directory depending on the OS
    if os.name == 'nt':  # Windows
        base_path = Path.home() / ".ollama" / "models"
    else:  # Linux/Mac
        base_path = Path.home() / ".ollama" / "models"

    manifests_dir = base_path / "manifests" / "registry.ollama.ai" / "library"

    if not manifests_dir.exists():
        print(f"Manifests directory not found at: {manifests_dir}")
        return

    print(f"{'MODEL (TAG)':<30} | {'BLOB FILE (GGUF)'}")
    print("-" * 105)

    models = []

    # Iterate over the model folders
    for model_dir in manifests_dir.iterdir():
        if not model_dir.is_dir():
            continue

        model_name = model_dir.name

        # Iterate over the tags within each model (latest, q4_0, etc.)
        for tag_file in model_dir.iterdir():
            if not tag_file.is_file():
                continue

            tag_name = tag_file.name

            try:
                with open(tag_file, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)

                # Find the layer that contains the model weights
                for layer in manifest.get("layers", []):
                    if layer.get("mediaType") == "application/vnd.ollama.image.model":
                        digest = layer.get("digest", "")
                        # Ollama names its files by replacing ':' with '-'
                        blob_filename = digest.replace(":", "-")

                        print(f"{model_name + ':' + tag_name:<30} | {blob_filename}")
                        models.append({
                            "model_name": model_name,
                            "tag_name": tag_name,
                            "blob_filename": blob_filename,
                        })
                        break

            except json.JSONDecodeError:
                print(f"Error decoding JSON in {model_name}:{tag_name}")
            except Exception as e:
                print(f"Error processing {model_name}:{tag_name} - {e}")

    return base_path, models


def create_symlinks(base_path, models):
    answer = input(
        "\nDo you want to create symlinks to share these models with other "
        "engines (LM Studio, llama.cpp, etc.)? [y/N]: "
    ).strip().lower()

    if answer not in ("y", "yes", "s", "si", "sí"):
        return

    default_destination = Path.home() / "LLM Models"
    destination_answer = input(f"Destination folder [{default_destination}]: ").strip()
    destination = Path(destination_answer).expanduser() if destination_answer else default_destination

    destination.mkdir(parents=True, exist_ok=True)

    created = 0
    for model in models:
        source = base_path / "blobs" / model["blob_filename"]

        if not source.exists():
            print(f"Warning: blob not found {source}, skipping")
            continue

        model_label = f"{model['model_name']}-{model['tag_name']}"

        links = [
            destination / f"{model_label}.gguf",
            destination / "lmstudio-community" / f"{model_label}-GGUF" / f"{model_label}.gguf",
        ]

        for link in links:
            link.parent.mkdir(parents=True, exist_ok=True)

            if link.exists() or link.is_symlink():
                link.unlink()

            link.symlink_to(source)
            print(f"Link created: {link} -> {source}")
            created += 1

    print(f"\n{created} link(s) created in {destination}")

if __name__ == "__main__":
    result = get_model_mapping()
    if result:
        base_path, models = result
        create_symlinks(base_path, models)
