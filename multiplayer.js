// ============================================================================
// FISTS OF DOOM: TORONTO — MULTIPLAYER SQUAD & BRAWL CLIENT
// Handles real-time WebSockets, remote player avatar rendering, smooth interpolation,
// and synchronized PvP combat / co-op defense.
// ============================================================================
(function () {
  'use strict';

  // Configurable Cloud Server (Render.com free tier or custom)
  const CLOUD_SERVER_URL = 'wss://toronto-defender.onrender.com';
  
  function getAutoServerUrl() {
    // 1. Check URL query parameters: e.g. ?server=wss://...
    const urlParams = new URLSearchParams(window.location.search);
    const queryServer = urlParams.get('server');
    if (queryServer) return queryServer;

    // 2. Check localStorage saved server
    const savedServer = localStorage.getItem('toronto_mp_server');
    if (savedServer) return savedServer;

    // 3. Served by the relay itself (localhost, LAN IP, my-mac.local, Render...): same origin.
    //    Only static hosts that can't run the relay (GitHub Pages, file://) use the cloud default.
    const host = window.location.host;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    if (window.location.protocol === 'file:' || !host || host.endsWith('github.io')) {
      return CLOUD_SERVER_URL;
    }
    return `${protocol}//${host}/ws`;
  }

  function getAutoRoom() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('room') || localStorage.getItem('toronto_mp_room') || '6ix';
  }

  function getSavedPlayerName() {
    let name = localStorage.getItem('toronto_mp_name');
    if (!name) {
      const heroes = ['DEFENDER', 'SIX-HERO', 'BRAWLER', 'NORTH-KNIGHT', 'MAPLE-FIST', 'TORONTO-APEX'];
      name = heroes[Math.floor(Math.random() * heroes.length)] + '-' + Math.floor(10 + Math.random() * 89);
      localStorage.setItem('toronto_mp_name', name);
    }
    return name;
  }

  // --- 3D Hero Avatar Builder for Remote Players ---
  function createRemoteHeroRig(name, colorHex) {
    const root = new THREE.Group();
    const color = colorHex || 0xef4444;

    const skinMat = new THREE.MeshStandardMaterial({ color: 0xdfad7b, roughness: 0.65, metalness: 0.05 });
    const vestMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.45, metalness: 0.25 });
    const pantsMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6, metalness: 0.1 });
    const wrapMat = new THREE.MeshStandardMaterial({ color: color, roughness: 0.35, metalness: 0.5 });
    const bootMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7, metalness: 0.2 });
    const hairMat = new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.9, metalness: 0.0 });
    const flashableMaterials = [skinMat, vestMat, pantsMat, wrapMat, bootMat];

    // Pelvis
    const pelvis = new THREE.Group();
    pelvis.position.set(0, 0.9, 0);
    root.add(pelvis);
    const hips = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.22, 0.3), pantsMat);
    hips.castShadow = true;
    pelvis.add(hips);
    const belt = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.07, 0.32), new THREE.MeshStandardMaterial({ color: 0x09090b, metalness: 0.6 }));
    belt.position.set(0, 0.08, 0);
    pelvis.add(belt);

    // Legs
    const leftLeg = new THREE.Group();
    leftLeg.position.set(-0.16, 0.82, 0);
    root.add(leftLeg);
    const lThigh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.42, 0.2), pantsMat);
    lThigh.position.set(0, -0.2, 0); lThigh.castShadow = true; leftLeg.add(lThigh);
    const lCalfPivot = new THREE.Group();
    lCalfPivot.position.set(0, -0.4, 0); leftLeg.add(lCalfPivot);
    const lCalf = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.4, 0.18), pantsMat);
    lCalf.position.set(0, -0.2, 0); lCalf.castShadow = true; lCalfPivot.add(lCalf);
    const lBoot = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.16, 0.26), bootMat);
    lBoot.position.set(0, -0.38, 0.04); lBoot.castShadow = true; lCalfPivot.add(lBoot);

    const rightLeg = new THREE.Group();
    rightLeg.position.set(0.16, 0.82, 0);
    root.add(rightLeg);
    const rThigh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.42, 0.2), pantsMat);
    rThigh.position.set(0, -0.2, 0); rThigh.castShadow = true; rightLeg.add(rThigh);
    const rCalfPivot = new THREE.Group();
    rCalfPivot.position.set(0, -0.4, 0); rightLeg.add(rCalfPivot);
    const rCalf = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.4, 0.18), pantsMat);
    rCalf.position.set(0, -0.2, 0); rCalf.castShadow = true; rCalfPivot.add(rCalf);
    const rBoot = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.16, 0.26), bootMat);
    rBoot.position.set(0, -0.38, 0.04); rBoot.castShadow = true; rCalfPivot.add(rBoot);

    // Torso
    const torso = new THREE.Group();
    torso.position.set(0, 0.98, 0);
    root.add(torso);
    const chest = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.54, 0.32), vestMat);
    chest.position.set(0, 0.27, 0); chest.castShadow = true; torso.add(chest);

    // Head
    const headPivot = new THREE.Group();
    headPivot.position.set(0, 0.68, 0);
    torso.add(headPivot);
    const head = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.32, 0.28), skinMat);
    head.position.set(0, 0.16, 0); head.castShadow = true; headPivot.add(head);

    // Eyes
    const eyeWhite = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const eyePupil = new THREE.MeshBasicMaterial({ color: 0x0284c7 });
    [-0.07, 0.07].forEach(ex => {
      const ew = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.02), eyeWhite);
      ew.position.set(ex, 0.18, 0.142); headPivot.add(ew);
      const ep = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.04, 0.022), eyePupil);
      ep.position.set(ex, 0.18, 0.144); headPivot.add(ep);
    });
    // Hair cap
    const buzz = new THREE.Mesh(new THREE.BoxGeometry(0.29, 0.08, 0.29), hairMat);
    buzz.position.set(0, 0.32, 0); headPivot.add(buzz);

    // Arms
    const lArmPivot = new THREE.Group();
    lArmPivot.position.set(-0.35, 0.48, 0); torso.add(lArmPivot);
    const lBicep = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.3, 0.16), skinMat);
    lBicep.position.set(0, -0.15, 0); lArmPivot.add(lBicep);
    const lForearm = new THREE.Group();
    lForearm.position.set(0, -0.3, 0); lArmPivot.add(lForearm);
    const lLower = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.28, 0.15), skinMat);
    lLower.position.set(0, -0.14, 0); lForearm.add(lLower);
    const lFist = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 0.2), wrapMat);
    lFist.position.set(0, -0.3, 0.02); lForearm.add(lFist);

    const rArmPivot = new THREE.Group();
    rArmPivot.position.set(0.35, 0.48, 0); torso.add(rArmPivot);
    const rBicep = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.3, 0.16), skinMat);
    rBicep.position.set(0, -0.15, 0); rArmPivot.add(rBicep);
    const rForearm = new THREE.Group();
    rForearm.position.set(0, -0.3, 0); rArmPivot.add(rForearm);
    const rLower = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.28, 0.15), skinMat);
    rLower.position.set(0, -0.14, 0); rForearm.add(rLower);
    const rFist = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 0.2), wrapMat);
    rFist.position.set(0, -0.3, 0.02); rForearm.add(rFist);

    // Canadian Hockey Stick for Berserk Mode (hidden by default)
    const stickMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.04, 0.95, 0.03),
      new THREE.MeshStandardMaterial({ color: 0xd90429, roughness: 0.4 })
    );
    stickMesh.position.set(0.08, -0.1, 0.15);
    stickMesh.rotation.set(-0.4, 0.2, -0.3);
    stickMesh.visible = false;
    rForearm.add(stickMesh);

    // 3D Billboard Nameplate & Live Health Bar
    const npCanvas = document.createElement('canvas');
    npCanvas.width = 256; npCanvas.height = 72;
    const npCtx = npCanvas.getContext('2d');
    const npTex = new THREE.CanvasTexture(npCanvas);
    npTex.minFilter = THREE.LinearFilter;
    const npMat = new THREE.SpriteMaterial({ map: npTex, depthTest: false, transparent: true });
    const nameplate = new THREE.Sprite(npMat);
    nameplate.scale.set(1.9, 0.54, 1);
    nameplate.position.set(0, 2.2, 0);
    root.add(nameplate);

    function updateNameplate(playerName, hp = 100, isBerserk = false) {
      npCtx.clearRect(0, 0, 256, 72);
      npCtx.fillStyle = 'rgba(10, 15, 24, 0.92)';
      if (npCtx.roundRect) {
        npCtx.beginPath();
        npCtx.roundRect(6, 6, 244, 60, 8);
        npCtx.fill();
      } else {
        npCtx.fillRect(6, 6, 244, 60);
      }

      const hexStr = '#' + (color.toString(16).padStart(6, '0'));
      npCtx.strokeStyle = isBerserk ? '#ff0033' : hexStr;
      npCtx.lineWidth = 3.5;
      npCtx.stroke();

      npCtx.font = 'bold 20px "Chakra Petch", Arial, sans-serif';
      npCtx.fillStyle = isBerserk ? '#ff3b4a' : '#ffffff';
      npCtx.textAlign = 'center';
      const label = (isBerserk ? '🍁 ' : '⭐ ') + playerName.toUpperCase();
      npCtx.fillText(label, 128, 30);

      // Health bar
      const barX = 18, barY = 40, barW = 220, barH = 14;
      npCtx.fillStyle = '#0a0a0c';
      npCtx.fillRect(barX, barY, barW, barH);
      const fillW = Math.max(0, Math.min(1, hp / 100)) * barW;
      npCtx.fillStyle = isBerserk ? '#ff1e27' : (hp > 30 ? hexStr : '#ef4444');
      npCtx.fillRect(barX, barY, fillW, barH);

      npTex.needsUpdate = true;
    }
    updateNameplate(name, 100, false);

    return {
      root,
      leftLeg, lCalfPivot,
      rightLeg, rCalfPivot,
      torso, headPivot,
      lArmPivot, lForearm,
      rArmPivot, rForearm,
      stickMesh,
      nameplate,
      updateNameplate,
      materials: flashableMaterials,
      originalColors: flashableMaterials.map(m => m.color.getHex())
    };
  }

  // --- Multiplayer Controller Class ---
  // Roles: the server names one HOST per room. The host's game runs the robots, snatchers
  // and civilians and streams them ("world"); guests render those and send hits back.
  // A player alone in a room (or offline) is effectively host of their own game.
  class MultiplayerClient {
    constructor() {
      this.ws = null;
      this.connected = false;
      this.connecting = false;
      this.localId = null;
      this.hostId = null;
      this.role = 'solo';            // 'solo' | 'host' | 'guest'
      this.localName = getSavedPlayerName();
      this.localColor = 0xef4444;
      this.room = getAutoRoom();
      this.serverUrl = getAutoServerUrl();
      this.scene = null;
      this.localPlayer = null;
      this.gameState = null;
      this.remotePlayers = new Map();
      this.sendTimer = 0;
      this.worldTimer = 0;
      this.reconnectTimer = null;
      this.reconnectAttempts = 0;
      this.friendlyFire = false;     // ROOM setting, owned by the server
    }

    init(scene, player, state) {
      this.scene = scene;
      this.localPlayer = player;
      this.gameState = state;
      this.initUI();
      this.updateHUDStatus('connecting');
      this.connect();
    }

    isGuest() { return this.role === 'guest'; }
    isHostWithPeers() { return this.role === 'host' && this.remotePlayers.size > 0; }

    socketUrl(base) {
      try {
        const u = new URL(base);
        u.searchParams.set('room', this.room);
        u.searchParams.set('name', this.localName);
        return u.toString();
      } catch (e) {
        const sep = base.includes('?') ? '&' : '?';
        return `${base}${sep}room=${encodeURIComponent(this.room)}&name=${encodeURIComponent(this.localName)}`;
      }
    }

    connect(overrideUrl) {
      if (this.reconnectTimer) { clearTimeout(this.reconnectTimer); this.reconnectTimer = null; }
      if (this.ws) {
        // Detach the old socket completely so its late onclose can't clobber the new one
        const old = this.ws;
        old.onopen = old.onmessage = old.onerror = old.onclose = null;
        try { old.close(); } catch (e) {}
        this.ws = null;
        this.connected = false;
        this.removeAllRemotePlayers();
        this.setRole('solo');
      }
      if (overrideUrl) this.serverUrl = overrideUrl;
      this.connecting = true;
      this.updateHUDStatus('connecting');
      const url = this.socketUrl(this.serverUrl);
      console.log(`[Multiplayer] Connecting to ${url} ...`);
      let ws;
      try {
        ws = new WebSocket(url);
      } catch (err) {
        console.warn('[Multiplayer] Failed to create WebSocket:', err);
        this.onConnectionFailed();
        return;
      }
      this.ws = ws;
      ws.onopen = () => {
        if (this.ws !== ws) return;
        this.connected = true;
        this.connecting = false;
        this.reconnectAttempts = 0;
      };
      ws.onmessage = (event) => {
        if (this.ws !== ws) return;
        let msg;
        try { msg = JSON.parse(event.data); } catch (e) { return; }
        try { this.handleMessage(msg); } catch (e) { console.warn('[Multiplayer] handler error', msg && msg.type, e); }
      };
      ws.onerror = (err) => { if (this.ws === ws) console.warn('[Multiplayer] WebSocket error'); };
      ws.onclose = (ev) => {
        if (this.ws !== ws) return;
        console.log(`[Multiplayer] socket closed (code ${ev && ev.code}); will retry`);
        this.ws = null;
        this.connected = false;
        this.connecting = false;
        this.removeAllRemotePlayers();
        this.setRole('solo');
        this.updateHUDStatus('offline');
        this.scheduleReconnect();
      };
    }

    scheduleReconnect() {
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
      this.reconnectAttempts++;
      const delay = Math.min(15000, 2000 + this.reconnectAttempts * 2000);
      this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null;
        if (!this.connected && !this.connecting) this.connect();
      }, delay);
    }

    onConnectionFailed() {
      this.connected = false;
      this.connecting = false;
      this.updateHUDStatus('offline');
      this.scheduleReconnect();
    }

    send(data) {
      if (this.ws && this.connected && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify(data));
      }
    }

    // ---- role changes drive the NPC ownership hand-off in game.js ----
    setRole(role) {
      if (role === this.role) return;
      const prev = this.role;
      this.role = role;
      console.log(`[Multiplayer] role ${prev} -> ${role}`);
      if (role === 'guest') {
        if (window.netBecomeGuest) window.netBecomeGuest();
      } else if (prev === 'guest') {
        if (window.netBecomeHost) window.netBecomeHost();
      }
      this.updateHUDStatus(this.connected ? 'connected' : 'offline');
    }

    refreshRole() {
      if (!this.connected || !this.localId) { this.setRole('solo'); return; }
      this.setRole(this.hostId === this.localId ? 'host' : 'guest');
    }

    handleMessage(msg) {
      switch (msg.type) {
        case 'welcome': {
          this.localId = msg.id;
          this.hostId = msg.hostId;
          if (msg.color !== undefined) this.localColor = msg.color;
          this.applyMode(!!msg.pvp, null);
          (msg.players || []).forEach(p => { if (p.id !== this.localId) this.addRemotePlayer(p); });
          this.refreshRole();
          this.updateHUDStatus('connected');
          if (window.showAnnouncement && this.role === 'guest') {
            const host = this.remotePlayers.get(this.hostId);
            window.showAnnouncement(`🤝 JOINED ${host ? host.name.toUpperCase() : 'THE SQUAD'}'S TORONTO!`, 2500);
          }
          break;
        }
        case 'host':
          this.hostId = msg.hostId;
          this.refreshRole();
          if (this.role === 'host' && window.showAnnouncement) window.showAnnouncement('👑 YOU ARE NOW RUNNING THE CITY', 2200);
          break;
        case 'mode':
          this.applyMode(!!msg.pvp, msg.by);
          break;
        case 'player_joined': {
          const p = msg.player;
          if (p && p.id !== this.localId) {
            this.addRemotePlayer(p);
            if (window.showAnnouncement) window.showAnnouncement(`⭐ ${String(p.name).toUpperCase()} JOINED THE SQUAD! ⭐`, 2500);
          }
          this.updateHUDStatus('connected');
          break;
        }
        case 'player_updated': {
          const p = msg.player;
          const rp = p && this.remotePlayers.get(p.id);
          if (rp) {
            rp.name = p.name;
            if (rp.rig) rp.rig.updateNameplate(rp.name, rp.health, rp.isBerserk);
          }
          break;
        }
        case 'state': {
          const rp = this.remotePlayers.get(msg.id);
          if (!rp) break;
          if (msg.x !== undefined) rp.targetPos.set(msg.x, msg.y, msg.z);
          rp.targetYaw = msg.yaw || 0;
          rp.anim = msg.anim || 'idle';
          const hp = (msg.health !== undefined) ? msg.health : rp.health;
          const berserk = !!msg.isBerserk;
          if (rp.rig && (hp !== rp.health || berserk !== rp.isBerserk)) {
            rp.rig.updateNameplate(rp.name, hp, berserk);
            if (rp.rig.stickMesh) rp.rig.stickMesh.visible = berserk;
          }
          rp.health = hp;
          rp.isBerserk = berserk;
          rp.armor = (msg.armor !== undefined) ? msg.armor : rp.armor;
          break;
        }
        case 'attack': {
          const rp = this.remotePlayers.get(msg.id);
          if (rp) this.triggerRemoteAttackAnim(rp, msg.attackType || 'punch');
          break;
        }
        case 'hit':
          this.handleIncomingHit(msg);
          break;
        case 'ko':
          if (window.showAnnouncement) window.showAnnouncement(`⚡ ${msg.killerName || 'PLAYER'} KO'D ${msg.victimName || 'PLAYER'}! ⚡`, 3500);
          if (window.audio && window.audio.playImpact) window.audio.playImpact('heavy');
          break;
        case 'player_left':
          if (this.remotePlayers.has(msg.id)) {
            this.removeRemotePlayer(msg.id);
            if (window.showAnnouncement) window.showAnnouncement(`🚪 ${msg.name || 'PLAYER'} LEFT THE 6IX`, 2200);
          }
          this.updateHUDStatus('connected');
          break;

        // ---- NPC sync ----
        case 'world':      // host -> guests
          if (this.role === 'guest' && window.applyEnemySnapshot) window.applyEnemySnapshot(msg.e || []);
          break;
        case 'enemy_hit':  // guest -> host
          if (this.role === 'host' && window.applyNetEnemyHit) window.applyNetEnemyHit(msg);
          break;
        case 'enemy_dmg':  // host -> me: a robot punched me on the host's screen
          if (window.applyNetEnemyDamage) window.applyNetEnemyDamage(msg.damage || 0);
          break;
        case 'score_event':
          if (window.applyScoreEvent) window.applyScoreEvent(msg.ev || {});
          break;
      }
    }

    // ---- outgoing NPC sync helpers (called from game.js) ----
    sendEnemyHit(nid, dmg, knockback, attackType, glory) {
      this.send({ type: 'enemy_hit', nid, dmg, kb: knockback, atype: attackType, glory: !!glory });
    }
    sendEnemyDamage(targetId, damage) {
      this.send({ type: 'enemy_dmg', targetId, damage });
    }
    sendScoreEvent(targetId, ev) {
      this.send({ type: 'score_event', targetId, ev });
    }

    addRemotePlayer(info) {
      if (this.remotePlayers.has(info.id)) return;
      const has = (info.x || info.z);
      const spawnX = has ? info.x : (this.localPlayer ? this.localPlayer.pos.x + 3 : 0);
      const spawnY = has ? (info.y || 0) : 0;
      const spawnZ = has ? info.z : (this.localPlayer ? this.localPlayer.pos.z + 3 : 0);
      const rig = createRemoteHeroRig(info.name || 'DEFENDER', info.color || 0xef4444);
      rig.root.position.set(spawnX, spawnY, spawnZ);
      if (this.scene) this.scene.add(rig.root);
      this.remotePlayers.set(info.id, {
        id: info.id,
        name: info.name || 'DEFENDER',
        color: info.color || 0xef4444,
        rig,
        currentPos: new THREE.Vector3(spawnX, spawnY, spawnZ),
        targetPos: new THREE.Vector3(spawnX, spawnY, spawnZ),
        eyePos: new THREE.Vector3(spawnX, spawnY + 1.7, spawnZ),
        currentYaw: info.yaw || 0,
        targetYaw: info.yaw || 0,
        anim: info.anim || 'idle',
        isBerserk: !!info.isBerserk,
        health: (info.health !== undefined) ? info.health : 100,
        armor: 50,
        walkPhase: Math.random() * Math.PI * 2,
        attackProgress: 0,
        isAttacking: false,
        attackType: 'punch'
      });
    }

    removeRemotePlayer(id) {
      const rp = this.remotePlayers.get(id);
      if (!rp) return;
      if (rp.rig && rp.rig.root && this.scene) this.scene.remove(rp.rig.root);
      this.remotePlayers.delete(id);
    }

    removeAllRemotePlayers() {
      this.remotePlayers.forEach((rp) => {
        if (rp.rig && rp.rig.root && this.scene) this.scene.remove(rp.rig.root);
      });
      this.remotePlayers.clear();
    }

    triggerRemoteAttackAnim(rp, atkType) {
      rp.isAttacking = true;
      rp.attackProgress = 0;
      rp.attackType = atkType;
      if (window.audio && window.audio.playPunch && this.localPlayer &&
          Math.hypot(rp.currentPos.x - this.localPlayer.pos.x, rp.currentPos.z - this.localPlayer.pos.z) < 30) {
        window.audio.playPunch(atkType === 'heavy' ? 1.5 : 1.0, rp.isBerserk);
      }
    }

    handleIncomingHit(msg) {
      if (!this.gameState || this.gameState.isDead) return;
      if (!this.friendlyFire) return;   // room is co-op: server shouldn't send these, but be safe
      const dmg = Math.max(0, Math.min(200, msg.damage || 20));
      const kbX = (msg.knockback && msg.knockback.x) || 0;
      const kbZ = (msg.knockback && msg.knockback.z) || 0;
      let remaining = dmg;
      if (this.gameState.armor > 0) {
        const absorb = Math.min(this.gameState.armor, dmg * 0.65);
        this.gameState.armor -= absorb;
        remaining -= absorb;
      }
      this.gameState.health = Math.max(0, this.gameState.health - remaining);
      if (window.triggerDamageFlash) window.triggerDamageFlash();
      if (window.triggerScreenShake) window.triggerScreenShake(16);
      if (window.setFaceExpression) window.setFaceExpression('hurt', 0.65);
      if (window.updateHUDHealth) window.updateHUDHealth();
      if (window.audio && window.audio.playImpact) window.audio.playImpact(msg.attackType || 'punch');
      if (this.localPlayer) {
        this.localPlayer.velocity.x += kbX;
        this.localPlayer.velocity.z += kbZ;
      }
      if (this.gameState.health <= 0) {
        this.gameState.health = 0;
        this.send({ type: 'ko', killerId: msg.attackerId, killerName: msg.attackerName });
        if (window.playerDeath) window.playerDeath();
      }
    }

    broadcastAttack(attackType) {
      if (!this.connected || !this.localPlayer) return;
      this.send({ type: 'attack', attackType });
    }

    // Horizontal (feet-to-feet) geometry: the local player position is at eye height,
    // remote rigs are at foot height, so 3D distance/direction was wrong up close.
    _meleeTargets(atk) {
      const out = [];
      const p = this.localPlayer.pos;
      const fx = -Math.sin(this.localPlayer.yaw), fz = -Math.cos(this.localPlayer.yaw);
      this.remotePlayers.forEach((rp, id) => {
        if (!rp.rig) return;
        const dx = rp.currentPos.x - p.x, dz = rp.currentPos.z - p.z;
        const dist = Math.hypot(dx, dz);
        if (dist > atk.range + 0.3) return;
        if (Math.abs(rp.currentPos.y + 1.7 - p.y) > 2.5) return;   // different floor
        const nx = dist > 0.05 ? dx / dist : fx, nz = dist > 0.05 ? dz / dist : fz;
        if (dist > 0.6 && nx * fx + nz * fz < 0.5) return;           // point blank always connects
        out.push({ rp, id, nx, nz });
      });
      return out;
    }

    checkMeleeHits(atk) {
      if (!this.connected || !this.localPlayer || this.remotePlayers.size === 0) return false;
      const targets = this._meleeTargets(atk);
      if (!targets.length) return false;
      if (!this.friendlyFire) {
        const t = targets[0];
        if (window.showAnnouncement) window.showAnnouncement(`🤜🤛 SQUAD FIST-BUMP WITH ${t.rp.name}!`, 1200);
        if (window.audio && window.audio.playPickup) window.audio.playPickup();
        if (window.spawnDebris) window.spawnDebris(t.rp.currentPos.x, 1.2, t.rp.currentPos.z, 0x38bdf8, 14, 6);
        return true;
      }
      const berserk = this.gameState && this.gameState.isBerserk;
      targets.forEach(({ rp, id, nx, nz }) => {
        const dmg = berserk ? atk.damage * 3 : atk.damage;
        const kb = berserk ? atk.knockback * 2.2 : atk.knockback;
        this.send({ type: 'hit', targetId: id, damage: dmg, knockback: { x: nx * kb, z: nz * kb }, attackType: atk.type });
        if (rp.rig && rp.rig.materials) {
          rp.rig.materials.forEach(m => m.color.setHex(0xff2222));
          setTimeout(() => {
            if (rp.rig && rp.rig.originalColors) rp.rig.materials.forEach((m, i) => m.color.setHex(rp.rig.originalColors[i]));
          }, 120);
        }
        if (window.spawnDebris) window.spawnDebris(rp.currentPos.x, 1.0, rp.currentPos.z, 0xffea00, 24, 8);
      });
      return true;
    }

    update(dt) {
      if (this.connected && this.localPlayer) {
        // 1. Local player state at ~20 Hz
        this.sendTimer += dt;
        if (this.sendTimer >= 0.05) {
          this.sendTimer = 0;
          const gs = this.gameState;
          this.send({
            type: 'state',
            x: Number(this.localPlayer.pos.x.toFixed(2)),
            y: Number((this.localPlayer.pos.y - 1.7).toFixed(2)),
            z: Number(this.localPlayer.pos.z.toFixed(2)),
            yaw: Number(this.localPlayer.yaw.toFixed(3)),
            anim: (gs && gs.isAttacking) ? gs.currentAnimType : 'idle',
            isBerserk: !!(gs && gs.isBerserk),
            health: gs ? (gs.isDead ? 0 : Math.round(gs.health)) : 100,
            armor: gs ? Math.round(gs.armor) : 50,
            score: gs ? gs.score : 0
          });
        }
        // 2. Host streams the NPC world at ~10 Hz
        if (this.isHostWithPeers() && window.buildEnemySnapshot) {
          this.worldTimer += dt;
          if (this.worldTimer >= 0.1) {
            this.worldTimer = 0;
            this.send({ type: 'world', e: window.buildEnemySnapshot() });
          }
        }
      }

      // 3. Interpolate & animate remote players
      this.remotePlayers.forEach((rp) => {
        if (!rp.rig) return;
        const before = rp.currentPos.distanceTo(rp.targetPos);
        if (before > 15) rp.currentPos.copy(rp.targetPos);           // teleport / respawn
        else rp.currentPos.lerp(rp.targetPos, Math.min(1.0, dt * 14.0));
        rp.eyePos.set(rp.currentPos.x, rp.currentPos.y + 1.7, rp.currentPos.z);
        rp.rig.root.position.copy(rp.currentPos);
        rp.rig.root.visible = rp.health > 0;
        let dYaw = rp.targetYaw - rp.currentYaw;
        dYaw = Math.atan2(Math.sin(dYaw), Math.cos(dYaw));
        rp.currentYaw += dYaw * Math.min(1.0, dt * 12.0);
        rp.rig.root.rotation.y = rp.currentYaw;
        if (before > 0.05) {
          rp.walkPhase += dt * 9.0;
          const s = Math.sin(rp.walkPhase) * 0.6;
          rp.rig.leftLeg.rotation.x = s;
          rp.rig.lCalfPivot.rotation.x = Math.max(0, -s * 0.6);
          rp.rig.rightLeg.rotation.x = -s;
          rp.rig.rCalfPivot.rotation.x = Math.max(0, s * 0.6);
        } else {
          rp.rig.leftLeg.rotation.x = rp.rig.lCalfPivot.rotation.x = 0;
          rp.rig.rightLeg.rotation.x = rp.rig.rCalfPivot.rotation.x = 0;
        }
        if (rp.isAttacking) {
          rp.attackProgress += dt * 4.2;
          const swing = Math.sin(Math.min(1.0, rp.attackProgress) * Math.PI);
          if (rp.attackType === 'kick') {
            rp.rig.rightLeg.rotation.set(-1.4 * swing, 0.2, 0);
          } else {
            rp.rig.rArmPivot.rotation.x = -1.2 - swing * 0.8;
            rp.rig.rForearm.rotation.x = -0.2 - swing * 0.9;
          }
          if (rp.attackProgress >= 1.0) {
            rp.isAttacking = false;
            rp.attackProgress = 0;
            rp.rig.rArmPivot.rotation.x = 0;
            rp.rig.rForearm.rotation.x = 0;
            rp.rig.rightLeg.rotation.set(0, 0, 0);
          }
        }
      });
    }

    // ---------------------------------------------------------------- UI
    initUI() {
      const nameInput = document.getElementById('mp-name-input');
      const roomInput = document.getElementById('mp-room-input');
      const serverInput = document.getElementById('mp-server-input');
      if (nameInput) {
        nameInput.value = this.localName;
        nameInput.addEventListener('change', (e) => this.setPlayerName(e.target.value));
      }
      if (roomInput) roomInput.value = this.room;
      if (serverInput) serverInput.value = this.serverUrl;

      const connectBtn = document.getElementById('mp-connect-btn');
      if (connectBtn) {
        connectBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          if (nameInput && nameInput.value) this.setPlayerName(nameInput.value);
          if (roomInput) {
            this.room = (roomInput.value || '6ix').trim().toLowerCase().replace(/[^a-z0-9_-]/g, '') || '6ix';
            roomInput.value = this.room;
            localStorage.setItem('toronto_mp_room', this.room);
          }
          if (serverInput && serverInput.value.trim()) {
            this.serverUrl = serverInput.value.trim();
            localStorage.setItem('toronto_mp_server', this.serverUrl);
          }
          this.connect(this.serverUrl);
        });
      }
      const modeBtn = document.getElementById('mp-mode-btn');
      if (modeBtn) {
        modeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          if (this.connected) this.send({ type: 'set_mode', pvp: !this.friendlyFire });
          else this.applyMode(!this.friendlyFire, null);   // offline: local only, no effect
        });
      }
      const badge = document.getElementById('mp-status-badge');
      if (badge) {
        badge.style.cursor = 'pointer';
        badge.addEventListener('click', (e) => {
          e.stopPropagation();
          if (window.pauseGame) window.pauseGame();
        });
      }
    }

    applyMode(pvp, byName) {
      const changed = pvp !== this.friendlyFire;
      this.friendlyFire = pvp;
      const btn = document.getElementById('mp-mode-btn');
      if (btn) {
        btn.className = pvp ? 'mp-mode-toggle-btn pvp-active' : 'mp-mode-toggle-btn';
        btn.innerText = pvp ? '⚔️ ARENA BRAWL (PVP DUEL ON)' : '🤝 SQUAD CO-OP (NO FRIENDLY FIRE)';
      }
      if (changed && byName !== null && window.showAnnouncement) {
        const who = byName ? ` (${String(byName).toUpperCase()})` : '';
        window.showAnnouncement(pvp ? `⚔️ BRAWL DUEL ON — FRIENDLY FIRE!${who}` : `🤝 SQUAD CO-OP — NO FRIENDLY FIRE${who}`, 2500);
      }
    }

    setPlayerName(name) {
      if (!name) return;
      this.localName = name.trim().slice(0, 20);
      localStorage.setItem('toronto_mp_name', this.localName);
      if (this.connected) this.send({ type: 'join_info', name: this.localName });
    }

    updateHUDStatus(status) {
      const badge = document.getElementById('mp-status-badge');
      const lobbyStatus = document.getElementById('mp-lobby-status');
      if (status === 'connected') {
        const count = this.remotePlayers.size + 1;
        const roleTxt = this.role === 'guest' ? 'GUEST' : (count > 1 ? 'HOST' : 'SOLO');
        if (badge) {
          badge.className = 'tag tag-green';
          badge.innerText = `🌐 ${this.room.toUpperCase()} • ${count} • ${roleTxt}`;
          badge.title = `Relay: ${this.serverUrl} [room ${this.room}]`;
        }
        if (lobbyStatus) {
          lobbyStatus.innerText = `ONLINE IN ROOM [${this.room.toUpperCase()}] • ${count} SQUAD • YOU ARE ${roleTxt}`;
          lobbyStatus.style.color = '#34d399';
        }
      } else if (status === 'connecting') {
        if (badge) { badge.className = 'tag tag-yellow'; badge.innerText = '🌐 CONNECTING...'; badge.title = `Connecting to ${this.serverUrl}`; }
        if (lobbyStatus) { lobbyStatus.innerText = `CONNECTING TO RELAY (${this.serverUrl})...`; lobbyStatus.style.color = '#fbbf24'; }
      } else {
        if (badge) { badge.className = 'tag tag-dim'; badge.innerText = '🌐 SOLO / OFFLINE'; badge.title = 'Offline. Click to open lobby.'; }
        if (lobbyStatus) { lobbyStatus.innerText = 'OFFLINE / LOCAL SINGLE-PLAYER'; lobbyStatus.style.color = '#94a3b8'; }
      }
    }
  }

  window.multiplayer = new MultiplayerClient();
  window.setMultiplayerName = function (name) {
    if (window.multiplayer) window.multiplayer.setPlayerName(name);
  };
})();
