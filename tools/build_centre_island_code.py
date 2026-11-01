#!/usr/bin/env python3
"""
Generates and inserts the complete Toronto Centre Island 3D geometry and interactive features into city.js.
"""
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CITY_JS = BASE_DIR / 'city.js'

centre_island_code = '''      // 2. CENTRE ISLAND • FULL INTERACTIVE TORONTO ISLAND WORLD (x = 180, z = 1250)
      const centreIsland = new THREE.Group();
      islandsGroup.add(centreIsland);

      const islandTurfMat = new THREE.MeshBasicMaterial({ color: 0x1a4d2e, fog: false });
      const islandPathMat = new THREE.MeshBasicMaterial({ color: 0x94a3b8, fog: false });
      const islandBoardwalkMat = new THREE.MeshBasicMaterial({ color: 0xb45309, fog: false });
      const islandLagoonMat = new THREE.MeshBasicMaterial({ color: 0x0284c7, transparent: true, opacity: 0.85, fog: false });
      const islandWhiteMat = new THREE.MeshBasicMaterial({ color: 0xf8fafc, fog: false });
      const islandOrangeMat = new THREE.MeshBasicMaterial({ color: 0xea580c, fog: false });
      const islandHedgeMat = new THREE.MeshBasicMaterial({ color: 0x14532d, fog: false });
      const islandFlowerRed = new THREE.MeshBasicMaterial({ color: 0xef4444, fog: false });
      const islandFlowerYellow = new THREE.MeshBasicMaterial({ color: 0xfacc15, fog: false });
      const islandFlowerPurple = new THREE.MeshBasicMaterial({ color: 0xa855f7, fog: false });

      // ---------- A. Base Island Landmasses (North lawns, South beach, Olympic Island) ----------
      {
        // 1. North Island main body (Avenue of the Island, Gardens, Maze, Centreville North)
        const northTurf = new THREE.Mesh(new THREE.BoxGeometry(580, 2.0, 180), islandTurfMat);
        northTurf.position.set(160, WATER_Y + 1.0, 1150);
        centreIsland.add(northTurf);

        // 2. South Island main body (Olympic Island South, Centreville South, Lawn Picnic Areas)
        const southTurf = new THREE.Mesh(new THREE.BoxGeometry(580, 2.0, 140), islandTurfMat);
        southTurf.position.set(160, WATER_Y + 1.0, 1310);
        centreIsland.add(southTurf);

        // 3. Olympic Island West Lawn (x: -140..40, z: 1120..1360)
        const olympicTurf = new THREE.Mesh(new THREE.BoxGeometry(180, 2.0, 220), islandTurfMat);
        olympicTurf.position.set(-60, WATER_Y + 1.0, 1240);
        centreIsland.add(olympicTurf);

        // 4. Centre Island Beach & Manitou Beach (Golden sand dunes sloping gently into Lake Ontario)
        const beachSand = new THREE.Mesh(new THREE.BoxGeometry(600, 2.0, 120), islandSandMat);
        beachSand.position.set(160, WATER_Y + 0.95, 1430);
        centreIsland.add(beachSand);

        // Sandy shoreline outer collar for smooth coastal transition
        const shoreCollar = new THREE.Mesh(new THREE.CylinderGeometry(340, 350, 1.4, 32), islandSandMat);
        shoreCollar.scale.set(1.0, 1.0, 0.65);
        shoreCollar.position.set(170, WATER_Y + 0.5, 1260);
        centreIsland.add(shoreCollar);

        // Long Pond Lagoon Water Surface (nestled between north & south island masses)
        const lagoonWater1 = new THREE.Mesh(new THREE.BoxGeometry(540, 0.2, 40), islandLagoonMat);
        lagoonWater1.position.set(160, WATER_Y + 0.25, 1248);
        centreIsland.add(lagoonWater1);

        const swanCoveWater = new THREE.Mesh(new THREE.BoxGeometry(50, 0.2, 45), islandLagoonMat);
        swanCoveWater.position.set(285, WATER_Y + 0.25, 1268);
        centreIsland.add(swanCoveWater);
      }

      // ---------- B. The 3 Arching Footbridges over the Lagoons ----------
      function createArchFootbridge(x, z, width, length, archH, railColor, name) {
        const bg = new THREE.Group();
        const segs = 10;
        const deckMat = new THREE.MeshBasicMaterial({ color: 0x78350f, fog: false });
        const railMat = new THREE.MeshBasicMaterial({ color: railColor, fog: false });

        for (let i = 0; i < segs; i++) {
          const t0 = i / segs, t1 = (i + 1) / segs;
          const y0 = Math.sin(t0 * Math.PI) * archH;
          const y1 = Math.sin(t1 * Math.PI) * archH;
          const z0 = -length / 2 + t0 * length;
          const z1 = -length / 2 + t1 * length;
          const dz = z1 - z0, dy = y1 - y0;
          const segLen = Math.hypot(dz, dy);
          const seg = new THREE.Mesh(new THREE.BoxGeometry(width, 0.45, segLen + 0.1), deckMat);
          seg.position.set(0, (y0 + y1) / 2 + 0.2, (z0 + z1) / 2);
          seg.rotation.x = -Math.atan2(dy, dz);
          bg.add(seg);

          // Railings on left and right
          [-width / 2 + 0.2, width / 2 - 0.2].forEach(rx => {
            const post = new THREE.Mesh(new THREE.BoxGeometry(0.2, 1.1, 0.2), railMat);
            post.position.set(rx, y0 + 0.75, z0);
            bg.add(post);

            const handrail = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.15, segLen + 0.1), railMat);
            handrail.position.set(rx, (y0 + y1) / 2 + 1.25, (z0 + z1) / 2);
            handrail.rotation.x = -Math.atan2(dy, dz);
            bg.add(handrail);
          });
        }

        // Stone end pillars with glowing warm carriage lanterns
        [-width / 2, width / 2].forEach(px => {
          [-length / 2, length / 2].forEach(pz => {
            const pier = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.8, 1.2), islandStoneMat);
            pier.position.set(px, 0.9, pz);
            bg.add(pier);

            const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.35, 6, 6), islandGoldMat);
            lamp.position.set(px, 2.0, pz);
            bg.add(lamp);
          });
        });

        bg.position.set(x, 0, z);
        centreIsland.add(bg);
        return bg;
      }

      // 1. Avenue of the Island Grand Bridge
      createArchFootbridge(180, 1248, 11.5, 32.0, 2.5, 0xf8fafc, 'Avenue of the Island Footbridge');
      // 2. Centreville Amusement Park Footbridge
      createArchFootbridge(240, 1242, 9.5, 30.0, 2.1, 0xfacc15, 'Centreville Footbridge');
      // 3. Olympic Island West Footbridge
      createArchFootbridge(10, 1230, 8.5, 28.0, 1.9, 0xd97706, 'Olympic Island Footbridge');

      // ---------- C. Centre Island Ferry Terminal & Docks (x = 180, z = 1080) ----------
      {
        const dtg = new THREE.Group();
        // Main wooden ferry docking pier extending north into harbour
        const pier = new THREE.Mesh(new THREE.BoxGeometry(18, 1.6, 38), islandBoardwalkMat);
        pier.position.set(180, 0.8, 1072);
        dtg.add(pier);

        // Pier support pilings in water
        for (let pz = 1056; pz <= 1088; pz += 6) {
          [-8.5, 8.5].forEach(px => {
            const piling = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.35, 3.5, 8), islandWoodMat);
            piling.position.set(180 + px, WATER_Y + 0.8, pz);
            dtg.add(piling);
          });
        }

        // Grand Heritage Entrance Gateway Arch
        const gateL = new THREE.Mesh(new THREE.BoxGeometry(1.8, 7.5, 1.8), islandStoneMat);
        gateL.position.set(171, 3.75, 1088);
        const gateR = new THREE.Mesh(new THREE.BoxGeometry(1.8, 7.5, 1.8), islandStoneMat);
        gateR.position.set(189, 3.75, 1088);
        const archTop = new THREE.Mesh(new THREE.BoxGeometry(22, 1.6, 2.2), islandStoneMat);
        archTop.position.set(180, 7.8, 1088);
        dtg.add(gateL, gateR, archTop);

        const welcomeSign = signMesh(['WELCOME TO CENTRE ISLAND', 'TORONTO ISLAND PARK • EST. 1870'], 20, 2.6, { bg: '#064e3b', fg: '#fef08a', borderColor: '#10b981', size: 56 });
        welcomeSign.position.set(180, 7.8, 1087);
        dtg.add(welcomeSign);

        const welcomeSignBack = signMesh(['CENTRE ISLAND FERRY TERMINAL', 'FERRIES TO DOWNTOWN TORONTO'], 19, 2.4, { bg: '#064e3b', fg: '#fef08a', borderColor: '#10b981', size: 54 });
        welcomeSignBack.position.set(180, 7.8, 1089);
        welcomeSignBack.rotation.y = Math.PI;
        dtg.add(welcomeSignBack);

        // Turnstiles, Waiting Canopy & Island Info Board
        const canopyRoof = new THREE.Mesh(new THREE.BoxGeometry(16, 0.4, 8), islandTurfMat);
        canopyRoof.position.set(180, 4.2, 1098);
        dtg.add(canopyRoof);
        [-7, 7].forEach(cx => {
          const col = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 4.0, 8), islandStoneMat);
          col.position.set(180 + cx, 2.0, 1098);
          dtg.add(col);
        });

        const infoBoard = signMesh(['TORONTO ISLAND PARK MAP', 'CENTREVILLE • BEACHES • HEDGE MAZE • PIZZA PIZZA'], 12, 2.2, { bg: '#1e3a8a', fg: '#38bdf8', borderColor: '#60a5fa', size: 48 });
        infoBoard.position.set(194, 2.4, 1098);
        infoBoard.rotation.y = -Math.PI / 2;
        dtg.add(infoBoard);

        // Bicycle rental racks with colorful rental bikes
        for (let bi = 0; bi < 8; bi++) {
          const bikeMat = [islandRedMat, islandGoldMat, islandCyanMat][bi % 3];
          const bikeFrame = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.8, 1.8), bikeMat);
          bikeFrame.position.set(168, 0.5, 1094 + bi * 1.5);
          dtg.add(bikeFrame);
        }

        centreIsland.add(dtg);
      }

      // ---------- D. Avenue of the Island & Formal Gardens (x: 160..200, z: 1088..1380) ----------
      {
        const avg = new THREE.Group();
        // Central Pedestrian Promenade
        const promenade = new THREE.Mesh(new THREE.BoxGeometry(12, 0.25, 280), islandPathMat);
        promenade.position.set(180, 0.12, 1235);
        avg.add(promenade);

        // Grand Ornamental Fountain at x = 180, z = 1170
        const fBasin = new THREE.Mesh(new THREE.CylinderGeometry(8.0, 8.5, 1.2, 28), islandStoneMat);
        fBasin.position.set(180, 0.6, 1170);
        avg.add(fBasin);
        const fPool = new THREE.Mesh(new THREE.CylinderGeometry(7.4, 7.4, 0.3, 28), islandLagoonMat);
        fPool.position.set(180, 1.1, 1170);
        avg.add(fPool);

        const fTier2 = new THREE.Mesh(new THREE.CylinderGeometry(4.4, 4.8, 1.4, 20), islandStoneMat);
        fTier2.position.set(180, 1.8, 1170);
        avg.add(fTier2);
        const fTier3 = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.5, 1.2, 16), islandStoneMat);
        fTier3.position.set(180, 2.8, 1170);
        avg.add(fTier3);

        islandFountainSpray = new THREE.Group();
        const sprayCore = new THREE.Mesh(
          new THREE.ConeGeometry(1.6, 5.5, 12, 1, true),
          new THREE.MeshBasicMaterial({ color: 0xbae6fd, transparent: true, opacity: 0.65, side: THREE.DoubleSide, fog: false })
        );
        sprayCore.position.y = 5.2;
        islandFountainSpray.add(sprayCore);
        // 8 arching spray streams
        for (let si = 0; si < 8; si++) {
          const sa = (si / 8) * Math.PI * 2;
          const stream = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 3.8), islandCyanMat);
          stream.position.set(Math.cos(sa) * 2.8, 2.8, Math.sin(sa) * 2.8);
          stream.rotation.y = sa;
          stream.rotation.x = 0.45;
          islandFountainSpray.add(stream);
        }
        islandFountainSpray.position.set(180, 0, 1170);
        avg.add(islandFountainSpray);

        // Raised Stone Flowerbeds with vibrant blooms along Avenue of the Island
        for (let fz = 1110; fz <= 1220; fz += 22) {
          [-8.5, 8.5].forEach((fx, fi) => {
            const fbed = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.65, 12), islandStoneMat);
            fbed.position.set(180 + fx, 0.32, fz);
            avg.add(fbed);

            // Flower blossom clusters
            const col = (fi + fz) % 3 === 0 ? islandFlowerRed : ((fi + fz) % 3 === 1 ? islandFlowerYellow : islandFlowerPurple);
            for (let fl = -4.5; fl <= 4.5; fl += 2.2) {
              const flower = new THREE.Mesh(new THREE.DodecahedronGeometry(0.55), col);
              flower.position.set(180 + fx + (fl % 2) * 0.4, 0.85, fz + fl);
              avg.add(flower);
            }

            // Park benches along flowerbeds
            const bench = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.75, 2.4), islandTurfMat);
            bench.position.set(180 + fx + (fx > 0 ? 3.0 : -3.0), 0.38, fz);
            avg.add(bench);

            // Cast-iron heritage lamppost
            const lampPost = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, 4.2, 8), islandStoneMat);
            lampPost.position.set(180 + fx + (fx > 0 ? 1.8 : -1.8), 2.1, fz + 6);
            avg.add(lampPost);
            const lampHead = new THREE.Mesh(new THREE.SphereGeometry(0.35, 6, 6), islandGoldMat);
            lampHead.position.set(180 + fx + (fx > 0 ? 1.8 : -1.8), 4.3, fz + 6);
            avg.add(lampHead);
          });
        }

        // Franklin Children's Garden timber storybook arches
        for (let az = 1205; az <= 1225; az += 10) {
          const arch = new THREE.Mesh(new THREE.BoxGeometry(13.5, 0.6, 1.2), islandWoodMat);
          arch.position.set(180, 4.4, az);
          avg.add(arch);
          [-6.5, 6.5].forEach(ax => {
            const post = new THREE.Mesh(new THREE.BoxGeometry(0.6, 4.4, 0.6), islandWoodMat);
            post.position.set(180 + ax, 2.2, az);
            avg.add(post);
          });
        }

        centreIsland.add(avg);
      }

      // ---------- E. William Meany Hedge Maze (x: 48..122, z: 1150..1220) ----------
      {
        const hmg = new THREE.Group();
        // Entrance Archway
        const mGate = signMesh(['WILLIAM MEANY HEDGE MAZE', 'TORONTO ISLAND PARK • DONATED 2015'], 18, 2.4, { bg: '#14532d', fg: '#bbf7d0', borderColor: '#22c55e', size: 52 });
        mGate.position.set(85, 3.8, 1150);
        hmg.add(mGate);
        [-7.5, 7.5].forEach(gx => {
          const post = new THREE.Mesh(new THREE.BoxGeometry(0.8, 4.0, 0.8), islandWoodMat);
          post.position.set(85 + gx, 2.0, 1150);
          hmg.add(post);
        });

        // Helper to place a solid hedge wall block
        function addHedge(hx, hz, hw, hd) {
          const hedge = new THREE.Mesh(new THREE.BoxGeometry(hw, 2.1, hd), islandHedgeMat);
          hedge.position.set(hx, 1.05, hz);
          hmg.add(hedge);
          addSolid({
            type: 'poly',
            pts: [
              [hx - hw / 2, hz - hd / 2],
              [hx + hw / 2, hz - hd / 2],
              [hx + hw / 2, hz + hd / 2],
              [hx - hw / 2, hz + hd / 2]
            ],
            h: 2.1
          });
        }

        // 1. Outer perimeter hedge walls (with entrance gap at x = 85, z = 1150)
        addHedge(65, 1150, 32, 1.4);
        addHedge(105, 1150, 32, 1.4);
        addHedge(48, 1185, 1.4, 70);
        addHedge(122, 1185, 1.4, 70);
        addHedge(85, 1220, 74, 1.4);

        // 2. Ring 1 hedge walls
        addHedge(68, 1162, 28, 1.2);
        addHedge(102, 1162, 28, 1.2);
        addHedge(56, 1185, 1.2, 46);
        addHedge(114, 1185, 1.2, 46);
        addHedge(85, 1208, 58, 1.2);

        // 3. Ring 2 hedge walls
        addHedge(76, 1172, 22, 1.2);
        addHedge(94, 1172, 14, 1.2);
        addHedge(64, 1188, 1.2, 32);
        addHedge(106, 1188, 1.2, 32);
        addHedge(85, 1198, 42, 1.2);

        // 4. Ring 3 inner core maze walls & dead ends
        addHedge(74, 1182, 1.2, 18);
        addHedge(96, 1182, 1.2, 18);
        addHedge(85, 1176, 18, 1.2);

        // Central Court Observation Lookout Tower (x: 82..88, z: 1182..1188)
        const towerDeck = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.4, 6.4), islandWoodMat);
        towerDeck.position.set(85, 3.2, 1185);
        hmg.add(towerDeck);
        // 4 corner timber posts
        [[-2.8, -2.8], [2.8, -2.8], [-2.8, 2.8], [2.8, 2.8]].forEach(([px, pz]) => {
          const col = new THREE.Mesh(new THREE.BoxGeometry(0.4, 5.5, 0.4), islandWoodMat);
          col.position.set(85 + px, 2.75, 1185 + pz);
          hmg.add(col);
        });
        // Pitched roof canopy
        const towerRoof = new THREE.Mesh(new THREE.ConeGeometry(5.2, 2.2, 4), islandTurfMat);
        towerRoof.position.set(85, 6.4, 1185);
        towerRoof.rotation.y = Math.PI / 4;
        hmg.add(towerRoof);

        // Tower railings
        const tRail = new THREE.Mesh(new THREE.BoxGeometry(6.4, 0.85, 0.2), islandWoodMat);
        tRail.position.set(85, 3.8, 1182);
        hmg.add(tRail);

        // Lookout sign
        const lSign = signMesh(['MAZE LOOKOUT TOWER', 'BIRD’S-EYE VIEW OF WILLIAM MEANY MAZE'], 7.2, 1.1, { bg: '#78350f', fg: '#fef08a', borderColor: '#b45309', size: 44 });
        lSign.position.set(85, 4.4, 1182);
        hmg.add(lSign);

        centreIsland.add(hmg);
      }

      // ---------- F. Centreville Amusement Park (x: 230..420, z: 1130..1320) ----------
      {
        const cpg = new THREE.Group();
        // Entrance Archway
        const cGate = signMesh(['CENTREVILLE AMUSEMENT PARK', 'FAMILY FUN • OVER 30 RIDES & ATTRACTIONS'], 22, 2.8, { bg: '#dc2626', fg: '#fef08a', borderColor: '#facc15', size: 56 });
        cGate.position.set(245, 4.4, 1145);
        cpg.add(cGate);
        [-9.5, 9.5].forEach(gx => {
          const col = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.6, 4.8, 10), islandRedMat);
          col.position.set(245 + gx, 2.4, 1145);
          cpg.add(col);
        });

        // 1. Giant Animated Ferris Wheel at x = 330, z = 1185
        const fwGroup = new THREE.Group();
        const legL = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 1.1, 32, 8), islandStoneMat);
        legL.position.set(-6, 16, 0);
        const legR = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 1.1, 32, 8), islandStoneMat);
        legR.position.set(6, 16, 0);
        fwGroup.add(legL, legR);

        islandFerrisWheel = new THREE.Group();
        const rimOuter = new THREE.Mesh(new THREE.TorusGeometry(18, 0.75, 10, 32), islandGoldMat);
        const rimInner = new THREE.Mesh(new THREE.TorusGeometry(12, 0.5, 8, 28), islandCyanMat);
        islandFerrisWheel.add(rimOuter, rimInner);
        for (let s = 0; s < 16; s++) {
          const sa = (s / 16) * Math.PI * 2;
          const spoke = new THREE.Mesh(new THREE.BoxGeometry(36, 0.35, 0.35), islandWhiteMat);
          spoke.rotation.z = sa;
          islandFerrisWheel.add(spoke);
          const gondolaCols = [islandRedMat, islandGoldMat, islandCyanMat, islandOrangeMat];
          const gondola = new THREE.Mesh(new THREE.SphereGeometry(1.5, 8, 8), gondolaCols[s % 4]);
          gondola.position.set(Math.cos(sa) * 18, Math.sin(sa) * 18, 0);
          islandFerrisWheel.add(gondola);
        }
        islandFerrisWheel.position.set(0, 24, 0);
        fwGroup.add(islandFerrisWheel);
        fwGroup.position.set(330, 0, 1185);
        cpg.add(fwGroup);
        addSolid({ type: 'circle', x: 330, z: 1185, r: 8.5 });

        // 2. Vintage Carousel Pavilion at x = 270, z = 1160
        const carPav = new THREE.Group();
        // Octagonal Striped Circus Canopy
        const canopy = new THREE.Mesh(new THREE.ConeGeometry(10.5, 5.5, 8), islandRedMat);
        canopy.position.y = 8.0;
        carPav.add(canopy);
        const canopyFinial = new THREE.Mesh(new THREE.SphereGeometry(0.9, 8, 8), islandGoldMat);
        canopyFinial.position.y = 11.2;
        carPav.add(canopyFinial);

        // Carousel Floor Platform
        const carFloor = new THREE.Mesh(new THREE.CylinderGeometry(9.5, 9.8, 0.8, 16), islandStoneMat);
        carFloor.position.y = 0.4;
        carPav.add(carFloor);

        // Rotating Carousel Core & Horses
        islandCarouselCore = new THREE.Group();
        const coreCol = new THREE.Mesh(new THREE.CylinderGeometry(2.5, 2.5, 6.5, 12), islandGoldMat);
        coreCol.position.y = 4.0;
        islandCarouselCore.add(coreCol);

        // 12 Carved Carousel Horses on Brass Poles
        for (let hi = 0; hi < 12; hi++) {
          const ha = (hi / 12) * Math.PI * 2;
          const hr = hi % 2 === 0 ? 5.5 : 7.8;
          const hx = Math.cos(ha) * hr, hz = Math.sin(ha) * hr;
          const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 6.2, 6), islandGoldMat);
          pole.position.set(hx, 3.8, hz);
          islandCarouselCore.add(pole);

          const horse = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 2.2), hi % 2 === 0 ? islandWhiteMat : islandOrangeMat);
          horse.position.set(hx, 2.4 + (hi % 2) * 0.4, hz);
          horse.rotation.y = ha + Math.PI / 2;
          islandCarouselCore.add(horse);
        }
        carPav.add(islandCarouselCore);
        carPav.position.set(270, 0, 1160);
        cpg.add(carPav);
        addSolid({ type: 'circle', x: 270, z: 1160, r: 9.8 });

        // 3. PIZZA PIZZA CONCESSION STAND & DINING PATIO (x = 240, z = 1220)
        const ppBuilding = new THREE.Group();
        // Orange & White Storefront
        const ppWalls = new THREE.Mesh(new THREE.BoxGeometry(16, 5.0, 9.0), islandOrangeMat);
        ppWalls.position.set(240, 2.5, 1220);
        ppBuilding.add(ppWalls);

        const ppTrim = new THREE.Mesh(new THREE.BoxGeometry(16.4, 0.6, 9.4), islandWhiteMat);
        ppTrim.position.set(240, 5.2, 1220);
        ppBuilding.add(ppTrim);

        // Rooftop Glowing Marquee Sign
        const ppSign = signMesh(['PIZZA PIZZA', 'FRESH HOT SLICES • WHOLE PIZZAS • POUTINE'], 15, 2.2, { bg: '#c2410c', fg: '#ffedd5', borderColor: '#fdba74', size: 54 });
        ppSign.position.set(240, 6.6, 1215.3);
        ppBuilding.add(ppSign);

        // Order Counter with Stainless Steel Sneeze Guards & Warmer Displays
        const ppCounter = new THREE.Mesh(new THREE.BoxGeometry(12, 1.1, 1.6), islandStoneMat);
        ppCounter.position.set(240, 0.55, 1215.2);
        ppBuilding.add(ppCounter);

        const ppMenu = signMesh(['PEPPERONI SLICE $4.99 • CHEESE $4.79 • DIP $1.25', 'WHOLE PIZZA $19.99 • POUTINE • DRINKS'], 11, 1.2, { bg: '#1c1917', fg: '#fef08a', borderColor: '#f97316', size: 36 });
        ppMenu.position.set(240, 3.2, 1215.3);
        ppBuilding.add(ppMenu);

        // Pizza slices in warm glowing display
        for (let pi = -4; pi <= 4; pi += 2.2) {
          const slice = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.12, 3), islandGoldMat);
          slice.position.set(240 + pi, 1.2, 1215.2);
          ppBuilding.add(slice);
        }

        // Outdoor Dining Patio: 6 Picnic Tables with Umbrellas
        const patioSpots = [
          [228, 1208], [236, 1208], [244, 1208], [252, 1208],
          [232, 1200], [248, 1200]
        ];
        patioSpots.forEach(([tx, tz]) => {
          // Table
          const table = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.8, 12), islandWoodMat);
          table.position.set(tx, 0.4, tz);
          ppBuilding.add(table);
          // Umbrella
          const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.8, 6), islandStoneMat);
          pole.position.set(tx, 1.4, tz);
          ppBuilding.add(pole);
          const umbrella = new THREE.Mesh(new THREE.ConeGeometry(2.0, 0.7, 8), islandRedMat);
          umbrella.position.set(tx, 2.7, tz);
          ppBuilding.add(umbrella);
          // Bench seats around table
          for (let si = 0; si < 4; si++) {
            const sa = (si / 4) * Math.PI * 2;
            const seat = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.45, 0.6), islandTurfMat);
            seat.position.set(tx + Math.cos(sa) * 1.8, 0.22, tz + Math.sin(sa) * 1.8);
            ppBuilding.add(seat);
          }
        });

        // Recycling and waste bins
        const trash1 = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.4, 1.1, 10), islandRedMat);
        trash1.position.set(248, 0.55, 1212);
        const trash2 = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.4, 1.1, islandCyanMat.color.getHex()), islandCyanMat);
        trash2.position.set(250, 0.55, 1212);
        ppBuilding.add(trash1, trash2);

        cpg.add(ppBuilding);
        addSolid({
          type: 'poly',
          pts: [
            [232, 1215], [248, 1215],
            [248, 1225], [232, 1225]
          ],
          h: 5.0
        });

        // 4. Centreville Express Miniature Train Depot at x = 360, z = 1240
        const depot = new THREE.Group();
        const dBuilding = new THREE.Mesh(new THREE.BoxGeometry(14, 4.5, 8), islandWoodMat);
        dBuilding.position.set(360, 2.25, 1240);
        depot.add(dBuilding);
        const dRoof = new THREE.Mesh(new THREE.BoxGeometry(15, 0.8, 9.5), islandTurfMat);
        dRoof.position.set(360, 4.7, 1240);
        depot.add(dRoof);
        const dSign = signMesh(['CENTREVILLE EXPRESS', 'MINIATURE RAILROAD DEPOT'], 12, 1.6, { bg: '#14532d', fg: '#fef08a', borderColor: '#22c55e', size: 48 });
        dSign.position.set(360, 3.6, 1235.8);
        depot.add(dSign);

        // Train tracks
        const railL = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 45), railSteelMat);
        railL.position.set(353, 0.1, 1240);
        const railR = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 45), railSteelMat);
        railR.position.set(355, 0.1, 1240);
        depot.add(railL, railR);
        cpg.add(depot);
        addSolid({ type: 'poly', pts: [[353, 1236], [367, 1236], [367, 1244], [353, 1244]], h: 4.5 });

        // 5. Carnival Game Booths at x = 300, z = 1220
        const gameBooths = new THREE.Group();
        const bNames = ['BALLOON POP', 'RING TOSS', 'LUCKY DUCK'];
        bNames.forEach((bn, bi) => {
          const bx = 290 + bi * 10;
          const booth = new THREE.Mesh(new THREE.BoxGeometry(7.5, 3.5, 4.5), islandWoodMat);
          booth.position.set(bx, 1.75, 1220);
          gameBooths.add(booth);
          const bRoof = new THREE.Mesh(new THREE.ConeGeometry(5.2, 1.8, 4), [islandRedMat, islandGoldMat, islandCyanMat][bi]);
          bRoof.position.set(bx, 4.2, 1220);
          bRoof.rotation.y = Math.PI / 4;
          gameBooths.add(bRoof);
          const bSign = signMesh([bn, 'WIN PRIZES!'], 6.5, 0.9, { bg: '#dc2626', fg: '#fef08a', borderColor: '#facc15', size: 40 });
          bSign.position.set(bx, 3.2, 1217.6);
          gameBooths.add(bSign);
        });
        cpg.add(gameBooths);

        // 6. Swan Pedal Boats floating in Centreville Lagoon Cove (x: 280, z: 1260)
        const swanSpots = [[275, 1262], [285, 1262], [275, 1272], [285, 1272]];
        swanSpots.forEach(([sx, sz]) => {
          const swan = new THREE.Group();
          const sBody = new THREE.Mesh(new THREE.BoxGeometry(2.4, 0.8, 3.2), islandWhiteMat);
          sBody.position.y = 0.4;
          swan.add(sBody);
          const sNeck = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.25, 2.2, 8), islandWhiteMat);
          sNeck.position.set(0, 1.3, -1.2);
          sNeck.rotation.x = -0.3;
          swan.add(sNeck);
          const sHead = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 8), islandWhiteMat);
          sHead.position.set(0, 2.3, -1.5);
          swan.add(sHead);
          const sBeak = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.6, 6), islandOrangeMat);
          sBeak.rotation.x = -Math.PI / 2;
          sBeak.position.set(0, 2.2, -1.9);
          swan.add(sBeak);
          swan.position.set(sx, WATER_Y, sz);
          cpg.add(swan);
        });

        centreIsland.add(cpg);
      }

      // ---------- G. Centre Island Beach & Lake Ontario South Shore (z: 1375..1490) ----------
      {
        const bg = new THREE.Group();
        // 1. Cedar Beach Boardwalk running along z = 1380
        const boardwalk = new THREE.Mesh(new THREE.BoxGeometry(480, 0.35, 3.8), islandBoardwalkMat);
        boardwalk.position.set(180, 0.18, 1380);
        bg.add(boardwalk);

        // 2. Lifeguard Watchtower at x = 220, z = 1420
        const lgTower = new THREE.Group();
        // 4 wooden stilts
        [[-1.8, -1.8], [1.8, -1.8], [-1.8, 1.8], [1.8, 1.8]].forEach(([lx, lz]) => {
          const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.22, 5.5, 8), islandWoodMat);
          leg.position.set(lx, 2.75, lz);
          lgTower.add(leg);
        });
        const lgCabin = new THREE.Mesh(new THREE.BoxGeometry(4.2, 2.6, 4.2), islandWhiteMat);
        lgCabin.position.y = 5.8;
        lgTower.add(lgCabin);
        const lgRoof = new THREE.Mesh(new THREE.ConeGeometry(3.6, 1.4, 4), islandRedMat);
        lgRoof.position.y = 7.6;
        lgRoof.rotation.y = Math.PI / 4;
        lgTower.add(lgRoof);
        const lgSign = signMesh(['LIFEGUARD STATION 4', 'CENTRE ISLAND BEACH'], 3.6, 0.8, { bg: '#b91c1c', fg: '#fef08a', borderColor: '#ef4444', size: 42 });
        lgSign.position.set(0, 6.2, 2.15);
        lgTower.add(lgSign);
        lgTower.position.set(220, 0, 1420);
        bg.add(lgTower);

        // 3. Beach Volleyball Court at x = 120, z = 1420
        const vbCourt = new THREE.Group();
        const net = new THREE.Mesh(new THREE.BoxGeometry(9.5, 1.1, 0.08), islandWhiteMat);
        net.position.set(0, 2.0, 0);
        vbCourt.add(net);
        [-4.8, 4.8].forEach(px => {
          const post = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 2.8, 6), islandWoodMat);
          post.position.set(px, 1.4, 0);
          vbCourt.add(post);
        });
        const ball = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 8), islandGoldMat);
        ball.position.set(1.5, 0.3, 2.0);
        vbCourt.add(ball);
        vbCourt.position.set(120, 0, 1420);
        bg.add(vbCourt);

        // 4. Colorful Rainbow Beach Umbrellas & Lounge Towels
        const beachSpots = [
          [80, 1405], [100, 1435], [140, 1410], [160, 1440],
          [200, 1405], [240, 1435], [260, 1410], [280, 1440]
        ];
        beachSpots.forEach(([bx, bz], bi) => {
          const uPole = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.6, 6), islandWhiteMat);
          uPole.position.set(bx, 1.3, bz);
          uPole.rotation.z = (bi % 2 === 0 ? 0.1 : -0.1);
          bg.add(uPole);

          const uCap = new THREE.Mesh(new THREE.ConeGeometry(2.1, 0.8, 8), [islandRedMat, islandGoldMat, islandCyanMat, islandOrangeMat][bi % 4]);
          uCap.position.set(bx, 2.5, bz);
          uCap.rotation.z = (bi % 2 === 0 ? 0.1 : -0.1);
          bg.add(uCap);

          // Beach towel on sand
          const towel = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.05, 2.2), [islandCyanMat, islandOrangeMat, islandFlowerPurple, islandRedMat][bi % 4]);
          towel.position.set(bx + 1.2, 0.05, bz + 0.8);
          bg.add(towel);
        });

        // 5. Heavy Stone Breakwater Jetty into Lake Ontario (x: 175..185, z: 1380..1475)
        const breakwater = new THREE.Group();
        const jettyDeck = new THREE.Mesh(new THREE.BoxGeometry(9.0, 1.2, 95), islandStoneMat);
        jettyDeck.position.set(180, 0.6, 1427.5);
        breakwater.add(jettyDeck);

        // Riprap boulders on both sides
        for (let bz = 1382; bz <= 1472; bz += 8) {
          [-5.2, 5.2].forEach(rx => {
            const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.4), islandStoneMat);
            rock.position.set(180 + rx, 0.4, bz);
            breakwater.add(rock);
          });
        }

        // Binocular viewing station at the end of the jetty overlooking Lake Ontario
        const binoPost = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.22, 1.5, 8), islandStoneMat);
        binoPost.position.set(180, 1.35, 1472);
        breakwater.add(binoPost);
        const binoHead = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.35, 0.85), islandCyanMat);
        binoHead.position.set(180, 2.1, 1472);
        breakwater.add(binoHead);

        const binoSign = signMesh(['LAKE ONTARIO OVERLOOK', 'LOOKING 180 MILES SOUTH TO ROCHESTER, NY'], 8.5, 1.2, { bg: '#0c4a6e', fg: '#e0f2fe', borderColor: '#38bdf8', size: 40 });
        binoSign.position.set(180, 2.9, 1471);
        breakwater.add(binoSign);

        bg.add(breakwater);
        centreIsland.add(bg);
      }

      // ---------- H. Olympic Island & Western Meadows (x = -60, z = 1240) ----------
      {
        const oig = new THREE.Group();
        // Wooden Picnic Shelters
        [[-80, 1180], [-80, 1280]].forEach(([px, pz]) => {
          const shelter = new THREE.Mesh(new THREE.BoxGeometry(16, 0.6, 10), islandWoodMat);
          shelter.position.set(px, 3.8, pz);
          oig.add(shelter);
          // 4 posts
          [[-7, -4], [7, -4], [-7, 4], [7, 4]].forEach(([sx, sz]) => {
            const post = new THREE.Mesh(new THREE.BoxGeometry(0.4, 3.8, 0.4), islandWoodMat);
            post.position.set(px + sx, 1.9, pz + sz);
            oig.add(post);
          });
          // Picnic tables inside
          [-3.5, 3.5].forEach(tx => {
            const pTable = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.75, 4.5), islandWoodMat);
            pTable.position.set(px + tx, 0.38, pz);
            oig.add(pTable);
          });
        });

        // Panoramic Skyline Viewing Bench Area
        const benchSign = signMesh(['TORONTO SKYLINE LOOKOUT', 'UNOBSTRUCTED VIEW OF CN TOWER & FINANCIAL DISTRICT'], 14, 1.8, { bg: '#0f172a', fg: '#fde047', borderColor: '#38bdf8', size: 48 });
        benchSign.position.set(-80, 3.2, 1120);
        benchSign.rotation.y = Math.PI;
        oig.add(benchSign);

        centreIsland.add(oig);
      }

      // ---------- I. Weeping Willows & Island Trees ----------
      {
        const treesGroup = new THREE.Group();
        // 1. Weeping Willows along Long Pond Lagoon banks
        for (let wx = -100; wx <= 380; wx += 24) {
          // Avoid bridge crossings at x=10, 180, 240
          if (Math.abs(wx - 10) < 14 || Math.abs(wx - 180) < 16 || Math.abs(wx - 240) < 16) continue;
          [1236, 1260].forEach((wz, wi) => {
            const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.75, 7.0, 8), islandWoodMat);
            trunk.position.set(wx, 3.5, wz);
            trunk.rotation.z = (wi === 0 ? 0.12 : -0.12);
            treesGroup.add(trunk);

            // Drooping weeping willow canopy
            const canopy = new THREE.Mesh(new THREE.ConeGeometry(4.8, 8.5, 8), islandTreeMat1);
            canopy.position.set(wx, 8.0, wz);
            treesGroup.add(canopy);
          });
        }

        // 2. Sugar Maples & Oaks across lawns
        for (let ti = 0; ti < 48; ti++) {
          const tx = -140 + hash(ti * 4.3 + 1) * 600;
          const tz = 1080 + hash(ti * 7.1 + 3) * 380;
          // Avoid placing in lagoon, maze or amusement park
          if (tz >= 1230 && tz <= 1265) continue;
          if (tx >= 45 && tx <= 125 && tz >= 1145 && tz <= 1225) continue;
          if (tx >= 230 && tx <= 380 && tz >= 1140 && tz <= 1250) continue;
          if (Math.abs(tx - 180) < 14) continue; // Avenue promenade

          const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.55, 6.0, 8), islandWoodMat);
          trunk.position.set(tx, 3.0, tz);
          treesGroup.add(trunk);

          const crown = new THREE.Mesh(new THREE.DodecahedronGeometry(3.6 + hash(ti) * 2.2), ti % 2 === 0 ? islandTreeMat1 : islandTreeMat2);
          crown.position.set(tx, 7.5, tz);
          treesGroup.add(crown);
        }

        centreIsland.add(treesGroup);
      }

      // ---------- J. Gibraltar Point Lighthouse (historic 1808 lighthouse at x = -180, z = 1340) ----------
      {
        const lhGroup = new THREE.Group();
        const lhTower = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 5.2, 34, 8), islandStoneMat);
        lhTower.position.y = 17;
        lhGroup.add(lhTower);
        const lhLantern = new THREE.Mesh(new THREE.CylinderGeometry(3.6, 3.6, 4.8, 10), islandRedMat);
        lhLantern.position.y = 36;
        lhGroup.add(lhLantern);
        const lhRoof = new THREE.Mesh(new THREE.ConeGeometry(4.2, 3.5, 10), islandRedMat);
        lhRoof.position.y = 40;
        lhGroup.add(lhRoof);
        lighthouseBeam = new THREE.Group();
        const beamCone = new THREE.Mesh(
          new THREE.ConeGeometry(9.5, 75, 12, 1, true),
          new THREE.MeshBasicMaterial({ color: 0xfef08a, transparent: true, opacity: 0.38, side: THREE.DoubleSide, depthWrite: false, fog: false })
        );
        beamCone.rotation.z = Math.PI / 2;
        beamCone.position.x = 38;
        lighthouseBeam.add(beamCone);
        lighthouseBeam.position.y = 36;
        lhGroup.add(lighthouseBeam);

        const lhSign = signMesh(['GIBRALTAR POINT LIGHTHOUSE', 'OLDEST LANDMARK IN TORONTO • BUILT 1808'], 12, 1.8, { bg: '#450a0a', fg: '#fef08a', borderColor: '#ef4444', size: 44 });
        lhSign.position.set(0, 4.2, 5.6);
        lhGroup.add(lhSign);

        lhGroup.position.set(-180, 0, 1340);
        centreIsland.add(lhGroup);
        addSolid({ type: 'circle', x: -180, z: 1340, r: 5.5 });
      }
'''

content = CITY_JS.read_text(encoding='utf-8')

# Target lines 9695-9756:
# Find '// 2. Centre Island & Hanlan\'s Point' through 'centreIsland.add(lhGroup);\n      }'
pattern = r'      // 2\. Centre Island & Hanlan\'s Point \(x = 180, z = 1220\)[\s\S]*?centreIsland\.add\(lhGroup\);\s*\n\s*}'

match = re.search(pattern, content)
if not match:
    print("ERROR: Pattern not found in city.js!")
    exit(1)

new_content = content[:match.start()] + centre_island_code + content[match.end():]
CITY_JS.write_text(new_content, encoding='utf-8')
print("Successfully replaced Centre Island section in city.js!")

