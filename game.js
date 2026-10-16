// ============================================================================
// FIST OF DOOM: BRUTAL BRAWLER - ENHANCED 3D ENGINE
// ============================================================================

// --- ENHANCED AUDIO SYNTHESIZER (Industrial Metal Riffs & Visceral FX) ---
class EnhancedRetroAudio {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
    this.musicTimer = null;
    this.isOCanada = false;
    this.oCanadaTimer = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioCtx();
      this.startMusic();
    } else if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playPunch(power = 1, isBerserk = false) {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;

    // Punch whoosh
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = isBerserk ? 'sawtooth' : 'triangle';
    osc.frequency.setValueAtTime(320 * power, t);
    osc.frequency.exponentialRampToValueAtTime(50, t + 0.14);
    gain.gain.setValueAtTime(0.4, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.14);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.15);
  }

  playImpact(type = 'punch') {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;

    // Meaty sub-bass boom
    const osc = this.ctx.createOscillator();
    const oscGain = this.ctx.createGain();
    osc.type = 'sine';

    // Crunchy bone noise
    const bufferSize = this.ctx.sampleRate * 0.2;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.04));
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    const noiseGain = this.ctx.createGain();

    if (type === 'kick') {
      osc.frequency.setValueAtTime(150, t);
      osc.frequency.exponentialRampToValueAtTime(25, t + 0.25);
      oscGain.gain.setValueAtTime(0.9, t);
      oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.25);
      noiseGain.gain.setValueAtTime(0.7, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);
    } else if (type === 'heavy') {
      osc.frequency.setValueAtTime(180, t);
      osc.frequency.exponentialRampToValueAtTime(30, t + 0.3);
      oscGain.gain.setValueAtTime(1.0, t);
      oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.3);
      noiseGain.gain.setValueAtTime(0.8, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.25);
    } else if (type === 'slam') {
      // Massive earthquake ground boom
      osc.frequency.setValueAtTime(240, t);
      osc.frequency.exponentialRampToValueAtTime(18, t + 0.7);
      oscGain.gain.setValueAtTime(1.2, t);
      oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.7);
      noiseGain.gain.setValueAtTime(1.1, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.5);
    } else if (type === 'glory') {
      // Brutal squelch / execution snap
      osc.frequency.setValueAtTime(280, t);
      osc.frequency.exponentialRampToValueAtTime(40, t + 0.4);
      oscGain.gain.setValueAtTime(1.1, t);
      oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.4);
      noiseGain.gain.setValueAtTime(1.0, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.35);
    } else {
      // Standard punch
      osc.frequency.setValueAtTime(200, t);
      osc.frequency.exponentialRampToValueAtTime(45, t + 0.16);
      oscGain.gain.setValueAtTime(0.65, t);
      oscGain.gain.exponentialRampToValueAtTime(0.01, t + 0.16);
      noiseGain.gain.setValueAtTime(0.5, t);
      noiseGain.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
    }

    osc.connect(oscGain);
    oscGain.connect(this.ctx.destination);
    noise.connect(noiseGain);
    noiseGain.connect(this.ctx.destination);

    osc.start(t);
    osc.stop(t + 0.75);
    noise.start(t);
  }

  playHockeySlapshot() {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;

    // 1. Sharp composite wood crack
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(950, t);
    osc.frequency.exponentialRampToValueAtTime(70, t + 0.08);
    gain.gain.setValueAtTime(0.65, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.1);

    // 2. High-impact noise slap (puck / slapshot impact)
    const bufSize = Math.floor(this.ctx.sampleRate * 0.15);
    const buf = this.ctx.createBuffer(1, bufSize, this.ctx.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.02));
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = buf;
    const nGain = this.ctx.createGain();
    nGain.gain.setValueAtTime(0.55, t);
    nGain.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
    noise.connect(nGain);
    nGain.connect(this.ctx.destination);
    noise.start(t);

    // 3. Deep bass reverberation
    const subOsc = this.ctx.createOscillator();
    const subGain = this.ctx.createGain();
    subOsc.type = 'sine';
    subOsc.frequency.setValueAtTime(120, t);
    subOsc.frequency.exponentialRampToValueAtTime(32, t + 0.28);
    subGain.gain.setValueAtTime(0.85, t);
    subGain.gain.exponentialRampToValueAtTime(0.01, t + 0.28);
    subOsc.connect(subGain);
    subGain.connect(this.ctx.destination);
    subOsc.start(t);
    subOsc.stop(t + 0.3);
  }

  playCrateSmash() {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;
    const bufferSize = this.ctx.sampleRate * 0.3;
    const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (this.ctx.sampleRate * 0.07));
    }
    const noise = this.ctx.createBufferSource();
    noise.buffer = buffer;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass';
    filter.frequency.setValueAtTime(1400, t);
    filter.frequency.exponentialRampToValueAtTime(250, t + 0.28);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(0.8, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.3);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.ctx.destination);
    noise.start(t);
  }

  playExplosion() {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(100, t);
    osc.frequency.exponentialRampToValueAtTime(20, t + 0.8);
    gain.gain.setValueAtTime(1.0, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.8);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.85);
  }

  playPickup() {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;
    const chords = [330, 440, 554.37, 659.25, 880];
    chords.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(freq, t + idx * 0.05);
      gain.gain.setValueAtTime(0.2, t + idx * 0.05);
      gain.gain.exponentialRampToValueAtTime(0.01, t + idx * 0.05 + 0.18);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(t + idx * 0.05);
      osc.stop(t + idx * 0.05 + 0.19);
    });
  }

  playBerserkRage() {
    if (!this.ctx || this.isMuted) return;
    const t = this.ctx.currentTime;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(80, t);
    osc.frequency.linearRampToValueAtTime(320, t + 0.4);
    gain.gain.setValueAtTime(0.5, t);
    gain.gain.exponentialRampToValueAtTime(0.01, t + 0.5);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + 0.55);
  }

  startMusic() {
    if (this.musicTimer || !this.ctx || this.isOCanada) return;
    // Heavy Industrial Bass & Kick/Snare pattern (DOOM style)
    const tempo = 132;
    const beat = 60 / tempo;
    const bassline = [36, 36, 39, 36, 42, 36, 39, 38];
    let step = 0;

    const tick = () => {
      if (!this.ctx || this.ctx.state !== 'running' || this.isOCanada) return;
      const t = this.ctx.currentTime;

      // Heavy Kick on beat 0, 2
      if (step % 4 === 0) {
        const kOsc = this.ctx.createOscillator();
        const kGain = this.ctx.createGain();
        kOsc.frequency.setValueAtTime(130, t);
        kOsc.frequency.exponentialRampToValueAtTime(35, t + 0.09);
        kGain.gain.setValueAtTime(0.25, t);
        kGain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);
        kOsc.connect(kGain);
        kGain.connect(this.ctx.destination);
        kOsc.start(t);
        kOsc.stop(t + 0.1);
      }

      // Snare on beat 2, 6
      if (step % 8 === 4) {
        const sBuf = this.ctx.createBuffer(1, Math.floor(this.ctx.sampleRate * 0.1), this.ctx.sampleRate);
        const sData = sBuf.getChannelData(0);
        for (let i = 0; i < sData.length; i++) sData[i] = (Math.random() * 2 - 1) * Math.exp(-i / 800);
        const sNoise = this.ctx.createBufferSource();
        sNoise.buffer = sBuf;
        const sGain = this.ctx.createGain();
        sGain.gain.setValueAtTime(0.18, t);
        sGain.gain.exponentialRampToValueAtTime(0.01, t + 0.1);
        sNoise.connect(sGain);
        sGain.connect(this.ctx.destination);
        sNoise.start(t);
      }

      // Distorted Guitar Bass
      const osc = this.ctx.createOscillator();
      const filter = this.ctx.createBiquadFilter();
      const gain = this.ctx.createGain();

      const note = bassline[step % bassline.length];
      const freq = 440 * Math.pow(2, (note - 69) / 12);

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, t);

      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1200, t);
      filter.frequency.exponentialRampToValueAtTime(300, t + beat * 0.45);

      gain.gain.setValueAtTime(0.09, t);
      gain.gain.exponentialRampToValueAtTime(0.005, t + beat * 0.45);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start(t);
      osc.stop(t + beat * 0.48);

      step++;
    };

    this.musicTimer = setInterval(tick, (beat / 2) * 1000);
  }

  stopMusic() {
    if (this.musicTimer) {
      clearInterval(this.musicTimer);
      this.musicTimer = null;
    }
  }

  startOCanada() {
    if (!this.ctx || this.isMuted) return;
    this.stopMusic();
    this.stopOCanada();
    this.isOCanada = true;

    // "O Canada" National Anthem in E♭ Major (+3 semitones from C Major)
    // 4/4 Time, 88 BPM Marching Cadence
    // Measure-by-Measure Timing Grid matching official vocal/band score:
    const O_CANADA_MELODY = [
      // Bar 1: "O Canada! Our home and native land!"
      { note: 67, len: 2, bass: 39, chord: 51 },  // G4
      { note: 70, len: 1.5, bass: 39, chord: 51 },  // Bb4
      { note: 70, len: 0.5, bass: 39, chord: 51 },  // Bb4
      { note: 63, len: 3, bass: 39, chord: 51 },  // Eb4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 68, len: 1, bass: 41, chord: 53 },  // Ab4
      { note: 70, len: 1, bass: 39, chord: 51 },  // Bb4
      { note: 72, len: 1, bass: 44, chord: 56 },  // C5
      { note: 65, len: 4, bass: 46, chord: 58 },  // F4
      // Bar 5: "True patriot love in all of us command."
      { note: 67, len: 2, bass: 39, chord: 51 },  // G4
      { note: 69, len: 1.5, bass: 41, chord: 53 },  // A4
      { note: 69, len: 0.5, bass: 41, chord: 53 },  // A4
      { note: 70, len: 3, bass: 46, chord: 58 },  // Bb4
      { note: 72, len: 1, bass: 41, chord: 53 },  // C5
      { note: 74, len: 1, bass: 46, chord: 58 },  // D5
      { note: 74, len: 1, bass: 46, chord: 58 },  // D5
      { note: 72, len: 1, bass: 41, chord: 53 },  // C5
      { note: 72, len: 1, bass: 41, chord: 53 },  // C5
      // Bar 8: last 2 notes = pickup into "With glowing hearts ... The True North strong and free!"
      { note: 70, len: 3, bass: 46, chord: 58 },  // Bb4
      { note: 65, len: 0.75, bass: 46, chord: 58 }, // F4
      { note: 67, len: 0.25, bass: 46, chord: 58 }, // G4
      { note: 68, len: 1.5, bass: 46, chord: 58 },  // Ab4
      { note: 67, len: 0.5, bass: 46, chord: 58 },  // G4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 67, len: 0.75, bass: 46, chord: 58 }, // G4
      { note: 68, len: 0.25, bass: 46, chord: 58 }, // Ab4
      { note: 70, len: 1.5, bass: 39, chord: 51 },  // Bb4
      { note: 68, len: 0.5, bass: 39, chord: 51 },  // Ab4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 68, len: 0.75, bass: 39, chord: 51 }, // Ab4
      { note: 70, len: 0.25, bass: 39, chord: 51 }, // Bb4
      { note: 72, len: 1, bass: 44, chord: 56 },  // C5
      { note: 70, len: 1, bass: 39, chord: 51 },  // Bb4
      { note: 68, len: 1, bass: 46, chord: 58 },  // Ab4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      // Bar 12: last 2 notes = pickup into "From far and wide ... We stand on guard for thee."
      { note: 65, len: 3, bass: 46, chord: 58 },  // F4
      { note: 65, len: 0.75, bass: 46, chord: 58 }, // F4
      { note: 67, len: 0.25, bass: 46, chord: 58 }, // G4
      { note: 68, len: 1.5, bass: 46, chord: 58 },  // Ab4
      { note: 67, len: 0.5, bass: 46, chord: 58 },  // G4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 67, len: 0.75, bass: 46, chord: 58 }, // G4
      { note: 68, len: 0.25, bass: 46, chord: 58 }, // Ab4
      { note: 70, len: 1.5, bass: 39, chord: 51 },  // Bb4
      { note: 68, len: 0.5, bass: 39, chord: 51 },  // Ab4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 70, len: 1, bass: 46, chord: 58 },  // Bb4
      { note: 70, len: 0.5, bass: 41, chord: 53 },  // Bb4
      { note: 69, len: 0.5, bass: 41, chord: 53 },  // A4
      { note: 67, len: 0.5, bass: 41, chord: 53 },  // G4
      { note: 69, len: 0.5, bass: 41, chord: 53 },  // A4
      { note: 70, len: 4, bass: 46, chord: 58 },  // Bb4
      // Bar 17: "God keep our land glorious and free!"
      { note: 67, len: 2, bass: 39, chord: 51 },  // G4
      { note: 70, len: 1.5, bass: 39, chord: 51 },  // Bb4
      { note: 70, len: 0.5, bass: 39, chord: 51 },  // Bb4
      { note: 63, len: 4, bass: 48, chord: 60 },  // Eb4
      { note: 68, len: 2, bass: 44, chord: 56 },  // Ab4
      { note: 72, len: 1.5, bass: 44, chord: 56 },  // C5
      { note: 72, len: 0.5, bass: 44, chord: 56 },  // C5
      { note: 65, len: 4, bass: 46, chord: 58 },  // F4
      // Bar 21: "O Canada, we stand on guard for thee."
      { note: 70, len: 2, bass: 39, chord: 51 },  // Bb4
      { note: 71, len: 1.5, bass: 43, chord: 55 },  // B4
      { note: 71, len: 0.5, bass: 43, chord: 55 },  // B4
      { note: 72, len: 1, bass: 48, chord: 60 },  // C5
      { note: 68, len: 1, bass: 41, chord: 53 },  // Ab4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 63, len: 2, bass: 39, chord: 51 },  // Eb4
      { note: 65, len: 2, bass: 46, chord: 58 },  // F4
      { note: 67, len: 4, bass: 39, chord: 51 },  // G4
      // Bar 25: "O Canada, we stand on guard for thee." (final)
      { note: 70, len: 2, bass: 39, chord: 51 },  // Bb4
      { note: 75, len: 1.5, bass: 43, chord: 55 },  // Eb5
      { note: 75, len: 0.5, bass: 43, chord: 55 },  // Eb5
      { note: 72, len: 1, bass: 44, chord: 56 },  // C5
      { note: 68, len: 1, bass: 41, chord: 53 },  // Ab4
      { note: 67, len: 1, bass: 39, chord: 51 },  // G4
      { note: 65, len: 1, bass: 46, chord: 58 },  // F4
      { note: 70, len: 2, bass: 39, chord: 51 },  // Bb4
      { note: 62, len: 2, bass: 46, chord: 58 },  // D4
      { note: 63, len: 4, bass: 39, chord: 51 }   // Eb4
    ];

    const beatDur = 60 / 88;
    let idx = 0;

    const playStep = () => {
      if (!this.isOCanada || !this.ctx || this.ctx.state !== 'running') return;
      const cur = O_CANADA_MELODY[idx % O_CANADA_MELODY.length];
      const dur = cur.len * beatDur;
      const t = this.ctx.currentTime;

      // Heroic dual-oscillator lead with fat chorus
      const o1 = this.ctx.createOscillator();
      const o2 = this.ctx.createOscillator();
      const filt = this.ctx.createBiquadFilter();
      const g = this.ctx.createGain();

      const f = 440 * Math.pow(2, (cur.note - 69) / 12);
      o1.type = 'sawtooth';
      o1.frequency.setValueAtTime(f, t);

      o2.type = 'square';
      o2.frequency.setValueAtTime(f * 1.004, t);

      filt.type = 'lowpass';
      filt.frequency.setValueAtTime(1800, t);
      filt.frequency.exponentialRampToValueAtTime(800, t + dur * 0.9);

      g.gain.setValueAtTime(0.22, t);
      g.gain.setValueAtTime(0.20, t + dur * 0.85);
      g.gain.exponentialRampToValueAtTime(0.005, t + dur * 0.98);

      o1.connect(filt);
      o2.connect(filt);
      filt.connect(g);
      g.connect(this.ctx.destination);

      o1.start(t);
      o2.start(t);
      o1.stop(t + dur);
      o2.stop(t + dur);

      // Harmony chord
      if (cur.chord) {
        const co = this.ctx.createOscillator();
        const cg = this.ctx.createGain();
        co.type = 'sawtooth';
        co.frequency.setValueAtTime(440 * Math.pow(2, (cur.chord - 69) / 12), t);
        cg.gain.setValueAtTime(0.08, t);
        cg.gain.exponentialRampToValueAtTime(0.005, t + dur * 0.9);
        co.connect(cg);
        cg.connect(this.ctx.destination);
        co.start(t);
        co.stop(t + dur);
      }

      // Heavy bass note
      if (cur.bass) {
        const bo = this.ctx.createOscillator();
        const bg = this.ctx.createGain();
        bo.type = 'triangle';
        bo.frequency.setValueAtTime(440 * Math.pow(2, (cur.bass - 69) / 12), t);
        bg.gain.setValueAtTime(0.22, t);
        bg.gain.exponentialRampToValueAtTime(0.01, t + dur * 0.85);
        bo.connect(bg);
        bg.connect(this.ctx.destination);
        bo.start(t);
        bo.stop(t + dur);
      }

      // Stadium rock kick drum
      const ko = this.ctx.createOscillator();
      const kg = this.ctx.createGain();
      ko.frequency.setValueAtTime(140, t);
      ko.frequency.exponentialRampToValueAtTime(36, t + 0.12);
      kg.gain.setValueAtTime(0.28, t);
      kg.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
      ko.connect(kg);
      kg.connect(this.ctx.destination);
      ko.start(t);
      ko.stop(t + 0.13);

      idx++;
      this.oCanadaTimer = setTimeout(playStep, dur * 1000);
    };

    playStep();
  }

  stopOCanada() {
    this.isOCanada = false;
    if (this.oCanadaTimer) {
      clearTimeout(this.oCanadaTimer);
      this.oCanadaTimer = null;
    }
  }

  playPeaceChime() {
    if (!this.ctx || this.isMuted) return;
    try {
      const t = this.ctx.currentTime;
      [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, t + i * 0.08);
        gain.gain.setValueAtTime(0.2, t + i * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, t + i * 0.08 + 0.45);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t + i * 0.08);
        osc.stop(t + i * 0.08 + 0.48);
      });
    } catch (err) { }
  }
}

