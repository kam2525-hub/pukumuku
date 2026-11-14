// ============================================================
// 走れ純くん！焼きたてパンお届けダッシュ！
// パン工房プクムク 公式ゲーム 第3弾
// ============================================================

// --- 1. サウンドシステム (Web Audio API: 疾走感ある自作音源) ---
const NOTE = {
  REST: 0,
  C4: 261.63, D4: 293.66, E4: 329.63, F4: 349.23, G4: 392.00, A4: 440.00, B4: 493.88,
  C5: 523.25, D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99, A5: 880.00, B5: 987.77,
  C6: 1046.50, D6: 1174.66, E6: 1318.51, G6: 1567.98
};

const DASH_BGM = [
  NOTE.C5, NOTE.E5, NOTE.G5, NOTE.E5, NOTE.A5, NOTE.G5, NOTE.E5, NOTE.C5,
  NOTE.D5, NOTE.F5, NOTE.A5, NOTE.F5, NOTE.G5, NOTE.B5, NOTE.D6, NOTE.G5,
  NOTE.E5, NOTE.G5, NOTE.C6, NOTE.G5, NOTE.A5, NOTE.G5, NOTE.F5, NOTE.E5,
  NOTE.D5, NOTE.G5, NOTE.B5, NOTE.D6, NOTE.C6, NOTE.REST, NOTE.G5, NOTE.REST
];

class DashSoundManager {
  constructor() {
    this.ctx = null;
    this.muted = false;
    this.bgmStep = 0;
    this.bgmTimer = null;
    this.isFever = false;
  }

  init() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (AC) this.ctx = new AC();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
  }

  tone(freq, dur, type = 'triangle', vol = 0.12, delay = 0) {
    if (this.muted || !this.ctx || freq <= 0) return;
    const t = this.ctx.currentTime + delay;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t);
    gain.gain.setValueAtTime(0.001, t);
    gain.gain.exponentialRampToValueAtTime(vol, t + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    osc.start(t);
    osc.stop(t + dur + 0.02);
  }

  startBGM() {
    this.stopBGM();
    this.bgmStep = 0;
    const tick = () => {
      if (!game.running) return;
      const freq = DASH_BGM[this.bgmStep % DASH_BGM.length];
      if (freq > 0) {
        const mul = this.isFever ? 1.122 : 1.0;
        this.tone(freq * mul, 0.12, 'triangle', 0.055);
      }
      this.bgmStep++;
      const interval = this.isFever ? 125 : Math.max(130, 175 - (game.speed - 11) * 3);
      this.bgmTimer = setTimeout(tick, interval);
    };
    tick();
  }

  stopBGM() {
    if (this.bgmTimer) {
      clearTimeout(this.bgmTimer);
      this.bgmTimer = null;
    }
  }

  playMove() { this.tone(380, 0.07, 'sine', 0.08); }
  playJump() {
    this.tone(340, 0.08, 'sine', 0.12, 0);
    this.tone(540, 0.14, 'sine', 0.12, 0.05);
  }
  playCatch(combo = 1) {
    const scale = [NOTE.C5, NOTE.D5, NOTE.E5, NOTE.F5, NOTE.G5, NOTE.A5, NOTE.B5, NOTE.C6];
    const f = scale[Math.min(combo - 1, scale.length - 1)] || NOTE.C5;
    this.tone(f, 0.11, 'triangle', 0.14);
  }
  playGold() {
    this.tone(NOTE.C6, 0.09, 'sine', 0.16, 0);
    this.tone(NOTE.E6, 0.09, 'sine', 0.16, 0.06);
    this.tone(NOTE.G6, 0.22, 'sine', 0.18, 0.12);
  }
  playPower() {
    this.tone(NOTE.E5, 0.08, 'square', 0.09, 0);
    this.tone(NOTE.G5, 0.08, 'square', 0.09, 0.06);
    this.tone(NOTE.C6, 0.18, 'square', 0.10, 0.12);
  }
  playSmash() {
    this.tone(240, 0.08, 'sawtooth', 0.11, 0);
    this.tone(480, 0.12, 'triangle', 0.14, 0.04);
  }
  playHit() {
    this.tone(150, 0.22, 'sawtooth', 0.16, 0);
    this.tone(110, 0.28, 'sawtooth', 0.14, 0.08);
  }
  playFever() {
    [NOTE.C5, NOTE.E5, NOTE.G5, NOTE.C6, NOTE.E6].forEach((n, i) => {
      this.tone(n, 0.14, 'triangle', 0.14, i * 0.055);
    });
  }
}

const sounds = new DashSoundManager();

// --- 2. 定数 & ランキング設定 ---
const LANE_X = [-1.75, 0, 1.75];
const DASH_GAS_API_URL = 'https://script.google.com/macros/s/AKfycbx5KO9aojN0Vw2R5goL6pHybirY8Ldwk6pnqV5Wgbxb21JW7BzeSYBBn573Q_8AawUCKA/exec';
const LOCAL_DASH_API = '/api/dash_ranking';
const LOCAL_DASH_KEY = 'pukumuku_bread_dash_rankings_v1';
const PLAYER_NAME_KEY = 'pukumuku_player_name_v1';

// 障害物定義 (Blender製GLB 全7種)
const OBSTACLE_DEFS = [
  { key: 'obs_bread_crate', file: '../models/dash_props/obs_bread_crate.glb', scale: 1.08, hitHeight: 0.80, canJumpOver: true },
  { key: 'obs_aframe_sign', file: '../models/dash_props/obs_aframe_sign.glb', scale: 1.08, hitHeight: 0.90, canJumpOver: true },
  { key: 'obs_traffic_cone', file: '../models/dash_props/obs_traffic_cone.glb', scale: 1.10, hitHeight: 0.68, canJumpOver: true },
  { key: 'obs_flour_spill', file: '../models/dash_props/obs_flour_spill.glb', scale: 1.18, hitHeight: 0.45, canJumpOver: true },
  { key: 'obs_crow', file: '../models/dash_props/obs_crow.glb', scale: 1.22, hitHeight: 0.85, canJumpOver: true, isCrow: true },
  { key: 'obs_delivery_cart', file: '../models/dash_props/obs_delivery_cart.glb', scale: 1.08, hitHeight: 2.25, canJumpOver: false },
  { key: 'obs_oven_rack', file: '../models/dash_props/obs_oven_rack.glb', scale: 1.08, hitHeight: 2.25, canJumpOver: false }
];

