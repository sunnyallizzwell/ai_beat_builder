from fastapi import APIRouter
from pydantic import BaseModel
import pretty_midi
import random
import os

router = APIRouter()
OUTPUT_DIR = '/app/shared_outputs'

class MathRequest(BaseModel):
    bpm: float = 120
    bars: int = 4

@router.post("/generate")
def generate_math_beat(req: MathRequest):
    pm = pretty_midi.PrettyMIDI(initial_tempo=req.bpm)
    drums = pretty_midi.Instrument(program=0, is_drum=True)
    
    KICK = 36; SNARE = 38; HIHAT_CLOSED = 42
    total_steps = req.bars * 16
    step_duration = (60.0 / req.bpm) / 4

    for step in range(total_steps):
        time = step * step_duration
        if step % 4 == 0: # Four on the floor kick
            drums.notes.append(pretty_midi.Note(100, KICK, time, time+0.1))
        if step % 8 == 4: # Snare on 2 and 4
            drums.notes.append(pretty_midi.Note(90, SNARE, time, time+0.1))
        if random.random() > 0.3: # Random hi-hats
            drums.notes.append(pretty_midi.Note(random.randint(60, 90), HIHAT_CLOSED, time, time+0.1))

    pm.instruments.append(drums)
    filename = f"math_beat_{random.randint(1000,9999)}.mid"
    pm.write(os.path.join(OUTPUT_DIR, filename))
    
    return {"status": "success", "file": filename}