const audio = new EnhancedRetroAudio();

// ============================================================================
// ATTACK CONFIGURATION & GAME STATE
// ============================================================================
const ATTACKS = {
  JAB: {
    id: 1,
    name: 'BARE KNUCKLES',
    sub: 'RAPID JABS [L-CLICK / F]',
    damage: 30,
    range: 3.5,
    cooldown: 0.22,
    knockback: 6,
    type: 'punch',
    color: '#ffcc00'
  },
  HOOK: {
    id: 2,
    name: 'BRASS KNUCKLES',
    sub: 'THUNDER HOOK [L-CLICK / F]',
    damage: 75,
    range: 3.8,
    cooldown: 0.42,
    knockback: 16,
    type: 'heavy',
    color: '#ff5500'
  },
  KICK: {
    id: 3,
    name: 'MIGHTY BOOT',
    sub: 'FRONT KICK [L-CLICK / E]',
    damage: 100,
    range: 4.2,
    cooldown: 0.55,
    knockback: 32,
    type: 'kick',
    color: '#00f0ff'
  },
  SLAM: {
    id: 4,
    name: 'METEOR SLAM GAUNTLET',
    sub: 'JUMP + PUNCH [L-CLICK IN AIR]',
    damage: 260,
    range: 8.5, // Large AoE
    cooldown: 0.95,
    knockback: 45,
    type: 'slam',
    color: '#ea80fc'
  }
};

// ============================================================================
// DIFFICULTY CONFIGURATIONS
// ============================================================================
const DIFFICULTY_CONFIGS = {
  easy: {
    key: 'easy',
    name: 'EASY',
    sub: 'TOURIST',
    tagClass: 'tag-green',
    targetEnemies: 14,
    hpMult: 0.7,
    speedMult: 0.85,
    damageMult: 0.65,
    attackCooldownMult: 1.4,
    aggroDist: 24,
    spawnInterval: 5.5,
    maxAlive: 14
  },
  medium: {
    key: 'medium',
    name: 'MEDIUM',
    sub: 'BRAWLER',
    tagClass: 'tag-cyan',
    targetEnemies: 30,
    hpMult: 1.0,
    speedMult: 1.0,
    damageMult: 1.0,
    attackCooldownMult: 1.0,
    aggroDist: 35,
    spawnInterval: 3.5,
    maxAlive: 30
  },
  hard: {
    key: 'hard',
    name: 'HARD',
    sub: 'BRUTAL',
    tagClass: 'tag-yellow',
    targetEnemies: 52,
    hpMult: 1.35,
    speedMult: 1.15,
    damageMult: 1.4,
    attackCooldownMult: 0.8,
    aggroDist: 48,
    spawnInterval: 2.2,
    maxAlive: 52
  },
  impossible: {
    key: 'impossible',
    name: 'IMPOSSIBLE',
    sub: 'TORONTO MAYHEM',
    tagClass: 'tag-red',
    targetEnemies: 88,
    hpMult: 1.75,
    speedMult: 1.35,
    damageMult: 1.9,
    attackCooldownMult: 0.6,
    aggroDist: 65,
    spawnInterval: 1.2,
    maxAlive: 88
  }
};
const DIFFICULTY_ORDER = ['easy', 'medium', 'hard', 'impossible'];

const state = {
  health: 100,
  maxHealth: 100,
  armor: 50,
  maxArmor: 100,
  score: 0,
  kills: 0,
  boxesSmashed: 0,
  totalBoxes: 8,
  difficulty: 'medium',
  spawnTimer: 0,
  activeAttack: ATTACKS.JAB,
  unlocked: {
    [ATTACKS.JAB.id]: true,
    [ATTACKS.HOOK.id]: false,
    [ATTACKS.KICK.id]: false,
    [ATTACKS.SLAM.id]: false
  },
  rage: 0,
  isBerserk: false,
  berserkTimer: 0,
  comboCount: 0,
  comboTimer: 0,
  isAttacking: false,
  attackProgress: 0,
  attackTimer: 0,
  currentAnimType: 'jab',
  screenShake: 0,
  faceExpression: 'neutral',
  faceTimer: 0,
  inGame: false,
  isPaused: false,
  freeMouseMode: false,
  isPointerLocked: false,
  isDead: false,
  gloryTarget: null,
  wasInsidePeace: false
};

// ============================================================================
// THREE.JS SETUP & 3D TORONTO OPEN-WORLD ARENA
// ============================================================================
const container = document.getElementById('game-container');
const scene = new THREE.Scene();

// Far clip increased to 2500m to render CN Tower (553m) and downtown skyline
const camera = new THREE.PerspectiveCamera(78, window.innerWidth / window.innerHeight, 0.1, 2500);
camera.position.set(0, 1.7, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.insertBefore(renderer.domElement, container.firstChild);

// Build Toronto City from real OpenStreetMap data with CN Tower Peace Sanctuary
const city = (typeof window.buildTorontoCity === 'function') ? window.buildTorontoCity(scene) : null;

const player = {
  pos: camera.position,
  velocity: new THREE.Vector3(),
  yaw: 0,
  pitch: 0,
  isGrounded: true,
  bobTimer: 0,
  speed: 7.0,
  sprintSpeed: 11.5,
  jumpStrength: 9.0
};

// Spawn player on Front St facing CN Tower if Toronto City is loaded
if (city && city.start) {
  player.pos.set(city.start.x, 1.7, city.start.z);
  player.yaw = city.startYaw;
  camera.rotation.order = 'YXZ';
  camera.rotation.y = city.startYaw;
}

// Colliders array (for fallback or supplemental obstacles)
const colliders = [];

// Texture Generators
function createProceduralTexture(type) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  if (type === 'wall') {
    ctx.fillStyle = '#1c202a';
    ctx.fillRect(0, 0, 256, 256);
    ctx.strokeStyle = '#2d3345';
    ctx.lineWidth = 6;
    ctx.strokeRect(4, 4, 248, 248);
  } else if (type === 'floor') {
    ctx.fillStyle = '#111318';
    ctx.fillRect(0, 0, 256, 256);
  } else if (type === 'crate') {
    ctx.fillStyle = '#8b5a2b';
    ctx.fillRect(0, 0, 256, 256);
    ctx.fillStyle = '#5c3818';
    ctx.fillRect(12, 12, 232, 232);
    ctx.strokeStyle = '#3d2510';
    ctx.lineWidth = 14;
    ctx.strokeRect(8, 8, 240, 240);
    ctx.beginPath();
    ctx.moveTo(8, 8); ctx.lineTo(248, 248);
    ctx.moveTo(248, 8); ctx.lineTo(8, 248);
    ctx.stroke();
    ctx.fillStyle = '#ffea00';
    ctx.font = 'bold 36px monospace';
    ctx.textAlign = 'center';
    ctx.fillText('SUPPLY', 128, 140);
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.magFilter = THREE.LinearFilter;
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  return texture;
}

const crateTex = createProceduralTexture('crate');

if (city) {
  // Atmospheric Toronto Night Skyline Lighting & Fog
  scene.fog = new THREE.FogExp2(0x0a0c12, 0.0022);

  const ambLight = new THREE.AmbientLight(0x424c5e, 1.8);
  scene.add(ambLight);

  const moonLight = new THREE.DirectionalLight(0xa5c4e8, 1.25);
  moonLight.position.set(150, 350, 180);
  scene.add(moonLight);
} else {
  // Fallback Indoor Enclosed Arena if map data failed to load
  scene.fog = new THREE.FogExp2(0x0a0c12, 0.038);
  const ambLight = new THREE.AmbientLight(0x2a2f3d, 1.4);
  scene.add(ambLight);

  const mainLight = new THREE.PointLight(0xff4422, 2.8, 45);
  mainLight.position.set(0, 6, 0);
  scene.add(mainLight);

  const floorTex = createProceduralTexture('floor');
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(90, 90), new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.7 }));
  floor.rotation.x = -Math.PI / 2;
  scene.add(floor);

  const wallTex = createProceduralTexture('wall');
  const wallMat = new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.65 });
  function addWall(x, z, width, depth, height = 6.2) {
    const wall = new THREE.Mesh(new THREE.BoxGeometry(width, height, depth), wallMat);
    wall.position.set(x, height / 2, z);
    scene.add(wall);
    colliders.push({ box: new THREE.Box3().setFromObject(wall), mesh: wall });
  }
  addWall(0, -40, 80, 2.5); addWall(0, 40, 80, 2.5);
  addWall(-40, 0, 2.5, 80); addWall(40, 0, 2.5, 80);
}

// ============================================================================
// 3D FIRST-PERSON ARMS & WEAPON VIEWMODEL (Attached to Camera!)
// ============================================================================
const armsRig = new THREE.Group();
camera.add(armsRig);
scene.add(camera);

// Build procedural 3D Arm & Knuckle Mesh
function buildArmMesh(isLeft = false) {
  const armGroup = new THREE.Group();

  // Forearm with combat glove
  const armGeo = new THREE.CylinderGeometry(0.09, 0.12, 0.7, 8);
  const gloveMat = new THREE.MeshStandardMaterial({
    color: 0x1e2430,
    roughness: 0.5,
    metalness: 0.4
  });
  const arm = new THREE.Mesh(armGeo, gloveMat);
  arm.rotation.x = Math.PI / 2.3;
  arm.position.set(0, -0.15, -0.25);
  armGroup.add(arm);

  // Armored Fist Clump
  const fistGeo = new THREE.BoxGeometry(0.18, 0.18, 0.24);
  const fistMat = new THREE.MeshStandardMaterial({
    color: 0x2b3342,
    roughness: 0.4,
    metalness: 0.6
  });
  const fist = new THREE.Mesh(fistGeo, fistMat);
  fist.position.set(0, -0.05, -0.55);
  armGroup.add(fist);

  // Brass / Steel Knuckles Spikes
  const spikeGeo = new THREE.ConeGeometry(0.025, 0.08, 6);
  const spikeMat = new THREE.MeshStandardMaterial({
    color: 0xf59e0b,
    metalness: 0.9,
    roughness: 0.2
  });

  [-0.06, -0.02, 0.02, 0.06].forEach(sX => {
    const spike = new THREE.Mesh(spikeGeo, spikeMat);
    spike.rotation.x = -Math.PI / 2;
    spike.position.set(sX, -0.02, -0.68);
    armGroup.add(spike);
  });

  return armGroup;
}

// Right & Left Arms
const rightArm = buildArmMesh(false);
rightArm.position.set(0.32, -0.28, -0.2);
armsRig.add(rightArm);

const leftArm = buildArmMesh(true);
leftArm.position.set(-0.32, -0.28, -0.2);
armsRig.add(leftArm);

// Combat Boot for Mighty Kick
const bootGroup = new THREE.Group();
const bootGeo = new THREE.BoxGeometry(0.24, 0.32, 0.6);
const bootMat = new THREE.MeshStandardMaterial({
  color: 0x111620,
  roughness: 0.6,
  metalness: 0.3
});
const bootMesh = new THREE.Mesh(bootGeo, bootMat);
bootGroup.add(bootMesh);

// Steel toe
const toeGeo = new THREE.BoxGeometry(0.26, 0.14, 0.16);
const toeMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8, roughness: 0.2 });
const toeMesh = new THREE.Mesh(toeGeo, toeMat);
toeMesh.position.set(0, -0.08, 0.32);
bootGroup.add(toeMesh);

bootGroup.position.set(0, -1.2, -0.5);
bootGroup.visible = false;
armsRig.add(bootGroup);

