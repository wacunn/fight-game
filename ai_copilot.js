/**
 * AI Copilot & Watch AI Mode for Toronto Defender Brawl
 * Evaluates the trained Recurrent PPO neural network weights in real-time,
 * allowing the autonomous AI to seamlessly take over player movement and combat.
 */

class AICopilot {
  constructor() {
    this.isActive = false;
    this.mode = 'hybrid'; // 'hybrid' (RL + Navigation), 'pure_rl' (Raw Tensor Model), 'expert' (Tactical)
    this.modelData = null;
    this.isModelLoaded = false;
    this.decisionTimer = 0;
    this.decisionInterval = 1.0 / 20.0; // 20 Hz decision loop

    // 128-unit Recurrent LSTM states
    this.h = new Float32Array(128);
    this.c = new Float32Array(128);

    // Current output intents
    this.moveDir = new THREE.Vector3();
    this.targetYaw = 0;
    this.aiIntentText = 'IDLE';

    // Telemetry HUD elements
    this.badgeEl = null;
    this.intentEl = null;

    this.init();
  }

  cycleMode() {
    const modes = ['hybrid', 'pure_rl', 'expert'];
    const idx = (modes.indexOf(this.mode) + 1) % modes.length;
    this.mode = modes[idx];
    this.updateModePill();
  }

  updateModePill() {
    const pill = document.getElementById('ai-mode-pill');
    if (!pill) return;
    if (this.mode === 'hybrid') {
      pill.innerHTML = '🤖 MODE: HYBRID (RL + NAV) <span style="opacity:0.7">[CLICK / B]</span>';
      pill.style.borderColor = '#3b82f6';
      pill.style.color = '#93c5fd';
    } else if (this.mode === 'pure_rl') {
      pill.innerHTML = '🧠 MODE: PURE NEURAL RL <span style="opacity:0.7">[CLICK / B]</span>';
      pill.style.borderColor = '#10b981';
      pill.style.color = '#6ee7b7';
    } else {
      pill.innerHTML = '⚡ MODE: TACTICAL EXPERT <span style="opacity:0.7">[CLICK / B]</span>';
      pill.style.borderColor = '#f59e0b';
      pill.style.color = '#fcd34d';
    }
  }

  init() {
    this.loadWeights();
    this.createHUD();
    this.bindEvents();
  }

  async loadWeights() {
    if (window.AI_MODEL_WEIGHTS) {
      this.modelData = window.AI_MODEL_WEIGHTS;
      this.isModelLoaded = true;
      console.log('🤖 AI Copilot: Inlined Recurrent PPO neural network weights loaded!');
      return;
    }
    try {
      const resp = await fetch('ai_model.json');
      if (resp.ok) {
        this.modelData = await resp.json();
        this.isModelLoaded = true;
        console.log('🤖 AI Copilot: Recurrent PPO neural network weights loaded successfully!');
      } else {
        console.log('🤖 AI Copilot: ai_model.json not found yet, operating in hybrid tactical heuristic mode.');
      }
    } catch (e) {
      console.log('🤖 AI Copilot: Local heuristic mode active (model weights pending):', e.message);
    }
  }