// --- 3. Three.js シーン構築 ---
const canvasWrap = document.getElementById('canvas-wrapper');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x9BE0FF);
scene.fog = new THREE.FogExp2(0xFFE7C7, 0.016);

const camera = new THREE.PerspectiveCamera(58, canvasWrap.clientWidth / Math.max(1, canvasWrap.clientHeight), 0.1, 120);
camera.position.set(0, 3.6, 5.2);
camera.lookAt(0, 1.1, -6.5);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setSize(canvasWrap.clientWidth, canvasWrap.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputEncoding = THREE.sRGBEncoding;
canvasWrap.appendChild(renderer.domElement);

// ライティング（朝のパン屋通りの爽やかで暖かい光）
const hemiLight = new THREE.HemisphereLight(0xFFFDF5, 0xD2A679, 0.95);
scene.add(hemiLight);

const sunLight = new THREE.DirectionalLight(0xFFF3DC, 1.15);
sunLight.position.set(8, 16, 10);
sunLight.castShadow = true;
sunLight.shadow.mapSize.set(1024, 1024);
sunLight.shadow.camera.near = 1;
sunLight.shadow.camera.far = 55;
sunLight.shadow.camera.left = -12;
sunLight.shadow.camera.right = 12;
sunLight.shadow.camera.top = 15;
sunLight.shadow.camera.bottom = -25;
scene.add(sunLight);

// 道路テクスチャの生成
function createRoadTexture() {
  const c = document.createElement('canvas');
  c.width = 512;
  c.height = 512;
  const ctx = c.getContext('2d');

  // 温かみのある石畳ベース
  ctx.fillStyle = '#D7C3AE';
  ctx.fillRect(0, 0, 512, 512);

  // 石畳模様
  const rows = 8, cols = 8;
  const w = 512 / cols, h = 512 / rows;
  for (let r = 0; r < rows; r++) {
    const offset = (r % 2) * (w / 2);
    for (let col = -1; col <= cols; col++) {
      const shade = ((r * 7 + col * 13) % 3) * 8;
      ctx.fillStyle = `rgb(${210 - shade}, ${188 - shade}, ${164 - shade})`;
      ctx.fillRect(col * w + offset + 3, r * h + 3, w - 6, h - 6);
    }
  }

  // 3レーン区切り白線（破線）
  ctx.fillStyle = 'rgba(255, 250, 240, 0.78)';
  const laneDiv1 = 512 * 0.333;
  const laneDiv2 = 512 * 0.666;
  for (let y = 16; y < 512; y += 96) {
    ctx.fillRect(laneDiv1 - 4, y, 8, 52);
    ctx.fillRect(laneDiv2 - 4, y, 8, 52);
  }

  // 両端の縁石ライン
  ctx.fillStyle = '#E0822A';
  ctx.fillRect(0, 0, 14, 512);
  ctx.fillRect(498, 0, 14, 512);

  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(1, 14);
  tex.encoding = THREE.sRGBEncoding;
  return tex;
}

const roadTexture = createRoadTexture();
const roadMesh = new THREE.Mesh(
  new THREE.PlaneGeometry(5.8, 110),
  new THREE.MeshStandardMaterial({ map: roadTexture, roughness: 0.85 })
);
roadMesh.rotation.x = -Math.PI / 2;
roadMesh.position.set(0, 0, -40);
roadMesh.receiveShadow = true;
scene.add(roadMesh);

// 左右の歩道・芝生ベース
const sidewalkGeo = new THREE.PlaneGeometry(32, 110);
const sidewalkMat = new THREE.MeshStandardMaterial({ color: 0xC8E6C9, roughness: 0.92 });
const groundSide = new THREE.Mesh(sidewalkGeo, sidewalkMat);
groundSide.rotation.x = -Math.PI / 2;
groundSide.position.set(0, -0.02, -40);
groundSide.receiveShadow = true;
scene.add(groundSide);

// 歩道ブロック
const curbMat = new THREE.MeshStandardMaterial({ color: 0xE5CBB0, roughness: 0.88 });
[-4.2, 4.2].forEach(x => {
  const sw = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.14, 110), curbMat);
  sw.position.set(x, 0.05, -40);
  sw.receiveShadow = true;
  scene.add(sw);
});

// --- 4. アセットローダー (純くん・店舗・パン・障害物・街並み) ---
const gltfLoader = new THREE.GLTFLoader();

let junKunGroup = new THREE.Group();
scene.add(junKunGroup);

let junKunModel = null;
let junMixer = null;
let junActions = {};
let junBreadBox = null;
let carriedMiniBreads = [];

const breadTemplates = {};
const obstacleTemplates = {};
let houseTemplate = null;
let lampTemplate = null;
let pukumukuShopMesh = null;

// 1) 純くんのロード（Blender製全力疾走＆ジャンプアニメーション内蔵）
gltfLoader.load('../models/jun_kun_dash.glb?v=20261114dash2', (gltf) => {
  junKunModel = gltf.scene;
  const s = 0.62;
  junKunModel.scale.set(s, s, s);
  junKunModel.rotation.y = Math.PI; // 奥(-Z)向きに走る！

  junKunModel.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
      if (child.name === 'Bread_Carry_Box') {
        junBreadBox = child;
      }
    }
  });

  junKunGroup.add(junKunModel);

  junMixer = new THREE.AnimationMixer(junKunModel);
  gltf.animations.forEach((clip) => {
    junActions[clip.name] = junMixer.clipAction(clip);
  });

  if (junActions['Carry_Idle']) {
    junActions['Carry_Idle'].play();
  }
});

// 2) パン工房プクムク店舗モデル（スタート地点の後ろ左に配置）
gltfLoader.load('../models/pukumuku_blender_shop.glb?v=20261114dash', (gltf) => {
  pukumukuShopMesh = gltf.scene;
  pukumukuShopMesh.scale.set(0.65, 0.65, 0.65);
  pukumukuShopMesh.rotation.y = Math.PI * 0.42;
  pukumukuShopMesh.position.set(-5.8, 0, -2.5);
  pukumukuShopMesh.traverse(c => {
    if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; }
  });
  scene.add(pukumukuShopMesh);
});

// 3) 40種以上の3Dパンをロード
const validBreadKeys = Object.keys(typeof BREAD_TYPES !== 'undefined' ? BREAD_TYPES : {});
validBreadKeys.forEach((key) => {
  gltfLoader.load(catchBreadAsset(key, 'glb'), (gltf) => {
    const m = gltf.scene;
    m.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
    breadTemplates[key] = m;
  });
});