// Canadian Hockey Stick for Berserk Rage Mode
function buildHockeyStickMesh() {
  const stickGroup = new THREE.Group();

  const mapleMat = new THREE.MeshStandardMaterial({
    color: 0xdfad7b,
    roughness: 0.4,
    metalness: 0.1
  });
  const carbonMat = new THREE.MeshStandardMaterial({
    color: 0x242426,
    roughness: 0.35,
    metalness: 0.3
  });
  const redMat = new THREE.MeshStandardMaterial({
    color: 0xd90429, // Team Canada Crimson Red
    roughness: 0.35,
    metalness: 0.2
  });
  const whiteTapeMat = new THREE.MeshStandardMaterial({
    color: 0xf4f4f5, // Hockey friction tape
    roughness: 0.85,
    metalness: 0.05
  });
  const blackBladeMat = new THREE.MeshStandardMaterial({
    color: 0x18181b, // Black cloth tape on blade
    roughness: 0.9,
    metalness: 0.05
  });
  const gloveMat = new THREE.MeshStandardMaterial({
    color: 0xb91c1c, // Red Canadian Hockey Glove
    roughness: 0.55,
    metalness: 0.2
  });
  const gloveCuffMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.6,
    metalness: 0.1
  });

  // 1. RECTANGULAR COMPOSITE SHAFT
  // Length from y = -0.55 up to y = +0.40 (total 0.95m)
  const shaftGeo = new THREE.BoxGeometry(0.032, 0.95, 0.022);
  const shaft = new THREE.Mesh(shaftGeo, carbonMat);
  shaft.position.set(0, -0.05, 0);
  stickGroup.add(shaft);

  // Maple wood face inlay along front of shaft
  const inlayGeo = new THREE.BoxGeometry(0.028, 0.92, 0.003);
  const inlay = new THREE.Mesh(inlayGeo, mapleMat);
  inlay.position.set(0, -0.05, 0.011);
  stickGroup.add(inlay);

  // Butt-end grip tape at bottom handle
  const buttKnob = new THREE.Mesh(new THREE.BoxGeometry(0.038, 0.06, 0.028), whiteTapeMat);
  buttKnob.position.set(0, -0.52, 0);
  stickGroup.add(buttKnob);

  const buttGrip = new THREE.Mesh(new THREE.BoxGeometry(0.035, 0.18, 0.025), whiteTapeMat);
  buttGrip.position.set(0, -0.42, 0);
  stickGroup.add(buttGrip);

  // Canadian Decals & Racing Stripes on upper shaft
  const stripeGeo1 = new THREE.BoxGeometry(0.035, 0.08, 0.025);
  const stripe1 = new THREE.Mesh(stripeGeo1, redMat);
  stripe1.position.set(0, 0.10, 0);
  stickGroup.add(stripe1);

  const stripeGeo2 = new THREE.BoxGeometry(0.035, 0.03, 0.025);
  const stripe2 = new THREE.Mesh(stripeGeo2, whiteTapeMat);
  stripe2.position.set(0, 0.16, 0);
  stickGroup.add(stripe2);

  const stripeGeo3 = new THREE.BoxGeometry(0.035, 0.08, 0.025);
  const stripe3 = new THREE.Mesh(stripeGeo3, redMat);
  stripe3.position.set(0, 0.22, 0);
  stickGroup.add(stripe3);

  // 2. THE TOP: HOSEL, HEEL & DISTINCTIVE UPRIGHT CURVED HOCKEY BLADE!
  const bladeGroup = new THREE.Group();
  bladeGroup.position.set(0, 0.40, 0);

  // Hosel (shaft to heel transition angle)
  const hoselGeo = new THREE.BoxGeometry(0.028, 0.10, 0.024);
  const hosel = new THREE.Mesh(hoselGeo, carbonMat);
  hosel.position.set(-0.025, 0.045, -0.01);
  hosel.rotation.set(-0.15, -0.35, 0.65);
  bladeGroup.add(hosel);

  // The Blade: Stands upright with vertical height ~0.082m, thin width ~0.013m
  // Sweeps outward to the left and curves forward (shooter hook)
  const bladeSegments = [
    { dx: -0.065, dy: 0.075, dz: -0.035, len: 0.09, ry: -0.55, rz: 0.25, h: 0.082 },
    { dx: -0.135, dy: 0.092, dz: -0.085, len: 0.09, ry: -0.85, rz: 0.16, h: 0.080 },
    { dx: -0.195, dy: 0.102, dz: -0.150, len: 0.09, ry: -1.18, rz: 0.08, h: 0.078 },
    { dx: -0.235, dy: 0.106, dz: -0.225, len: 0.09, ry: -1.52, rz: 0.02, h: 0.075 }
  ];

  bladeSegments.forEach((seg) => {
    // Blade core (black composite)
    const bGeo = new THREE.BoxGeometry(0.013, seg.h, seg.len);
    const bMesh = new THREE.Mesh(bGeo, blackBladeMat);
    bMesh.position.set(seg.dx, seg.dy, seg.dz);
    bMesh.rotation.set(0.05, seg.ry, seg.rz);
    bladeGroup.add(bMesh);

    // White cloth tape wraps around each segment
    const tapeGeo = new THREE.BoxGeometry(0.015, seg.h + 0.002, 0.035);
    const tapeMesh = new THREE.Mesh(tapeGeo, whiteTapeMat);
    tapeMesh.position.set(seg.dx, seg.dy, seg.dz);
    tapeMesh.rotation.set(0.05, seg.ry, seg.rz);
    bladeGroup.add(tapeMesh);
  });

  // Rounded Toe at tip (Segment 4 end)
  const toeGeo = new THREE.CylinderGeometry(0.037, 0.037, 0.013, 16);
  const toeMesh = new THREE.Mesh(toeGeo, blackBladeMat);
  toeMesh.position.set(-0.245, 0.106, -0.275);
  toeMesh.rotation.set(0.05, -1.55, Math.PI / 2);
  bladeGroup.add(toeMesh);

  // Red Maple Leaf accent badge on the heel
  const badgeGeo = new THREE.BoxGeometry(0.015, 0.045, 0.045);
  const badgeMesh = new THREE.Mesh(badgeGeo, redMat);
  badgeMesh.position.set(-0.065, 0.075, -0.035);
  badgeMesh.rotation.set(0.05, -0.55, 0.25);
  bladeGroup.add(badgeMesh);

  stickGroup.add(bladeGroup);

  // 3. TWO CANADIAN HOCKEY GLOVES AT HANDLE (BOTTOM)
  // Lower hand (near butt end, y = -0.36)
  const buttGlove = new THREE.Group();
  const bgFist = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.15), gloveMat);
  const bgCuff = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.14, 0.13), gloveCuffMat);
  bgCuff.position.set(0.02, -0.08, 0);
  buttGlove.add(bgFist);
  buttGlove.add(bgCuff);
  buttGlove.position.set(0, -0.36, 0);
  stickGroup.add(buttGlove);

  // Upper hand (guide/power hand, y = -0.12)
  const powerGlove = new THREE.Group();
  const pgFist = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.12, 0.15), gloveMat);
  const pgCuff = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.14, 0.13), gloveCuffMat);
  pgCuff.position.set(0.02, -0.08, 0);
  powerGlove.add(pgFist);
  powerGlove.add(pgCuff);
  powerGlove.position.set(0, -0.12, 0);
  stickGroup.add(powerGlove);

  // First-person idle stance
  stickGroup.position.set(0.22, -0.26, -0.44);
  stickGroup.rotation.set(-0.22, -0.42, 0.38);
  stickGroup.visible = false;

  return stickGroup;
}

const hockeyStick = buildHockeyStickMesh();
armsRig.add(hockeyStick);

// ============================================================================
// SUPPLY CRATES & EXPLOSIVE BARRELS
// ============================================================================
const crates = [];
const crateGeo = new THREE.BoxGeometry(1.8, 1.8, 1.8);
const crateMat = new THREE.MeshStandardMaterial({ map: crateTex, roughness: 0.6 });

const crateLocations = [
  { x: -6, z: -10, loot: 'HOOK', desc: 'BRASS KNUCKLES! UNLOCKED THUNDER HOOK [2]' },
  { x: 8, z: -10, loot: 'KICK', desc: 'COMBAT BOOTS! UNLOCKED MIGHTY KICK [3 / E]' },
  { x: 0, z: -30, loot: 'SLAM', desc: 'METEOR GAUNTLET! UNLOCKED JUMP SLAM [4 / JUMP+ATTACK]' },
  { x: -28, z: -26, loot: 'HEALTH', desc: 'SUPER BERSERK STIMPACK! (+50 HP)' },
  { x: 28, z: -26, loot: 'ARMOR', desc: 'SECURITY VEST! (+50 SHIELD)' },
  { x: -28, z: 26, loot: 'SLAM', desc: 'METEOR ENERGY RECHARGED! (+150 SCORE)' },
  { x: 28, z: 26, loot: 'HEALTH', desc: 'BERSERK STIMPACK! (+50 HP)' },
  { x: 0, z: 20, loot: 'KICK', desc: 'REINFORCED STEEL BOOTS!' }
];

state.totalBoxes = crateLocations.length;

function spawnCrates() {
  crates.forEach(c => {
    if (c.mesh) scene.remove(c.mesh);
  });
  crates.length = 0;

  let spots = [];
  if (city) {
    const pzX = (city.peaceZone ? city.peaceZone.x : city.start.x);
    const pzZ = (city.peaceZone ? city.peaceZone.z : city.start.z);
    const pzR = (city.peaceZone ? city.peaceZone.radius : 55);

    const torontoCrateTargets = [
      { x: pzX + (pzR + 15), z: pzZ + 5, loot: 'HOOK', desc: 'BRASS KNUCKLES! UNLOCKED THUNDER HOOK [2]' },
      { x: pzX - (pzR + 15), z: pzZ - 5, loot: 'KICK', desc: 'COMBAT BOOTS! UNLOCKED MIGHTY KICK [3 / E]' },
      { x: pzX + 10, z: pzZ + (pzR + 18), loot: 'SLAM', desc: 'METEOR GAUNTLET! UNLOCKED JUMP SLAM [4 / JUMP+ATTACK]' },
      { x: pzX - 10, z: pzZ - (pzR + 18), loot: 'HEALTH', desc: 'SUPER BERSERK STIMPACK! (+50 HP)' },
      { x: -160, z: -55, loot: 'ARMOR', desc: 'SECURITY VEST! (+50 SHIELD)' },
      { x: -220, z: -70, loot: 'SLAM', desc: 'METEOR ENERGY RECHARGED! (+150 SCORE)' },
      { x: -140, z: 120, loot: 'HEALTH', desc: 'BERSERK STIMPACK! (+50 HP)' },
      { x: 40, z: 130, loot: 'KICK', desc: 'REINFORCED STEEL BOOTS!' }
    ];

    torontoCrateTargets.forEach(target => {
      let spot = city.findOpenSpot(target.x, target.z, 0, 20, 1.6);
      if (city.isInsidePeaceZone(spot.x, spot.z)) {
        spot = city.findOpenSpot(target.x, target.z, 25, 45, 1.6);
      }
      spots.push({ x: spot.x, z: spot.z, loot: target.loot, desc: target.desc });
    });
  } else {
    spots = crateLocations;
  }

  state.totalBoxes = spots.length;
  const hudBoxesEl = document.getElementById('hud-boxes');
  if (hudBoxesEl) hudBoxesEl.innerText = `${state.boxesSmashed}/${state.totalBoxes}`;
  spots.forEach((loc) => {
    const crate = new THREE.Mesh(crateGeo, crateMat);
    crate.position.set(loc.x, 0.9, loc.z);
    crate.castShadow = true;
    crate.receiveShadow = true;
    scene.add(crate);

    crates.push({
      mesh: crate,
      loot: loc.loot,
      desc: loc.desc,
      hp: 40,
      destroyed: false
    });
  });
}
spawnCrates();

// Loot Pickups
const pickups = [];

function spawnPickup(x, y, z, loot, desc) {
  const group = new THREE.Group();
  group.position.set(x, y + 0.6, z);

  let color = 0xffcc00;
  if (loot === 'KICK') color = 0x00f0ff;
  if (loot === 'SLAM') color = 0xea80fc;
  if (loot === 'HEALTH') color = 0x22c55e;
  if (loot === 'ARMOR') color = 0x38bdf8;

  const itemMesh = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.55, 0),
    new THREE.MeshStandardMaterial({ color: color, emissive: color, emissiveIntensity: 0.6 })
  );
  group.add(itemMesh);

  const pLight = new THREE.PointLight(color, 2.5, 6);
  group.add(pLight);
  scene.add(group);

  pickups.push({
    group: group,
    loot: loot,
    desc: desc,
    initialY: y + 0.6,
    collected: false
  });
}

// 3D Particles (Blood, Splinters, Debris)
const particles = [];

function spawnDebris(x, y, z, colorHex, count = 20, speed = 7) {
  for (let i = 0; i < count; i++) {
    const pMesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.14, 0.14, 0.14),
      new THREE.MeshBasicMaterial({ color: colorHex })
    );
    pMesh.position.set(x, y, z);
    scene.add(pMesh);

    const angle = Math.random() * Math.PI * 2;
    const upward = Math.random() * speed + 1.5;
    const spread = Math.random() * speed;

    particles.push({
      mesh: pMesh,
      vx: Math.cos(angle) * spread,
      vy: upward,
      vz: Math.sin(angle) * spread,
      life: 0.6 + Math.random() * 0.4
    });
  }
}

// Radial Shockwave Effect for Meteor Slam
function createMeteorShockwave(x, z) {
  const geo = new THREE.RingGeometry(0.3, 1.0, 36);
  const mat = new THREE.MeshBasicMaterial({
    color: 0xffaa00,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.95
  });
  const ring = new THREE.Mesh(geo, mat);
  ring.rotation.x = -Math.PI / 2;
  ring.position.set(x, 0.08, z);
  scene.add(ring);

  let radius = 1.0;
  let opacity = 0.95;

  const interval = setInterval(() => {
    radius += 0.55;
    opacity -= 0.06;
    ring.scale.set(radius, radius, 1);
    ring.material.opacity = Math.max(0, opacity);
    if (opacity <= 0) {
      clearInterval(interval);
      scene.remove(ring);
    }
  }, 16);
}

// ============================================================================
// 3D HUMANOID RIVAL FIGHTERS & BRAWLER AI SYSTEM
// ============================================================================
const enemies = [];

