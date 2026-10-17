# Customise Lab – UGC reel

`customiselab-ugc.mp4` is a 28-second vertical (1080×1920, 30 fps) UGC-style screen-recording reel. It walks through personalising a Cotton Tee with a company logo on customiselab.com.au. It has a voiceover, a music bed and UI sound effects, normalised to about -15 LUFS.

| Time | Screen | Voiceover |
|---|---|---|
| 0–3.5s | Hook overlay | "POV: the boss wants team tees with our logo… by Friday." |
| 3.5–6s | Home carousel → Cotton Tee | "So I jumped on Customise Lab." |
| 6–10s | Product page → colour: Black | "Grabbed the cotton tee, picked black," |
| 10–13s | Upload Image tab → photo library → logo | "and uploaded our logo. Literally just a PNG." |
| 13–18s | Canvas: drag, resize, CENTRE; live preview | "Drag it, resize it, centre it. The live preview shows exactly how it'll print." |
| 18–22.7s | Size L → Add to cart → cart drawer | "Pick your size, add to cart, and it's printed right here in Australia." |
| 22.7–28s | End card | "Customise Lab dot com dot AU. Your logo. Your tee." |

**Note:** the screens are recreated from phone screenshots of the site, not captured live. The site couldn't be reached from the build environment. The "Bluegum Coffee Co." logo is a fictional sample.

## Rebuild

```bash
pip install numpy kokoro-onnx soundfile
./build.sh   # also needs node + playwright (Chromium) and ffmpeg
```

- `scene.html` holds the whole animation as a deterministic `render(t)`, plus the `VO` script, captions and SFX cues. Open `scene.html?play` in a browser to preview it in real time.
- `render.mjs` captures each frame with headless Chromium and pipes them to ffmpeg. `node render.mjs --stills 5,14,28` writes PNG stills to `build/`.
- `voice.py` synthesises the voiceover offline with [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) (Apache-2.0). `build.sh` downloads the model into `models/` on the first run. Set `VOICE` to change the voice: the default is `af_heart`, and the British options are `bf_emma`, `bf_isabella` and `bm_george`. `VOICE_SPEED` sets the speaking rate. The script warns if a line runs into the next one.
- `audio.py` synthesises a royalty-free music bed and SFX, ducks the music under the voice and mixes everything.
- `fonts/` holds Cormorant Garamond and Montserrat (SIL OFL).

To use a real voice recording instead, replace `build/voice.wav` (44.1 kHz mono) and rerun the `audio.py` and ffmpeg steps from `build.sh`.
