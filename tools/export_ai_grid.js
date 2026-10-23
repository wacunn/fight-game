// Rasterize the game's own street-level collision into the 1 m occupancy grid that both the
// RL env (Python) and the in-game neural copilot (JS) use. Re-run whenever city.js / the map changes:
//   open the game, open the browser console, paste this file, then run:  await exportAIGrid()
// It downloads ai_grid.js; drop it next to index.html (and in rl/ for training).
(function () {
  async function buildAIGrid(onProgress) {
    const city = window.__city || (window.gameCity) || null;
    if (!city || !city.canMoveTo) throw new Error('city not found (expose it as window.gameCity)');
    const B = city.bounds;
    const x0 = Math.floor(B.minX), z0 = Math.floor(B.minZ);
    const W = Math.ceil(B.maxX) - x0, H = Math.ceil(B.maxZ) - z0;
    const bytes = new Uint8Array(Math.ceil(W * H / 8));
    for (let j = 0; j < H; j++) {
      const z = z0 + j + 0.5;
      for (let i = 0; i < W; i++) {
        // player radius 0.6 at eye height 1.7 (street level: the open rail cut counts as blocked)
        if (!city.canMoveTo(x0 + i + 0.5, z, 0.6, 1.7)) {
          const k = j * W + i;
          bytes[k >> 3] |= (1 << (k & 7));
        }
      }
      if (onProgress && (j % 50 === 0)) { onProgress(j / H); await new Promise(r => setTimeout(r, 0)); }
    }
    let bin = '';
    for (let k = 0; k < bytes.length; k += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(k, k + 0x8000));
    const pz = city.peaceZone;
    return {
      version: 1, res: 1.0, x0, z0, w: W, h: H,
      bits: btoa(bin),                       // row-major (z rows), LSB-first, 1 = blocked
      peaceZone: { x: pz.x, z: pz.z, radius: pz.radius },
      start: city.start ? { x: city.start.x, z: city.start.z } : null,
      missions: (window.MISSION_LANDMARKS_EXPORT || []).map(m => ({ id: m.id, x: m.coords[0], z: m.coords[1] })),
    };
  }
  window.buildAIGrid = buildAIGrid;
  window.exportAIGrid = async function () {
    const g = await buildAIGrid(p => console.log(`AI grid ${(p * 100).toFixed(0)}%`));
    const blob = new Blob(['window.AI_GRID = ' + JSON.stringify(g) + ';\n'], { type: 'application/javascript' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'ai_grid.js'; a.click();
    return g;
  };
})();