// Four distinct rival human fighters
const FIGHTER_ARCHETYPES = [
  {
    name: 'BRUISER TYSON',
    title: 'HEAVYWEIGHT BRAWLER',
    hp: 175,
    speed: 3.1,
    damage: 22,
    scale: 1.08,
    skinColor: 0xba7a48,
    hairColor: 0x18181b,
    vestColor: 0x1f2937,
    pantsColor: 0xb91c1c, // red boxing trunks
    wrapColor: 0xdc2626,  // red boxing wraps
    bootColor: 0x111827,
    hairStyle: 'shaved',
    bandanaColor: null
  },
  {
    name: 'STRIKER DAMIAN',
    title: 'STREET FIGHTER',
    hp: 110,
    speed: 4.6,
    damage: 14,
    scale: 0.98,
    skinColor: 0xe5ad82,
    hairColor: 0x451a03,
    vestColor: 0x334155, // urban vest
    pantsColor: 0x1e293b,
    wrapColor: 0x06b6d4,  // cyan taped fists
    bootColor: 0x0f172a,
    hairStyle: 'bandana',
    bandanaColor: 0xef4444 // red headband
  },
  {
    name: 'CYBER REX',
    title: 'ARENA CYBORG',
    hp: 145,
    speed: 3.6,
    damage: 18,
    scale: 1.04,
    skinColor: 0x784421,
    hairColor: 0x000000,
    vestColor: 0x09090b,
    pantsColor: 0x27272a,
    wrapColor: 0xf59e0b,  // gold brass knuckle gloves
    bootColor: 0x18181b,
    hairStyle: 'visor',
    bandanaColor: 0x22c55e // glowing optic green visor
  },
  {
    name: 'IRON KAI',
    title: 'MUAY THAI RIVAL',
    hp: 125,
    speed: 4.1,
    damage: 16,
    scale: 1.0,
    skinColor: 0xd4976a,
    hairColor: 0x171717,
    vestColor: 0x4c1d95, // purple combat shorts
    pantsColor: 0x581c87,
    wrapColor: 0xf8fafc,  // white Muay Thai wraps
    bootColor: 0x1e1b4b,
    hairStyle: 'topknot',
    bandanaColor: 0xa855f7
  }
];

function create3DHumanFighter(x, z, archetypeIndex) {
  const arch = FIGHTER_ARCHETYPES[archetypeIndex % FIGHTER_ARCHETYPES.length];
  const root = new THREE.Group();
  root.position.set(x, 0, z);
  root.scale.set(arch.scale, arch.scale, arch.scale);

  // Materials
  const skinMat = new THREE.MeshStandardMaterial({ color: arch.skinColor, roughness: 0.7, metalness: 0.05 });
  const vestMat = new THREE.MeshStandardMaterial({ color: arch.vestColor, roughness: 0.6, metalness: 0.1 });
  const pantsMat = new THREE.MeshStandardMaterial({ color: arch.pantsColor, roughness: 0.6, metalness: 0.1 });
  const wrapMat = new THREE.MeshStandardMaterial({ color: arch.wrapColor, roughness: 0.5, metalness: 0.3 });
  const bootMat = new THREE.MeshStandardMaterial({ color: arch.bootColor, roughness: 0.7, metalness: 0.2 });
  const hairMat = new THREE.MeshStandardMaterial({ color: arch.hairColor, roughness: 0.9, metalness: 0.0 });
  const beltMat = new THREE.MeshStandardMaterial({ color: 0x09090b, roughness: 0.4, metalness: 0.5 });
  const buckleMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.2, metalness: 0.9 });
  const eyeWhiteMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
  const eyePupilMat = new THREE.MeshBasicMaterial({ color: 0x0f172a });

  // Store all mesh materials for hit flash & stagger tinting
  const flashableMaterials = [skinMat, vestMat, pantsMat, wrapMat, bootMat];

  // --- Pelvis & Hips ---
  const pelvisGroup = new THREE.Group();
  pelvisGroup.position.set(0, 0.9, 0);
  root.add(pelvisGroup);

  const hips = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.22, 0.3), pantsMat);
  hips.castShadow = true;
  pelvisGroup.add(hips);

  const belt = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.07, 0.32), beltMat);
  belt.position.set(0, 0.08, 0);
  pelvisGroup.add(belt);

  const buckle = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.34), buckleMat);
  buckle.position.set(0, 0.08, 0);
  pelvisGroup.add(buckle);

  // --- Legs ---
  // Left Leg
  const leftLegPivot = new THREE.Group();
  leftLegPivot.position.set(-0.16, 0.82, 0);
  root.add(leftLegPivot);

  const leftThigh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.42, 0.2), pantsMat);
  leftThigh.position.set(0, -0.2, 0);
  leftThigh.castShadow = true;
  leftLegPivot.add(leftThigh);

  const leftCalfPivot = new THREE.Group();
  leftCalfPivot.position.set(0, -0.4, 0);
  leftLegPivot.add(leftCalfPivot);

  const leftCalf = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.4, 0.18), pantsMat);
  leftCalf.position.set(0, -0.2, 0);
  leftCalf.castShadow = true;
  leftCalfPivot.add(leftCalf);

  const leftBoot = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.16, 0.26), bootMat);
  leftBoot.position.set(0, -0.38, 0.04);
  leftBoot.castShadow = true;
  leftCalfPivot.add(leftBoot);

  // Right Leg
  const rightLegPivot = new THREE.Group();
  rightLegPivot.position.set(0.16, 0.82, 0);
  root.add(rightLegPivot);

  const rightThigh = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.42, 0.2), pantsMat);
  rightThigh.position.set(0, -0.2, 0);
  rightThigh.castShadow = true;
  rightLegPivot.add(rightThigh);

  const rightCalfPivot = new THREE.Group();
  rightCalfPivot.position.set(0, -0.4, 0);
  rightLegPivot.add(rightCalfPivot);

  const rightCalf = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.4, 0.18), pantsMat);
  rightCalf.position.set(0, -0.2, 0);
  rightCalf.castShadow = true;
  rightCalfPivot.add(rightCalf);

  const rightBoot = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.16, 0.26), bootMat);
  rightBoot.position.set(0, -0.38, 0.04);
  rightBoot.castShadow = true;
  rightCalfPivot.add(rightBoot);

  // --- Upper Body / Torso ---
  const torsoPivot = new THREE.Group();
  torsoPivot.position.set(0, 0.98, 0);
  root.add(torsoPivot);

  // Muscular abdomen & chest vest
  const abdomen = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.24, 0.26), vestMat);
  abdomen.position.set(0, 0.1, 0);
  abdomen.castShadow = true;
  torsoPivot.add(abdomen);

  const chest = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.36, 0.32), vestMat);
  chest.position.set(0, 0.36, 0);
  chest.castShadow = true;
  torsoPivot.add(chest);

  // Neck
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.14, 8), skinMat);
  neck.position.set(0, 0.58, 0);
  torsoPivot.add(neck);

  // Head
  const headPivot = new THREE.Group();
  headPivot.position.set(0, 0.68, 0);
  torsoPivot.add(headPivot);

  const head = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.32, 0.28), skinMat);
  head.position.set(0, 0.16, 0);
  head.castShadow = true;
  headPivot.add(head);

  // Fighter Face Eyes
  const eyeLeft = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.02), eyeWhiteMat);
  eyeLeft.position.set(-0.07, 0.18, 0.142);
  headPivot.add(eyeLeft);
  const pupilLeft = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.04, 0.022), eyePupilMat);
  pupilLeft.position.set(-0.07, 0.18, 0.144);
  headPivot.add(pupilLeft);

  const eyeRight = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.04, 0.02), eyeWhiteMat);
  eyeRight.position.set(0.07, 0.18, 0.142);
  headPivot.add(eyeRight);
  const pupilRight = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.04, 0.022), eyePupilMat);
  pupilRight.position.set(0.07, 0.18, 0.144);
  headPivot.add(pupilRight);

  // Eyebrows / Fighter Grimace
  const brow = new THREE.Mesh(
    new THREE.BoxGeometry(0.24, 0.03, 0.03),
    new THREE.MeshBasicMaterial({ color: 0x111111 })
  );
  brow.position.set(0, 0.21, 0.144);
  headPivot.add(brow);

  // Hair / Bandana / Visor Styles
  if (arch.hairStyle === 'bandana' && arch.bandanaColor) {
    const bandanaMat = new THREE.MeshStandardMaterial({ color: arch.bandanaColor });
    flashableMaterials.push(bandanaMat);
    const band = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.08, 0.3), bandanaMat);
    band.position.set(0, 0.24, 0);
    headPivot.add(band);
    const tail = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.22, 0.06), bandanaMat);
    tail.position.set(0, 0.18, -0.16);
    tail.rotation.x = 0.2;
    headPivot.add(tail);
  } else if (arch.hairStyle === 'visor' && arch.bandanaColor) {
    const visorMat = new THREE.MeshBasicMaterial({ color: arch.bandanaColor });
    const visor = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.06, 0.05), visorMat);
    visor.position.set(0, 0.18, 0.146);
    headPivot.add(visor);
  } else if (arch.hairStyle === 'topknot') {
    const hairTop = new THREE.Mesh(new THREE.BoxGeometry(0.29, 0.1, 0.29), hairMat);
    hairTop.position.set(0, 0.33, 0);
    headPivot.add(hairTop);
    const knot = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 0.12, 6), hairMat);
    knot.position.set(0, 0.42, -0.05);
    headPivot.add(knot);
  } else {
    // Shaved / buzz cut hair cap
    const buzz = new THREE.Mesh(new THREE.BoxGeometry(0.29, 0.08, 0.29), hairMat);
    buzz.position.set(0, 0.32, 0);
    headPivot.add(buzz);
  }

  // --- Arms (Left & Right) with Boxing Handwraps / Gloves ---
  // Left Arm
  const leftArmPivot = new THREE.Group();
  leftArmPivot.position.set(-0.35, 0.48, 0);
  torsoPivot.add(leftArmPivot);

  const leftBicep = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.3, 0.16), skinMat);
  leftBicep.position.set(0, -0.15, 0);
  leftBicep.castShadow = true;
  leftArmPivot.add(leftBicep);

  const leftForearmPivot = new THREE.Group();
  leftForearmPivot.position.set(0, -0.3, 0);
  leftArmPivot.add(leftForearmPivot);

  const leftForearm = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.28, 0.15), skinMat);
  leftForearm.position.set(0, -0.14, 0);
  leftForearm.castShadow = true;
  leftForearmPivot.add(leftForearm);

  const leftFist = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 0.2), wrapMat);
  leftFist.position.set(0, -0.3, 0.02);
  leftFist.castShadow = true;
  leftForearmPivot.add(leftFist);

  // Right Arm
  const rightArmPivot = new THREE.Group();
  rightArmPivot.position.set(0.35, 0.48, 0);
  torsoPivot.add(rightArmPivot);

  const rightBicep = new THREE.Mesh(new THREE.BoxGeometry(0.15, 0.3, 0.16), skinMat);
  rightBicep.position.set(0, -0.15, 0);
  rightBicep.castShadow = true;
  rightArmPivot.add(rightBicep);

  const rightForearmPivot = new THREE.Group();
  rightForearmPivot.position.set(0, -0.3, 0);
  rightArmPivot.add(rightForearmPivot);

  const rightForearm = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.28, 0.15), skinMat);
  rightForearm.position.set(0, -0.14, 0);
  rightForearm.castShadow = true;
  rightForearmPivot.add(rightForearm);

  const rightFist = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.18, 0.2), wrapMat);
  rightFist.position.set(0, -0.3, 0.02);
  rightFist.castShadow = true;
  rightForearmPivot.add(rightFist);

  // Ground Contact Shadow Disc
  const shadowGeo = new THREE.CircleGeometry(0.48, 16);
  const shadowMat = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.45 });
  const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
  shadowMesh.rotation.x = -Math.PI / 2;
  shadowMesh.position.set(0, 0.02, 0);
  root.add(shadowMesh);

  // --- Dynamic Overhead 3D Health Bar & Nameplate Sprite ---
  const nameplateCanvas = document.createElement('canvas');
  nameplateCanvas.width = 256;
  nameplateCanvas.height = 72;
  const npCtx = nameplateCanvas.getContext('2d');
  const nameplateTexture = new THREE.CanvasTexture(nameplateCanvas);
  nameplateTexture.minFilter = THREE.LinearFilter;
  const nameplateMaterial = new THREE.SpriteMaterial({ map: nameplateTexture, depthTest: false, transparent: true });
  const nameplateSprite = new THREE.Sprite(nameplateMaterial);
  nameplateSprite.scale.set(1.9, 0.54, 1);
  nameplateSprite.position.set(0, 2.2, 0);
  root.add(nameplateSprite);

  function updateNameplate(hp, maxHp, isStaggered) {
    npCtx.clearRect(0, 0, 256, 72);

    // Background pill
    npCtx.fillStyle = 'rgba(10, 14, 20, 0.88)';
    if (npCtx.roundRect) {
      npCtx.beginPath();
      npCtx.roundRect(4, 4, 248, 64, 8);
      npCtx.fill();
    } else {
      npCtx.fillRect(4, 4, 248, 64);
    }
    npCtx.lineWidth = 2;
    npCtx.strokeStyle = isStaggered ? '#ffea00' : 'rgba(255, 255, 255, 0.25)';
    npCtx.stroke();

    // Name and Tag
    npCtx.font = 'bold 17px "Rajdhani", sans-serif';
    npCtx.fillStyle = isStaggered ? '#ffea00' : '#ffffff';
    npCtx.fillText(isStaggered ? `⚡ ${arch.name} [STAGGERED!]` : `${arch.name}`, 14, 26);

    npCtx.font = 'bold 12px monospace';
    npCtx.fillStyle = '#94a3b8';
    npCtx.fillText(isStaggered ? 'PRESS F / CLICK: GLORY KILL' : `${Math.max(0, Math.round(hp))}/${maxHp} HP`, 14, 44);

    // Health bar container
    const barX = 14;
    const barY = 50;
    const barW = 228;
    const barH = 10;
    npCtx.fillStyle = 'rgba(0, 0, 0, 0.65)';
    npCtx.fillRect(barX, barY, barW, barH);

    // Health bar fill
    const pct = Math.max(0, Math.min(1, hp / maxHp));
    const barColor = isStaggered ? '#ffea00' : (pct > 0.5 ? '#10b981' : (pct > 0.25 ? '#f59e0b' : '#ef4444'));
    npCtx.fillStyle = barColor;
    npCtx.fillRect(barX, barY, barW * pct, barH);

    nameplateTexture.needsUpdate = true;
  }
  updateNameplate(arch.hp, arch.hp, false);

  scene.add(root);

  return {
    root,
    pelvisGroup,
    leftLegPivot,
    leftCalfPivot,
    rightLegPivot,
    rightCalfPivot,
    torsoPivot,
    headPivot,
    leftArmPivot,
    leftForearmPivot,
    rightArmPivot,
    rightForearmPivot,
    nameplateSprite,
    updateNameplate,
    materials: flashableMaterials,
    originalColors: flashableMaterials.map(m => m.color.getHex()),
    arch
  };
}

function spawnEnemy(x, z, archIdx = 0) {
  const fighterRig = create3DHumanFighter(x, z, archIdx);
  const arch = fighterRig.arch;
  const cfg = DIFFICULTY_CONFIGS[state.difficulty || 'medium'] || DIFFICULTY_CONFIGS.medium;

  const maxHp = Math.round(arch.hp * cfg.hpMult);
  fighterRig.updateNameplate(maxHp, maxHp, false);

  enemies.push({
    rig: fighterRig,
    sprite: fighterRig.root, // alias for position compatibility
    name: arch.name,
    hp: maxHp,
    maxHp: maxHp,
    speed: arch.speed * cfg.speedMult,
    damage: Math.round(arch.damage * cfg.damageMult),
    attackCooldown: 1.1 / cfg.attackCooldownMult,
    attackTimer: 0.5 + Math.random() * 0.5,
    attackProg: 0,
    aggroDist: cfg.aggroDist,
    isPunching: false,
    punchArm: 'right',
    punchHasDealtDamage: false,
    walkPhase: Math.random() * Math.PI * 2,
    flinchTimer: 0,
    isStaggered: false,
    staggerTimer: 0,
    isDead: false,
    isKnockedOut: false,
    koProgress: 0,
    vx: 0,
    vz: 0
  });
}

