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
      // North Lagoon Channel: flows between the North Arrival Island and Centreville/park mainland under North Arrival Bridge (x=28, z=Z(118..158))
      { name: 'North Lagoon Channel', w: 26, pts: [[-120, Z(138)], [-40, Z(138)], [28, Z(138)], [100, Z(138)], [170, Z(145)]] },
      // Manitou Lagoon / Long Pond: spans under Manitou Bridge (0, Z(230..280))
      { name: 'Long Pond', w: 38, pts: [[-290, Z(255)], [-150, Z(255)], [0, Z(255)], [80, Z(255)], [180, Z(255)], [330, Z(260)]] },
      // Blockhouse Bay: runs between Olympic Island and Gibraltar Point, passing under Olympic-Gibraltar bridge (x=-340, z=Z(318))
      { name: 'Blockhouse Bay', w: 36, pts: [[-340, Z(220)], [-340, Z(280)], [-340, Z(318)], [-350, Z(380)], [-420, Z(430)]] },
      // South Lagoon: winds behind Centre Island dunes flanking the formal gardens to the west and east
      { name: 'South Lagoon West', w: 26, pts: [[-260, Z(370)], [-180, Z(360)], [-100, Z(365)], [-52, Z(340)]] },
      { name: 'South Lagoon East', w: 26, pts: [[52, Z(340)], [100, Z(365)], [180, Z(360)], [260, Z(370)]] },
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
      // North Island Ferry Promenade: starts at Ferry Terminal (0, Z(-5)), curves gently east, then south towards the first bridge
      { name: 'North Island Promenade', w: 10, kind: 'paved', pts: [[0, Z(-5)], [0, Z(15)], [14, Z(35)], [24, Z(60)], [28, Z(90)], [28, Z(120)]] },
      // Avenue of the Islands south: continues south across Manitou Bridge towards Grand Fountain (Z(310)), Formal Gardens (Z(345-415)), and South Beach (Z(455))
      { name: 'Avenue of the Islands', w: 10, kind: 'gravel', pts: [[28, Z(158)], [12, Z(195)], [0, Z(230)], [0, Z(280)], [0, Z(465)]] },
      // Wooded Path to Centreville: shaded winding trail branching east into the dense forest to discover Centreville
      { name: 'Wooded Path to Centreville', w: 6, kind: 'gravel', pts: [[28, Z(158)], [55, Z(175)], [90, Z(190)], [125, Z(200)], [150, Z(200)]] },
      // Centreville Village Midway: paved promenade through turn-of-the-century Victorian village square
      { name: 'Centreville Village Midway', w: 8, kind: 'paved', pts: [[150, Z(200)], [175, Z(200)], [205, Z(195)], [235, Z(190)]] },
      // Far Enough Farm Lane: rustic trail leading east to the historic farm
      { name: 'Far Enough Farm Lane', w: 5, kind: 'gravel', pts: [[235, Z(190)], [265, Z(185)], [295, Z(180)], [330, Z(175)]] },
      { name: 'Maze Promenade Link', w: 6, kind: 'gravel', pts: [[0, Z(385)], [-30, Z(385)]] },
      { name: 'West Garden Promenade', w: 4, kind: 'gravel', pts: [[-10, Z(330)], [-36, Z(330)], [-36, Z(425)], [-10, Z(425)]] },
      { name: 'East Garden Promenade', w: 4, kind: 'gravel', pts: [[10, Z(330)], [36, Z(330)], [36, Z(425)], [10, Z(425)]] },
      { name: 'Cibola Avenue', w: 6, kind: 'paved', pts: [[28, Z(60)], [80, Z(70)], [150, Z(60)], [338, Z(66)], [392, Z(94)], [520, Z(100)], [620, Z(70)], [729, Z(46)], [776, Z(74)], [880, Z(100)], [1100, Z(100)], [1150, Z(70)], [1150, Z(-12)]] },
      { name: 'Manitou Road', w: 5, kind: 'paved', pts: [[0, Z(280)], [-60, Z(265)], [-170, Z(255)], [-260, Z(248)], [-335, Z(240)], [-420, Z(250)], [-520, Z(210)], [-568, Z(197)], [-612, Z(160)], [-690, Z(85)], [-720, Z(-95)]] },
      { name: 'Hanlan\'s Point Road', w: 6, kind: 'paved', pts: [[-720, Z(-95)], [-800, Z(-60)], [-960, Z(-130)]] },
      { name: 'Olympic Island Trail', w: 5, kind: 'gravel', pts: [[0, Z(280)], [-22, Z(290)], [-68, Z(310)], [-160, Z(320)], [-268, Z(322)], [-312, Z(322)], [-400, Z(330)], [-480, Z(308)]] },
      { name: 'Lighthouse Trail', w: 4, kind: 'gravel', pts: [[-420, Z(250)], [-470, Z(300)]] },
      { name: 'Lakeshore Avenue', w: 6, kind: 'paved', pts: [[-620, Z(440)], [-300, Z(455)], [-60, Z(452)], [0, Z(450)], [300, Z(440)]] },
      { name: 'The Boardwalk', w: 5, kind: 'boardwalk', pts: [[300, Z(440)], [600, Z(412)], [800, Z(362)], [1000, Z(292)], [1150, Z(222)], [1245, Z(130)]] },
      { name: 'Ward\'s Lane', w: 3, kind: 'gravel', pts: [[900, Z(0)], [1140, Z(0)]] },
      { name: 'Algonquin Lane', w: 3, kind: 'gravel', pts: [[420, Z(62)], [600, Z(62)]] }
    ];
    const BOARDWALK = PATHS.find(p => p.kind === 'boardwalk');

    // Lawns, gardens, and clearings where trees are kept clear
    const CLEARINGS = [
      { r: [-25, 85, Z(-20), Z(112)] }, // North Island: Ferry Terminal, Pizza Pizza, Subway, Washrooms/Lockers & BBQ Restaurant patio
      { r: [-45, 45, Z(280), Z(435)] }, // Avenue of the Islands south: Grand Fountain, Formal Gardens & Reflecting Pools
      { c: [-160, Z(330), 65] }, // Olympic Island Great Lawn (skyline panorama)
      { r: [135, 245, Z(155), Z(245)] }, // Centreville Turn-of-the-Century Victorian Village
      { r: [265, 345, Z(140), Z(225)] }, // Far Enough Farm (Big Red Barn, Silo, Paddocks)
      { r: [-105, -25, Z(350), Z(425)] }, // William Meany Hedge Maze (South part, WEST of Avenue)
      { r: [-55, 55, Z(435), Z(475)] }, // South Beach Pavilion, Restaurant & Bike Rental
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
      { name: 'North Arrival Bridge', x0: 28, z0: Z(118), x1: 28, z1: Z(158), w: 8.0, archH: 2.2, yBase: 0.55 },
      { name: 'Manitou Bridge', x0: 0, z0: Z(230), x1: 0, z1: Z(280), w: 9.0, archH: 2.4, yBase: 0.55 },
      { name: 'Olympic-Gibraltar Bridge', x0: -370, z0: Z(318), x1: -310, z1: Z(318), w: 7.0, archH: 2.3, yBase: 0.55 },
      { name: 'Algonquin Bridge', x0: 330, z0: Z(65), x1: 395, z1: Z(95), w: 7.2, archH: 2.5, yBase: 0.55 },
      { name: 'Ward-Algonquin Footbridge', x0: 720, z0: Z(45), x1: 780, z1: Z(75), w: 6.5, archH: 2.4, yBase: 0.55 },
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
    // Landmark: North Island Arrival Concessions & Amenities
    // Walking south from Centre Island Ferry Dock along the path curving east then south:
    // 1. Pizza Pizza food kiosk & outdoor umbrella patio at (12, Z(48))
    // 2. Subway fresh sub sandwich kiosk at (12, Z(66))
    // 3. Park Washroom & Public Lockers Building with drinking fountain at (12, Z(88))
    // 4. Toronto Island BBQ & Beer Co.: large waterfront restaurant & smoker deck to the east at (65, Z(65))
    //    situated north of the First Bridge (North Arrival Bridge at z=Z(118..158))!
    // ------------------------------------------------------------------------
    {
      const conGrp = new THREE.Group();

      // --- 1. PIZZA PIZZA KIOSK at (12, Z(48)) ---
      const ppBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(8.5, 3.8, 6.0),
        new THREE.MeshStandardMaterial({ color: 0x9a3412, roughness: 0.6 })
      );
      ppBuilding.position.set(12, 1.9, Z(48));
      conGrp.add(ppBuilding);
      rectOb(7.5, 16.5, Z(45), Z(51)); // solid interior

      // Service counter & canopy awning
      const ppAwning = new THREE.Mesh(
        new THREE.BoxGeometry(9.0, 0.4, 2.2),
        new THREE.MeshStandardMaterial({ color: 0xea580c, roughness: 0.4 })
      );
      ppAwning.position.set(12, 3.4, Z(44.8));
      conGrp.add(ppAwning);

      const ppSign = makeSign(
        ['PIZZA PIZZA', 'FRESH SLICES & DRINKS • CENTRE ISLAND CONCESSIONS'],
        8.2, 1.8,
        { bg: '#ea580c', fg: '#ffffff', borderColor: '#facc15' }
      );
      ppSign.position.set(12, 4.4, Z(44.8));
      conGrp.add(ppSign);

      // Outdoor dining patio tables with orange umbrellas
      [Z(44), Z(52)].forEach((oz, ti) => {
        const tbl = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 0.8, 12), woodMat);
        tbl.position.set(20, GROUND_Y + 0.4, oz);
        conGrp.add(tbl);
        circOb(20, oz, 1.1);
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 6), metalMat);
        pole.position.set(20, GROUND_Y + 1.2, oz);
        conGrp.add(pole);
        const umb = new THREE.Mesh(new THREE.ConeGeometry(1.5, 0.6, 10), new THREE.MeshStandardMaterial({ color: 0xf97316, roughness: 0.5 }));
        umb.position.set(20, GROUND_Y + 2.3, oz);
        conGrp.add(umb);
      });

      // --- 2. SUBWAY KIOSK at (12, Z(66)) ---
      const subBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(8.5, 3.8, 6.0),
        new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 0.6 })
      );
      subBuilding.position.set(12, 1.9, Z(66));
      conGrp.add(subBuilding);
      rectOb(7.5, 16.5, Z(63), Z(69)); // solid interior

      const subAwning = new THREE.Mesh(
        new THREE.BoxGeometry(9.0, 0.4, 2.2),
        new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.4 })
      );
      subAwning.position.set(12, 3.4, Z(62.8));
      conGrp.add(subAwning);

      const subSign = makeSign(
        ['SUBWAY', 'FRESH SUBS & SALADS • EAT FRESH'],
        8.2, 1.8,
        { bg: '#15803d', fg: '#facc15', borderColor: '#ffffff' }
      );
      subSign.position.set(12, 4.4, Z(62.8));
      conGrp.add(subSign);

      // Outdoor dining patio tables with yellow & green umbrellas
      [Z(62), Z(70)].forEach((oz, ti) => {
        const tbl = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 0.8, 12), woodMat);
        tbl.position.set(20, GROUND_Y + 0.4, oz);
        conGrp.add(tbl);
        circOb(20, oz, 1.1);
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 6), metalMat);
        pole.position.set(20, GROUND_Y + 1.2, oz);
        conGrp.add(pole);
        const umb = new THREE.Mesh(new THREE.ConeGeometry(1.5, 0.6, 10), new THREE.MeshStandardMaterial({ color: ti === 0 ? 0xfacc15 : 0x16a34a, roughness: 0.5 }));
        umb.position.set(20, GROUND_Y + 2.3, oz);
        conGrp.add(umb);
      });

      // --- 3. PARK WASHROOM & PUBLIC LOCKERS BUILDING at (12, Z(88)) ---
      const washBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(11.0, 4.2, 8.0),
        new THREE.MeshStandardMaterial({ color: 0x854d0e, roughness: 0.7 })
      );
      washBuilding.position.set(12, 2.1, Z(88));
      conGrp.add(washBuilding);
      rectOb(6.2, 17.8, Z(83.8), Z(92.2)); // solid interior

      // Cedar board-and-batten hip roof
      const washRoof = new THREE.Mesh(
        new THREE.ConeGeometry(8.5, 2.4, 4),
        new THREE.MeshStandardMaterial({ color: 0x1e3a29, roughness: 0.7 })
      );
      washRoof.rotation.y = Math.PI / 4;
      washRoof.position.set(12, 5.2, Z(88));
      conGrp.add(washRoof);

      // Blue public locker banks mounted along exterior east wall facing the path
      const lockerBank = new THREE.Mesh(
        new THREE.BoxGeometry(0.4, 2.2, 5.0),
        new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.4, metalness: 0.5 })
      );
      lockerBank.position.set(17.8, 1.5, Z(88));
      conGrp.add(lockerBank);

      // Locker canopy
      const lockerCanopy = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.2, 5.6), darkWoodMat);
      lockerCanopy.position.set(18.2, 2.7, Z(88));
      conGrp.add(lockerCanopy);

      const lockerSign = makeSign(
        ['PUBLIC LOCKERS', 'SECURE DAY STORAGE • COIN / DIGITAL'],
        4.8, 0.9,
        { bg: '#0369a1', fg: '#ffffff', borderColor: '#38bdf8', titleSize: 34, subSize: 20 }
      );
      lockerSign.position.set(18.1, 3.1, Z(88));
      lockerSign.rotation.y = Math.PI / 2;
      conGrp.add(lockerSign);

      const washSign = makeSign(
        ['PUBLIC RESTROOMS', 'TORONTO ISLAND PARK • MEN & WOMEN'],
        7.5, 1.4,
        { bg: '#1e3a8a', fg: '#f8fafc', borderColor: '#60a5fa' }
      );
      washSign.position.set(12, 3.6, Z(83.8));
      conGrp.add(washSign);

      // Stainless steel drinking water fountain
      const fountainPed = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.25, 1.0, 8), metalMat);
      fountainPed.position.set(19.5, 0.5, Z(84));
      conGrp.add(fountainPed);
      const fountainBasin = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.2, 0.2, 8), metalMat);
      fountainBasin.position.set(19.5, 1.0, Z(84));
      conGrp.add(fountainBasin);

      // --- 4. TORONTO ISLAND BBQ & BEER CO. RESTAURANT at (65, Z(65)) ---
      // Situated to the east, north of the first bridge, overlooking the water & skyline
      const bbqBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(16.0, 6.2, 12.0),
        new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.8 })
      );
      bbqBuilding.position.set(65, 3.1, Z(65));
      conGrp.add(bbqBuilding);
      rectOb(56.5, 73.5, Z(58.5), Z(71.5)); // building interior blocks collision

      const bbqRoof = new THREE.Mesh(
        new THREE.ConeGeometry(12.0, 3.5, 4),
        new THREE.MeshStandardMaterial({ color: 0x1c1917, roughness: 0.6 })
      );
      bbqRoof.rotation.y = Math.PI / 4;
      bbqRoof.position.set(65, 7.6, Z(65));
      conGrp.add(bbqRoof);

      // Grand Restaurant Sign facing arrival path
      const bbqSign = makeSign(
        ['TORONTO ISLAND BBQ & BEER CO.', 'SLOW-SMOKED BBQ • LOCAL CRAFT BEER • SKYLINE PATIO'],
        13.5, 2.4,
        { bg: '#451a03', fg: '#fef08a', borderColor: '#d97706' }
      );
      bbqSign.position.set(56.8, 5.2, Z(65));
      bbqSign.rotation.y = -Math.PI / 2;
      conGrp.add(bbqSign);

      // Sprawling raised outdoor dining deck patio overlooking water
      const patioDeck = new THREE.Mesh(
        new THREE.BoxGeometry(22.0, 0.35, 24.0),
        new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 })
      );
      patioDeck.position.set(65, GROUND_Y + 0.18, Z(80));
      conGrp.add(patioDeck);

      // Perimeter wooden railing around patio
      const patioRail = new THREE.Mesh(
        new THREE.BoxGeometry(22.2, 1.0, 0.15),
        darkWoodMat
      );
      patioRail.position.set(65, GROUND_Y + 0.7, Z(92));
      conGrp.add(patioRail);

      // Outdoor bar counter on patio
      const barCounter = new THREE.Mesh(new THREE.BoxGeometry(6.0, 1.1, 1.4), darkWoodMat);
      barCounter.position.set(65, GROUND_Y + 0.7, Z(75));
      conGrp.add(barCounter);
      rectOb(61.8, 68.2, Z(74.1), Z(75.9));

      // Smoker BBQ pit with chimney
      const smoker = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.8, 1.6), new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.4, metalness: 0.8 }));
      smoker.position.set(54, GROUND_Y + 0.9, Z(74));
      conGrp.add(smoker);
      const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 3.2, 8), metalMat);
      stack.position.set(54, GROUND_Y + 2.8, Z(74));
      conGrp.add(stack);
      circOb(54, Z(74), 1.2);

      // 6 Outdoor picnic tables with patio umbrellas on the BBQ deck
      [-6, 6].forEach(ox => {
        [Z(81), Z(86), Z(90)].forEach(oz => {
          const tbl = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.8, 12), woodMat);
          tbl.position.set(65 + ox, GROUND_Y + 0.6, oz);
          conGrp.add(tbl);
          circOb(65 + ox, oz, 1.2);

          const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.4, 6), metalMat);
          pole.position.set(65 + ox, GROUND_Y + 1.4, oz);
          conGrp.add(pole);

          const umb = new THREE.Mesh(new THREE.ConeGeometry(1.6, 0.65, 10), new THREE.MeshStandardMaterial({ color: ox < 0 ? 0xdc2626 : 0x16a34a, roughness: 0.5 }));
          umb.position.set(65 + ox, GROUND_Y + 2.5, oz);
          conGrp.add(umb);
        });
      });

      // Overhead pergola with festive string lights
      [-9, 9].forEach(px => {
        [Z(73), Z(91)].forEach(pz => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.3, 3.2, 0.3), darkWoodMat);
          post.position.set(65 + px, GROUND_Y + 1.6, pz);
          conGrp.add(post);
        });
      });

      islandsGroup.add(conGrp);
    }

    // ------------------------------------------------------------------------
    // Landmark: Avenue of the Islands - Grand Fountain, Formal Gardens & Flanking Reflecting Pools
    // Walking south from Centre Dock, cross Manitou Bridge (z ~ Z(255)) to reach the Grand Fountain at Z(310),
    // followed by the Grand Formal Gardens and twin sunken Reflecting Pools (Z(345) - Z(415)) east & west of the path!
    // ------------------------------------------------------------------------
    let fountainSpray = null;
    const poolJets = [];
    {
      const avg = new THREE.Group();
      const flowerCols = [0xef4444, 0xfacc15, 0xa855f7, 0xf472b6, 0xffffff, 0xfb923c, 0x3b82f6];
      const blooms = [];

      // 1. North Avenue of the Islands (from Dock z=Z(24) to Manitou Bridge z=Z(216))
      // Flanked by park flowerbeds, benches, and Victorian cast-iron lampposts
      for (let fz = Z(24); fz <= Z(216); fz += 24) {
        [-8.5, 8.5].forEach((fx, fi) => {
          const bed = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.45, 12), stoneMat);
          bed.position.set(fx, GROUND_Y + 0.1, fz);
          avg.add(bed);
          rectOb(fx - 1.6, fx + 1.6, fz - 6, fz + 6);
          const col = flowerCols[(fi + Math.round(fz / 24)) % flowerCols.length];
          for (let fl = -5; fl <= 5; fl += 0.9) {
            for (let w = -1.0; w <= 1.0; w += 0.7) blooms.push([fx + w, fz + fl, col]);
          }
        });
      }

      // 2. Grand Fountain Plaza (Immediately south of Manitou Bridge, at x = 0, z = Z(310) = 5310)
      const fz = Z(310);

      // Circular flagstone plaza paving
      const plazaPaving = new THREE.Mesh(new THREE.CircleGeometry(14.5, 32), stoneMat);
      plazaPaving.rotation.x = -Math.PI / 2;
      plazaPaving.position.set(0, GROUND_Y + 0.02, fz);
      avg.add(plazaPaving);

      // Outer fountain pool coping wall (radius 10.2m, height 1.15m)
      const pool = new THREE.Mesh(new THREE.CylinderGeometry(10.2, 10.8, 1.2, 32), stoneMat);
      pool.position.set(0, GROUND_Y + 0.45, fz);
      avg.add(pool);

      const waterSurf = new THREE.Mesh(new THREE.CircleGeometry(9.6, 32), new THREE.MeshStandardMaterial({
        color: 0x38bdf8, roughness: 0.1, metalness: 0.35, transparent: true, opacity: 0.9
      }));
      waterSurf.rotation.x = -Math.PI / 2;
      waterSurf.position.set(0, GROUND_Y + 0.95, fz);
      avg.add(waterSurf);

      // Multi-tiered classical carved stone tiers
      const tier1 = new THREE.Mesh(new THREE.CylinderGeometry(4.6, 5.2, 1.4, 20), stoneMat);
      tier1.position.set(0, GROUND_Y + 1.45, fz);
      avg.add(tier1);
      const tier1Water = new THREE.Mesh(new THREE.CircleGeometry(4.3, 20), new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1 }));
      tier1Water.rotation.x = -Math.PI / 2;
      tier1Water.position.set(0, GROUND_Y + 2.16, fz);
      avg.add(tier1Water);

      const tier2 = new THREE.Mesh(new THREE.CylinderGeometry(2.1, 2.5, 1.5, 16), stoneMat);
      tier2.position.set(0, GROUND_Y + 2.85, fz);
      avg.add(tier2);

      // Central soaring geyser spray (animated scale in update)
      fountainSpray = new THREE.Mesh(
        new THREE.ConeGeometry(0.9, 7.5, 14, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.82, fog: false })
      );
      fountainSpray.position.set(0, GROUND_Y + 6.8, fz);
      avg.add(fountainSpray);

      // 8 perimeter arched water streams spouting inward
      for (let j = 0; j < 8; j++) {
        const ang = (j / 8) * Math.PI * 2;
        const stream = new THREE.Mesh(
          new THREE.CylinderGeometry(0.08, 0.16, 4.2, 6),
          new THREE.MeshBasicMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.75, fog: false })
        );
        const sx = Math.cos(ang) * 6.5, sz = Math.sin(ang) * 6.5;
        stream.position.set(sx, GROUND_Y + 2.2, fz + sz);
        stream.rotation.x = -Math.sin(ang) * 0.45;
        stream.rotation.z = Math.cos(ang) * 0.45;
        avg.add(stream);
      }

      // Plaza ornamental stone urns and curved resting benches around the fountain
      for (let k = 0; k < 4; k++) {
        const ba = (k / 4) * Math.PI * 2 + Math.PI / 4;
        const bx = Math.cos(ba) * 12.8, bz = Math.sin(ba) * 12.8;
        const bch = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.45, 0.8), darkWoodMat);
        bch.position.set(bx, GROUND_Y + 0.45, fz + bz);
        bch.rotation.y = -ba + Math.PI / 2;
        avg.add(bch);

        const urn = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.35, 0.9, 10), stoneMat);
        const ux = Math.cos(ba + 0.35) * 13.2, uz = Math.sin(ba + 0.35) * 13.2;
        urn.position.set(ux, GROUND_Y + 0.45, fz + uz);
        avg.add(urn);
        for (let u = 0; u < 5; u++) blooms.push([ux + (rnd() - 0.5) * 0.5, fz + uz + (rnd() - 0.5) * 0.5, 0xef4444]);
      }
      circOb(0, fz, 10.6);

      // 3. Grand Formal Gardens & Sunken Reflecting Pools (Water areas in the ground, z = Z(345) to Z(415))
      // Symmetrically placed to the WEST (x = -26) and EAST (x = +26) of Avenue of the Island!
      [-26, 26].forEach((poolX, pIdx) => {
        const pZ0 = Z(345), pZ1 = Z(415), pLen = pZ1 - pZ0, pW = 14;
        const pMidZ = (pZ0 + pZ1) / 2;

        // Cut limestone coping rim enclosing the pool
        const copingT = 0.8;
        // North & South rim caps
        [-pLen / 2, pLen / 2].forEach(oz => {
          const cap = new THREE.Mesh(new THREE.BoxGeometry(pW + copingT * 2, 0.35, copingT), stoneMat);
          cap.position.set(poolX, GROUND_Y + 0.16, pMidZ + oz);
          avg.add(cap);
        });
        // East & West rim sides
        [-pW / 2, pW / 2].forEach(ox => {
          const side = new THREE.Mesh(new THREE.BoxGeometry(copingT, 0.35, pLen), stoneMat);
          side.position.set(poolX + ox, GROUND_Y + 0.16, pMidZ);
          avg.add(side);
        });

        // Sunken reflecting pool water surface
        const poolWater = new THREE.Mesh(
          new THREE.PlaneGeometry(pW - 0.2, pLen - 0.2),
          new THREE.MeshStandardMaterial({
            color: 0x0284c7,
            roughness: 0.12,
            metalness: 0.5,
            transparent: true,
            opacity: 0.88
          })
        );
        poolWater.rotation.x = -Math.PI / 2;
        poolWater.position.set(poolX, GROUND_Y + 0.06, pMidZ);
        avg.add(poolWater);

        // Submerged pool floor (dark aquamarine stone tiling)
        const poolFloor = new THREE.Mesh(
          new THREE.PlaneGeometry(pW, pLen),
          new THREE.MeshStandardMaterial({ color: 0x0c4a6e, roughness: 0.8 })
        );
        poolFloor.rotation.x = -Math.PI / 2;
        poolFloor.position.set(poolX, GROUND_Y - 0.8, pMidZ);
        avg.add(poolFloor);

        // 3 stone bubbler fountain pedestals spaced along each pool's centerline
        [-24, 0, 24].forEach((oz, jetIdx) => {
          const ped = new THREE.Mesh(new THREE.CylinderGeometry(0.65, 0.8, 0.6, 12), stoneMat);
          ped.position.set(poolX, GROUND_Y - 0.1, pMidZ + oz);
          avg.add(ped);

          const spray = new THREE.Mesh(
            new THREE.ConeGeometry(0.35, 2.4, 8, 1, true),
            new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.75, fog: false })
          );
          spray.position.set(poolX, GROUND_Y + 1.2, pMidZ + oz);
          avg.add(spray);
          poolJets.push(spray);
        });

        // Floating lily pads & water lilies in the reflecting pools
        const padMat = new THREE.MeshLambertMaterial({ color: 0x15803d });
        const padGeo = new THREE.CircleGeometry(0.55, 10);
        for (let l = 0; l < 18; l++) {
          const lox = (rnd() - 0.5) * (pW - 2.8);
          const loz = (rnd() - 0.5) * (pLen - 6.0);
          const pad = new THREE.Mesh(padGeo, padMat);
          pad.rotation.x = -Math.PI / 2;
          pad.position.set(poolX + lox, GROUND_Y + 0.08, pMidZ + loz);
          avg.add(pad);

          if (l % 2 === 0) {
            const bloom = new THREE.Mesh(new THREE.DodecahedronGeometry(0.18, 0), new THREE.MeshBasicMaterial({ color: (l % 4 === 0) ? 0xf472b6 : 0xffffff, fog: false }));
            bloom.position.set(poolX + lox, GROUND_Y + 0.22, pMidZ + loz);
            avg.add(bloom);
          }
        }

        // Flanking Formal Parterre Gardens & Flowerbeds on outer side of each reflecting pool
        const gardenOuterX = poolX + (pIdx === 0 ? -12.5 : 12.5);
        for (let gz = pZ0 + 5; gz <= pZ1 - 5; gz += 16) {
          const gBed = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.35, 12), stoneMat);
          gBed.position.set(gardenOuterX, GROUND_Y + 0.1, gz);
          avg.add(gBed);
          rectOb(gardenOuterX - 2.25, gardenOuterX + 2.25, gz - 6, gz + 6);

          const col = flowerCols[Math.floor(rnd() * flowerCols.length)];
          for (let fl = -5; fl <= 5; fl += 0.8) {
            for (let w = -1.6; w <= 1.6; w += 0.8) blooms.push([gardenOuterX + w, gz + fl, col]);
          }

          // Ornamental boxwood hedge borders
          const hBorder = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.65, 13), hedgeMat);
          hBorder.position.set(gardenOuterX + (pIdx === 0 ? -2.6 : 2.6), GROUND_Y + 0.32, gz);
          avg.add(hBorder);
        }

        // Benches along the garden promenades
        for (let bz = pZ0 + 12; bz <= pZ1 - 12; bz += 22) {
          // Inner bench facing pool
          const b1 = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.45, 0.7), darkWoodMat);
          b1.position.set(poolX + (pIdx === 0 ? 8.5 : -8.5), GROUND_Y + 0.45, bz);
          avg.add(b1);
          // Outer bench facing garden
          const b2 = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.45, 0.7), darkWoodMat);
          b2.position.set(poolX + (pIdx === 0 ? -8.5 : 8.5), GROUND_Y + 0.45, bz);
          avg.add(b2);
        }

        // Deep water obstacle inside pool prevents walking into water
        rectOb(poolX - pW / 2 - 0.4, poolX + pW / 2 + 0.4, pZ0 - 0.4, pZ1 + 0.4);
      });

      // 4. Instanced flower blooms for all Avenue & Parterre garden beds
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
    // Landmark: William Meany Hedge Maze (South part, WEST of Avenue of the Island)
    // Situated at x = -65, z = Z(385) with Dirt-colored ground and the 1888 antique school bell!
    // ------------------------------------------------------------------------
    {
      const hmg = new THREE.Group();
      const hx = -65, hz = Z(385);

      // Earth-toned packed dirt ground so green cedar hedges stand out sharply
      const mazeGround = new THREE.Mesh(new THREE.BoxGeometry(76, 0.08, 76), dirtMat);
      mazeGround.position.set(hx, 0.57, hz);
      mazeGround.receiveShadow = true;
      hmg.add(mazeGround);

      // Entrance Gate Arch & Commemorative Plaque Sign facing east towards Avenue path
      const mSign = makeSign(
        ['WILLIAM MEANY HEDGE MAZE', 'HISTORIC 1888 SCHOOL BELL • DONATED 2015'],
        18, 2.4,
        { bg: '#14532d', fg: '#bbf7d0', borderColor: '#22c55e' }
      );
      mSign.position.set(hx + 37, 3.8, hz);
      mSign.rotation.y = -Math.PI / 2;
      hmg.add(mSign);

      function addMazeWall(wx, wz, ww, wd) {
        const wall = new THREE.Mesh(new THREE.BoxGeometry(ww, 2.2, wd), hedgeMat);
        wall.position.set(hx + wx, 1.6, hz + wz);
        hmg.add(wall);
        rectOb(hx + wx - ww / 2, hx + wx + ww / 2, hz + wz - wd / 2, hz + wz + wd / 2);
      }

      // Outer perimeter hedge walls with entrance opening facing EAST towards Avenue
      addMazeWall(36, -20, 1.4, 32);
      addMazeWall(36, 20, 1.4, 32);
      addMazeWall(-36, 0, 1.4, 72);
      addMazeWall(0, -36, 72, 1.4);
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
    // Landmark: Centreville Turn-of-the-Century Victorian Village
    // Discovered down the wooded path east of the First Bridge (at x=140..245, z=Z(155..245)):
    // - Victorian Town Hall with 18m Clock & Bell Tower, portico stairs, and bell
    // - Centreville General Store with wooden porch veranda, rocking chairs, apple barrels
    // - Old-Fashioned Sweet Shoppe & Ice Cream Parlour with striped candy awnings
    // - Carousel Cafe & Bakery with buttercup clapboard, flower boxes & cafe seating
    // - Antique 1907 Dentzel Carousel in 16-sided Victorian rotunda with rotating painted horses
    // - Giant 26m Ferris Wheel in YZ plane with 12 rotating passenger carts
    // ------------------------------------------------------------------------
    let ferrisWheelMesh = null, carouselTop = null;
    {
      const cvg = new THREE.Group();

      // 1. VICTORIAN TOWN HALL (EST. 1900) at (180, Z(185))
      const thHall = new THREE.Mesh(
        new THREE.BoxGeometry(16.0, 7.5, 12.0),
        new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.6 }) // cream clapboard
      );
      thHall.position.set(180, 3.75, Z(185));
      cvg.add(thHall);
      rectOb(171.5, 188.5, Z(178.5), Z(191.5)); // interior blocks

      // Burgundy mansard trim roof
      const thRoof = new THREE.Mesh(
        new THREE.ConeGeometry(12.0, 3.2, 4),
        new THREE.MeshStandardMaterial({ color: 0x831843, roughness: 0.5 })
      );
      thRoof.rotation.y = Math.PI / 4;
      thRoof.position.set(180, 8.8, Z(185));
      cvg.add(thRoof);

      // Central Four-Sided Victorian Clock Tower & Belfry (18m tall)
      const towerBase = new THREE.Mesh(
        new THREE.BoxGeometry(4.2, 7.0, 4.2),
        new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.6 })
      );
      towerBase.position.set(180, 11.0, Z(185));
      cvg.add(towerBase);

      // 4 Illuminated Clock Faces
      const clkGeo = new THREE.CircleGeometry(1.2, 16);
      const clkMat = new THREE.MeshBasicMaterial({ color: 0xfef9c3, side: THREE.DoubleSide, fog: false });
      [[0, -2.12, 0], [0, 2.12, Math.PI], [-2.12, 0, Math.PI / 2], [2.12, 0, -Math.PI / 2]].forEach(([ox, oz, ry]) => {
        const cFace = new THREE.Mesh(clkGeo, clkMat);
        cFace.position.set(180 + ox, 11.5, Z(185) + oz);
        cFace.rotation.y = ry;
        cvg.add(cFace);
      });

      // Copper Spire on top of clock tower
      const spire = new THREE.Mesh(
        new THREE.ConeGeometry(2.4, 5.5, 4),
        new THREE.MeshStandardMaterial({ color: 0x0d9488, roughness: 0.4, metalness: 0.5 })
      );
      spire.rotation.y = Math.PI / 4;
      spire.position.set(180, 17.2, Z(185));
      cvg.add(spire);

      // Front porch stairs & banner
      const thSign = makeSign(
        ['CENTREVILLE TOWN HALL', 'ESTABLISHED 1900 • HISTORIC VILLAGE SQUARE'],
        9.5, 1.8,
        { bg: '#831843', fg: '#fef08a', borderColor: '#f472b6' }
      );
      thSign.position.set(180, 5.2, Z(178.6));
      cvg.add(thSign);

      // 2. CENTREVILLE GENERAL STORE at (150, Z(215))
      const gsBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(12.0, 4.8, 9.0),
        new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.7 })
      );
      gsBuilding.position.set(150, 2.4, Z(215));
      cvg.add(gsBuilding);
      rectOb(143.5, 156.5, Z(210), Z(220));

      const gsRoof = new THREE.Mesh(new THREE.ConeGeometry(8.5, 2.5, 4), darkWoodMat);
      gsRoof.rotation.y = Math.PI / 4;
      gsRoof.position.set(150, 5.8, Z(215));
      cvg.add(gsRoof);

      // Wooden boardwalk veranda porch with rocking chairs & apple barrels
      const gsPorch = new THREE.Mesh(new THREE.BoxGeometry(12.4, 0.3, 3.2), woodMat);
      gsPorch.position.set(150, GROUND_Y + 0.15, Z(208.5));
      cvg.add(gsPorch);

      [-3.5, 3.5].forEach(ox => {
        const chair = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.9, 0.8), darkWoodMat);
        chair.position.set(150 + ox, GROUND_Y + 0.6, Z(208.5));
        cvg.add(chair);
      });

      const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.9, 10), woodMat);
      barrel.position.set(145, GROUND_Y + 0.6, Z(208.5));
      cvg.add(barrel);

      const gsSign = makeSign(
        ['CENTREVILLE GENERAL STORE', 'OLD-FASHIONED CANDY • SUNDRIES & SOUVENIRS'],
        9.0, 1.6,
        { bg: '#14532d', fg: '#fef08a', borderColor: '#86efac' }
      );
      gsSign.position.set(150, 4.2, Z(207.2));
      cvg.add(gsSign);

      // 3. OLD-FASHIONED SWEET SHOPPE & ICE CREAM PARLOUR at (210, Z(215))
      const ssBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(12.0, 4.8, 9.0),
        new THREE.MeshStandardMaterial({ color: 0xfdf2f8, roughness: 0.4 })
      );
      ssBuilding.position.set(210, 2.4, Z(215));
      cvg.add(ssBuilding);
      rectOb(203.5, 216.5, Z(210), Z(220));

      // Candy-striped pink and white scalloped awnings
      const ssAwning = new THREE.Mesh(
        new THREE.BoxGeometry(12.4, 0.4, 2.4),
        new THREE.MeshStandardMaterial({ color: 0xf472b6, roughness: 0.3 })
      );
      ssAwning.position.set(210, 3.6, Z(209));
      cvg.add(ssAwning);

      const ssSign = makeSign(
        ['OLD FASHIONED SWEET SHOPPE', 'HAND-SCOOPED ICE CREAM • WAFFLE CONES & FUDGE'],
        9.8, 1.6,
        { bg: '#9d174d', fg: '#fdf2f8', borderColor: '#f472b6' }
      );
      ssSign.position.set(210, 4.5, Z(209));
      cvg.add(ssSign);

      // 4. CAROUSEL CAFE & BAKERY at (150, Z(180))
      const ccBuilding = new THREE.Mesh(
        new THREE.BoxGeometry(11.0, 4.5, 8.0),
        new THREE.MeshStandardMaterial({ color: 0xfef08a, roughness: 0.6 })
      );
      ccBuilding.position.set(150, 2.25, Z(180));
      cvg.add(ccBuilding);
      rectOb(144, 156, Z(175.5), Z(184.5));

      const ccSign = makeSign(
        ['CAROUSEL CAFE & BAKERY', 'FRESH PASTRIES • GOURMET COFFEE • PATIO'],
        8.8, 1.5,
        { bg: '#854d0e', fg: '#fef9c3', borderColor: '#fde047' }
      );
      ccSign.position.set(150, 4.1, Z(175.8));
      cvg.add(ccSign);

      // 5. GIANT 26M FERRIS WHEEL at (225, Z(225)) facing West along village square
      const fwGrp = new THREE.Group();
      fwGrp.position.set(225, 14.5, Z(225));

      const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 6.2, 10), metalMat);
      axle.rotation.z = Math.PI / 2;
      fwGrp.add(axle);

      [-2.6, 2.6].forEach(lx => {
        const leg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.48, 15.5, 8), metalMat);
        leg1.position.set(lx, -7.0, -5.0);
        leg1.rotation.x = -0.35;
        fwGrp.add(leg1);
        const leg2 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.48, 15.5, 8), metalMat);
        leg2.position.set(lx, -7.0, 5.0);
        leg2.rotation.x = 0.35;
        fwGrp.add(leg2);
      });

      const wheelWheel = new THREE.Group();
      const rOuter = 11.5, rInner = 9.0;
      const rim1 = new THREE.Mesh(new THREE.TorusGeometry(rOuter, 0.22, 8, 36), metalMat);
      rim1.rotation.y = Math.PI / 2;
      rim1.position.x = -1.3;
      wheelWheel.add(rim1);
      const rim2 = new THREE.Mesh(new THREE.TorusGeometry(rOuter, 0.22, 8, 36), metalMat);
      rim2.rotation.y = Math.PI / 2;
      rim2.position.x = 1.3;
      wheelWheel.add(rim2);

      const irim1 = new THREE.Mesh(new THREE.TorusGeometry(rInner, 0.16, 8, 32), metalMat);
      irim1.rotation.y = Math.PI / 2;
      irim1.position.x = -1.3;
      wheelWheel.add(irim1);
      const irim2 = new THREE.Mesh(new THREE.TorusGeometry(rInner, 0.16, 8, 32), metalMat);
      irim2.rotation.y = Math.PI / 2;
      irim2.position.x = 1.3;
      wheelWheel.add(irim2);

      const nSpokes = 12;
      const cartCols = [0xef4444, 0x3b82f6, 0xfacc15, 0x10b981, 0xa855f7, 0xf97316];
      for (let i = 0; i < nSpokes; i++) {
        const ang = (i / nSpokes) * Math.PI * 2;
        const sp1 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, rOuter * 2, 6), metalMat);
        sp1.rotation.x = ang;
        sp1.position.x = -1.3;
        wheelWheel.add(sp1);
        const sp2 = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, rOuter * 2, 6), metalMat);
        sp2.rotation.x = ang;
        sp2.position.x = 1.3;
        wheelWheel.add(sp2);

        const cross = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.6, 6), metalMat);
        cross.rotation.z = Math.PI / 2;
        cross.position.set(0, Math.sin(ang) * rOuter, Math.cos(ang) * rOuter);
        wheelWheel.add(cross);

        const cart = new THREE.Mesh(
          new THREE.BoxGeometry(2.0, 1.4, 1.6),
          new THREE.MeshStandardMaterial({ color: cartCols[i % cartCols.length], roughness: 0.4 })
        );
        cart.position.set(0, Math.sin(ang) * rOuter, Math.cos(ang) * rOuter);
        wheelWheel.add(cart);
      }
      fwGrp.add(wheelWheel);
      ferrisWheelMesh = wheelWheel;
      cvg.add(fwGrp);
      circOb(225, Z(225), 5.5);

      // 6. ANTIQUE 1907 DENTZEL CAROUSEL at (180, Z(225))
      const carBase = new THREE.Mesh(new THREE.CylinderGeometry(8.5, 9.0, 0.8, 20), woodMat);
      carBase.position.set(180, GROUND_Y + 0.4, Z(225));
      cvg.add(carBase);

      const carCenter = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 5.0, 12), metalMat);
      carCenter.position.set(180, GROUND_Y + 2.8, Z(225));
      cvg.add(carCenter);

      carouselTop = new THREE.Group();
      carouselTop.position.set(180, GROUND_Y + 4.8, Z(225));
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
      circOb(180, Z(225), 9.2);

      islandsGroup.add(cvg);
    }

    // ------------------------------------------------------------------------
    // Landmark: The Centreville Miniature Train (Beasley Bear Express)
    // Runs on miniature narrow-gauge tracks looping around Centreville, through the woods,
    // and past Far Enough Farm!
    // ------------------------------------------------------------------------
    let miniTrain = null, miniTrainPuff = null;
    const TRAIN_TRACK = [
      [160, Z(165)],
      [205, Z(165)],
      [245, Z(150)],
      [290, Z(145)],
      [320, Z(170)],
      [305, Z(205)],
      [250, Z(235)],
      [190, Z(240)],
      [140, Z(220)],
      [140, Z(185)]
    ];

    function evalTrainTrack(tNorm) {
      const n = TRAIN_TRACK.length;
      const f = ((tNorm % 1) + 1) % 1 * n;
      const idx = Math.floor(f);
      const frac = f - idx;
      const p0 = TRAIN_TRACK[(idx - 1 + n) % n];
      const p1 = TRAIN_TRACK[idx % n];
      const p2 = TRAIN_TRACK[(idx + 1) % n];
      const p3 = TRAIN_TRACK[(idx + 2) % n];
      const t = frac, t2 = t * t, t3 = t2 * t;
      const cat = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3);
      const x = cat(p0[0], p1[0], p2[0], p3[0]);
      const z = cat(p0[1], p1[1], p2[1], p3[1]);
      const dtFrac = 0.01;
      const tN = t + dtFrac, tN2 = tN * tN, tN3 = tN2 * tN;
      const catN = (a, b, c, d) => 0.5 * ((2 * b) + (-a + c) * tN + (2 * a - 5 * b + 4 * c - d) * tN2 + (-a + 3 * b - 3 * c + d) * tN3);
      const nx = catN(p0[0], p1[0], p2[0], p3[0]);
      const nz = catN(p0[1], p1[1], p2[1], p3[1]);
      return { x, z, yaw: Math.atan2(nx - x, nz - z) };
    }

    {
      const trGrp = new THREE.Group();

      // 1. CENTREVILLE RAILWAY STATION PLATFORM at (160, Z(165))
      const plat = new THREE.Mesh(new THREE.BoxGeometry(14.0, 0.4, 4.5), woodMat);
      plat.position.set(160, GROUND_Y + 0.2, Z(161));
      trGrp.add(plat);
      rectOb(152.5, 167.5, Z(158.5), Z(163.5));

      const depotRoof = new THREE.Mesh(new THREE.BoxGeometry(14.4, 0.3, 4.8), darkWoodMat);
      depotRoof.position.set(160, 3.6, Z(161));
      trGrp.add(depotRoof);

      [-6, 0, 6].forEach(px => {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.25, 3.2, 0.25), darkWoodMat);
        post.position.set(160 + px, 1.8, Z(161));
        trGrp.add(post);
      });

      const stSign = makeSign(
        ['CENTREVILLE RAILWAY STATION', 'BEASLEY BEAR EXPRESS • MINIATURE TRAIN TOUR'],
        11.5, 1.8,
        { bg: '#1e3a8a', fg: '#fef08a', borderColor: '#3b82f6' }
      );
      stSign.position.set(160, 4.2, Z(163.4));
      trGrp.add(stSign);

      // Station brass boarding bell
      const bell = new THREE.Mesh(new THREE.ConeGeometry(0.25, 0.35, 8), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.8, roughness: 0.2 }));
      bell.position.set(155, 2.8, Z(163));
      trGrp.add(bell);

      // 2. RAILWAY TRACKS (Ballast bed, wooden crossties, and dual steel rails)
      const numTies = 140;
      const tieGeo = new THREE.BoxGeometry(1.6, 0.12, 0.25);
      const tieMesh = new THREE.InstancedMesh(tieGeo, darkWoodMat, numTies);
      const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v = new THREE.Vector3(), one = new THREE.Vector3(1, 1, 1), up = new THREE.Vector3(0, 1, 0);

      for (let i = 0; i < numTies; i++) {
        const tr = evalTrainTrack(i / numTies);
        q.setFromAxisAngle(up, tr.yaw);
        m4.compose(v.set(tr.x, GROUND_Y + 0.06, tr.z), q, one);
        tieMesh.setMatrixAt(i, m4);
      }
      trGrp.add(tieMesh);

      // Dual shiny steel rails
      [-0.55, 0.55].forEach(side => {
        const railCurve = [];
        for (let i = 0; i <= numTies; i++) {
          const tr = evalTrainTrack(i / numTies);
          const ox = Math.cos(tr.yaw) * side, oz = -Math.sin(tr.yaw) * side;
          railCurve.push(new THREE.Vector3(tr.x + ox, GROUND_Y + 0.14, tr.z + oz));
        }
        const rPath = new THREE.CatmullRomCurve3(railCurve, true);
        const railGeo = new THREE.TubeGeometry(rPath, 90, 0.04, 6, true);
        const railMesh = new THREE.Mesh(railGeo, metalMat);
        trGrp.add(railMesh);
      });

      // 3. ANIMATED MINIATURE STEAM TRAIN
      miniTrain = new THREE.Group();

      // Steam Locomotive
      const loco = new THREE.Group();
      // Boiler
      const boiler = new THREE.Mesh(
        new THREE.CylinderGeometry(0.55, 0.55, 2.2, 12),
        new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.3, metalness: 0.7 })
      );
      boiler.rotation.x = Math.PI / 2;
      boiler.position.set(0, 0.75, 0.3);
      loco.add(boiler);

      // Driver Cab
      const cab = new THREE.Mesh(
        new THREE.BoxGeometry(1.3, 1.4, 1.1),
        new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.4 })
      );
      cab.position.set(0, 1.1, -0.9);
      loco.add(cab);

      // Red Cowcatcher (pilot) at front
      const cow = new THREE.Mesh(
        new THREE.ConeGeometry(0.65, 0.7, 4),
        new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.5 })
      );
      cow.rotation.x = -Math.PI / 2;
      cow.rotation.y = Math.PI / 4;
      cow.position.set(0, 0.35, 1.6);
      loco.add(cow);

      // Smokestack with steam puff
      const stack = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.1, 0.6, 8), metalMat);
      stack.position.set(0, 1.45, 1.1);
      loco.add(stack);

      miniTrainPuff = new THREE.Mesh(
        new THREE.SphereGeometry(0.28, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xf8fafc, transparent: true, opacity: 0.75, fog: false })
      );
      miniTrainPuff.position.set(0, 1.85, 1.0);
      loco.add(miniTrainPuff);

      // Brass Headlamp
      const lamp = new THREE.Mesh(
        new THREE.CylinderGeometry(0.16, 0.16, 0.25, 8),
        new THREE.MeshBasicMaterial({ color: 0xfef08a, fog: false })
      );
      lamp.rotation.x = Math.PI / 2;
      lamp.position.set(0, 1.1, 1.4);
      loco.add(lamp);

      // Coal Tender
      const tender = new THREE.Mesh(
        new THREE.BoxGeometry(1.2, 0.8, 1.3),
        new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.8 })
      );
      tender.position.set(0, 0.65, -2.2);
      loco.add(tender);

      // 3 Open-air Passenger Coaches
      [-4.0, -6.0, -8.0].forEach((cz, ci) => {
        const coach = new THREE.Group();
        coach.position.set(0, 0, cz);

        // Green carriage body
        const body = new THREE.Mesh(
          new THREE.BoxGeometry(1.3, 0.65, 1.7),
          new THREE.MeshStandardMaterial({ color: ci % 2 === 0 ? 0x15803d : 0xca8a04, roughness: 0.5 })
        );
        body.position.y = 0.55;
        coach.add(body);

        // Canopy roof
        const cRoof = new THREE.Mesh(new THREE.BoxGeometry(1.35, 0.1, 1.8), darkWoodMat);
        cRoof.position.y = 1.35;
        coach.add(cRoof);

        // Canopy support posts
        [-0.6, 0.6].forEach(px => {
          [-0.75, 0.75].forEach(pz => {
            const p = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.8, 6), metalMat);
            p.position.set(px, 0.95, pz);
            coach.add(p);
          });
        });

        loco.add(coach);
      });

      miniTrain.add(loco);
      trGrp.add(miniTrain);

      islandsGroup.add(trGrp);
    }

    // ------------------------------------------------------------------------
    // Landmark: Far Enough Farm (Est. 1959)
    // Located beyond Centreville to the east (x=265..345, z=Z(140..225)):
    // - Cedar Entrance Archway
    // - Big Classic Red Barn with gambrel roof, hayloft & golden rooster weather vane
    // - Farm Silo (white corrugated concrete with galvanized silver dome)
    // - Vintage Red Farmall Tractor
    // - Cedar post-and-rail fences & paddocks with sheep, cows, horses, goats & pigs!
    // ------------------------------------------------------------------------
    {
      const farmGrp = new THREE.Group();

      // 1. CEDAR ENTRANCE ARCHWAY at (255, Z(185))
      [-3.2, 3.2].forEach(ox => {
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 4.8, 8), darkWoodMat);
        post.position.set(255, 2.4, Z(185) + ox);
        farmGrp.add(post);
        circOb(255, Z(185) + ox, 0.4);
      });
      const archBeam = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 7.2), darkWoodMat);
      archBeam.position.set(255, 4.8, Z(185));
      farmGrp.add(archBeam);

      const farmSign = makeSign(
        ['FAR ENOUGH FARM', 'ESTABLISHED 1959 • FREE HISTORIC PETTING FARM'],
        11.5, 1.8,
        { bg: '#7f1d1d', fg: '#fef3c7', borderColor: '#f59e0b' }
      );
      farmSign.position.set(255, 5.8, Z(185));
      farmSign.rotation.y = -Math.PI / 2;
      farmGrp.add(farmSign);

      // 2. THE BIG RED BARN at (295, Z(185))
      const barnBody = new THREE.Mesh(
        new THREE.BoxGeometry(20.0, 6.5, 13.0),
        new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.7 })
      );
      barnBody.position.set(295, 3.25, Z(185));
      farmGrp.add(barnBody);
      rectOb(284, 306, Z(177.5), Z(192.5)); // Barn walls block collision

      // Gambrel Barn Roof (Traditional double-sloped red roof with white fascia)
      const roofLower = new THREE.Mesh(
        new THREE.BoxGeometry(20.4, 3.2, 13.4),
        new THREE.MeshStandardMaterial({ color: 0x7f1d1d, roughness: 0.6 })
      );
      roofLower.position.set(295, 7.8, Z(185));
      farmGrp.add(roofLower);

      const roofUpper = new THREE.Mesh(
        new THREE.ConeGeometry(9.2, 3.6, 4),
        new THREE.MeshStandardMaterial({ color: 0x7f1d1d, roughness: 0.6 })
      );
      roofUpper.rotation.y = Math.PI / 4;
      roofUpper.position.set(295, 10.8, Z(185));
      farmGrp.add(roofUpper);

      // Rooftop Cupola with Golden Rooster Weather Vane
      const cupola = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.6, 2.0), new THREE.MeshStandardMaterial({ color: 0xf8fafc }));
      cupola.position.set(295, 12.8, Z(185));
      farmGrp.add(cupola);

      const vanePole = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.6, 6), metalMat);
      vanePole.position.set(295, 14.0, Z(185));
      farmGrp.add(vanePole);

      const rooster = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.4, 0.1), new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.8 }));
      rooster.position.set(295, 14.6, Z(185));
      farmGrp.add(rooster);

      // White double barn doors with cross-bucks
      const doorL = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4.2, 2.5), new THREE.MeshStandardMaterial({ color: 0xf8fafc }));
      doorL.position.set(284.9, 2.1, Z(183.5));
      farmGrp.add(doorL);
      const doorR = new THREE.Mesh(new THREE.BoxGeometry(0.2, 4.2, 2.5), new THREE.MeshStandardMaterial({ color: 0xf8fafc }));
      doorR.position.set(284.9, 2.1, Z(186.5));
      farmGrp.add(doorR);

      // Straw bales stacked near barn entrance
      [-1.2, 0, 1.2].forEach((oz, bi) => {
        const bale = new THREE.Mesh(
          new THREE.BoxGeometry(1.4, 0.7, 0.9),
          new THREE.MeshStandardMaterial({ color: 0xfde047, roughness: 0.9 })
        );
        bale.position.set(283.5, GROUND_Y + 0.35 + (bi === 1 ? 0.7 : 0), Z(180) + oz);
        farmGrp.add(bale);
        circOb(283.5, Z(180) + oz, 0.6);
      });

      // 3. FARM SILO at (312, Z(175))
      const silo = new THREE.Mesh(
        new THREE.CylinderGeometry(2.8, 2.8, 13.0, 16),
        new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.6 })
      );
      silo.position.set(312, 6.5, Z(175));
      farmGrp.add(silo);
      circOb(312, Z(175), 3.0); // solid silo

      // Galvanized metal dome cap
      const siloDome = new THREE.Mesh(
        new THREE.SphereGeometry(2.82, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.5),
        metalMat
      );
      siloDome.position.set(312, 13.0, Z(175));
      farmGrp.add(siloDome);

      // 4. VINTAGE RED FARMALL TRACTOR at (282, Z(192))
      const trGrpTractor = new THREE.Group();
      trGrpTractor.position.set(282, GROUND_Y, Z(192));
      trGrpTractor.rotation.y = 0.4;

      // Red chassis and engine hood
      const hood = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.9, 2.4), new THREE.MeshStandardMaterial({ color: 0xdc2626, roughness: 0.4 }));
      hood.position.set(0, 0.9, 0.4);
      trGrpTractor.add(hood);

      // Big rear tractor wheels
      const wheelMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.9 });
      [-0.8, 0.8].forEach(wx => {
        const rWheel = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 0.35, 14), wheelMat);
        rWheel.rotation.z = Math.PI / 2;
        rWheel.position.set(wx, 0.9, -0.6);
        trGrpTractor.add(rWheel);
      });

      // Front small steering wheels
      [-0.5, 0.5].forEach(wx => {
        const fWheel = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 0.22, 10), wheelMat);
        fWheel.rotation.z = Math.PI / 2;
        fWheel.position.set(wx, 0.45, 1.4);
        trGrpTractor.add(fWheel);
      });

      // Vertical exhaust pipe
      const exPipe = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 1.2, 6), metalMat);
      exPipe.position.set(0.4, 1.7, 0.9);
      trGrpTractor.add(exPipe);

      farmGrp.add(trGrpTractor);
      circOb(282, Z(192), 1.5);

      // 5. POST-AND-RAIL FENCES & ANIMAL PADDOCKS
      // Paddock A: Sheep Pasture at (278, Z(165))
      // Paddock B: Horse / Pony Corral at (324, Z(200))
      // Paddock C: Holstein Dairy Cows at (324, Z(160))
      // Paddock D: Goats & Pigs at (278, Z(205))
      const padFences = [
        [268, 288, Z(154), Z(176)], // Sheep
        [312, 336, Z(188), Z(214)], // Horses
        [312, 336, Z(148), Z(174)], // Cows
        [268, 288, Z(196), Z(216)]  // Goats & Pigs
      ];

      padFences.forEach(([x0, x1, z0, z1]) => {
        // Wooden corner posts
        [[x0, z0], [x1, z0], [x0, z1], [x1, z1]].forEach(([px, pz]) => {
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.14, 1.4, 6), darkWoodMat);
          post.position.set(px, GROUND_Y + 0.7, pz);
          farmGrp.add(post);
        });
        // Perimeter rails
        const lenX = x1 - x0, lenZ = z1 - z0;
        [0.4, 0.9].forEach(ry => {
          const r1 = new THREE.Mesh(new THREE.BoxGeometry(lenX, 0.1, 0.08), woodMat);
          r1.position.set((x0 + x1) / 2, GROUND_Y + ry, z0);
          farmGrp.add(r1);
          const r2 = new THREE.Mesh(new THREE.BoxGeometry(lenX, 0.1, 0.08), woodMat);
          r2.position.set((x0 + x1) / 2, GROUND_Y + ry, z1);
          farmGrp.add(r2);
          const r3 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.1, lenZ), woodMat);
          r3.position.set(x0, GROUND_Y + ry, (z0 + z1) / 2);
          farmGrp.add(r3);
          const r4 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.1, lenZ), woodMat);
          r4.position.set(x1, GROUND_Y + ry, (z0 + z1) / 2);
          farmGrp.add(r4);
        });
      });

      // 6. ANIMALS IN THE PADDOCKS
      // A. Sheep in Sheep Pasture (fluffy white bodies, black faces & legs)
      const sheepMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.9 });
      const sheepFaceMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.8 });
      [
        [273, Z(160), 0.5], [280, Z(163), -0.8], [276, Z(170), 1.2], [283, Z(168), 2.1]
      ].forEach(([sx, sz, srot]) => {
        const shp = new THREE.Group();
        shp.position.set(sx, GROUND_Y, sz);
        shp.rotation.y = srot;

        const body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 8, 8), sheepMat);
        body.scale.set(1.4, 1.0, 1.0);
        body.position.y = 0.65;
        shp.add(body);

        const head = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.4), sheepFaceMat);
        head.position.set(0.85, 0.85, 0);
        shp.add(head);

        [-0.4, 0.4].forEach(lx => {
          [-0.25, 0.25].forEach(lz => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.45, 6), sheepFaceMat);
            leg.position.set(lx, 0.22, lz);
            shp.add(leg);
          });
        });

        farmGrp.add(shp);
        circOb(sx, sz, 0.7);
      });

      // B. Horses in Horse Corral (chestnut & black horses)
      const horseCols = [0x78350f, 0x1c1917];
      [
        [320, Z(196), 0.3, horseCols[0]], [328, Z(206), -1.1, horseCols[1]]
      ].forEach(([hx, hz, hrot, col]) => {
        const hrs = new THREE.Group();
        hrs.position.set(hx, GROUND_Y, hz);
        hrs.rotation.y = hrot;

        const hMat = new THREE.MeshStandardMaterial({ color: col, roughness: 0.6 });
        const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.9, 0.8), hMat);
        body.position.y = 1.35;
        hrs.add(body);

        const neck = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.9, 0.4), hMat);
        neck.position.set(0.9, 1.8, 0);
        neck.rotation.z = -0.4;
        hrs.add(neck);

        const head = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.4, 0.35), hMat);
        head.position.set(1.3, 2.1, 0);
        hrs.add(head);

        [-0.6, 0.6].forEach(lx => {
          [-0.25, 0.25].forEach(lz => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 0.9, 6), hMat);
            leg.position.set(lx, 0.45, lz);
            hrs.add(leg);
          });
        });

        farmGrp.add(hrs);
        circOb(hx, hz, 1.1);
      });

      // C. Holstein Dairy Cows (black-and-white spotted cows)
      const cowMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.7 });
      const cowSpotMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.7 });
      [
        [320, Z(156), 0.6], [328, Z(165), -0.7]
      ].forEach(([cx, cz, crot]) => {
        const cw = new THREE.Group();
        cw.position.set(cx, GROUND_Y, cz);
        cw.rotation.y = crot;

        const body = new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.1, 0.9), cowMat);
        body.position.y = 1.25;
        cw.add(body);

        const spot = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.9, 0.92), cowSpotMat);
        spot.position.set(0.2, 1.25, 0);
        cw.add(spot);

        const head = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.55, 0.5), cowMat);
        head.position.set(1.3, 1.6, 0);
        cw.add(head);

        [-0.7, 0.7].forEach(lx => {
          [-0.3, 0.3].forEach(lz => {
            const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.75, 6), cowSpotMat);
            leg.position.set(lx, 0.38, lz);
            cw.add(leg);
          });
        });

        farmGrp.add(cw);
        circOb(cx, cz, 1.2);
      });

      // D. Goats & Pigs in Paddock D
      // Cable spool climbing ramp for goats
      const spool = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.8, 10), woodMat);
      spool.position.set(278, GROUND_Y + 0.4, Z(206));
      farmGrp.add(spool);
      circOb(278, Z(206), 1.2);

      // Goat standing on spool
      const goatMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.7 });
      const gt = new THREE.Group();
      gt.position.set(278, GROUND_Y + 0.8, Z(206));
      const gBody = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.55, 0.45), goatMat);
      gBody.position.y = 0.5;
      gt.add(gBody);
      const gHead = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.35, 0.3), goatMat);
      gHead.position.set(0.5, 0.8, 0);
      gt.add(gHead);
      farmGrp.add(gt);

      // Pink Pigs near shelter
      const pigMat = new THREE.MeshStandardMaterial({ color: 0xf472b6, roughness: 0.6 });
      [[273, Z(211)], [283, Z(210)]].forEach(([px, pz]) => {
        const pg = new THREE.Group();
        pg.position.set(px, GROUND_Y, pz);
        const pBody = new THREE.Mesh(new THREE.SphereGeometry(0.48, 8, 8), pigMat);
        pBody.scale.set(1.3, 0.9, 0.9);
        pBody.position.y = 0.42;
        pg.add(pBody);
        farmGrp.add(pg);
        circOb(px, pz, 0.6);
      });

      islandsGroup.add(farmGrp);
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
    // Landmark: South Beach & Pier Pavilion Complex (Cafe/Grill, Bike Rental, Lockers)
    // Located at the head of the 120m pier along the South Beach Boardwalk (z ~ Z(455))
    // ------------------------------------------------------------------------
    {
      const sbg = new THREE.Group();

      // 1. South Beach Cafe & Grill with Outdoor Beachfront Patio (x = 34, z = Z(455))
      const cafeDeck = new THREE.Mesh(new THREE.BoxGeometry(28, 0.3, 20), woodMat);
      cafeDeck.position.set(34, 0.65, Z(455));
      sbg.add(cafeDeck);

      const cafeBldg = new THREE.Mesh(new THREE.BoxGeometry(22, 4.8, 11), darkWoodMat);
      cafeBldg.position.set(34, 2.9, Z(448));
      sbg.add(cafeBldg);

      const cafeRoof = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 13.5, 2.4, 4, 1), new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.8 }));
      cafeRoof.scale.set(1.1, 1, 0.7);
      cafeRoof.rotation.y = Math.PI / 4;
      cafeRoof.position.set(34, 5.8, Z(448));
      sbg.add(cafeRoof);

      const cafeSign = makeSign(
        ['SOUTH BEACH CAFE & GRILL', 'BEACHFRONT PATIO • BURGERS • ICE CREAM • REFRESHMENTS'],
        20, 2.2,
        { bg: '#854d0e', fg: '#fef08a', borderColor: '#eab308' }
      );
      cafeSign.position.set(34, 5.0, Z(453.7));
      sbg.add(cafeSign);

      // Outdoor Dining Pergola with picnic tables & umbrellas
      [-8, 0, 8].forEach(px => {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.3, 3.2, 0.3), darkWoodMat);
        post.position.set(34 + px, 2.1, Z(461));
        sbg.add(post);
      });
      const pergolaBeam = new THREE.Mesh(new THREE.BoxGeometry(19, 0.25, 0.3), darkWoodMat);
      pergolaBeam.position.set(34, 3.7, Z(461));
      sbg.add(pergolaBeam);

      // Patio Tables with Umbrellas
      const tableGeo = new THREE.CylinderGeometry(1.2, 1.2, 0.1, 12);
      const umbrellaGeo = new THREE.ConeGeometry(2.0, 0.9, 12);
      const uColors = [0x3b82f6, 0xfacc15, 0xef4444, 0x10b981];
      [[-7, Z(457)], [0, Z(457)], [7, Z(457)], [-7, Z(462)], [0, Z(462)], [7, Z(462)]].forEach(([tx, tz], i) => {
        const tbl = new THREE.Mesh(tableGeo, woodMat);
        tbl.position.set(34 + tx, 1.35, tz);
        sbg.add(tbl);
        const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.8, 6), metalMat);
        pole.position.set(34 + tx, 2.0, tz);
        sbg.add(pole);
        const umb = new THREE.Mesh(umbrellaGeo, new THREE.MeshStandardMaterial({ color: uColors[i % uColors.length], roughness: 0.6 }));
        umb.position.set(34 + tx, 3.2, tz);
        sbg.add(umb);
      });
      rectOb(23, 45, Z(442), Z(454));

      // 2. Toronto Island Bicycle Rental Building (x = -34, z = Z(455))
      const bikeDeck = new THREE.Mesh(new THREE.BoxGeometry(26, 0.3, 18), woodMat);
      bikeDeck.position.set(-34, 0.65, Z(455));
      sbg.add(bikeDeck);

      const bikeBldg = new THREE.Mesh(new THREE.BoxGeometry(20, 4.4, 10), new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.6 }));
      bikeBldg.position.set(-34, 2.7, Z(448));
      sbg.add(bikeBldg);

      const bikeRoof = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 12.5, 2.2, 4, 1), new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.7 }));
      bikeRoof.scale.set(1.1, 1, 0.7);
      bikeRoof.rotation.y = Math.PI / 4;
      bikeRoof.position.set(-34, 5.4, Z(448));
      sbg.add(bikeRoof);

      const bikeSign = makeSign(
        ['TORONTO ISLAND BICYCLE RENTAL', 'QUADRICYCLES (SURREYS) • TANDEM BIKES • CRUISERS'],
        20, 2.2,
        { bg: '#991b1b', fg: '#fef9c3', borderColor: '#f87171' }
      );
      bikeSign.position.set(-34, 4.8, Z(453.2));
      sbg.add(bikeSign);

      // Staged Quadricycle (4-wheel Surrey) Carts & Tandem Bicycles
      function makeSurrey(col, sx, sz) {
        const sg = new THREE.Group();
        const frame = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.3, 2.8), new THREE.MeshStandardMaterial({ color: col, roughness: 0.4 }));
        frame.position.y = 0.5;
        sg.add(frame);
        [-0.8, 0.8].forEach(wx => {
          [-1.1, 1.1].forEach(wz => {
            const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.35, 0.12, 12), metalMat);
            wh.rotation.z = Math.PI / 2;
            wh.position.set(wx, 0.35, wz);
            sg.add(wh);
          });
        });
        const canopy = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.15, 2.9), new THREE.MeshStandardMaterial({ color: 0xfef08a, roughness: 0.6 }));
        canopy.position.y = 1.85;
        sg.add(canopy);
        [-0.75, 0.75].forEach(cx => {
          [-1.3, 1.3].forEach(cz => {
            const post = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.35, 6), metalMat);
            post.position.set(cx, 1.2, cz);
            sg.add(post);
          });
        });
        sg.position.set(sx, 0.65, sz);
        return sg;
      }
      sbg.add(makeSurrey(0xef4444, -40, Z(459)));
      sbg.add(makeSurrey(0x2563eb, -34, Z(459)));
      sbg.add(makeSurrey(0x16a34a, -28, Z(459)));
      rectOb(-44, -24, Z(443), Z(453));

      // 3. Beach Lockers & Changing Pavilion (x = -10, z = Z(452))
      const lockerBldg = new THREE.Mesh(new THREE.BoxGeometry(12, 4.2, 9), new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.8 }));
      lockerBldg.position.set(-10, 2.6, Z(450));
      sbg.add(lockerBldg);

      const lockerSign = makeSign(
        ['BEACH LOCKERS & CHANGING ROOMS', 'PUBLIC WASHROOMS • RINSE SHOWERS'],
        13, 1.7,
        { bg: '#1e3a8a', fg: '#bae6fd', borderColor: '#38bdf8' }
      );
      lockerSign.position.set(-10, 4.5, Z(454.7));
      sbg.add(lockerSign);

      // Outdoor Fresh-Water Rinse Showers on concrete pad
      const showerPad = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.1, 3.5), new THREE.MeshStandardMaterial({ color: 0x94a3b8 }));
      showerPad.position.set(-10, 0.6, Z(457.5));
      sbg.add(showerPad);
      [-0.8, 0.8].forEach(sx => {
        const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.6, 8), metalMat);
        pipe.position.set(-10 + sx, 1.8, Z(457.5));
        sbg.add(pipe);
        const head = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.05, 0.1, 8), metalMat);
        head.position.set(-10 + sx, 3.0, Z(457.5));
        sbg.add(head);
      });
      rectOb(-16, -4, Z(445), Z(455));

      // 4. Lifeguard Watchtower at pier entrance (x = 0, z = Z(466))
      const lgTower = new THREE.Group();
      [-1.4, 1.4].forEach(tx => {
        [-1.4, 1.4].forEach(tz => {
          const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.2, 5.6, 6), woodMat);
          leg.position.set(tx, 2.8, tz);
          lgTower.add(leg);
        });
      });
      const lgDeck = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.3, 3.6), woodMat);
      lgDeck.position.y = 5.4;
      lgTower.add(lgDeck);
      const lgRoof = new THREE.Mesh(new THREE.ConeGeometry(2.8, 1.2, 4), new THREE.MeshStandardMaterial({ color: 0xdc2626 }));
      lgRoof.rotation.y = Math.PI / 4;
      lgRoof.position.y = 7.4;
      lgTower.add(lgRoof);
      const lgFlag = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.7, 1.2), new THREE.MeshBasicMaterial({ color: 0xdc2626, fog: false }));
      lgFlag.position.set(0, 8.4, 0.6);
      lgTower.add(lgFlag);
      lgTower.position.set(0, 0.55, Z(466));
      sbg.add(lgTower);
      circOb(0, Z(466), 1.6);

      islandsGroup.add(sbg);
    }

    // ------------------------------------------------------------------------
    // Wildlife: Flocks of Canada Geese grazing on lawns & Seagulls along the pier
    // ------------------------------------------------------------------------
    const grazingGeese = [];
    {
      const wg = new THREE.Group();
      const gooseBodyMat = new THREE.MeshStandardMaterial({ color: 0x4a433b, roughness: 0.8 });
      const gooseBlackMat = new THREE.MeshStandardMaterial({ color: 0x171717, roughness: 0.7 });
      const gooseWhiteMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc });

      function makeCanadaGoose() {
        const g = new THREE.Group();
        g.scale.setScalar(1.25); // easily visible
        const body = new THREE.Mesh(new THREE.SphereGeometry(0.32, 10, 8), gooseBodyMat);
        body.scale.set(1.4, 0.75, 0.85);
        body.position.y = 0.35;
        g.add(body);
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.08, 0.5, 8), gooseBlackMat);
        neck.position.set(0.32, 0.6, 0);
        neck.rotation.z = -0.3;
        g.add(neck);
        g.neck = neck;
        const head = new THREE.Mesh(new THREE.SphereGeometry(0.09, 8, 6), gooseBlackMat);
        head.position.set(0.42, 0.85, 0);
        g.add(head);
        g.head = head;
        const chin = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.08, 0.16), gooseWhiteMat);
        chin.position.set(0.41, 0.83, 0);
        g.add(chin);
        const bill = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.16, 6), gooseBlackMat);
        bill.rotation.z = -Math.PI / 2;
        bill.position.set(0.54, 0.84, 0);
        g.add(bill);
        return g;
      }

      // Flocks grazing peacefully on lawns across the islands
      const gooseFlocks = [
        { cx: 16, cz: Z(25), count: 6, r: 8 }, // Ferry Dock arrival lawn
        { cx: 32, cz: Z(105), count: 5, r: 8 }, // Near First Bridge & BBQ patio
        { cx: 0, cz: Z(315), count: 6, r: 10 }, // Near Grand Fountain
        { cx: 260, cz: Z(150), count: 6, r: 12 }, // Far Enough Farm pasture
        { cx: -160, cz: Z(325), count: 8, r: 18 }, // Olympic Island Great Lawn
        { cx: 110, cz: Z(230), count: 6, r: 12 },
        { cx: 580, cz: Z(290), count: 6, r: 14 },
        { cx: -25, cz: Z(430), count: 5, r: 10 }
      ];

      gooseFlocks.forEach(flock => {
        for (let i = 0; i < flock.count; i++) {
          const a = rnd() * Math.PI * 2, d = rnd() * flock.r;
          const gx = flock.cx + Math.cos(a) * d, gz = flock.cz + Math.sin(a) * d;
          if (landField(gx, gz) > 2) {
            const goose = makeCanadaGoose();
            const y = terrainH(gx, gz);
            goose.position.set(gx, y, gz);
            goose.rotation.y = rnd() * Math.PI * 2;
            wg.add(goose);
            grazingGeese.push({ obj: goose, phase: rnd() * 6.28, speed: 1.5 + rnd() });
          }
        }
      });

      // Seagulls perched along the Centre Island Pier railings
      const gullWhite = new THREE.MeshBasicMaterial({ color: 0xf1f5f9 });
      const gullGrey = new THREE.MeshBasicMaterial({ color: 0x94a3b8 });
      const gullBeak = new THREE.MeshBasicMaterial({ color: 0xfacc15 });
      function makeSeagull() {
        const sg = new THREE.Group();
        const b = new THREE.Mesh(new THREE.SphereGeometry(0.18, 8, 6), gullWhite);
        b.scale.set(1.4, 0.7, 0.8);
        sg.add(b);
        const w = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.08, 0.35), gullGrey);
        w.position.set(-0.05, 0.08, 0);
        sg.add(w);
        const bk = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.16, 5), gullBeak);
        bk.rotation.z = -Math.PI / 2;
        bk.position.set(0.28, 0.05, 0);
        sg.add(bk);
        return sg;
      }

      for (let pz = Z(475); pz <= Z(580); pz += 12) {
        [-5.8, 5.8].forEach(px => {
          if (rnd() < 0.6) {
            const gull = makeSeagull();
            gull.position.set(px, 1.5, pz);
            gull.rotation.y = px > 0 ? -1.2 : 1.2;
            wg.add(gull);
          }
        });
      }
      islandsGroup.add(wg);
    }

    // ------------------------------------------------------------------------
    // Wildlife and Boats: Swimming Swans, Moored Canoes, Harbour Ferry
    // ------------------------------------------------------------------------
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
    // Distant 3D Toronto Skyline across Toronto Harbour (Illuminated Night Skyline)
    // Towering skyscrapers with glowing office window grids, illuminated crowns,
    // Rogers Centre blue ring, and the illuminated CN Tower with LED shaft tracks,
    // observation deck window band, and flashing aviation beacons!
    // ------------------------------------------------------------------------
    let cnBeacon = null, towerBeacons = [];
    {
      const skyGrp = new THREE.Group();
      const skyZ = Z(-1600);

      // Procedural 256x512 glowing window texture for skyscraper facades
      const winCan = document.createElement('canvas');
      winCan.width = 256;
      winCan.height = 512;
      const wg = winCan.getContext('2d');
      if (wg) {
        wg.fillStyle = '#090d16'; // dark facade background
        wg.fillRect(0, 0, 256, 512);
        const winCols = ['#fef08a', '#fde047', '#fed7aa', '#bae6fd', '#e0f2fe', '#ffffff'];
        for (let wy = 8; wy < 504; wy += 14) {
          for (let wx = 6; wx < 250; wx += 10) {
            if (Math.random() < 0.65) {
              wg.fillStyle = winCols[Math.floor(Math.random() * winCols.length)];
              wg.fillRect(wx, wy, 6, 8);
            }
          }
        }
      }
      const winTex = new THREE.CanvasTexture(winCan);
      winTex.wrapS = THREE.RepeatWrapping;
      winTex.wrapT = THREE.RepeatWrapping;
      const litTowerMat = new THREE.MeshBasicMaterial({ map: winTex, fog: false });

      // CN Tower (553m) - Full Architectural Detail & Lighting
      const cn = new THREE.Group();
      // Hexagonal tripod base (0-90m)
      const base = new THREE.Mesh(new THREE.ConeGeometry(22, 180, 3), concreteMat);
      base.position.y = 90;
      cn.add(base);

      // Main concrete shaft (90-340m)
      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(4.4, 6.2, 250, 12), concreteMat);
      shaft.position.y = 215;
      cn.add(shaft);

      // Dual continuous vertical LED light strips on shaft (Cyan and Magenta)
      const ledStrip1 = new THREE.Mesh(
        new THREE.BoxGeometry(0.5, 248, 0.3),
        new THREE.MeshBasicMaterial({ color: 0x38bdf8, fog: false }) // brilliant cyan LED
      );
      ledStrip1.position.set(0, 215, 4.6);
      cn.add(ledStrip1);

      const ledStrip2 = new THREE.Mesh(
        new THREE.BoxGeometry(0.5, 248, 0.3),
        new THREE.MeshBasicMaterial({ color: 0xec4899, fog: false }) // brilliant magenta LED
      );
      ledStrip2.position.set(0, 215, -4.6);
      cn.add(ledStrip2);

      // 7-story Main Observation Deck Pod (342-360m)
      const pod = new THREE.Mesh(new THREE.CylinderGeometry(19, 14, 18, 16), concreteMat);
      pod.position.y = 351;
      cn.add(pod);

      // 360-degree glowing observation window band
      const podWindows = new THREE.Mesh(
        new THREE.CylinderGeometry(19.2, 19.2, 5.0, 16),
        new THREE.MeshBasicMaterial({ color: 0xfef08a, fog: false })
      );
      podWindows.position.y = 351;
      cn.add(podWindows);

      // SkyPod (upper observation pod at 447m)
      const skyPod = new THREE.Mesh(new THREE.CylinderGeometry(8.5, 7.0, 10, 12), concreteMat);
      skyPod.position.y = 432;
      cn.add(skyPod);
      const skyPodBand = new THREE.Mesh(
        new THREE.CylinderGeometry(8.6, 8.6, 3.2, 12),
        new THREE.MeshBasicMaterial({ color: 0xfef9c3, fog: false })
      );
      skyPodBand.position.y = 432;
      cn.add(skyPodBand);

      // Transmission Spire / Antenna Mast (447-553m)
      const spire = new THREE.Mesh(new THREE.ConeGeometry(1.8, 118, 8), metalMat);
      spire.position.y = 496;
      cn.add(spire);

      // Flashing summit aviation obstruction beacon at 553m
      cnBeacon = new THREE.Mesh(
        new THREE.SphereGeometry(2.4, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0xef4444, fog: false })
      );
      cnBeacon.position.y = 553;
      cn.add(cnBeacon);

      cn.position.set(-280, 0, skyZ);
      skyGrp.add(cn);

      // Rogers Centre Dome with blue perimeter ring
      const dome = new THREE.Mesh(new THREE.SphereGeometry(46, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.48), concreteMat);
      dome.position.set(-440, 22, skyZ + 40);
      skyGrp.add(dome);

      const domeRing = new THREE.Mesh(
        new THREE.TorusGeometry(46.2, 1.2, 8, 32),
        new THREE.MeshBasicMaterial({ color: 0x1d4ed8, fog: false }) // bright blue stadium glow
      );
      domeRing.rotation.x = Math.PI / 2;
      domeRing.position.set(-440, 24, skyZ + 40);
      skyGrp.add(domeRing);

      // Financial District Skyscrapers with illuminated windows and architectural crowns:
      // 1. First Canadian Place (298m) - White illuminated mechanical penthouse roof
      const fcp = new THREE.Mesh(new THREE.BoxGeometry(36, 298, 36), litTowerMat);
      fcp.position.set(100, 149, skyZ);
      skyGrp.add(fcp);
      const fcpCrown = new THREE.Mesh(new THREE.BoxGeometry(32, 12, 32), new THREE.MeshBasicMaterial({ color: 0xffffff, fog: false }));
      fcpCrown.position.set(100, 304, skyZ);
      skyGrp.add(fcpCrown);
      const fcpB1 = new THREE.Mesh(new THREE.SphereGeometry(1.5, 6, 6), new THREE.MeshBasicMaterial({ color: 0xef4444, fog: false }));
      fcpB1.position.set(100, 311, skyZ);
      skyGrp.add(fcpB1);
      towerBeacons.push(fcpB1);

      // 2. Scotia Plaza (275m) - Deep red chevron / pyramid crown
      const scotia = new THREE.Mesh(new THREE.BoxGeometry(32, 275, 32), litTowerMat);
      scotia.position.set(180, 137.5, skyZ + 20);
      skyGrp.add(scotia);
      const scotiaCrown = new THREE.Mesh(new THREE.ConeGeometry(18, 22, 4), new THREE.MeshBasicMaterial({ color: 0xdc2626, fog: false }));
      scotiaCrown.rotation.y = Math.PI / 4;
      scotiaCrown.position.set(180, 286, skyZ + 20);
      skyGrp.add(scotiaCrown);

      // 3. TD Centre (222m) - Mies van der Rohe dark bronze towers with green illuminated TD logo band
      const td = new THREE.Mesh(new THREE.BoxGeometry(42, 222, 42), litTowerMat);
      td.position.set(-40, 111, skyZ - 10);
      skyGrp.add(td);
      const tdCrown = new THREE.Mesh(new THREE.BoxGeometry(42.5, 6, 42.5), new THREE.MeshBasicMaterial({ color: 0x16a34a, fog: false }));
      tdCrown.position.set(-40, 225, skyZ - 10);
      skyGrp.add(tdCrown);

      // 4. Royal Bank Plaza (180m) - Gold reflective towers with golden crown
      const rbc = new THREE.Mesh(new THREE.BoxGeometry(36, 180, 36), litTowerMat);
      rbc.position.set(-120, 90, skyZ + 15);
      skyGrp.add(rbc);
      const rbcCrown = new THREE.Mesh(new THREE.BoxGeometry(36.5, 6, 36.5), new THREE.MeshBasicMaterial({ color: 0xf59e0b, fog: false }));
      rbcCrown.position.set(-120, 183, skyZ + 15);
      skyGrp.add(rbcCrown);

      // 5. Bay Wellington / Brookfield Place (260m) - Glowing glass pyramid crown
      const bwp = new THREE.Mesh(new THREE.BoxGeometry(34, 260, 34), litTowerMat);
      bwp.position.set(280, 130, skyZ + 10);
      skyGrp.add(bwp);
      const bwpCrown = new THREE.Mesh(new THREE.ConeGeometry(17, 16, 4), new THREE.MeshBasicMaterial({ color: 0x38bdf8, fog: false }));
      bwpCrown.rotation.y = Math.PI / 4;
      bwpCrown.position.set(280, 268, skyZ + 10);
      skyGrp.add(bwpCrown);

      // 40 additional illuminated skyline towers stretching along the harbour shore
      for (let k = 0; k < 42; k++) {
        const tx = -720 + k * 35 + (k % 3) * 6;
        if (Math.abs(tx - (-280)) < 30 || Math.abs(tx - (-440)) < 40) continue; // avoid clipping CN Tower / dome
        const th = 60 + (k * 43) % 150 + (k % 5) * 18;
        const tw = 20 + (k * 7) % 18, tdLen = 20 + (k * 11) % 16;
        const dz = 30 + (k * 19) % 140;
        const b = new THREE.Mesh(new THREE.BoxGeometry(tw, th, tdLen), litTowerMat);
        b.position.set(tx, th / 2, skyZ + dz);
        skyGrp.add(b);

        // Lit rooftop crown band on taller towers
        if (th > 140) {
          const crMat = new THREE.MeshBasicMaterial({ color: [0x38bdf8, 0xfacc15, 0xef4444, 0x10b981, 0xa855f7][k % 5], fog: false });
          const cr = new THREE.Mesh(new THREE.BoxGeometry(tw + 0.5, 4.0, tdLen + 0.5), crMat);
          cr.position.set(tx, th + 2.0, skyZ + dz);
          skyGrp.add(cr);
        }
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
      // Specific landmarks
      if (x >= 260 && x <= 345 && z >= Z(140) && z <= Z(225)) return 'FAR ENOUGH FARM • PETTING FARM';
      if (x >= 135 && x <= 245 && z >= Z(155) && z <= Z(245)) return 'CENTREVILLE TURN-OF-THE-CENTURY VILLAGE';
      if (Math.hypot(x - 160, z - Z(165)) < 16) return 'CENTREVILLE RAILWAY STATION';
      if (x >= 25 && x <= 135 && z >= Z(155) && z <= Z(210)) return 'WOODED PATH TO CENTREVILLE';
      if (x >= 50 && x <= 80 && z >= Z(50) && z <= Z(95)) return 'TORONTO ISLAND BBQ & BEER CO. PATIO';
      if (Math.hypot(x - 12, z - Z(48)) < 12) return 'PIZZA PIZZA • ISLAND CONCESSIONS';
      if (Math.hypot(x - 12, z - Z(66)) < 12) return 'SUBWAY • FRESH SUBS';
      if (Math.hypot(x - 12, z - Z(88)) < 14) return 'PARK WASHROOMS & PUBLIC LOCKERS';
      if (x >= -25 && x <= 45 && z >= Z(-15) && z <= Z(115)) return 'CENTRE ISLAND ARRIVAL PLAZA';
      if (Math.hypot(x, z - Z(310)) < 26) return 'AVENUE OF THE ISLANDS • GRAND FOUNTAIN';
      if (Math.abs(x) < 45 && z >= Z(330) && z <= Z(425)) return 'GRAND FORMAL GARDENS & REFLECTING POOLS';
      if (x >= -105 && x <= -25 && z >= Z(350) && z <= Z(425)) return 'WILLIAM MEANY HEDGE MAZE';
      if (Math.hypot(x - 34, z - Z(455)) < 22) return 'SOUTH BEACH CAFE & PATIO';
      if (Math.hypot(x + 34, z - Z(455)) < 22) return 'TORONTO ISLAND BICYCLE RENTAL';
      if (Math.hypot(x + 10, z - Z(452)) < 15) return 'BEACH LOCKERS & PAVILION';
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
      if (Math.abs(x) < 45 && z < Z(245)) return 'AVENUE OF THE ISLANDS';
      if (x < -280) return 'GIBRALTAR POINT WOODS';
      return 'CENTRE ISLAND PARK';
    }

    // ------------------------------------------------------------------------
    // Animation Loop
    // ------------------------------------------------------------------------
    let tTime = 0, ferryT = 0, miniTrainT = 0;
    function update(dt, playerPos) {
      tTime += dt;
      if (ferrisWheelMesh) ferrisWheelMesh.rotation.x += dt * 0.22;
      if (carouselTop) carouselTop.rotation.y += dt * 0.6;
      if (fountainSpray) fountainSpray.scale.y = 0.95 + Math.sin(tTime * 4.5) * 0.12;
      if (lighthouseBeacon) lighthouseBeacon.rotation.y += dt * 1.8;
      if (radarDish) radarDish.rotation.y += dt * 3.2;

      // Miniature Steam Train moving smoothly along track loop
      if (miniTrain) {
        miniTrainT = (miniTrainT + dt * 0.016) % 1.0;
        const tr = evalTrainTrack(miniTrainT);
        miniTrain.position.set(tr.x, GROUND_Y + 0.12, tr.z);
        miniTrain.rotation.y = tr.yaw;
        if (miniTrainPuff) {
          miniTrainPuff.scale.setScalar(0.85 + Math.sin(tTime * 12.0) * 0.35);
          miniTrainPuff.position.y = 1.85 + Math.sin(tTime * 8.0) * 0.12;
        }
      }

      // Flashing CN Tower & skyscraper obstruction beacons
      if (cnBeacon) {
        const flash = (Math.sin(tTime * 3.5) > 0.3) ? 1.0 : 0.12;
        cnBeacon.visible = flash > 0.5;
        towerBeacons.forEach(b => { b.visible = flash > 0.5; });
      }

      // Bubbler fountain jets in the twin reflecting pools
      poolJets.forEach((jet, ji) => {
        jet.scale.y = 0.85 + Math.sin(tTime * 5.0 + ji * 1.4) * 0.3;
      });

      // Canada Geese pecking & bobbing
      grazingGeese.forEach(g => {
        if (g.obj.neck) {
          g.obj.neck.rotation.x = Math.sin(tTime * g.speed + g.phase) * 0.35;
        }
      });

      // Swimming swans & wildlife
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
        try {
          ctx.imageSmoothingEnabled = true;
          ctx.drawImage(MM, sx, sz, VIEW / STEP, VIEW / STEP, 0, 0, size, size);
        } catch (e) {}
      }

      const toM = (x, z) => [(x - playerPos.x) / VIEW * size + size / 2, (z - playerPos.z) / VIEW * size + size / 2];
      ctx.font = 'bold 9px sans-serif';
      ctx.fillStyle = '#f8fafc';
      [
        ['FERRY', 0, Z(-5)],
        ['BBQ', 65, Z(65)],
        ['VILLAGE', 180, Z(185)],
        ['TRAIN', 160, Z(165)],
        ['FARM', 295, Z(185)],
        ['FOUNTAIN', 0, Z(310)],
        ['GARDENS', 0, Z(380)],
        ['MAZE', -65, Z(385)],
        ['CAFE', 34, Z(455)],
        ['BIKES', -34, Z(455)],
        ['AIRPORT', -1260, Z(-200)],
        ['LIGHTHOUSE', -480, Z(320)],
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
        pizzaPizza: [12, Z(48)],
        subway: [12, Z(66)],
        islandLockers: [12, Z(88)],
        islandBBQ: [65, Z(65)],
        northBridge: [28, Z(138)],
        woodedPath: [75, Z(185)],
        centreville: [180, Z(185)],
        centrevilleTrain: [160, Z(165)],
        farEnoughFarm: [295, Z(185)],
        grandFountain: [0, Z(310)],
        avenueGardens: [0, Z(380)],
        westReflectingPool: [-26, Z(380)],
        eastReflectingPool: [26, Z(380)],
        hedgeMaze: [-65, Z(385)], // William Meany Hedge Maze (South Centre Island, West of Avenue)
        centreBeach: [0, Z(455)],
        beachCafe: [34, Z(455)],
        bikeRental: [-34, Z(455)],
        beachLockers: [-10, Z(452)],
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
        formalGarden: [0, Z(380)],
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
})();'''

def main():
    print(f"Writing complete Toronto Islands code to {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, 'w') as f:
        f.write(CODE.strip() + '\n')
    print("Done! File size:", len(CODE), "bytes.")

if __name__ == '__main__':
    main()
