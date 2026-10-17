"""Synthesises a royalty-free upbeat music bed plus tap/whoosh/pop/ding SFX for the reel,
and mixes in the voiceover (if given) with the music ducked under speech.

Usage: python3 audio.py build/timeline.json build/audio.wav [build/voice.wav]
"""
import json
import sys
import wave

import numpy as np

SR = 44100
BPM = 112
BEAT = 60 / BPM

timeline = json.load(open(sys.argv[1]))
out_path = sys.argv[2]
dur = timeline["DURATION"]
n = int(dur * SR)
music = np.zeros(n)
sfx = np.zeros(n)
rng = np.random.default_rng(7)


def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i : i + len(sig)] += sig


def env(length, attack=0.005, decay=0.2):
    t = np.arange(int(length * SR)) / SR
    return np.minimum(t / attack, 1) * np.exp(-t / decay)


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    freq = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 9) * 0.9


def clap():
    e = env(0.22, 0.002, 0.07)
    noise = rng.standard_normal(len(e))
    noise = noise - np.convolve(noise, np.ones(8) / 8, "same")  # crude high-pass
    return noise * e * 0.35


def hat():
    e = env(0.06, 0.001, 0.015)
    noise = rng.standard_normal(len(e))
    return (noise - np.convolve(noise, np.ones(4) / 4, "same")) * e * 0.18


def tone(freq, length, decay, shape="saw", amp=0.2):
    t = np.arange(int(length * SR)) / SR
    if shape == "saw":
        sig = sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 8))
    else:
        sig = np.sin(2 * np.pi * freq * t)
    return sig * env(length, 0.004, decay) * amp


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


# F - C - G - Am, one chord per bar
progression = [(53, [65, 69, 72]), (48, [64, 67, 72]), (55, [62, 67, 71]), (57, [64, 69, 72])]
bars = int(dur / (4 * BEAT)) + 1
for bar in range(bars):
    t0 = bar * 4 * BEAT
    root, chord = progression[bar % 4]
    intro = t0 < 2.9  # keep the hook sparse: no kick until the reveal
    for b in range(4):
        tb = t0 + b * BEAT
        if not intro:
            add(music, tb, kick())
        if b in (1, 3):
            add(music, tb, clap())
        add(music, tb + BEAT / 2, hat())
        add(music, tb + BEAT / 4 * 3, hat() * 0.5)
        if not intro:
            add(music, tb, tone(midi(root - 12), BEAT * 0.9, 0.18, "saw", 0.16))
            add(music, tb + BEAT / 2, tone(midi(root), BEAT * 0.45, 0.1, "saw", 0.09))
    # plucky chord stabs on the off-beats
    for step in (0.5, 1.5, 2.5, 3.0, 3.5):
        for m in chord:
            add(music, t0 + step * BEAT, tone(midi(m), 0.4, 0.12, "saw", 0.035))

# soften the saws a touch
music = np.convolve(music, np.ones(6) / 6, "same")

ev = timeline["SFX"]
for t in ev["taps"]:
    add(sfx, t, tone(1800, 0.04, 0.008, "sine", 0.35))
for t in ev["whoosh"]:
    length = 0.35
    noise = rng.standard_normal(int(length * SR))
    noise = np.convolve(noise, np.ones(30) / 30, "same")
    shape = np.sin(np.linspace(0, np.pi, len(noise))) ** 2
    add(sfx, t - 0.1, noise * shape * 0.5)
for t in ev["pop"]:
    tt = np.arange(int(0.18 * SR)) / SR
    f = 300 + 900 * np.exp(-tt * 25)
    add(sfx, t, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 18) * 0.6)
for t in ev["ding"]:
    for m, delay in ((84, 0), (88, 0.09), (91, 0.18)):
        add(sfx, t + delay, tone(midi(m), 0.9, 0.35, "sine", 0.22))

music /= max(1e-9, np.abs(music).max())
voice = np.zeros(n)
if len(sys.argv) > 3:
    with wave.open(sys.argv[3]) as w:
        assert w.getframerate() == SR
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    voice[: min(n, len(v))] = v[:n]
# duck the music while someone is talking (smoothed speech envelope)
win = int(0.25 * SR)
speech = np.convolve(np.abs(voice), np.ones(win) / win, "same")
duck = 1 - 0.55 * np.clip(speech / 0.04, 0, 1)

mix = music * 0.42 * duck + sfx * 0.7 + voice * 0.95
fade = np.ones(n)
fl = int(0.8 * SR)
fade[-fl:] = np.linspace(1, 0, fl)
mix *= fade
mix /= max(1e-9, np.abs(mix).max()) / 0.89

pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
with wave.open(out_path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", out_path)
