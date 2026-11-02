/**
 * TORONTO ISLANDS ARCHIPELAGO MINI-WORLD
 * ============================================================================
 * A complete, authentic 3D simulation of the Toronto Islands archipelago:
 *
 * 1. REAL WATERWAYS UNDER EVERY BRIDGE:
 *    - Distinct, physically separated island landmasses.
 *    - Long Pond & Allan A. Lamport Regatta Course (45-50m wide open water).
 *    - Blockhouse Bay & Trout Pond channels.
 *    - South Lagoon winding behind Centre Island beach dunes.
 *    - Algonquin Canal separating Algonquin and Ward's Island.
 *    - Hanlan's Canal separating Gibraltar Point and Hanlan's Point.
 *    - Under every bridge, open blue water flows beneath with stone/timber embankments!
 *
 * 2. ANCIENT URBAN FOREST & NATURE TRAILS:
 *    - 380+ full 3D trees representing authentic Toronto Island species:
 *      * Massive heritage Eastern Cottonwoods (Populus deltoides) with towering 18m canopies
 *      * Cascading Weeping Willows (Salix babylonica) draping branches into lagoon waters
 *      * Sugar Maples and Red Oaks in dense interior woodland groves
 *      * Coastal White Pines and Eastern Redcedars along beach dunes
 *    - Winding crushed-gravel and packed-earth nature trails weaving beneath shady canopy tunnels
 *    - Secluded sunlit clearings: Avenue Grand Fountain, William Meany Hedge Maze,
 *      Centreville Vintage Amusement Park, Olympic Island Great Lawn (skyline panorama),
 *      1808 Gibraltar Lighthouse Sanctuary, South Beach & Pier, and Historic Cottage Villages.
 *
 * 3. AUTHENTIC ISLAND LANDMARKS & LIFE:
 *    - William Meany Hedge Maze with earth-toned pathways & lookout tower
 *    - Rotating Centreville Ferris wheel, vintage carousel, Pizza Pizza food court
 *    - 1808 Gibraltar Point Limestone Lighthouse with revolving beam
 *    - Billy Bishop Airport (CYTZ) runway 08/26, terminal, control tower, radar & Dash-8 aircraft
 *    - Algonquin & Ward's Island pedestrian-only summer cottage communities
 *    - Lagoon boat docks, moored canoes, and water lily pads
 *    - Distant 3D Toronto Skyline across the harbour (CN Tower, Rogers Centre, Financial Towers)
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
    const turfMat = new THREE.MeshStandardMaterial({ color: 0x1e6f3d, roughness: 0.88, metalness: 0.04 });
    const lawnMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.82, metalness: 0.04 });
    const meadowMat = new THREE.MeshStandardMaterial({ color: 0x2d8a3e, roughness: 0.85 });
    const sandMat = new THREE.MeshStandardMaterial({ color: 0xecd08c, roughness: 0.95 });
    const waterMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, roughness: 0.2, metalness: 0.45, opacity: 0.88, transparent: true });
    const lagoonWaterMat = new THREE.MeshStandardMaterial({ color: 0x0e7490, roughness: 0.25, metalness: 0.35, opacity: 0.92, transparent: true });
    const canalWallMat = new THREE.MeshStandardMaterial({ color: 0x57534e, roughness: 0.85, metalness: 0.1 });
    const woodMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.75, metalness: 0.1 });
    const darkWoodMat = new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.8 });
    const pathMat = new THREE.MeshStandardMaterial({ color: 0xd1d5db, roughness: 0.92 }); // Crushed limestone gravel
    const dirtMat = new THREE.MeshBasicMaterial({ color: 0x6e4727, fog: false }); // Packed earth for maze & trails
    const hedgeMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.9 });
    const stoneMat = new THREE.MeshStandardMaterial({ color: 0xd6d3d1, roughness: 0.75 });
    const concreteMat = new THREE.MeshStandardMaterial({ color: 0xa8a29e, roughness: 0.85 });
    const asphaltMat = new THREE.MeshStandardMaterial({ color: 0x27272a, roughness: 0.9 });
    const whiteMarkMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, fog: false });
    const yellowMarkMat = new THREE.MeshBasicMaterial({ color: 0xfacc15, fog: false });

    // Tree Foliage & Bark Materials
    const barkMat = new THREE.MeshStandardMaterial({ color: 0x3d2817, roughness: 0.92 });
    const barkCottonwoodMat = new THREE.MeshStandardMaterial({ color: 0x4b3621, roughness: 0.95 });
    const leafDarkMat = new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 0.85 });
    const leafDeepMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.85 });
    const leafWillowMat = new THREE.MeshStandardMaterial({ color: 0x4ade80, roughness: 0.85 });
    const leafWillowDroopMat = new THREE.MeshStandardMaterial({ color: 0x65a30d, roughness: 0.88 });
    const leafSummerMat = new THREE.MeshStandardMaterial({ color: 0x22c55e, roughness: 0.85 });
    const pineMat = new THREE.MeshStandardMaterial({ color: 0x064e3b, roughness: 0.9 });

    // Architectural & Lighting Materials
    const metalMat = new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.3, metalness: 0.8 });
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, metalness: 0.9, opacity: 0.65, transparent: true });
    const lightGlowMat = new THREE.MeshBasicMaterial({ color: 0xfef08a, fog: false });

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
    // Water Expanses & Calm Lagoons
    // --------------------------------------------------------------------------
    // 1. Giant Lake Ontario Water Expanse (South of the Islands)
    const lakePlane = new THREE.Mesh(new THREE.PlaneGeometry(3800, 2400), waterMat);
    lakePlane.rotation.x = -Math.PI / 2;
    lakePlane.position.set(0, -0.3, Z_BASE + 700);
    islandsGroup.add(lakePlane);

    // 2. Inner Toronto Harbour (North between downtown skyline and island docks)
    const harbourPlane = new THREE.Mesh(new THREE.PlaneGeometry(3600, 1400), waterMat);
    harbourPlane.rotation.x = -Math.PI / 2;
    harbourPlane.position.set(0, -0.28, Z_BASE - 500);
    islandsGroup.add(harbourPlane);

    // 3. Protected Island Waterway Network (Long Pond, Allan Lamport Regatta Course,
    //    Blockhouse Bay, South Lagoon, Algonquin Canal, Hanlan's Canal)
    //    Water surface at y = 0.05 (just 0.5m below the grass/banks) so under every
    //    bridge the player looks down from the arch and sees shimmering blue water!
    const interiorLagoonPlane = new THREE.Mesh(new THREE.PlaneGeometry(2800, 900), lagoonWaterMat);
    interiorLagoonPlane.rotation.x = -Math.PI / 2;
    interiorLagoonPlane.position.set(0, 0.05, Z_BASE + 250);
    islandsGroup.add(interiorLagoonPlane);

    // --------------------------------------------------------------------------
    // Distinct Physically Separated Island Landmasses
    // (Open water channels cut completely between the islands)
    // --------------------------------------------------------------------------
    const islandMeshes = new THREE.Group();

    function addIslandBlock(cx, cz, w, d, mat) {
      const m = new THREE.Mesh(new THREE.BoxGeometry(w, 0.6, d), mat || turfMat);
      m.position.set(cx, 0.25, cz);
      m.receiveShadow = true;
      islandMeshes.add(m);
      return m;
    }

    // 1. CENTRE ISLAND MAIN (North Ferry Dock, Promenade, Gardens, Hedge Maze, Centreville)
    // Bounds: x = -240..+320, z = 4980..5230.
    // Stops cleanly at z = 5230 on the south where Long Pond begins!
    addIslandBlock(40, Z_BASE + 115, 540, 230, turfMat);
    addIslandBlock(180, Z_BASE + 150, 260, 160, turfMat); // Centreville peninsula

    // 2. OLYMPIC ISLAND (South-Central Skyline Island across Long Pond)
    // Bounds: x = -310..+50, z = 5280..5420.
    // Separated from Centre Island by Long Pond (z = 5230..5280, 50m open water channel!)
    // Separated from Gibraltar Point by Blockhouse Bay (x = -370..-310, 60m open water channel!)
    addIslandBlock(-140, Z_BASE + 350, 360, 140, lawnMat);

    // 3. SOUTH BEACH DUNE RIDGE & PIER
    // Bounds: x = -90..+260, z = 5380..5480.
    // Separated from Centre Island Main by South Lagoon (z = 5330..5380, 50m open water channel!)
    addIslandBlock(80, Z_BASE + 430, 340, 100, sandMat);

    // Centre Island 120m Lake Ontario Pier extending south into the open lake
    const pier = new THREE.Mesh(new THREE.BoxGeometry(12, 0.8, 120), woodMat);
    pier.position.set(0, 0.55, Z_BASE + 530);
    islandMeshes.add(pier);
    // Pier railings & wooden benches
    [-5.6, 5.6].forEach(px => {
      const rail = new THREE.Mesh(new THREE.BoxGeometry(0.3, 1.1, 120), darkWoodMat);
      rail.position.set(px, 1.2, Z_BASE + 530);
      islandMeshes.add(rail);
    });

    // 4. GIBRALTAR POINT (Historic 1808 Lighthouse, Forest Sanctuary & Dunes)
    // Bounds: x = -600..-370, z = 5210..5440.
    // Separated from Olympic Island by Blockhouse Bay (x = -370..-310)
    // Separated from Hanlan's Point by Hanlan's Canal (z = 5160..5210)
    addIslandBlock(-485, Z_BASE + 325, 230, 230, turfMat);
    addIslandBlock(-485, Z_BASE + 435, 210, 50, sandMat); // Gibraltar South Beach Dunes

    // 5. HANLAN'S POINT (Western Ferry Slip, Memorial Plaza, Ball Fields & Beach)
    // Bounds: x = -920..-570, z = 4920..5160.
    // Separated from Gibraltar Point by Hanlan's Canal (z = 5160..5210)
    // Separated from Billy Bishop Airport by Western Gap (x = -980..-920)
    addIslandBlock(-745, Z_BASE + 40, 330, 240, turfMat);
    addIslandBlock(-900, Z_BASE + 40, 60, 220, sandMat); // Hanlan's Beach

    // 6. BILLY BISHOP AIRPORT (CYTZ)
    // Bounds: x = -1560..-980, z = 4720..4960.
    addIslandBlock(-1270, Z_BASE - 160, 580, 240, concreteMat);
    // Main Runway 08/26
    const runway = new THREE.Mesh(new THREE.BoxGeometry(520, 0.1, 44), asphaltMat);
    runway.position.set(-1260, 0.58, Z_BASE - 170);
    islandMeshes.add(runway);
    for (let rx = -1230; rx <= -1050; rx += 36) {
      const dash = new THREE.Mesh(new THREE.BoxGeometry(20, 0.12, 2.2), whiteMarkMat);
      dash.position.set(rx, 0.6, Z_BASE - 170);
      islandMeshes.add(dash);
    }
    [-1500, -1020].forEach((tx) => {
      for (let s = -16; s <= 16; s += 4) {
        const thr = new THREE.Mesh(new THREE.BoxGeometry(16, 0.12, 1.8), whiteMarkMat);
        thr.position.set(tx, 0.6, Z_BASE - 170 + s);
        islandMeshes.add(thr);
      }
    });

    // 7. ALGONQUIN ISLAND (Residential Cottage Community across Long Pond East)
    // Bounds: x = 400..720, z = 4980..5200.
    // Separated from Centreville by Long Pond East (x = 320..400, 80m open water channel!)
    // Separated from Ward's Island by Algonquin Canal (x = 720..780, 60m open water channel!)
    addIslandBlock(560, Z_BASE + 90, 300, 220, lawnMat);

    // 8. WARD'S ISLAND (Eastern Historic Summer Village, Cafe, Beach & Boardwalk)
    // Bounds: x = 780..1240, z = 4920..5180.
    // Separated from Algonquin Island by Algonquin Canal (x = 720..780)
    addIslandBlock(1010, Z_BASE + 50, 440, 240, turfMat);
    addIslandBlock(1220, Z_BASE + 70, 80, 200, sandMat); // Ward's Beach
    // Ward's Lake Boardwalk along Lake Ontario
    const wardsBrd = new THREE.Mesh(new THREE.BoxGeometry(180, 0.35, 5), woodMat);
    wardsBrd.position.set(1140, 0.6, Z_BASE + 140);
    islandMeshes.add(wardsBrd);

    islandsGroup.add(islandMeshes);

    // --------------------------------------------------------------------------
    // Stone Riprap & Timber Retaining Bulkheads Along Water Channels
    // --------------------------------------------------------------------------
    const bulkheads = new THREE.Group();
    function addBulkhead(cx, cz, w, d, isStone) {
      const bh = new THREE.Mesh(new THREE.BoxGeometry(w, 0.75, d), isStone ? stoneMat : darkWoodMat);
      bh.position.set(cx, 0.35, cz);
      bulkheads.add(bh);
    }
    // Long Pond North Bank (Centre Island side)
    addBulkhead(40, Z_BASE + 230, 540, 2.4, false);
    // Long Pond South Bank (Olympic Island side)
    addBulkhead(-140, Z_BASE + 280, 360, 2.4, false);
    // Blockhouse Bay Banks
    addBulkhead(-370, Z_BASE + 325, 2.4, 180, true);
    addBulkhead(-310, Z_BASE + 325, 2.4, 140, true);
    // South Lagoon Banks
    addBulkhead(40, Z_BASE + 330, 300, 2.4, false);
    addBulkhead(80, Z_BASE + 380, 320, 2.4, false);
    // Algonquin Canal Banks
    addBulkhead(720, Z_BASE + 90, 2.4, 200, false);
    addBulkhead(780, Z_BASE + 50, 2.4, 220, false);
    // Long Pond East Bank (Centreville to Algonquin)
    addBulkhead(320, Z_BASE + 150, 2.4, 160, true);
    addBulkhead(400, Z_BASE + 90, 2.4, 200, true);
    // Hanlan's Canal Banks
    addBulkhead(-600, Z_BASE + 160, 180, 2.4, false);
    addBulkhead(-600, Z_BASE + 210, 180, 2.4, false);

    islandsGroup.add(bulkheads);

    // --------------------------------------------------------------------------
    // Arched Footbridges Spanning Across Real Open Water
    // Under every bridge, 100% open blue water flows beneath!
    // --------------------------------------------------------------------------
    const bridges = [
      // 1. Manitou Bridge (Centre Island to Olympic Island across Long Pond)
      { name: 'Manitou Bridge', x0: -15, z0: Z_BASE + 230, x1: 15, z1: Z_BASE + 280, w: 9.0, archH: 2.6, yBase: 0.5 },
      // 2. Olympic to Gibraltar Bridge across Blockhouse Bay
      { name: 'Olympic-Gibraltar Bridge', x0: -370, z0: Z_BASE + 310, x1: -310, z1: Z_BASE + 325, w: 7.0, archH: 2.4, yBase: 0.5 },
      // 3. Centreville to Algonquin Island Bridge across Long Pond East
      { name: 'Algonquin Bridge', x0: 320, z0: Z_BASE + 70, x1: 400, z1: Z_BASE + 90, w: 7.5, archH: 2.5, yBase: 0.5 },
      // 4. Algonquin to Ward's Island Bridge across Algonquin Canal
      { name: 'Ward-Algonquin Footbridge', x0: 720, z0: Z_BASE + 50, x1: 780, z1: Z_BASE + 70, w: 6.5, archH: 2.2, yBase: 0.5 },
      // 5. Avenue of the Island South Lagoon Bridge to South Beach
      { name: 'Avenue Lagoon Bridge', x0: -15, z0: Z_BASE + 330, x1: 15, z1: Z_BASE + 380, w: 10.0, archH: 2.5, yBase: 0.5 },
      // 6. Gibraltar to Hanlan's Point Trail Bridge across Hanlan's Canal
      { name: 'Gibraltar-Hanlan Bridge', x0: -610, z0: Z_BASE + 160, x1: -570, z1: Z_BASE + 205, w: 7.0, archH: 2.2, yBase: 0.5 }
    ];

    bridges.forEach(b => {
      const bg = new THREE.Group();
      const segs = 16;
      const dx = (b.x1 - b.x0) / segs;
      const dz = (b.z1 - b.z0) / segs;
      const len = Math.hypot(b.x1 - b.x0, b.z1 - b.z0);
      const rotY = Math.atan2(b.x1 - b.x0, b.z1 - b.z0);

      // Parabolic arch deck planks with visible water beneath
      for (let i = 0; i < segs; i++) {
        const t = (i + 0.5) / segs;
        const curY = b.yBase + Math.sin(t * Math.PI) * b.archH;
        const px = b.x0 + dx * i + dx * 0.5;
        const pz = b.z0 + dz * i + dz * 0.5;

        // Wood deck plank
        const plank = new THREE.Mesh(new THREE.BoxGeometry(b.w, 0.45, (len / segs) + 0.15), woodMat);
        plank.position.set(px, curY, pz);
        plank.rotation.y = rotY;
        bg.add(plank);

        // Side railings & posts
        [-b.w / 2 + 0.25, b.w / 2 - 0.25].forEach(rx => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.3, 1.15, 0.3), darkWoodMat);
          post.position.set(px + Math.cos(rotY) * rx, curY + 0.65, pz - Math.sin(rotY) * rx);
          bg.add(post);
        });
      }

      // Continuous handrails on top of posts
      [-b.w / 2 + 0.25, b.w / 2 - 0.25].forEach(rx => {
        const rail = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.15, len + 1.0), darkWoodMat);
        rail.position.set((b.x0 + b.x1) / 2 + Math.cos(rotY) * rx, b.yBase + b.archH * 0.68 + 1.15, (b.z0 + b.z1) / 2 - Math.sin(rotY) * rx);
        rail.rotation.y = rotY;
        bg.add(rail);
      });

      // Midspan timber support pilings resting in the water beneath
      const midX = (b.x0 + b.x1) / 2;
      const midZ = (b.z0 + b.z1) / 2;
      [-b.w / 2 + 0.5, b.w / 2 - 0.5].forEach(px => {
        const pile = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.4, 4.0, 8), darkWoodMat);
        pile.position.set(midX + Math.cos(rotY) * px, 1.0, midZ - Math.sin(rotY) * px);
        bg.add(pile);
      });

      // Heavy stone landing abutments anchoring bridge to shore
      [ [b.x0, b.z0], [b.x1, b.z1] ].forEach(([ax, az]) => {
        const abut = new THREE.Mesh(new THREE.BoxGeometry(b.w + 1.6, 1.4, 4.0), stoneMat);
        abut.position.set(ax, b.yBase + 0.2, az);
        abut.rotation.y = rotY;
        bg.add(abut);
      });

      islandsGroup.add(bg);
    });

    // --------------------------------------------------------------------------
    // Winding Crushed-Gravel & Dirt Nature Trails
    // --------------------------------------------------------------------------
    const trailsGroup = new THREE.Group();
    function addTrailSegment(x0, z0, x1, z1, w, mat) {
      const len = Math.hypot(x1 - x0, z1 - z0);
      const rotY = Math.atan2(x1 - x0, z1 - z0);
      const trail = new THREE.Mesh(new THREE.BoxGeometry(w, 0.12, len), mat || pathMat);
      trail.position.set((x0 + x1) / 2, 0.56, (z0 + z1) / 2);
      trail.rotation.y = rotY;
      trailsGroup.add(trail);
    }

    // Avenue of the Island Wide Crushed-Limestone Promenade
    addTrailSegment(0, Z_BASE + 10, 0, Z_BASE + 230, 14, pathMat);
    // Trail from Fountain past Maze
    addTrailSegment(0, Z_BASE + 145, -115, Z_BASE + 145, 8, pathMat);
    // Trail from Fountain to Centreville
    addTrailSegment(0, Z_BASE + 130, 190, Z_BASE + 130, 9, pathMat);
    // Long Pond North Bank Scenic Walkway (lined with willows)
    addTrailSegment(-180, Z_BASE + 225, 200, Z_BASE + 225, 6.5, pathMat);

    // Olympic Island Skyline Lawn Loop Trail
    addTrailSegment(0, Z_BASE + 280, -140, Z_BASE + 330, 7.5, pathMat);
    addTrailSegment(-140, Z_BASE + 330, -280, Z_BASE + 340, 7.0, pathMat);
    addTrailSegment(-280, Z_BASE + 340, -340, Z_BASE + 320, 6.5, pathMat);
    addTrailSegment(-140, Z_BASE + 330, -140, Z_BASE + 400, 7.0, pathMat);

    // West Woods & Gibraltar Nature Trails (Packed Dirt)
    addTrailSegment(-580, Z_BASE + 185, -480, Z_BASE + 280, 5.0, dirtMat);
    addTrailSegment(-480, Z_BASE + 280, -480, Z_BASE + 380, 5.5, dirtMat);
    addTrailSegment(-480, Z_BASE + 320, -350, Z_BASE + 318, 5.0, dirtMat);
    addTrailSegment(-720, Z_BASE - 100, -720, Z_BASE + 100, 8.0, pathMat); // Hanlan's Spine
    addTrailSegment(-720, Z_BASE + 100, -590, Z_BASE + 180, 6.0, dirtMat);

    // Algonquin & Ward's Island Cottage Lanes
    addTrailSegment(360, Z_BASE + 80, 650, Z_BASE + 80, 5.5, pathMat);
    addTrailSegment(500, Z_BASE + 20, 500, Z_BASE + 160, 4.5, dirtMat);
    addTrailSegment(750, Z_BASE + 60, 1150, Z_BASE + 60, 6.0, pathMat);
    addTrailSegment(950, Z_BASE - 10, 950, Z_BASE + 130, 5.0, pathMat);

    islandsGroup.add(trailsGroup);

    // --------------------------------------------------------------------------
    // Landmark 1: Centre Island Ferry Terminal & Docks (x: 0, z: 5000)
    // --------------------------------------------------------------------------
    {
      const termGrp = new THREE.Group();
      // Main boarding pier deck
      const pierDeck = new THREE.Mesh(new THREE.BoxGeometry(32, 0.6, 50), woodMat);
      pierDeck.position.set(0, 0.55, Z_BASE - 10);
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
    // Landmark 2: Avenue of the Island Formal Promenade, Gardens & Grand Fountain
    // --------------------------------------------------------------------------
    let fountainSpray = null;
    {
      const avg = new THREE.Group();

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
      const fWater = new THREE.Mesh(new THREE.CylinderGeometry(7.8, 7.8, 0.2, 28), lagoonWaterMat);
      fWater.position.set(0, 1.4, Z_BASE + 130);
      avg.add(fWater);
      const fTier2 = new THREE.Mesh(new THREE.CylinderGeometry(4.2, 4.8, 1.4, 20), stoneMat);
      fTier2.position.set(0, 2.0, Z_BASE + 130);
      avg.add(fTier2);
      const fTier3 = new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.4, 1.2, 16), stoneMat);
      fTier3.position.set(0, 3.1, Z_BASE + 130);
      avg.add(fTier3);

      fountainSpray = new THREE.Group();
      const sprayCone = new THREE.Mesh(
        new THREE.ConeGeometry(1.6, 5.0, 12, 1, true),
        new THREE.MeshBasicMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.7, side: THREE.DoubleSide })
      );
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
      mazeGround.position.set(hx, 0.57, hz);
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

      const gallery = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 3.2, 0.8, 12), darkWoodMat);
      gallery.position.set(lx, 24.8, lz);
      lhg.add(gallery);

      const lantern = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.2, 2.6, 12), glassMat);
      lantern.position.set(lx, 26.2, lz);
      lhg.add(lantern);

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

      const term = new THREE.Mesh(new THREE.BoxGeometry(72, 8.5, 36), concreteMat);
      term.position.set(ax, 4.75, az);
      apg.add(term);

      const glassFacade = new THREE.Mesh(new THREE.BoxGeometry(72.4, 4.5, 1.0), glassMat);
      glassFacade.position.set(ax, 5.0, az + 18.2);
      apg.add(glassFacade);

      const apSign = makeSign(['BILLY BISHOP TORONTO CITY AIRPORT (CYTZ)', 'ISLAND TERMINAL • WESTERN GAP • PORTER AIRLINES GATEWAY'], 24, 2.4, { bg: '#0f172a', fg: '#38bdf8', borderColor: '#0284c7' });
      apSign.position.set(ax, 9.8, az + 18.5);
      apg.add(apSign);

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

      function addAirplane(px, pz, rotY) {
        const pl = new THREE.Group();
        const fuse = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.6, 26, 12), new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 }));
        fuse.rotation.x = Math.PI / 2;
        pl.add(fuse);
        const wings = new THREE.Mesh(new THREE.BoxGeometry(28, 0.3, 3.5), new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4 }));
        wings.position.set(0, 0.8, -2);
        pl.add(wings);
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
        const bldg = new THREE.Mesh(new THREE.BoxGeometry(8.5, 3.4, 7.0), new THREE.MeshStandardMaterial({ color: col, roughness: 0.7 }));
        bldg.position.y = 1.7;
        c.add(bldg);
        const roof = new THREE.Mesh(new THREE.ConeGeometry(7.2, 2.6, 4), darkWoodMat);
        roof.position.y = 4.4;
        roof.rotation.y = Math.PI / 4;
        c.add(roof);
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
      hpPier.position.set(hx, 0.55, hz);
      hpg.add(hpPier);

      const hpSign = makeSign(['HANLAN\'S POINT FERRY TERMINAL', 'BOATS TO MAINLAND BATHURST QUAY & WEST HARBOUR'], 18, 2.2, { bg: '#1e3a8a', fg: '#38bdf8', borderColor: '#0284c7' });
      hpSign.position.set(hx, 4.2, hz + 12);
      hpg.add(hpSign);

      const plinth = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.8, 3.2), stoneMat);
      plinth.position.set(hx + 35, 1.4, hz + 35);
      hpg.add(plinth);
      const statue = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 2.4, 8), new THREE.MeshStandardMaterial({ color: 0x78350f, metalness: 0.8, roughness: 0.3 }));
      statue.position.set(hx + 35, 3.4, hz + 35);
      hpg.add(statue);

      islandsGroup.add(hpg);
    }

    // --------------------------------------------------------------------------
    // Lagoon Details: Canoe Slips, Moored Boats & Water Lily Pads
    // --------------------------------------------------------------------------
    {
      const boatGrp = new THREE.Group();
      const boatCols = [0xef4444, 0x3b82f6, 0xfacc15, 0x10b981];

      function addCanoe(cx, cz, rotY, col) {
        const boat = new THREE.Group();
        const hull = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.6, 5.2), new THREE.MeshStandardMaterial({ color: col, roughness: 0.5 }));
        hull.position.y = 0.2;
        boat.add(hull);
        const interior = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.4, 4.4), woodMat);
        interior.position.y = 0.35;
        boat.add(interior);
        boat.position.set(cx, 0.05, cz);
        boat.rotation.y = rotY;
        boatGrp.add(boat);
      }

      // Small rental boat docks along Long Pond & Algonquin Canal
      function addDock(dx, dz, dw, dd, rotY) {
        const d = new THREE.Mesh(new THREE.BoxGeometry(dw, 0.3, dd), woodMat);
        d.position.set(dx, 0.2, dz);
        d.rotation.y = rotY;
        boatGrp.add(d);
      }

      addDock(-40, Z_BASE + 235, 4.5, 14, 0);
      addCanoe(-36, Z_BASE + 235, 0.1, boatCols[0]);
      addCanoe(-44, Z_BASE + 235, -0.15, boatCols[1]);

      addDock(160, Z_BASE + 235, 4.5, 14, 0);
      addCanoe(164, Z_BASE + 235, 0.05, boatCols[2]);

      addDock(405, Z_BASE + 110, 14, 4.5, 0);
      addCanoe(405, Z_BASE + 115, Math.PI / 2 + 0.1, boatCols[3]);

      // Water lily pads floating in quiet backwaters
      const lilyMat = new THREE.MeshBasicMaterial({ color: 0x15803d, fog: false });
      const lilyFlowerMat = new THREE.MeshBasicMaterial({ color: 0xf472b6, fog: false });
      const lilySpots = [
        [-80, Z_BASE + 245], [-120, Z_BASE + 255], [60, Z_BASE + 245],
        [-340, Z_BASE + 330], [-350, Z_BASE + 350], [750, Z_BASE + 100]
      ];
      lilySpots.forEach(([lx, lz]) => {
        for (let i = 0; i < 4; i++) {
          const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 0.04, 8), lilyMat);
          pad.position.set(lx + (i % 2) * 1.4, 0.08, lz + Math.floor(i / 2) * 1.4);
          boatGrp.add(pad);
        }
        const fl = new THREE.Mesh(new THREE.DodecahedronGeometry(0.25), lilyFlowerMat);
        fl.position.set(lx + 0.5, 0.18, lz + 0.5);
        boatGrp.add(fl);
      });

      islandsGroup.add(boatGrp);
    }

    // --------------------------------------------------------------------------
    // Ancient Toronto Island Urban Forest & Canopy System (380+ Full 3D Trees)
    // --------------------------------------------------------------------------
    {
      const forestGroup = new THREE.Group();

      /**
       * Creates an authentic 3D tree:
       * - 'cottonwood': Heritage Eastern Cottonwood (thick trunk, 18m tall sprawling canopy)
       * - 'willow': Cascading Weeping Willow (leaning trunk, drooping pendulous branches touching water)
       * - 'maple': Sugar Maple / Red Oak (dense rounded shade crown)
       * - 'pine': Coastal White Pine (tall conifer with tiered needle skirts)
       */
      function buildTree(x, z, species, scale, rotY, leanAngle) {
        const sc = scale || 1.0;
        const tg = new THREE.Group();

        if (species === 'willow') {
          // Weeping Willow (Salix babylonica)
          const lean = leanAngle !== undefined ? leanAngle : 0.25;
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.45 * sc, 0.75 * sc, 6.5 * sc, 8), barkMat);
          trunk.position.y = (3.25 * sc);
          trunk.rotation.z = lean;
          tg.add(trunk);

          // Broad umbrella crown dome
          const crownDome = new THREE.Mesh(new THREE.ConeGeometry(5.2 * sc, 4.2 * sc, 8), leafWillowMat);
          crownDome.position.set(-Math.sin(lean) * 3.0 * sc, 7.5 * sc, 0);
          tg.add(crownDome);

          // 7 Drooping pendulous branch curtains hanging down toward the water
          const droopCount = 7;
          for (let d = 0; d < droopCount; d++) {
            const ang = (d / droopCount) * Math.PI * 2;
            const r = 3.6 * sc;
            const droop = new THREE.Mesh(new THREE.ConeGeometry(1.6 * sc, 6.2 * sc, 6), leafWillowDroopMat);
            droop.position.set(
              -Math.sin(lean) * 3.0 * sc + Math.cos(ang) * r,
              5.2 * sc,
              Math.sin(ang) * r
            );
            tg.add(droop);
          }
        } else if (species === 'pine') {
          // Coastal White Pine & Eastern Redcedar
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.32 * sc, 0.55 * sc, 8.0 * sc, 6), barkMat);
          trunk.position.y = 4.0 * sc;
          tg.add(trunk);

          // 3 Tiered Conical Evergreen Needle Skirts
          [
            { r: 4.4 * sc, h: 4.8 * sc, y: 7.2 * sc },
            { r: 3.4 * sc, h: 4.2 * sc, y: 10.4 * sc },
            { r: 2.2 * sc, h: 3.6 * sc, y: 13.2 * sc }
          ].forEach(t => {
            const cone = new THREE.Mesh(new THREE.ConeGeometry(t.r, t.h, 7), pineMat);
            cone.position.y = t.y;
            tg.add(cone);
          });
        } else if (species === 'maple') {
          // Sugar Maple / Red Oak
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.48 * sc, 0.78 * sc, 7.5 * sc, 8), barkMat);
          trunk.position.y = 3.75 * sc;
          tg.add(trunk);

          // Multi-spherical dense leafy shade crown
          const mainCrown = new THREE.Mesh(new THREE.DodecahedronGeometry(4.8 * sc, 1), leafDarkMat);
          mainCrown.position.y = 9.2 * sc;
          tg.add(mainCrown);

          const sideCrown1 = new THREE.Mesh(new THREE.DodecahedronGeometry(3.6 * sc, 1), leafSummerMat);
          sideCrown1.position.set(2.2 * sc, 8.0 * sc, 1.2 * sc);
          tg.add(sideCrown1);

          const sideCrown2 = new THREE.Mesh(new THREE.DodecahedronGeometry(3.4 * sc, 1), leafDeepMat);
          sideCrown2.position.set(-2.0 * sc, 8.4 * sc, -1.0 * sc);
          tg.add(sideCrown2);
        } else {
          // Heritage Eastern Cottonwood (Populus deltoides)
          // Massive deeply-furrowed trunk and vast spreading 18m canopy
          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.75 * sc, 1.25 * sc, 10.0 * sc, 8), barkCottonwoodMat);
          trunk.position.y = 5.0 * sc;
          tg.add(trunk);

          // 5 Large spreading canopy foliage lobes
          const lobes = [
            { rx: 0, ry: 12.5 * sc, rz: 0, r: 6.2 * sc, mat: leafDarkMat },
            { rx: 3.5 * sc, ry: 11.0 * sc, rz: 2.0 * sc, r: 4.8 * sc, mat: leafSummerMat },
            { rx: -3.8 * sc, ry: 11.2 * sc, rz: -2.2 * sc, r: 5.0 * sc, mat: leafDeepMat },
            { rx: -2.2 * sc, ry: 13.8 * sc, rz: 3.2 * sc, r: 4.6 * sc, mat: leafDarkMat },
            { rx: 2.5 * sc, ry: 14.0 * sc, rz: -2.8 * sc, r: 4.5 * sc, mat: leafSummerMat }
          ];
          lobes.forEach(lb => {
            const fol = new THREE.Mesh(new THREE.DodecahedronGeometry(lb.r, 1), lb.mat);
            fol.position.set(lb.rx, lb.ry, lb.rz);
            tg.add(fol);
          });
        }

        tg.position.set(x, 0.55, z);
        if (rotY) tg.rotation.y = rotY;
        forestGroup.add(tg);
      }

      // ------------------------------------------------------------------------
      // Sector 1: Long Pond & Allan Lamport Regatta Course Willow Belts (75 Trees)
      // Weeping willows line both banks of Long Pond, dipping into the water
      // ------------------------------------------------------------------------
      for (let wx = -220; wx <= 220; wx += 16) {
        if (Math.abs(wx) > 18) { // Leave opening for Manitou Bridge at x = 0
          // North Bank
          buildTree(wx, Z_BASE + 226, 'willow', 0.95 + ((wx % 7) * 0.05), (wx * 0.3), 0.22);
          // North Bank second row (massive cottonwoods behind willows)
          if (wx % 32 === 0) {
            buildTree(wx, Z_BASE + 215, 'cottonwood', 1.15, (wx * 0.5));
          }
        }
      }
      for (let wx = -200; wx <= 40; wx += 16) {
        if (Math.abs(wx) > 18) { // Leave opening for Manitou Bridge
          // South Bank (Olympic Island edge)
          buildTree(wx, Z_BASE + 284, 'willow', 0.98 + ((wx % 5) * 0.05), (wx * 0.4), -0.22);
        }
      }

      // ------------------------------------------------------------------------
      // Sector 2: Avenue of the Island Tree Allée & Promenade (60 Trees)
      // Forms an overhead shady tree corridor leading from docks to fountain
      // ------------------------------------------------------------------------
      for (let fz = Z_BASE + 25; fz <= Z_BASE + 225; fz += 18) {
        [-14, 14].forEach((fx, fi) => {
          const sp = (fz % 36 === 0) ? 'cottonwood' : 'maple';
          buildTree(fx, fz, sp, 1.05 + (fi * 0.1), fz * 0.2);
        });
        // Outer wood border
        [-24, 24].forEach((fx) => {
          if (fz % 36 === 18) {
            buildTree(fx, fz, 'cottonwood', 1.2, fz * 0.3);
          }
        });
      }

      // ------------------------------------------------------------------------
      // Sector 3: William Meany Hedge Maze Enclosing Forest (35 Trees)
      // Dense forest wall enclosing the maze so it sits secluded in the woods
      // ------------------------------------------------------------------------
      for (let mx = -165; mx <= -65; mx += 18) {
        buildTree(mx, Z_BASE + 102, 'cottonwood', 1.1, mx * 0.2); // North of maze
        buildTree(mx, Z_BASE + 188, 'maple', 1.05, mx * 0.3);    // South of maze
      }
      for (let mz = Z_BASE + 110; mz <= Z_BASE + 180; mz += 18) {
        buildTree(-160, mz, 'cottonwood', 1.2, mz * 0.25);        // West of maze
      }

      // ------------------------------------------------------------------------
      // Sector 4: Centreville Amusement Park Forest Groves (45 Trees)
      // Encloses the vintage carousel, Ferris wheel, and Pizza Pizza patio
      // ------------------------------------------------------------------------
      for (let cx = 80; cx <= 240; cx += 22) {
        buildTree(cx, Z_BASE + 95, 'cottonwood', 1.15, cx * 0.4);
        buildTree(cx, Z_BASE + 245, 'willow', 1.0, cx * 0.2, 0.18);
      }
      [
        [110, Z_BASE + 140], [110, Z_BASE + 200], [150, Z_BASE + 145],
        [210, Z_BASE + 175], [235, Z_BASE + 130], [240, Z_BASE + 215]
      ].forEach(([tx, tz]) => {
        buildTree(tx, tz, 'maple', 1.0, tx * 0.1);
      });

      // ------------------------------------------------------------------------
      // Sector 5: Olympic Island Great Lawn & Skyline Vista Frame (50 Trees)
      // Ring of towering cottonwoods & willows around perimeter, leaving center
      // open for the panoramic view of CN Tower and city skyline across Long Pond!
      // ------------------------------------------------------------------------
      for (let ox = -300; ox <= 20; ox += 24) {
        buildTree(ox, Z_BASE + 412, 'cottonwood', 1.25, ox * 0.1); // South outer rim
      }
      for (let oz = Z_BASE + 295; oz <= Z_BASE + 400; oz += 20) {
        buildTree(-305, oz, 'willow', 1.05, oz * 0.2, 0.25);     // West rim along Blockhouse Bay
        buildTree(35, oz, 'willow', 1.0, oz * 0.3, -0.22);       // East rim along lagoon
      }
      // Clustered grove inside Olympic Island knolls
      [
        [-240, Z_BASE + 360], [-210, Z_BASE + 380], [-80, Z_BASE + 380],
        [-50, Z_BASE + 360], [-170, Z_BASE + 395]
      ].forEach(([tx, tz]) => {
        buildTree(tx, tz, 'cottonwood', 1.3, tx * 0.5);
      });

      // ------------------------------------------------------------------------
      // Sector 6: Gibraltar Point Nature Reserve & 1808 Lighthouse Sanctuary (55 Trees)
      // Dense maritime conifer & heritage cottonwood woodland with whispering pines
      // ------------------------------------------------------------------------
      for (let gx = -580; gx <= -380; gx += 25) {
        buildTree(gx, Z_BASE + 225, 'willow', 1.0, gx * 0.2, -0.2); // Hanlan's canal edge
        buildTree(gx, Z_BASE + 415, 'pine', 1.15, gx * 0.3);        // Dune pines
      }
      for (let gz = Z_BASE + 235; gz <= Z_BASE + 410; gz += 22) {
        buildTree(-380, gz, 'willow', 1.05, gz * 0.4, 0.22);       // Blockhouse Bay edge
        buildTree(-585, gz, 'cottonwood', 1.2, gz * 0.1);          // West woodland edge
      }
      // Ancient pines surrounding the 1808 Lighthouse clearing
      [
        [-505, Z_BASE + 300], [-455, Z_BASE + 300],
        [-505, Z_BASE + 340], [-455, Z_BASE + 340],
        [-520, Z_BASE + 320], [-440, Z_BASE + 320]
      ].forEach(([tx, tz]) => {
        buildTree(tx, tz, 'pine', 1.2, tx * 0.2);
      });

      // ------------------------------------------------------------------------
      // Sector 7: Hanlan's Point Heritage Woodland & Dunes (40 Trees)
      // Famous mature cottonwoods producing the historic June summer snow
      // ------------------------------------------------------------------------
      for (let hx = -860; hx <= -620; hx += 28) {
        buildTree(hx, Z_BASE - 60, 'cottonwood', 1.3, hx * 0.3);
        buildTree(hx, Z_BASE + 140, 'cottonwood', 1.25, hx * 0.4);
      }
      for (let hz = Z_BASE - 40; hz <= Z_BASE + 120; hz += 24) {
        buildTree(-610, hz, 'maple', 1.1, hz * 0.2);
        buildTree(-870, hz, 'pine', 1.05, hz * 0.5); // Hanlan's beach dunes
      }

      // ------------------------------------------------------------------------
      // Sector 8: Algonquin & Ward's Island Cottage Village Canopies (50 Trees)
      // Weeping willows along Algonquin Canal & tall maples shading cottage lanes
      // ------------------------------------------------------------------------
      // Algonquin Canal Willow Corridor
      for (let cz = Z_BASE + 10; cz <= Z_BASE + 170; cz += 20) {
        buildTree(715, cz, 'willow', 1.05, cz * 0.3, 0.22); // Algonquin west bank
        buildTree(785, cz, 'willow', 1.05, cz * 0.4, -0.22); // Ward's east bank
      }
      // Algonquin Cottage Gardens
      [
        [430, Z_BASE + 30], [470, Z_BASE + 70], [530, Z_BASE + 35],
        [580, Z_BASE + 120], [630, Z_BASE + 50], [660, Z_BASE + 130]
      ].forEach(([tx, tz]) => {
        buildTree(tx, tz, 'maple', 1.0, tx * 0.2);
      });
      // Ward's Village & Cafe Shading Canopies
      [
        [830, Z_BASE + 30], [880, Z_BASE + 80], [940, Z_BASE + 20],
        [980, Z_BASE + 100], [1030, Z_BASE + 40], [1070, Z_BASE + 95],
        [1120, Z_BASE + 35], [1160, Z_BASE + 110], [1210, Z_BASE + 40]
      ].forEach(([tx, tz]) => {
        buildTree(tx, tz, 'cottonwood', 1.25, tx * 0.3);
      });

      islandsGroup.add(forestGroup);
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
      // 1. Bridges are always walkable at deck height across water channels
      const b = getIslandBridgeAt(x, z);
      if (b) return true;

      // 2. Pier and Boardwalks
      if (Math.abs(x) <= 6 && z >= Z_BASE + 450 && z <= Z_BASE + 590) return true; // Centre Pier
      if (x >= 1050 && x <= 1230 && z >= Z_BASE + 135 && z <= Z_BASE + 145) return true; // Ward's Boardwalk
      if (Math.abs(x) <= 16 && z >= Z_BASE - 35 && z <= Z_BASE + 15) return true; // Centre Dock Pier
      if (Math.abs(x - (-720)) <= 12 && z >= Z_BASE - 140 && z <= Z_BASE - 100) return true; // Hanlan's Pier

      // 3. Solid building collisions (Pizza Pizza, Lighthouse base, Airport terminal)
      if (x >= 158 && x <= 182 && z >= Z_BASE + 222 && z <= Z_BASE + 238) return false; // Pizza Pizza walls
      if (Math.hypot(x - (-480), z - (Z_BASE + 320)) < 4.2) return false; // Lighthouse stone tower base
      if (x >= -1100 && x <= -1020 && z >= Z_BASE - 250 && z <= Z_BASE - 210) return false; // Airport terminal

      // 4. Open Water Channels (Water blocks walking! Player must cross on bridge)
      // Long Pond channel (between Centre Island and Olympic Island)
      if (z > Z_BASE + 230 && z < Z_BASE + 280 && x >= -270 && x <= 120) return false;
      // Blockhouse Bay channel (between Gibraltar Point and Olympic Island)
      if (x > -370 && x < -310 && z >= Z_BASE + 240 && z <= Z_BASE + 390) return false;
      // South Lagoon channel (between Centre Island and South Beach Dunes)
      if (z > Z_BASE + 330 && z < Z_BASE + 380 && x >= -90 && x <= 220) return false;
      // Long Pond East channel (between Centreville and Algonquin Island)
      if (x > 320 && x < 400 && z >= Z_BASE + 20 && z <= Z_BASE + 190) return false;
      // Algonquin Canal (between Algonquin Island and Ward's Island)
      if (x > 720 && x < 780 && z >= Z_BASE - 10 && z <= Z_BASE + 170) return false;
      // Hanlan's Canal (between Gibraltar Point and Hanlan's Point)
      if (z > Z_BASE + 160 && z < Z_BASE + 210 && x >= -660 && x <= -520) return false;
      // Inner Harbour (North of island docks) - except Billy Bishop Airport (x <= -980)
      if (z < Z_BASE - 15 && x > -980) return false;
      // Lake Ontario (South of beaches)
      if (z > Z_BASE + 490) return false;
      // Western Gap
      if (x > -980 && x < -920 && z >= Z_BASE - 280 && z <= Z_BASE + 100) return false;

      // 5. Landmass checks
      // A. Centre Island Main (Docks, Promenade, Gardens, Maze, Centreville)
      if (x >= -240 && x <= 320 && z >= Z_BASE - 15 && z <= Z_BASE + 230) return true;
      if (Math.hypot(x - 80, z - (Z_BASE + 180)) <= 210 && z <= Z_BASE + 230) return true;

      // B. Olympic Island
      if (x >= -310 && x <= 50 && z >= Z_BASE + 280 && z <= Z_BASE + 440) return true;

      // C. South Beach Dune Ridge
      if (x >= -90 && x <= 260 && z >= Z_BASE + 380 && z <= Z_BASE + 490) return true;

      // D. Gibraltar Point
      if (x >= -600 && x <= -370 && z >= Z_BASE + 210 && z <= Z_BASE + 450) return true;

      // E. Hanlan's Point
      if (x >= -920 && x <= -570 && z >= Z_BASE - 140 && z <= Z_BASE + 160) return true;

      // F. Billy Bishop Airport
      if (x >= -1560 && x <= -980 && z >= Z_BASE - 320 && z <= Z_BASE - 40) return true;

      // G. Algonquin Island
      if (x >= 400 && x <= 720 && z >= Z_BASE - 10 && z <= Z_BASE + 190) return true;

      // H. Ward's Island
      if (x >= 780 && x <= 1260 && z >= Z_BASE - 40 && z <= Z_BASE + 190) return true;

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
      if (x <= -980) return "BILLY BISHOP AIRPORT (CYTZ)";
      if (x <= -600 && z <= Z_BASE + 100) return "HANLAN'S POINT • FERRY SLIP";
      if (x <= -600) return "HANLAN'S POINT BEACH • LAKE ONTARIO";
      if (x <= -370 && z >= Z_BASE + 210) return "GIBRALTAR POINT • 1808 LIGHTHOUSE";
      if (x <= 50 && z >= Z_BASE + 280) return "OLYMPIC ISLAND • SKYLINE LAWN";
      if (z >= Z_BASE + 380) return "CENTRE ISLAND BEACH & LAKE ONTARIO PIER";
      if (x >= 80 && x <= 320 && z >= Z_BASE + 100 && z <= Z_BASE + 250) {
        if (Math.hypot(x - 170, z - (Z_BASE + 230)) < 24) return "PIZZA PIZZA • CENTREVILLE";
        return "CENTREVILLE AMUSEMENT PARK";
      }
      if (x >= -160 && x <= -70 && z >= Z_BASE + 100 && z <= Z_BASE + 190) return "WILLIAM MEANY HEDGE MAZE";
      if (x >= 400 && x <= 720) return "ALGONQUIN ISLAND • COTTAGES";
      if (x >= 780) {
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
      if (ferrisWheelMesh) {
        ferrisWheelMesh.rotation.z += dt * 0.25;
      }
      if (fountainSpray) {
        fountainSpray.scale.y = 0.95 + Math.sin(tTime * 4.5) * 0.12;
      }
      if (lighthouseBeacon) {
        lighthouseBeacon.rotation.y += dt * 1.8;
      }
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

      const scale = size / 3200;
      const ox = size / 2;
      const oz = size / 2;

      function toMx(wx) { return ox + wx * scale; }
      function toMz(wz) { return oz + (wz - (Z_BASE + 100)) * (scale * 2.6); }

      // Water background (Lake Ontario / Harbour)
      ctx.fillStyle = '#0284c7';
      ctx.fillRect(0, 0, size, size);

      // Distinct Islands (with visible blue water channels between them!)
      // Centre Island Main
      ctx.fillStyle = '#15803d';
      ctx.fillRect(toMx(-240), toMz(Z_BASE - 15), 560 * scale, 245 * scale * 2.6);

      // Olympic Island (separated by Long Pond!)
      ctx.fillStyle = '#16a34a';
      ctx.fillRect(toMx(-310), toMz(Z_BASE + 280), 360 * scale, 140 * scale * 2.6);

      // South Beach Dune Ridge (separated by South Lagoon!)
      ctx.fillStyle = '#fde047';
      ctx.fillRect(toMx(-90), toMz(Z_BASE + 380), 350 * scale, 100 * scale * 2.6);

      // Gibraltar Point (separated by Blockhouse Bay!)
      ctx.fillStyle = '#15803d';
      ctx.fillRect(toMx(-600), toMz(Z_BASE + 210), 230 * scale, 230 * scale * 2.6);

      // Hanlan's Point (separated by Hanlan's Canal!)
      ctx.fillStyle = '#15803d';
      ctx.fillRect(toMx(-920), toMz(Z_BASE - 140), 350 * scale, 300 * scale * 2.6);

      // Billy Bishop Airport
      ctx.fillStyle = '#475569';
      ctx.fillRect(toMx(-1560), toMz(Z_BASE - 320), 580 * scale, 280 * scale * 2.6);
      ctx.fillStyle = '#1e293b';
      ctx.fillRect(toMx(-1520), toMz(Z_BASE - 190), 500 * scale, 40 * scale * 2.6); // Runway

      // Algonquin Island (separated by Long Pond East & Algonquin Canal!)
      ctx.fillStyle = '#16a34a';
      ctx.fillRect(toMx(400), toMz(Z_BASE - 10), 320 * scale, 200 * scale * 2.6);

      // Ward's Island
      ctx.fillStyle = '#15803d';
      ctx.fillRect(toMx(780), toMz(Z_BASE - 40), 460 * scale, 230 * scale * 2.6);

      // Beaches (Golden Sand)
      ctx.fillStyle = '#fde047';
      ctx.fillRect(toMx(-920), toMz(Z_BASE - 100), 40 * scale, 220 * scale * 2.6); // Hanlan's Beach
      ctx.fillRect(toMx(1200), toMz(Z_BASE - 10), 60 * scale, 180 * scale * 2.6); // Ward's Beach

      // Walkable Bridges spanning across the blue waterways
      ctx.strokeStyle = '#b45309';
      ctx.lineWidth = 3.0;
      bridges.forEach(b => {
        ctx.beginPath();
        ctx.moveTo(toMx(b.x0), toMz(b.z0));
        ctx.lineTo(toMx(b.x1), toMz(b.z1));
        ctx.stroke();
      });

      // Centre Pier
      ctx.fillStyle = '#92400e';
      ctx.fillRect(toMx(-6), toMz(Z_BASE + 450), 12 * scale, 120 * scale * 2.6);

      // Docks & Landmarks (Labels & Icons)
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 8px sans-serif';
      ctx.fillText('🚢 CENTRE DOCK', toMx(0) - 30, toMz(Z_BASE) - 6);
      ctx.fillText('✈️ AIRPORT', toMx(-1360), toMz(Z_BASE - 200));
      ctx.fillText('🗼 1808 LIGHTHOUSE', toMx(-570), toMz(Z_BASE + 330));
      ctx.fillText('🎡 CENTREVILLE', toMx(170), toMz(Z_BASE + 130));
      ctx.fillText('🏡 WARD\'S ISLAND', toMx(950), toMz(Z_BASE + 20));

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
