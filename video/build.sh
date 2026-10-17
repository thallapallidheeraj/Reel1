#!/usr/bin/env bash
# Builds customiselab-ugc.mp4: renders frames, synthesises voiceover + music/SFX, muxes them.
# Python deps: pip install numpy kokoro-onnx soundfile
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
node render.mjs build/silent.mp4
if [ ! -f "${KOKORO_DIR:-models}/kokoro-v1.0.onnx" ]; then
  mkdir -p "${KOKORO_DIR:-models}"
  for f in kokoro-v1.0.onnx voices-v1.0.bin; do
    curl -fsSL -C - -o "${KOKORO_DIR:-models}/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
  done
fi
python3 voice.py build/timeline.json build/voice.wav
python3 audio.py build/timeline.json build/audio.wav build/voice.wav
ffmpeg -y -loglevel error -i build/silent.mp4 -i build/audio.wav -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 44100 -c:a aac -b:a 192k -shortest \
  -movflags +faststart customiselab-ugc.mp4
echo "done: $(pwd)/customiselab-ugc.mp4"