// Street patrol targets distributed across Downtown Toronto sectors
const ALL_TORONTO_STREET_TARGETS = [
  // Sector 1: Bremner Blvd & CN Tower Perimeter (South)
  { x: -360, z: 290, idx: 0 }, { x: -310, z: 285, idx: 1 }, { x: -410, z: 290, idx: 2 },
  { x: -260, z: 290, idx: 3 }, { x: -210, z: 285, idx: 0 }, { x: -460, z: 290, idx: 1 },
  // Sector 2: Front St Corridor (North of CN Tower)
  { x: -360, z: 120, idx: 2 }, { x: -310, z: 110, idx: 3 }, { x: -420, z: 120, idx: 0 },
  { x: -470, z: 115, idx: 1 }, { x: -260, z: 110, idx: 2 }, { x: -210, z: 115, idx: 3 },
  // Sector 3: Simcoe, Wellington & Metro Hall
  { x: -210, z: -60, idx: 0 }, { x: -160, z: -60, idx: 1 }, { x: -240, z: -100, idx: 2 },
  { x: -180, z: -120, idx: 3 }, { x: -280, z: -70, idx: 0 }, { x: -330, z: -60, idx: 1 },
  // Sector 4: Entertainment District & King St West
  { x: -140, z: -40, idx: 2 }, { x: -150, z: 120, idx: 3 }, { x: -220, z: -160, idx: 0 },
  { x: -280, z: -160, idx: 1 }, { x: -340, z: -170, idx: 2 }, { x: -400, z: -170, idx: 3 },
  { x: -450, z: -180, idx: 0 }, { x: -500, z: -180, idx: 1 },
  // Sector 5: Rogers Centre Plaza & Blue Jays Way
  { x: -440, z: 230, idx: 2 }, { x: -460, z: 180, idx: 3 }, { x: -500, z: 240, idx: 0 },
  { x: -520, z: 300, idx: 1 }, { x: -480, z: 340, idx: 2 }, { x: -540, z: 360, idx: 3 },
  // Sector 6: Roundhouse Park & Steam Whistle
  { x: -220, z: 320, idx: 0 }, { x: -260, z: 340, idx: 1 }, { x: -180, z: 330, idx: 2 },
  { x: -200, z: 360, idx: 3 }, { x: -240, z: 380, idx: 0 }, { x: -160, z: 370, idx: 1 },
  // Sector 7: Financial District (Bay & King, Wellington, TD Centre)
  { x: -80, z: 80, idx: 2 }, { x: 30, z: 140, idx: 3 }, { x: 100, z: -60, idx: 0 },
  { x: -10, z: -120, idx: 1 }, { x: 50, z: -70, idx: 2 }, { x: 120, z: -110, idx: 3 },
  { x: 180, z: -90, idx: 0 }, { x: 230, z: -130, idx: 1 }, { x: 160, z: -170, idx: 2 },
  { x: 220, z: -210, idx: 3 }, { x: 280, z: -180, idx: 0 }, { x: 320, z: -140, idx: 1 },
  // Sector 8: Union Station & Scotiabank Arena
  { x: -100, z: -20, idx: 2 }, { x: -50, z: -20, idx: 3 }, { x: 20, z: -30, idx: 0 },
  { x: 80, z: -20, idx: 1 }, { x: 140, z: -30, idx: 2 }, { x: 200, z: -40, idx: 3 },
  { x: 260, z: 40, idx: 0 }, { x: 240, z: 90, idx: 1 }, { x: 200, z: 120, idx: 2 },
  // Sector 9: Harbourfront / Queens Quay Promenade
  { x: -320, z: 420, idx: 3 }, { x: -240, z: 430, idx: 0 }, { x: -160, z: 440, idx: 1 },
  { x: -80, z: 450, idx: 2 }, { x: 0, z: 460, idx: 3 }, { x: 100, z: 460, idx: 0 },
  { x: 200, z: 450, idx: 1 }, { x: 280, z: 440, idx: 2 }, { x: 340, z: 430, idx: 3 },
  // Sector 10: University Ave & Roy Thomson Hall
  { x: -120, z: -180, idx: 0 }, { x: -70, z: -190, idx: 1 }, { x: -30, z: -220, idx: 2 },
  { x: 20, z: -240, idx: 3 }, { x: 60, z: -280, idx: 0 }, { x: -40, z: -270, idx: 1 },
  // Sector 11: Spadina & CityPlace Corridor
  { x: -580, z: 200, idx: 2 }, { x: -620, z: 260, idx: 3 }, { x: -660, z: 320, idx: 0 },
  { x: -640, z: 380, idx: 1 }, { x: -600, z: 440, idx: 2 }, { x: -680, z: 450, idx: 3 },
  // Sector 12: York St & Lakeshore Boulevard
  { x: -120, z: 220, idx: 0 }, { x: -60, z: 230, idx: 1 }, { x: 0, z: 230, idx: 2 },
  { x: 60, z: 240, idx: 3 }, { x: 120, z: 250, idx: 0 }, { x: 180, z: 260, idx: 1 }
];

function populateEnemies() {
  // Clear any existing enemies
  enemies.forEach(e => {
    if (e.rig && e.rig.root) scene.remove(e.rig.root);
  });
  enemies.length = 0;

  const cfg = DIFFICULTY_CONFIGS[state.difficulty || 'medium'] || DIFFICULTY_CONFIGS.medium;

  if (city) {
    const targets = ALL_TORONTO_STREET_TARGETS;
    let spawnedCount = 0;

    for (let i = 0; i < targets.length && spawnedCount < cfg.targetEnemies; i++) {
      const target = targets[i];
      let spot = city.findOpenSpot(target.x, target.z, 0, 30, 2.0);
      const playerX = player.pos.x;
      const playerZ = player.pos.z;
      let fromPlayer = Math.hypot(spot.x - playerX, spot.z - playerZ);
      let fromStart = Math.hypot(spot.x - city.start.x, spot.z - city.start.z);

      if (fromPlayer < 25 || fromStart < 25) {
        spot = city.findOpenSpot(target.x, target.z, 25, 45, 2.0);
        fromPlayer = Math.hypot(spot.x - playerX, spot.z - playerZ);
        fromStart = Math.hypot(spot.x - city.start.x, spot.z - city.start.z);
      }

      const fromPeace = Math.hypot(spot.x - city.peaceZone.x, spot.z - city.peaceZone.z);
      if (!city.isInsidePeaceZone(spot.x, spot.z) &&
        fromPeace >= city.peaceZone.radius + 20 &&
        fromPlayer >= 25 &&
        fromStart >= 25) {
        spawnEnemy(spot.x, spot.z, target.idx);
        spawnedCount++;
      }
    }

    // If still need more to satisfy target count (e.g. Impossible 88)
    while (spawnedCount < cfg.targetEnemies) {
      spawnSingleReinforcement();
      spawnedCount++;
    }
  } else {
    const spawns = [
      [-8, -18, 0], [8, -18, 1], [-20, 16, 2], [20, 16, 3],
      [-26, -10, 0], [26, -10, 1], [0, 28, 2], [-18, -28, 3]
    ];
    spawns.slice(0, cfg.targetEnemies).forEach(([x, z, idx]) => spawnEnemy(x, z, idx));
  }
}

function spawnSingleReinforcement() {
  if (!city) return;
  const pX = player.pos.x;
  const pZ = player.pos.z;
  const angle = Math.random() * Math.PI * 2;
  const dist = 35 + Math.random() * 65;
  const tx = pX + Math.cos(angle) * dist;
  const tz = pZ + Math.sin(angle) * dist;

  const spot = city.findOpenSpot(tx, tz, 5, 25, 2.0);
  const fromPeace = Math.hypot(spot.x - city.peaceZone.x, spot.z - city.peaceZone.z);
  const fromPlayer = Math.hypot(spot.x - pX, spot.z - pZ);

  if (!city.isInsidePeaceZone(spot.x, spot.z) && fromPeace >= city.peaceZone.radius + 15 && fromPlayer >= 25) {
    const archIdx = Math.floor(Math.random() * 4);
    spawnEnemy(spot.x, spot.z, archIdx);
  }
}

function spawnAdditionalEnemies(count) {
  if (!city) return;
  for (let i = 0; i < count; i++) {
    spawnSingleReinforcement();
  }
}

function setDifficulty(diffKey, announce = true) {
  if (!DIFFICULTY_CONFIGS[diffKey]) return;
  state.difficulty = diffKey;
  const cfg = DIFFICULTY_CONFIGS[diffKey];

  // Update in-game HUD badge
  const diffBadge = document.getElementById('diff-badge');
  if (diffBadge) {
    diffBadge.innerText = `DIFF: ${cfg.name}`;
    diffBadge.className = `tag ${cfg.tagClass}`;
  }

  // Update menu start modal buttons
  document.querySelectorAll('.diff-btn').forEach(btn => {
    if (btn.getAttribute('data-diff') === diffKey) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Adjust existing live enemies to new multipliers
  enemies.forEach(enemy => {
    if (enemy.isDead || enemy.isKnockedOut) return;
    enemy.speed = enemy.rig.arch.speed * cfg.speedMult;
    enemy.damage = Math.round(enemy.rig.arch.damage * cfg.damageMult);
    enemy.attackCooldown = (1.1 / cfg.attackCooldownMult);
    enemy.aggroDist = cfg.aggroDist;
  });

  // Scale active enemy population
  const aliveEnemies = enemies.filter(e => !e.isDead);
  if (aliveEnemies.length < cfg.targetEnemies) {
    spawnAdditionalEnemies(cfg.targetEnemies - aliveEnemies.length);
  } else if (aliveEnemies.length > cfg.targetEnemies) {
    const excess = aliveEnemies.length - cfg.targetEnemies;
    const sorted = aliveEnemies.slice().sort((a, b) => {
      const da = a.rig.root.position.distanceTo(player.pos);
      const db = b.rig.root.position.distanceTo(player.pos);
      return db - da; // remove furthest first
    });
    for (let i = 0; i < excess; i++) {
      const e = sorted[i];
      if (e.rig && e.rig.root) scene.remove(e.rig.root);
      const idx = enemies.indexOf(e);
      if (idx !== -1) enemies.splice(idx, 1);
    }
  }

  if (announce) {
    showAnnouncement(`⚡ DIFFICULTY SET: ${cfg.name} (${cfg.targetEnemies} FOES) ⚡`);
    audio.playImpact('heavy');
  }
}

function cycleDifficulty(dir) {
  const curIdx = DIFFICULTY_ORDER.indexOf(state.difficulty || 'medium');
  let nextIdx = curIdx + dir;
  if (nextIdx < 0) nextIdx = 0;
  if (nextIdx >= DIFFICULTY_ORDER.length) nextIdx = DIFFICULTY_ORDER.length - 1;
  if (nextIdx !== curIdx) {
    setDifficulty(DIFFICULTY_ORDER[nextIdx], true);
  }
}

populateEnemies();

// ============================================================================
// CONTROLS & POINTER LOCK MANAGEMENT (NEVER TRAPS CURSOR!)
// ============================================================================
const keys = {};
let mouseSensitivity = 0.0024;

// Pointer Lock Change Listener
document.addEventListener('pointerlockchange', () => {
  state.isPointerLocked = (document.pointerLockElement === container);
  const tag = document.getElementById('mouse-status-tag');

  if (state.isPointerLocked) {
    tag.innerText = 'MOUSE: LOCKED (FPS)';
    tag.className = 'tag tag-green';
  } else {
    tag.innerText = 'MOUSE: UNLOCKED';
    tag.className = 'tag tag-dim';
  }

  // When pointer lock is lost in mouse-look mode (e.g. user pressed Esc), pause the game
  if (!state.isPointerLocked && state.inGame && !state.freeMouseMode && !state.isDead && !state.isPaused) {
    pauseGame();
  }
});

// Canvas Click: NEVER traps pointer automatically; executes attacks during gameplay
container.addEventListener('click', (e) => {
  if (!state.inGame || state.isPaused || state.isDead) return;
  if (e.button === 0) {
    triggerAttack();
  }
});

// Mouse Movement: Only rotates if pointer locked OR right click drag in free mouse
document.addEventListener('mousemove', (e) => {
  if (state.isDead || state.isPaused) return;
  if (state.isPointerLocked || (state.freeMouseMode && e.buttons === 2)) {
    player.yaw -= e.movementX * mouseSensitivity;
    player.pitch -= e.movementY * mouseSensitivity;
    player.pitch = Math.max(-Math.PI / 2.3, Math.min(Math.PI / 2.3, player.pitch));
  }
});

// Keyboard - use e.code exclusively to prevent Shift/caps desync
window.addEventListener('keydown', (e) => {
  keys[e.code] = true;

  // Cheat code: [Shift] + 1 (or '!') triggers Canadian Berserker Mode with full timeout
  if (e.key === '!' || (e.shiftKey && (e.code === 'Digit1' || e.key === '1'))) {
    e.preventDefault();
    state.rage = 100;
    updateRageBar();
    activateBerserkMode();
    showAnnouncement("🍁 CHEAT ACTIVATED: CANADIAN BERSERK MODE! 🍁");
    return;
  }

  // Difficulty Hotkeys: [ (BracketLeft) decrease, ] (BracketRight) increase
  if (e.code === 'BracketLeft') {
    e.preventDefault();
    cycleDifficulty(-1);
    return;
  }
  if (e.code === 'BracketRight') {
    e.preventDefault();
    cycleDifficulty(1);
    return;
  }

  if (e.code === 'KeyF') triggerAttack();
  if (e.code === 'KeyE' && state.unlocked[ATTACKS.KICK.id]) triggerQuickKick();

  if (e.code.startsWith('Digit') && !e.shiftKey) {
    const n = parseInt(e.code.slice(5), 10);
    if (n >= 1 && n <= 4) selectAttackSlot(n);
  }

  if (e.code === 'Escape' || e.code === 'KeyP') {
    e.preventDefault();
    togglePause();
  }
  if (e.code === 'Space') e.preventDefault(); // stop page scroll
});

window.addEventListener('keyup', (e) => {
  keys[e.code] = false;
});

window.addEventListener('blur', () => {
  for (const k in keys) keys[k] = false;
});

window.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  if (state.inGame && !state.isPaused && state.unlocked[ATTACKS.KICK.id]) {
    triggerQuickKick();
  }
});

function selectAttackSlot(num) {
  const list = [ATTACKS.JAB, ATTACKS.HOOK, ATTACKS.KICK, ATTACKS.SLAM];
  const target = list[num - 1];
  if (target && state.unlocked[target.id]) {
    state.activeAttack = target;
    updateHUDWeapon();
  }
}

// Pause Management
function pauseGame() {
  state.isPaused = true;
  if (document.pointerLockElement) document.exitPointerLock();

  const overlay = document.getElementById('menu-overlay');
  overlay.classList.remove('hidden');
  document.getElementById('menu-title').innerText = 'GAME PAUSED';
  document.getElementById('menu-subtitle').innerText = 'FIGHTER READY. SELECT MODE TO RESUME:';
  document.getElementById('start-mouse-btn').innerText = 'RESUME GAME (MOUSE LOOK)';
  document.getElementById('start-free-btn').innerText = 'RESUME GAME (FREE MOUSE MODE)';
}

