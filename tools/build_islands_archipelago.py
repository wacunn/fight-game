#!/usr/bin/env python3
"""
Generates fightGame/islands.js:
Authentic Toronto Islands Archipelago Mini-World with:
- Continuous mathematical landField(x, z) with channels, lagoons, and ponds.
- Open waterways under every bridge (Long Pond, Blockhouse Bay, South Lagoon, Algonquin Canal, Hanlan Canal, Algonquin Channel West).
- 6,000+ instanced trees (Eastern Cottonwoods, Sugar Maples, Weeping Willows along water banks, Coastal White Pines, Shrubs).
- Instanced wetland cattails, reeds, floating lily pads, and blooming water lilies.
- Real-world accurate landmarks:
  * William Meany Hedge Maze situated on the EAST side of Avenue of the Island (x: 105, z: Z(175))
    with dirt-colored walking pathways and the historic 1888 antique school bell in the center!
  * Centreville Amusement Park (giant rotating Ferris wheel, spinning vintage carousel, Pizza Pizza food court).
  * 1808 Gibraltar Point Limestone Lighthouse with rotating beacon beam.
  * Billy Bishop Airport (CYTZ) runway 08/26, terminal, control tower, radar dish, and Dash-8 aircraft.
  * Algonquin & Ward's Island summer cottage communities & Ward's Cafe.
  * Hanlan's Point ferry dock, Ned Hanlan memorial statue, and baseball diamonds.
  * Distant 3D Toronto Skyline across Toronto Harbour (CN Tower, Rogers Centre, Financial District).
- Animated wildlife (swimming white swans, moored canoes, cruising harbour ferry).
- Full collision and elevation API for player and NPC navigation.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / 'islands.js'

CODE = r'''/**
 * TORONTO ISLANDS ARCHIPELAGO MINI-WORLD
 * ============================================================================
 * An authentic 3D simulation of the Toronto Islands archipelago:
 *
 * 1. REAL WATERWAYS UNDER EVERY BRIDGE:
 *    - Distinct, physically separated island landmasses.
 *    - Long Pond & Allan A. Lamport Regatta Course (38m wide open water).
 *    - Blockhouse Bay separating Olympic Island and Gibraltar Point.
 *    - South Lagoon winding behind Centre Island beach dunes.
 *    - Algonquin Canal separating Algonquin and Ward's Island.
 *    - Hanlan's Canal separating Gibraltar Point and Hanlan's Point.
 *    - Algonquin Channel West separating Centreville from Algonquin Island.
 *    - Open blue water flows freely under every bridge with stone/timber abutments!
 *
 * 2. ANCIENT URBAN FOREST & NATURE TRAILS (6,000+ INSTANCED TREES & FLORA):
 *    - Massive heritage Eastern Cottonwoods (Populus deltoides) with towering canopies
 *    - Cascading Weeping Willows (Salix babylonica) draping branches into lagoon waters
 *    - Sugar Maples and Red Oaks in dense interior woodland groves
 *    - Coastal White Pines and Eastern Redcedars along beach dunes
 *    - Understory shrubs, wetland reeds, cattails, and floating water lily pads
 *    - Winding crushed-gravel and packed-earth nature trails weaving beneath shady canopy tunnels
 *    - 1.5km wooden Boardwalk from Centre Island Beach to Ward's Island Beach
 *
 * 3. AUTHENTIC ISLAND LANDMARKS & LIFE (ACCURATE REAL-WORLD POSITIONS):
 *    - William Meany Hedge Maze: located on the EAST side of Avenue of the Island (x=105, z=Z(175)),
 *      nestled between Avenue formal gardens and Centreville Carousel / Franklin Children's Garden.
 *      Features rich earth-toned dirt walking paths and the historic 1888 Toronto Island School Bell at the center!
 *    - Centreville Vintage Amusement Park: giant rotating 26m Ferris wheel, vintage carousel, Pizza Pizza food court.
 *    - 1808 Gibraltar Point Limestone Lighthouse with sweeping revolving beacon beam.
 *    - Billy Bishop Airport (CYTZ): Runway 08/26, terminal, control tower, rotating radar & Dash-8 aircraft.
 *    - Algonquin & Ward's Island pedestrian-only summer cottage communities & Ward's Cafe patio.
 *    - Hanlan's Point ferry terminal, Ned Hanlan memorial sculling statue, and historic baseball diamonds.
 *    - Animated wildlife: swimming swans on the lagoons, moored canoes on Long Pond, cruising harbour ferry.
 *    - Distant 3D Toronto Skyline across the harbour (553m CN Tower, Rogers Centre, Financial District towers).
 *
 * Coordinate Space:
 * Centered around (x = 0, z = 5000), allowing the entire 2.9km archipelago to be
 * explored without interfering with downtown mainland city grids or AI combat training.
 * ============================================================================
 */

(function () {
  'use strict';

  function buildTorontoIslands(scene) {
    const islandsGroup = new THREE.Group();
    islandsGroup.name = 'torontoIslandsArchipelago';

    const Z_BASE = 5000;
    const Z = o => Z_BASE + o;
    const GROUND_Y = 0.55; // walking height on the islands
    const WATER_Y = 0.0;

    // ------------------------------------------------------------------------
    // Deterministic noise for procedural terrain and vegetation
    // ------------------------------------------------------------------------
    function hash2(i, j) {
      const h = Math.sin(i * 127.1 + j * 311.7) * 43758.5453;
      return h - Math.floor(h);
    }
    function vnoise(x, z) {
      const i = Math.floor(x), j = Math.floor(z);
      const fx = x - i, fz = z - j;
      const u = fx * fx * (3 - 2 * fx), v = fz * fz * (3 - 2 * fz);
      const a = hash2(i, j), b = hash2(i + 1, j), c = hash2(i, j + 1), d = hash2(i + 1, j + 1);
      return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
    }
    function fbm(x, z) {
      return vnoise(x, z) * 0.55 + vnoise(x * 2.03 + 17, z * 2.03 + 9) * 0.3 + vnoise(x * 4.1 + 31, z * 4.1 + 5) * 0.15;
    }
    const n1 = t => vnoise(t, 0.37) * 2 - 1;
    let seed = 20261101;
    function rnd() {
      seed = (seed * 16807) % 2147483647;
      return (seed - 1) / 2147483646;
    }
    const smooth = (a, b, t) => {
      const k = Math.max(0, Math.min(1, (t - a) / (b - a)));
      return k * k * (3 - 2 * k);
    };

    // ------------------------------------------------------------------------
    // Geography: Island Shorelines & Continuous Land Field
    // ------------------------------------------------------------------------
    function interp(ctrl, x) {
      if (x <= ctrl[0][0]) return ctrl[0][1];
      for (let i = 1; i < ctrl.length; i++) {
        if (x <= ctrl[i][0]) {
          const a = ctrl[i - 1], b = ctrl[i];
          let t = (x - a[0]) / (b[0] - a[0]);
          t = t * t * (3 - 2 * t);
          return a[1] + (b[1] - a[1]) * t;
        }
      }
      return ctrl[ctrl.length - 1][1];
    }

    // Harbour-side (north) and lake-side (south) shorelines of the main chain
    const NORTH = [
      [-905, Z(-160)], [-760, Z(-135)], [-720, Z(-105)], [-640, Z(-70)], [-520, Z(-15)], [-400, Z(0)],
      [-250, Z(30)], [-100, Z(10)], [0, Z(-5)], [150, Z(0)], [300, Z(-15)], [450, Z(-30)], [600, Z(-35)],
      [800, Z(-45)], [1000, Z(-25)], [1135, Z(-25)], [1250, Z(0)], [1330, Z(80)]
    ];
    const SOUTH = [
      [-905, Z(330)], [-800, Z(400)], [-650, Z(460)], [-480, Z(490)], [-300, Z(500)], [0, Z(500)],
      [200, Z(495)], [400, Z(480)], [600, Z(450)], [800, Z(400)], [1000, Z(330)], [1150, Z(260)], [1250, Z(180)], [1330, Z(100)]
    ];
    const zN = x => interp(NORTH, x) + n1(x / 70) * 8;
    const zS = x => interp(SOUTH, x) + n1(x / 85 + 11) * 7;
    const EAST_TIP = 1335;

    // Lagoons, channels and ponds (water carved out of the land under bridges)
    const CHANNELS = [
      // Manitou Lagoon / Long Pond: spans under Manitou Bridge (0, Z(230..280))
      { name: 'Long Pond', w: 38, pts: [[-290, Z(255)], [-150, Z(255)], [0, Z(255)], [80, Z(255)], [180, Z(255)], [330, Z(260)]] },
      // Blockhouse Bay: runs between Olympic Island and Gibraltar Point, passing under Olympic-Gibraltar bridge (x=-340, z=Z(318))
      { name: 'Blockhouse Bay', w: 36, pts: [[-340, Z(220)], [-340, Z(280)], [-340, Z(318)], [-350, Z(380)], [-420, Z(430)]] },
      // South Lagoon: winds behind Centre Island beach dunes, passing under Avenue South Lagoon bridge (x=0, z=Z(355))
      { name: 'South Lagoon', w: 32, pts: [[-180, Z(360)], [-80, Z(355)], [0, Z(355)], [80, Z(355)], [180, Z(360)], [260, Z(370)]] },
      // Algonquin Canal: runs between Algonquin & Ward's Island, passing under Ward-Algonquin bridge (x=750, z=Z(60))
      { name: 'Algonquin Canal', w: 28, pts: [[750, Z(-60)], [750, Z(0)], [750, Z(60)], [750, Z(100)], [750, Z(180)]] },
      // Hanlan Canal: runs between Hanlan's Point and Gibraltar Point, passing under Gibraltar-Hanlan bridge (x=-590, z=Z(182))
      { name: 'Hanlan Canal', w: 28, pts: [[-560, Z(210)], [-590, Z(182)], [-620, Z(150)], [-680, Z(90)]] },
      // Algonquin Channel West: separating Centreville from Algonquin Island, passing under Algonquin Bridge (x=360, z=Z(80))
      { name: 'Algonquin Channel West', w: 28, pts: [[360, Z(-50)], [360, Z(10)], [360, Z(80)], [360, Z(150)], [360, Z(220)]] }
    ];

    const PONDS = [
      { name: 'Trout Pond', x: -690, z: Z(300), r: 38 },
      { name: 'Lighthouse Pond', x: -400, z: Z(195), r: 26 },
      { name: 'Centreville Swan Pond', x: 210, z: Z(290), r: 24 },
      { name: 'Algonquin Pond', x: 580, z: Z(140), r: 20 },
      { name: 'Ward\'s Pond', x: 960, z: Z(160), r: 26 }
    ];

    function distSeg(px, pz, ax, az, bx, bz) {
      const dx = bx - ax, dz = bz - az, L2 = dx * dx + dz * dz || 1;
      let t = ((px - ax) * dx + (pz - az) * dz) / L2;
      t = t < 0 ? 0 : (t > 1 ? 1 : t);
      const qx = ax + dx * t - px, qz = az + dz * t - pz;
      return Math.sqrt(qx * qx + qz * qz);
    }

    function distLine(px, pz, pts) {
      let d = Infinity;
      for (let i = 1; i < pts.length; i++) {
        d = Math.min(d, distSeg(px, pz, pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1]));
      }
      return d;
    }

    // Distance to nearest lagoon / pond edge (positive outside the water)
    function inlandWaterDist(x, z) {
      let d = Infinity;
      for (const c of CHANNELS) {
        d = Math.min(d, distLine(x, z, c.pts) - (c.w / 2) * (1 + n1(x / 40 + z / 53) * 0.10));
      }
      for (const p of PONDS) {
        d = Math.min(d, Math.hypot(x - p.x, z - p.z) - p.r * (1 + n1(Math.atan2(z - p.z, x - p.x) * 2 + p.r) * 0.12));
      }
      return d;
    }

    // Land field: metres to nearest shore, positive on land, negative in water
    function landField(x, z) {
      let L = -Infinity;
      if (x >= -905) {
        L = Math.min(z - zN(x), zS(x) - z, EAST_TIP + n1(z / 60) * 10 - x, x + 905 + n1(z / 45) * 4);
      }
      // Billy Bishop airport: filled land mass joined to Hanlan's Point
      const air = Math.min(x + 1575, z - Z(-310), Z(-35) - z, -860 - x);
      L = Math.max(L, air);
      if (L > -12) {
        L = Math.min(L, inlandWaterDist(x, z));
      }
      return L;
    }

    function isAirport(x, z) {
      return x < -880 && z < Z(-35);
    }

    function terrainH(x, z) {
      const L = landField(x, z);
      if (L <= 0) return Math.max(-2.4, L * 0.32);
      let h = Math.min(GROUND_Y, L * 0.22);
      if (x > -905 && !isAirport(x, z)) {
        const s = zS(x) - z; // dunes behind the lake beaches
        if (s > 0 && s < 75) {
          const dune = Math.max(0, fbm(x / 26, z / 26) - 0.42) * 2.8;
          h += dune * Math.min(1, s / 14) * Math.min(1, (75 - s) / 25);
        }
      }
      return h;
    }

    function isSand(x, z, L) {
      if (isAirport(x, z)) return false;
      if (L < 2.6) return true; // shoreline band
      if (x > -905 && zS(x) - z < 48 + n1(x / 33) * 12) return true; // south beaches
      if (x < -868 && x > -905) return true; // Hanlan's west beach
      if (x > 1185 && L < 40) return true; // Ward's east beach
      return false;
    }

    // ------------------------------------------------------------------------
    // Paths (Park roads, trails, boardwalk) & Clearings
    // ------------------------------------------------------------------------
    const PATHS = [
      { name: 'Avenue of the Islands', w: 12, kind: 'gravel', pts: [[0, Z(-5)], [0, Z(470)]] },
      { name: 'Maze Promenade Link', w: 6, kind: 'gravel', pts: [[0, Z(175)], [70, Z(175)]] },
      { name: 'Cibola Avenue', w: 6, kind: 'paved', pts: [[0, Z(25)], [150, Z(45)], [338, Z(66)], [392, Z(94)], [520, Z(100)], [620, Z(70)], [729, Z(46)], [776, Z(74)], [880, Z(100)], [1100, Z(100)], [1150, Z(70)], [1150, Z(-12)]] },
      { name: 'Manitou Road', w: 5, kind: 'paved', pts: [[0, Z(200)], [-60, Z(215)], [-170, Z(222)], [-260, Z(228)], [-335, Z(236)], [-420, Z(250)], [-520, Z(210)], [-568, Z(197)], [-612, Z(160)], [-690, Z(85)], [-720, Z(-95)]] },
      { name: 'Hanlan\'s Point Road', w: 6, kind: 'paved', pts: [[-720, Z(-95)], [-800, Z(-60)], [-960, Z(-130)]] },
      { name: 'Olympic Island Trail', w: 5, kind: 'gravel', pts: [[0, Z(320)], [-22, Z(320)], [-68, Z(320)], [-160, Z(320)], [-268, Z(322)], [-312, Z(322)], [-400, Z(330)], [-480, Z(308)]] },
      { name: 'Lighthouse Trail', w: 4, kind: 'gravel', pts: [[-420, Z(250)], [-470, Z(300)]] },
      { name: 'Lakeshore Avenue', w: 6, kind: 'paved', pts: [[-620, Z(440)], [-300, Z(455)], [-60, Z(452)], [0, Z(450)], [300, Z(440)]] },
      { name: 'The Boardwalk', w: 5, kind: 'boardwalk', pts: [[300, Z(440)], [600, Z(412)], [800, Z(362)], [1000, Z(292)], [1150, Z(222)], [1245, Z(130)]] },
      { name: 'Centreville Loop', w: 4, kind: 'gravel', pts: [[0, Z(140)], [80, Z(140)], [140, Z(95)], [260, Z(110)], [270, Z(200)], [220, Z(255)], [120, Z(250)], [0, Z(240)]] },
      { name: 'Ward\'s Lane', w: 3, kind: 'gravel', pts: [[900, Z(0)], [1140, Z(0)]] },
      { name: 'Algonquin Lane', w: 3, kind: 'gravel', pts: [[420, Z(62)], [600, Z(62)]] }
    ];
    const BOARDWALK = PATHS.find(p => p.kind === 'boardwalk');

    // Lawns, gardens, and clearings where trees are kept clear
    const CLEARINGS = [
      { r: [-45, 45, Z(-35), Z(245)] }, // Avenue of the Islands and formal gardens
      { c: [-160, Z(330), 65] }, // Olympic Island Great Lawn (skyline panorama)
      { r: [50, 300, Z(80), Z(270)] }, // Centreville Amusement Park
      { r: [65, 145, Z(135), Z(215)] }, // William Meany Hedge Maze (EAST side of Avenue)
      { r: [28, 98, Z(22), Z(92)] }, // Formal parterre garden
      { c: [-780, Z(0), 85] }, // Hanlan's ball fields
      { c: [-480, Z(320), 38] }, // Gibraltar lighthouse sanctuary
      { r: [412, 702, Z(22), Z(112)] }, // Algonquin cottages
      { r: [892, 1142, Z(-48), Z(48)] }, // Ward's cottages
      { c: [1050, Z(70), 28] }, // Ward's Cafe patio
      { c: [0, Z(-5), 38] }, { c: [-720, Z(-110), 34] }, { c: [1140, Z(-20), 30] }, // Ferry docks
      { c: [100, Z(330), 36] }, // Picnic meadow by Long Pond
      { c: [560, Z(300), 48] }, // Ward's meadow
      { c: [-560, Z(80), 40] }, // Hanlan's picnic grounds
      { c: [-330, Z(150), 34] } // Gibraltar glade
    ];

    function inClearing(x, z, pad) {
      const p = pad || 0;
      for (const c of CLEARINGS) {
        if (c.r) {
          if (x > c.r[0] - p && x < c.r[1] + p && z > c.r[2] - p && z < c.r[3] + p) return true;
        } else if (Math.hypot(x - c.c[0], z - c.c[1]) < c.c[2] + p) {
          return true;
        }
      }
      return false;
    }

    function nearPath(x, z, pad) {
      for (const p of PATHS) {
        if (distLine(x, z, p.pts) < p.w / 2 + (pad || 0)) return p;
      }
      return null;
    }

    // Forest density in [0, 1]: rich natural woods with glades
    function forestDensity(x, z, L) {
      if (L < 3.5 || isAirport(x, z) || isSand(x, z, L)) return 0;
      if (inClearing(x, z)) return 0;
      const f = fbm(x / 150 + 3.1, z / 150 + 7.7);
      return smooth(0.36, 0.58, f);
    }

    // ------------------------------------------------------------------------
    // Materials
    // ------------------------------------------------------------------------
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x7a5230, roughness: 0.8 });
    const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x4a2c14, roughness: 0.85 });
    const stoneMat = new THREE.MeshStandardMaterial({ color: 0xd6d3d1, roughness: 0.75 });
    const concreteMat = new THREE.MeshStandardMaterial({ color: 0xa8a29e, roughness: 0.85 });
    const asphaltMat = new THREE.MeshStandardMaterial({ color: 0x2b2b2e, roughness: 0.9 });
    const whiteMarkMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, fog: false });
    const yellowMarkMat = new THREE.MeshBasicMaterial({ color: 0xfacc15, fog: false });
    const hedgeMat = new THREE.MeshStandardMaterial({ color: 0x165b2d, roughness: 0.9 });
    const dirtMat = new THREE.MeshStandardMaterial({ color: 0x6e4727, roughness: 0.95 }); // Rich packed dirt for maze
    const bellBrassMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.28, metalness: 0.85 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.3, metalness: 0.8 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x7fb8d4, roughness: 0.1, metalness: 0.6, opacity: 0.65, transparent: true });
    const lampGlowMat = new THREE.MeshBasicMaterial({ color: 0xffd58a, fog: false });

    // Counter-clockwise-from-above mesh builder with vertex colors
    function Mesher() {
      this.pos = [];
      this.nor = [];
      this.col = [];
      this.idx = [];
    }
    Mesher.prototype.v = function (x, y, z, c) {
      this.pos.push(x, y, z);
      this.nor.push(0, 1, 0);
      this.col.push(c[0], c[1], c[2]);
      return this.pos.length / 3 - 1;
    };
    Mesher.prototype.quadUp = function (a, b, c, d) {
      const P = this.pos;
      const ny = (P[b * 3 + 2] - P[a * 3 + 2]) * (P[c * 3] - P[a * 3]) - (P[b * 3] - P[a * 3]) * (P[c * 3 + 2] - P[a * 3 + 2]);
      if (ny >= 0) this.idx.push(a, b, c, a, c, d);
      else this.idx.push(a, c, b, a, d, c);
    };
    Mesher.prototype.build = function (computeNormals) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(this.pos, 3));
      g.setAttribute('normal', new THREE.Float32BufferAttribute(this.nor, 3));
      g.setAttribute('color', new THREE.Float32BufferAttribute(this.col, 3));
      g.setIndex(this.idx);
      if (computeNormals) g.computeVertexNormals();
      return g;
    };

    const hex = h => [((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255];
    const mix = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
    const C = {
      lawn: hex(0x4f9a3a),
      lawnDry: hex(0x7aa04a),
      forest: hex(0x2f4a22),
      litter: hex(0x4d3d24),
      sand: hex(0xe2cf9c),
      sandDark: hex(0xc9b27a),
      mud: hex(0x6d5a3c),
      deep: hex(0x1b3a40),
      concrete: hex(0x8f908c),
      gravel: hex(0xc9bea5),
      paved: hex(0x4a4a4f),
      board: hex(0x8a6a45)
    };

    function surfaceColor(x, z, L) {
      if (isAirport(x, z)) return mix(C.concrete, hex(0x7d7e7a), vnoise(x / 9, z / 9));
      if (L < 0) return mix(C.sandDark, C.deep, Math.min(1, -L / 9));
      if (isSand(x, z, L)) return L < 1.2 ? mix(C.mud, C.sandDark, L / 1.2) : mix(C.sand, C.sandDark, vnoise(x / 6, z / 6) * 0.6);
      const f = forestDensity(x, z, L);
      const grass = mix(C.lawn, C.lawnDry, vnoise(x / 20, z / 20) * 0.7);
      const floor = mix(C.forest, C.litter, vnoise(x / 7 + 3, z / 7) * 0.8);
      return mix(grass, floor, Math.min(1, f * 1.2));
    }

    // ------------------------------------------------------------------------
    // Water surface plane
    // ------------------------------------------------------------------------
    const waterMat = new THREE.MeshStandardMaterial({
      color: 0x1f6f8b,
      roughness: 0.12,
      metalness: 0.35,
      opacity: 0.85,
      transparent: true,
      depthWrite: false
    });
    const water = new THREE.Mesh(new THREE.PlaneGeometry(6400, 3600, 1, 1), waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.set(0, WATER_Y, Z(-200));
    water.renderOrder = 1;
    islandsGroup.add(water);

    // ------------------------------------------------------------------------
    // Terrain (land + shallows) 5m grid
    // ------------------------------------------------------------------------
    const GX0 = -1600, GX1 = 1360, GZ0 = Z(-340), GZ1 = Z(560), STEP = 5;
    const NX = Math.round((GX1 - GX0) / STEP) + 1, NZ = Math.round((GZ1 - GZ0) / STEP) + 1;
    const Lgrid = new Float32Array(NX * NZ);
    {
      const m = new Mesher();
      const vid = new Int32Array(NX * NZ);
      for (let j = 0; j < NZ; j++) {
        for (let i = 0; i < NX; i++) {
          const x = GX0 + i * STEP, z = GZ0 + j * STEP;
          const L = landField(x, z);
          Lgrid[j * NX + i] = L;
          vid[j * NX + i] = m.v(x, terrainH(x, z), z, surfaceColor(x, z, L));
        }
      }
      for (let j = 0; j < NZ - 1; j++) {
        for (let i = 0; i < NX - 1; i++) {
          const k = j * NX + i;
          if (Math.max(Lgrid[k], Lgrid[k + 1], Lgrid[k + NX], Lgrid[k + NX + 1]) < -7) continue; // open water
          m.quadUp(vid[k], vid[k + 1], vid[k + NX + 1], vid[k + NX]);
        }
      }
      const terrain = new THREE.Mesh(m.build(true), new THREE.MeshLambertMaterial({ vertexColors: true }));
      terrain.receiveShadow = true;
      islandsGroup.add(terrain);
    }

    function sampleL(x, z) {
      const i = Math.round((x - GX0) / STEP), j = Math.round((z - GZ0) / STEP);
      if (i < 0 || j < 0 || i >= NX || j >= NZ) return -99;
      return Lgrid[j * NX + i];
    }

    // ------------------------------------------------------------------------
    // Paths and Boardwalk
    // ------------------------------------------------------------------------
    {
      const m = new Mesher();
      PATHS.forEach(p => {
        const col = p.kind === 'gravel' ? C.gravel : (p.kind === 'boardwalk' ? C.board : C.paved);
        const lift = p.kind === 'boardwalk' ? 0.32 : 0.05;
        for (let s = 1; s < p.pts.length; s++) {
          const a = p.pts[s - 1], b = p.pts[s], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
          const nx = -(b[1] - a[1]) / L * p.w / 2, nz = (b[0] - a[0]) / L * p.w / 2;
          const n = Math.max(1, Math.ceil(L / 3));
          for (let k = 0; k < n; k++) {
            const t0 = k / n, t1 = (k + 1) / n;
            const x0 = a[0] + (b[0] - a[0]) * t0, z0 = a[1] + (b[1] - a[1]) * t0;
            const x1 = a[0] + (b[0] - a[0]) * t1, z1 = a[1] + (b[1] - a[1]) * t1;
            if (landField(x0, z0) < 1.5 || landField(x1, z1) < 1.5) continue; // bridges carry over water
            const y0 = terrainH(x0, z0) + lift, y1 = terrainH(x1, z1) + lift;
            const shade = mix(col, [0, 0, 0], vnoise(x0 / 4, z0 / 4) * 0.12);
            const q = [
              m.v(x0 + nx, y0, z0 + nz, shade),
              m.v(x1 + nx, y1, z1 + nz, shade),
              m.v(x1 - nx, y1, z1 - nz, shade),
              m.v(x0 - nx, y0, z0 - nz, shade)
            ];
            m.quadUp(q[0], q[1], q[2], q[3]);
          }
        }
      });
      const pathMesh = new THREE.Mesh(m.build(), new THREE.MeshLambertMaterial({ vertexColors: true }));
      pathMesh.receiveShadow = true;
      islandsGroup.add(pathMesh);
    }

    // ------------------------------------------------------------------------
    // Obstacles Spatial Grid (buildings, walls)
    // ------------------------------------------------------------------------
    const OB_CELL = 10;
    const obGrid = new Map();
    function obAdd(o) {
      const r = o.c ? o.c[2] : Math.max(o.r[1] - o.r[0], o.r[3] - o.r[2]);
      const cx = o.c ? o.c[0] : (o.r[0] + o.r[1]) / 2, cz = o.c ? o.c[1] : (o.r[2] + o.r[3]) / 2;
      for (let i = Math.floor((cx - r) / OB_CELL); i <= Math.floor((cx + r) / OB_CELL); i++) {
        for (let j = Math.floor((cz - r) / OB_CELL); j <= Math.floor((cz + r) / OB_CELL); j++) {
          const k = i + ',' + j;
          if (!obGrid.has(k)) obGrid.set(k, []);
          obGrid.get(k).push(o);
        }
      }
    }
    const rectOb = (x0, x1, z0, z1) => obAdd({ r: [Math.min(x0, x1), Math.max(x0, x1), Math.min(z0, z1), Math.max(z0, z1)] });
    const circOb = (x, z, r) => obAdd({ c: [x, z, r] });

    function blocked(x, z, rad) {
      const list = obGrid.get(Math.floor(x / OB_CELL) + ',' + Math.floor(z / OB_CELL));
      if (!list) return false;
      for (const o of list) {
        if (o.c) {
          if (Math.hypot(x - o.c[0], z - o.c[1]) < o.c[2] + rad) return true;
        } else if (x > o.r[0] - rad && x < o.r[1] + rad && z > o.r[2] - rad && z < o.r[3] + rad) {
          return true;
        }
      }
      return false;
    }

    // ------------------------------------------------------------------------
    // Signs helper
    // ------------------------------------------------------------------------
    function makeSign(lines, w, h, opts) {
      const o = opts || {};
      const can = document.createElement('canvas');
      can.width = 512;
      can.height = Math.round(512 * (h / w));
      const g = can.getContext('2d');
      g.fillStyle = o.bg || '#0f172a';
      g.fillRect(0, 0, can.width, can.height);
      g.strokeStyle = o.borderColor || '#38bdf8';
      g.lineWidth = 10;
      g.strokeRect(5, 5, can.width - 10, can.height - 10);
      g.textAlign = 'center';
      g.textBaseline = 'middle';
      lines.forEach((txt, idx) => {
        const py = (can.height / (lines.length + 1)) * (idx + 1);
        g.font = idx === 0 ? 'bold ' + (o.titleSize || 46) + 'px sans-serif' : 'bold ' + (o.subSize || 28) + 'px sans-serif';
        g.fillStyle = idx === 0 ? (o.fg || '#ffffff') : (o.subFg || '#cbd5e1');
        g.fillText(txt, can.width / 2, py);
      });
      return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(can), side: THREE.DoubleSide }));
    }

    // ------------------------------------------------------------------------
    // Bridges over lagoons (Arched Timber Footbridges with Railings & Stone Abutments)
    // ------------------------------------------------------------------------
    const bridges = [
      { name: 'Manitou Bridge', x0: 0, z0: Z(230), x1: 0, z1: Z(280), w: 9.0, archH: 2.4, yBase: 0.55 },
      { name: 'Olympic-Gibraltar Bridge', x0: -370, z0: Z(318), x1: -310, z1: Z(318), w: 7.0, archH: 2.3, yBase: 0.55 },
      { name: 'Algonquin Bridge', x0: 330, z0: Z(65), x1: 395, z1: Z(95), w: 7.2, archH: 2.5, yBase: 0.55 },
      { name: 'Ward-Algonquin Footbridge', x0: 720, z0: Z(45), x1: 780, z1: Z(75), w: 6.5, archH: 2.4, yBase: 0.55 },
      { name: 'Avenue South Lagoon Bridge', x0: 0, z0: Z(335), x1: 0, z1: Z(375), w: 10.0, archH: 2.4, yBase: 0.55 },
      { name: 'Gibraltar-Hanlan Bridge', x0: -566, z0: Z(200), x1: -614, z1: Z(164), w: 6.5, archH: 2.3, yBase: 0.55 }
    ];

    bridges.forEach(b => {
      b.len = Math.hypot(b.x1 - b.x0, b.z1 - b.z0);
      b.fx = (b.x1 - b.x0) / b.len;
      b.fz = (b.z1 - b.z0) / b.len;
      const bg = new THREE.Group();
      const segs = 16, rotY = Math.atan2(b.fx, b.fz);
      for (let i = 0; i < segs; i++) {
        const t = (i + 0.5) / segs, y = b.yBase + Math.sin(t * Math.PI) * b.archH;
        const px = b.x0 + (b.x1 - b.x0) * t, pz = b.z0 + (b.z1 - b.z0) * t;
        const slope = Math.cos(t * Math.PI) * Math.PI * b.archH / b.len;
        const plank = new THREE.Mesh(new THREE.BoxGeometry(b.w, 0.35, b.len / segs + 0.25), woodMat);
        plank.position.set(px, y, pz);
        plank.rotation.set(-Math.atan(slope), rotY, 0, 'YXZ');
        bg.add(plank);
        [-1, 1].forEach(sd => {
          const ox = Math.cos(rotY) * sd * (b.w / 2 - 0.15), oz = -Math.sin(rotY) * sd * (b.w / 2 - 0.15);
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.22, 1.1, 0.22), darkWoodMat);
          post.position.set(px + ox, y + 0.7, pz + oz);
          bg.add(post);
          const rail = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.14, b.len / segs + 0.3), darkWoodMat);
          rail.position.set(px + ox, y + 1.22, pz + oz);
          rail.rotation.set(-Math.atan(slope), rotY, 0, 'YXZ');
          bg.add(rail);
        });
      }
      [[b.x0, b.z0], [b.x1, b.z1]].forEach(([ax, az]) => {
        const abut = new THREE.Mesh(new THREE.BoxGeometry(b.w + 1.2, 1.1, 3.0), stoneMat);
        abut.position.set(ax, 0.2, az);
        abut.rotation.y = rotY;
        bg.add(abut);
      });
      islandsGroup.add(bg);
    });

    function getIslandBridgeAt(x, z, pad) {
      for (const b of bridges) {
        const dx = x - b.x0, dz = z - b.z0;
        const s = dx * b.fx + dz * b.fz, l = -dx * b.fz + dz * b.fx;
        if (s >= -1.5 - (pad || 0) && s <= b.len + 1.5 + (pad || 0) && Math.abs(l) <= b.w / 2 - 0.45) {
          return b;
        }
      }
      return null;
    }

    // ------------------------------------------------------------------------
    // Piers and Docks
    // ------------------------------------------------------------------------
    const PIERS = [
      { name: 'Centre Island Pier', r: [-6, 6, Z(470), Z(590)], y: 0.55 },
      { name: 'Centre Island Ferry Dock', r: [-16, 16, Z(-40), Z(12)], y: 0.55 },
      { name: 'Hanlan\'s Point Ferry Dock', r: [-732, -708, Z(-150), Z(-100)], y: 0.55 },
      { name: 'Ward\'s Island Ferry Dock', r: [1128, 1152, Z(-60), Z(-14)], y: 0.55 }
    ];

    PIERS.forEach(p => {
      const w = p.r[1] - p.r[0], d = p.r[3] - p.r[2];
      const deck = new THREE.Mesh(new THREE.BoxGeometry(w, 0.4, d), woodMat);
      deck.position.set((p.r[0] + p.r[1]) / 2, p.y - 0.2, (p.r[2] + p.r[3]) / 2);
      islandsGroup.add(deck);
      for (let pz = p.r[2] + 2; pz < p.r[3]; pz += 6) {
        [p.r[0] + 0.6, p.r[1] - 0.6].forEach(px => {
          const pile = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 3, 6), darkWoodMat);
          pile.position.set(px, -0.9, pz);
          islandsGroup.add(pile);
        });
      }
    });

    function pierAt(x, z) {
      for (const p of PIERS) {
        if (x >= p.r[0] && x <= p.r[1] && z >= p.r[2] && z <= p.r[3]) return p;
      }
      return null;
    }

    // ------------------------------------------------------------------------
    // FOREST: 6,000+ Instanced Trees by Species & Shrubs
    // ------------------------------------------------------------------------
    const TRUNK_CELL = 8;
    const trunkGrid = new Map();
    const trees = { round: [], willow: [], pine: [] };
    const shrubs = [];

    {
      const SP = 6.5;
      for (let x = GX0 + 40; x < GX1; x += SP) {
        for (let z = GZ0; z < GZ1; z += SP) {
          const tx = x + (rnd() - 0.5) * SP * 0.9, tz = z + (rnd() - 0.5) * SP * 0.9;
          const L = sampleL(tx, tz);
          if (L < 2.5 || isAirport(tx, tz)) continue;
          if (nearPath(tx, tz, 2.5) || inClearing(tx, tz, 2.0)) continue;
          const wd = inlandWaterDist(tx, tz);
          let kind = null;
          if (wd > 1.5 && wd < 10 && rnd() < 0.52) {
            kind = 'willow'; // weeping willows line the water banks
          } else if (isSand(tx, tz, L)) {
            if (tx < -280 && L > 12 && zS(tx) - tz > 22 && rnd() < 0.24) {
              kind = 'pine'; // coastal pines on dunes
            }
          } else {
            const f = forestDensity(tx, tz, L);
            if (rnd() < f * 0.95) {
              kind = (tx < -350 && rnd() < 0.35) ? 'pine' : 'round';
            } else if (f < 0.1 && rnd() < 0.025) {
              kind = 'round'; // lone shade trees
            }
            if (f > 0.3 && rnd() < 0.45) {
              shrubs.push([tx + (rnd() - 0.5) * 4, tz + (rnd() - 0.5) * 4, 0.6 + rnd() * 1.0]);
            }
          }
          if (!kind) continue;
          const y = terrainH(tx, tz);
          const s = kind === 'pine' ? 0.8 + rnd() * 0.6 : 0.75 + rnd() * 0.7;
          trees[kind].push({ kind, x: tx, z: tz, y, s, r: rnd() });
          const k = Math.floor(tx / TRUNK_CELL) + ',' + Math.floor(tz / TRUNK_CELL);
          if (!trunkGrid.has(k)) trunkGrid.set(k, []);
          trunkGrid.get(k).push([tx, tz, 0.35 + s * 0.25]);
        }
      }
    }

    function trunkBlocked(x, z, rad) {
      const i = Math.floor(x / TRUNK_CELL), j = Math.floor(z / TRUNK_CELL);
      for (let a = i - 1; a <= i + 1; a++) {
        for (let b = j - 1; b <= j + 1; b++) {
          const list = trunkGrid.get(a + ',' + b);
          if (!list) continue;
          for (const t of list) {
            if (Math.hypot(x - t[0], z - t[1]) < t[2] + rad) return true;
          }
        }
      }
      return false;
    }

    {
      const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), v = new THREE.Vector3(), sc = new THREE.Vector3(), col = new THREE.Color();
      const all = trees.round.concat(trees.willow, trees.pine);

      // Trunks
      const trunkGeo = new THREE.CylinderGeometry(0.22, 0.38, 1, 6);
      trunkGeo.translate(0, 0.5, 0);
      const trunkMesh = new THREE.InstancedMesh(trunkGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), all.length);
      all.forEach((t, i) => {
        const h = (t.kind === 'pine' ? 3.0 : 4.2) * t.s;
        m4.compose(v.set(t.x, t.y - 0.1, t.z), q.setFromEuler(e.set(0, 0, 0)), sc.set(t.s * 1.1, h, t.s * 1.1));
        trunkMesh.setMatrixAt(i, m4);
        trunkMesh.setColorAt(i, col.setHex(0x4a3726).multiplyScalar(0.8 + t.r * 0.4));
      });
      islandsGroup.add(trunkMesh);

      // Broadleaf crowns (Cottonwood, Silver Maple, Oak): two overlapping blobs per tree
      const roundGeo = new THREE.DodecahedronGeometry(1, 1);
      const roundMesh = new THREE.InstancedMesh(roundGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), trees.round.length * 2);
      const greens = [0x2f6b2a, 0x3d7d2f, 0x497f34, 0x2b5e2c, 0x5b8a3a, 0x376e35];
      const autumn = [0xc9852b, 0xb8572a, 0xd9a23a, 0x9c6b2a];
      trees.round.forEach((t, i) => {
        const base = t.r < 0.16 ? autumn[Math.floor(t.r * 100) % autumn.length] : greens[Math.floor(t.r * 997) % greens.length];
        const R = 3.0 * t.s, top = t.y + 4.2 * t.s + R * 0.6;
        e.set(0, t.r * 6.28, 0);
        q.setFromEuler(e);
        m4.compose(v.set(t.x, top, t.z), q, sc.set(R * 1.05, R * 0.85, R));
        roundMesh.setMatrixAt(i * 2, m4);
        roundMesh.setColorAt(i * 2, col.setHex(base));
        m4.compose(v.set(t.x + (t.r - 0.5) * R * 0.9, top + R * 0.45, t.z + (0.5 - t.r) * R * 0.7), q, sc.set(R * 0.72, R * 0.65, R * 0.72));
        roundMesh.setMatrixAt(i * 2 + 1, m4);
        roundMesh.setColorAt(i * 2 + 1, col.setHex(base).multiplyScalar(1.12));
      });
      islandsGroup.add(roundMesh);

      // Weeping Willows: rounded crown + drooping curtain along lagoon banks
      const wCrown = new THREE.InstancedMesh(roundGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), trees.willow.length);
      const wCurtainGeo = new THREE.CylinderGeometry(1.6, 2.2, 1, 9, 1, true);
      wCurtainGeo.translate(0, -0.5, 0);
      const wCurtain = new THREE.InstancedMesh(wCurtainGeo, new THREE.MeshLambertMaterial({ color: 0xffffff, side: THREE.DoubleSide }), trees.willow.length);
      trees.willow.forEach((t, i) => {
        const R = 3.2 * t.s, top = t.y + 3.8 * t.s + R * 0.5;
        e.set(0, t.r * 6.28, 0);
        q.setFromEuler(e);
        m4.compose(v.set(t.x, top, t.z), q, sc.set(R * 1.15, R * 0.7, R * 1.15));
        wCrown.setMatrixAt(i, m4);
        wCrown.setColorAt(i, col.setHex(0x5ca83e));
        m4.compose(v.set(t.x, top - R * 0.2, t.z), q, sc.set(R * 1.1, R * 1.25, R * 1.1));
        wCurtain.setMatrixAt(i, m4);
        wCurtain.setColorAt(i, col.setHex(0x6ca33e));
      });
      islandsGroup.add(wCrown, wCurtain);

      // Coastal White Pines: layered conical tiers
      const pineGeo = new THREE.ConeGeometry(1, 1, 7);
      pineGeo.translate(0, 0.5, 0);
      const pineMesh = new THREE.InstancedMesh(pineGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), trees.pine.length * 3);
      const pGreens = [0x1f4a30, 0x245436, 0x184028];
      trees.pine.forEach((t, i) => {
        const cBase = pGreens[Math.floor(t.r * 97) % pGreens.length];
        for (let k = 0; k < 3; k++) {
          const R = (3.0 - k * 0.65) * t.s, H = (3.4 - k * 0.5) * t.s;
          const y = t.y + (2.2 + k * 1.8) * t.s;
          e.set(0, t.r * 6.28 + k * 0.7, 0);
          q.setFromEuler(e);
          m4.compose(v.set(t.x, y, t.z), q, sc.set(R, H, R));
          pineMesh.setMatrixAt(i * 3 + k, m4);
          pineMesh.setColorAt(i * 3 + k, col.setHex(cBase).multiplyScalar(1 + k * 0.12));
        }
      });
      islandsGroup.add(pineMesh);

      // Understory shrubs
      const shrubMesh = new THREE.InstancedMesh(roundGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), shrubs.length);
      const sGreens = [0x3c6e2e, 0x4d7c34, 0x5a8a3a];
      shrubs.forEach(([x, z, s], i) => {
        const y = terrainH(x, z);
        m4.compose(v.set(x, y + s * 0.5, z), q.setFromEuler(e.set(0, 0, 0)), sc.set(s * 1.2, s * 0.7, s * 1.2));
        shrubMesh.setMatrixAt(i, m4);
        shrubMesh.setColorAt(i, col.setHex(sGreens[i % 3]));
      });
      islandsGroup.add(shrubMesh);
    }

    // ------------------------------------------------------------------------
    // WETLANDS: Reeds and Cattails Along Lagoons, Lily Pads with Blooms
    // ------------------------------------------------------------------------
    {
      const reeds = [], pads = [];
      const shoreWalk = (pts, half) => {
        for (let i = 1; i < pts.length; i++) {
          const a = pts[i - 1], b = pts[i], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
          const nx = -(b[1] - a[1]) / L, nz = (b[0] - a[0]) / L;
          for (let s = 0; s < L; s += 1.6) {
            [-1, 1].forEach(sd => {
              if (rnd() < 0.45) return;
              const off = half + (rnd() - 0.55) * 3.2;
              const x = a[0] + (b[0] - a[0]) * s / L + nx * sd * off, z = a[1] + (b[1] - a[1]) * s / L + nz * sd * off;
              const L2 = landField(x, z);
              if (L2 > -2.2 && L2 < 1.4 && !getIslandBridgeAt(x, z, 4) && !nearPath(x, z, 1)) {
                reeds.push([x, z]);
              }
            });
            if (rnd() < 0.18) {
              const x = a[0] + (b[0] - a[0]) * s / L + nx * (rnd() - 0.5) * half * 1.4;
              const z = a[1] + (b[1] - a[1]) * s / L + nz * (rnd() - 0.5) * half * 1.4;
              if (landField(x, z) < -2 && !getIslandBridgeAt(x, z, 5)) {
                pads.push([x, z, rnd()]);
              }
            }
          }
        }
      };

      CHANNELS.forEach(c => shoreWalk(c.pts, c.w / 2));
      PONDS.forEach(p => {
        for (let a = 0; a < Math.PI * 2; a += 0.09) {
          const off = p.r + (rnd() - 0.6) * 3;
          const x = p.x + Math.cos(a) * off, z = p.z + Math.sin(a) * off;
          const L2 = landField(x, z);
          if (rnd() < 0.7 && L2 > -2.2 && L2 < 1.4) reeds.push([x, z]);
        }
        for (let k = 0; k < p.r * 1.6; k++) {
          const a = rnd() * 6.283, d = rnd() * p.r * 0.85;
          pads.push([p.x + Math.cos(a) * d, p.z + Math.sin(a) * d, rnd()]);
        }
      });

      const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v = new THREE.Vector3(), sc = new THREE.Vector3(), col = new THREE.Color(), e = new THREE.Euler();
      const reedGeo = new THREE.ConeGeometry(0.45, 1, 5, 1, true);
      reedGeo.translate(0, 0.5, 0);
      const reedMesh = new THREE.InstancedMesh(reedGeo, new THREE.MeshLambertMaterial({ color: 0xffffff, side: THREE.DoubleSide }), reeds.length);
      const cattails = [];
      reeds.forEach(([x, z], i) => {
        const h = 1.2 + rnd() * 1.0;
        e.set((rnd() - 0.5) * 0.25, rnd() * 6.28, (rnd() - 0.5) * 0.25);
        q.setFromEuler(e);
        m4.compose(v.set(x, Math.max(-0.4, terrainH(x, z) - 0.1), z), q, sc.set(0.7 + rnd() * 0.6, h, 0.7 + rnd() * 0.6));
        reedMesh.setMatrixAt(i, m4);
        reedMesh.setColorAt(i, col.setHex(rnd() < 0.7 ? 0x6b8a3a : 0x9a9a52));
        if (rnd() < 0.35) cattails.push([x + (rnd() - 0.5) * 0.4, z + (rnd() - 0.5) * 0.4, Math.max(-0.4, terrainH(x, z)) + h * 0.95]);
      });
      islandsGroup.add(reedMesh);

      const catMesh = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.07, 0.07, 0.35, 5), new THREE.MeshLambertMaterial({ color: 0x5a3a1e }), cattails.length);
      cattails.forEach(([x, z, y], i) => {
        m4.makeTranslation(x, y, z);
        catMesh.setMatrixAt(i, m4);
      });
      islandsGroup.add(catMesh);

      const padGeo = new THREE.CircleGeometry(0.75, 9, 0.35, Math.PI * 2 - 0.35);
      padGeo.rotateX(-Math.PI / 2);
      const padMesh = new THREE.InstancedMesh(padGeo, new THREE.MeshLambertMaterial({ color: 0xffffff }), pads.length);
      const blooms = [];
      pads.forEach(([x, z, r], i) => {
        e.set(0, r * 6.28, 0);
        q.setFromEuler(e);
        m4.compose(v.set(x, WATER_Y + 0.03, z), q, sc.set(0.7 + r, 1, 0.7 + r));
        padMesh.setMatrixAt(i, m4);
        padMesh.setColorAt(i, col.setHex(r < 0.5 ? 0x3e7a2e : 0x4f8a34));
        if (r > 0.86) blooms.push([x, z]);
      });
      islandsGroup.add(padMesh);

      const bloomMesh = new THREE.InstancedMesh(new THREE.DodecahedronGeometry(0.22, 0), new THREE.MeshBasicMaterial({ color: 0xf5c6d8, fog: false }), blooms.length);
      blooms.forEach(([x, z], i) => {
        m4.makeTranslation(x, WATER_Y + 0.15, z);
        bloomMesh.setMatrixAt(i, m4);
      });
      islandsGroup.add(bloomMesh);
    }

    // ------------------------------------------------------------------------
    // Park Lamps, Benches & Cedar Picnic Tables
    // ------------------------------------------------------------------------
    {
      const lamps = [];
      PATHS.forEach(p => {
        if (p.w < 5) return;
        let carry = 10, side = 1;
        for (let s = 1; s < p.pts.length; s++) {
          const a = p.pts[s - 1], b = p.pts[s], L = Math.hypot(b[0] - a[0], b[1] - a[1]);
          const nx = -(b[1] - a[1]) / L, nz = (b[0] - a[0]) / L;
          let t = carry;
          while (t < L) {
            const x = a[0] + (b[0] - a[0]) * t / L + nx * side * (p.w / 2 + 0.8);
            const z = a[1] + (b[1] - a[1]) * t / L + nz * side * (p.w / 2 + 0.8);
            if (landField(x, z) > 2 && !getIslandBridgeAt(x, z, 2)) lamps.push([x, z]);
            side = -side;
            t += 34;
          }
          carry = t - L;
        }
      });

      const m4 = new THREE.Matrix4();
      const post = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.07, 0.1, 4, 6), new THREE.MeshLambertMaterial({ color: 0x1f2a24 }), lamps.length);
      const head = new THREE.InstancedMesh(new THREE.SphereGeometry(0.28, 8, 6), lampGlowMat, lamps.length);
      lamps.forEach(([x, z], i) => {
        const y = terrainH(x, z);
        m4.makeTranslation(x, y + 2, z);
        post.setMatrixAt(i, m4);
        m4.makeTranslation(x, y + 4.1, z);
        head.setMatrixAt(i, m4);
        circOb(x, z, 0.25);
      });
      islandsGroup.add(post, head);

      // Picnic tables in glades & meadows
      const tables = [];
      for (let k = 0; k < 900 && tables.length < 70; k++) {
        const c = CLEARINGS[Math.floor(rnd() * CLEARINGS.length)];
        if (!c.c || c.c[2] < 30) continue;
        const a = rnd() * 6.283, d = rnd() * c.c[2] * 0.85;
        const x = c.c[0] + Math.cos(a) * d, z = c.c[1] + Math.sin(a) * d;
        if (landField(x, z) < 4 || nearPath(x, z, 3) || isSand(x, z, 9)) continue;
        if (tables.some(t => Math.hypot(t[0] - x, t[1] - z) < 9)) continue;
        tables.push([x, z, rnd() * 3.14]);
      }
      const top = new THREE.InstancedMesh(new THREE.BoxGeometry(1.8, 0.08, 0.8), woodMat, tables.length);
      const bench = new THREE.InstancedMesh(new THREE.BoxGeometry(1.8, 0.06, 0.3), woodMat, tables.length * 2);
      const legs = new THREE.InstancedMesh(new THREE.BoxGeometry(0.1, 0.75, 1.9), darkWoodMat, tables.length * 2);
      const q = new THREE.Quaternion(), v = new THREE.Vector3(), one = new THREE.Vector3(1, 1, 1), up = new THREE.Vector3(0, 1, 0), off = new THREE.Vector3();
      tables.forEach(([x, z, rot], i) => {
        const y = terrainH(x, z);
        q.setFromAxisAngle(up, rot);
        m4.compose(v.set(x, y + 0.78, z), q, one);
        top.setMatrixAt(i, m4);
        [-1, 1].forEach((sd, k) => {
          const bx = -Math.sin(rot) * sd * 0.65, bz = Math.cos(rot) * sd * 0.65;
          m4.compose(v.set(x + bx, y + 0.45, z + bz), q, one);
          bench.setMatrixAt(i * 2 + k, m4);
          const lx = Math.cos(rot) * sd * 0.75, lz = Math.sin(rot) * sd * 0.75;
          m4.compose(v.set(x + lx, y + 0.38, z + lz), q, one);
          legs.setMatrixAt(i * 2 + k, m4);
        });
        circOb(x, z, 1.0);
      });
      islandsGroup.add(top, bench, legs);
    }

    // ------------------------------------------------------------------------
    // Landmark: Centre Island Ferry Terminal
    // ------------------------------------------------------------------------
    {
      const termGrp = new THREE.Group();
      const canopy = new THREE.Mesh(new THREE.BoxGeometry(26, 0.8, 16), darkWoodMat);
      canopy.position.set(0, 4.8, Z(6));
      termGrp.add(canopy);
      const roof = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 9.5, 3.2, 4, 1), new THREE.MeshStandardMaterial({ color: 0x2f5a3a, roughness: 0.7 }));
      roof.scale.set(1.45, 1, 0.9);
      roof.rotation.y = Math.PI / 4;
      roof.position.set(0, 6.8, Z(6));
      termGrp.add(roof);
      [-11, 11].forEach(cx => [Z(0), Z(12)].forEach(cz => {
        const p = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 4.8, 8), darkWoodMat);
        p.position.set(cx, 2.4, cz);
        termGrp.add(p);
        circOb(cx, cz, 0.4);
      }));
      const sNorth = makeSign(['CENTRE ISLAND FERRY TERMINAL', 'TORONTO ISLAND PARK'], 18, 2.4, { bg: '#064e3b', fg: '#fef08a', borderColor: '#10b981' });
      sNorth.position.set(0, 5.9, Z(14.2));
      termGrp.add(sNorth);
      const sSouth = makeSign(['TORONTO ISLAND FERRIES', 'TO JACK LAYTON FERRY TERMINAL'], 16, 2.0, { bg: '#1e3a8a', fg: '#bae6fd', borderColor: '#0284c7' });
      sSouth.position.set(0, 5.9, Z(-2.2));
      sSouth.rotation.y = Math.PI;
      termGrp.add(sSouth);
      islandsGroup.add(termGrp);
    }

    // ------------------------------------------------------------------------
    // Landmark: Avenue of the Islands - Flowerbeds, Grand Fountain, Formal Garden
    // ------------------------------------------------------------------------
    let fountainSpray = null;
    {
      const avg = new THREE.Group();
      const flowerCols = [0xef4444, 0xfacc15, 0xa855f7, 0xf472b6, 0xffffff, 0xfb923c];
      const blooms = [];
      for (let fz = Z(30); fz <= Z(210); fz += 24) {
        if (Math.abs(fz - Z(130)) < 14) continue; // leave room for the Grand Fountain
        [-9.5, 9.5].forEach((fx, fi) => {
          const bed = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.45, 12), stoneMat);
          bed.position.set(fx, GROUND_Y + 0.1, fz);
          avg.add(bed);
          rectOb(fx - 1.75, fx + 1.75, fz - 6, fz + 6);
          const col = flowerCols[(fi + Math.round(fz / 24)) % flowerCols.length];
          for (let fl = -5; fl <= 5; fl += 0.9) {
            for (let w = -1.1; w <= 1.1; w += 0.73) blooms.push([fx + w, fz + fl, col]);
          }
        });
      }

      // Formal garden parterre with sundial
      const gx0 = 30, gx1 = 96, gz0 = Z(24), gz1 = Z(90);
      const hedges = [];
      const hedge = (x0, z0, x1, z1) => {
        const len = Math.hypot(x1 - x0, z1 - z0);
        const h = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.85, len), hedgeMat);
        h.position.set((x0 + x1) / 2, GROUND_Y + 0.42, (z0 + z1) / 2);
        h.rotation.y = Math.atan2(x1 - x0, z1 - z0);
        avg.add(h);
        rectOb(Math.min(x0, x1) - 0.4, Math.max(x0, x1) + 0.4, Math.min(z0, z1) - 0.4, Math.max(z0, z1) + 0.4);
      };
      hedge(gx0, gz0, gx1, gz0); hedge(gx1, gz0, gx1, gz1); hedge(gx1, gz1, gx0, gz1); hedge(gx0, gz1, gx0, gz0);
      hedge(gx0 + 16, gz0 + 14, gx1 - 16, gz0 + 14); hedge(gx0 + 16, gz1 - 14, gx1 - 16, gz1 - 14);
      const dial = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.5, 1.1, 8), stoneMat);
      dial.position.set((gx0 + gx1) / 2, GROUND_Y + 0.55, (gz0 + gz1) / 2);
      avg.add(dial);
      circOb((gx0 + gx1) / 2, (gz0 + gz1) / 2, 0.5);

      // Grand Fountain at Avenue centre
      const fz = Z(130);
      const pool = new THREE.Mesh(new THREE.CylinderGeometry(10, 10.8, 1.2, 24), stoneMat);
      pool.position.set(0, GROUND_Y + 0.4, fz);
      avg.add(pool);

      const waterSurf = new THREE.Mesh(new THREE.CircleGeometry(9.4, 24), new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, metalness: 0.4 }));
      waterSurf.rotation.x = -Math.PI / 2;
      waterSurf.position.set(0, GROUND_Y + 0.95, fz);
      avg.add(waterSurf);

      const tier1 = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 5.0, 1.4, 16), stoneMat);
      tier1.position.set(0, GROUND_Y + 1.4, fz);
      avg.add(tier1);
      const tier2 = new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.4, 1.6, 16), stoneMat);
      tier2.position.set(0, GROUND_Y + 2.7, fz);
      avg.add(tier2);

      fountainSpray = new THREE.Mesh(
        new THREE.ConeGeometry(0.8, 6.0, 12, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75, fog: false })
      );
      fountainSpray.position.set(0, GROUND_Y + 6.0, fz);
      avg.add(fountainSpray);

      // Instanced flower blooms
      const m4 = new THREE.Matrix4(), col = new THREE.Color();
      const flGeo = new THREE.DodecahedronGeometry(0.18, 0);
      const flMesh = new THREE.InstancedMesh(flGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false }), blooms.length);
      blooms.forEach(([x, z, c], i) => {
        m4.makeTranslation(x, GROUND_Y + 0.35, z);
        flMesh.setMatrixAt(i, m4);
        flMesh.setColorAt(i, col.setHex(c));
      });
      avg.add(flMesh);
      islandsGroup.add(avg);
    }

    // ------------------------------------------------------------------------
    // Landmark: William Meany Hedge Maze (Authentic Real-World Location on EAST side)
    // Situated at x = 105, z = Z(175) with Dirt-colored ground and the 1888 antique school bell!
    // ------------------------------------------------------------------------
    {
      const hmg = new THREE.Group();
      const hx = 105, hz = Z(175);

      // Earth-toned packed dirt ground so green cedar hedges stand out sharply
      const mazeGround = new THREE.Mesh(new THREE.BoxGeometry(76, 0.08, 76), dirtMat);
      mazeGround.position.set(hx, 0.57, hz);
      mazeGround.receiveShadow = true;
      hmg.add(mazeGround);

      // Entrance Gate Arch & Commemorative Plaque Sign
      const mSign = makeSign(
        ['WILLIAM MEANY HEDGE MAZE', 'DONATED 2015 • HISTORIC 1888 SCHOOL BELL'],
        18, 2.4,
        { bg: '#14532d', fg: '#bbf7d0', borderColor: '#22c55e' }
      );
      mSign.position.set(hx, 3.8, hz - 37);
      hmg.add(mSign);

      function addMazeWall(wx, wz, ww, wd) {
        const wall = new THREE.Mesh(new THREE.BoxGeometry(ww, 2.2, wd), hedgeMat);
        wall.position.set(hx + wx, 1.6, hz + wz);
        hmg.add(wall);
        rectOb(hx + wx - ww / 2, hx + wx + ww / 2, hz + wz - wd / 2, hz + wz + wd / 2);
      }

      // Outer perimeter hedge walls with entrance openings facing north & west
      addMazeWall(-20, -36, 32, 1.4);
      addMazeWall(20, -36, 32, 1.4);
      addMazeWall(-36, -20, 1.4, 32);
      addMazeWall(-36, 20, 1.4, 32);
      addMazeWall(36, 0, 1.4, 72);
      addMazeWall(0, 36, 72, 1.4);

      // Concentric inner hedge rings & labyrinth turns
      addMazeWall(-18, -24, 28, 1.2);
      addMazeWall(18, -24, 28, 1.2);
      addMazeWall(-26, 0, 1.2, 46);
      addMazeWall(26, 0, 1.2, 46);
      addMazeWall(0, 24, 52, 1.2);

      addMazeWall(-12, -12, 18, 1.2);
      addMazeWall(12, -12, 18, 1.2);
      addMazeWall(-16, 6, 1.2, 28);
      addMazeWall(16, 6, 1.2, 28);
      addMazeWall(0, 14, 32, 1.2);

      // Centerpiece: Historic 1888 Toronto Island School Bell Arbor & Bell
      const bellArbor = new THREE.Group();
      [-2.4, 2.4].forEach(px => {
        [-2.4, 2.4].forEach(pz => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.35, 3.4, 0.35), darkWoodMat);
          post.position.set(hx + px, 1.7, hz + pz);
          bellArbor.add(post);
        });
      });
      const arborBeamX1 = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.3, 0.35), darkWoodMat);
      arborBeamX1.position.set(hx, 3.4, hz - 2.4);
      bellArbor.add(arborBeamX1);
      const arborBeamX2 = new THREE.Mesh(new THREE.BoxGeometry(5.4, 0.3, 0.35), darkWoodMat);
      arborBeamX2.position.set(hx, 3.4, hz + 2.4);
      bellArbor.add(arborBeamX2);
      const arborBeamZ1 = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.3, 5.4), darkWoodMat);
      arborBeamZ1.position.set(hx - 2.4, 3.4, hz);
      bellArbor.add(arborBeamZ1);
      const arborBeamZ2 = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.3, 5.4), darkWoodMat);
      arborBeamZ2.position.set(hx + 2.4, 3.4, hz);
      bellArbor.add(arborBeamZ2);

      // Peaked cedar shake cupola roof
      const cupolaRoof = new THREE.Mesh(new THREE.ConeGeometry(4.2, 1.8, 4), darkWoodMat);
      cupolaRoof.position.set(hx, 4.4, hz);
      cupolaRoof.rotation.y = Math.PI / 4;
      bellArbor.add(cupolaRoof);

      // Historic 1888 Antique Brass Toronto Island School Bell
      const bellSupport = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.9, 8), metalMat);
      bellSupport.position.set(hx, 3.0, hz);
      bellArbor.add(bellSupport);

      const bellYoke = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.15, 0.25), darkWoodMat);
      bellYoke.position.set(hx, 2.7, hz);
      bellArbor.add(bellYoke);

      const bellBody = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.65, 0.75, 16, 1, true), bellBrassMat);
      bellBody.position.set(hx, 2.3, hz);
      bellArbor.add(bellBody);

      const bellDome = new THREE.Mesh(new THREE.SphereGeometry(0.24, 16, 8, 0, Math.PI * 2, 0, Math.PI * 0.5), bellBrassMat);
      bellDome.position.set(hx, 2.65, hz);
      bellArbor.add(bellDome);

      const clapper = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), metalMat);
      clapper.position.set(hx, 1.95, hz);
      bellArbor.add(clapper);

      const clapperRope = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.1, 6), woodMat);
      clapperRope.position.set(hx + 0.1, 1.45, hz);
      bellArbor.add(clapperRope);

      // Historic bronze plaque
      const bPlaque = makeSign(
        ['HISTORIC 1888 TORONTO ISLAND SCHOOL BELL', 'RING THE BELL TO CELEBRATE CONQUERING THE MAZE!'],
        4.0, 1.2,
        { bg: '#78350f', fg: '#fef08a', borderColor: '#d97706', titleSize: 32, subSize: 20 }
      );
      bPlaque.position.set(hx, 1.2, hz + 2.5);
      bellArbor.add(bPlaque);

      [-2.4, 2.4].forEach(px => {
        [-2.4, 2.4].forEach(pz => {
          circOb(hx + px, hz + pz, 0.35);
        });
      });
      hmg.add(bellArbor);
      islandsGroup.add(hmg);
    }

    // ------------------------------------------------------------------------
    // Landmark: Centreville Amusement Park (Ferris Wheel, Carousel, Food Court)
    // ------------------------------------------------------------------------
    let ferrisWheelMesh = null, carouselTop = null;
    {
      const cvg = new THREE.Group();

      // Giant Rotating 26m Ferris Wheel at (190, Z(125))
      const fwGrp = new THREE.Group();
      fwGrp.position.set(190, 14.5, Z(125));

      [-4.5, 4.5].forEach(lx => {
        const leg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 15.5, 8), metalMat);
        leg1.position.set(190 + lx, 7.5, Z(120));
        leg1.rotation.x = -0.35;
        cvg.add(leg1);
        const leg2 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 15.5, 8), metalMat);
        leg2.position.set(190 + lx, 7.5, Z(130));
        leg2.rotation.x = 0.35;
        cvg.add(leg2);
      });

      const wheelWheel = new THREE.Group();
      const rOuter = 11.5, rInner = 9.0;
      const rim1 = new THREE.Mesh(new THREE.TorusGeometry(rOuter, 0.22, 8, 32), metalMat);
      rim1.position.z = -1.2;
      wheelWheel.add(rim1);
      const rim2 = new THREE.Mesh(new THREE.TorusGeometry(rOuter, 0.22, 8, 32), metalMat);
      rim2.position.z = 1.2;
      wheelWheel.add(rim2);

      const nSpokes = 12;
      const cartCols = [0xef4444, 0x3b82f6, 0xfacc15, 0x10b981, 0xa855f7, 0xf97316];
      for (let i = 0; i < nSpokes; i++) {
        const ang = (i / nSpokes) * Math.PI * 2;
        const sp1 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, rOuter * 2, 6), metalMat);
        sp1.rotation.z = ang;
        sp1.position.z = -1.2;
        wheelWheel.add(sp1);
        const sp2 = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, rOuter * 2, 6), metalMat);
        sp2.rotation.z = ang;
        sp2.position.z = 1.2;
        wheelWheel.add(sp2);

        const cart = new THREE.Mesh(
          new THREE.BoxGeometry(1.8, 1.4, 2.0),
          new THREE.MeshStandardMaterial({ color: cartCols[i % cartCols.length], roughness: 0.4 })
        );
        cart.position.set(Math.cos(ang) * rOuter, Math.sin(ang) * rOuter, 0);
        wheelWheel.add(cart);
      }
      fwGrp.add(wheelWheel);
      ferrisWheelMesh = wheelWheel;
      cvg.add(fwGrp);
      circOb(190, Z(125), 5.5);

      // Vintage Spinning Carousel at (210, Z(140))
      const carBase = new THREE.Mesh(new THREE.CylinderGeometry(8.5, 9.0, 0.8, 20), woodMat);
      carBase.position.set(210, GROUND_Y + 0.4, Z(140));
      cvg.add(carBase);

      const carCenter = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 5.0, 12), metalMat);
      carCenter.position.set(210, GROUND_Y + 2.8, Z(140));
      cvg.add(carCenter);

      carouselTop = new THREE.Group();
      carouselTop.position.set(210, GROUND_Y + 4.8, Z(140));
      const canopy = new THREE.Mesh(
        new THREE.ConeGeometry(9.5, 3.2, 20),
        new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.5 })
      );
      carouselTop.add(canopy);

      for (let i = 0; i < 8; i++) {
        const ang = (i / 8) * Math.PI * 2;
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 4.2, 6), metalMat);
        pole.position.set(Math.cos(ang) * 6.5, -2.1, Math.sin(ang) * 6.5);
        carouselTop.add(pole);
        const horse = new THREE.Mesh(
          new THREE.BoxGeometry(1.4, 0.8, 0.5),
          new THREE.MeshStandardMaterial({ color: i % 2 === 0 ? 0xf8fafc : 0x78350f })
        );
        horse.position.set(Math.cos(ang) * 6.5, -2.1 + (i % 2) * 0.4, Math.sin(ang) * 6.5);
        carouselTop.add(horse);
      }
      cvg.add(carouselTop);
      circOb(210, Z(140), 9.2);

      // Centreville Food Court & Pizza Pizza at (170, Z(225))
      const fcBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(26, 5.2, 22),
        new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.6 })
      );
      fcBuilding.position.set(170, 3.1, Z(225));
      cvg.add(fcBuilding);
      rectOb(156, 184, Z(214), Z(236)); // Interior walls block collision!

      const pizzaSign = makeSign(
        ['PIZZA PIZZA', 'CENTREVILLE FOOD COURT • FRESH SLICES & PATIO'],
        14, 2.2,
        { bg: '#ea580c', fg: '#ffffff', borderColor: '#facc15' }
      );
      pizzaSign.position.set(170, 6.2, Z(213.8));
      cvg.add(pizzaSign);

      // Dining patio tables outside
      [-10, 10].forEach(ox => {
        [Z(204), Z(208)].forEach(oz => {
          const table = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.8, 12), woodMat);
          table.position.set(170 + ox, GROUND_Y + 0.4, oz);
          cvg.add(table);
          circOb(170 + ox, oz, 1.2);
        });
      });

      islandsGroup.add(cvg);
    }

    // ------------------------------------------------------------------------
    // Landmark: Gibraltar Point 1808 Lighthouse
    // ------------------------------------------------------------------------
    let lighthouseBeacon = null;
    {
      const lhg = new THREE.Group();
      const lx = -480, lz = Z(320);
      const tower = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 4.2, 24, 6), stoneMat);
      tower.position.set(lx, 12.5, lz);
      lhg.add(tower);
      circOb(lx, lz, 4.4); // Solid limestone tower blocks collision!

      const gallery = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.2, 0.8, 12), darkWoodMat);
      gallery.position.set(lx, 24.8, lz);
      lhg.add(gallery);

      const lantern = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 2.6, 12), glassMat);
      lantern.position.set(lx, 26.2, lz);
      lhg.add(lantern);

      const cap = new THREE.Mesh(new THREE.ConeGeometry(2.8, 2.4, 12), new THREE.MeshStandardMaterial({ color: 0x2f6b55, roughness: 0.4, metalness: 0.6 }));
      cap.position.set(lx, 28.4, lz);
      lhg.add(cap);

      lighthouseBeacon = new THREE.Group();
      const beam = new THREE.Mesh(
        new THREE.ConeGeometry(12, 180, 16, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xfef08a, transparent: true, opacity: 0.22, side: THREE.DoubleSide, depthWrite: false, fog: false })
      );
      beam.rotation.x = Math.PI / 2;
      beam.position.z = 90;
      lighthouseBeacon.add(beam);
      lighthouseBeacon.position.set(lx, 26.2, lz);
      lhg.add(lighthouseBeacon);

      const lhSign = makeSign(
        ['GIBRALTAR POINT LIGHTHOUSE', 'BUILT 1808 • TORONTO\'S OLDEST LANDMARK'],
        14, 2.0,
        { bg: '#1c1917', fg: '#fde047', borderColor: '#d97706' }
      );
      lhSign.position.set(lx, 2.0, lz - 9);
      lhSign.rotation.y = Math.PI;
      lhg.add(lhSign);

      islandsGroup.add(lhg);
    }

    // ------------------------------------------------------------------------
    // Landmark: Billy Bishop Toronto City Airport (CYTZ)
    // ------------------------------------------------------------------------
    let radarDish = null;
    {
      const apg = new THREE.Group();
      // Runway 08/26: 520m asphalt strip
      const runway = new THREE.Mesh(new THREE.BoxGeometry(520, 0.1, 44), asphaltMat);
      runway.position.set(-1260, GROUND_Y + 0.05, Z(-170));
      apg.add(runway);

      for (let rx = -1490; rx <= -1030; rx += 36) {
        const dash = new THREE.Mesh(new THREE.BoxGeometry(20, 0.12, 1.2), whiteMarkMat);
        dash.position.set(rx, GROUND_Y + 0.11, Z(-170));
        apg.add(dash);
      }
      [-1508, -1012].forEach(tx => {
        for (let s = -16; s <= 16; s += 4) {
          const thr = new THREE.Mesh(new THREE.BoxGeometry(16, 0.12, 1.8), whiteMarkMat);
          thr.position.set(tx, GROUND_Y + 0.11, Z(-170) + s);
          apg.add(thr);
        }
      });

      // Terminal building & control tower
      const ax = -1060, az = Z(-230);
      const term = new THREE.Mesh(new THREE.BoxGeometry(72, 8.5, 36), concreteMat);
      term.position.set(ax, 4.75, az);
      apg.add(term);
      const facade = new THREE.Mesh(new THREE.BoxGeometry(72.4, 4.5, 1.0), glassMat);
      facade.position.set(ax, 5.0, az + 18.2);
      apg.add(facade);
      const apSign = makeSign(
        ['BILLY BISHOP TORONTO CITY AIRPORT', 'ISLAND TERMINAL • WESTERN GAP'],
        24, 2.4,
        { bg: '#0f172a', fg: '#38bdf8', borderColor: '#0284c7' }
      );
      apSign.position.set(ax, 9.8, az + 18.6);
      apg.add(apSign);
      rectOb(ax - 36, ax + 36, az - 18, az + 18);

      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 3.2, 28, 12), concreteMat);
      shaft.position.set(ax + 48, 14.5, az);
      apg.add(shaft);
      const cab = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 3.6, 4.5, 12), glassMat);
      cab.position.set(ax + 48, 29.5, az);
      apg.add(cab);
      circOb(ax + 48, az, 3.3);

      radarDish = new THREE.Group();
      radarDish.add(new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.2, 0.4), metalMat));
      radarDish.position.set(ax + 48, 32.5, az);
      apg.add(radarDish);

      // Dash-8 aircraft parked at gates
      const plane = (px, pz, rotY) => {
        const pl = new THREE.Group();
        const fuse = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 26, 12), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 }));
        fuse.rotation.x = Math.PI / 2;
        pl.add(fuse);
        const navy = new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 });
        const wings = new THREE.Mesh(new THREE.BoxGeometry(28, 0.3, 3.5), navy);
        wings.position.set(0, 0.8, -2);
        pl.add(wings);
        const fin = new THREE.Mesh(new THREE.BoxGeometry(0.3, 4.5, 3.0), navy);
        fin.position.set(0, 3.2, 11);
        pl.add(fin);
        const tail = new THREE.Mesh(new THREE.BoxGeometry(8, 0.25, 2.0), navy);
        tail.position.set(0, 5.4, 11);
        pl.add(tail);
        pl.position.set(px, 2.2, pz);
        pl.rotation.y = rotY;
        apg.add(pl);
        circOb(px, pz, 9);
      };
      plane(ax - 28, az + 45, 0.3);
      plane(ax + 24, az + 55, -0.2);

      islandsGroup.add(apg);
    }

    // ------------------------------------------------------------------------
    // Landmark: Algonquin and Ward's Island Summer Cottages, Ward's Cafe
    // ------------------------------------------------------------------------
    {
      const cottGrp = new THREE.Group();
      const pastel = [0xbfdbfe, 0xbbf7d0, 0xfef08a, 0xfbcfe8, 0xe9d5ff, 0xfed7aa];

      function addCottage(cx, cz, rotY, col) {
        const c = new THREE.Group();
        const bldg = new THREE.Mesh(new THREE.BoxGeometry(8.5, 3.4, 7.0), new THREE.MeshStandardMaterial({ color: col, roughness: 0.7 }));
        bldg.position.y = 1.7;
        c.add(bldg);
        const roof = new THREE.Mesh(new THREE.ConeGeometry(6.6, 2.6, 4), darkWoodMat);
        roof.position.y = 4.4;
        roof.rotation.y = Math.PI / 4;
        c.add(roof);
        const porch = new THREE.Mesh(new THREE.BoxGeometry(7.5, 0.3, 2.2), woodMat);
        porch.position.set(0, 0.2, 4.2);
        c.add(porch);
        const fence = new THREE.Mesh(new THREE.BoxGeometry(12, 0.8, 0.1), new THREE.MeshStandardMaterial({ color: 0xf5f5f0 }));
        fence.position.set(0, 0.4, 7.5);
        c.add(fence);
        c.position.set(cx, GROUND_Y, cz);
        c.rotation.y = rotY;
        cottGrp.add(c);
        circOb(cx, cz, 5.2);
      }

      for (let i = 0; i < 8; i++) {
        addCottage(440 + (i % 4) * 36, Z(40) + Math.floor(i / 4) * 44, (i % 3) * 0.4, pastel[i % 6]);
      }
      for (let i = 0; i < 12; i++) {
        addCottage(920 + (i % 6) * 38, Z(-20) + Math.floor(i / 6) * 40, (i % 2) * 0.35, pastel[(i + 2) % 6]);
      }

      // Ward's Island Cafe & garden patio
      const cafe = new THREE.Mesh(new THREE.BoxGeometry(18, 4.2, 12), new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.6 }));
      cafe.position.set(1050, 2.65, Z(70));
      cottGrp.add(cafe);
      const cafeSign = makeSign(
        ['WARD\'S ISLAND CAFE', 'GARDEN PATIO • BAKERY'],
        14, 2.0,
        { bg: '#047857', fg: '#fef08a', borderColor: '#10b981' }
      );
      cafeSign.position.set(1050, 5.2, Z(63.8));
      cafeSign.rotation.y = Math.PI;
      cottGrp.add(cafeSign);
      rectOb(1041, 1059, Z(64), Z(76));

      islandsGroup.add(cottGrp);
    }

    // ------------------------------------------------------------------------
    // Landmark: Hanlan's Point Terminal, Ned Hanlan Statue, Ball Diamonds
    // ------------------------------------------------------------------------
    {
      const hpg = new THREE.Group();
      const hx = -720, hz = Z(-120);
      const hpSign = makeSign(
        ['HANLAN\'S POINT FERRY DOCK', 'TO JACK LAYTON FERRY TERMINAL'],
        16, 2.2,
        { bg: '#1e3a8a', fg: '#bae6fd', borderColor: '#0284c7' }
      );
      hpSign.position.set(hx, 4.2, hz + 32);
      hpg.add(hpSign);

      [-7, 7].forEach(o => {
        const p = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 4.2, 6), darkWoodMat);
        p.position.set(hx + o, 2.1, hz + 32);
        hpg.add(p);
        circOb(hx + o, hz + 32, 0.3);
      });

      const plinth = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.8, 3.2), stoneMat);
      plinth.position.set(hx + 35, 1.4, hz + 35);
      hpg.add(plinth);
      const statue = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 2.4, 8), new THREE.MeshStandardMaterial({ color: 0x6b4423, metalness: 0.8, roughness: 0.3 }));
      statue.position.set(hx + 35, 3.4, hz + 35);
      hpg.add(statue);
      circOb(hx + 35, hz + 35, 2.3);

      // Two baseball diamonds
      const dirt = new THREE.MeshLambertMaterial({ color: 0xa0704a });
      [[-800, Z(-25), 0.6], [-760, Z(40), 2.4]].forEach(([dx, dz, rot]) => {
        const inf = new THREE.Mesh(new THREE.CircleGeometry(20, 24, -Math.PI / 4, Math.PI / 2), dirt);
        inf.rotation.x = -Math.PI / 2;
        inf.rotation.z = rot;
        inf.position.set(dx, GROUND_Y + 0.03, dz);
        hpg.add(inf);
        const back = new THREE.Mesh(new THREE.BoxGeometry(10, 3.5, 0.15), new THREE.MeshStandardMaterial({ color: 0x9ca3af, metalness: 0.6, roughness: 0.4, transparent: true, opacity: 0.6 }));
        back.position.set(dx - Math.sin(rot) * 4, GROUND_Y + 1.75, dz - Math.cos(rot) * 4);
        back.rotation.y = rot;
        hpg.add(back);
      });

      islandsGroup.add(hpg);
    }

    // ------------------------------------------------------------------------
    // Beach Details: Lifeguard Stands & Pier Railing
    // ------------------------------------------------------------------------
    {
      const bg = new THREE.Group();
      [[-200, Z(470)], [200, Z(465)], [700, Z(395)], [1180, Z(175)], [-880, Z(150)]].forEach(([x, z]) => {
        const y = terrainH(x, z);
        const seat = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.2, 1.2), new THREE.MeshStandardMaterial({ color: 0xffffff }));
        seat.position.set(x, y + 2.6, z);
        bg.add(seat);
        [-0.6, 0.6].forEach(o => {
          [-0.5, 0.5].forEach(p => {
            const l = new THREE.Mesh(new THREE.BoxGeometry(0.12, 2.6, 0.12), new THREE.MeshStandardMaterial({ color: 0xf8fafc }));
            l.position.set(x + o, y + 1.3, z + p);
            bg.add(l);
          });
        });
        const flag = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.6, 0.9), new THREE.MeshBasicMaterial({ color: 0xdc2626, fog: false }));
        flag.position.set(x + 0.7, y + 3.6, z);
        bg.add(flag);
        circOb(x, z, 1.0);
      });
      islandsGroup.add(bg);
    }

    // ------------------------------------------------------------------------
    // Wildlife and Boats: Swimming Swans, Moored Canoes, Harbour Ferry
    // ------------------------------------------------------------------------
    const swimmers = [];
    {
      const white = new THREE.MeshLambertMaterial({ color: 0xffffff });
      const beak = new THREE.MeshLambertMaterial({ color: 0xea580c });
      function makeSwan() {
        const sw = new THREE.Group();
        const body = new THREE.Mesh(new THREE.SphereGeometry(0.45, 12, 8), white);
        body.scale.set(1.4, 0.75, 0.85);
        sw.add(body);
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.12, 0.65, 8), white);
        neck.position.set(0.4, 0.35, 0);
        neck.rotation.z = -0.35;
        sw.add(neck);
        const head = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), white);
        head.position.set(0.52, 0.68, 0);
        sw.add(head);
        const bk = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.22, 6), beak);
        bk.position.set(0.66, 0.65, 0);
        bk.rotation.z = -Math.PI / 2;
        sw.add(bk);
        return sw;
      }

      function makeCanoe(col) {
        const cn = new THREE.Group();
        const hull = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.55, 0.8), new THREE.MeshStandardMaterial({ color: col, roughness: 0.6 }));
        hull.position.y = 0.2;
        cn.add(hull);
        const seat = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.08, 0.7), darkWoodMat);
        seat.position.set(-0.6, 0.35, 0);
        cn.add(seat);
        return cn;
      }

      function lanePoint(ch, dist) {
        let acc = 0;
        for (let i = 1; i < ch.pts.length; i++) {
          const a = ch.pts[i - 1], b = ch.pts[i], seg = Math.hypot(b[0] - a[0], b[1] - a[1]);
          if (acc + seg >= dist || i === ch.pts.length - 1) {
            const t = Math.max(0, Math.min(1, (dist - acc) / seg));
            const tx = (b[0] - a[0]) / seg, tz = (b[1] - a[1]) / seg;
            return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, tx, tz];
          }
          acc += seg;
        }
        return [ch.pts[0][0], ch.pts[0][1], 1, 0];
      }

      const activeChannels = [CHANNELS[0], CHANNELS[1], CHANNELS[3]];
      activeChannels.forEach((ch, ci) => {
        let total = 0;
        for (let i = 1; i < ch.pts.length; i++) total += Math.hypot(ch.pts[i][0] - ch.pts[i - 1][0], ch.pts[i][1] - ch.pts[i - 1][1]);
        for (let k = 0; k < 3; k++) {
          const sw = makeSwan();
          islandsGroup.add(sw);
          swimmers.push({
            obj: sw,
            ch,
            L: total,
            s: (total / 3) * k + ci * 12,
            speed: 1.2 + rnd() * 0.7,
            dir: k % 2 === 0 ? 1 : -1,
            lane: (rnd() - 0.5) * (ch.w * 0.4),
            bob: rnd() * 6.28
          });
        }
      });

      // Moored canoes
      [[-60, Z(255), 0.4, 0x15803d], [140, Z(265), -0.3, 0xb91c1c], [260, Z(385), 0.7, 0x1d4ed8]].forEach(([x, z, r, c]) => {
        const cn = makeCanoe(c);
        cn.position.set(x, WATER_Y, z);
        cn.rotation.y = r;
        islandsGroup.add(cn);
        circOb(x, z, 1.8);
      });
    }

    // Animated Toronto Harbour Ferry
    let ferry = null;
    {
      ferry = new THREE.Group();
      const hull = new THREE.Mesh(new THREE.BoxGeometry(10, 3.2, 36), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 }));
      hull.position.y = 1.2;
      ferry.add(hull);
      const cabin = new THREE.Mesh(new THREE.BoxGeometry(8.2, 2.8, 22), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 }));
      cabin.position.set(0, 4.0, -1);
      ferry.add(cabin);
      const bridge = new THREE.Mesh(new THREE.BoxGeometry(7.0, 2.2, 7.0), glassMat);
      bridge.position.set(0, 6.4, 4);
      ferry.add(bridge);
      const funnel = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.9, 3.4, 12), new THREE.MeshStandardMaterial({ color: 0xdc2626 }));
      funnel.position.set(0, 7.0, -5);
      ferry.add(funnel);
      ferry.position.set(0, 0, Z(-60));
      islandsGroup.add(ferry);
    }

    // ------------------------------------------------------------------------
    // Distant 3D Toronto Skyline across Toronto Harbour
    // ------------------------------------------------------------------------
    {
      const skyGrp = new THREE.Group();
      const skyZ = Z(-1600);
      // CN Tower (553m)
      const cn = new THREE.Group();
      const base = new THREE.Mesh(new THREE.ConeGeometry(22, 180, 3), concreteMat);
      base.position.y = 90;
      cn.add(base);
      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 5.8, 260, 12), concreteMat);
      shaft.position.y = 230;
      cn.add(shaft);
      const pod = new THREE.Mesh(new THREE.CylinderGeometry(18, 14, 16, 16), concreteMat);
      pod.position.y = 350;
      cn.add(pod);
      const glassBand = new THREE.Mesh(new THREE.CylinderGeometry(18.2, 18.2, 4.5, 16), glassMat);
      glassBand.position.y = 350;
      cn.add(glassBand);
      const skyPod = new THREE.Mesh(new THREE.CylinderGeometry(9, 7.5, 9, 12), concreteMat);
      skyPod.position.y = 430;
      cn.add(skyPod);
      const spire = new THREE.Mesh(new THREE.ConeGeometry(1.6, 120, 8), metalMat);
      spire.position.y = 495;
      cn.add(spire);
      cn.position.set(-280, 0, skyZ);
      skyGrp.add(cn);

      // Rogers Centre dome
      const dome = new THREE.Mesh(new THREE.SphereGeometry(44, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.48), concreteMat);
      dome.position.set(-440, 22, skyZ + 40);
      skyGrp.add(dome);

      // Financial District Skyscrapers
      const tower = (tx, tw, th, td, col, dz) => {
        const b = new THREE.Mesh(new THREE.BoxGeometry(tw, th, td), new THREE.MeshStandardMaterial({ color: col, roughness: 0.3, metalness: 0.6 }));
        b.position.set(tx, th / 2, skyZ + (dz || 0));
        skyGrp.add(b);
      };
      tower(100, 36, 298, 36, 0xf1f5f9);
      tower(180, 32, 275, 32, 0x991b1b);
      tower(-40, 42, 222, 42, 0x18181b);
      tower(280, 34, 260, 34, 0x38bdf8);
      tower(-120, 38, 210, 38, 0xc9a24a);
      tower(420, 48, 140, 38, 0x0284c7);
      for (let k = 0; k < 40; k++) {
        tower(-700 + k * 36 + rnd() * 10, 18 + rnd() * 20, 40 + rnd() * 140, 18 + rnd() * 16, [0x334155, 0x475569, 0x1e3a5f, 0x64748b][k % 4], 60 + rnd() * 120);
      }
      islandsGroup.add(skyGrp);
    }

    scene.add(islandsGroup);

    // ------------------------------------------------------------------------
    // Collision and Walkability API
    // ------------------------------------------------------------------------
    function isInsideIslands(x, z) {
      return z >= Z(-400) && z <= Z(650) && x >= -1650 && x <= 1500;
    }

    function canMoveTo(x, z, radius, y) {
      const r = radius || 0.4;
      if (getIslandBridgeAt(x, z)) return true;
      if (pierAt(x, z)) return !blocked(x, z, r);
      if (blocked(x, z, r)) return false;
      if (trunkBlocked(x, z, r)) return false;
      return landField(x, z) > 0.9; // Shoreline and open water block walking
    }

    function floorAt(x, z, y) {
      const b = getIslandBridgeAt(x, z);
      if (b) {
        const t = Math.max(0, Math.min(1, ((x - b.x0) * b.fx + (z - b.z0) * b.fz) / b.len));
        return b.yBase + Math.sin(t * Math.PI) * b.archH + 0.15;
      }
      const p = pierAt(x, z);
      if (p) return p.y;
      const h = Math.max(0, terrainH(x, z));
      if (distLine(x, z, BOARDWALK.pts) < BOARDWALK.w / 2) return h + 0.32;
      return h;
    }

    function getNeighborhood(x, z) {
      if (isAirport(x, z)) return 'BILLY BISHOP AIRPORT (CYTZ)';
      const b = getIslandBridgeAt(x, z, 2);
      if (b) return b.name.toUpperCase();
      if (pierAt(x, z)) return pierAt(x, z).name.toUpperCase();
      for (const p of PONDS) {
        if (Math.hypot(x - p.x, z - p.z) < p.r + 12) return p.name.toUpperCase();
      }
      for (const c of CHANNELS) {
        if (distLine(x, z, c.pts) < c.w / 2 + 10) return c.name.toUpperCase();
      }
      if (x >= 65 && x <= 145 && z >= Z(135) && z <= Z(215)) return 'WILLIAM MEANY HEDGE MAZE';
      if (Math.hypot(x - 170, z - Z(225)) < 24) return 'FOOD COURT • CENTREVILLE';
      if (x >= 50 && x <= 300 && z >= Z(80) && z <= Z(270)) return 'CENTREVILLE AMUSEMENT PARK';
      if (x >= 28 && x <= 98 && z >= Z(22) && z <= Z(92)) return 'FORMAL GARDEN';
      if (Math.hypot(x + 480, z - Z(320)) < 45) return 'GIBRALTAR POINT • 1808 LIGHTHOUSE';
      if (Math.hypot(x + 160, z - Z(330)) < 70) return 'OLYMPIC ISLAND';
      if (Math.hypot(x + 780, z - Z(0)) < 85) return 'HANLAN\'S POINT • BALL DIAMONDS';
      const L = landField(x, z);
      if (x > -905 && zS(x) - z < 60) {
        if (x < -560) return 'HANLAN\'S BEACH';
        if (x < -280) return 'GIBRALTAR POINT BEACH';
        if (x < 300) return 'CENTRE ISLAND BEACH & PIER';
        return 'WARD\'S ISLAND BEACH & BOARDWALK';
      }
      if (x > 380 && x < 740 && z < Z(195)) return 'ALGONQUIN ISLAND • COTTAGES';
      if (x > 760) return 'WARD\'S ISLAND • SUMMER VILLAGE';
      if (x < -560) return 'HANLAN\'S POINT';
      if (forestDensity(x, z, L) > 0.5) return 'ISLAND WOODS • FOREST TRAIL';
      if (Math.abs(x) < 45 && z < Z(245)) return 'AVENUE OF THE ISLANDS • GARDENS';
      if (x < -280) return 'GIBRALTAR POINT WOODS';
      return 'CENTRE ISLAND PARK';
    }

    // ------------------------------------------------------------------------
    // Animation Loop
    // ------------------------------------------------------------------------
    let tTime = 0, ferryT = 0;
    function update(dt, playerPos) {
      tTime += dt;
      if (ferrisWheelMesh) ferrisWheelMesh.rotation.x += dt * 0.22;
      if (carouselTop) carouselTop.rotation.y += dt * 0.6;
      if (fountainSpray) fountainSpray.scale.y = 0.95 + Math.sin(tTime * 4.5) * 0.12;
      if (lighthouseBeacon) lighthouseBeacon.rotation.y += dt * 1.8;
      if (radarDish) radarDish.rotation.y += dt * 3.2;

      swimmers.forEach(sw => {
        sw.s += sw.dir * sw.speed * dt;
        if (sw.s < 3) { sw.s = 3; sw.dir = 1; }
        if (sw.s > sw.L - 3) { sw.s = sw.L - 3; sw.dir = -1; }
        const [x, z, tx, tz] = lanePoint(sw.ch, sw.s);
        sw.obj.position.set(x - tz * sw.lane, WATER_Y + Math.sin(tTime * 1.3 + sw.bob) * 0.04, z + tx * sw.lane);
        sw.obj.rotation.y = Math.atan2(tx * sw.dir, tz * sw.dir);
      });

      // Ferry: 70 s round trip, docking for 12 s at each end
      if (ferry) {
        ferryT = (ferryT + dt) % 70;
        const k = ferryT < 12 ? 0 : ferryT < 35 ? (ferryT - 12) / 23 : ferryT < 47 ? 1 : 1 - (ferryT - 47) / 23;
        const e = k * k * (3 - 2 * k);
        ferry.position.set(0, 0, Z(-60) - e * 700);
      }
    }

    // ------------------------------------------------------------------------
    // Minimap: Pre-rendered Terrain Canvas & Player-Centred Window
    // ------------------------------------------------------------------------
    const MM = document.createElement('canvas');
    MM.width = NX;
    MM.height = NZ;
    {
      const g = MM.getContext('2d');
      if (g && g.createImageData) {
        const img = g.createImageData(NX, NZ);
        for (let j = 0; j < NZ; j++) {
          for (let i = 0; i < NX; i++) {
            const L = Lgrid[j * NX + i], x = GX0 + i * STEP, z = GZ0 + j * STEP, o = (j * NX + i) * 4;
            let c;
            if (L <= 0) c = L > -3 ? [40, 120, 150] : [20, 82, 120];
            else if (isAirport(x, z)) c = [110, 112, 118];
            else if (isSand(x, z, L)) c = [222, 204, 150];
            else {
              const f = forestDensity(x, z, L);
              c = f > 0.35 ? [30, 84, 40] : [74, 150, 64];
            }
            img.data[o] = c[0];
            img.data[o + 1] = c[1];
            img.data[o + 2] = c[2];
            img.data[o + 3] = 255;
          }
        }
        g.putImageData(img, 0, 0);
        const toPx = (x, z) => [(x - GX0) / STEP, (z - GZ0) / STEP];
        g.lineCap = 'round';
        PATHS.forEach(p => {
          g.strokeStyle = p.kind === 'boardwalk' ? '#b08a5a' : (p.kind === 'gravel' ? '#e5dcc6' : '#cbd5e1');
          g.lineWidth = Math.max(1, p.w / STEP);
          g.beginPath();
          p.pts.forEach((q, i) => {
            const [a, b] = toPx(q[0], q[1]);
            i ? g.lineTo(a, b) : g.moveTo(a, b);
          });
          g.stroke();
        });
        g.strokeStyle = '#8b5a2b';
        g.lineWidth = 2;
        bridges.forEach(b => {
          const a = toPx(b.x0, b.z0), c = toPx(b.x1, b.z1);
          g.beginPath();
          g.moveTo(a[0], a[1]);
          g.lineTo(c[0], c[1]);
          g.stroke();
        });
      }
    }

    function drawMinimap(ctx, size, playerPos, playerYaw, dots) {
      if (!ctx) return;
      const VIEW = 700; // metres across
      const sx = (playerPos.x - VIEW / 2 - GX0) / STEP, sz = (playerPos.z - VIEW / 2 - GZ0) / STEP;
      ctx.fillStyle = '#145276';
      ctx.fillRect(0, 0, size, size);

      if (ctx.drawImage) {
        ctx.imageSmoothingEnabled = true;
        ctx.drawImage(MM, sx, sz, VIEW / STEP, VIEW / STEP, 0, 0, size, size);
      }

      const toM = (x, z) => [(x - playerPos.x) / VIEW * size + size / 2, (z - playerPos.z) / VIEW * size + size / 2];
      ctx.font = 'bold 9px sans-serif';
      ctx.fillStyle = '#f8fafc';
      [
        ['FERRY', 0, Z(-5)],
        ['AIRPORT', -1260, Z(-200)],
        ['LIGHTHOUSE', -480, Z(320)],
        ['CENTREVILLE', 170, Z(150)],
        ['MAZE', 105, Z(175)],
        ['WARD\'S', 1000, Z(30)],
        ['ALGONQUIN', 520, Z(60)],
        ['HANLAN\'S', -760, Z(-40)],
        ['OLYMPIC', -160, Z(330)]
      ].forEach(([t, x, z]) => {
        const [a, b] = toM(x, z);
        if (a > -40 && a < size + 40 && b > 0 && b < size) {
          ctx.fillText(t, a - ctx.measureText(t).width / 2, b);
        }
      });

      (dots || []).forEach(d => {
        const [a, b] = toM(d.x, d.z);
        if (a < 0 || b < 0 || a > size || b > size) return;
        ctx.fillStyle = d.c || '#ef4444';
        ctx.beginPath();
        ctx.arc(a, b, d.r || 2.5, 0, Math.PI * 2);
        ctx.fill();
      });

      ctx.save();
      ctx.translate(size / 2, size / 2);
      ctx.rotate(-playerYaw);
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.moveTo(0, -7);
      ctx.lineTo(5, 6);
      ctx.lineTo(0, 3);
      ctx.lineTo(-5, 6);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.strokeRect(1, 1, size - 2, size - 2);
    }

    return {
      group: islandsGroup,
      Z_BASE,
      isInsideIslands,
      canMoveTo,
      floorAt,
      getNeighborhood,
      drawMinimap,
      update,
      landmarks: {
        centreDock: [0, Z(0)],
        avenueGardens: [0, Z(130)],
        hedgeMaze: [105, Z(175)], // Authenticated real-world location on east side of Avenue of the Island
        centreville: [190, Z(130)],
        pizzaPizza: [170, Z(225)], // Centreville food court
        centreBeach: [0, Z(455)],
        centrePier: [0, Z(530)],
        olympicIsland: [-160, Z(330)],
        gibraltarLighthouse: [-480, Z(320)],
        hanlansDock: [-720, Z(-90)],
        hanlansBeach: [-886, Z(100)],
        airportRunway: [-1260, Z(-170)],
        airportTerminal: [-1060, Z(-200)],
        algonquinIsland: [540, Z(130)],
        wardsDock: [1140, Z(-5)],
        wardsBeach: [1210, Z(120)],
        wardsCafe: [1050, Z(85)],
        formalGarden: [63, Z(57)],
        longPond: [100, Z(255)]
      },
      stats: {
        trees: trees.round.length + trees.willow.length + trees.pine.length,
        willows: trees.willow.length,
        pines: trees.pine.length,
        shrubs: shrubs.length
      }
    };
  }

  window.buildTorontoIslands = buildTorontoIslands;
})();
'''

def main():
    print(f"Writing complete Toronto Islands code to {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write(CODE.strip() + '\n')
    print("Done! File size:", len(CODE), "bytes.")

if __name__ == '__main__':
    main()
