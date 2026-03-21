from fastapi import APIRouter
from pydantic import BaseModel
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import random
import os

router = APIRouter()
OUTPUT_DIR = '/app/shared_outputs'

print("[SYSTEM] Loading MusicGen Model to CPU...")
model = MusicGen.get_pretrained('facebook/musicgen-small', device='cpu')
print("[SYSTEM] MusicGen Ready.")

class AIRequest(BaseModel):
    prompt: str
    duration: int = 10

@router.post("/generate")
def generate_ai_beat(req: AIRequest):
    try:
        model.set_generation_params(duration=req.duration)
        wav = model.generate([req.prompt], progress=False)
        
        filename = f"ai_beat_{random.randint(1000,9999)}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        audio_write(filepath, wav[0].cpu(), model.sample_rate, strategy="loudness")
        return {"status": "success", "file": f"{filename}.wav"}
    except Exception as e:
        return {"status": "error", "message": str(e)}