function resumeGame(usePointerLock = true) {
  state.isPaused = false;
  state.inGame = true;
  state.freeMouseMode = !usePointerLock;
  document.getElementById('menu-overlay').classList.add('hidden');

  if (usePointerLock) {
    container.requestPointerLock();
  } else {
    if (document.pointerLockElement) document.exitPointerLock();
  }
}

function togglePause() {
  if (state.isPaused) {
    resumeGame(!state.freeMouseMode);
  } else {
    pauseGame();
  }
}

document.getElementById('esc-unlock-btn').addEventListener('click', () => {
  pauseGame();
});

// ============================================================================
// ATTACK & GLORY KILL EXECUTION MECHANICS
// ============================================================================
function triggerAttack() {
  if (state.attackTimer > 0 || state.isDead || state.isPaused) return;

  // Peace Sanctuary: No fighting allowed
  if (city && city.isInsidePeaceZone(player.pos.x, player.pos.z)) {
    showAnnouncement("🕊️ PEACE SANCTUARY: NO COMBAT PERMITTED");
    audio.playPeaceChime?.();
    return;
  }

  // Check Glory Kill Execution on nearby staggered fighter
  if (state.gloryTarget) {
    executeGloryKill(state.gloryTarget);
    return;
  }

  // Airborne + Meteor Slam Unlocked -> METEOR JUMP SLAM!
  if (!player.isGrounded && state.unlocked[ATTACKS.SLAM.id]) {
    executeMeteorSlam();
    return;
  }

  const atk = state.activeAttack;
  state.attackTimer = atk.cooldown;
  state.isAttacking = true;
  state.attackProgress = 0;
  state.currentAnimType = atk.type;

  audio.playPunch(atk.type === 'heavy' ? 1.6 : 1.0, state.isBerserk);

  // Check hits in front of player
  setTimeout(() => {
    checkMeleeHits(atk);
  }, 90);
}

function triggerQuickKick() {
  if (state.attackTimer > 0 || state.isDead || state.isPaused) return;

  // Peace Sanctuary: No fighting allowed
  if (city && city.isInsidePeaceZone(player.pos.x, player.pos.z)) {
    showAnnouncement("🕊️ PEACE SANCTUARY: NO COMBAT PERMITTED");
    audio.playPeaceChime?.();
    return;
  }

  const atk = ATTACKS.KICK;
  state.attackTimer = atk.cooldown;
  state.isAttacking = true;
  state.attackProgress = 0;
  state.currentAnimType = 'kick';

  audio.playPunch(1.4, state.isBerserk);

  setTimeout(() => {
    checkMeleeHits(atk);
  }, 100);
}

function executeMeteorSlam() {
  // Peace Sanctuary: No fighting allowed
  if (city && city.isInsidePeaceZone(player.pos.x, player.pos.z)) {
    showAnnouncement("🕊️ PEACE SANCTUARY: NO COMBAT PERMITTED");
    audio.playPeaceChime?.();
    return;
  }

  const atk = ATTACKS.SLAM;
  state.attackTimer = atk.cooldown;
  state.isAttacking = true;
  state.attackProgress = 0;
  state.currentAnimType = 'slam';

  // Rocket downward with immense slam velocity
  player.velocity.y = -22.0;
  showAnnouncement("💥 METEOR JUMP SLAM!");
  audio.playPunch(2.4, true);

  const checkImpact = setInterval(() => {
    if (player.isGrounded) {
      clearInterval(checkImpact);

      // Detonation on impact
      audio.playImpact('slam');
      triggerScreenShake(28);
      triggerSlamFlash();
      createMeteorShockwave(player.pos.x, player.pos.z);
      spawnDebris(player.pos.x, 0.5, player.pos.z, 0xffaa00, 40, 11);

      // Hit all enemies in AoE
      enemies.forEach(enemy => {
        if (enemy.isDead) return;
        const dist = enemy.sprite.position.distanceTo(player.pos);
        if (dist <= atk.range) {
          const dmg = state.isBerserk ? atk.damage * 2.5 : atk.damage;
          hitEnemy(enemy, dmg, atk.knockback * 1.6, 'slam');
        }
      });

      // Break crates
      crates.forEach(crate => {
        if (crate.destroyed) return;
        const dist = crate.mesh.position.distanceTo(player.pos);
        if (dist <= atk.range) damageCrate(crate, 300);
      });
    }
  }, 25);
}

function executeGloryKill(enemy) {
  state.gloryTarget = null;
  state.attackTimer = 0.5;
  state.isAttacking = true;
  state.currentAnimType = 'heavy';

  showAnnouncement("⚡ BRUTAL KNOCKOUT TAKEDOWN! ⚡");
  audio.playImpact('glory');
  triggerScreenShake(20);

  const pos = enemy.rig ? enemy.rig.root.position : enemy.sprite.position;
  // Massive blood fountain
  spawnDebris(pos.x, 1.2, pos.z, 0x9e0b11, 55, 12);

  // Guaranteed Health & Shield drops
  state.health = Math.min(state.maxHealth, state.health + 35);
  state.armor = Math.min(state.maxArmor, state.armor + 30);
  updateHUDHealth();

  killEnemy(enemy, true);
}

function checkMeleeHits(atk) {
  let hitSomething = false;

  // Check Crates
  crates.forEach(crate => {
    if (crate.destroyed) return;
    const dist = crate.mesh.position.distanceTo(camera.position);
    if (dist <= atk.range) {
      const dirToCrate = crate.mesh.position.clone().sub(camera.position).normalize();
      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      if (dirToCrate.dot(forward) > 0.6) {
        damageCrate(crate, state.isBerserk ? atk.damage * 3 : atk.damage);
        hitSomething = true;
      }
    }
  });

  // Check Enemies
  enemies.forEach(enemy => {
    if (enemy.isDead || enemy.isKnockedOut) return;
    const pos = enemy.rig ? enemy.rig.root.position : enemy.sprite.position;
    const dist = pos.distanceTo(camera.position);
    if (dist <= atk.range) {
      const dirToEnemy = pos.clone().sub(camera.position).normalize();
      const forward = new THREE.Vector3();
      camera.getWorldDirection(forward);
      if (dirToEnemy.dot(forward) > 0.55) {
        const dmg = state.isBerserk ? atk.damage * 3 : atk.damage;
        const kb = state.isBerserk ? atk.knockback * 2.2 : atk.knockback;
        hitEnemy(enemy, dmg, kb, atk.type);
        hitSomething = true;
      }
    }
  });

  if (hitSomething) {
    showHitMarker();
    triggerScreenShake(state.isBerserk ? atk.knockback * 1.5 : atk.knockback * 0.7);
    if (state.isBerserk) {
      audio.playHockeySlapshot();
    } else {
      audio.playImpact(atk.type);
    }
    registerCombo();
  }
}

function damageCrate(crate, dmg) {
  crate.hp -= dmg;
  spawnDebris(crate.mesh.position.x, 0.9, crate.mesh.position.z, 0x8b5a2b, 15, 6);

  if (crate.hp <= 0 && !crate.destroyed) {
    crate.destroyed = true;
    scene.remove(crate.mesh);
    audio.playCrateSmash();
    spawnDebris(crate.mesh.position.x, 0.9, crate.mesh.position.z, 0x5c3818, 40, 9);
    spawnPickup(crate.mesh.position.x, 0.9, crate.mesh.position.z, crate.loot, crate.desc);

    state.boxesSmashed++;
    state.score += 200;
    document.getElementById('hud-boxes').innerText = `${state.boxesSmashed}/${state.totalBoxes}`;
    document.getElementById('hud-score').innerText = state.score;
  }
}

function setEnemyTint(enemy, hex) {
  if (enemy.rig && enemy.rig.materials) {
    enemy.rig.materials.forEach(mat => mat.color.setHex(hex));
  }
}

function restoreEnemyTint(enemy) {
  if (enemy.rig && enemy.rig.materials && enemy.rig.originalColors) {
    enemy.rig.materials.forEach((mat, i) => mat.color.setHex(enemy.rig.originalColors[i]));
  }
}

function hitEnemy(enemy, dmg, knockback, type) {
  if (enemy.isDead || enemy.isKnockedOut) return;

  enemy.hp -= dmg;
  enemy.flinchTimer = 0.22;

  // Update 3D overhead health bar
  if (enemy.rig && enemy.rig.updateNameplate) {
    enemy.rig.updateNameplate(enemy.hp, enemy.maxHp, enemy.isStaggered);
  }

  // Check for Staggered Glory Kill Threshold (low HP)
  if (enemy.hp > 0 && enemy.hp <= enemy.maxHp * 0.32) {
    enemy.isStaggered = true;
    enemy.staggerTimer = 4.5;
    setEnemyTint(enemy, 0xffea00); // Flashing gold
    if (enemy.rig && enemy.rig.updateNameplate) {
      enemy.rig.updateNameplate(enemy.hp, enemy.maxHp, true);
    }
  } else {
    // Normal flash red on hit
    setEnemyTint(enemy, 0xff2222);
    setTimeout(() => {
      if (!enemy.isDead && !enemy.isStaggered) {
        restoreEnemyTint(enemy);
      }
    }, 110);
  }

  // Knockback physics
  const pos = enemy.rig ? enemy.rig.root.position : enemy.sprite.position;
  const dir = pos.clone().sub(player.pos).normalize();
  enemy.vx = dir.x * knockback;
  enemy.vz = dir.z * knockback;

  spawnDebris(pos.x, 1.0, pos.z, 0xb91c1c, 18, 8);

  if (enemy.hp <= 0 && !enemy.isDead) {
    killEnemy(enemy);
  }
}

function killEnemy(enemy, isGlory = false) {
  if (enemy.isDead) return;
  enemy.isDead = true;
  enemy.isKnockedOut = true;
  enemy.koProgress = 0;
  state.kills++;
  state.score += isGlory ? 500 : 300;
  document.getElementById('hud-kills').innerText = state.kills;
  document.getElementById('hud-score').innerText = state.score;

  // Build Rage
  state.rage = Math.min(100, state.rage + 25);
  updateRageBar();
  if (state.rage >= 100 && !state.isBerserk) {
    activateBerserkMode();
  }

  setFaceExpression('grin', 1.4);
  audio.playImpact('heavy');
  showAnnouncement(`💀 ${enemy.name} KNOCKED OUT! 💀`);

  const pos = enemy.rig ? enemy.rig.root.position : enemy.sprite.position;
  spawnDebris(pos.x, 1.0, pos.z, 0xb91c1c, 32, 9);

  // Hide overhead nameplate upon KO
  if (enemy.rig && enemy.rig.nameplateSprite) {
    enemy.rig.nameplateSprite.visible = false;
  }

  // Clean up mesh after dramatic knockout fall
  setTimeout(() => {
    if (enemy.rig && enemy.rig.root) scene.remove(enemy.rig.root);

    // Respawn next wave of fighters when all are KO'd
    if (enemies.every(e => e.isDead)) {
      showAnnouncement("🔥 ARENA CLEARED! NEXT RIVAL FIGHTERS INCOMING! 🔥");
      setTimeout(() => populateEnemies(), 2200);
    }
  }, 2400);
}

function activateBerserkMode() {
  state.isBerserk = true;
  state.berserkTimer = 16.0;
  showAnnouncement("🍁 CANADIAN BERSERK RAGE! HOCKEY STICK READY! 🍁");
  audio.playBerserkRage();
  audio.stopMusic();
  audio.startOCanada();
  const bOverlay = document.getElementById('berserk-overlay');
  if (bOverlay) bOverlay.style.opacity = '1';
}

function updateRageBar() {
  document.getElementById('rage-bar-fill').style.width = `${state.rage}%`;
}

// ============================================================================
// HUD FACE & 3D ARMS ANIMATIONS
// ============================================================================
const faceCanvas = document.getElementById('hud-face-canvas');
const faceCtx = faceCanvas.getContext('2d');
faceCtx.imageSmoothingEnabled = false;

function drawFace() {
  faceCtx.fillStyle = '#101217';
  faceCtx.fillRect(0, 0, 72, 72);

  // Fighter head
  faceCtx.fillStyle = '#d99e6b';
  faceCtx.fillRect(18, 18, 36, 42);

  // Hair
  faceCtx.fillStyle = '#78350f';
  faceCtx.fillRect(16, 12, 40, 12);
  faceCtx.fillRect(16, 12, 6, 26);
  faceCtx.fillRect(50, 12, 6, 26);

  // Eyes
  const lookOffset = Math.sin(Date.now() * 0.003) > 0.4 ? 2 : 0;
  faceCtx.fillStyle = '#fff';
  faceCtx.fillRect(22, 28, 9, 6);
  faceCtx.fillRect(41, 28, 9, 6);
  faceCtx.fillStyle = state.isBerserk ? '#ff0000' : '#0284c7';
  faceCtx.fillRect(24 + lookOffset, 29, 5, 5);
  faceCtx.fillRect(43 + lookOffset, 29, 5, 5);

  // Mouth
  if (state.faceExpression === 'grin' || state.isBerserk) {
    faceCtx.fillStyle = '#fff';
    faceCtx.fillRect(26, 46, 20, 6);
    faceCtx.fillStyle = '#220000';
    faceCtx.fillRect(26, 46, 20, 1);
  } else if (state.faceExpression === 'hurt') {
    faceCtx.fillStyle = '#450a0a';
    faceCtx.fillRect(28, 45, 16, 8);
  } else {
    faceCtx.fillStyle = '#92400e';
    faceCtx.fillRect(28, 47, 16, 3);
  }

  // Blood cuts on face
  if (state.health < 50) {
    faceCtx.fillStyle = '#dc2626';
    faceCtx.fillRect(20, 22, 4, 10);
    faceCtx.fillRect(44, 40, 6, 4);
  }
}

function setFaceExpression(expr, duration = 0.8) {
  state.faceExpression = expr;
  state.faceTimer = duration;
}

