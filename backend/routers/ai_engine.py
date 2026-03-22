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
    duration: int = 15
    extend_track: bool = False # The new Checkbox flag

def sanitize_filename(prompt: str, extend_track: bool) -> str:
    clean = re.sub(r'[^a-zA-Z0-9 ]', '', prompt)
    clean = clean.strip().replace(' ', '_')[:40]
    if not clean:
        clean = "ai_beat"
        
    prefix = "FULL_SONG_" if extend_track else "SHORT_"
    return f"{prefix}{clean}_{int(time.time())}"

# --- THE ISOLATED QUARANTINE ZONE ---
def _generate_isolated(prompt: str, duration: int, extend_track: bool, filepath: str):
    from audiocraft.models import MusicGen
    from audiocraft.data.audio import audio_write
    import torch
    
    print(f"\n[SYSTEM] Clone spawned. Extend Track: {extend_track}. Loading model...")
    model = MusicGen.get_pretrained('facebook/musicgen-small', device='cpu')
    
    model.set_generation_params(
        duration=duration,
        cfg_coef=5.0, 
        temperature=0.85 
    )
    
    print("[SYSTEM] Generating base audio...")
    wav = model.generate([prompt], progress=False)
    
    # --- THE SEAMLESS DJ MIX MAGIC ---
    if extend_track:
        print("[SYSTEM] Stitching seamless 3-minute track using AI Continuation...")
        print("[SYSTEM] Note: This requires heavy calculation and will take several minutes.")
        
        # Calculate how many chunks we need to hit roughly 3 minutes (180 seconds)
        # We subtract 3 seconds from the duration because that's our "mix-in" overlap
        net_gain_per_chunk = duration - 3 
        if net_gain_per_chunk <= 0: net_gain_per_chunk = 12
        total_chunks = 180 // net_gain_per_chunk
        
        full_audio = wav
        
        for i in range(total_chunks - 1):
            print(f"[SYSTEM] AI Mixing chunk {i+2} of {total_chunks}...")
            # Grab the last 3 seconds of the generated audio to use as the "mix-in" point
            prompt_waveform = full_audio[..., -int(3 * model.sample_rate):]
            
            # AI listens to the end of the track and seamlessly continues the beat
            next_chunk = model.generate_continuation(
                prompt_waveform, 
                model.sample_rate, 
                [prompt], 
                progress=False
            )
            
            # Slice off the overlap and stitch the fresh audio on
            fresh_audio = next_chunk[..., int(3 * model.sample_rate):]
            full_audio = torch.cat([full_audio, fresh_audio], dim=-1)
            
        wav = full_audio 
    # ---------------------------------------
    
    audio_write(filepath, wav[0].cpu(), model.sample_rate, strategy="peak")
    print(f"[SYSTEM] Task complete. Saved file. Terminating clone to flush RAM.\n")
# ------------------------------------

@router.post("/generate")
def generate_ai_beat(req: AIRequest):
    filename = sanitize_filename(req.prompt, req.extend_track)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        p = multiprocessing.Process(
            target=_generate_isolated, 
            args=(req.prompt, req.duration, req.extend_track, filepath)
        )
        p.start()
        p.join() 
        
        if p.exitcode == 0:
            return {"status": "success", "file": f"{filename}.wav"}
        else:
            return {"status": "error", "message": "The AI process crashed."}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}