// 4) Blender製 障害物ロード
OBSTACLE_DEFS.forEach((def) => {
  gltfLoader.load(`${def.file}?v=20261114dash`, (gltf) => {
    const m = gltf.scene;
    m.scale.set(def.scale, def.scale, def.scale);
    m.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
    obstacleTemplates[def.key] = m;
  });
});

// 5) Blender製 街並み＆街灯ロード
const sceneryProps = [];
function initSceneryLoop() {
  if (!houseTemplate || !lampTemplate) return;
  if (sceneryProps.length > 0) return;

  const pastelWalls = [0xF5E6D3, 0xDCEFD8, 0xFCE4EC, 0xE3F2FD, 0xFFF3E0];
  let idx = 0;
  for (let i = 0; i < 10; i++) {
    const z = -6 - i * 8.5;
    [-1, 1].forEach((side) => {
      // 建物
      const h = houseTemplate.clone();
      const wallHex = pastelWalls[idx % pastelWalls.length];
      idx++;
      h.traverse(c => {
        if (c.isMesh && c.material && c.material.name && c.material.name.includes('CreamWall')) {
          c.material = c.material.clone();
          c.material.color.setHex(wallHex);
        }
      });
      h.position.set(side * 6.8, 0, z);
      h.rotation.y = side === -1 ? Math.PI / 2 : -Math.PI / 2;
      sceneryProps.push({ mesh: h, baseZ: z, isScenery: true });
      scene.add(h);

      // 街灯（建物の間に交互に配置）
      if (i % 2 === 0) {
        const l = lampTemplate.clone();
        l.position.set(side * 3.45, 0, z + 3.5);
        l.rotation.y = side === -1 ? 0 : Math.PI;
        sceneryProps.push({ mesh: l, baseZ: z + 3.5, isScenery: true });
        scene.add(l);
      }
    });
  }
}

gltfLoader.load('../models/dash_props/prop_shop_house.glb?v=20261114dash', (gltf) => {
  houseTemplate = gltf.scene;
  houseTemplate.scale.set(1.15, 1.15, 1.15);
  houseTemplate.traverse(c => { if (c.isMesh) { c.castShadow = true; c.receiveShadow = true; } });
  initSceneryLoop();
});

gltfLoader.load('../models/dash_props/prop_street_lamp.glb?v=20261114dash', (gltf) => {
  lampTemplate = gltf.scene;
  lampTemplate.scale.set(1.0, 1.0, 1.0);
  lampTemplate.traverse(c => { if (c.isMesh) { c.castShadow = true; } });
  initSceneryLoop();
});

// --- 5. ゲーム状態管理 ---
const game = {
  running: false,
  lane: 1, // 0, 1, 2
  playerX: 0,
  playerY: 0,
  vy: 0,
  isGrounded: true,
  lives: 3,
  score: 0,
  distance: 0,
  breadsCollected: 0,
  combo: 0,
  maxCombo: 0,
  speed: 12.5,
  invincibleTimer: 0,
  feverGauge: 0,
  feverTimer: 0,
  doubleTimer: 0,
  magnetTimer: 0,
  dashBoostTimer: 0,
  shakeTimer: 0,
  nextSpawnDist: 10,
  activeBreads: [],
  activeObstacles: [],
  flyingParticles: [],
  lastRecordId: null
};

function switchJunAnim(name) {
  if (!junActions[name]) return;
  Object.entries(junActions).forEach(([k, action]) => {
    if (k === name) {
      if (!action.isRunning()) action.reset().fadeIn(0.15).play();
    } else {
      action.fadeOut(0.15);
    }
  });
}

function addMiniBreadToBox(breadKey) {
  if (!junBreadBox || !breadTemplates[breadKey]) return;
  const mini = breadTemplates[breadKey].clone();
  mini.scale.set(0.13, 0.13, 0.13);
  const idx = carriedMiniBreads.length % 6;
  const col = idx % 3;
  const row = Math.floor(idx / 3);
  // 木箱の中の位置に配置
  mini.position.set((col - 1) * 0.12, 0.62 + row * 0.08, 0.25 + (row - 0.5) * 0.06);
  mini.rotation.set(0.2, idx * 0.8, 0);

  if (carriedMiniBreads.length >= 6) {
    const old = carriedMiniBreads.shift();
    if (old.parent) old.parent.remove(old);
  }
  junKunModel.add(mini);
  carriedMiniBreads.push(mini);
}

function clearCarriedBreads() {
  carriedMiniBreads.forEach(m => { if (m.parent) m.parent.remove(m); });
  carriedMiniBreads = [];
}

// --- 6. コースパターン自動生成（詰みゼロ・序盤易→後半障害物ラッシュ設計） ---
const SPECIAL_BREAD_KEYS = new Set(['bread_burnt', 'bread_gold', 'bread_egg', 'bread_mushroom', 'bread_negi']);
const PICKUP_KEYS = validBreadKeys.filter(k => !SPECIAL_BREAD_KEYS.has(k));

function pickRandomBreadKey() {
  const r = Math.random();
  if (r < 0.045) return 'bread_gold';
  if (r < 0.070) return 'bread_egg';
  if (r < 0.085 && game.magnetTimer <= 0) return 'bread_mushroom';
  if (r < 0.110) return 'bread_negi';
  if (r < 0.170 && !game.feverTimer) return 'bread_burnt';
  if (PICKUP_KEYS.length > 0) {
    return PICKUP_KEYS[Math.floor(Math.random() * PICKUP_KEYS.length)];
  }
  return 'bread_croissant';
}

function spawnBreadItem(lane, z, y = 0.65, forceKey = null) {
  const key = forceKey || pickRandomBreadKey();
  const tpl = breadTemplates[key];
  if (!tpl) return;
  const mesh = tpl.clone();
  const def = (typeof BREAD_TYPES !== 'undefined' && BREAD_TYPES[key]) ? BREAD_TYPES[key] : { name: 'パン', score: 250 };
  const s = (def.scale || 0.27) * 1.95;
  mesh.scale.set(s, s, s);
  mesh.position.set(LANE_X[lane], y, z);
  mesh.rotation.x = 0.4;
  scene.add(mesh);

  game.activeBreads.push({
    mesh,
    key,
    def,
    lane,
    yBase: y,
    phase: Math.random() * Math.PI * 2,
    collected: false
  });
}

