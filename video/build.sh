#!/usr/bin/env bash
# Builds customiselab-ugc.mp4: renders frames, synthesises audio, muxes both.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
node render.mjs build/silent.mp4
python3 audio.py build/timeline.json build/audio.wav
ffmpeg -y -loglevel error -i build/silent.mp4 -i build/audio.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart customiselab-ugc.mp4
echo "done: $(pwd)/customiselab-ugc.mp4"
