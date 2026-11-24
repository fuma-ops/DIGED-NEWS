// Rend ov.html image par image (fond transparent) : node ovshot.cjs <début> <fin> <fps> <sous-dossier> [dossier du short]
const { chromium } = require('playwright'); const path = require('path'), fs = require('fs');
const [, , from, to, fps, sub, dir = process.cwd()] = process.argv;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(dir, 'ov.html'), { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.join(dir, sub), { recursive: true });
  for (let f = +from; f < +to; f++) { await p.evaluate((t) => window.render(t), f / +fps); await p.screenshot({ path: path.join(dir, sub, `f${String(f).padStart(5, '0')}.png`), omitBackground: true }); }
  await b.close();
})();