function spawnObstacleItem(lane, z, forceDef = null) {
  const def = forceDef || OBSTACLE_DEFS[Math.floor(Math.random() * OBSTACLE_DEFS.length)];
  const tpl = obstacleTemplates[def.key];
  if (!tpl) return;
  const mesh = tpl.clone();
  mesh.position.set(LANE_X[lane], def.isCrow ? 0.35 : 0, z);
  scene.add(mesh);

  game.activeObstacles.push({
    mesh,
    def,
    lane,
    hit: false,
    smashed: false,
    vy: 0,
    vx: 0,
    phase: Math.random() * Math.PI * 2
  });
}

function spawnWave() {
  const spawnZ = -60;

  // フィーバー中も障害物を残しつつ、控えめなボーナスパターンにする
  if (game.feverTimer > 0) {
    const obsLane = Math.floor(Math.random() * 3);
    spawnObstacleItem(obsLane, spawnZ, OBSTACLE_DEFS[Math.floor(Math.random() * OBSTACLE_DEFS.length)]);
    for (let l = 0; l < 3; l++) {
      if (l === obsLane) continue;
      for (let k = 0; k < 2; k++) {
        spawnBreadItem(l, spawnZ - k * 2.2, 0.72);
      }
    }
    return 10.5;
  }

  const d = game.distance;
  const highDefs = OBSTACLE_DEFS.filter(def => !def.canJumpOver);
  const lowDefs = OBSTACLE_DEFS.filter(def => def.canJumpOver && !def.isCrow);
  const crowDef = OBSTACLE_DEFS.find(def => def.isCrow);
  const pickHigh = () => highDefs[Math.floor(Math.random() * highDefs.length)];
  const pickLow = () => lowDefs[Math.floor(Math.random() * lowDefs.length)];

  // 段階1: 序盤 (0m〜90m) はシンプルで簡単！1レーン障害物＋パンたっぷり
  if (d < 90) {
    const gap = Math.max(10.5, 12.5 - d * 0.022);
    const obsLane = Math.floor(Math.random() * 3);
    const useHigh = d > 35 && Math.random() < 0.35;
    spawnObstacleItem(obsLane, spawnZ, useHigh ? pickHigh() : pickLow());

    const breadLane = (obsLane + 1 + Math.floor(Math.random() * 2)) % 3;
    for (let k = 0; k < 3; k++) {
      spawnBreadItem(breadLane, spawnZ - k * 1.9, 0.68);
    }
    return gap;
  }

  // 段階2: 中盤 (90m〜260m) 障害物が2レーンや全レーン低ゲートに増加
  if (d < 260) {
    const gap = Math.max(8.0, 10.2 - (d - 90) * 0.013);
    const p = Math.random();
    if (p < 0.38) {
      // ミックス配置（高い壁 + 低い障害物 + パン列）
      const lanes = [0, 1, 2].sort(() => Math.random() - 0.5);
      spawnObstacleItem(lanes[0], spawnZ, pickHigh());
      spawnObstacleItem(lanes[1], spawnZ, pickLow());
      for (let k = 0; k < 3; k++) {
        spawnBreadItem(lanes[2], spawnZ - k * 1.8, 0.68);
      }
      return gap;
    } else if (p < 0.70) {
      // ダブル高い壁（1レーン突破）
      const safeLane = Math.floor(Math.random() * 3);
      for (let l = 0; l < 3; l++) {
        if (l === safeLane) {
          for (let k = 0; k < 3; k++) spawnBreadItem(l, spawnZ - k * 1.8, 0.68);
        } else {
          spawnObstacleItem(l, spawnZ, pickHigh());
        }
      }
      return gap;
    } else if (p < 0.88) {
      // ジャンプ必須ゲート
      const bonusLane = Math.floor(Math.random() * 3);
      for (let l = 0; l < 3; l++) {
        spawnObstacleItem(l, spawnZ, pickLow());
        if (l === bonusLane) {
          spawnBreadItem(l, spawnZ, 1.85, 'bread_gold');
        }
      }
      return gap + 0.8;
    } else {
      // カラス1羽＋地上障害物1つ
      const lanes = [0, 1, 2].sort(() => Math.random() - 0.5);
      spawnObstacleItem(lanes[0], spawnZ - 2.0, crowDef || pickLow());
      spawnObstacleItem(lanes[1], spawnZ, pickLow());
      for (let k = 0; k < 3; k++) spawnBreadItem(lanes[2], spawnZ - k * 1.8, 0.68);
      return gap;
    }
  }

  // 段階3・4: 後半 (260m〜) 2段・3段の複合障害物ラッシュでどんどん増える！
  const isRush = d >= 550;
  const baseGap = isRush
    ? Math.max(5.2, 6.6 - (d - 550) * 0.003)
    : Math.max(6.6, 8.2 - (d - 260) * 0.0055);

  // 第1段（手前）: 2レーン障害物＋安全レーン1つ
  const safe1 = Math.floor(Math.random() * 3);
  for (let l = 0; l < 3; l++) {
    if (l === safe1) {
      spawnBreadItem(l, spawnZ, 0.68);
      spawnBreadItem(l, spawnZ - 1.8, 0.68);
    } else if (Math.random() < 0.30 && crowDef) {
      spawnObstacleItem(l, spawnZ - 2.2, crowDef);
    } else {
      spawnObstacleItem(l, spawnZ, Math.random() < 0.55 ? pickHigh() : pickLow());
    }
  }

  // 第2段（奥 -4.8m）: safe1にも障害物を置いてジグザグ回避やジャンプを迫る
  const z2 = spawnZ - 4.8;
  const safe2 = (safe1 + 1 + Math.floor(Math.random() * 2)) % 3;
  if (Math.random() < 0.28) {
    // 第2段が全レーン低いゲート（ジャンプ突破）
    for (let l = 0; l < 3; l++) {
      spawnObstacleItem(l, z2, pickLow());
    }
    spawnBreadItem(safe2, z2, 1.88, 'bread_gold');
  } else {
    for (let l = 0; l < 3; l++) {
      if (l === safe2) {
        spawnBreadItem(l, z2, 0.68);
      } else if (l === safe1) {
        // さっき安全だったレーンに高い壁または低い障害物を配置
        spawnObstacleItem(l, z2, Math.random() < 0.65 ? pickHigh() : pickLow());
      } else if (Math.random() < 0.85) {
        spawnObstacleItem(l, z2, (Math.random() < 0.35 && crowDef) ? crowDef : pickLow());
      }
    }
  }

  // 激ムズ帯 (550m〜) はさらに第3段 (-9.4m) も追加して障害物密度を上げ続ける！
  if (isRush) {
    const z3 = spawnZ - 9.4;
    const safe3 = (safe2 + 1 + Math.floor(Math.random() * 2)) % 3;
    for (let l = 0; l < 3; l++) {
      if (l === safe3) {
        spawnBreadItem(l, z3, 0.68);
      } else if (l === safe2 || Math.random() < 0.75) {
        const useCrow = Math.random() < 0.32 && crowDef;
        spawnObstacleItem(l, z3, useCrow ? crowDef : (Math.random() < 0.5 ? pickHigh() : pickLow()));
      }
    }
    return baseGap + 7.2;
  }

  return baseGap + 4.0;
}