  createHUD() {
    // 1. Top HUD Quick-Toggle Button
    const topBar = document.querySelector('.header-left') || document.body;
    const btn = document.createElement('button');
    btn.id = 'ai-watch-btn';
    btn.className = 'ai-toggle-btn';
    btn.innerHTML = '🤖 WATCH AI <span class="ai-key-hint">[V]</span>';
    btn.title = 'Toggle Autonomous Neural AI Copilot (Hotkey: V)';
    btn.onclick = () => this.toggle();
    topBar.appendChild(btn);
    this.btnEl = btn;

    const muteBtn = document.createElement('button');
    muteBtn.id = 'audio-mute-btn';
    muteBtn.className = 'ai-toggle-btn';
    const isMuted = (window.audio && window.audio.isMuted) || (new URLSearchParams(window.location.search).get('muted') === '1');
    muteBtn.innerHTML = isMuted ? '🔇 MUTED <span class="ai-key-hint">[M]</span>' : '🔊 SOUND <span class="ai-key-hint">[M]</span>';
    if (isMuted) muteBtn.classList.add('active');
    muteBtn.title = 'Toggle Audio Sound / Mute (Hotkey: M)';
    muteBtn.onclick = () => {
      if (window.audio && window.audio.toggleMute) {
        window.audio.toggleMute();
      }
    };
    topBar.appendChild(muteBtn);

    const boardBtn = document.createElement('a');
    boardBtn.id = 'ai-leaderboard-btn';
    boardBtn.className = 'ai-toggle-btn';
    boardBtn.innerHTML = '📊 RL LEADERBOARD';
    boardBtn.href = 'dashboard.html';
    boardBtn.target = '_blank';
    boardBtn.title = 'Open Live Real-Time Training Telemetry & District Leaderboard';
    boardBtn.style.textDecoration = 'none';
    topBar.appendChild(boardBtn);

    // 2. Holographic HUD overlay for AI telemetry
    const banner = document.createElement('div');
    banner.id = 'ai-pilot-hud';
    banner.className = 'ai-pilot-banner hidden';
    banner.innerHTML = `
      <div class="ai-pilot-indicator">
        <span class="ai-pulse-dot"></span>
        <span class="ai-title">NEURAL AI COPILOT ACTIVE</span>
        <span id="ai-mode-pill" class="ai-mode-pill" style="cursor: pointer; pointer-events: auto; background: rgba(0,0,0,0.5); border: 1px solid #3b82f6; color: #93c5fd; padding: 3px 8px; border-radius: 4px; margin-left: 8px; font-size: 11px; font-weight: 700; text-transform: uppercase;">🤖 MODE: HYBRID (RL + NAV) <span style="opacity:0.7">[CLICK / B]</span></span>
        <span class="ai-cancel-prompt">[PRESS V TO TAKE OVER]</span>
      </div>
      <div id="ai-intent-status" class="ai-intent-sub">INITIALIZING TELEMETRY...</div>
    `;
    document.body.appendChild(banner);
    this.bannerEl = banner;
    this.intentEl = document.getElementById('ai-intent-status');
    const pill = document.getElementById('ai-mode-pill');
    if (pill) pill.onclick = () => this.cycleMode();
  }

