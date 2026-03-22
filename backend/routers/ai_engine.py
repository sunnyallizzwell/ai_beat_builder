from fastapi import APIRouter
from pydantic import BaseModel
import os
import re
import time
import multiprocessing

router = APIRouter()
OUTPUT_DIR = '/app/shared_outputs'

class AIRequest(BaseModel):
    prompt: str
    duration: int = 10

def sanitize_filename(prompt: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9 ]', '', prompt)
    clean = clean.strip().replace(' ', '_')[:50]
    if not clean:
        clean = "ai_beat"
    return f"{clean}_{int(time.time())}"

# --- THE ISOLATED QUARANTINE ZONE ---
# This function runs in its own dedicated Linux process.
def _generate_isolated(prompt: str, duration: int, filepath: str):
    # We import Audiocraft ONLY inside this dying process. 
    # The main server RAM is never contaminated.
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    
    print(f"\n[SYSTEM] Clone process spawned. Loading model from SSD into RAM...")
    model = MusicGen.get_pretrained('facebook/musicgen-medium', device='cpu')
    
    model.set_generation_params(
        duration=duration,
        cfg_coef=5.0, 
        temperature=0.85 
    )
    
    print("[SYSTEM] Generating audio...")
    wav = model.generate([prompt], progress=False)
    
    audio_write(filepath, wav[0].cpu(), model.sample_rate, strategy="peak")
    print("[SYSTEM] Audio saved. Terminating clone process to flush 100% of RAM.\n")
# ------------------------------------

@router.post("/generate")
def generate_ai_beat(req: AIRequest):
    filename = sanitize_filename(req.prompt)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        # 1. Spawn the isolated process
        p = multiprocessing.Process(
            target=_generate_isolated, 
            args=(req.prompt, req.duration, filepath)
        )
        p.start()
        
        # 2. Force the web server to wait until the clone process finishes
        p.join() 
        
        # 3. Check if the clone process died successfully (Exit code 0 means success)
        if p.exitcode == 0:
            return {"status": "success", "file": f"{filename}.wav"}
        else:
            return {"status": "error", "message": "The AI process crashed or was killed by the OS."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}