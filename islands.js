/**
 * TORONTO ISLANDS ARCHIPELAGO MINI-WORLD
 * ============================================================================
 * A complete, authentic 3D simulation of the Toronto Islands archipelago:
 *
 * 1. BILLY BISHOP AIRPORT (CYTZ): Runway 08/26, control tower, terminal, Dash-8s, Western Gap
 * 2. HANLAN'S POINT: Ferry terminal, Ned Hanlan memorial, baseball fields, west beach
 * 3. GIBRALTAR POINT: Historic 1808 stone lighthouse, revolving beacon, sand dunes & forest
 * 4. CENTRE ISLAND: Ferry terminal, Avenue of the Island formal flowerbeds, Grand Fountain,
 *    William Meany Hedge Maze, Centreville amusement park (Ferris wheel, carousel, train,
 *    Pizza Pizza), south beach dunes & 120m Lake Ontario pier
 * 5. OLYMPIC ISLAND: Scenic skyline lawns, weeping willows, arched footbridges
 * 6. ALGONQUIN ISLAND: Pedestrian-only cottage community, footbridge, flower gardens
 * 7. WARD'S ISLAND: Historic summer cottages, Ward's Cafe, boardwalk, beach, Eastern Gap
 * 8. PANORAMIC TORONTO SKYLINE: 3D silhouette across the harbour (CN Tower, Rogers Centre,
 *    Financial District towers, Harbourfront)
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

    const Z_BASE = 5000; // Base Z center of the archipelago world

    // --------------------------------------------------------------------------
    // Materials
    // --------------------------------------------------------------------------
    const turfMat = new THREE.MeshStandardMaterial({ color: 0x1e6f3d, roughness: 0.85, metalness: 0.05 });
    const lawnMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.8, metalness: 0.05 });
    const sandMat = new THREE.MeshStandardMaterial({ color: 0xecd08c, roughness: 0.95 });
    const waterMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.2, metalness: 0.45, opacity: 0.88, transparent: true });
    const lagoonMat = new THREE.MeshStandardMaterial({ color: 0x0e7490, roughness: 0.25, metalness: 0.35, opacity: 0.92, transparent: true });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.75, metalness: 0.1 });
    const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.8 });
    const pathMat = new THREE.MeshStandardMaterial({ color: 0x9ca3af, roughness: 0.9 });
    const dirtMat = new THREE.MeshBasicMaterial({ color: 0x6e4727, fog: false });
    const hedgeMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.9 });
    const stoneMat = new THREE.MeshStandardMaterial({ color: 0xd6d3d1, roughness: 0.75 });
    const concreteMat = new THREE.MeshStandardMaterial({ color: 0xa8a29e, roughness: 0.85 });
    const asphaltMat = new THREE.MeshStandardMaterial({ color: 0x27272a, roughness: 0.9 });
    const whiteMarkMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, fog: false });
    const yellowMarkMat = new THREE.MeshBasicMaterial({ color: 0xfacc15, fog: false });
    const barkMat = new THREE.MeshStandardMaterial({ color: 0x3d2817, roughness: 0.9 });
    const leafDarkMat = new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 0.85 });
    const leafWillowMat = new THREE.MeshStandardMaterial({ color: 0x4ade80, roughness: 0.85 });
    const leafAutumnMat = new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.85 });
    const pineMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.9 });
    const metalMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.3, metalness: 0.8 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, metalness: 0.9, opacity: 0.65, transparent: true });
    const lightGlowMat = new THREE.MeshBasicMaterial({ color: 0xfef08a, fog: false });
    const beaconMat = new THREE.MeshBasicMaterial({ color: 0xfffbeb, fog: false });

    // Animated objects registry
    const animators = [];

    // --------------------------------------------------------------------------
    // Helper: Canvas Sign Texture Generator
    // --------------------------------------------------------------------------
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
      const count = lines.length;
      lines.forEach((txt, idx) => {
        const py = (can.height / (count + 1)) * (idx + 1);
        g.font = idx === 0 ? 'bold ' + (o.titleSize || 46) + 'px sans-serif' : 'bold ' + (o.subSize || 28) + 'px sans-serif';
        g.fillStyle = idx === 0 ? (o.fg || '#ffffff') : (o.subFg || '#94a3b8');
        g.fillText(txt, can.width / 2, py);
      });
      const tex = new THREE.CanvasTexture(can);
      const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide, fog: false })
      );
      return mesh;
    }

    // --------------------------------------------------------------------------
    // Water Surfaces (Lake Ontario South, Inner Harbour North, Protected Lagoons)
    // --------------------------------------------------------------------------
    // Giant Lake Ontario water expanse
    const lakePlane = new THREE.Mesh(new THREE.PlaneGeometry(3600, 2200), waterMat);
    lakePlane.rotation.x = -Math.PI / 2;
    lakePlane.position.set(0, -0.3, Z_BASE);
    islandsGroup.add(lakePlane);

    // Inner Harbour calm surface
    const harbourPlane = new THREE.Mesh(new THREE.PlaneGeometry(3400, 1200), waterMat);
    harbourPlane.rotation.x = -Math.PI / 2;
    harbourPlane.position.set(0, -0.28, Z_BASE - 600);
    islandsGroup.add(harbourPlane);

    // --------------------------------------------------------------------------
    // Island Landmasses
    // --------------------------------------------------------------------------
    const islandMeshes = new THREE.Group();

    function addLandmass(cx, cz, w, d, mat, shape) {
      let geo;
      if (shape === 'rounded') {
        geo = new THREE.CylinderGeometry(1, 1, 0.6, 32);
      } else {
        geo = new THREE.BoxGeometry(1, 0.6, 1);
      }
      const m = new THREE.Mesh(geo, mat || turfMat);
      m.scale.set(w, 1, d);
      m.position.set(cx, 0.25, cz);
      m.receiveShadow = true;
      islandMeshes.add(m);
      return m;
    }

    // 1. CENTRE ISLAND (Main Spine: Docks, Avenue, Gardens, Hedge Maze, Centreville)
    addLandmass(0, Z_BASE + 200, 520, 380, turfMat, 'rounded');
    addLandmass(80, Z_BASE + 180, 420, 320, turfMat, 'rounded');
    // South Beach Dune Ridge
    addLandmass(20, Z_BASE + 450, 480, 110, sandMat, 'rounded');
    // Centre Island 120m Lake Ontario Pier
    const pier = new THREE.Mesh(new THREE.BoxGeometry(12, 0.8, 120), woodMat);
    pier.position.set(0, 0.4, Z_BASE + 530);
    islandMeshes.add(pier);

    // 2. OLYMPIC ISLAND (South-Central Skyline Lawn)
    addLandmass(-160, Z_BASE + 330, 280, 200, lawnMat, 'rounded');

    // 3. GIBRALTAR POINT (Historic Lighthouse Peninsula & Nature Reserve)
    addLandmass(-460, Z_BASE + 330, 360, 260, turfMat, 'rounded');
    addLandmass(-480, Z_BASE + 440, 320, 90, sandMat, 'rounded');

    // 4. HANLAN'S POINT (Western Ferry Terminal, Memorial & Park)
    addLandmass(-740, Z_BASE + 20, 380, 480, turfMat, 'rounded');
    addLandmass(-880, Z_BASE + 10, 80, 420, sandMat, 'rounded'); // Hanlan's Beach

    // 5. BILLY BISHOP AIRPORT (CYTZ)
    addLandmass(-1260, Z_BASE - 180, 580, 280, concreteMat, 'box');
    // Main Runway 08/26 (Asphalt strip with markings)
    const runway = new THREE.Mesh(new THREE.BoxGeometry(520, 0.1, 44), asphaltMat);
    runway.position.set(-1260, 0.58, Z_BASE - 170);
    islandMeshes.add(runway);
    // Runway center dashes
    for (let rx = -1230; rx <= -1050; rx += 36) {
      const dash = new THREE.Mesh(new THREE.BoxGeometry(20, 0.12, 2.2), whiteMarkMat);
      dash.position.set(rx, 0.6, Z_BASE - 170);
      islandMeshes.add(dash);
    }
    // Runway threshold stripes (Runway 08 west & Runway 26 east)
    [-1500, -1020].forEach((tx) => {
      for (let s = -16; s <= 16; s += 4) {
        const thr = new THREE.Mesh(new THREE.BoxGeometry(16, 0.12, 1.8), whiteMarkMat);
        thr.position.set(tx, 0.6, Z_BASE - 170 + s);
        islandMeshes.add(thr);
      }
    });

    // 6. ALGONQUIN ISLAND (Residential Cottage Community across Long Pond)
    addLandmass(540, Z_BASE + 80, 320, 260, lawnMat, 'rounded');

    // 7. WARD'S ISLAND (Eastern Summer Village, Cafe & Beach)
    addLandmass(1050, Z_BASE + 20, 440, 280, turfMat, 'rounded');
    addLandmass(1220, Z_BASE + 60, 120, 240, sandMat, 'rounded'); // Ward's Beach
    // Ward's Island Lake Boardwalk
    const wardsBrd = new THREE.Mesh(new THREE.BoxGeometry(180, 0.35, 5), woodMat);
    wardsBrd.position.set(1140, 0.6, Z_BASE + 140);
    islandMeshes.add(wardsBrd);

    islandsGroup.add(islandMeshes);

    // --------------------------------------------------------------------------
    // Walkable Bridges & Arch Elevated Footways
    // --------------------------------------------------------------------------
    const bridges = [
      // 1. Manitou Bridge (Centre Island to Olympic Island across Long Pond)
      { name: 'Manitou Bridge', x0: -20, z0: Z_BASE + 230, x1: 20, z1: Z_BASE + 280, w: 9.0, archH: 2.6, yBase: 0.5 },
      // 2. Olympic to Gibraltar Bridge
      { name: 'Olympic-Gibraltar Bridge', x0: -310, z0: Z_BASE + 290, x1: -270, z1: Z_BASE + 330, w: 6.5, archH: 2.4, yBase: 0.5 },
      // 3. Centreville to Algonquin Island Bridge
      { name: 'Algonquin Bridge', x0: 340, z0: Z_BASE + 65, x1: 390, z1: Z_BASE + 95, w: 7.2, archH: 2.5, yBase: 0.5 },
      // 4. Algonquin to Ward's Island Bridge
      { name: 'Ward-Algonquin Footbridge', x0: 730, z0: Z_BASE + 45, x1: 775, z1: Z_BASE + 75, w: 6.0, archH: 2.2, yBase: 0.5 },
      // 5. Avenue of the Island South Lagoon Bridge (to South Beach)
      { name: 'Avenue Lagoon Bridge', x0: -15, z0: Z_BASE + 330, x1: 15, z1: Z_BASE + 380, w: 10.0, archH: 2.5, yBase: 0.5 },
      // 6. Gibraltar to Hanlan's Point Trail Bridge
      { name: 'Gibraltar-Hanlan Bridge', x0: -610, z0: Z_BASE + 160, x1: -570, z1: Z_BASE + 195, w: 6.5, archH: 2.2, yBase: 0.5 }
    ];

    bridges.forEach(b => {
      const bg = new THREE.Group();
      const segs = 14;
      const dx = (b.x1 - b.x0) / segs;
      const dz = (b.z1 - b.z0) / segs;
      const len = Math.hypot(b.x1 - b.x0, b.z1 - b.z0);
      const rotY = Math.atan2(b.x1 - b.x0, b.z1 - b.z0);

      // Parabolic arch deck planks
      for (let i = 0; i < segs; i++) {
        const t = (i + 0.5) / segs;
        const curY = b.yBase + Math.sin(t * Math.PI) * b.archH;
        const px = b.x0 + dx * i + dx * 0.5;
        const pz = b.z0 + dz * i + dz * 0.5;
        const plank = new THREE.Mesh(new THREE.BoxGeometry(b.w, 0.4, (len / segs) + 0.2), woodMat);
        plank.position.set(px, curY, pz);
        plank.rotation.y = rotY;
        bg.add(plank);

        // Side railings
        [-b.w / 2 + 0.2, b.w / 2 - 0.2].forEach(rx => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.3, 1.1, 0.3), darkWoodMat);
          post.position.set(px + Math.cos(rotY) * rx, curY + 0.6, pz - Math.sin(rotY) * rx);
          bg.add(post);
        });
      }

      // Stone abutments at bridge landings
      [ [b.x0, b.z0], [b.x1, b.z1] ].forEach(([ax, az]) => {
        const abut = new THREE.Mesh(new THREE.BoxGeometry(b.w + 1.2, 1.2, 3.2), stoneMat);
        abut.position.set(ax, b.yBase + 0.2, az);
        abut.rotation.y = rotY;
        bg.add(abut);
      });

      islandsGroup.add(bg);
    });

    // --------------------------------------------------------------------------
    // Landmark 1: Centre Island Ferry Terminal & Docks (x: 0, z: 5000)
    // --------------------------------------------------------------------------
    {
      const termGrp = new THREE.Group();
      // Main boarding pier deck
      const pierDeck = new THREE.Mesh(new THREE.BoxGeometry(32, 0.6, 50), woodMat);
      pierDeck.position.set(0, 0.45, Z_BASE - 10);
      termGrp.add(pierDeck);

      // Gabled Welcome Canopy
      const canopy = new THREE.Mesh(new THREE.BoxGeometry(26, 1.0, 16), darkWoodMat);
      canopy.position.set(0, 4.8, Z_BASE + 6);
      termGrp.add(canopy);
      [-11, 11].forEach(cx => {
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 4.8, 8), darkWoodMat);
        post.position.set(cx, 2.4, Z_BASE + 6);
        termGrp.add(post);
      });

      // Terminal Signs
      const sNorth = makeSign(['CENTRE ISLAND FERRY TERMINAL', 'WELCOME TO TORONTO ISLAND PARK • EST. 1888'], 18, 2.4, { bg: '#064e3b', fg: '#fef08a', borderColor: '#10b981' });
      sNorth.position.set(0, 5.8, Z_BASE + 14);
      termGrp.add(sNorth);

      const sSouth = makeSign(['TORONTO ISLAND FERRIES', 'BOATS TO JACK LAYTON FERRY TERMINAL (CITY)'], 16, 2.0, { bg: '#1e3a8a', fg: '#38bdf8', borderColor: '#0284c7' });
      sSouth.position.set(0, 5.8, Z_BASE - 2);
      sSouth.rotation.y = Math.PI;
      termGrp.add(sSouth);

      islandsGroup.add(termGrp);
    }

    // --------------------------------------------------------------------------
    // Landmark 2: Avenue of the Island Formal Promenade, Gardens & Fountain
    // --------------------------------------------------------------------------
    let fountainSpray = null;
    {
      const avg = new THREE.Group();
      // Wide crushed gravel promenade
      const prom = new THREE.Mesh(new THREE.BoxGeometry(14, 0.15, 220), pathMat);
      prom.position.set(0, 0.58, Z_BASE + 120);
      avg.add(prom);

      // Formal flowerbeds along Avenue of the Island
      const flowerCols = [0xef4444, 0xfacc15, 0xa855f7, 0xf472b6, 0x38bdf8];
      for (let fz = Z_BASE + 30; fz <= Z_BASE + 210; fz += 24) {
        [-9, 9].forEach((fx, fi) => {
          const bed = new THREE.Mesh(new THREE.BoxGeometry(3.5, 0.5, 12), stoneMat);
          bed.position.set(fx, 0.65, fz);
          avg.add(bed);

          const col = flowerCols[(fi + Math.round(fz / 24)) % flowerCols.length];
          const bloomMat = new THREE.MeshBasicMaterial({ color: col, fog: false });
          for (let fl = -4.5; fl <= 4.5; fl += 2.2) {
            const flower = new THREE.Mesh(new THREE.DodecahedronGeometry(0.48), bloomMat);
            flower.position.set(fx, 1.05, fz + fl);
            avg.add(flower);
          }
        });
      }

      // Grand Ornamental 3-Tier Fountain at (0, Z_BASE + 130)
      const fBasin = new THREE.Mesh(new THREE.CylinderGeometry(8.5, 9.0, 1.2, 28), stoneMat);
      fBasin.position.set(0, 0.9, Z_BASE + 130);
      avg.add(fBasin);
      const fWater = new THREE.Mesh(new THREE.CylinderGeometry(7.8, 7.8, 0.2, 28), lagoonMat);
      fWater.position.set(0, 1.4, Z_BASE + 130);
      avg.add(fWater);
      const fTier2 = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.8, 1.4, 20), stoneMat);
      fTier2.position.set(0, 2.0, Z_BASE + 130);
      avg.add(fTier2);
      const fTier3 = new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.4, 1.2, 16), stoneMat);
      fTier3.position.set(0, 3.1, Z_BASE + 130);
      avg.add(fTier3);

      fountainSpray = new THREE.Group();
      const sprayCone = new THREE.Mesh(new THREE.ConeGeometry(1.6, 5.0, 12, 1, true), new THREE.MeshBasicMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.7, side: THREE.DoubleSide }));
      sprayCone.position.set(0, 5.6, Z_BASE + 130);
      fountainSpray.add(sprayCone);
      avg.add(fountainSpray);

      islandsGroup.add(avg);
    }

    // --------------------------------------------------------------------------
    // Landmark 3: William Meany Hedge Maze (x: -115, z: Z_BASE + 145)
    // --------------------------------------------------------------------------
    {
      const hmg = new THREE.Group();
      const hx = -115, hz = Z_BASE + 145;

      // Earthy packed dirt ground inside the maze so green hedges stand out sharply
      const mazeGround = new THREE.Mesh(new THREE.BoxGeometry(78, 0.08, 74), dirtMat);
      mazeGround.position.set(hx, 0.54, hz);
      hmg.add(mazeGround);

      // Entrance Gate Arch
      const mSign = makeSign(['WILLIAM MEANY HEDGE MAZE', 'TORONTO ISLAND PARK • DONATED 2015'], 16, 2.2, { bg: '#14532d', fg: '#bbf7d0', borderColor: '#22c55e' });
      mSign.position.set(hx, 3.8, hz - 36);
      hmg.add(mSign);

      function addMazeWall(wx, wz, ww, wd) {
        const wall = new THREE.Mesh(new THREE.BoxGeometry(ww, 2.2, wd), hedgeMat);
        wall.position.set(hx + wx, 1.6, hz + wz);
        hmg.add(wall);
      }

      // Outer perimeter hedge walls with entrance gap
      addMazeWall(-20, -36, 34, 1.4);
      addMazeWall(20, -36, 34, 1.4);
      addMazeWall(-38, 0, 1.4, 72);
      addMazeWall(38, 0, 1.4, 72);
      addMazeWall(0, 36, 76, 1.4);

      // Inner rings & dead ends
      addMazeWall(-16, -24, 26, 1.2);
      addMazeWall(16, -24, 26, 1.2);
      addMazeWall(-28, 0, 1.2, 48);
      addMazeWall(28, 0, 1.2, 48);
      addMazeWall(0, 24, 56, 1.2);

      addMazeWall(-10, -12, 18, 1.2);
      addMazeWall(10, -12, 18, 1.2);
      addMazeWall(-18, 4, 1.2, 30);
      addMazeWall(18, 4, 1.2, 30);
      addMazeWall(0, 14, 36, 1.2);

      // Central observation lookout tower
      const tower = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.4, 6.4), woodMat);
      tower.position.set(hx, 3.2, hz);
      hmg.add(tower);
      [-2.8, 2.8].forEach(px => {
        [-2.8, 2.8].forEach(pz => {
          const leg = new THREE.Mesh(new THREE.BoxGeometry(0.4, 3.2, 0.4), darkWoodMat);
          leg.position.set(hx + px, 1.6, hz + pz);
          hmg.add(leg);
        });
      });
      const tRoof = new THREE.Mesh(new THREE.ConeGeometry(5.4, 2.2, 4), hedgeMat);
      tRoof.position.set(hx, 4.6, hz);
      tRoof.rotation.y = Math.PI / 4;
      hmg.add(tRoof);

      islandsGroup.add(hmg);
    }

    // --------------------------------------------------------------------------
    // Landmark 4: Centreville Amusement Park (Ferris Wheel, Carousel, Pizza Pizza)
    // --------------------------------------------------------------------------
    let ferrisWheelMesh = null;
    {
      const cvg = new THREE.Group();
      // Giant Rotating Ferris Wheel at (190, Z_BASE + 130)
      const fwGrp = new THREE.Group();
      fwGrp.position.set(190, 14.5, Z_BASE + 130);

      // A-frame steel support legs
      [-4.5, 4.5].forEach(lx => {
        const leg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 15.5, 8), metalMat);
        leg1.position.set(190 + lx, 7.5, Z_BASE + 125);
        leg1.rotation.x = -0.35;
        cvg.add(leg1);
        const leg2 = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.45, 15.5, 8), metalMat);
        leg2.position.set(190 + lx, 7.5, Z_BASE + 135);
        leg2.rotation.x = 0.35;
        cvg.add(leg2);
      });

      // Rotating Wheel Assembly
      ferrisWheelMesh = new THREE.Group();
      const hub = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 3.2, 16), metalMat);
      hub.rotation.z = Math.PI / 2;
      ferrisWheelMesh.add(hub);

      // 16 radial spokes and gondolas
      const spokeCount = 16;
      const wheelRadius = 12.0;
      const gondolaCols = [0xef4444, 0xfacc15, 0x3b82f6, 0x10b981];
      for (let si = 0; si < spokeCount; si++) {
        const ang = (si / spokeCount) * Math.PI * 2;
        const spoke = new THREE.Mesh(new THREE.BoxGeometry(wheelRadius * 2, 0.15, 0.15), metalMat);
        spoke.rotation.z = ang;
        ferrisWheelMesh.add(spoke);

        // Passenger Gondola
        const gCol = gondolaCols[si % gondolaCols.length];
        const gondola = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.5, 1.6), new THREE.MeshStandardMaterial({ color: gCol, roughness: 0.5 }));
        gondola.position.set(Math.cos(ang) * wheelRadius, Math.sin(ang) * wheelRadius, 0);
        ferrisWheelMesh.add(gondola);
      }
      fwGrp.add(ferrisWheelMesh);
      cvg.add(fwGrp);

      // Vintage Wooden Carousel at (140, Z_BASE + 180)
      const carBase = new THREE.Mesh(new THREE.CylinderGeometry(9.0, 9.5, 1.0, 24), woodMat);
      carBase.position.set(140, 1.0, Z_BASE + 180);
      cvg.add(carBase);
      const carRoof = new THREE.Mesh(new THREE.ConeGeometry(9.5, 3.5, 24), new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.5 }));
      carRoof.position.set(140, 4.8, Z_BASE + 180);
      cvg.add(carRoof);

      // PIZZA PIZZA CONCESSIONS & DINING PATIO at (170, Z_BASE + 230)
      const ppBuilding = new THREE.Mesh(new THREE.BoxGeometry(22, 4.5, 14), new THREE.MeshStandardMaterial({ color: 0xf97316, roughness: 0.5 }));
      ppBuilding.position.set(170, 2.75, Z_BASE + 230);
      cvg.add(ppBuilding);

      const ppRoofTrim = new THREE.Mesh(new THREE.BoxGeometry(22.8, 0.8, 14.8), new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5 }));
      ppRoofTrim.position.set(170, 5.2, Z_BASE + 230);
      cvg.add(ppRoofTrim);

      const ppSign = makeSign(['PIZZA PIZZA', 'CENTREVILLE FOOD COURT • FRESH SLICES & COMBOS'], 18, 2.2, { bg: '#c2410c', fg: '#ffedd5', borderColor: '#f97316' });
      ppSign.position.set(170, 5.8, Z_BASE + 222.8);
      cvg.add(ppSign);

      // Outdoor dining patio & umbrellas
      const patio = new THREE.Mesh(new THREE.BoxGeometry(28, 0.15, 18), pathMat);
      patio.position.set(170, 0.58, Z_BASE + 212);
      cvg.add(patio);

      [-8, 0, 8].forEach(ux => {
        [-5, 5].forEach(uz => {
          const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.8, 8), metalMat);
          pole.position.set(170 + ux, 1.9, Z_BASE + 212 + uz);
          cvg.add(pole);
          const umbrella = new THREE.Mesh(new THREE.ConeGeometry(2.2, 0.8, 12), new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.45 }));
          umbrella.position.set(170 + ux, 3.2, Z_BASE + 212 + uz);
          cvg.add(umbrella);
          const table = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.8, 12), woodMat);
          table.position.set(170 + ux, 0.9, Z_BASE + 212 + uz);
          cvg.add(table);
        });
      });

      islandsGroup.add(cvg);
    }

    // --------------------------------------------------------------------------
    // Landmark 5: Gibraltar Point 1808 Historic Stone Lighthouse (-480, Z_BASE + 320)
    // --------------------------------------------------------------------------
    let lighthouseBeacon = null;
    {
      const lhg = new THREE.Group();
      const lx = -480, lz = Z_BASE + 320;

      // Hexagonal tapered limestone tower (25m tall)
      const tower = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 4.2, 24, 6), stoneMat);
      tower.position.set(lx, 12.5, lz);
      lhg.add(tower);

      // Upper lantern gallery deck
      const gallery = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.2, 0.8, 12), darkWoodMat);
      gallery.position.set(lx, 24.8, lz);
      lhg.add(gallery);

      // Glass lantern room
      const lantern = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 2.6, 12), glassMat);
      lantern.position.set(lx, 26.2, lz);
      lhg.add(lantern);

      // Conical copper roof & weather vane
      const copperRoof = new THREE.Mesh(new THREE.ConeGeometry(2.8, 2.4, 12), new THREE.MeshStandardMaterial({ color: 0x059669, roughness: 0.4, metalness: 0.7 }));
      copperRoof.position.set(lx, 28.4, lz);
      lhg.add(copperRoof);

      // Revolving beacon light beam
      lighthouseBeacon = new THREE.Group();
      const beam = new THREE.Mesh(
        new THREE.ConeGeometry(12, 180, 16, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xfef08a, transparent: true, opacity: 0.28, side: THREE.DoubleSide })
      );
      beam.rotation.x = Math.PI / 2;
      beam.position.z = 90;
      lighthouseBeacon.add(beam);
      lighthouseBeacon.position.set(lx, 26.2, lz);
      lhg.add(lighthouseBeacon);

      // Historic plaque sign
      const lhSign = makeSign(['GIBRALTAR POINT LIGHTHOUSE', 'TORONTO\'S OLDEST LANDMARK • BUILT 1808 • HISTORIC KEEPER J.P. RADELMÜLLER'], 18, 2.4, { bg: '#1c1917', fg: '#fde047', borderColor: '#d97706' });
      lhSign.position.set(lx, 2.2, lz + 8);
      lhg.add(lhSign);

      islandsGroup.add(lhg);
    }

    // --------------------------------------------------------------------------
    // Landmark 6: Billy Bishop Toronto City Airport (CYTZ) (-1260, Z_BASE - 180)
    // --------------------------------------------------------------------------
    let radarDish = null;
    {
      const apg = new THREE.Group();
      const ax = -1060, az = Z_BASE - 230;

      // Modern glass & white steel passenger terminal
      const term = new THREE.Mesh(new THREE.BoxGeometry(72, 8.5, 36), concreteMat);
      term.position.set(ax, 4.75, az);
      apg.add(term);

      const glassFacade = new THREE.Mesh(new THREE.BoxGeometry(72.4, 4.5, 1.0), glassMat);
      glassFacade.position.set(ax, 5.0, az + 18.2);
      apg.add(glassFacade);

      const apSign = makeSign(['BILLY BISHOP TORONTO CITY AIRPORT (CYTZ)', 'ISLAND TERMINAL • WESTERN GAP • PORTER AIRLINES GATEWAY'], 24, 2.4, { bg: '#0f172a', fg: '#38bdf8', borderColor: '#0284c7' });
      apSign.position.set(ax, 9.8, az + 18.5);
      apg.add(apSign);

      // Air Traffic Control Tower with rotating radar
      const towerShaft = new THREE.Mesh(new THREE.CylinderGeometry(2.4, 3.2, 28, 12), concreteMat);
      towerShaft.position.set(ax + 48, 14.5, az);
      apg.add(towerShaft);

      const cab = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 3.6, 4.5, 12), glassMat);
      cab.position.set(ax + 48, 29.5, az);
      apg.add(cab);

      radarDish = new THREE.Group();
      const dish = new THREE.Mesh(new THREE.BoxGeometry(3.8, 1.2, 0.4), metalMat);
      radarDish.add(dish);
      radarDish.position.set(ax + 48, 32.5, az);
      apg.add(radarDish);

      // 2 Dash-8 Q400 Turboprop Airplanes on Apron
      function addAirplane(px, pz, rotY) {
        const pl = new THREE.Group();
        // Fuselage
        const fuse = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 26, 12), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 }));
        fuse.rotation.x = Math.PI / 2;
        pl.add(fuse);
        // Wings
        const wings = new THREE.Mesh(new THREE.BoxGeometry(28, 0.3, 3.5), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 }));
        wings.position.set(0, 0.8, -2);
        pl.add(wings);
        // T-Tail
        const fin = new THREE.Mesh(new THREE.BoxGeometry(0.3, 4.5, 3.0), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 }));
        fin.position.set(0, 3.2, 11);
        pl.add(fin);
        const tTail = new THREE.Mesh(new THREE.BoxGeometry(8, 0.25, 2.0), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 }));
        tTail.position.set(0, 5.4, 11);
        pl.add(tTail);

        pl.position.set(px, 2.2, pz);
        pl.rotation.y = rotY;
        apg.add(pl);
      }
      addAirplane(ax - 28, az + 45, 0.3);
      addAirplane(ax + 24, az + 55, -0.2);

      islandsGroup.add(apg);
    }

    // --------------------------------------------------------------------------
    // Landmark 7: Algonquin & Ward's Island Summer Cottages & Cafe
    // --------------------------------------------------------------------------
    {
      const cottGrp = new THREE.Group();
      const pastelCols = [0xbfdbfe, 0xbbf7d0, 0xfef08a, 0xfbcfe8, 0xe9d5ff, 0xfed7aa];

      function addCottage(cx, cz, rotY, col) {
        const c = new THREE.Group();
        // Wooden cottage walls
        const bldg = new THREE.Mesh(new THREE.BoxGeometry(8.5, 3.4, 7.0), new THREE.MeshStandardMaterial({ color: col, roughness: 0.7 }));
        bldg.position.y = 1.7;
        c.add(bldg);
        // Pitched roof
        const roof = new THREE.Mesh(new THREE.ConeGeometry(7.2, 2.6, 4), darkWoodMat);
        roof.position.y = 4.4;
        roof.rotation.y = Math.PI / 4;
        c.add(roof);
        // Front porch & railing
        const porch = new THREE.Mesh(new THREE.BoxGeometry(7.5, 0.3, 2.2), woodMat);
        porch.position.set(0, 0.2, 4.2);
        c.add(porch);

        c.position.set(cx, 0.55, cz);
        c.rotation.y = rotY;
        cottGrp.add(c);
      }

      // Algonquin Island Cottages
      for (let i = 0; i < 8; i++) {
        const ax = 440 + (i % 4) * 36;
        const az = Z_BASE + 40 + Math.floor(i / 4) * 44;
        addCottage(ax, az, (i % 3) * 0.4, pastelCols[i % pastelCols.length]);
      }

      // Ward's Island Cottages & Lanes
      for (let i = 0; i < 12; i++) {
        const wx = 920 + (i % 6) * 38;
        const wz = Z_BASE - 20 + Math.floor(i / 6) * 40;
        addCottage(wx, wz, (i % 2) * 0.35, pastelCols[(i + 2) % pastelCols.length]);
      }

      // Ward's Island Cafe & The Rectory Patio at (1050, Z_BASE + 70)
      const cafe = new THREE.Mesh(new THREE.BoxGeometry(18, 4.2, 12), new THREE.MeshStandardMaterial({ color: 0xfef3c7, roughness: 0.6 }));
      cafe.position.set(1050, 2.65, Z_BASE + 70);
      cottGrp.add(cafe);
      const cafeSign = makeSign(['WARD\'S ISLAND CAFE & DINING', 'GARDEN PATIO • FRESH BAKERY • THE RECTORY CAFE'], 16, 2.0, { bg: '#047857', fg: '#fef08a', borderColor: '#10b981' });
      cafeSign.position.set(1050, 5.2, Z_BASE + 63.8);
      cottGrp.add(cafeSign);

      islandsGroup.add(cottGrp);
    }

    // --------------------------------------------------------------------------
    // Landmark 8: Hanlan's Point Ferry Terminal & Ned Hanlan Memorial Plaza
    // --------------------------------------------------------------------------
    {
      const hpg = new THREE.Group();
      const hx = -720, hz = Z_BASE - 120;
      const hpPier = new THREE.Mesh(new THREE.BoxGeometry(24, 0.6, 42), woodMat);
      hpPier.position.set(hx, 0.45, hz);
      hpg.add(hpPier);

      const hpSign = makeSign(['HANLAN\'S POINT FERRY TERMINAL', 'BOATS TO MAINLAND BATHURST QUAY & WEST HARBOUR'], 18, 2.2, { bg: '#1e3a8a', fg: '#38bdf8', borderColor: '#0284c7' });
      hpSign.position.set(hx, 4.2, hz + 12);
      hpg.add(hpSign);

      // Historic Ned Hanlan Statue (Bronze rower sculpture on stone plinth)
      const plinth = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.8, 3.2), stoneMat);
      plinth.position.set(hx + 35, 1.4, hz + 35);
      hpg.add(plinth);
      const statue = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 2.4, 8), new THREE.MeshStandardMaterial({ color: 0x78350f, metalness: 0.8, roughness: 0.3 }));
      statue.position.set(hx + 35, 3.4, hz + 35);
      hpg.add(statue);

      islandsGroup.add(hpg);
    }

    // --------------------------------------------------------------------------
    // Ancient Toronto Island Urban Forest & Canopy Trees
    // --------------------------------------------------------------------------
    {
      const treeGrp = new THREE.Group();
      function addTree(tx, tz, kind) {
        const tg = new THREE.Group();
        if (kind === 'willow') {
          // Weeping Willow along lagoon banks
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.6, 5.5, 8), barkMat);
          trunk.position.y = 2.75;
          tg.add(trunk);
          const crown = new THREE.Mesh(new THREE.ConeGeometry(4.2, 7.5, 8), leafWillowMat);
          crown.position.y = 6.8;
          tg.add(crown);
        } else if (kind === 'pine') {
          // Evergreen pine on dunes
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.45, 6.0, 6), barkMat);
          trunk.position.y = 3.0;
          tg.add(trunk);
          const crown = new THREE.Mesh(new THREE.ConeGeometry(3.2, 8.5, 6), pineMat);
          crown.position.y = 7.5;
          tg.add(crown);
        } else {
          // Giant Eastern Cottonwood / Sugar Maple
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.8, 7.5, 8), barkMat);
          trunk.position.y = 3.75;
          tg.add(trunk);
          const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(5.2, 1), leafDarkMat);
          crown.position.y = 9.5;
          tg.add(crown);
        }
        tg.position.set(tx, 0.5, tz);
        treeGrp.add(tg);
      }

      // Scatter natural groves across all islands
      const treeSpots = [
        [-50, Z_BASE + 80, 'cottonwood'], [60, Z_BASE + 70, 'cottonwood'],
        [-80, Z_BASE + 220, 'willow'], [-140, Z_BASE + 260, 'willow'],
        [-220, Z_BASE + 310, 'cottonwood'], [-260, Z_BASE + 360, 'cottonwood'],
        [-380, Z_BASE + 320, 'willow'], [-420, Z_BASE + 280, 'pine'],
        [-520, Z_BASE + 360, 'pine'], [-580, Z_BASE + 310, 'pine'],
        [-700, Z_BASE + 180, 'cottonwood'], [-780, Z_BASE + 140, 'cottonwood'],
        [280, Z_BASE + 120, 'cottonwood'], [320, Z_BASE + 160, 'willow'],
        [460, Z_BASE + 80, 'cottonwood'], [620, Z_BASE + 70, 'willow'],
        [820, Z_BASE + 50, 'cottonwood'], [980, Z_BASE + 60, 'willow'],
        [1180, Z_BASE + 80, 'willow'], [1280, Z_BASE + 40, 'pine']
      ];
      treeSpots.forEach(([tx, tz, kind]) => addTree(tx, tz, kind));

      islandsGroup.add(treeGrp);
    }

    // --------------------------------------------------------------------------
    // Distant 3D Panoramic Toronto Skyline Across the Harbour (z = 4100)
    // --------------------------------------------------------------------------
    {
      const skyGrp = new THREE.Group();
      const skyZ = Z_BASE - 900; // 900m north across the harbour

      // CN Tower (553m landmark)
      const cnTower = new THREE.Group();
      const shaft = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 9.0, 340, 16), concreteMat);
      shaft.position.y = 170;
      cnTower.add(shaft);
      const skyPod = new THREE.Mesh(new THREE.CylinderGeometry(14, 18, 22, 16), concreteMat);
      skyPod.position.y = 345;
      cnTower.add(skyPod);
      const ring = new THREE.Mesh(new THREE.CylinderGeometry(19, 19, 4, 16), lightGlowMat);
      ring.position.y = 352;
      cnTower.add(ring);
      const needle = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 3.5, 120, 8), metalMat);
      needle.position.y = 420;
      cnTower.add(needle);
      const redBeacon = new THREE.Mesh(new THREE.SphereGeometry(1.5, 8, 8), new THREE.MeshBasicMaterial({ color: 0xef4444, fog: false }));
      redBeacon.position.y = 482;
      cnTower.add(redBeacon);
      cnTower.position.set(-280, 0, skyZ);
      skyGrp.add(cnTower);

      // Rogers Centre Dome
      const rogersDome = new THREE.Mesh(new THREE.SphereGeometry(44, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.48), concreteMat);
      rogersDome.position.set(-440, 22, skyZ + 40);
      skyGrp.add(rogersDome);

      // Financial District Skyscrapers (First Canadian Place, Scotia Plaza, TD Centre)
      function addTowers(tx, tw, th, td, col) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(tw, th, td), new THREE.MeshStandardMaterial({ color: col, roughness: 0.3, metalness: 0.7 }));
        b.position.set(tx, th / 2, skyZ);
        skyGrp.add(b);
      }
      addTowers(100, 36, 298, 36, 0xf8fafc); // First Canadian Place (white marble)
      addTowers(180, 32, 275, 32, 0x991b1b); // Scotia Plaza (red granite)
      addTowers(-40, 42, 222, 42, 0x18181b); // TD Centre (black Mies tower)
      addTowers(280, 34, 260, 34, 0x38bdf8); // Brookfield Place / Bay-Adelaide glass tower
      addTowers(-120, 38, 210, 38, 0x64748b); // Royal Bank Plaza / Metro Hall
      addTowers(420, 48, 140, 38, 0x0284c7); // Waterfront Towers & Westin

      islandsGroup.add(skyGrp);
    }

    scene.add(islandsGroup);

    // --------------------------------------------------------------------------
    // Collision & Walkability API
    // --------------------------------------------------------------------------
    function isInsideIslands(x, z) {
      return z >= Z_BASE - 400 && z <= Z_BASE + 650 && x >= -1650 && x <= 1500;
    }

    function getIslandBridgeAt(x, z) {
      for (let i = 0; i < bridges.length; i++) {
        const b = bridges[i];
        const minX = Math.min(b.x0, b.x1) - b.w / 2;
        const maxX = Math.max(b.x0, b.x1) + b.w / 2;
        const minZ = Math.min(b.z0, b.z1) - 2;
        const maxZ = Math.max(b.z0, b.z1) + 2;
        if (x >= minX && x <= maxX && z >= minZ && z <= maxZ) {
          return b;
        }
      }
      return null;
    }

    function canMoveTo(x, z, radius, y) {
      // 1. Bridges are always walkable at deck height
      const b = getIslandBridgeAt(x, z);
      if (b) return true;

      // 2. Pier and Boardwalks
      if (Math.abs(x) <= 6 && z >= Z_BASE + 450 && z <= Z_BASE + 590) return true; // Centre Pier
      if (x >= 1050 && x <= 1230 && z >= Z_BASE + 135 && z <= Z_BASE + 145) return true; // Ward's Boardwalk
      if (Math.abs(x) <= 16 && z >= Z_BASE - 35 && z <= Z_BASE + 15) return true; // Centre Dock Pier
      if (Math.abs(x - (-720)) <= 12 && z >= Z_BASE - 140 && z <= Z_BASE - 100) return true; // Hanlan's Pier

      // 3. Solid building collisions (Pizza Pizza, Lighthouse, Terminal)
      if (x >= 158 && x <= 182 && z >= Z_BASE + 222 && z <= Z_BASE + 238) return false; // Pizza Pizza walls
      if (Math.hypot(x - (-480), z - (Z_BASE + 320)) < 4.2) return false; // Lighthouse base
      if (x >= -1100 && x <= -1020 && z >= Z_BASE - 250 && z <= Z_BASE - 210) return false; // Airport terminal

      // 4. Landmass checks
      // A. Centre Island
      if (Math.hypot(x, z - (Z_BASE + 200)) <= 250) return true;
      if (Math.hypot(x - 80, z - (Z_BASE + 180)) <= 200) return true;
      if (Math.hypot(x - 20, z - (Z_BASE + 450)) <= 230) return true; // South Beach
      // B. Olympic Island
      if (Math.hypot(x - (-160), z - (Z_BASE + 330)) <= 135) return true;
      // C. Gibraltar Point
      if (Math.hypot(x - (-460), z - (Z_BASE + 330)) <= 170) return true;
      // D. Hanlan's Point
      if (Math.hypot(x - (-740), z - (Z_BASE + 20)) <= 180) return true;
      // E. Billy Bishop Airport
      if (x >= -1560 && x <= -960 && z >= Z_BASE - 320 && z <= Z_BASE - 40) return true;
      // F. Algonquin Island
      if (Math.hypot(x - 540, z - (Z_BASE + 80)) <= 150) return true;
      // G. Ward's Island
      if (Math.hypot(x - 1050, z - (Z_BASE + 20)) <= 210) return true;

      // Everything else is open water: block walking!
      return false;
    }

    function floorAt(x, z, y) {
      // 1. Bridges: arch height
      const b = getIslandBridgeAt(x, z);
      if (b) {
        const len = Math.hypot(b.x1 - b.x0, b.z1 - b.z0) || 1;
        const proj = ((x - b.x0) * (b.x1 - b.x0) + (z - b.z0) * (b.z1 - b.z0)) / (len * len);
        const t = Math.max(0, Math.min(1, proj));
        return b.yBase + Math.sin(t * Math.PI) * b.archH;
      }
      // 2. Piers and Boardwalks
      if (Math.abs(x) <= 6 && z >= Z_BASE + 450 && z <= Z_BASE + 590) return 0.55; // Centre Pier
      if (Math.abs(x) <= 16 && z >= Z_BASE - 35 && z <= Z_BASE + 15) return 0.55; // Centre Dock
      if (Math.abs(x - (-720)) <= 12 && z >= Z_BASE - 140 && z <= Z_BASE - 100) return 0.55; // Hanlan's Dock
      if (x >= 1050 && x <= 1230 && z >= Z_BASE + 135 && z <= Z_BASE + 145) return 0.65; // Ward's Boardwalk
      // 3. Regular Island turf / ground
      return 0.55;
    }

    function getNeighborhood(x, z) {
      if (x <= -960) return "BILLY BISHOP AIRPORT (CYTZ)";
      if (x <= -600 && z <= Z_BASE + 100) return "HANLAN'S POINT • FERRY SLIP";
      if (x <= -600) return "HANLAN'S POINT BEACH • LAKE ONTARIO";
      if (x <= -300 && z >= Z_BASE + 250) return "GIBRALTAR POINT • 1808 LIGHTHOUSE";
      if (x <= -50 && z >= Z_BASE + 240) return "OLYMPIC ISLAND PARK";
      if (z >= Z_BASE + 420) return "CENTRE ISLAND BEACH & LAKE ONTARIO PIER";
      if (x >= 60 && x <= 300 && z >= Z_BASE + 100 && z <= Z_BASE + 250) {
        if (Math.hypot(x - 170, z - (Z_BASE + 230)) < 24) return "PIZZA PIZZA • CENTREVILLE";
        return "CENTREVILLE AMUSEMENT PARK";
      }
      if (x >= -160 && x <= -70 && z >= Z_BASE + 100 && z <= Z_BASE + 190) return "WILLIAM MEANY HEDGE MAZE";
      if (x >= 350 && x <= 750) return "ALGONQUIN ISLAND • COTTAGES";
      if (x >= 750) {
        if (z >= Z_BASE + 50) return "WARD'S ISLAND BEACH & BOARDWALK";
        return "WARD'S ISLAND • SUMMER VILLAGE";
      }
      if (z <= Z_BASE + 20) return "CENTRE ISLAND FERRY TERMINAL";
      return "AVENUE OF THE ISLAND • GARDENS";
    }

    // --------------------------------------------------------------------------
    // Dynamic Updates (Ferris Wheel, Fountain Spray, Beacon, Radar)
    // --------------------------------------------------------------------------
    let tTime = 0;
    function update(dt, playerPos) {
      tTime += dt;
      // 1. Rotate Ferris Wheel
      if (ferrisWheelMesh) {
        ferrisWheelMesh.rotation.z += dt * 0.25;
      }
      // 2. Splashing Fountain Spray
      if (fountainSpray) {
        fountainSpray.scale.y = 0.95 + Math.sin(tTime * 4.5) * 0.12;
      }
      // 3. Revolving Gibraltar Lighthouse Beacon
      if (lighthouseBeacon) {
        lighthouseBeacon.rotation.y += dt * 1.8;
      }
      // 4. Rotating Airport Radar Dish
      if (radarDish) {
        radarDish.rotation.y += dt * 3.2;
      }
    }

    // --------------------------------------------------------------------------
    // Dedicated Toronto Islands GPS Minimap
    // --------------------------------------------------------------------------
    function drawMinimap(ctx, size, playerPos, playerYaw, dots) {
      ctx.clearRect(0, 0, size, size);
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, size, size);

      // Map coordinate transforms
      // X spans: -1600 to +1500 (3100m)
      // Z spans: Z_BASE - 400 to Z_BASE + 600 (1000m)
      const scale = size / 3200;
      const ox = size / 2;
      const oz = size / 2;

      function toMx(wx) { return ox + wx * scale; }
      function toMz(wz) { return oz + (wz - (Z_BASE + 100)) * (scale * 2.6); }

      // Water background (Lake Ontario / Harbour)
      ctx.fillStyle = '#0369a1';
      ctx.fillRect(0, 0, size, size);

      // Draw Landmasses (Green/Sand)
      ctx.fillStyle = '#15803d';
      // Centre Island
      ctx.beginPath(); ctx.ellipse(toMx(0), toMz(Z_BASE + 200), 240 * scale, 160 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();
      // Olympic Island
      ctx.fillStyle = '#16a34a';
      ctx.beginPath(); ctx.ellipse(toMx(-160), toMz(Z_BASE + 330), 130 * scale, 90 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();
      // Gibraltar Point
      ctx.fillStyle = '#15803d';
      ctx.beginPath(); ctx.ellipse(toMx(-460), toMz(Z_BASE + 330), 160 * scale, 110 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();
      // Hanlan's Point
      ctx.beginPath(); ctx.ellipse(toMx(-740), toMz(Z_BASE + 20), 170 * scale, 210 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();
      // Billy Bishop Airport
      ctx.fillStyle = '#475569';
      ctx.fillRect(toMx(-1550), toMz(Z_BASE - 300), 570 * scale, 240 * scale * 2.6);
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(toMx(-1520), toMz(Z_BASE - 190), 500 * scale, 36 * scale * 2.6); // Runway
      // Algonquin Island
      ctx.fillStyle = '#16a34a';
      ctx.beginPath(); ctx.ellipse(toMx(540), toMz(Z_BASE + 80), 150 * scale, 120 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();
      // Ward's Island
      ctx.fillStyle = '#15803d';
      ctx.beginPath(); ctx.ellipse(toMx(1050), toMz(Z_BASE + 20), 190 * scale, 130 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill();

      // Beaches (Golden Sand)
      ctx.fillStyle = '#fde047';
      ctx.beginPath(); ctx.ellipse(toMx(20), toMz(Z_BASE + 450), 220 * scale, 40 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill(); // Centre Beach
      ctx.beginPath(); ctx.ellipse(toMx(1220), toMz(Z_BASE + 60), 50 * scale, 100 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill(); // Ward's Beach
      ctx.beginPath(); ctx.ellipse(toMx(-880), toMz(Z_BASE + 10), 35 * scale, 180 * scale * 2.6, 0, 0, Math.PI * 2); ctx.fill(); // Hanlan's Beach

      // Draw Walkable Bridges (Brown lines)
      ctx.strokeStyle = '#b45309';
      ctx.lineWidth = 2.5;
      bridges.forEach(b => {
        ctx.beginPath();
        ctx.moveTo(toMx(b.x0), toMz(b.z0));
        ctx.lineTo(toMx(b.x1), toMz(b.z1));
        ctx.stroke();
      });

      // Centre Pier
      ctx.fillStyle = '#92400e';
      ctx.fillRect(toMx(-4), toMz(Z_BASE + 450), 8 * scale, 120 * scale * 2.6);

      // Docks & Landmarks (Labels & Icons)
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 8px sans-serif';
      ctx.fillText('🚢 CENTRE DOCK', toMx(0) - 30, toMz(Z_BASE) - 6);
      ctx.fillText('✈️ AIRPORT', toMx(-1320), toMz(Z_BASE - 200));
      ctx.fillText('🗼 1808 LIGHTHOUSE', toMx(-520), toMz(Z_BASE + 330));
      ctx.fillText('🎡 CENTREVILLE', toMx(170), toMz(Z_BASE + 130));
      ctx.fillText('🏡 WARD\'S ISLAND', toMx(980), toMz(Z_BASE + 20));

      // Draw Player arrow
      const px = toMx(playerPos.x);
      const pz = toMz(playerPos.z);
      ctx.save();
      ctx.translate(px, pz);
      ctx.rotate(-playerYaw);
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.moveTo(0, -6);
      ctx.lineTo(4.5, 5);
      ctx.lineTo(0, 3);
      ctx.lineTo(-4.5, 5);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // Outer border
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
        centreDock: [0, Z_BASE],
        avenueGardens: [0, Z_BASE + 130],
        hedgeMaze: [-115, Z_BASE + 145],
        centreville: [190, Z_BASE + 130],
        pizzaPizza: [170, Z_BASE + 230],
        centreBeach: [0, Z_BASE + 450],
        centrePier: [0, Z_BASE + 530],
        olympicIsland: [-160, Z_BASE + 330],
        gibraltarLighthouse: [-480, Z_BASE + 320],
        hanlansDock: [-720, Z_BASE - 120],
        hanlansBeach: [-880, Z_BASE + 10],
        airportRunway: [-1260, Z_BASE - 170],
        airportTerminal: [-1060, Z_BASE - 230],
        algonquinIsland: [540, Z_BASE + 80],
        wardsDock: [1120, Z_BASE - 20],
        wardsBeach: [1220, Z_BASE + 60],
        wardsCafe: [1050, Z_BASE + 70]
      }
    };
  }

  window.buildTorontoIslands = buildTorontoIslands;
})();
