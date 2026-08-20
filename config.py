import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Set up module resolution paths
ROOT_DIR = Path(__file__).parent.resolve()
dirs_to_add = [
    ROOT_DIR,
    ROOT_DIR / "1_data",
    ROOT_DIR / "2_vectorstore",
    ROOT_DIR / "3_agents",
    ROOT_DIR / "4_graph",
    ROOT_DIR / "5_api",
    ROOT_DIR / "6_frontend",
]

for d in dirs_to_add:
    d_str = str(d)
    if d_str not in sys.path:
        sys.path.insert(0, d_str)

# Alias 3_agents as agents if accessed via package notation
agents_dir = ROOT_DIR / "3_agents"
if agents_dir.exists():
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("agents", agents_dir / "__init__.py")
        if spec:
            agents_mod = importlib.util.module_from_spec(spec)
            sys.modules["agents"] = agents_mod
    except Exception:
        pass

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./2_vectorstore/chroma_db")
JRC_API_BASE = os.getenv("JRC_API_BASE", "https://data.jrc.ec.europa.eu/api/3")
