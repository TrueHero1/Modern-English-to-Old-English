# Temporary patch — run this instead to see the full Ollama response structure
import requests, json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:8b"

resp = requests.post(
    OLLAMA_URL,
    json={
        "model":  MODEL,
        "prompt": "Translate into Old English: The king rides.",
        "stream": False,
        "options": {
            "num_predict": -1  # Fixed: No longer limits the output to 512 tokens
        },
    },
    timeout=120,
)

data = resp.json()
print("=== ALL RESPONSE KEYS ===")
for k, v in data.items():
    if k == "context":
        print(f"  {k}: [list of {len(v)} ints]")
    else:
        # Increased print length so you can actually read the 'thinking' output
        print(f"  {k}: {repr(str(v)[:1000])}")