// --- 7. UI更新＆エフェクト ---
function showBanner(text) {
  const el = document.getElementById('banner-toast');
  if (!el) return;
  el.textContent = text;
  el.classList.add('show');
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove('show'), 1400);
}

function flashScreen(color) {
  const el = document.getElementById('screen-flash');
  if (!el) return;
  el.style.background = color;
  el.style.opacity = '0.42';
  setTimeout(() => { el.style.opacity = '0'; }, 160);
}

function updateHUD() {
  document.getElementById('score-display').textContent = `¥${game.score.toLocaleString()}`;
  document.getElementById('dist-display').textContent = `${Math.floor(game.distance)}m`;
  document.getElementById('lives-display').textContent = '❤️'.repeat(Math.max(0, game.lives)) + '🤍'.repeat(Math.max(0, 3 - game.lives));
  document.getElementById('combo-display').textContent = game.combo >= 2 ? `🔥 ${game.combo} COMBO!` : '';

  const fBar = document.getElementById('fever-bar-fill');
  const fLabel = document.getElementById('fever-label');
  if (game.feverTimer > 0) {
    fBar.style.width = `${(game.feverTimer / 3.5) * 100}%`;
    fLabel.textContent = `🔥 FEVER! ${Math.ceil(game.feverTimer)}s`;
  } else {
    fBar.style.width = `${Math.min(100, game.feverGauge)}%`;
    fLabel.textContent = `🔥 FEVER ${Math.floor(game.feverGauge)}%`;
  }

  const buffs = [];
  if (game.doubleTimer > 0) buffs.push(`<span class="buff-pill">🍳 得点2倍 (${Math.ceil(game.doubleTimer)}s)</span>`);
  if (game.magnetTimer > 0) buffs.push(`<span class="buff-pill">🍄 磁石 (${Math.ceil(game.magnetTimer)}s)</span>`);
  if (game.dashBoostTimer > 0) buffs.push(`<span class="buff-pill">🥖 無敵ダッシュ (${Math.ceil(game.dashBoostTimer)}s)</span>`);
  document.getElementById('buff-container').innerHTML = buffs.join('');
}

// --- 8. 操作（スワイプ＆キーボード） ---
function moveLane(delta) {
  if (!game.running) return;
  const next = Math.max(0, Math.min(2, game.lane + delta));
  if (next !== game.lane) {
    game.lane = next;
    sounds.playMove();
  }
}

function doJump() {
  if (!game.running) return;
  if (game.isGrounded) {
    game.vy = 11.2;
    game.isGrounded = false;
    switchJunAnim('Dash_Jump');
    sounds.playJump();
  }
}

function doFastFall() {
  if (!game.running) return;
  if (!game.isGrounded) {
    game.vy = Math.min(game.vy, -17.0);
  }
}

window.addEventListener('keydown', (e) => {
  if (!game.running) return;
  if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') moveLane(-1);
  else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') moveLane(1);
  else if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W' || e.key === ' ') {
    e.preventDefault();
    doJump();
  } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
    doFastFall();
  }
});

let touchStartX = 0, touchStartY = 0, touchHandled = false;
const gameContainer = document.getElementById('game-container');
gameContainer.addEventListener('touchstart', (e) => {
  if (!game.running || e.target.closest('button, a, input')) return;
  touchStartX = e.touches[0].clientX;
  touchStartY = e.touches[0].clientY;
  touchHandled = false;
}, { passive: true });

gameContainer.addEventListener('touchmove', (e) => {
  if (!game.running || touchHandled || e.target.closest('button, a, input')) return;
  const dx = e.touches[0].clientX - touchStartX;
  const dy = e.touches[0].clientY - touchStartY;
  if (Math.abs(dx) > 28 && Math.abs(dx) > Math.abs(dy)) {
    moveLane(dx > 0 ? 1 : -1);
    touchHandled = true;
  } else if (dy < -30 && Math.abs(dy) > Math.abs(dx)) {
    doJump();
    touchHandled = true;
  } else if (dy > 32 && Math.abs(dy) > Math.abs(dx)) {
    doFastFall();
    touchHandled = true;
  }
}, { passive: true });

gameContainer.addEventListener('touchend', (e) => {
  if (!game.running || touchHandled || e.target.closest('button, a, input')) return;
  const dx = e.changedTouches[0].clientX - touchStartX;
  const dy = e.changedTouches[0].clientY - touchStartY;
  if (Math.abs(dx) < 15 && Math.abs(dy) < 15) {
    doJump(); // 軽くタップでジャンプ！
  }
}, { passive: true });

// --- 9. ゲームループ ---
function startGame() {
  sounds.init();
  // 前回のクリア
  game.activeBreads.forEach(b => scene.remove(b.mesh));
  game.activeObstacles.forEach(o => scene.remove(o.mesh));
  game.activeBreads = [];
  game.activeObstacles = [];
  clearCarriedBreads();

  game.running = true;
  game.lane = 1;
  game.playerX = 0;
  game.playerY = 0;
  game.vy = 0;
  game.isGrounded = true;
  game.lives = 3;
  game.score = 0;
  game.distance = 0;
  game.breadsCollected = 0;
  game.combo = 0;
  game.maxCombo = 0;
  game.speed = 15.5;
  game.invincibleTimer = 0;
  game.feverGauge = 0;
  game.feverTimer = 0;
  game.doubleTimer = 0;
  game.magnetTimer = 0;
  game.dashBoostTimer = 0;
  game.shakeTimer = 0;
  game.nextSpawnDist = 4;
  game.lastRecordId = null;

  if (pukumukuShopMesh) {
    pukumukuShopMesh.position.set(-5.8, 0, -2.5);
    pukumukuShopMesh.visible = true;
  }

  document.getElementById('start-screen').classList.remove('active');
  document.getElementById('result-screen').classList.remove('active');
  document.getElementById('hud').classList.add('active');

  const hint = document.getElementById('swipe-hint');
  hint.classList.add('show');
  setTimeout(() => hint.classList.remove('show'), 3600);

  switchJunAnim('Dash_Run');
  sounds.isFever = false;
  sounds.startBGM();
  updateHUD();
}

