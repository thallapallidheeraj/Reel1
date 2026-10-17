"""Synthesises the voiceover track from the VO lines in timeline.json using Kokoro TTS (offline, Apache-2.0).

Usage: python3 voice.py build/timeline.json build/voice.wav
Env:   KOKORO_DIR   folder holding kokoro-v1.0.onnx + voices-v1.0.bin (default: models/)
       VOICE        Kokoro voice id (default af_heart; British options: bf_emma, bf_isabella, bm_george)
       VOICE_SPEED  speaking rate (default 1.12)
"""
import json
import os
import sys
import wave

import numpy as np
from kokoro_onnx import Kokoro

SR = 44100
model_dir = os.environ.get("KOKORO_DIR", os.path.join(os.path.dirname(__file__), "models"))
voice = os.environ.get("VOICE", "af_heart")
speed = float(os.environ.get("VOICE_SPEED", "1.12"))
lang = "en-gb" if voice[:1] == "b" else "en-us"

timeline = json.load(open(sys.argv[1]))
kokoro = Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))

track = np.zeros(int(timeline["DURATION"] * SR))
lines = timeline["VO"]
for i, (start, text) in enumerate(lines):
    samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
    # resample 24 kHz -> 44.1 kHz
    src_t = np.arange(len(samples)) / sr
    clip = np.interp(np.arange(int(len(samples) / sr * SR)) / SR, src_t, samples)
    end = start + len(clip) / SR
    nxt = lines[i + 1][0] if i + 1 < len(lines) else timeline["DURATION"]
    flag = "  <-- OVERLAPS next line" if end > nxt else ""
    print(f"{start:5.2f}-{end:5.2f}s  {text}{flag}")
    a = int(start * SR)
    clip = clip[: len(track) - a]
    track[a : a + len(clip)] += clip

track /= max(1e-9, np.abs(track).max()) / 0.95
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((track * 32767).astype(np.int16).tobytes())
print("wrote", sys.argv[2])
