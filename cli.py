import typer
import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from core.engine import MaxwellEngine

app = typer.Typer(help="Maxwell Engine CLI (Zero-Hallucination Edition)")

def download_model_if_needed(model_input: str) -> str:
    """
    TR: Eğer model_input bir lokal dosya (örn: model.gguf) ise doğrudan döndürür.
    TR: Eğer bir HuggingFace repo'su ise (örn: Qwen/Qwen2.5-0.5B-Instruct-GGUF) indirip lokal yolunu döndürür.
    
    EN: If model_input is a local file (e.g., model.gguf), it returns it directly.
    EN: If it's a HuggingFace repo, it downloads it and returns the local path.
    """
    if os.path.exists(model_input):
        return model_input
        
    typer.secho(f"Local model not found. Downloading/checking via HuggingFace: {model_input}", fg=typer.colors.YELLOW)
    try:
        # TR: Varsayılan dosya adı (örnek)
        # TR: Kullanıcı genelde repo_id ve filename'i CLI'dan tam veremeyebilir.
        # TR: Basitlik adına, eğer "repo_id:filename" formatında verirse:
        # EN: Default filename (example)
        # EN: Users might not provide the exact repo_id and filename via CLI.
        # EN: For simplicity, if provided in "repo_id:filename" format:
        if ":" in model_input:
            repo_id, filename = model_input.split(":")
        else:
            typer.secho("Format must be 'repo_id:filename.gguf' when downloading from HuggingFace.", fg=typer.colors.RED)
            typer.secho("Example: Qwen/Qwen2.5-1.5B-Instruct-GGUF:qwen2.5-1.5b-instruct-q4_k_m.gguf", fg=typer.colors.RED)
            raise typer.Exit(code=1)
            
        model_path = hf_hub_download(repo_id=repo_id, filename=filename)
        typer.secho(f"Model ready: {model_path}", fg=typer.colors.GREEN)
        return model_path
    except Exception as e:
        typer.secho(f"Model download error: {e}", fg=typer.colors.RED)
        typer.secho("Hint: Ensure the HuggingFace repo ID and filename are correct.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

@app.command()
def analyze(
    path: str = typer.Argument(..., help="Path to the file or directory to analyze"),
    model: str = typer.Option(
        "Qwen/Qwen2.5-1.5B-Instruct-GGUF:qwen2.5-1.5b-instruct-q4_k_m.gguf", 
        "--model", "-m", 
        help="Lokal path veya HF 'repo_id:filename'"
    )
):
    """
    Analyzes a given file using the Maxwell Engine (Llama-cpp Backend).
    """
    target_path = Path(path)
    
    if not target_path.exists():
        typer.secho(f"Error: Path '{path}' does not exist.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    content = ""
    if target_path.is_file():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            typer.secho(f"Error reading file: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)
    else:
        typer.secho("Directory analysis is not yet fully supported. Please provide a file.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)
        
    model_path = download_model_if_needed(model)
        
    typer.secho("\n[*] Starting Maxwell Engine...", fg=typer.colors.CYAN)
    typer.secho(f"[*] Target: {target_path.name}", fg=typer.colors.CYAN)
    typer.secho("[*] Initializing Thermodynamic Matrix (Llama-CPP), please wait...\n", fg=typer.colors.CYAN)
    
    engine = MaxwellEngine(model_path=model_path)
    result_json = engine.analyze(content)
    
    typer.echo(result_json)

if __name__ == "__main__":
    app()