  bindEvents() {
    window.addEventListener('keydown', (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) return;
      if (e.code === 'KeyB' && !e.repeat && !e.ctrlKey && !e.metaKey) {
        this.cycleMode();
      }
    });
  }

  toggle(forceState) {
    const now = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
    if (forceState === undefined && this._lastToggleTime && (now - this._lastToggleTime < 250)) {
      console.warn('🤖 AI Copilot: toggle debounced');
      return;
    }
    this._lastToggleTime = now;

    this.isActive = (forceState !== undefined) ? forceState : !this.isActive;

    if (this.isActive) {
      // If game has not started yet or is paused, start/resume it immediately
      if (window.gameState && (!window.gameState.inGame || window.gameState.isPaused)) {
        if (window.audio && !window.audio.isMuted && window.audio.init) window.audio.init();
        if (window.gameState.isDead && window.resetGame) window.resetGame();
        if (window.resumeGame) window.resumeGame(false); // Free mouse look mode for spectator
      }
      const overlay = document.getElementById('menu-overlay');
      if (overlay && !overlay.classList.contains('hidden')) {
        overlay.classList.add('hidden');
      }
      if (window.gameState) {
        window.gameState.inGame = true;
        window.gameState.isPaused = false;
        window.gameState.freeMouseMode = true;
      }
    }

    if (this.btnEl) {
      if (this.isActive) {
        this.btnEl.classList.add('active');
        this.btnEl.innerHTML = '🤖 AI ACTIVE <span class="ai-key-hint">[V]</span>';
      } else {
        this.btnEl.classList.remove('active');
        this.btnEl.innerHTML = '🤖 WATCH AI <span class="ai-key-hint">[V]</span>';
      }
    }

    if (this.bannerEl) {
      if (this.isActive) {
        this.bannerEl.classList.remove('hidden');
        if (window.audio && !window.audio.isMuted && window.audio.playPunch) {
          window.audio.playPunch(0.9, false);
        }
      } else {
        this.bannerEl.classList.add('hidden');
        this.moveDir.set(0, 0, 0);
      }
    }

    // Reset recurrent state on toggle
    this.h.fill(0);
    this.c.fill(0);
    console.log(`🤖 AI Copilot toggled: ${this.isActive ? 'ENABLED' : 'DISABLED'}`);
  }

  update(dt, player, state, city, enemies, traffic, missionState) {
    if (!this.isActive || !player || state.isDead || state.isPaused) return;

    this.decisionTimer += dt;
    if (this.decisionTimer >= this.decisionInterval) {
      this.decisionTimer = 0;
      this.evaluatePolicy(player, state, city, enemies, traffic, missionState);
    }

    // Smoothly turn player and camera towards AI target heading (shortest angle interpolation)
    if (this.moveDir.lengthSq() > 0.01) {
      let diff = this.targetYaw - player.yaw;
      while (diff < -Math.PI) diff += Math.PI * 2;
      while (diff > Math.PI) diff -= Math.PI * 2;
      player.yaw += diff * Math.min(1.0, dt * 10.0);
      if (typeof camera !== 'undefined' && camera) {
        camera.rotation.order = 'YXZ';
        camera.rotation.y = player.yaw;
      }
    }

    // Update HUD intent
    if (this.intentEl) {
      this.intentEl.innerText = this.aiIntentText;
    }
  }

  /**
   * Constructs the 56-dimensional observation vector and runs forward inference
   */
  evaluatePolicy(player, state, city, enemies, traffic, missionState) {
    const px = player.pos.x;
    const pz = player.pos.z;
    const py = player.pos.y;
    const pYaw = player.yaw;

    // Determine Active Goal
    let gx = px, gz = pz, goalType = 0; // 0=waypoint, 1=threat, 2=sanctuary
    let goalDist = 999.0;

    // High Priority 1: Retreat to Peace Sanctuary when HP is critically low (< 35)
    const nearestSanctuary = this.findNearestSanctuary(px, pz, city);
    if (state.health < 35 && nearestSanctuary) {
      gx = nearestSanctuary.x;
      gz = nearestSanctuary.z;
      goalType = 2;
      this.aiIntentText = '🕊️ LOW HP: RETREATING TO PEACE SANCTUARY TO REGENERATE';
    }
    // High Priority 2: Engage nearest active hostile threat
    else {
      let nearestHostile = null;
      let minEnemyDist = 999.0;
      if (enemies && enemies.length > 0) {
        for (let i = 0; i < enemies.length; i++) {
          const e = enemies[i];
          if (e.isDead || e.isKnockedOut || !e.rig) continue;
          const ed = Math.hypot(e.rig.root.position.x - px, e.rig.root.position.z - pz);
          if (ed < minEnemyDist) {
            minEnemyDist = ed;
            nearestHostile = e;
          }
        }
      }

      if (nearestHostile && minEnemyDist < 30.0) {
        gx = nearestHostile.rig.root.position.x;
        gz = nearestHostile.rig.root.position.z;
        goalType = 1;
        this.aiIntentText = `⚔️ ENGAGING HOSTILE ROBOT (${Math.round(minEnemyDist)}m)`;
      } else if (missionState && missionState.active && missionState.pos) {
        gx = missionState.pos.x;
        gz = missionState.pos.z;
        goalType = 0;
        this.aiIntentText = '🎯 NAVIGATING TO ACTIVE MISSION DISTRESS BEACON';
      } else if (nearestSanctuary) {
        gx = nearestSanctuary.x;
        gz = nearestSanctuary.z;
        goalType = 2;
        this.aiIntentText = '🏙️ PATROLLING TORONTO SECTOR';
      }
    }

    goalDist = Math.hypot(gx - px, gz - pz);

    // Mode Dispatch: Pure RL vs Expert Tactical vs Hybrid (RL + Navigation)
    if (this.mode === 'pure_rl' && this.isModelLoaded && this.modelData && this.modelData.weights) {
      const obs = this.buildObservation(player, state, city, enemies, traffic, gx, gz, goalType);
      const action = this.forwardPass(obs);
      this.executeAction(action, player, state, gx, gz);
      this.aiIntentText = `🧠 [PURE RL] Move: ${action.move} | Combat: ${action.combat} | Target: ${Math.round(goalDist)}m`;
    } else if (this.mode === 'expert') {
      this.executeTacticalHeuristic(player, state, city, enemies, traffic, gx, gz, goalType, goalDist);
    } else {
      // Default: Intelligent Hybrid Mode (Neural Policy + Tactical Obstacle Avoidance)
      let rlActionUsable = false;
      let neuralAction = null;
      if (this.isModelLoaded && this.modelData && this.modelData.weights) {
        const obs = this.buildObservation(player, state, city, enemies, traffic, gx, gz, goalType);
        const action = this.forwardPass(obs);
        neuralAction = action;
        this.executeAction(action, player, state, gx, gz);

        // Check if RL movement direction is walkable and active
        if (this.moveDir.lengthSq() > 0.01) {
          const testX = px + this.moveDir.x * 2.0;
          const testZ = pz + this.moveDir.z * 2.0;
          if (!city || city.canMoveTo(testX, testZ, 0.6, py)) {
            rlActionUsable = true;
          }
        }
      }

      // If RL chose Idle while goal is distant, or RL path is blocked by a wall:
      if (!rlActionUsable && goalDist > 1.2) {
        this.executeTacticalHeuristic(player, state, city, enemies, traffic, gx, gz, goalType, goalDist);
        this.aiIntentText = `🧭 [HYBRID NAV] Steered around obstacle toward target (${Math.round(goalDist)}m)`;
      } else if (rlActionUsable && neuralAction) {
        this.aiIntentText = `🤖 [HYBRID RL] Neural Move: ${neuralAction.move} | Combat: ${neuralAction.combat} | Target: ${Math.round(goalDist)}m`;
      }
    }
  }

  findNearestSanctuary(px, pz, city) {
    const sanctuaries = [
      { x: -286.5, z: 159.4, name: 'CN Tower Peace Sanctuary' },
      { x: -245.0, z: -240.0, name: 'Pecaut Square' },
      { x: -203.9, z: 349.5, name: 'Roundhouse Park' },
      { x: 956.7, z: -534.9, name: 'St. Lawrence Market' },
      { x: 265.4, z: -128.9, name: 'Union Station' }
    ];
    let best = sanctuaries[0];
    let bestDist = Math.hypot(sanctuaries[0].x - px, sanctuaries[0].z - pz);
    for (let i = 1; i < sanctuaries.length; i++) {
      const d = Math.hypot(sanctuaries[i].x - px, sanctuaries[i].z - pz);
      if (d < bestDist) {
        bestDist = d;
        best = sanctuaries[i];
      }
    }
    return best;
  }

  buildObservation(player, state, city, enemies, traffic, gx, gz, goalType) {
    const obs = new Float32Array(56);
    const px = player.pos.x, pz = player.pos.z;

    // Convert Three.js player.yaw (0 = North/-Z) to 2D Cartesian heading (0 = East/+X)
    // Three.js forward = (-sin(yaw), -cos(yaw))
    // 2D Cartesian angle = atan2(forwardZ, forwardX)
    const forwardX = -Math.sin(player.yaw);
    const forwardZ = -Math.cos(player.yaw);
    const heading = Math.atan2(forwardZ, forwardX);

    // 1. Ego State (8)
    obs[0] = px / 1000.0;
    obs[1] = pz / 1000.0;
    obs[2] = Math.sin(heading);
    obs[3] = Math.cos(heading);
    obs[4] = (player.velocity ? player.velocity.x : 0) / 10.0;
    obs[5] = (player.velocity ? player.velocity.z : 0) / 10.0;
    obs[6] = state.health / 100.0;
    obs[7] = (state.rage || 0) / 100.0;

    // 2. Active Goal (8)
    const dx = gx - px, dz = gz - pz;
    const dist = Math.hypot(dx, dz);
    const relAng = Math.atan2(dz, dx) - heading;
    obs[8] = Math.max(-1.0, Math.min(1.0, dx / 500.0));
    obs[9] = Math.max(-1.0, Math.min(1.0, dz / 500.0));
    obs[10] = Math.tanh(dist / 50.0);
    obs[11] = Math.sin(relAng);
    obs[12] = Math.cos(relAng);
    obs[13] = goalType === 0 ? 1.0 : 0.0;
    obs[14] = goalType === 1 ? 1.0 : 0.0;
    obs[15] = goalType === 2 ? 1.0 : 0.0;

    // 3. 16-ray LiDAR distance probes (16)
    for (let i = 0; i < 16; i++) {
      const ang = heading + (i / 16.0) * Math.PI * 2.0;
      let d = 20.0;
      for (let r = 2.0; r <= 20.0; r += 2.0) {
        const rx = px + Math.cos(ang) * r;
        const rz = pz + Math.sin(ang) * r;
        if (city && !city.canMoveTo(rx, rz, 0.5, player.pos.y)) {
          d = r;
          break;
        }
      }
      obs[16 + i] = d / 20.0;
    }

    // 4. Top 3 Nearest Threats (12)
    const activeEnemies = [];
    if (enemies && enemies.length > 0) {
      for (let i = 0; i < enemies.length; i++) {
        const e = enemies[i];
        if (e.isDead || e.isKnockedOut || !e.rig) continue;
        const ePos = e.rig.root.position;
        const ed = Math.hypot(ePos.x - px, ePos.z - pz);
        activeEnemies.push({ x: ePos.x, z: ePos.z, dist: ed, hp: e.health || 100, maxHp: e.maxHealth || 100 });
      }
      activeEnemies.sort((a, b) => a.dist - b.dist);
    }
    for (let i = 0; i < 3; i++) {
      const baseIdx = 32 + i * 4;
      if (i < activeEnemies.length) {
        const e = activeEnemies[i];
        obs[baseIdx] = Math.max(-1.0, Math.min(1.0, (e.x - px) / 40.0));
        obs[baseIdx + 1] = Math.max(-1.0, Math.min(1.0, (e.z - pz) / 40.0));
        obs[baseIdx + 2] = Math.max(-1.0, Math.min(1.0, e.dist / 40.0));
        obs[baseIdx + 3] = e.hp / e.maxHp;
      }
    }

    // 5. Nearest Innocent / Pedestrian (4)
    let nearestCiv = null, minCivDist = 999.0;
    if (traffic && traffic.pedestrians) {
      for (let i = 0; i < traffic.pedestrians.length; i++) {
        const p = traffic.pedestrians[i];
        if (!p || !p.mesh) continue;
        const pPos = p.mesh.position;
        const cd = Math.hypot(pPos.x - px, pPos.z - pz);
        if (cd < minCivDist) {
          minCivDist = cd;
          nearestCiv = { x: pPos.x, z: pPos.z, dist: cd, isSnatched: !!p.isSnatched };
        }
      }
    }
    if (nearestCiv) {
      obs[44] = Math.max(-1.0, Math.min(1.0, (nearestCiv.x - px) / 40.0));
      obs[45] = Math.max(-1.0, Math.min(1.0, (nearestCiv.z - pz) / 40.0));
      obs[46] = Math.max(-1.0, Math.min(1.0, nearestCiv.dist / 40.0));
      obs[47] = nearestCiv.isSnatched ? 1.0 : 0.0;
    }

    // 6. Nearest Traffic Hazard (Car) (6)
    let nearestCar = null, minCarDist = 999.0;
    if (traffic && traffic.cars) {
      for (let i = 0; i < traffic.cars.length; i++) {
        const c = traffic.cars[i];
        if (!c || !c.mesh) continue;
        const cPos = c.mesh.position;
        const cd = Math.hypot(cPos.x - px, cPos.z - pz);
        if (cd < minCarDist) {
          minCarDist = cd;
          nearestCar = { x: cPos.x, z: cPos.z, dist: cd, vx: c.speed || 0, vz: 0 };
        }
      }
    }
    if (nearestCar) {
      obs[48] = Math.max(-1.0, Math.min(1.0, (nearestCar.x - px) / 40.0));
      obs[49] = Math.max(-1.0, Math.min(1.0, (nearestCar.z - pz) / 40.0));
      obs[50] = Math.max(-1.0, Math.min(1.0, nearestCar.vx / 15.0));
      obs[51] = Math.max(-1.0, Math.min(1.0, nearestCar.vz / 15.0));
      obs[52] = Math.max(-1.0, Math.min(1.0, nearestCar.dist / 40.0));
      obs[53] = 1.0 / (1.0 + nearestCar.dist / 10.0);
    }

    // 7. Nearest Peace Sanctuary (2)
    const sanc = this.findNearestSanctuary(px, pz, city);
    if (sanc) {
      obs[54] = Math.max(-1.0, Math.min(1.0, (sanc.x - px) / 500.0));
      obs[55] = Math.max(-1.0, Math.min(1.0, (sanc.z - pz) / 500.0));
    }

    return obs;
  }

  /**
   * Vanilla JS Forward Pass for LSTM(56, 128) + MLP(128 -> 64 -> 64 -> 15)
   */
  forwardPass(obs) {
    const w = this.modelData.weights;
    const hiddenDim = 128;

    // 1. LSTM Cell step
    // gates = W_ih * obs + W_hh * h + bias (size: 512 = 4 * 128 for i, f, g, o)
    const gates = new Float32Array(512);
    for (let i = 0; i < 512; i++) {
      let sum = w.lstm_bias[i];
      const row_ih = w.lstm_w_ih[i];
      for (let j = 0; j < 56; j++) {
        sum += row_ih[j] * obs[j];
      }
      const row_hh = w.lstm_w_hh[i];
      for (let j = 0; j < hiddenDim; j++) {
        sum += row_hh[j] * this.h[j];
      }
      gates[i] = sum;
    }

    // Activation of gates (PyTorch order: input, forget, cell/candidate, output)
    for (let i = 0; i < hiddenDim; i++) {
      const inGate = 1.0 / (1.0 + Math.exp(-gates[i]));
      const forgetGate = 1.0 / (1.0 + Math.exp(-gates[hiddenDim + i]));
      const cellCandidate = Math.tanh(gates[hiddenDim * 2 + i]);
      const outGate = 1.0 / (1.0 + Math.exp(-gates[hiddenDim * 3 + i]));

      this.c[i] = forgetGate * this.c[i] + inGate * cellCandidate;
      this.h[i] = outGate * Math.tanh(this.c[i]);
    }

    // 2. MLP Policy Layer 0 (128 -> 64) + Tanh
    const l0 = new Float32Array(64);
    for (let i = 0; i < 64; i++) {
      let sum = w.p0_b[i];
      const row = w.p0_w[i];
      for (let j = 0; j < hiddenDim; j++) {
        sum += row[j] * this.h[j];
      }
      l0[i] = Math.tanh(sum);
    }

    // 3. MLP Policy Layer 2 (64 -> 64) + Tanh
    const l2 = new Float32Array(64);
    for (let i = 0; i < 64; i++) {
      let sum = w.p2_b[i];
      const row = w.p2_w[i];
      for (let j = 0; j < 64; j++) {
        sum += row[j] * l0[j];
      }
      l2[i] = Math.tanh(sum);
    }

    // 4. Action Head (64 -> 15 logits)
    const logits = new Float32Array(15);
    for (let i = 0; i < 15; i++) {
      let sum = w.act_b[i];
      const row = w.act_w[i];
      for (let j = 0; j < 64; j++) {
        sum += row[j] * l2[j];
      }
      logits[i] = sum;
    }

    // MultiDiscrete: logits[0..8] for move, logits[9..14] for combat action
    let bestMove = 0, maxMoveLogit = -1e9;
    for (let i = 0; i < 9; i++) {
      if (logits[i] > maxMoveLogit) {
        maxMoveLogit = logits[i];
        bestMove = i;
      }
    }

    let bestCombat = 0, maxCombatLogit = -1e9;
    for (let i = 9; i < 15; i++) {
      if (logits[i] > maxCombatLogit) {
        maxCombatLogit = logits[i];
        bestCombat = i - 9;
      }
    }

    return { move: bestMove, combat: bestCombat };
  }

  executeAction(action, player, state, gx, gz) {
    // Exact move directions matching toronto_env.py MOVE_DIRS:
    // 0: Idle, 1: N (-Z), 2: NE, 3: E (+X), 4: SE, 5: S (+Z), 6: SW, 7: W (-X), 8: NW
    const moveVectors = [
      null,
      { x: 0.0, z: -1.0 },       // 1: North (-Z)
      { x: 0.7071, z: -0.7071 }, // 2: NE
      { x: 1.0, z: 0.0 },        // 3: East (+X)
      { x: 0.7071, z: 0.7071 },  // 4: SE
      { x: 0.0, z: 1.0 },        // 5: South (+Z)
      { x: -0.7071, z: 0.7071 }, // 6: SW
      { x: -1.0, z: 0.0 },       // 7: West (-X)
      { x: -0.7071, z: -0.7071 } // 8: NW
    ];

    if (action.move > 0 && moveVectors[action.move]) {
      const v = moveVectors[action.move];
      this.moveDir.set(v.x, 0, v.z);
      this.targetYaw = Math.atan2(-v.x, -v.z);
    } else {
      this.moveDir.set(0, 0, 0);
    }

    // Combat triggers
    if (action.combat === 1) {
      if (window.triggerAttack) window.triggerAttack();
    } else if (action.combat === 2) {
      if (window.triggerQuickKick) window.triggerQuickKick();
    } else if (action.combat === 3) {
      if (window.executeMeteorSlam) window.executeMeteorSlam();
    } else if (action.combat === 4) {
      if (window.triggerDodgeRoll) window.triggerDodgeRoll();
    }
  }

  /**
   * Tactical Heuristic Copilot: Navigates sidewalks, overpasses, evades cars,
   * strikes hostiles, executes glory kills, and heals at sanctuaries.
   */
  executeTacticalHeuristic(player, state, city, enemies, traffic, gx, gz, goalType, goalDist) {
    const px = player.pos.x, pz = player.pos.z, py = player.pos.y;

    // 1. Vehicle Collision Avoidance (Highest priority)
    let carHazard = null;
    if (traffic && traffic.cars) {
      for (let i = 0; i < traffic.cars.length; i++) {
        const car = traffic.cars[i];
        if (!car || !car.mesh) continue;
        const cPos = car.mesh.position;
        const d = Math.hypot(cPos.x - px, cPos.z - pz);
        if (d < 10.0) {
          carHazard = car;
          break;
        }
      }
    }

    if (carHazard) {
      this.aiIntentText = '⚠️ EVADING ONCOMING VEHICLE!';
      const cPos = carHazard.mesh.position;
      // Perpendicular escape vector
      const awayX = px - cPos.x;
      const awayZ = pz - cPos.z;
      const len = Math.hypot(awayX, awayZ) || 1.0;
      this.moveDir.set(awayX / len, 0, awayZ / len);
      this.targetYaw = Math.atan2(-this.moveDir.x, -this.moveDir.z);
      return;
    }

    // 2. Combat Execution when close to hostile
    let nearestHostile = null;
    let minEnemyDist = 999.0;
    if (enemies && enemies.length > 0) {
      for (let i = 0; i < enemies.length; i++) {
        const e = enemies[i];
        if (e.isDead || e.isKnockedOut || !e.rig) continue;
        const ed = Math.hypot(e.rig.root.position.x - px, e.rig.root.position.z - pz);
        if (ed < minEnemyDist) {
          minEnemyDist = ed;
          nearestHostile = e;
        }
      }
    }

    // Glory Kill stagger check
    if (state.gloryTarget && window.executeGloryKill) {
      this.aiIntentText = '💀 EXECUTING GLORY FINISHER!';
      window.executeGloryKill(state.gloryTarget);
      return;
    }

    // Melee attack triggers
    if (nearestHostile && minEnemyDist <= 3.2 && state.health > 25) {
      // Rotate to face enemy in Three.js coordinates
      const ex = nearestHostile.rig.root.position.x;
      const ez = nearestHostile.rig.root.position.z;
      this.targetYaw = Math.atan2(-(ex - px), -(ez - pz));

      // Perform meteor slam if surrounded or kick/punch
      if (minEnemyDist <= 2.2) {
        if (window.triggerAttack && state.attackTimer <= 0) {
          window.triggerAttack();
        }
      } else {
        if (window.triggerQuickKick && state.attackTimer <= 0) {
          window.triggerQuickKick();
        }
      }
    }

    // 3. Navigation towards Goal with Obstacle Avoidance
    const directDx = gx - px;
    const directDz = gz - pz;
    const dGoal = Math.hypot(directDx, directDz) || 1.0;

    let bestDir = null;
    let bestScore = -9999.0;

    // Probe 16 candidate headings
    for (let i = 0; i < 16; i++) {
      const ang = (i / 16.0) * Math.PI * 2.0;
      const candX = Math.cos(ang);
      const candZ = Math.sin(ang);

      // Alignment score with goal
      const dot = (candX * directDx + candZ * directDz) / dGoal;
      let score = dot * 2.0;

      // Check walkability 2.5m ahead
      const testX = px + candX * 2.5;
      const testZ = pz + candZ * 2.5;

      let walkable = true;
      if (city && !city.canMoveTo(testX, testZ, 0.6, py)) {
        walkable = false;
        score -= 10.0;
      }

      if (walkable && score > bestScore) {
        bestScore = score;
        bestDir = { x: candX, z: candZ };
      }
    }

    if (bestDir && dGoal > 1.2) {
      this.moveDir.set(bestDir.x, 0, bestDir.z);
      this.targetYaw = Math.atan2(-this.moveDir.x, -this.moveDir.z);
    } else if (dGoal > 1.2) {
      // Direct vector fallback so hero never gets stuck
      const directX = directDx / dGoal;
      const directZ = directDz / dGoal;
      this.moveDir.set(directX, 0, directZ);
      this.targetYaw = Math.atan2(-directX, -directZ);
    } else {
      this.moveDir.set(0, 0, 0);
    }
  }
}

// Global singleton instance
window.aiCopilot = new AICopilot();
