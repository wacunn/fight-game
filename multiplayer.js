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

    // 3. Localhost / local LAN auto-detection
    const host = window.location.host;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    if (host.includes('localhost') || host.includes('127.0.0.1') || host.startsWith('192.168.') || host.startsWith('10.')) {
      return `${protocol}//${host}/ws`;
    }

    // 4. Default to Production Cloud Relay on GitHub Pages / remote hosting
    return CLOUD_SERVER_URL;
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
  class MultiplayerClient {
    constructor() {
      this.ws = null;
      this.connected = false;
      this.connecting = false;
      this.localId = null;
      this.localName = getSavedPlayerName();
      this.localColor = 0xef4444;
      this.room = getAutoRoom();
      this.serverUrl = getAutoServerUrl();

      this.scene = null;
      this.localPlayer = null;
      this.gameState = null;

      // remotePlayers: id -> { id, name, color, rig, targetPos, targetYaw, currentPos, currentYaw, ... }
      this.remotePlayers = new Map();

      this.sendTimer = 0;
      this.reconnectTimer = null;
      this.reconnectAttempts = 0;
      this.friendlyFire = false; // Default: Co-op mode (no friendly fire between kids!)
    }

    init(scene, player, state) {
      this.scene = scene;
      this.localPlayer = player;
      this.gameState = state;

      this.initUI();
      this.updateHUDStatus('connecting');
      this.connect();
    }

    connect(overrideUrl) {
      if (this.ws) {
        try { this.ws.close(); } catch (e) {}
        this.ws = null;
      }

      const url = overrideUrl || this.serverUrl;
      this.serverUrl = url;
      this.connecting = true;
      this.updateHUDStatus('connecting');

      console.log(`[Multiplayer] Connecting to relay server: ${url} (Room: ${this.room})...`);

      try {
        this.ws = new WebSocket(url);
      } catch (err) {
        console.warn('[Multiplayer] Failed to create WebSocket connection:', err);
        this.onConnectionFailed();
        return;
      }

      this.ws.onopen = () => {
        this.connected = true;
        this.connecting = false;
        this.reconnectAttempts = 0;
        console.log('[Multiplayer] Connected successfully to relay server!');

        // Send Join info with custom name
        this.send({
          type: 'join_info',
          name: this.localName,
          color: this.localColor
        });

        this.updateHUDStatus('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          this.handleMessage(msg);
        } catch (e) {
          console.warn('[Multiplayer] Malformed message received:', e);
        }
      };

      this.ws.onerror = (err) => {
        console.warn('[Multiplayer] WebSocket error:', err);
      };

      this.ws.onclose = () => {
        this.connected = false;
        this.connecting = false;
        console.log('[Multiplayer] Disconnected from relay server.');
        this.removeAllRemotePlayers();
        this.updateHUDStatus('offline');
        this.scheduleReconnect();
      };
    }

    scheduleReconnect() {
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
      // Reconnect with gentle backoff
      this.reconnectAttempts++;
      const delay = Math.min(12000, 2000 + this.reconnectAttempts * 2000);
      this.reconnectTimer = setTimeout(() => {
        if (!this.connected) {
          this.connect();
        }
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

    handleMessage(msg) {
      const type = msg.type;

      if (type === 'welcome') {
        this.localId = msg.id;
        if (msg.color) this.localColor = msg.color;
        console.log(`[Multiplayer] Welcomed by server as ${this.localId}`);

        // Add any players already in the room
        if (Array.isArray(msg.players)) {
          msg.players.forEach(p => {
            if (p.id !== this.localId) {
              this.addRemotePlayer(p);
            }
          });
        }
        this.updateHUDStatus('connected');

      } else if (type === 'player_joined') {
        const p = msg.player;
        if (p && p.id !== this.localId) {
          this.addRemotePlayer(p);
          if (window.showAnnouncement) {
            window.showAnnouncement(`⭐ ${p.name.toUpperCase()} JOINED THE SQUAD! ⭐`, 2500);
          }
        }
        this.updateHUDStatus('connected');

      } else if (type === 'player_updated') {
        const p = msg.player;
        if (p && this.remotePlayers.has(p.id)) {
          const rp = this.remotePlayers.get(p.id);
          rp.name = p.name;
          rp.color = p.color;
          if (rp.rig && rp.rig.updateNameplate) {
            rp.rig.updateNameplate(rp.name, rp.health || 100, rp.isBerserk || false);
          }
        }

      } else if (type === 'state') {
        const id = msg.id;
        if (id && this.remotePlayers.has(id)) {
          const rp = this.remotePlayers.get(id);
          rp.targetPos.set(msg.x, msg.y, msg.z);
          rp.targetYaw = msg.yaw || 0;
          rp.targetPitch = msg.pitch || 0;
          rp.anim = msg.anim || 'idle';
          rp.isBerserk = !!msg.isBerserk;
          rp.health = (msg.health !== undefined) ? msg.health : 100;
          rp.armor = (msg.armor !== undefined) ? msg.armor : 50;

          if (rp.rig) {
            rp.rig.updateNameplate(rp.name, rp.health, rp.isBerserk);
            if (rp.rig.stickMesh) rp.rig.stickMesh.visible = rp.isBerserk;
          }
        }

      } else if (type === 'attack') {
        const id = msg.id;
        if (id && this.remotePlayers.has(id)) {
          const rp = this.remotePlayers.get(id);
          this.triggerRemoteAttackAnim(rp, msg.attackType || 'punch');
        }

      } else if (type === 'hit') {
        // We received a direct punch/kick/slam from another player!
        this.handleIncomingHit(msg);

      } else if (type === 'ko') {
        if (window.showAnnouncement) {
          window.showAnnouncement(`⚡ ${msg.killerName || 'PLAYER'} KO'D ${msg.victimName || 'PLAYER'}! ⚡`, 3500);
        }
        if (window.audio && window.audio.playImpact) {
          window.audio.playImpact('heavy');
        }

      } else if (type === 'player_left') {
        const id = msg.id;
        if (id && this.remotePlayers.has(id)) {
          const rp = this.remotePlayers.get(id);
          this.removeRemotePlayer(id);
          if (window.showAnnouncement) {
            window.showAnnouncement(`🚪 ${msg.name || 'PLAYER'} LEFT THE 6IX`, 2200);
          }
        }
        this.updateHUDStatus('connected');
      }
    }

    addRemotePlayer(info) {
      if (this.remotePlayers.has(info.id)) return;

      const spawnX = (info.x !== undefined) ? info.x : (this.localPlayer ? this.localPlayer.pos.x + 3 : 0);
      const spawnY = (info.y !== undefined) ? info.y : 0;
      const spawnZ = (info.z !== undefined) ? info.z : (this.localPlayer ? this.localPlayer.pos.z + 3 : 0);

      const rig = createRemoteHeroRig(info.name || 'DEFENDER', info.color || 0xef4444);
      rig.root.position.set(spawnX, spawnY, spawnZ);
      if (this.scene) this.scene.add(rig.root);

      const remotePlayer = {
        id: info.id,
        name: info.name || 'DEFENDER',
        color: info.color || 0xef4444,
        rig: rig,
        currentPos: new THREE.Vector3(spawnX, spawnY, spawnZ),
        targetPos: new THREE.Vector3(spawnX, spawnY, spawnZ),
        currentYaw: info.yaw || 0,
        targetYaw: info.yaw || 0,
        anim: info.anim || 'idle',
        isBerserk: !!info.isBerserk,
        health: 100,
        armor: 50,
        walkPhase: Math.random() * Math.PI * 2,
        attackProgress: 0,
        isAttacking: false,
        attackType: 'punch'
      };

      this.remotePlayers.set(info.id, remotePlayer);
      console.log(`[Multiplayer] Added remote player avatar: ${info.name} (${info.id})`);
    }

    removeRemotePlayer(id) {
      if (!this.remotePlayers.has(id)) return;
      const rp = this.remotePlayers.get(id);
      if (rp.rig && rp.rig.root && this.scene) {
        this.scene.remove(rp.rig.root);
      }
      this.remotePlayers.delete(id);
    }

    removeAllRemotePlayers() {
      this.remotePlayers.forEach((rp, id) => {
        if (rp.rig && rp.rig.root && this.scene) {
          this.scene.remove(rp.rig.root);
        }
      });
      this.remotePlayers.clear();
    }

    triggerRemoteAttackAnim(rp, atkType) {
      rp.isAttacking = true;
      rp.attackProgress = 0;
      rp.attackType = atkType;

      if (window.audio && window.audio.playPunch) {
        window.audio.playPunch(atkType === 'heavy' ? 1.5 : 1.0, rp.isBerserk);
      }
    }

    handleIncomingHit(msg) {
      if (!this.gameState || this.gameState.isDead) return;

      // In Cooperative Mode, kids take zero damage and zero knockback from each other!
      if (!this.friendlyFire && !msg.isPvP) {
        return;
      }

      const dmg = msg.damage || 20;
      const kbX = (msg.knockback && msg.knockback.x) || 0;
      const kbZ = (msg.knockback && msg.knockback.z) || 0;

      // Apply damage to local player
      let remaining = dmg;
      if (this.gameState.armor > 0) {
        const absorb = Math.min(this.gameState.armor, dmg * 0.65);
        this.gameState.armor -= absorb;
        remaining -= absorb;
      }
      this.gameState.health = Math.max(0, this.gameState.health - remaining);

      // Trigger visual FX
      if (window.triggerDamageFlash) window.triggerDamageFlash();
      if (window.triggerScreenShake) window.triggerScreenShake(16);
      if (window.setFaceExpression) window.setFaceExpression('hurt', 0.65);
      if (window.updateHUDHealth) window.updateHUDHealth();
      if (window.audio && window.audio.playImpact) window.audio.playImpact(msg.attackType || 'punch');

      // Knockback physics impulse
      if (this.localPlayer) {
        this.localPlayer.velocity.x += kbX;
        this.localPlayer.velocity.z += kbZ;
      }

      // Check if fallen
      if (this.gameState.health <= 0) {
        this.gameState.health = 0;
        this.send({
          type: 'ko',
          killerId: msg.attackerId,
          killerName: msg.attackerName
        });
        if (window.playerDeath) window.playerDeath();
      }
    }

    // Called on local attack swing to broadcast to network
    broadcastAttack(attackType) {
      if (!this.connected || !this.localPlayer) return;
      const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), this.localPlayer.yaw);
      this.send({
        type: 'attack',
        attackType: attackType,
        x: this.localPlayer.pos.x,
        y: this.localPlayer.pos.y,
        z: this.localPlayer.pos.z,
        fx: forward.x,
        fz: forward.z
      });
    }

    // Called during local player melee hit detection to test against remote players
    checkMeleeHits(atk) {
      if (!this.connected || !this.localPlayer || this.remotePlayers.size === 0) return false;

      const pPos = this.localPlayer.pos;
      const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), this.localPlayer.yaw);

      // In Cooperative Mode, friendly fire is completely disabled: kids cannot hurt or knock each other out!
      if (!this.friendlyFire) {
        let fistBumped = false;
        this.remotePlayers.forEach((rp) => {
          if (!rp.rig) return;
          const rPos = rp.currentPos;
          const dist = pPos.distanceTo(rPos);

          if (dist <= atk.range + 0.3) {
            const toTarget = rPos.clone().sub(pPos).normalize();
            if (toTarget.dot(forward) > 0.52) {
              fistBumped = true;
              if (window.showAnnouncement) {
                window.showAnnouncement(`🤜🤛 SQUAD FIST-BUMP WITH ${rp.name}!`, 1200);
              }
              if (window.audio && window.audio.playPickup) {
                window.audio.playPickup();
              }
              if (window.spawnDebris) {
                window.spawnDebris(rPos.x, 1.2, rPos.z, 0x38bdf8, 14, 6);
              }
            }
          }
        });
        return fistBumped;
      }

      // PvP Mode (when explicitly toggled to Brawl Duel)
      let hitAny = false;
      this.remotePlayers.forEach((rp, id) => {
        if (!rp.rig) return;
        const rPos = rp.currentPos;
        const dist = pPos.distanceTo(rPos);

        if (dist <= atk.range + 0.3) {
          const toTarget = rPos.clone().sub(pPos).normalize();
          if (toTarget.dot(forward) > 0.52) {
            // Landed hit on remote player!
            hitAny = true;
            const dmg = this.gameState && this.gameState.isBerserk ? atk.damage * 3 : atk.damage;
            const kb = this.gameState && this.gameState.isBerserk ? atk.knockback * 2.2 : atk.knockback;

            const kbVec = { x: toTarget.x * kb, z: toTarget.z * kb };
            this.send({
              type: 'hit',
              targetId: id,
              isPvP: true,
              damage: dmg,
              knockback: kbVec,
              attackType: atk.type
            });

            // Flash remote player mesh
            if (rp.rig && rp.rig.materials) {
              rp.rig.materials.forEach(m => m.color.setHex(0xff2222));
              setTimeout(() => {
                if (rp.rig && rp.rig.materials && rp.rig.originalColors) {
                  rp.rig.materials.forEach((m, idx) => m.color.setHex(rp.rig.originalColors[idx]));
                }
              }, 120);
            }

            if (window.spawnDebris) {
              window.spawnDebris(rPos.x, 1.0, rPos.z, 0xffea00, 24, 8);
            }
          }
        }
      });

      return hitAny;
    }

    update(dt) {
      // 1. Throttled transmission of local player state (~20 updates/sec)
      if (this.connected && this.localPlayer) {
        this.sendTimer += dt;
        if (this.sendTimer >= 0.05) {
          this.sendTimer = 0;
          this.send({
            type: 'state',
            x: Number(this.localPlayer.pos.x.toFixed(2)),
            y: Number((this.localPlayer.pos.y - 1.7).toFixed(2)),
            z: Number(this.localPlayer.pos.z.toFixed(2)),
            yaw: Number(this.localPlayer.yaw.toFixed(3)),
            pitch: Number(this.localPlayer.pitch.toFixed(3)),
            anim: (this.gameState && this.gameState.isAttacking) ? this.gameState.currentAnimType : 'idle',
            isBerserk: !!(this.gameState && this.gameState.isBerserk),
            health: this.gameState ? Math.round(this.gameState.health) : 100,
            armor: this.gameState ? Math.round(this.gameState.armor) : 50,
            score: this.gameState ? this.gameState.score : 0
          });
        }
      }

      // 2. Smooth Interpolation & Animations for all Remote Players
      this.remotePlayers.forEach((rp, id) => {
        if (!rp.rig) return;

        // Smooth positional lerp
        const lerpFactor = Math.min(1.0, dt * 14.0);
        rp.currentPos.lerp(rp.targetPos, lerpFactor);
        rp.rig.root.position.copy(rp.currentPos);

        // Smooth yaw rotation
        let dYaw = rp.targetYaw - rp.currentYaw;
        dYaw = Math.atan2(Math.sin(dYaw), Math.cos(dYaw));
        rp.currentYaw += dYaw * Math.min(1.0, dt * 12.0);
        rp.rig.root.rotation.y = rp.currentYaw;

        // Animate legs based on movement speed
        const distMoved = rp.currentPos.distanceTo(rp.targetPos);
        if (distMoved > 0.05) {
          rp.walkPhase += dt * 9.0;
          const legSwing = Math.sin(rp.walkPhase) * 0.6;
          rp.rig.leftLeg.rotation.x = legSwing;
          rp.rig.lCalfPivot.rotation.x = Math.max(0, -legSwing * 0.6);
          rp.rig.rightLeg.rotation.x = -legSwing;
          rp.rig.rCalfPivot.rotation.x = Math.max(0, legSwing * 0.6);
        } else {
          rp.rig.leftLeg.rotation.x = 0;
          rp.rig.lCalfPivot.rotation.x = 0;
          rp.rig.rightLeg.rotation.x = 0;
          rp.rig.rCalfPivot.rotation.x = 0;
        }

        // Animate attacks
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
          }
        }
      });
    }

    initUI() {
      // 1. Name input
      const nameInput = document.getElementById('mp-name-input');
      if (nameInput) {
        nameInput.value = this.localName;
        nameInput.addEventListener('input', (e) => {
          this.setPlayerName(e.target.value);
        });
        nameInput.addEventListener('change', (e) => {
          this.setPlayerName(e.target.value);
        });
      }

      // 2. Room input
      const roomInput = document.getElementById('mp-room-input');
      if (roomInput) {
        roomInput.value = this.room;
        roomInput.addEventListener('change', (e) => {
          const r = (e.target.value || '6ix').trim().toLowerCase();
          this.room = r;
          localStorage.setItem('toronto_mp_room', r);
        });
      }

      // 3. Server input
      const serverInput = document.getElementById('mp-server-input');
      if (serverInput) {
        serverInput.value = this.serverUrl;
        serverInput.addEventListener('change', (e) => {
          const s = (e.target.value || '').trim();
          if (s) {
            this.serverUrl = s;
            localStorage.setItem('toronto_mp_server', s);
          }
        });
      }

      // 4. Connect button
      const connectBtn = document.getElementById('mp-connect-btn');
      if (connectBtn) {
        connectBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          if (nameInput && nameInput.value) this.setPlayerName(nameInput.value);
          if (roomInput && roomInput.value) {
            this.room = roomInput.value.trim().toLowerCase() || '6ix';
            localStorage.setItem('toronto_mp_room', this.room);
          }
          if (serverInput && serverInput.value) {
            this.serverUrl = serverInput.value.trim();
            localStorage.setItem('toronto_mp_server', this.serverUrl);
          }
          this.connect(this.serverUrl);
        });
      }

      // 5. Co-op vs PvP Mode Toggle button
      const modeBtn = document.getElementById('mp-mode-btn');
      if (modeBtn) {
        modeBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.setFriendlyFire(!this.friendlyFire);
        });
      }

      // 6. Header Badge opens Menu
      const badge = document.getElementById('mp-status-badge');
      if (badge) {
        badge.style.cursor = 'pointer';
        badge.addEventListener('click', (e) => {
          e.stopPropagation();
          if (window.pauseGame) window.pauseGame();
        });
      }
    }

    setFriendlyFire(enabled) {
      this.friendlyFire = !!enabled;
      const btn = document.getElementById('mp-mode-btn');
      if (btn) {
        if (this.friendlyFire) {
          btn.className = 'mp-mode-toggle-btn pvp-active';
          btn.innerText = '⚔️ ARENA BRAWL (PVP DUEL ON)';
        } else {
          btn.className = 'mp-mode-toggle-btn';
          btn.innerText = '🤝 SQUAD CO-OP (NO FRIENDLY FIRE)';
        }
      }
      if (window.showAnnouncement) {
        window.showAnnouncement(this.friendlyFire ? '⚔️ BRAWL DUEL ACTIVE: FRIENDLY FIRE ON!' : '🤝 SQUAD CO-OP ACTIVE: FRIENDLY FIRE OFF!', 2500);
      }
    }

    setPlayerName(name) {
      if (!name) return;
      this.localName = name.trim().slice(0, 20);
      localStorage.setItem('toronto_mp_name', this.localName);
      if (this.connected) {
        this.send({
          type: 'join_info',
          name: this.localName,
          color: this.localColor
        });
      }
    }

    updateHUDStatus(status) {
      const badge = document.getElementById('mp-status-badge');
      const lobbyStatus = document.getElementById('mp-lobby-status');

      if (status === 'connected') {
        const count = this.remotePlayers.size + 1;
        if (badge) {
          badge.className = 'tag tag-green';
          badge.innerText = `🌐 ONLINE (${count} SQUAD)`;
          badge.title = `Connected to relay: ${this.serverUrl} [Room: ${this.room}]`;
        }
        if (lobbyStatus) {
          lobbyStatus.innerText = `ONLINE IN ROOM: [${this.room.toUpperCase()}] • ${count} SQUAD MEMBERS`;
          lobbyStatus.style.color = '#34d399';
        }
      } else if (status === 'connecting') {
        if (badge) {
          badge.className = 'tag tag-yellow';
          badge.innerText = `🌐 CONNECTING...`;
          badge.title = `Attempting connection to: ${this.serverUrl}`;
        }
        if (lobbyStatus) {
          lobbyStatus.innerText = `CONNECTING TO RELAY (${this.serverUrl})...`;
          lobbyStatus.style.color = '#fbbf24';
        }
      } else {
        if (badge) {
          badge.className = 'tag tag-dim';
          badge.innerText = `🌐 SOLO / OFFLINE`;
          badge.title = `Offline. Single-player mode active. Click to open lobby.`;
        }
        if (lobbyStatus) {
          lobbyStatus.innerText = `OFFLINE / LOCAL SINGLE-PLAYER`;
          lobbyStatus.style.color = '#94a3b8';
        }
      }
    }
  }

  // Create global multiplayer singleton
  window.multiplayer = new MultiplayerClient();

  // Expose global helper for player name changes
  window.setMultiplayerName = function (name) {
    if (window.multiplayer) window.multiplayer.setPlayerName(name);
  };
})();