function endGame() {
  game.running = false;
  sounds.stopBGM();
  switchJunAnim('Carry_Idle');

  document.getElementById('hud').classList.remove('active');
  document.getElementById('final-score-text').textContent = game.score.toLocaleString();
  document.getElementById('final-dist-text').textContent = Math.floor(game.distance).toLocaleString();
  document.getElementById('result-sub-info').textContent = `お届けパン：${game.breadsCollected}個 ／ 最大コンボ：${game.maxCombo}`;

  const submitBtn = document.getElementById('submit-ranking-btn');
  submitBtn.disabled = false;
  submitBtn.textContent = '登録！';
  document.getElementById('ranking-feedback').textContent = '';

  const savedName = localStorage.getItem(PLAYER_NAME_KEY) || '';
  if (savedName) {
    document.getElementById('player-name-input').value = savedName;
  }

  document.getElementById('result-screen').classList.add('active');
  fetchDashRankings(currentResultMode, 'result-ranking-list');
}

const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);

  if (junMixer) {
    junMixer.timeScale = game.running ? (game.speed / 12.0) : 1.0;
    junMixer.update(dt);
  }

  if (game.running) {
    // 速度曲線（最初は走りやすく、距離に応じてどんどん高速化）
    const baseSpeed = Math.min(28.0, 12.5 + game.distance * 0.015);
    const boostMul = game.dashBoostTimer > 0 ? 1.35 : (game.feverTimer > 0 ? 1.18 : 1.0);
    game.speed = baseSpeed * boostMul;
    const moveStep = game.speed * dt;
    game.distance += moveStep;

    // 道路UVスクロール
    roadTexture.offset.y -= moveStep * 0.127;

    // お店モデルの移動
    if (pukumukuShopMesh && pukumukuShopMesh.visible) {
      pukumukuShopMesh.position.z += moveStep;
      if (pukumukuShopMesh.position.z > 14) pukumukuShopMesh.visible = false;
    }

    // 街並み・街灯ループ
    sceneryProps.forEach(p => {
      p.mesh.position.z += moveStep;
      if (p.mesh.position.z > 10) {
        p.mesh.position.z -= 85;
      }
    });

    // 純くんの横移動＆傾き
    const targetX = LANE_X[game.lane];
    const diffX = targetX - game.playerX;
    game.playerX += diffX * Math.min(1, dt * 16);

    // 純くんのジャンプ物理
    if (!game.isGrounded) {
      game.vy += -28.0 * dt;
      game.playerY += game.vy * dt;
      if (game.playerY <= 0) {
        game.playerY = 0;
        game.vy = 0;
        game.isGrounded = true;
        switchJunAnim('Dash_Run');
      }
    }

    junKunGroup.position.set(game.playerX, game.playerY, 0);
    if (junKunModel) {
      junKunModel.rotation.z = -diffX * 0.16;
      // 無敵点滅演出
      if (game.invincibleTimer > 0 && game.dashBoostTimer <= 0 && game.feverTimer <= 0) {
        junKunModel.visible = Math.floor(game.invincibleTimer * 18) % 2 === 0;
      } else {
        junKunModel.visible = true;
      }
    }

    // カメラ追従＆シェイク
    const camTargetX = game.playerX * 0.35;
    camera.position.x += (camTargetX - camera.position.x) * Math.min(1, dt * 8);
    if (game.shakeTimer > 0) {
      game.shakeTimer -= dt;
      camera.position.y = 3.6 + (Math.random() - 0.5) * 0.28;
    } else {
      camera.position.y += (3.6 - camera.position.y) * Math.min(1, dt * 10);
    }

    // タイマー更新
    if (game.invincibleTimer > 0) game.invincibleTimer -= dt;
    if (game.doubleTimer > 0) game.doubleTimer -= dt;
    if (game.magnetTimer > 0) game.magnetTimer -= dt;
    if (game.dashBoostTimer > 0) game.dashBoostTimer -= dt;
    if (game.feverTimer > 0) {
      game.feverTimer -= dt;
      if (game.feverTimer <= 0) {
        game.feverTimer = 0;
        sounds.isFever = false;
      }
    }

    // Wave生成
    game.nextSpawnDist -= moveStep;
    if (game.nextSpawnDist <= 0) {
      game.nextSpawnDist = spawnWave();
    }

    const isInvincibleDash = (game.dashBoostTimer > 0 || game.feverTimer > 0);

    // パンアイテム更新＆当たり判定
    for (let i = game.activeBreads.length - 1; i >= 0; i--) {
      const b = game.activeBreads[i];
      b.mesh.position.z += moveStep;
      b.mesh.rotation.y += dt * 2.2;
      b.phase += dt * 4.5;
      b.mesh.position.y = b.yBase + Math.sin(b.phase) * 0.08;

      // マグネット時のみ控えめに吸い寄せ！（フィーバー時の自動吸引は廃止）
      if (b.key !== 'bread_burnt' && game.magnetTimer > 0 && b.mesh.position.z > -7.5 && b.mesh.position.z < 1.5) {
        b.mesh.position.x += (game.playerX - b.mesh.position.x) * Math.min(1, dt * 6.5);
        b.yBase += (game.playerY + 0.65 - b.yBase) * Math.min(1, dt * 6.5);
      }

      const dx = Math.abs(b.mesh.position.x - game.playerX);
      const dz = Math.abs(b.mesh.position.z - 0);
      const dy = Math.abs(b.mesh.position.y - (game.playerY + 0.65));

      if (!b.collected && dx < 0.95 && dz < 0.95 && dy < 1.15) {
        b.collected = true;
        scene.remove(b.mesh);
        game.activeBreads.splice(i, 1);

        if (b.key === 'bread_burnt') {
          if (!isInvincibleDash) {
            game.score = Math.max(0, game.score - 100);
            game.combo = 0;
            sounds.playHit();
            showBanner('⚠️ コゲパン！ -¥100');
          }
        } else {
          game.combo++;
          game.maxCombo = Math.max(game.maxCombo, game.combo);
          game.breadsCollected++;

          const mul = (game.doubleTimer > 0 ? 2 : 1) * (game.feverTimer > 0 ? 1.5 : 1);
          const pts = Math.round((b.def.score || 250) * mul);
          game.score += pts;
          addMiniBreadToBox(b.key);

          // フィーバーゲージ上昇（溜まりすぎないよう控えめに）
          if (game.feverTimer <= 0) {
            game.feverGauge += (b.key === 'bread_gold' ? 12 : 3.5);
            if (game.feverGauge >= 100) {
              game.feverGauge = 0;
              game.feverTimer = 3.5;
              sounds.isFever = true;
              sounds.playFever();
              flashScreen('#FFD54F');
              showBanner('🔥 焼きたてフィーバー!!');
            }
          }

          if (b.key === 'bread_gold') {
            sounds.playGold();
            showBanner(`✨ 金のパン！ +¥${pts.toLocaleString()}`);
          } else if (b.key === 'bread_egg') {
            game.doubleTimer = 7.0;
            sounds.playPower();
            showBanner('🍳 得点2倍タイム！');
          } else if (b.key === 'bread_mushroom') {
            game.magnetTimer = 4.5;
            sounds.playPower();
            showBanner('🍄 パン吸い寄せマグネット！');
          } else if (b.key === 'bread_negi') {
            game.dashBoostTimer = 5.0;
            sounds.playPower();
            showBanner('🥖 無敵ねぎダッシュ！');
          } else {
            sounds.playCatch(game.combo);
          }
        }
        updateHUD();
        continue;
      }

      if (b.mesh.position.z > 7.5) {
        scene.remove(b.mesh);
        game.activeBreads.splice(i, 1);
      }
    }

    // 障害物更新＆当たり判定
    for (let i = game.activeObstacles.length - 1; i >= 0; i--) {
      const o = game.activeObstacles[i];

      if (o.smashed) {
        o.vy -= 25 * dt;
        o.mesh.position.y += o.vy * dt;
        o.mesh.position.x += o.vx * dt;
        o.mesh.position.z -= moveStep * 0.6;
        o.mesh.rotation.x += dt * 10;
        o.mesh.rotation.z += dt * 8;
        if (o.mesh.position.y < -3 || o.mesh.position.z < -40) {
          scene.remove(o.mesh);
          game.activeObstacles.splice(i, 1);
        }
        continue;
      }

      o.mesh.position.z += moveStep + (o.def.isCrow ? 7.5 * dt : 0);
      if (o.def.isCrow) {
        o.phase += dt * 7.5;
        o.mesh.position.y = 0.35 + Math.sin(o.phase) * 0.14;
      }

      const dx = Math.abs(o.mesh.position.x - game.playerX);
      const dz = Math.abs(o.mesh.position.z - 0);

      if (!o.hit && dx < 0.62 && dz < 0.56) {
        // ジャンプで飛び越えられるか？
        const clearedByJump = o.def.canJumpOver && (game.playerY >= o.def.hitHeight - 0.14);
        if (!clearedByJump) {
          if (isInvincibleDash) {
            o.smashed = true;
            o.vy = 11;
            o.vx = (o.mesh.position.x >= game.playerX ? 1 : -1) * 5;
            game.score += 300;
            sounds.playSmash();
            showBanner('💥 粉砕ボーナス +¥300！');
            updateHUD();
            continue;
          } else if (game.invincibleTimer <= 0) {
            o.hit = true;
            game.lives--;
            game.combo = 0;
            game.invincibleTimer = 1.6;
            game.shakeTimer = 0.28;
            sounds.playHit();
            flashScreen('#FF1744');
            updateHUD();

            if (game.lives <= 0) {
              endGame();
              break;
            }
          }
        }
      }

      if (o.mesh.position.z > 7.5) {
        scene.remove(o.mesh);
        game.activeObstacles.splice(i, 1);
      }
    }

    // 距離更新（毎フレーム軽量反映）
    document.getElementById('dist-display').textContent = `${Math.floor(game.distance)}m`;
    if (game.feverTimer > 0) updateHUD();
  }

  renderer.render(scene, camera);
}

