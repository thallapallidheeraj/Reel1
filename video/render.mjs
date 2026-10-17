// Renders scene.html frame-by-frame with headless Chromium and pipes JPEG frames into ffmpeg.
// Usage: node render.mjs [out.mp4] [--stills 1,5.6,14]   (stills mode writes PNGs instead)
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
let playwright;
try { playwright = require('playwright'); } catch { playwright = require('/opt/node-tools/node_modules/playwright'); }

const here = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const stillsIdx = args.indexOf('--stills');
const stills = stillsIdx >= 0 ? args[stillsIdx + 1].split(',').map(Number) : null;
const out = resolve(args.find(a => a.endsWith('.mp4')) || resolve(here, 'build/silent.mp4'));
const FPS = 30;

const browser = await playwright.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
await page.goto(pathToFileURL(resolve(here, 'scene.html')).href);
await page.evaluate(() => document.fonts.ready);
const timeline = await page.evaluate(() => window.TIMELINE);
mkdirSync(resolve(here, 'build'), { recursive: true });
writeFileSync(resolve(here, 'build/timeline.json'), JSON.stringify(timeline));

if (stills) {
  for (const t of stills) {
    await page.evaluate(t => window.render(t), t);
    await page.screenshot({ path: resolve(here, `build/still-${t}.png`) });
  }
} else {
  mkdirSync(dirname(out), { recursive: true });
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '18', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(timeline.DURATION * FPS);
  for (let i = 0; i < frames; i++) {
    await page.evaluate(t => window.render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 90 === 0) console.log(`frame ${i}/${frames}`);
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg exited ' + c))));
  console.log('wrote', out);
}
await browser.close();