// 3D Arms Bobbing & Procedural Swing Animation
function updateArmsRig(dt) {
  const swayX = Math.sin(player.bobTimer) * 0.04;
  const swayY = Math.abs(Math.cos(player.bobTimer)) * 0.035;

  const prog = state.attackProgress;
  const anim = state.currentAnimType;

  // Canadian Hockey Stick Wielding in Berserk Mode
  if (state.isBerserk) {
    rightArm.visible = false;
    leftArm.visible = false;

    if (state.isAttacking && anim === 'kick') {
      bootGroup.visible = true;
      if (typeof hockeyStick !== 'undefined') hockeyStick.visible = false;
      const reach = Math.sin(prog * Math.PI);
      bootGroup.position.set(0, -0.25 - (1 - reach) * 0.8, -0.6 - reach * 0.7);
      bootGroup.rotation.x = 0.3 - reach * 0.4;
    } else {
      bootGroup.visible = false;
      if (typeof hockeyStick !== 'undefined') {
        hockeyStick.visible = true;

        if (state.isAttacking) {
          // Dynamic Hockey Slapshot Swing!
          if (prog < 0.28) {
            // Windup: pull back and up to the right
            const w = prog / 0.28;
            hockeyStick.position.set(0.22 + w * 0.16, -0.26 + w * 0.20, -0.44 + w * 0.10);
            hockeyStick.rotation.set(-0.22 - w * 0.45, -0.42 - w * 0.30, 0.38 + w * 0.55);
          } else {
            // Explosive downswing and follow-through across screen to bottom-left
            const s = (prog - 0.28) / 0.72;
            const curve = Math.sin(s * Math.PI * 0.5);
            hockeyStick.position.set(
              0.38 - curve * 0.82,
              -0.06 - curve * 0.30,
              -0.34 - Math.sin(s * Math.PI) * 0.36
            );
            hockeyStick.rotation.set(-0.67 + s * 1.25, -0.72 + s * 1.35, 0.93 - s * 2.0);
          }
        } else {
          // Ready Idle Hockey Stance
          hockeyStick.position.set(0.22 + swayX, -0.26 + swayY, -0.44);
          hockeyStick.rotation.set(-0.22, -0.42, 0.38);
        }
      }
    }
    return;
  }

  // Not in Berserk: ensure hockey stick is hidden
  if (typeof hockeyStick !== 'undefined') hockeyStick.visible = false;

  if (state.isAttacking) {
    if (anim === 'kick') {
      // Hide arms, thrust mighty boot forward into screen!
      rightArm.visible = false;
      leftArm.visible = false;
      bootGroup.visible = true;

      const reach = Math.sin(prog * Math.PI);
      bootGroup.position.set(0, -0.25 - (1 - reach) * 0.8, -0.6 - reach * 0.7);
      bootGroup.rotation.x = 0.3 - reach * 0.4;
    } else if (anim === 'slam') {
      // Both fists raised high, then slammed down
      bootGroup.visible = false;
      rightArm.visible = true;
      leftArm.visible = true;

      const slamReach = Math.sin(prog * Math.PI);
      rightArm.position.set(0.24, -0.15 + slamReach * 0.25, -0.3 - slamReach * 0.45);
      leftArm.position.set(-0.24, -0.15 + slamReach * 0.25, -0.3 - slamReach * 0.45);
    } else if (anim === 'heavy') {
      // Brass Knuckles Hook: Wide brutal haymaker arc
      bootGroup.visible = false;
      rightArm.visible = true;
      leftArm.visible = true;

      const hookArc = Math.sin(prog * Math.PI);
      rightArm.position.set(0.32 - hookArc * 0.55, -0.24 + swayY, -0.2 - hookArc * 0.5);
      rightArm.rotation.y = hookArc * 0.8;
      leftArm.position.set(-0.32, -0.32 + swayY, -0.2);
    } else {
      // Standard Jab: Fast straight punch thrust
      bootGroup.visible = false;
      rightArm.visible = true;
      leftArm.visible = true;

      const jab = Math.sin(prog * Math.PI);
      rightArm.position.set(0.32 + swayX, -0.26 + swayY, -0.2 - jab * 0.55);
      leftArm.position.set(-0.32 + swayX, -0.28 + swayY, -0.2);
    }
  } else {
    // Idle weapon stance: gentle natural breathing bob
    bootGroup.visible = false;
    rightArm.visible = true;
    leftArm.visible = true;
    rightArm.rotation.set(0, 0, 0);
    leftArm.rotation.set(0, 0, 0);

    rightArm.position.set(0.32 + swayX, -0.28 + swayY, -0.2);
    leftArm.position.set(-0.32 + swayX, -0.30 + swayY, -0.2);
  }
}

// ============================================================================
// HUD UPDATES & SCREEN FX
// ============================================================================
function updateHUDWeapon() {
  const atk = state.activeAttack;
  document.getElementById('hud-attack-name').innerText = atk.name;
  document.getElementById('hud-attack-name').style.color = atk.color;
  document.getElementById('hud-attack-desc').innerText = atk.sub;

  for (let i = 1; i <= 4; i++) {
    const slot = document.querySelector(`.slot[data-slot="${i}"]`);
    if (slot) {
      if (state.unlocked[i]) {
        slot.className = 'slot unlocked';
        if (state.activeAttack.id === i) slot.classList.add('active');
      } else {
        slot.className = 'slot locked';
      }
    }
  }
}

function updateHUDHealth() {
  document.getElementById('hud-health').innerText = Math.max(0, Math.round(state.health));
  document.getElementById('hud-health-bar').style.width = `${Math.max(0, state.health)}%`;
  document.getElementById('hud-armor').innerText = Math.max(0, Math.round(state.armor));
  document.getElementById('hud-armor-bar').style.width = `${Math.max(0, state.armor)}%`;
}

function showHitMarker() {
  const hm = document.getElementById('hit-marker');
  hm.classList.add('active');
  setTimeout(() => hm.classList.remove('active'), 90);
}

function triggerScreenShake(amount = 14) {
  state.screenShake = amount;
}

function triggerDamageFlash() {
  const f = document.getElementById('damage-flash');
  f.style.opacity = '1';
  setTimeout(() => f.style.opacity = '0', 140);
}

function triggerSlamFlash() {
  const f = document.getElementById('slam-flash');
  f.style.opacity = '1';
  setTimeout(() => f.style.opacity = '0', 180);
}

function showAnnouncement(text) {
  const ann = document.getElementById('announcement');
  ann.innerText = text;
  ann.classList.add('show');
  setTimeout(() => ann.classList.remove('show'), 2200);
}

// Peace Sanctuary Banner Controller
let peaceBannerTimer = null;
function triggerPeaceZoneBanner(insidePeace) {
  const banner = document.getElementById('peace-zone-banner');
  if (!banner) return;

  clearTimeout(peaceBannerTimer);
  banner.classList.remove('hidden');

  const title = banner.querySelector('.peace-banner-title');
  const sub = banner.querySelector('.peace-banner-sub');
  const icon = banner.querySelector('.peace-banner-icon');

  if (insidePeace) {
    banner.classList.remove('combat-alert');
    if (title) title.innerText = 'CN TOWER PEACE SANCTUARY';
    if (sub) sub.innerText = 'NO COMBAT PERMITTED • SAFE HAVEN • VITALITY REGENERATING';
    if (icon) icon.innerText = '🕊️';
    showAnnouncement('🕊️ ENTERED CN TOWER PEACE SANCTUARY');
    audio.playPeaceChime?.();
  } else {
    banner.classList.add('combat-alert');
    if (title) title.innerText = 'EXITING PEACE SANCTUARY';
    if (sub) sub.innerText = 'COMBAT ZONE ACTIVE • WATCH YOUR BACK!';
    if (icon) icon.innerText = '⚠️';
    showAnnouncement('⚔️ ENTERING TORONTO COMBAT ZONE');
  }

  peaceBannerTimer = setTimeout(() => {
    banner.classList.add('hidden');
  }, 3800);
}

function registerCombo() {
  state.comboCount++;
  state.comboTimer = 2.2;
  const countEl = document.getElementById('combo-count');
  const titleEl = document.getElementById('combo-title');
  titleEl.innerText = state.comboCount > 4 ? '🔥 BRUTAL COMBO' : 'COMBO';
  countEl.innerText = `x${state.comboCount}`;
  countEl.style.transform = 'scale(1.25)';
  setTimeout(() => countEl.style.transform = 'scale(1.0)', 100);
}

// ============================================================================
// MAIN LOOP & GAME PHYSICS
// ============================================================================
let lastTime = performance.now();
let fpsCount = 0;
let fpsTimer = 0;

function animate(now) {
  requestAnimationFrame(animate);

  const dt = Math.min((now - lastTime) / 1000, 0.1);
  lastTime = now;

  // FPS Counter
  fpsCount++;
  fpsTimer += dt;
  if (fpsTimer >= 1.0) {
    document.getElementById('fps-counter').innerText = `${fpsCount} FPS`;
    fpsCount = 0;
    fpsTimer = 0;
  }

  if (state.inGame && !state.isDead && !state.isPaused) {
    updatePlayer(dt);
    updateEnemies(dt);
    updatePickups(dt);
    updateParticles(dt);
    updateCombatTimers(dt);
  }

  // City animation & dynamic lighting
  if (city) {
    city.update(dt, player.pos);
  }

  // Draw Toronto GPS Minimap & Sanctuary Radar
  const minimapCanvas = document.getElementById('minimap-canvas');
  if (city && minimapCanvas) {
    const ctx = minimapCanvas.getContext('2d');
    const dots = [];
    enemies.forEach(e => {
      if (!e.isDead && !e.isKnockedOut) {
        dots.push({
          x: e.rig.root.position.x,
          z: e.rig.root.position.z,
          c: e.isStaggered ? '#ffea00' : '#ff3344',
          r: e.isStaggered ? 4 : 3
        });
      }
    });
    crates.forEach(c => {
      if (!c.destroyed) {
        dots.push({
          x: c.mesh.position.x,
          z: c.mesh.position.z,
          c: '#f59e0b',
          r: 2.5
        });
      }
    });
    city.drawMinimap(ctx, 160, player.pos, player.yaw, dots);

    // Distance to CN Tower
    const towerDist = Math.round(Math.hypot(player.pos.x - city.landmarks.cnTower[0], player.pos.z - city.landmarks.cnTower[1]));
    const towerDistEl = document.getElementById('tower-distance');
    if (towerDistEl) {
      if (city.isInsidePeaceZone(player.pos.x, player.pos.z)) {
        towerDistEl.innerText = 'CN TOWER SANCTUARY (INSIDE)';
        towerDistEl.style.color = '#34d399';
      } else {
        towerDistEl.innerText = `CN TOWER: ${towerDist}m`;
        towerDistEl.style.color = '#38bdf8';
      }
    }
  }

  // Camera Shake
  if (state.screenShake > 0) {
    camera.position.x += (Math.random() - 0.5) * state.screenShake * 0.02;
    camera.position.y += (Math.random() - 0.5) * state.screenShake * 0.02;
    state.screenShake *= 0.82;
    if (state.screenShake < 0.05) state.screenShake = 0;
  }

  updateArmsRig(dt);
  drawFace();

  renderer.render(scene, camera);
}

function updatePlayer(dt) {
  // Turning: ArrowLeft / ArrowRight or Q (E is reserved for kick)
  if (keys['ArrowLeft'] || keys['KeyQ']) player.yaw += 2.6 * dt;
  if (keys['ArrowRight']) player.yaw -= 2.6 * dt;
  if (keys['PageUp']) player.pitch = Math.min(Math.PI / 2.3, player.pitch + 2.0 * dt);
  if (keys['PageDown']) player.pitch = Math.max(-Math.PI / 2.3, player.pitch - 2.0 * dt);

  camera.rotation.order = 'YXZ';
  camera.rotation.y = player.yaw;
  camera.rotation.x = player.pitch;

  // Inertial camera roll when strafing
  let rollTarget = 0;
  if (keys['KeyA']) rollTarget = 0.025;
  if (keys['KeyD']) rollTarget = -0.025;
  camera.rotation.z += (rollTarget - camera.rotation.z) * 0.1;

  // Movement input: Support W/S/A/D and Arrow keys by e.code
  const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.yaw);
  const right = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), player.yaw);
  const moveDir = new THREE.Vector3();

  if (keys['KeyW'] || keys['ArrowUp']) moveDir.add(forward);
  if (keys['KeyS'] || keys['ArrowDown']) moveDir.sub(forward);
  if (keys['KeyD']) moveDir.add(right);
  if (keys['KeyA']) moveDir.sub(right);

  const isMoving = moveDir.lengthSq() > 0;
  if (isMoving) moveDir.normalize();

  const isSprinting = keys['ShiftLeft'] || keys['ShiftRight'] || state.isBerserk;
  const curSpeed = isSprinting ? player.sprintSpeed : player.speed;

  // Jump
  if (keys['Space'] && player.isGrounded) {
    player.velocity.y = player.jumpStrength;
    player.isGrounded = false;
  }

  // Gravity
  player.velocity.y -= 24.0 * dt;

  player.velocity.x = moveDir.x * curSpeed;
  player.velocity.z = moveDir.z * curSpeed;

  const nextX = player.pos.x + player.velocity.x * dt;
  const nextZ = player.pos.z + player.velocity.z * dt;

  if (canMoveTo(nextX, player.pos.z)) player.pos.x = nextX;
  if (canMoveTo(player.pos.x, nextZ)) player.pos.z = nextZ;

  player.pos.y += player.velocity.y * dt;
  if (player.pos.y <= 1.7) {
    player.pos.y = 1.7;
    player.velocity.y = 0;
    player.isGrounded = true;
  }

  if (isMoving && player.isGrounded) {
    player.bobTimer += dt * (isSprinting ? 16 : 10);
  } else {
    player.bobTimer *= 0.8;
  }

  // --- Peace Sanctuary Aura & Transition Check ---
  const insidePeace = city ? city.isInsidePeaceZone(player.pos.x, player.pos.z) : false;

  if (insidePeace !== state.wasInsidePeace) {
    state.wasInsidePeace = insidePeace;
    triggerPeaceZoneBanner(insidePeace);
  }

  if (insidePeace) {
    // Regenerate Vitality & Shield continuously
    if (state.health < 100) {
      state.health = Math.min(100, state.health + 8.0 * dt);
      updateHUDHealth();
    }
    if (state.armor < 50) {
      state.armor = Math.min(50, state.armor + 5.0 * dt);
      updateHUDHealth();
    }
    const statusPill = document.getElementById('peace-zone-status');
    if (statusPill) {
      statusPill.className = 'peace-status-pill safe';
      statusPill.innerText = '🕊️ PEACE SANCTUARY';
    }
  } else {
    const statusPill = document.getElementById('peace-zone-status');
    if (statusPill) {
      statusPill.className = 'peace-status-pill danger';
      statusPill.innerText = '⚔️ COMBAT ZONE';
    }
  }
}

function canMoveTo(x, z) {
  if (city) {
    if (!city.canMoveTo(x, z, 0.6)) return false;
  } else {
    if (Math.abs(x) > 38 || Math.abs(z) > 38) return false;

    const pRadius = 0.6;
    for (let i = 0; i < colliders.length; i++) {
      const box = colliders[i].box;
      if (x + pRadius > box.min.x && x - pRadius < box.max.x &&
        z + pRadius > box.min.z && z - pRadius < box.max.z) {
        return false;
      }
    }
  }

  for (let i = 0; i < crates.length; i++) {
    const c = crates[i];
    if (!c.destroyed) {
      const dist = Math.hypot(x - c.mesh.position.x, z - c.mesh.position.z);
      if (dist < 1.3) return false;
    }
  }

  return true;
}