// --- 10. ランキングシステム (GAS + ローカルAPI + localStorage 1人1枠) ---
let currentModalMode = 'score';
let currentResultMode = 'score';

function escapeHtml(str) {
  return String(str || '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
}

function formatDateDisplay(raw) {
  if (!raw) return '';
  try {
    const d = new Date(String(raw).replace(/\(.*\)/, '').trim());
    if (!isNaN(d.getTime())) {
      return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
    }
  } catch (e) {}
  return String(raw).slice(0, 11);
}

function getLocalDashRankings() {
  try {
    const raw = localStorage.getItem(LOCAL_DASH_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}
  return [
    { id: 'd1', name: 'プクムク店長', score: 24500, distance: 420, date: '11/14 09:00' },
    { id: 'd2', name: '早起きパン職人', score: 18200, distance: 340, date: '11/14 09:15' },
    { id: 'd3', name: 'クロワッサン好き', score: 14800, distance: 280, date: '11/14 09:30' },
    { id: 'd4', name: '看板娘みく', score: 11200, distance: 210, date: '11/14 10:00' },
    { id: 'd5', name: '見習いコッペ', score: 7500, distance: 150, date: '11/14 10:15' }
  ];
}

function saveLocalDashEntry(entry) {
  const list = getLocalDashRankings();
  const idx = list.findIndex(r => (r.name || '').trim() === entry.name);
  if (idx !== -1) {
    list[idx] = {
      ...list[idx],
      id: entry.id,
      score: Math.max(Number(list[idx].score || 0), entry.score),
      distance: Math.max(Number(list[idx].distance || 0), entry.distance),
      date: entry.date
    };
  } else {
    list.push(entry);
  }
  try { localStorage.setItem(LOCAL_DASH_KEY, JSON.stringify(list)); } catch (e) {}
}

async function fetchDashRankings(mode = 'score', containerId = 'modal-ranking-list') {
  const listEl = document.getElementById(containerId);
  if (!listEl) return;
  listEl.innerHTML = '<div class="ranking-row"><span style="flex:1; text-align:center;">⏳ ランキング読込中...</span></div>';

  const records = [];
  try {
    const res = await fetch(`${LOCAL_DASH_API}?t=${Date.now()}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      const arr = mode === 'dist' ? (data.distRankings || []) : (data.scoreRankings || []);
      records.push(...arr);
    }
  } catch (e) {}

  try {
    const gasRes = await fetch(`${DASH_GAS_API_URL}?game=bread_dash&sheet=bread_dash&mode=${mode}&t=${Date.now()}`, { cache: 'no-store' });
    if (gasRes.ok) {
      const gasData = await gasRes.json();
      const arr = Array.isArray(gasData) ? gasData : (gasData.rankings || []);
      arr.forEach((r, idx) => {
        if (r.game === 'bread_dash' || r.distance !== undefined) {
          records.push({
            id: r.id || `gas_${idx}_${r.name}`,
            name: String(r.name || '名無し職人'),
            score: Number(r.score || 0),
            distance: Number(r.distance || 0),
            date: r.date || ''
          });
        }
      });
    }
  } catch (e) {}

  const combined = [...records, ...getLocalDashRankings()].map(r => ({
    id: r.id,
    name: String(r.name || '名無し職人').trim().slice(0, 12),
    score: Number(r.score || 0),
    distance: Number(r.distance || 0),
    date: r.date || ''
  }));

  if (mode === 'dist') {
    combined.sort((a, b) => (b.distance - a.distance) || (b.score - a.score));
  } else {
    combined.sort((a, b) => (b.score - a.score) || (b.distance - a.distance));
  }

  const unique = [];
  const seen = new Set();
  for (const r of combined) {
    if (!r.name || seen.has(r.name)) continue;
    seen.add(r.name);
    unique.push(r);
  }

  renderDashRanking(unique.slice(0, 10), mode, listEl);
}

function renderDashRanking(items, mode, el) {
  const medals = ['🥇', '🥈', '🥉', '4位', '5位', '6位', '7位', '8位', '9位', '10位'];
  const currentName = localStorage.getItem(PLAYER_NAME_KEY) || '';

  el.innerHTML = items.map((item, idx) => {
    const isMe = (game.lastRecordId && item.id === game.lastRecordId) || (game.lastRecordId && currentName && item.name === currentName);
    const valStr = mode === 'dist' ? `${Math.floor(item.distance)} m` : `¥${item.score.toLocaleString()}`;
    return `
      <div class="ranking-row ${isMe ? 'current-play' : ''}">
        <span class="ranking-rank">${medals[idx] || (idx + 1 + '位')}</span>
        <span class="ranking-name" title="${escapeHtml(item.name)}">🏃 ${escapeHtml(item.name)}</span>
        <span class="ranking-score">${valStr}</span>
        <span class="ranking-date">${escapeHtml(formatDateDisplay(item.date))}</span>
      </div>
    `;
  }).join('');
}

async function submitDashScore() {
  const input = document.getElementById('player-name-input');
  const btn = document.getElementById('submit-ranking-btn');
  const fb = document.getElementById('ranking-feedback');

  const name = (input.value.trim() || '名無し職人').slice(0, 12);
  localStorage.setItem(PLAYER_NAME_KEY, name);

  btn.disabled = true;
  btn.textContent = '送信中...';

  const entry = {
    id: 'dash_' + Date.now(),
    name,
    score: game.score,
    distance: Math.floor(game.distance),
    date: new Date().toISOString()
  };
  game.lastRecordId = entry.id;
  saveLocalDashEntry(entry);

  try {
    await fetch(LOCAL_DASH_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry)
    });
  } catch (e) {}

  try {
    fetch(DASH_GAS_API_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({ action: 'register', game: 'bread_dash', sheet: 'bread_dash', ...entry })
    }).catch(() => {});
  } catch (e) {}

  btn.textContent = '登録済！';
  fb.textContent = `🎉 「${name}」さんの記録を登録しました！`;
  fetchDashRankings(currentResultMode, 'result-ranking-list');
}

// --- 11. イベント設定 ---
document.getElementById('start-btn').addEventListener('click', startGame);
document.getElementById('restart-btn').addEventListener('click', startGame);
document.getElementById('submit-ranking-btn').addEventListener('click', submitDashScore);

document.getElementById('sound-btn').addEventListener('click', () => {
  sounds.muted = !sounds.muted;
  document.getElementById('sound-btn').textContent = sounds.muted ? '🔇' : '🔊';
});

const guideModal = document.getElementById('guide-modal');
document.getElementById('open-guide-btn').addEventListener('click', () => guideModal.classList.add('active'));
document.getElementById('close-guide-btn').addEventListener('click', () => guideModal.classList.remove('active'));

const rankingModal = document.getElementById('ranking-modal');
document.getElementById('open-ranking-btn').addEventListener('click', () => {
  rankingModal.classList.add('active');
  fetchDashRankings(currentModalMode, 'modal-ranking-list');
});
document.getElementById('close-ranking-btn').addEventListener('click', () => rankingModal.classList.remove('active'));

document.getElementById('modal-tab-score').addEventListener('click', (e) => {
  currentModalMode = 'score';
  e.target.classList.add('active');
  document.getElementById('modal-tab-dist').classList.remove('active');
  fetchDashRankings('score', 'modal-ranking-list');
});
document.getElementById('modal-tab-dist').addEventListener('click', (e) => {
  currentModalMode = 'dist';
  e.target.classList.add('active');
  document.getElementById('modal-tab-score').classList.remove('active');
  fetchDashRankings('dist', 'modal-ranking-list');
});

document.getElementById('result-tab-score').addEventListener('click', (e) => {
  currentResultMode = 'score';
  e.target.classList.add('active');
  document.getElementById('result-tab-dist').classList.remove('active');
  fetchDashRankings('score', 'result-ranking-list');
});
document.getElementById('result-tab-dist').addEventListener('click', (e) => {
  currentResultMode = 'dist';
  e.target.classList.add('active');
  document.getElementById('result-tab-score').classList.remove('active');
  fetchDashRankings('dist', 'result-ranking-list');
});

window.addEventListener('resize', () => {
  camera.aspect = canvasWrap.clientWidth / Math.max(1, canvasWrap.clientHeight);
  camera.updateProjectionMatrix();
  renderer.setSize(canvasWrap.clientWidth, canvasWrap.clientHeight);
});

animate();
