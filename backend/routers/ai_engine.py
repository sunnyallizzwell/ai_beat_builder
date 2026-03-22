from fastapi import APIRouter
from pydantic import BaseModel
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import os
import re
import time

router = APIRouter()
OUTPUT_DIR = '/app/shared_outputs'

print("[SYSTEM] Loading MusicGen Model to CPU...")
model = MusicGen.get_pretrained('facebook/musicgen-medium', device='cpu')
print("[SYSTEM] MusicGen Ready.")

class AIRequest(BaseModel):
    prompt: str
    duration: int = 10

def sanitize_filename(prompt: str) -> str:
    # Keep only alphanumeric characters and spaces
    clean = re.sub(r'[^a-zA-Z0-9 ]', '', prompt)
    # Replace spaces with underscores and limit to 50 characters to prevent OS crashes
    clean = clean.strip().replace(' ', '_')[:50]
    if not clean:
        clean = "ai_beat"
    # Append a short timestamp so if you use the same prompt twice, it doesn't overwrite
    return f"{clean}_{int(time.time())}"

@router.post("/generate")
def generate_ai_beat(req: AIRequest):
    try:
        # QUALITY UPGRADES:
        # cfg_coef: 5.0 forces the AI to strictly obey your prompt (less random noise)
        # temperature: 0.85 reduces chaos and makes the beat more structured
        model.set_generation_params(
            duration=req.duration,
            cfg_coef=5.0, 
            temperature=0.85 
        )
        wav = model.generate([req.prompt], progress=False)
        
        filename = sanitize_filename(req.prompt)
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # QUALITY UPGRADE: Change strategy to "peak" to stop bass distortion/clipping
        audio_write(filepath, wav[0].cpu(), model.sample_rate, strategy="peak")
        return {"status": "success", "file": f"{filename}.wav"}
    except Exception as e:
        return {"status": "error", "message": str(e)}