function updateEnemies(dt) {
  let nearestStaggered = null;
  let minDist = 4.0;
  const playerInPeace = city ? city.isInsidePeaceZone(player.pos.x, player.pos.z) : false;

  enemies.forEach(enemy => {
    // 1. Knockout knockdown animation
    if (enemy.isKnockedOut) {
      if (enemy.koProgress < 1.0) {
        enemy.koProgress = Math.min(1.0, enemy.koProgress + dt * 3.2);
        enemy.rig.root.rotation.x = -Math.PI / 2 * enemy.koProgress;
        enemy.rig.root.position.y = 0.22 * (1 - enemy.koProgress) + 0.12 * enemy.koProgress;
        enemy.rig.leftLegPivot.rotation.x = 0.35 * enemy.koProgress;
        enemy.rig.rightLegPivot.rotation.x = 0.45 * enemy.koProgress;
        enemy.rig.leftArmPivot.rotation.x = 0.5 * enemy.koProgress;
        enemy.rig.rightArmPivot.rotation.x = 0.5 * enemy.koProgress;
      }
      return;
    }

    if (enemy.isDead) return;

    // Apply knockback velocity
    enemy.rig.root.position.x += enemy.vx * dt;
    enemy.rig.root.position.z += enemy.vz * dt;
    enemy.vx *= 0.86;
    enemy.vz *= 0.86;

    // Keep within world bounds
    if (city && city.bounds) {
      enemy.rig.root.position.x = Math.max(city.bounds.minX + 5, Math.min(city.bounds.maxX - 5, enemy.rig.root.position.x));
      enemy.rig.root.position.z = Math.max(city.bounds.minZ + 5, Math.min(city.bounds.maxZ - 5, enemy.rig.root.position.z));
    } else {
      enemy.rig.root.position.x = Math.max(-36, Math.min(36, enemy.rig.root.position.x));
      enemy.rig.root.position.z = Math.max(-36, Math.min(36, enemy.rig.root.position.z));
    }

    // Peace Sanctuary Repulsion: push enemy away so bad guys NEVER enter the sanctuary!
    if (city && city.peaceZone) {
      const edx = enemy.rig.root.position.x - city.peaceZone.x;
      const edz = enemy.rig.root.position.z - city.peaceZone.z;
      const edist = Math.hypot(edx, edz);
      const minSafeDist = city.peaceZone.radius + 3.0;
      if (edist < minSafeDist && edist > 0.05) {
        const push = (minSafeDist - edist);
        enemy.rig.root.position.x += (edx / edist) * push;
        enemy.rig.root.position.z += (edz / edist) * push;
        enemy.vx += (edx / edist) * 6.0;
        enemy.vz += (edz / edist) * 6.0;
      }
    }

    // Rotate whole body to face the player (only Y yaw, perfectly upright!)
    const targetAngle = Math.atan2(player.pos.x - enemy.rig.root.position.x, player.pos.z - enemy.rig.root.position.z);
    enemy.rig.root.rotation.y = targetAngle;

    // Handle Flinch on Hit
    if (enemy.flinchTimer > 0) {
      enemy.flinchTimer -= dt;
      enemy.rig.torsoPivot.rotation.x = 0.35;
      enemy.rig.headPivot.rotation.x = -0.3;
    } else {
      enemy.rig.torsoPivot.rotation.x = 0;
      enemy.rig.headPivot.rotation.x = 0;
    }

    // Check Stagger state
    if (enemy.isStaggered) {
      enemy.staggerTimer -= dt;
      if (enemy.staggerTimer <= 0) {
        enemy.isStaggered = false;
        restoreEnemyTint(enemy);
      } else {
        const flash = Math.sin(Date.now() * 0.02) > 0;
        setEnemyTint(enemy, flash ? 0xffea00 : 0xef4444);
      }
      enemy.rig.torsoPivot.rotation.x = 0.3;
      enemy.rig.headPivot.rotation.z = Math.sin(Date.now() * 0.007) * 0.25;
      enemy.rig.leftArmPivot.rotation.x = -0.3;
      enemy.rig.rightArmPivot.rotation.x = -0.3;
      enemy.rig.updateNameplate(enemy.hp, enemy.maxHp, true);
    }

    const distToPlayer = enemy.rig.root.position.distanceTo(player.pos);

    // Track Glory Target
    if (enemy.isStaggered && distToPlayer < minDist) {
      nearestStaggered = enemy;
      minDist = distToPlayer;
    }

    // AI Chasing, Footwork & Punch Attacks (Enemies CANNOT pursue into or attack inside Peace Sanctuary)
    if (!enemy.isStaggered) {
      const aggroLimit = enemy.aggroDist || 45;
      const isMoving = !playerInPeace && distToPlayer > 2.0 && distToPlayer < aggroLimit;

      if (isMoving) {
        const dir = player.pos.clone().sub(enemy.rig.root.position).normalize();
        enemy.rig.root.position.x += dir.x * enemy.speed * dt;
        enemy.rig.root.position.z += dir.z * enemy.speed * dt;

        // Human walk cycle animation
        enemy.walkPhase += dt * enemy.speed * 3.8;
        const legSwing = Math.sin(enemy.walkPhase) * 0.6;
        enemy.rig.leftLegPivot.rotation.x = legSwing;
        enemy.rig.leftCalfPivot.rotation.x = Math.max(0, -legSwing * 0.6);
        enemy.rig.rightLegPivot.rotation.x = -legSwing;
        enemy.rig.rightCalfPivot.rotation.x = Math.max(0, legSwing * 0.6);

        enemy.rig.torsoPivot.position.y = 0.98 + Math.abs(Math.sin(enemy.walkPhase * 2)) * 0.04;
        enemy.rig.torsoPivot.rotation.y = Math.sin(enemy.walkPhase) * 0.12;
      } else {
        // Boxer bounce / guard
        enemy.rig.leftLegPivot.rotation.x = 0.1;
        enemy.rig.leftCalfPivot.rotation.x = 0;
        enemy.rig.rightLegPivot.rotation.x = -0.15;
        enemy.rig.rightCalfPivot.rotation.x = 0.1;
        enemy.rig.torsoPivot.position.y = 0.98 + Math.sin(Date.now() * 0.005) * 0.02;
      }

      // Punch Attack / Boxer Guard Animation
      if (enemy.isPunching) {
        enemy.attackProg += dt * 3.2;
        const punchReach = Math.sin(enemy.attackProg * Math.PI);

        if (enemy.punchArm === 'right') {
          enemy.rig.rightArmPivot.rotation.x = -1.3 - punchReach * 0.65;
          enemy.rig.rightForearmPivot.rotation.x = -0.2 - punchReach * 0.75;
          enemy.rig.torsoPivot.rotation.y = -punchReach * 0.35;
          enemy.rig.leftArmPivot.rotation.x = -1.2;
          enemy.rig.leftForearmPivot.rotation.x = -0.8;
        } else {
          enemy.rig.leftArmPivot.rotation.x = -1.3 - punchReach * 0.65;
          enemy.rig.leftForearmPivot.rotation.x = -0.2 - punchReach * 0.75;
          enemy.rig.torsoPivot.rotation.y = punchReach * 0.35;
          enemy.rig.rightArmPivot.rotation.x = -1.2;
          enemy.rig.rightForearmPivot.rotation.x = -0.8;
        }

        // Deal damage at peak extension (strictly blocked if player is in Peace Sanctuary)
        if (enemy.attackProg >= 0.5 && !enemy.punchHasDealtDamage) {
          enemy.punchHasDealtDamage = true;
          if (distToPlayer <= 2.4 && !playerInPeace) {
            damagePlayer(enemy.damage);
            audio.playImpact('punch');
          }
        }

        if (enemy.attackProg >= 1.0) {
          enemy.isPunching = false;
          enemy.attackProg = 0;
        }
      } else {
        // Guard stance
        const sway = Math.sin(Date.now() * 0.004) * 0.08;
        enemy.rig.leftArmPivot.rotation.set(-1.15 + sway, 0.3, 0.15);
        enemy.rig.leftForearmPivot.rotation.set(-0.85, 0, 0);
        enemy.rig.rightArmPivot.rotation.set(-1.25 - sway, -0.3, -0.15);
        enemy.rig.rightForearmPivot.rotation.set(-0.85, 0, 0);

        // Within attack range -> trigger a punch (strictly blocked if player is in Peace Sanctuary)
        if (distToPlayer <= 2.2 && !playerInPeace) {
          enemy.attackTimer -= dt;
          if (enemy.attackTimer <= 0) {
            enemy.attackTimer = enemy.attackCooldown + Math.random() * 0.4;
            enemy.isPunching = true;
            enemy.attackProg = 0;
            enemy.punchArm = Math.random() > 0.4 ? 'right' : 'left';
            enemy.punchHasDealtDamage = false;
            audio.playPunch(0.9, false);
          }
        }
      }
    }
  });

  // Glory Kill Prompt Visibility
  state.gloryTarget = nearestStaggered;
  const gPrompt = document.getElementById('glory-kill-prompt');
  if (state.gloryTarget) {
    gPrompt.classList.add('active');
  } else {
    gPrompt.classList.remove('active');
  }
}


function damagePlayer(dmg) {
  if (state.isDead) return;

  let remaining = dmg;
  if (state.armor > 0) {
    const absorb = Math.min(state.armor, dmg * 0.65);
    state.armor -= absorb;
    remaining -= absorb;
  }
  state.health -= remaining;

  triggerDamageFlash();
  triggerScreenShake(14);
  setFaceExpression('hurt', 0.6);
  updateHUDHealth();

  if (state.health <= 0) {
    state.health = 0;
    playerDeath();
  }
}

function playerDeath() {
  state.isDead = true;
  showAnnouncement("💀 SLAIN IN BATTLE! 💀");
  if (document.pointerLockElement) document.exitPointerLock();
  const overlay = document.getElementById('menu-overlay');
  overlay.classList.remove('hidden');
  document.getElementById('menu-title').innerText = 'YOU DIED';
  document.getElementById('menu-subtitle').innerText = 'THE RIVAL FIGHTERS KNOCKED YOU OUT IN THE ARENA.';
  document.getElementById('start-mouse-btn').innerText = 'RESPAWN & FIGHT AGAIN';
}

function updatePickups(dt) {
  pickups.forEach(p => {
    if (p.collected) return;
    p.group.rotation.y += 2.5 * dt;
    p.group.position.y = p.initialY + Math.sin(Date.now() * 0.005) * 0.14;

    const dist = p.group.position.distanceTo(player.pos);
    if (dist < 1.8) {
      p.collected = true;
      scene.remove(p.group);
      audio.playPickup();
      showAnnouncement(`✨ LOOTED: ${p.desc}`);

      if (p.loot === 'HOOK') {
        state.unlocked[ATTACKS.HOOK.id] = true;
        state.activeAttack = ATTACKS.HOOK;
      } else if (p.loot === 'KICK') {
        state.unlocked[ATTACKS.KICK.id] = true;
        state.activeAttack = ATTACKS.KICK;
      } else if (p.loot === 'SLAM') {
        state.unlocked[ATTACKS.SLAM.id] = true;
        state.activeAttack = ATTACKS.SLAM;
      } else if (p.loot === 'HEALTH') {
        state.health = Math.min(state.maxHealth, state.health + 50);
      } else if (p.loot === 'ARMOR') {
        state.armor = Math.min(state.maxArmor, state.armor + 50);
      }

      updateHUDWeapon();
      updateHUDHealth();
    }
  });
}

function updateParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.life -= dt;
    p.vy -= 18 * dt;
    p.mesh.position.x += p.vx * dt;
    p.mesh.position.y += p.vy * dt;
    p.mesh.position.z += p.vz * dt;

    if (p.mesh.position.y < 0.1) {
      p.mesh.position.y = 0.1;
      p.vx *= 0.5;
      p.vz *= 0.5;
    }

    if (p.life <= 0) {
      scene.remove(p.mesh);
      particles.splice(i, 1);
    }
  }
}

function updateCombatTimers(dt) {
  if (state.attackTimer > 0) {
    state.attackTimer -= dt;
    state.attackProgress = 1 - (state.attackTimer / state.activeAttack.cooldown);
    if (state.attackTimer <= 0) {
      state.isAttacking = false;
      state.attackProgress = 0;
    }
  }

  if (state.comboTimer > 0) {
    state.comboTimer -= dt;
    if (state.comboTimer <= 0) {
      state.comboCount = 0;
      document.getElementById('combo-title').innerText = 'COMBO';
      document.getElementById('combo-count').innerText = 'x0';
    }
  }

  if (state.isBerserk) {
    state.berserkTimer -= dt;
    if (state.berserkTimer <= 0) {
      state.isBerserk = false;
      state.berserkTimer = 0;
      state.rage = 0;
      updateRageBar();
      const bOverlay = document.getElementById('berserk-overlay');
      if (bOverlay) bOverlay.style.opacity = '0';
      showAnnouncement("BERSERK RAGE ENDED");
      audio.stopOCanada();
      audio.startMusic();
    }
  }

  // Dynamic reinforcement spawn rate based on difficulty
  if (state.inGame && !state.isPaused && !state.isDead && city) {
    state.spawnTimer = (state.spawnTimer || 0) + dt;
    const cfg = DIFFICULTY_CONFIGS[state.difficulty || 'medium'] || DIFFICULTY_CONFIGS.medium;
    if (state.spawnTimer >= cfg.spawnInterval) {
      state.spawnTimer = 0;
      const aliveCount = enemies.filter(e => !e.isDead).length;
      if (aliveCount < cfg.targetEnemies) {
        spawnSingleReinforcement();
      }
    }
  }

  if (state.faceTimer > 0) {
    state.faceTimer -= dt;
    if (state.faceTimer <= 0) state.faceExpression = 'neutral';
  }
}

// ============================================================================
// START & MODE SELECTORS
// ============================================================================
document.getElementById('start-mouse-btn').addEventListener('click', () => {
  audio.init();
  if (state.isDead) resetGame();
  resumeGame(true);
});

document.getElementById('start-free-btn').addEventListener('click', () => {
  audio.init();
  if (state.isDead) resetGame();
  resumeGame(false);
});

function resetGame() {
  state.health = 100;
  state.armor = 50;
  state.isDead = false;
  if (state.isBerserk) {
    state.isBerserk = false;
    state.berserkTimer = 0;
    audio.stopOCanada();
    const bOverlay = document.getElementById('berserk-overlay');
    if (bOverlay) bOverlay.style.opacity = '0';
  }
  if (city && city.start) {
    player.pos.set(city.start.x, 1.7, city.start.z);
    player.yaw = city.startYaw;
    camera.rotation.order = 'YXZ';
    camera.rotation.y = city.startYaw;
  } else {
    player.pos.set(0, 1.7, 0);
  }
  populateEnemies();
  spawnCrates();
  updateHUDHealth();
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Difficulty Selection Event Listeners
const prevDiffBtn = document.getElementById('diff-prev-btn');
if (prevDiffBtn) {
  prevDiffBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    cycleDifficulty(-1);
  });
}
const nextDiffBtn = document.getElementById('diff-next-btn');
if (nextDiffBtn) {
  nextDiffBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    cycleDifficulty(1);
  });
}
const diffBadgeEl = document.getElementById('diff-badge');
if (diffBadgeEl) {
  diffBadgeEl.addEventListener('click', (e) => {
    e.stopPropagation();
    cycleDifficulty(1);
  });
}
document.querySelectorAll('.diff-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const diff = btn.getAttribute('data-diff');
    if (diff) setDifficulty(diff, false);
  });
});

// Init HUD & Start Loop
updateHUDWeapon();
updateHUDHealth();
requestAnimationFrame(animate);
