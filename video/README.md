# Customise Lab – UGC reel

`customiselab-ugc.mp4` is a 30-second vertical (1080×1920, 30 fps) UGC-style screen-recording reel. It walks through designing a custom T-shirt with a company logo on customiselab.com.au.

| Time | Beat |
|---|---|
| 0–3s | Hook: "POV: the boss wants team tees with our logo… by Friday" |
| 3–6s | Homepage → "Start designing" |
| 6–8s | Pick the Classic Cotton Tee |
| 8–11s | Choose a colour (white → navy → black) |
| 11–15s | Upload the company logo (`bluegum-logo.png`) |
| 15–20s | Drag and resize the logo on the chest |
| 20–24s | Add team sizes (S×2, M×4, L×4, XL×2) |
| 24–26s | Add to cart |
| 26–30s | End card: "Your logo. Your tee." + customiselab.com.au CTA |

**Note:** the site couldn't be reached from the build environment, so the screens are a recreation, not a capture of the live site. The UI, URL paths, colours, product names and the "Bluegum Coffee Co." logo are placeholders. Before posting, swap in the real brand colours, logo and product names in `scene.html` so the reel matches the site.

## Rebuild

```bash
./build.sh   # needs node + playwright (Chromium), python3 + numpy, ffmpeg
```

- `scene.html` holds the whole animation as a deterministic `render(t)`. Open `scene.html?play` in a browser to preview it in real time.
- `render.mjs` captures each frame with headless Chromium and pipes them to ffmpeg. `node render.mjs --stills 5,14,28` writes PNG stills to `build/`.
- `audio.py` synthesises a royalty-free music bed plus tap, whoosh, pop and ding SFX, timed to the scene.
