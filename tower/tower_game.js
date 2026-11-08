// ============================================================
// 🍔 ぐらぐら！サンドイッチタワー (C) パン工房プクムク
// Three.js + Cannon.js 3D物理シミュレーション (パンケーキタワー風)
// ============================================================

// --- 1. サウンドシステム (Web Audio API: 100%著作権フリー) ---
class TowerSoundSystem {
  constructor() {
    this.ctx = null;
    this.isMuted = false;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
  }

  toggleMute() {
    this.init();
    this.isMuted = !this.isMuted;
    return this.isMuted;
  }

  // 具材投下音（可愛いスライドホイッスル風「ヒュンッ♪」）
  playDrop() {
    if (this.isMuted || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(175, now + 0.14);
      gain.gain.setValueAtTime(0.07, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.15);
    } catch (e) {}
  }

  // 着地音（積むほどド・レ・ミ・ファ・ソ・ラ・シ・ド♪と音階が上がる楽しい木琴マリンバ風サウンド！）
  playLand(stackCount = 0) {
    if (this.isMuted || !this.ctx) return;
    const nowMs = performance.now();
    if (this.lastLandTime && nowMs - this.lastLandTime < 180) return; // 多重ノイズ完全防止
    this.lastLandTime = nowMs;

    try {
      const now = this.ctx.currentTime;
      // Cメジャースケール（ド・レ・ミ・ファ・ソ・ラ・シ・ド・レ・ミ・ファ・ソ・ラ・シ・高ド）
      const scaleFreqs = [
        261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88,
        523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50
      ];
      const idx = Math.min(scaleFreqs.length - 1, Math.max(0, stackCount));
      const freq = scaleFreqs[idx];

      // メイン音（丸みのあるマリンバ基本波）
      const osc1 = this.ctx.createOscillator();
      const gain1 = this.ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(freq, now);
      gain1.gain.setValueAtTime(0.08, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
      osc1.connect(gain1);
      gain1.connect(this.ctx.destination);
      osc1.start(now);
      osc1.stop(now + 0.17);

      // 木琴のアタック倍音（2オクターブ上の短いコツッという響き）
      const osc2 = this.ctx.createOscillator();
      const gain2 = this.ctx.createGain();
      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(freq * 2.0, now);
      gain2.gain.setValueAtTime(0.03, now);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
      osc2.connect(gain2);
      gain2.connect(this.ctx.destination);
      osc2.start(now);
      osc2.stop(now + 0.06);
    } catch (e) {}
  }

  // PERFECT キラキラチャイム（ティロリロリーン✨）
  playPerfect() {
    if (this.isMuted || !this.ctx) return;
    [523.25, 659.25, 783.99, 1046.50, 1318.51].forEach((freq, idx) => {
      setTimeout(() => {
        try {
          const now = this.ctx.currentTime;
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now);
          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + 0.19);
        } catch (e) {}
      }, idx * 45);
    });
  }

  // レシピ完成ボーナス音（パパパパーン🎉）
  playRecipeCombo() {
    this.playRecipeBonus();
  }
  playRecipeBonus() {
    if (this.isMuted || !this.ctx) return;
    const notes = [
      { f: 587.33, d: 0, len: 0.10 },
      { f: 587.33, d: 90, len: 0.10 },
      { f: 587.33, d: 180, len: 0.10 },
      { f: 880.00, d: 280, len: 0.32 }
    ];
    notes.forEach(n => {
      setTimeout(() => {
        try {
          const now = this.ctx.currentTime;
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(n.f, now);
          gain.gain.setValueAtTime(0.075, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + n.len);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + n.len + 0.02);
        } catch (e) {}
      }, n.d);
    });
  }

  // レア具材登場音（キラーン🌟）
  playRareAppear() {
    this.playRareSpawn();
  }
  playRareSpawn() {
    if (this.isMuted || !this.ctx) return;
    [880, 1174.66, 1760].forEach((freq, idx) => {
      setTimeout(() => {
        try {
          const now = this.ctx.currentTime;
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now);
          gain.gain.setValueAtTime(0.06, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + 0.17);
        } catch (e) {}
      }, idx * 55);
    });
  }

  // バーガー完成！祝福大ファンファーレ（🎊）
  playFanfare() {
    this.playCompleteFanfare();
  }
  playCompleteFanfare() {
    if (this.isMuted || !this.ctx) return;
    const melody = [
      { f: 523.25, d: 0, len: 0.14 },
      { f: 659.25, d: 130, len: 0.14 },
      { f: 783.99, d: 260, len: 0.14 },
      { f: 1046.50, d: 400, len: 0.18 },
      { f: 783.99, d: 560, len: 0.14 },
      { f: 1046.50, d: 700, len: 0.45 }
    ];
    melody.forEach(n => {
      setTimeout(() => {
        try {
          const now = this.ctx.currentTime;
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(n.f, now);
          gain.gain.setValueAtTime(0.09, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + n.len);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now);
          osc.stop(now + n.len + 0.02);
        } catch (e) {}
      }, n.d);
    });
  }

  // 落下音（コミカルな「ヒュ〜ドン」）
  playFall() {
    if (this.isMuted || !this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(180, now);
      osc.frequency.exponentialRampToValueAtTime(45, now + 0.22);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start(now);
      osc.stop(now + 0.23);
    } catch (e) {}
  }

  // 営業終了ファンファーレ
  playGameOver() {
    if (this.isMuted || !this.ctx) return;
    [261.63, 329.63, 392.00, 523.25].forEach((freq, idx) => {
      setTimeout(() => {
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
          gain.gain.setValueAtTime(0.22, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.3);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.31);
        } catch (e) {}
      }, idx * 100);
    });
  }
}

const sounds = new TowerSoundSystem();

// --- 2. 全13種類の具材定義 (高さcm・純利益price・図鑑説明desc付き) ---
const INGREDIENTS_DEF = [
  // 1. 肉厚パティ
  {
    id: 'item_patty',
    name: '🥩 肉厚パティ',
    type: 'cylinder',
    radius: 0.50,
    height: 0.195, // 1.95 cm
    price: 450,
    desc: 'ジューシーな100%ビーフ！分厚くて安定感バツグンの主役具材。',
    mass: 1.0,
    friction: 0.98,
    color: 0x4A2E18,
    glbFile: 'item_patty.glb'
  },
  // 2. とろけるチーズ
  {
    id: 'item_cheese',
    name: '🧀 とろけるチーズ',
    type: 'box',
    width: 0.95,
    height: 0.085, // 0.85 cm
    depth: 0.96,
    price: 250,
    desc: '濃厚チェダーチーズ。薄くて平らなのでタワーの土台固めに最適！',
    mass: 1.0,
    friction: 0.98,
    color: 0xFFC107,
    glbFile: 'item_cheese.glb'
  },
  // 3. スライストマト
  {
    id: 'item_tomato',
    name: '🍅 スライストマト',
    type: 'cylinder',
    radius: 0.51,
    height: 0.126, // 1.26 cm
    price: 300,
    desc: '真っ赤な完熟トマト。レタス・ベーコンと重ねるとBLTコンボ発動！',
    mass: 1.0,
    friction: 0.98,
    color: 0xE53935,
    glbFile: 'item_tomato.glb'
  },
  // 4. フリルレタス
  {
    id: 'item_lettuce',
    name: '🥬 フリルレタス',
    type: 'box',
    width: 1.06,
    height: 0.148, // 1.48 cm
    depth: 0.96,
    price: 220,
    desc: 'シャキシャキの新鮮レタス。幅が広くて上の具材を受け止めやすい！',
    mass: 1.0,
    friction: 0.98,
    color: 0x43A047,
    glbFile: 'item_lettuce.glb'
  },
  // 5. ぷるぷる目玉焼き
  {
    id: 'item_fried_egg',
    name: '🍳 ぷるぷる目玉焼き',
    type: 'cylinder',
    radius: 0.49,
    height: 0.156, // 1.56 cm
    price: 350,
    desc: '半熟とろ〜り目玉焼き。パティと重ねると月見バーガーコンボ！',
    mass: 1.0,
    friction: 0.98,
    color: 0xFFF9C4,
    glbFile: 'item_fried_egg.glb'
  },
  // 6. カリカリベーコン
  {
    id: 'item_bacon',
    name: '🥓 カリカリベーコン',
    type: 'box',
    width: 0.96,
    height: 0.16, // 1.60 cm
    depth: 0.66,
    price: 400,
    desc: '香ばしいスモークベーコン。高単価で純利益がぐんぐん伸びる！',
    mass: 1.0,
    friction: 0.98,
    color: 0xB71C1C,
    glbFile: 'item_bacon.glb'
  },
  // 7. スライスきゅうり
  {
    id: 'item_cucumber',
    name: '🥒 スライスきゅうり',
    type: 'cylinder',
    radius: 0.44,
    height: 0.109, // 1.09 cm
    price: 180,
    desc: 'みずみずしいきゅうり。少し小ぶりなので真ん中を狙って落とそう！',
    mass: 1.0,
    friction: 0.98,
    color: 0x2E7D32,
    glbFile: 'item_cucumber.glb'
  },
  // 8. オニオンリング
  {
    id: 'item_onion',
    name: '🧅 オニオンリング',
    type: 'cylinder',
    radius: 0.51,
    height: 0.08, // 0.80 cm
    price: 200,
    desc: '甘みたっぷりの紫玉ねぎスライス。薄型でバランスを崩しにくい！',
    mass: 1.0,
    friction: 0.98,
    color: 0x7B1FA2,
    glbFile: 'item_onion.glb'
  },
  // 9. クリーミーアボカド
  {
    id: 'item_avocado',
    name: '🥑 スライスアボカド',
    type: 'box',
    width: 0.94,
    height: 0.10, // 1.00 cm
    depth: 0.88,
    price: 380,
    desc: '森のバターと呼ばれる濃厚アボカド。カフェ風リッチサンドに！',
    mass: 1.0,
    friction: 0.98,
    color: 0x558B2F,
    glbFile: 'item_avocado.glb'
  },
  // 10. ふっくらパンケーキ
  {
    id: 'item_pancake',
    name: '🥞 ふっくらパンケーキ',
    type: 'cylinder',
    radius: 0.52,
    height: 0.190, // 1.90 cm
    price: 420,
    desc: 'プクムク自慢の厚焼きパンケーキ！高さも値段もトップクラス。',
    mass: 1.0,
    friction: 0.98,
    color: 0xDDA15E,
    glbFile: 'item_pancake.glb'
  },
  // 11. 【レア具材】黄金の特大パティ（幅広で超積みやすく、一撃+¥2,000！）
  {
    id: 'item_golden_patty',
    name: '🌟 金の特大パティ',
    type: 'cylinder',
    radius: 0.61,
    height: 0.21, // 2.10 cm
    price: 2000,
    desc: '【レア】24Kに輝く特大黄金パティ！超幅広で積みやすく一撃¥2,000！',
    mass: 1.0,
    friction: 0.98,
    color: 0xFFD700,
    isRare: true,
    bonusScore: 2000,
    glbFile: 'item_patty.glb'
  },
  // 12. 【レア具材】一本丸ごと極太ソーセージ（インパクト抜群、一撃+¥1,800！）
  {
    id: 'item_mega_sausage',
    name: '🌭 極太ソーセージ',
    type: 'box',
    width: 1.02,
    height: 0.18, // 1.80 cm
    depth: 0.54,
    price: 1800,
    desc: '【レア】パリッとジューシーな極太ソーセージ！一撃¥1,800の大ボーナス！',
    mass: 1.0,
    friction: 0.98,
    color: 0xC62828,
    isRare: true,
    bonusScore: 1800,
    glbFile: 'item_bacon.glb'
  }
];

// ★仕上げ用「特製ゴマ付き上バンズ（Top Bun）」定義
const TOP_BUN_DEF = {
  id: 'item_top_bun',
  name: '👑 特製上バンズ',
  type: 'cylinder',
  radius: 0.64,
  height: 0.28, // 2.80 cm
  price: 1000,
  desc: '【仕上げ専用】最後にこれを見事乗せて完成させると、獲得純利益が【2倍】に！！',
  mass: 1.0,
  friction: 0.98,
  color: 0xD28238,
  isTopBun: true
};

// --- 3. ゲーム管理変数 ---
let scene, camera, renderer, world;
let plateBody, baseBunBody, baseBunMesh;
window.getActiveItems = () => activeItems;
let activeItems = []; // { def, mesh, body, state, ... }
let activeParticles = []; // 3Dキラキラ・ジューシーエフェクト配列
let currentHeldMesh = null;
let currentHeldDef = null;
let nextItemDef = null;
let currentDroppingItem = null; // ★現在投下中の具材（着地・接触または落下するまで次の具材を出さない厳格ロック用）
let isGameCompletedWithBun = false; // 上バンズで完成させたかどうか

let isPlaying = false;
let isDropping = false;
let lives = 3;
let stackedCount = 0;
let lastStackedCount = 0;
let highestY = 0; // スタックされた上面の最高Y座標
window.tongX = 0; // トングX位置
let gameStartTime = 0; // スタート直後のタップ抜け防止用タイムスタンプ

// 左右スイング関連（お皿のギリギリ外に落ちないよう振幅を0.54に最適化）
let tongSwingTime = 0;
const TONG_SWING_AMPLITUDE = 0.54; // お皿の内側にしっかり収まる快適な揺れ幅
const TONG_SWING_BASE_SPEED = 2.0; // 揺れの基本速度

let basePlateY = 0.4;

// トング関連 (物理投下高0.95でお皿/塔から高く配置、先端が具材をつかむ隙間0.02、Armパカッ開閉対応)
const TONG_HEIGHT_OFFSET = 0.95; // 物理投下高さ（トングと具材一式をお皿/塔上面から高く配置）
const TONG_VISUAL_OFFSET = 0.02; // 見た目の隙間（先端が具材上面をつかむ見た目）
let tongMeshGroup = null;
let tongArmL = null;
let tongArmR = null;
let currentTongOpen = 0.0;
let targetTongOpen = 0.0;
let tongRecoilY = 0.0; // 投下時にキュッと跳ね上がるリコイル演出
let isGLBTongsLoaded = false;
let studioEnvMap = null; // トング金属専用の環境マップ（パンや皿の白飛びを防止）

// スマートカメラ関連（全表示要素のBox3 + 縦横FOVに基づく連続フレーミング）
let currentLookY = 1.0;
let targetLookY = 1.0;
let currentCameraDistance = 5.2;
let targetCameraDistance = 5.2;
const CAMERA_PITCH_ANGLE = 14 * Math.PI / 180; // 約14度見下ろす自然な俯瞰アングル
let diagnosticSimulatedHeight = null; // 診断用シミュレーション高さ（null時は実スタック高）

// 中心コンボ関連
let currentCombo = 0;
let maxCombo = 0;
let totalScore = 0;

// 純くん関連 (独立小台・足元接地・全身ダイナミックアクション)
let junKun = null;
let junKunMixer = null;
let junKunAnimations = {};
let junKunCurrentAction = null;
let junKunStool = null;
let junBodyNode = null;
let junLegL = null;
let junLegR = null;
const junKunBaseY = 0.30; // スツール上面Y座標にピッタリ接地
let junHopTime = 0;
let junSpinTime = 0; // 360度ハッピースピン時間

// GLBモデルキャッシュ（中央補正済みテンプレート）
const loadedGLBModels = {};
const gltfLoader = new THREE.GLTFLoader();
// /tower/ 配下でも sandwich_tower.html(ルート) 配下でも共通でmodels/を参照できるベースパス
const MODELS_BASE = (location.pathname.includes('/tower/')) ? '../models/' : 'models/';

// localStorageキー
const BEST_HEIGHT_KEY = 'pukumuku_tower_best_height_v2';
const BEST_SCORE_KEY = 'pukumuku_tower_best_score_v2';

// --- 4. 初期化 ---
function initGame() {
  const container = document.getElementById('game-container');
  const canvas = document.getElementById('webgl-canvas');
  const width = container.clientWidth;
  const height = container.clientHeight;

  // 1. Three.js シーン
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xFFF8E7);
  scene.fog = new THREE.FogExp2(0xFFF8E7, 0.020);

  // 2. カメラ (スマホ 415x740 / 390x667 最適化: 全要素包含スマートフレーミング)
  camera = new THREE.PerspectiveCamera(54, width / height, 0.1, 100);
  updateSmartCamera(1.0); // 初期位置・距離・注視点を即時計算

  window.camera = camera;
  window.scene = scene;
  window.getActiveItems = () => activeItems;
  window.getStackedCount = () => stackedCount;
  window.getHighestY = () => highestY;
  window.getIsDropping = () => isDropping;
  window.getCurrentHeldDef = () => currentHeldDef;
  window.getCurrentHeldMesh = () => currentHeldMesh;
  window.getLives = () => lives;
  window.simulateTowerHeight = (h) => { diagnosticSimulatedHeight = h; updateSmartCamera(1.0); };
  window.getDiagnosticState = () => ({
    highestY,
    diagnosticSimulatedHeight,
    cameraDistance: currentCameraDistance,
    lookY: currentLookY,
    cameraPos: { x: camera.position.x, y: camera.position.y, z: camera.position.z }
  });

  // 3. レンダラー
  renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // 4. トング金属専用スタジオ環境マップ生成（scene.environmentには入れず白飛び完全防止）
  setupStudioEnvironment();

  // 5. 照明（白飛びのない温かみのあるこんがりキツネ色を引き立てる自然光）
  const ambientLight = new THREE.AmbientLight(0xFFEFE0, 0.55);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xFFFAF0, 0.75);
  dirLight.position.set(3.0, 10.0, 4.5);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 1024;
  dirLight.shadow.mapSize.height = 1024;
  dirLight.shadow.camera.near = 0.5;
  dirLight.shadow.camera.far = 30;
  dirLight.shadow.camera.left = -3;
  dirLight.shadow.camera.right = 3;
  dirLight.shadow.camera.top = 10;
  dirLight.shadow.camera.bottom = -2;
  scene.add(dirLight);

  // 6. Cannon 物理ワールド
  world = new CANNON.World();
  world.gravity.set(0, -9.82, 0);
  world.broadphase = new CANNON.NaiveBroadphase();
  world.solver.iterations = 16;

  // ★反発ゼロ＆超高摩擦設定（パンケーキタワー仕様: ピタッと安定し、崩れにくくサクサク積める！）
  world.defaultContactMaterial.friction = 0.98;
  world.defaultContactMaterial.restitution = 0.0;
  world.defaultContactMaterial.contactEquationStiffness = 1e7;
  world.defaultContactMaterial.contactEquationRelaxation = 3;

  // 6. テーブルとお皿の作成
  createTableAndPlate();
  // ※ユーザー要望により後ろのプクムク店舗背景は削除し、清潔でシンプルなスタジオ背景に
  createTongModel();

  // 7. 純くん専用の独立小台 & 純くん（3Dキャラクター）の読み込み
  createJunKunStool();
  loadJunKun();

  // 8. 全10種類具材GLBモデルの非同期先読み＆原点中央補正
  preloadGLBModels();

  // 9. 最高記録の表示 & 具材図鑑の生成
  displayBestRecords();
  renderIngredientCatalog();

  // 10. リサイズ処理
  window.addEventListener('resize', onWindowResize);

  // 11. 手動操作（ドラッグ、スライダー、ボタン、キーボード）のバインド
  bindManualControlEvents();

  // 12. アニメーションループ開始
  requestAnimationFrame(animate);
}

// PMREMGeneratorによる簡易スタジオ環境マップ（外部HDR不要で金属パーツに銀色の反射光を付与）
function setupStudioEnvironment() {
  const envScene = new THREE.Scene();

  // 明るい灰色の室内ドーム（BackSide）
  const domeGeo = new THREE.SphereGeometry(15, 16, 16);
  const domeMat = new THREE.MeshBasicMaterial({
    color: 0xE2E8F0,
    side: THREE.BackSide
  });
  envScene.add(new THREE.Mesh(domeGeo, domeMat));

  // 上部ソフトボックス（天窓・上部照明パネル）
  const panelGeo = new THREE.PlaneGeometry(10, 10);
  const panelMatTop = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
  const panelTop = new THREE.Mesh(panelGeo, panelMatTop);
  panelTop.position.set(0, 8, 0);
  panelTop.rotation.x = Math.PI / 2;
  envScene.add(panelTop);

  // 斜め前方左右の反射パネル（トング側面に美しいハイライトを走らせる）
  const panelSideMat = new THREE.MeshBasicMaterial({ color: 0xF8FAFC });
  const panelL = new THREE.Mesh(panelGeo, panelSideMat);
  panelL.position.set(-6, 5, 5);
  panelL.lookAt(0, 1, 0);
  envScene.add(panelL);

  const panelR = new THREE.Mesh(panelGeo, panelSideMat);
  panelR.position.set(6, 5, 5);
  panelR.lookAt(0, 1, 0);
  envScene.add(panelR);

  // PMREMGeneratorでキューブマップテクスチャを1度だけ生成してstudioEnvMapに保存
  // ★scene.environmentには入れず、トングの金属材質にだけ割り当てることでパンや皿の白飛びを100%防止！
  const pmremGen = new THREE.PMREMGenerator(renderer);
  pmremGen.compileEquirectangularShader();
  studioEnvMap = pmremGen.fromScene(envScene, 0.04).texture;
  pmremGen.dispose();
}

// 純くん専用の独立小台（ステップスツール: お皿やタワーと干渉せず足裏接地・ステップ移動できるよう少し広め）
function createJunKunStool() {
  const stoolGeo = new THREE.CylinderGeometry(0.28, 0.32, 0.30, 24);
  const stoolMat = new THREE.MeshStandardMaterial({
    color: 0x8D6E63,
    roughness: 0.65
  });
  junKunStool = new THREE.Mesh(stoolGeo, stoolMat);
  // お皿の外側左手前、塔と被らず全身が完全に見える位置。上面 Y=0.30
  junKunStool.position.set(-0.62, 0.15, 1.22);
  junKunStool.receiveShadow = true;
  junKunStool.castShadow = true;
  scene.add(junKunStool);
}

// 全具材GLBモデルの先読み＆Box3中央補正（ロード完了時に保持具材を即座にリアルモデルへ差し替え）
function preloadGLBModels() {
  const loadedFiles = new Set();
  INGREDIENTS_DEF.forEach(def => {
    if (def.glbFile && !loadedFiles.has(def.glbFile)) {
      loadedFiles.add(def.glbFile);
      gltfLoader.load(`${MODELS_BASE}${def.glbFile}`, (gltf) => {
        const rawModel = gltf.scene;

        rawModel.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });

        const box = new THREE.Box3().setFromObject(rawModel);
        const center = new THREE.Vector3();
        box.getCenter(center);

        const wrapper = new THREE.Group();
        rawModel.position.set(-center.x, -center.y, -center.z);
        wrapper.add(rawModel);

        loadedGLBModels[def.id] = wrapper;
        updateCatalogThumbnailForId(def.id);

        // 同じGLBファイルを共有しているレア具材（金の特大パティ・極太ソーセージ）にもモデルを共有登録！
        INGREDIENTS_DEF.forEach(otherDef => {
          if (otherDef.id !== def.id && otherDef.glbFile === def.glbFile) {
            loadedGLBModels[otherDef.id] = wrapper.clone(true);
            updateCatalogThumbnailForId(otherDef.id);
          }
        });

        // もし現在トングで保持中の具材が未ロードだった場合、リアルGLBへ自動差し替え
        if (currentHeldDef && currentHeldDef.id === def.id && currentHeldMesh && isPlaying && !isDropping) {
          const oldPos = currentHeldMesh.position.clone();
          scene.remove(currentHeldMesh);
          currentHeldMesh = createIngredientMesh(currentHeldDef);
          currentHeldMesh.position.copy(oldPos);
          scene.add(currentHeldMesh);
        }
      }, undefined, (err) => {
        console.warn(`Fallback to procedural for ${def.id}:`, err);
      });
    }
  });
}

// 土台パン＆仕上げ用「特製ゴマ付き上バンズ」のリアルGLB読み込み（models/bread_burger_unity.glb）
function loadBaseBunGLB() {
  gltfLoader.load(`${MODELS_BASE}bread_burger_unity.glb`, (gltf) => {
    let bottomBun = null;
    let topBunMesh = null;
    const sesameSeeds = [];

    gltf.scene.traverse((child) => {
      if (child.isMesh) {
        const n = child.name || '';
        if (n.includes('bottom bun') || n.includes('bottom_bun')) {
          bottomBun = child.clone();
        } else if (n.includes('top bun') || n.includes('top_bun')) {
          topBunMesh = child.clone();
        } else if (n.includes('sesame')) {
          sesameSeeds.push(child.clone());
        }
      }
    });

    // 1. 土台パン（下バンズ）の差し替え
    if (bottomBun) {
      if (baseBunMesh) scene.remove(baseBunMesh);
      bottomBun.scale.set(1.48, 0.95, 1.48);
      bottomBun.position.set(0, basePlateY + 0.12, 0);
      bottomBun.castShadow = true;
      bottomBun.receiveShadow = true;
      baseBunMesh = bottomBun;
      scene.add(baseBunMesh);
    }

    // 2. 仕上げ用「特製ゴマ付き上バンズ（TOP_BUN_DEF）」モデルの構築＆キャッシュ
    if (topBunMesh) {
      const topGroup = new THREE.Group();
      topBunMesh.castShadow = true;
      topBunMesh.receiveShadow = true;
      topGroup.add(topBunMesh);
      sesameSeeds.forEach(s => {
        s.castShadow = true;
        s.receiveShadow = true;
        topGroup.add(s);
      });

      const box = new THREE.Box3().setFromObject(topGroup);
      const center = new THREE.Vector3();
      const size = new THREE.Vector3();
      box.getCenter(center);
      box.getSize(size);

      const wrapper = new THREE.Group();
      topGroup.position.set(-center.x, -center.y, -center.z);
      wrapper.add(topGroup);

      // TOP_BUN_DEF のサイズ（半径0.64、高さ0.28）に美しく合わせるスケール
      const sx = (TOP_BUN_DEF.radius * 2) / Math.max(0.1, size.x);
      const sy = TOP_BUN_DEF.height / Math.max(0.1, size.y);
      const sz = (TOP_BUN_DEF.radius * 2) / Math.max(0.1, size.z);
      wrapper.scale.set(sx, sy, sz);

      loadedGLBModels[TOP_BUN_DEF.id] = wrapper;
      updateCatalogThumbnailForId(TOP_BUN_DEF.id);
    }
  }, undefined, (err) => console.warn('Base bun GLB fallback:', err));
}

// 純くんの読み込み（独立小台の上面にピッタリ接地、木箱パーツ完全非表示、全身ダイナミック可動）
function loadJunKun() {
  gltfLoader.load(`${MODELS_BASE}jun_kun_carry_box.glb`, (gltf) => {
    junKun = gltf.scene;
    window.junKun = junKun;
    junKun.rotation.set(0, 0.55, 0); // お皿とタワーを見つめる角度
    const scale = 0.48; // 存在感たっぷりで元気な動きがはっきり見えるサイズ！
    junKun.scale.set(scale, scale, scale);
    
    // 足裏（実測 Y=0.0）をスツール上面（Y=0.30）にピッタリ合わせる！
    junKun.position.set(-0.62, junKunBaseY, 1.22);

    junKun.traverse((child) => {
      if (child.name === 'Body') junBodyNode = child;
      if (child.name === 'Leg_L') junLegL = child;
      if (child.name === 'Leg_R') junLegR = child;

      // 木箱および箱の中のテキスト・円柱パーツを非表示化（※純くんのオレンジ色の食パン頭『パン』は残す！）
      const n = child.name || '';
      if (
        n.includes('Bread') ||
        n.includes('Box') ||
        n.includes('Basket') ||
        n.includes('立方体') ||
        n.includes('テキスト') ||
        n.includes('円柱')
      ) {
        child.visible = false;
      }

      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });

    scene.add(junKun);

    // アニメーションミキサー
    junKunMixer = new THREE.AnimationMixer(junKun);
    gltf.animations.forEach((clip) => {
      junKunAnimations[clip.name] = junKunMixer.clipAction(clip);
    });

    // 初期ポーズ: 手を振って元気にスタンバイ
    playJunKunAnimation(junKunAnimations['Wave'] ? 'Wave' : 'Carry_Idle', 0.2);
  }, undefined, (err) => console.warn('Jun-kun load error:', err));
}

// 純くんのアニメーション再生（毎回reset()してルート移動累積・T字を完全防止）
function playJunKunAnimation(name, fadeDuration = 0.15, loop = true) {
  if (!junKunMixer || !junKunAnimations[name]) return;
  const newAction = junKunAnimations[name];

  if (junKunCurrentAction && junKunCurrentAction !== newAction) {
    junKunCurrentAction.fadeOut(fadeDuration);
  }
  newAction.reset(); // ★必ずリセット！
  newAction.fadeIn(fadeDuration);
  if (!loop) {
    newAction.setLoop(THREE.LoopOnce);
    newAction.clampWhenFinished = true;
  } else {
    newAction.setLoop(THREE.LoopRepeat);
  }
  newAction.play();
  junKunCurrentAction = newAction;
}

// 純くんのリアクション（跳ね＋360度ハッピースピン＋モーション）
function triggerJunReaction(type, combo = 0) {
  if (!junKun) return;

  if (type === 'success') {
    playJunKunAnimation('Wave', 0.15, true);
    junHopTime = 0.48; // 元気にピョンと跳ねる！
    setTimeout(() => {
      if (isPlaying && !isDropping && junKunCurrentAction === junKunAnimations['Wave']) {
        playJunKunAnimation('Carry_Idle', 0.25);
      }
    }, 1200);
  } else if (type === 'big_success') {
    playJunKunAnimation('Wave', 0.10, true);
    junHopTime = 0.78; // 大ジャンプ！
    junSpinTime = 0.68; // くるっと360度ハッピースピン！
    setTimeout(() => {
      if (isPlaying && !isDropping && junKunCurrentAction === junKunAnimations['Wave']) {
        playJunKunAnimation('Carry_Idle', 0.25);
      }
    }, 1600);
  } else if (type === 'fail') {
    playJunKunAnimation('Bow', 0.15, false); // 心配・お辞儀
    setTimeout(() => {
      if (isPlaying && junKunCurrentAction === junKunAnimations['Bow']) {
        playJunKunAnimation('Carry_Idle', 0.25);
      }
    }, 1100);
  } else {
    playJunKunAnimation('Carry_Idle', 0.20);
  }
}

// テーブルとお皿
function createTableAndPlate() {
  // テーブル天板（Three.js）
  const tableGeo = new THREE.CylinderGeometry(2.4, 2.4, 0.2, 32);
  const tableMat = new THREE.MeshStandardMaterial({ color: 0xD7CCC8, roughness: 0.6 });
  const tableMesh = new THREE.Mesh(tableGeo, tableMat);
  tableMesh.position.set(0, -0.1, 0);
  tableMesh.receiveShadow = true;
  scene.add(tableMesh);

  // お皿（Three.js）- まぶしい真っ白を抑えた清潔な陶器調オフホワイト
  const plateGeo = new THREE.CylinderGeometry(1.35, 1.1, 0.14, 32);
  const plateMat = new THREE.MeshStandardMaterial({ color: 0xF5F0EA, roughness: 0.45, metalness: 0.05 });
  const plateMesh = new THREE.Mesh(plateGeo, plateMat);
  plateMesh.position.set(0, basePlateY - 0.07, 0);
  plateMesh.receiveShadow = true;
  scene.add(plateMesh);

  // ★お皿の物理ボディ (Static) - CANNON.CylinderのZ軸向きをY軸垂直に補正！
  const plateShape = new CANNON.Cylinder(1.35, 1.1, 0.14, 24);
  const qPlate = new CANNON.Quaternion();
  qPlate.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2); // 垂直円柱化！

  plateBody = new CANNON.Body({ mass: 0 });
  plateBody.addShape(plateShape, new CANNON.Vec3(0, 0, 0), qPlate);
  plateBody.position.set(0, basePlateY - 0.07, 0);
  plateBody.material = new CANNON.Material({ friction: 0.98, restitution: 0.0 });
  world.addBody(plateBody);

  // お皿の上の「土台パン（底のパンケーキ/バンズ）」
  createBaseBun();
}

// 土台パン
function createBaseBun() {
  // 土台パン（バンズ）- 白飛びしないこんがり美味しそうなキツネ色
  const radius = 0.68;
  const height = 0.24;
  const bunGeo = new THREE.CylinderGeometry(radius, radius * 0.95, height, 28);
  const bunMat = new THREE.MeshStandardMaterial({ color: 0xC87834, roughness: 0.70 });
  const bunMesh = new THREE.Mesh(bunGeo, bunMat);
  bunMesh.position.set(0, basePlateY + height / 2, 0);
  bunMesh.castShadow = true;
  bunMesh.receiveShadow = true;
  baseBunMesh = bunMesh;
  scene.add(baseBunMesh);

  // ★リアルなGLBバンズの非同期読み込み（読み込み完了後に差し替え）
  loadBaseBunGLB();

  // ★土台パンの物理ボディ (Static) - CANNON.CylinderのZ軸向きをY軸垂直に補正！
  const bunShape = new CANNON.Cylinder(radius, radius * 0.95, height, 20);
  const qBun = new CANNON.Quaternion();
  qBun.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);

  baseBunBody = new CANNON.Body({ mass: 0 });
  baseBunBody.addShape(bunShape, new CANNON.Vec3(0, 0, 0), qBun);
  baseBunBody.position.set(0, basePlateY + height / 2, 0);
  baseBunBody.material = new CANNON.Material({ friction: 0.98, restitution: 0.0 });
  world.addBody(baseBunBody);

  // 土台パン上面のY座標
  highestY = basePlateY + height; // 0.4 + 0.24 = 0.64
}

// 保持具材の上面(Box3.max.y)からトング先端下面(Y≈0.04)までの隙間を0.02に保つ配置Y計算 (先端が具材をつかむ見た目)
function getTongVisualPlacementY(currentTopY, def) {
  const itemHoldY = currentTopY + TONG_HEIGHT_OFFSET; // 物理投下高さ (currentTopY + 0.95)
  const itemHalfH = def ? (def.height * 0.5) : 0.08;
  const targetGap = 0.02; // 具材上面〜トング先端下面の視覚的隙間 (先端が具材をつかむ見た目)
  const tipLocalY = 0.04; // bakery_tongs.glbの先端下面ローカルY (約0.04)
  // 計算: tongBaseY + tipLocalY - (itemHoldY + itemHalfH) = targetGap
  return itemHoldY + itemHalfH + targetGap - tipLocalY;
}

// トングの3Dモデル（GLBモデル優先読み込み & プロシージャルArm_L/Arm_R開閉フォールバック）
function createTongModel() {
  tongMeshGroup = new THREE.Group();
  scene.add(tongMeshGroup);

  // 1. プロシージャルフォールバックを初期構築（先端下面Y=0、上端Y=1.3、Arm_L/R開閉対応）
  buildProceduralTongs();

  // 2. Blender制作GLBモデル (models/bakery_tongs.glb) のロード
  gltfLoader.load(`${MODELS_BASE}bakery_tongs.glb`, (gltf) => {
    console.log('Bakery tongs GLB loaded successfully!');
    // 既存のプロシージャルメッシュをクリア
    while (tongMeshGroup.children.length > 0) {
      tongMeshGroup.remove(tongMeshGroup.children[0]);
    }

    const rawScene = gltf.scene;
    // ★勝手に中心揃えせず、先端基準(Y≈0.04)をそのまま活かして配置！

    const pivotY = 1.19; // 左右腕ピボット高さ
    const armPivotL = new THREE.Group();
    armPivotL.name = 'Arm_L';
    armPivotL.position.set(0, pivotY, 0);

    const armPivotR = new THREE.Group();
    armPivotR.name = 'Arm_R';
    armPivotR.position.set(0, pivotY, 0);

    const centerGroup = new THREE.Group();
    centerGroup.name = 'Center_Hinge';

    const children = [...rawScene.children];
    children.forEach(child => {
      child.traverse(c => {
        if (c.isMesh) {
          c.castShadow = true;
          c.receiveShadow = true;
          // ★Codex作成のオリジナル3色（オレンジ持ち手・黒滑り止め・銀色金属）を100%完全保持！
          // 色やmetalnessは全素材で置き換えない。金属だけenvMapIntensityを適度に上げて銀色に見せる！
          if (c.material) {
            const matName = (c.material.name || '').toLowerCase();
            const isMetal = (c.material.metalness > 0.5) || matName.includes('steel') || matName.includes('polish');
            if (isMetal) {
              if (studioEnvMap) c.material.envMap = studioEnvMap; // ★金属材質だけに直接割り当て！
              c.material.envMapIntensity = 1.45; // 金属パーツにだけ環境反射を効かせて銀色に輝かせる
            } else {
              c.material.envMap = null;
              c.material.envMapIntensity = 0.0; // オレンジや黒、他の素材は反射させない
            }
            c.material.needsUpdate = true;
          }
        }
      });

      const name = child.name;
      if (name.includes('_L') || name.includes('.L') || name.includes('Arm_L') || name.includes('Jaw_L')) {
        child.position.y -= pivotY;
        armPivotL.add(child);
      } else if (name.includes('_R') || name.includes('.R') || name.includes('Arm_R') || name.includes('Jaw_R')) {
        child.position.y -= pivotY;
        armPivotR.add(child);
      } else {
        centerGroup.add(child);
      }
    });

    tongArmL = armPivotL;
    tongArmR = armPivotR;

    tongMeshGroup.add(centerGroup);
    tongMeshGroup.add(armPivotL);
    tongMeshGroup.add(armPivotR);

    isGLBTongsLoaded = true;
  }, undefined, (err) => {
    console.log('bakery_tongs.glb load fallback:', err);
  });
}

// プロシージャルなベーカリートング（先端下面Y=0、上端Y=1.30、Arm_L/Rピボット開閉完全対応）
function buildProceduralTongs() {
  const metalMat = new THREE.MeshStandardMaterial({
    color: 0xCFD8DC,
    metalness: 0.70,
    roughness: 0.30,
    envMap: studioEnvMap,
    envMapIntensity: 1.30
  });

  // 上部持ち手（アーチ）: Y=1.22
  const topGeo = new THREE.CylinderGeometry(0.038, 0.038, 0.40, 16);
  const topArch = new THREE.Mesh(topGeo, metalMat);
  topArch.position.set(0, 1.25, 0);
  topArch.rotation.z = Math.PI / 2;
  topArch.castShadow = true;
  tongMeshGroup.add(topArch);

  // ピボット付 左アーム (Arm_L)
  tongArmL = new THREE.Group();
  tongArmL.name = 'Arm_L';
  tongArmL.position.set(-0.16, 1.22, 0); // 上部回転軸

  const armGeoL = new THREE.CylinderGeometry(0.028, 0.032, 1.22, 12);
  const armMeshL = new THREE.Mesh(armGeoL, metalMat);
  armMeshL.position.set(-0.10, -0.58, 0);
  armMeshL.rotation.z = -0.14;
  armMeshL.castShadow = true;
  tongArmL.add(armMeshL);

  // 先端グリップ (Y=0 付近)
  const tipGeoL = new THREE.BoxGeometry(0.12, 0.06, 0.22);
  const tipMeshL = new THREE.Mesh(tipGeoL, metalMat);
  tipMeshL.position.set(-0.06, -1.18, 0);
  tipMeshL.castShadow = true;
  tongArmL.add(tipMeshL);

  tongMeshGroup.add(tongArmL);

  // ピボット付 右アーム (Arm_R)
  tongArmR = new THREE.Group();
  tongArmR.name = 'Arm_R';
  tongArmR.position.set(0.16, 1.22, 0); // 上部回転軸

  const armGeoR = new THREE.CylinderGeometry(0.028, 0.032, 1.22, 12);
  const armMeshR = new THREE.Mesh(armGeoR, metalMat);
  armMeshR.position.set(0.10, -0.58, 0);
  armMeshR.rotation.z = 0.14;
  armMeshR.castShadow = true;
  tongArmR.add(armMeshR);

  // 先端グリップ (Y=0 付近)
  const tipGeoR = new THREE.BoxGeometry(0.12, 0.06, 0.22);
  const tipMeshR = new THREE.Mesh(tipGeoR, metalMat);
  tipMeshR.position.set(0.06, -1.18, 0);
  tipMeshR.castShadow = true;
  tongArmR.add(tipMeshR);

  tongMeshGroup.add(tongArmR);
}

// トングの開閉アニメーション更新（投下時にパカッと大きく開き、装填時は外側からキュッと挟み込む！）
function updateTongAnimation(delta) {
  currentTongOpen += (targetTongOpen - currentTongOpen) * Math.min(1.0, delta * 12.0);
  tongRecoilY *= Math.max(0.0, 1.0 - delta * 8.0); // 投下時の軽快な跳ね上がり減衰
  const openAngle = 0.42; // しっかりパカッと開くのが一目でわかる角度（約24度）
  if (tongArmL) {
    tongArmL.rotation.z = -currentTongOpen * openAngle;
  }
  if (tongArmR) {
    tongArmR.rotation.z = currentTongOpen * openAngle;
  }
}

// 具材の3Dメッシュ生成（GLBキャッシュ優先、レア具材ゴールド化・上バンズ対応）
function createIngredientMesh(def) {
  if (loadedGLBModels[def.id]) {
    const cloned = loadedGLBModels[def.id].clone(true);
    // 金の特大パティ: 焼き目のディテールがくっきり見えつつキラキラ輝く24Kゴールドマテリアルを適用！
    if (def.id === 'item_golden_patty') {
      cloned.scale.set(1.16, 1.10, 1.16);
      cloned.traverse(c => {
        if (c.isMesh) {
          const isGrillMark = (c.material && c.material.color && c.material.color.r < 0.25);
          c.material = new THREE.MeshStandardMaterial({
            color: isGrillMark ? 0xB87300 : 0xFFD52E,
            metalness: 0.68,
            roughness: 0.26,
            emissive: isGrillMark ? 0x3A2000 : 0x5A3A00,
            emissiveIntensity: 0.22,
            envMap: studioEnvMap,
            envMapIntensity: 1.4
          });
        }
      });
    } else if (def.id === 'item_mega_sausage') {
      cloned.scale.set(1.14, 1.55, 1.25);
      cloned.traverse(c => {
        if (c.isMesh) {
          const isStripe = (c.material && c.material.color && c.material.color.r > 0.75);
          c.material = new THREE.MeshStandardMaterial({
            color: isStripe ? 0xE57373 : 0xB71C1C,
            roughness: 0.28,
            metalness: 0.12
          });
        }
      });
    }
    return cloned;
  }

  // プロシージャルフォールバック（上バンズはドーム型＋白ゴマ付きで可愛く生成）
  if (def.isTopBun) {
    const group = new THREE.Group();
    const bunGeo = new THREE.CylinderGeometry(def.radius * 0.88, def.radius, def.height, 28);
    const bunMat = new THREE.MeshStandardMaterial({ color: 0xD28238, roughness: 0.55 });
    const bunMesh = new THREE.Mesh(bunGeo, bunMat);
    bunMesh.castShadow = true;
    bunMesh.receiveShadow = true;
    group.add(bunMesh);

    const seedGeo = new THREE.SphereGeometry(0.035, 8, 8);
    seedGeo.scale(1.0, 0.45, 1.6);
    const seedMat = new THREE.MeshStandardMaterial({ color: 0xFFF8E1, roughness: 0.4 });
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const s = new THREE.Mesh(seedGeo, seedMat);
      s.position.set(Math.cos(angle) * 0.32, def.height * 0.5, Math.sin(angle) * 0.32);
      s.rotation.y = angle;
      group.add(s);
    }
    return group;
  }

  let geo;
  if (def.type === 'cylinder') {
    geo = new THREE.CylinderGeometry(def.radius, def.radius, def.height, 28);
  } else if (def.type === 'box') {
    geo = new THREE.BoxGeometry(def.width, def.height, def.depth);
  }

  const mat = new THREE.MeshStandardMaterial({
    color: def.color,
    roughness: def.isRare ? 0.22 : 0.42,
    metalness: def.id === 'item_golden_patty' ? 0.75 : 0.05,
    envMap: def.id === 'item_golden_patty' ? studioEnvMap : null,
    envMapIntensity: def.id === 'item_golden_patty' ? 1.5 : 0.0
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

// 段階的な具材抽選（レア具材サプライズ出現＆レシピコンボが狙いやすいバランス）
function pickNextIngredient() {
  const normalDefs = INGREDIENTS_DEF.filter(d => !d.isRare);
  const rareDefs = INGREDIENTS_DEF.filter(d => d.isRare);

  // 2段目以降、約18%の確率でワクワクする「レア具材」がサプライズ出現！
  if (stackedCount >= 2 && rareDefs.length > 0 && Math.random() < 0.18) {
    return rareDefs[Math.floor(Math.random() * rareDefs.length)];
  }

  // 序盤3段: 安定感が高くレシピコンボ（チーズバーガー・月見）に繋がりやすい具材中心
  if (stackedCount < 3) {
    const easyPool = normalDefs.filter(d => ['item_patty', 'item_cheese', 'item_pancake', 'item_fried_egg'].includes(d.id));
    return easyPool[Math.floor(Math.random() * easyPool.length)];
  }
  // 4〜6段: BLTや野菜系も加わる
  if (stackedCount < 6) {
    const midPool = normalDefs.filter(d => ['item_patty', 'item_cheese', 'item_bacon', 'item_lettuce', 'item_tomato', 'item_fried_egg', 'item_pancake'].includes(d.id));
    return midPool[Math.floor(Math.random() * midPool.length)];
  }
  return normalDefs[Math.floor(Math.random() * normalDefs.length)];
}

// 手動操作イベントのバインド（左右スイング ➔ 画面タップ・ボタン・Spaceで投下＆上バンズ完成ボタン！）
function bindManualControlEvents() {
  const container = document.getElementById('game-container');
  const dropBtn = document.getElementById('drop-btn');
  const finishBunBtn = document.getElementById('finish-bun-btn');

  // 1. 「🍔 具材を落とす！」ボタン
  if (dropBtn) {
    dropBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sounds.init();
      if (isPlaying && !isDropping && performance.now() - gameStartTime >= 450) {
        dropCurrentItem();
      }
    });
  }

  // 2. 「👑 完成させる！(×2)（上バンズ装填）」ボタン
  if (finishBunBtn) {
    finishBunBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sounds.init();
      const landedCount = activeItems.filter(it => !it.isFallen && it.hasTouchedBelow).length;
      if (isPlaying && !isDropping && (stackedCount >= 1 || landedCount >= 1)) {
        triggerFinishTopBun();
      }
    });
  }

  // 3. 画面タップで即座に投下！（狙った瞬間に遅延ゼロでポンッと落とせる）
  container.addEventListener('pointerdown', (e) => {
    if (e.target.closest('button') || e.target.closest('a') || e.target.closest('.modal-card')) return;
    if (performance.now() - gameStartTime < 450) return; // スタート直後のタップ抜けガード

    sounds.init();
    if (isPlaying && !isDropping) {
      dropCurrentItem();
    }
  });

  // 4. PCキーボード操作（Space/Enter/Downで投下）
  window.addEventListener('keydown', (e) => {
    if (!isPlaying) return;
    if (e.code === 'Space' || e.code === 'Enter' || e.code === 'ArrowDown') {
      e.preventDefault();
      if (!isDropping && performance.now() - gameStartTime >= 450) {
        dropCurrentItem();
      }
    }
  });
}

// 「👑 完成させる！(×2)」ボタンでトングの具材を『特製上バンズ』に切り替えるギミック
function triggerFinishTopBun() {
  const landedCount = activeItems.filter(it => !it.isFallen && it.hasTouchedBelow).length;
  if (!isPlaying || isDropping || (stackedCount < 1 && landedCount < 1)) return;
  if (currentHeldDef && currentHeldDef.isTopBun) {
    // すでに上バンズを持っている状態で押されたらそのまま投下！
    dropCurrentItem();
    return;
  }

  sounds.playRareAppear();
  currentHeldDef = TOP_BUN_DEF;

  if (currentHeldMesh) {
    scene.remove(currentHeldMesh);
  }
  currentHeldMesh = createIngredientMesh(currentHeldDef);
  scene.add(currentHeldMesh);

  // トングが外側からパッと開いて上バンズをキュッと掴み直す演出！
  currentTongOpen = 1.0;
  targetTongOpen = 0.0;

  showToast('👑 仕上げの特製上バンズ！乗せて完成するとスコア2倍(×2)！', 'good');
  triggerJunReaction('big_success');

  const finishBtn = document.getElementById('finish-bun-btn');
  if (finishBtn) {
    finishBtn.innerText = '👑 バンズ投下！(×2)';
  }
}

// 上バンズ完成ボタンの状態更新
function updateFinishBunButtonUI() {
  const finishBtn = document.getElementById('finish-bun-btn');
  if (!finishBtn) return;
  const landedCount = activeItems.filter(it => !it.isFallen && it.hasTouchedBelow).length;
  if ((stackedCount >= 1 || landedCount >= 1) && isPlaying) {
    finishBtn.disabled = false;
    if (currentHeldDef && currentHeldDef.isTopBun) {
      finishBtn.innerText = '👑 バンズ投下！(×2)';
      finishBtn.classList.add('ready-glow');
    } else {
      finishBtn.innerText = '👑 完成させる！(×2)';
      if (stackedCount >= 5 || landedCount >= 5) {
        finishBtn.classList.add('ready-glow');
      } else {
        finishBtn.classList.remove('ready-glow');
      }
    }
  } else {
    finishBtn.disabled = true;
    finishBtn.innerText = '👑 完成させる！(×2)';
    finishBtn.classList.remove('ready-glow');
  }
}

// トングで掴んでいる具材の準備（装填時に外側からキュッと掴むアニメーション付き）
function prepareNextItem() {
  if (!isPlaying) return;

  currentHeldDef = nextItemDef || pickNextIngredient();
  nextItemDef = pickNextIngredient();

  // NEXT UI の更新 & レア具材予告のゴールド発光
  const nextEl = document.getElementById('next-item-name');
  const nextCard = nextEl ? nextEl.closest('.next-card') : null;
  if (nextEl) nextEl.innerText = nextItemDef.name;
  if (nextCard) {
    if (nextItemDef.isRare) {
      nextCard.classList.add('rare-glow');
    } else {
      nextCard.classList.remove('rare-glow');
    }
  }

  // 今トングに装填された具材がレア具材ならサプライズ音＆トースト通知！
  if (currentHeldDef.isRare) {
    sounds.playRareAppear();
    showToast(`✨ レア具材「${currentHeldDef.name}」出現！(+¥${currentHeldDef.bonusScore.toLocaleString()})`, 'good');
    triggerJunReaction('big_success');
  }

  if (currentHeldMesh) {
    scene.remove(currentHeldMesh);
  }
  currentHeldMesh = createIngredientMesh(currentHeldDef);
  scene.add(currentHeldMesh);
  isDropping = false;
  currentDroppingItem = null; // 装填完了したので投下中ロックを解除

  // ★トングが開いた状態(0.95)から新しい具材を外側からキュッと挟み込む(0.0)ことで開閉動作が常にくっきり見える！
  currentTongOpen = 0.95;
  targetTongOpen = 0.0;

  updateFinishBunButtonUI();
}

// 具材の投下（落下中は二重投下防止・スタート直後のタップ抜け防止）
function dropCurrentItem() {
  if (!currentHeldMesh || !currentHeldDef || isDropping || currentDroppingItem || !isPlaying) return;
  if (performance.now() - gameStartTime < 450) return;

  isDropping = true;
  currentTongOpen = 1.0; // ★投下した瞬間に即座にパカッと大きく開く！
  targetTongOpen = 1.0;
  tongRecoilY = 0.14; // トングがキュッと上に跳ね上がるリコイル演出
  sounds.playDrop();

  const def = currentHeldDef;

  // ★安全スポーン高度の絶対保証
  const baseTopY = basePlateY + 0.24;
  let highestActiveY = baseTopY;
  activeItems.forEach(it => {
    if (!it.isFallen) {
      const topY = it.body.position.y + it.def.height * 0.5;
      if (topY > highestActiveY) highestActiveY = topY;
    }
  });
  const safeBaseY = Math.max(highestY, highestActiveY);
  const spawnY = safeBaseY + TONG_HEIGHT_OFFSET;
  const spawnX = window.tongX;

  // ★Cannon 剛体の生成 - 円柱はクォータニオンで必ずY軸垂直に補正！
  let shape;
  let qShape = null;

  if (def.type === 'cylinder') {
    shape = new CANNON.Cylinder(def.radius, def.radius, def.height, 24);
    qShape = new CANNON.Quaternion();
    qShape.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2); // 垂直円柱化！
  } else if (def.type === 'box') {
    shape = new CANNON.Box(new CANNON.Vec3(def.width / 2, def.height / 2, def.depth / 2));
  }

  // パンケーキタワー仕様: 働くのは重力だけ！反発ゼロ・高摩擦で真下にストンと落ちる
  const mat = new CANNON.Material({ friction: 0.98, restitution: 0.0 });
  const body = new CANNON.Body({
    mass: def.mass,
    material: mat,
    position: new CANNON.Vec3(spawnX, spawnY, 0),
    linearDamping: 0.40,
    angularDamping: 0.60
  });

  // 2.5D物理化（奥行きZを完全ロックし、正面からのバランスのみに集中）
  body.angularFactor = new CANNON.Vec3(0, 0, 1);
  body.linearFactor = new CANNON.Vec3(1, 1, 0.0);

  if (qShape) {
    body.addShape(shape, new CANNON.Vec3(0, 0, 0), qShape);
  } else {
    body.addShape(shape);
  }

  body.velocity.set(0, 0, 0);
  body.angularVelocity.set(0, 0, 0);

  world.addBody(body);

  const droppedMesh = currentHeldMesh;
  currentHeldMesh = null;

  const newItem = {
    def: def,
    mesh: droppedMesh,
    body: body,
    baseScale: droppedMesh.scale.clone(),
    squashTime: 0,
    timeSinceDrop: 0,
    timeSinceTouch: 0,
    settledTime: 0,
    stoppedTimer: 0,
    lostSupportTime: 0,
    hasTouchedBelow: false, // ★下の具材・土台パン・お皿に触れたかどうかのフラグ
    everScored: false,
    hasDeductedLife: false,
    hasPlayedLand: false,
    isFallen: false,
    inTower: false
  };
  activeItems.push(newItem);
  currentDroppingItem = newItem; // ★この具材が着地または落下するまで次の具材を出さない！

  // 着地・接触イベント: 下の具材や土台・お皿に触れた瞬間に着地音＆ぷるん弾力＆接触フラグON！
  body.addEventListener('collide', () => {
    newItem.hasTouchedBelow = true;
    if (!newItem.hasPlayedLand && newItem.timeSinceDrop > 0.05) {
      newItem.hasPlayedLand = true;
      newItem.squashTime = 0.26; // 着地時のぷるんとした弾力（Squash & Stretch）開始！
      sounds.playLand(stackedCount);
    }
  });
}

// ★3Dジューシー＆キラキラ星パーティクル演出（PERFECT時・レシピ完成時・バーガー完成時に弾け飛ぶ！）
function spawnJuicyParticles(pos, colorHex = 0xFFD700, count = 14) {
  const starGeo = new THREE.OctahedronGeometry(0.055, 0);
  const dropGeo = new THREE.SphereGeometry(0.042, 8, 8);

  for (let i = 0; i < count; i++) {
    const isStar = (i % 2 === 0);
    const mat = new THREE.MeshStandardMaterial({
      color: isStar ? 0xFFD700 : colorHex,
      emissive: isStar ? 0xFFA000 : colorHex,
      emissiveIntensity: 0.55,
      roughness: 0.2,
      metalness: 0.3
    });
    const pMesh = new THREE.Mesh(isStar ? starGeo : dropGeo, mat);
    pMesh.position.set(
      pos.x + (Math.random() - 0.5) * 0.5,
      pos.y + 0.05,
      pos.z + (Math.random() - 0.5) * 0.4
    );

    const angle = (i / count) * Math.PI * 2 + Math.random() * 0.4;
    const speedH = 1.1 + Math.random() * 1.4;
    const vel = new THREE.Vector3(
      Math.cos(angle) * speedH,
      1.8 + Math.random() * 1.8,
      Math.sin(angle) * speedH * 0.6
    );

    scene.add(pMesh);
    activeParticles.push({
      mesh: pMesh,
      vel: vel,
      life: 0.75 + Math.random() * 0.30,
      maxLife: 1.0
    });
  }
}

// パーティクルの毎フレーム更新
function updateParticles(delta) {
  for (let i = activeParticles.length - 1; i >= 0; i--) {
    const p = activeParticles[i];
    p.life -= delta;
    if (p.life <= 0) {
      scene.remove(p.mesh);
      if (p.mesh.material) p.mesh.material.dispose();
      activeParticles.splice(i, 1);
      continue;
    }
    p.vel.y -= 5.8 * delta; // 重力でふわっと弧を描く
    p.mesh.position.addScaledVector(p.vel, delta);
    p.mesh.rotation.x += delta * 6.0;
    p.mesh.rotation.y += delta * 8.0;
    const s = Math.max(0.01, p.life / p.maxLife);
    p.mesh.scale.set(s, s, s);
  }
}

// ★特定レシピのコンボボーナス（隠しオーダー）判定
function checkRecipeCombo(validTower) {
  if (validTower.length < 2) return;
  const top1 = validTower[validTower.length - 1].def.id;
  const top2 = validTower[validTower.length - 2].def.id;
  const top3 = validTower.length >= 3 ? validTower[validTower.length - 3].def.id : null;

  const isPatty = (id) => id === 'item_patty' || id === 'item_golden_patty';
  let recipeName = null;
  let recipeBonus = 0;

  // 3段コンボ判定
  if (top3) {
    const set3 = new Set([top1, top2, top3]);
    if (set3.has('item_bacon') && set3.has('item_lettuce') && set3.has('item_tomato')) {
      recipeName = '🥓🥬🍅 クラシックBLTサンド完成！';
      recipeBonus = 2500;
    } else if (isPatty(top1) && top2 === 'item_cheese' && isPatty(top3)) {
      recipeName = '🍔🧀 ダブルチーズバーガー完成！';
      recipeBonus = 3000;
    }
  }

  // 2段コンボ判定（3段コンボが発火していない場合）
  if (!recipeName) {
    if ((isPatty(top1) && top2 === 'item_cheese') || (top1 === 'item_cheese' && isPatty(top2))) {
      recipeName = '🧀 絶品チーズバーガー！';
      recipeBonus = 1000;
    } else if ((isPatty(top1) && top2 === 'item_fried_egg') || (top1 === 'item_fried_egg' && isPatty(top2))) {
      recipeName = '🍳 とろ〜り月見バーガー！';
      recipeBonus = 1200;
    } else if (isPatty(top1) && isPatty(top2)) {
      recipeName = '🥩 肉汁ダブルパティ！';
      recipeBonus = 1500;
    } else if ((top1 === 'item_pancake' && top2 === 'item_fried_egg') || (top1 === 'item_fried_egg' && top2 === 'item_pancake')) {
      recipeName = '🥞 モーニングパンケーキ！';
      recipeBonus = 1200;
    }
  }

  if (recipeName && recipeBonus > 0) {
    totalScore += recipeBonus;
    sounds.playRecipeCombo();
    const topItem = validTower[validTower.length - 1];
    spawnJuicyParticles(topItem.body.position, 0xFF8F00, 18);

    const recipePopup = document.getElementById('recipe-popup');
    if (recipePopup) {
      recipePopup.innerText = `🍽️ ${recipeName} (+¥${recipeBonus.toLocaleString()})`;
      recipePopup.classList.add('show');
      setTimeout(() => {
        recipePopup.classList.remove('show');
      }, 1800);
    }
  }
}

// ★有効な積み重なり（Valid Tower Stack）の毎フレーム再構築
function rebuildValidTower(delta) {
  const baseTopY = basePlateY + 0.24; // 0.64 (土台パン上面)

  // 1. 各アクティブ具材の物理状態チェック & 落下・停止判定
  activeItems.forEach(item => {
    item.timeSinceDrop += delta;
    if (item.hasTouchedBelow) {
      item.timeSinceTouch = (item.timeSinceTouch || 0) + delta;
    }

    const up = new THREE.Vector3(0, 1, 0).applyQuaternion(item.mesh.quaternion);
    item.upY = up.y;
    // タワーが斜めになっても着地判定が途切れないよう、傾き約40度以内(up.y >= 0.75)を水平と認定
    item.isNearHorizontal = up.y >= 0.75;

    const linVel = item.body.velocity.length();
    const angVel = item.body.angularVelocity.length();
    item.isSettled = (linVel < 0.35 && angVel < 0.45);

    if (item.isSettled && item.isNearHorizontal) {
      item.settledTime = (item.settledTime || 0) + delta;
    } else {
      item.settledTime = 0;
    }

    // 接触後に静止しているかの追跡（斜め着地やお皿上での停止判定用）
    const isStationary = (linVel < 0.25 && angVel < 0.35);
    if (item.hasTouchedBelow && isStationary && item.timeSinceDrop >= 0.25) {
      item.stoppedTimer = (item.stoppedTimer || 0) + delta;
    } else {
      item.stoppedTimer = 0;
    }

    const distSq = item.body.position.x * item.body.position.x + item.body.position.z * item.body.position.z;
    const fellBelow = item.body.position.y < (basePlateY - 0.12) || (item.body.position.y < basePlateY && distSq > 1.8);

    if (!item.hasDeductedLife && fellBelow) {
      item.hasDeductedLife = true;
      item.isFallen = true;
      sounds.playFall();
      onItemFall(item);
    }
  });

  // 2. 土台パンから上へ、有効な積み重なりチェーンを再構築
  const validTower = [];
  const visited = new Set();
  let currentTop = {
    body: baseBunBody,
    height: 0.24,
    radius: 0.68,
    topY: baseTopY,
    posX: 0,
    posZ: 0
  };

  const candidates = activeItems.filter(item => 
    !item.isFallen && 
    item.timeSinceDrop >= 0.15 && 
    (item.settledTime || 0) >= 0.15
  );

  let stackFound = true;
  while (stackFound) {
    stackFound = false;
    let bestCandidate = null;
    let minOffset = Infinity;

    for (let i = 0; i < candidates.length; i++) {
      const cand = candidates[i];
      if (visited.has(cand)) continue;

      const parentCenterY = (currentTop.body === baseBunBody) ? (basePlateY + 0.12) : currentTop.body.position.y;
      const yDiff = cand.body.position.y - parentCenterY;
      const minExpectedYDiff = (currentTop.height * 0.30 + cand.def.height * 0.30);
      if (yDiff < minExpectedYDiff) continue;

      const dx = cand.body.position.x - currentTop.posX;
      const dz = cand.body.position.z - currentTop.posZ;
      const hDist = Math.sqrt(dx * dx + dz * dz);
      if (hDist > 0.60) continue;

      let hasTopContact = false;
      for (let cIdx = 0; cIdx < world.contacts.length; cIdx++) {
        const c = world.contacts[cIdx];
        if (c.bi === currentTop.body && c.bj === cand.body) {
          if (c.ni.y > 0.18) { hasTopContact = true; break; }
        } else if (c.bj === currentTop.body && c.bi === cand.body) {
          if (c.ni.y < -0.18) { hasTopContact = true; break; }
        }
      }

      if (!hasTopContact && cand.everScored) {
        const expectedDistance = (currentTop.height * 0.5 + cand.def.height * 0.5);
        if (Math.abs(yDiff - expectedDistance) < 0.22 && hDist < 0.68) {
          hasTopContact = true;
        }
      }

      if (hasTopContact) {
        if (hDist < minOffset) {
          minOffset = hDist;
          bestCandidate = cand;
        }
      }
    }

    if (bestCandidate) {
      visited.add(bestCandidate);
      validTower.push(bestCandidate);
      const candTopY = bestCandidate.body.position.y + (bestCandidate.def.height * 0.5);
      currentTop = {
        body: bestCandidate.body,
        height: bestCandidate.def.height,
        radius: bestCandidate.def.radius || (bestCandidate.def.width * 0.5),
        topY: candTopY,
        posX: bestCandidate.body.position.x,
        posZ: bestCandidate.body.position.z
      };
      stackFound = true;
    }
  }

  const validSet = new Set(validTower);
  activeItems.forEach(item => {
    item.inTower = validSet.has(item);
    if (!item.inTower) {
      item.lostSupportTime = (item.lostSupportTime || 0) + delta;
    } else {
      item.lostSupportTime = 0;
    }
  });

  // ★現在投下中の具材（currentDroppingItem）の監視:
  // 下の具材・お皿に触れて落ち着くか、地面に落ちるまで、絶対に次の具材を出さない（過去の斜め具材による誤解除バグを完全根絶！）
  if (isDropping && currentDroppingItem) {
    if (currentDroppingItem.isFallen) {
      // onItemFall 側で 450ms 後に prepareNextItem() される
    } else if (
      currentDroppingItem.hasTouchedBelow &&
      ((currentDroppingItem.timeSinceTouch || 0) >= 0.42 || currentDroppingItem.stoppedTimer >= 0.35)
    ) {
      // ★もし投下中だった具材が「👑 特製上バンズ」で、お皿や具材の上に着地して落ちずに残ったら「バーガー完成！（スコア2倍）」発動！
      if (currentDroppingItem.def.isTopBun) {
        if (!currentDroppingItem.everScored) {
          currentDroppingItem.everScored = true;
          totalScore += (currentDroppingItem.def.price || 1000);
        }
        spawnJuicyParticles(currentDroppingItem.body.position, 0xFFD700, 32);
        completeSandwichTower();
        return;
      }

      // 下の具材またはお皿に触れてから約0.4秒（トングがパカッと開いて一呼吸置く気持ちいいディレイ）経過したら次を装填！
      isDropping = false;
      currentDroppingItem = null;
      if (isPlaying) {
        prepareNextItem();
      }
    } else if (currentDroppingItem.timeSinceDrop >= 5.0) {
      isDropping = false;
      currentDroppingItem = null;
      if (isPlaying) {
        prepareNextItem();
      }
    }
  }

  // 3. ★一番上にある具材の高さ（cm）と現在の純利益（¥）をリアルタイム計測・更新！
  // 「何段か」ではなく、現在お皿・タワーの上に乗っている全具材の中で「一番高い位置にある具材の上面Y」から直接高さを算出！
  let highestIngredientTopY = baseTopY;
  let landedItemCount = 0;
  activeItems.forEach(it => {
    if (!it.isFallen && it.hasTouchedBelow) {
      landedItemCount++;
      const tY = it.body.position.y + it.def.height * 0.5;
      if (tY > highestIngredientTopY) {
        highestIngredientTopY = tY;
      }
      // お皿・タワーの上に着地して安定した具材には、その具材の値段（price）を1回加算！
      if (!it.hasAddedBasePrice && ((it.timeSinceTouch || 0) >= 0.25 || it.everScored)) {
        it.hasAddedBasePrice = true;
        totalScore += (it.def.price || 300);
      }
    }
  });

  if (currentTop.topY > highestIngredientTopY) {
    highestIngredientTopY = currentTop.topY;
  }

  const currentCount = Math.max(validTower.length, landedItemCount);
  const currentHeightCm = Math.max(0, (highestIngredientTopY - baseTopY) * 10).toFixed(1);

  stackedCount = currentCount;

  // highestY も一番上の具材の高さに合わせて更新
  if (highestIngredientTopY > highestY) {
    highestY = highestIngredientTopY;
  }

  // 現在のリアルタイム純利益（具材単価＋コンボ＋レシピ＋高さボーナス）
  const liveScore = totalScore + Math.floor(parseFloat(currentHeightCm) * 100);

  const countEl = document.getElementById('count-val');
  const heightEl = document.getElementById('height-val');
  const scoreEl = document.getElementById('score-val');
  if (countEl) countEl.innerText = currentCount;
  if (heightEl) heightEl.innerText = currentHeightCm;
  if (scoreEl) scoreEl.innerText = liveScore.toLocaleString();

  updateFinishBunButtonUI();

  const prevBestHeight = parseFloat(localStorage.getItem(BEST_HEIGHT_KEY) || '0.0');
  if (parseFloat(currentHeightCm) > prevBestHeight) {
    localStorage.setItem(BEST_HEIGHT_KEY, currentHeightCm);
    displayBestRecords();
  }

  // 4. 新規スタック達成時のイベント処理
  const newlyScoredItems = validTower.filter(item => !item.everScored);
  if (newlyScoredItems.length > 0) {
    let completedWithTopBun = false;

    newlyScoredItems.forEach(item => {
      item.everScored = true;
      if (!item.hasAddedBasePrice) {
        item.hasAddedBasePrice = true;
        totalScore += (item.def.price || 300);
      }

      // レア具材演出！
      if (item.def.isRare) {
        spawnJuicyParticles(item.body.position, 0xFFD700, 20);
      }

      // ★仕上げの上バンズが乗ったら「🍔 特製サンドイッチ完成！！」大ファンファーレ！
      if (item.def.isTopBun) {
        completedWithTopBun = true;
        spawnJuicyParticles(item.body.position, 0xFFD700, 32);
        return;
      }

      const offset = Math.sqrt(item.body.position.x * item.body.position.x + item.body.position.z * item.body.position.z);
      handleCenterCombo(offset, item);

      // レシピコンボ（隠しオーダー）チェック！
      checkRecipeCombo(validTower);

      if (currentCount >= 5 || offset < 0.18 || item.def.isRare) {
        triggerJunReaction('big_success', currentCombo);
      } else {
        triggerJunReaction('success', currentCombo);
      }
    });

    if (completedWithTopBun) {
      completeSandwichTower();
      return;
    }

    // ★現在投下中の具材自身がスタック判定された場合も、トングが開いて少し止まる余韻（接触後0.32秒以上）を待ってから次を装填！
    if (isDropping && currentDroppingItem && currentDroppingItem.everScored && (currentDroppingItem.timeSinceTouch || 0) >= 0.32) {
      isDropping = false;
      currentDroppingItem = null;
      if (isPlaying) {
        prepareNextItem();
      }
    }
  }
  lastStackedCount = currentCount;

  targetCameraY = 0.95 + Math.max(0, highestY - 1.20) * 0.65;
}

// 純くんの応援吹き出し更新
function setJunCheerText(text) {
  const el = document.getElementById('jun-balloon-text');
  if (el) el.innerText = text;
}

// 中心コンボの処理（PERFECT時にキラキラ星＆ジューシー3Dエフェクトが弾け飛ぶ！）
function handleCenterCombo(offset, item) {
  const popup = document.getElementById('combo-popup');
  let text = '';
  let cls = '';

  if (offset < 0.18) {
    currentCombo++;
    if (currentCombo > maxCombo) maxCombo = currentCombo;
    const bonus = 500 * currentCombo;
    totalScore += bonus;
    text = `🌟 PERFECT!! x${currentCombo} (+¥${bonus.toLocaleString()})`;
    cls = 'combo-popup combo-perfect show';
    sounds.playPerfect();
    if (item && item.body) {
      spawnJuicyParticles(item.body.position, item.def.color || 0xFFD700, 16);
    }
  } else if (offset < 0.35) {
    currentCombo = Math.max(1, currentCombo);
    const bonus = 250;
    totalScore += bonus;
    text = `✨ GREAT! (+¥${bonus})`;
    cls = 'combo-popup combo-great show';
    if (item && item.body) {
      spawnJuicyParticles(item.body.position, item.def.color || 0xFFA000, 6);
    }
  } else {
    currentCombo = 0;
    text = `⚠️ CAUTION! (ぐらっ…)`;
    cls = 'combo-popup combo-caution show';
  }

  if (popup) {
    popup.innerText = text;
    popup.className = cls;
    setTimeout(() => {
      popup.classList.remove('show');
    }, 1100);
  }
}

// ★上バンズ着地による「🍔 特製サンドイッチ完成！！」大団円フィニッシュ（純利益2倍ボーナス！）
function completeSandwichTower() {
  isPlaying = false;
  isDropping = true;
  isGameCompletedWithBun = true;
  sounds.playFanfare();
  triggerJunReaction('big_success');
  showToast('🎊 特製サンドイッチ完成！！純利益スコアが【2倍(×2)】に！！', 'good');

  setTimeout(() => {
    endGame(true);
  }, 1100);
}

// 具材が落下したときの処理（各個1回のみライフ減少）
function onItemFall(item) {
  lives--;
  currentCombo = 0;
  updateLivesUI();
  showToast('⚠️ 具材が落下！残機 -1', 'bad');
  setJunCheerText('😢 ああっ！落ちちゃった…！');

  // 純くんが心配するリアクション
  triggerJunReaction('fail');

  // 物理ワールドとシーンから除外
  world.removeBody(item.body);
  scene.remove(item.mesh);

  if (lives <= 0) {
    endGame(false);
  } else if (isDropping && item === currentDroppingItem) {
    // 投下中だった具材自身の直接落下なら、少し余韻を置いてから次の具材を装填
    setTimeout(() => {
      if (currentDroppingItem === item) {
        isDropping = false;
        currentDroppingItem = null;
        if (isPlaying) {
          prepareNextItem();
        }
      }
    }, 450);
  }
}

// UI更新
function updateStatsUI() {
  const baseTopY = basePlateY + 0.24; // 0.64
  const heightCm = Math.max(0, (highestY - baseTopY) * 10).toFixed(1);
  const heightEl = document.getElementById('height-val');
  const countEl = document.getElementById('count-val');
  const scoreEl = document.getElementById('score-val');

  if (heightEl) heightEl.innerText = heightCm;
  if (countEl) countEl.innerText = stackedCount;
  if (scoreEl) scoreEl.innerText = totalScore.toLocaleString();
}

function updateLivesUI() {
  const livesEl = document.getElementById('lives-container');
  if (livesEl) {
    let hearts = '';
    for (let i = 0; i < 3; i++) {
      hearts += (i < lives) ? '❤️' : '💔';
    }
    livesEl.innerText = hearts;
  }
}

function showToast(text, type = 'good') {
  const toast = document.getElementById('toast-msg');
  if (!toast) return;
  toast.innerText = text;
  toast.className = type === 'good' ? 'toast-good show' : 'toast-bad show';
  setTimeout(() => {
    toast.classList.remove('show');
  }, 1400);
}

// 最高記録の表示
function displayBestRecords() {
  const bestHeight = parseFloat(localStorage.getItem(BEST_HEIGHT_KEY) || '0.0');
  const bestScore = parseInt(localStorage.getItem(BEST_SCORE_KEY) || '0', 10);

  const startBest = document.getElementById('start-best-val');
  if (startBest) startBest.innerText = `${bestHeight.toFixed(1)} cm / ¥${bestScore.toLocaleString()}`;

  const hudBest = document.getElementById('hud-best-height');
  if (hudBest) hudBest.innerText = bestHeight.toFixed(1);

  const resBest = document.getElementById('result-best-val');
  if (resBest) resBest.innerText = `${bestHeight.toFixed(1)} cm`;

  const resBestScore = document.getElementById('result-best-score-val');
  if (resBestScore) resBestScore.innerText = `¥${bestScore.toLocaleString()}`;
}

// ゲームスタート
function startGame() {
  isPlaying = true;
  isDropping = false;
  currentDroppingItem = null;
  isGameCompletedWithBun = false;
  gameStartTime = performance.now(); // スタート直後のタップ抜け防止用タイムスタンプ
  lives = 3;
  stackedCount = 0;
  lastStackedCount = 0;
  highestY = basePlateY + 0.24;
  targetCameraY = 0.95;
  currentCameraY = 0.95;
  currentCombo = 0;
  maxCombo = 0;
  totalScore = 0;
  nextItemDef = null;

  // スイング位置を中央にリセット
  tongSwingTime = 0;
  window.tongX = 0;

  // 既存具材のクリア
  activeItems.forEach(item => {
    world.removeBody(item.body);
    scene.remove(item.mesh);
  });
  activeItems = [];

  // 既存パーティクルのクリア
  activeParticles.forEach(p => scene.remove(p.mesh));
  activeParticles = [];

  updateLivesUI();
  updateStatsUI();
  updateFinishBunButtonUI();

  document.getElementById('start-modal').classList.remove('active');
  document.getElementById('result-modal').classList.remove('active');

  sounds.init();

  // 純くんを応援待機ポーズへ
  triggerJunReaction('idle');
  setJunCheerText('まっすぐ狙って落としてね！');

  prepareNextItem();
}

let lastFinalEarnedScore = 0;
let lastFinalHeightCm = 0.0;

// ゲーム終了（上バンズ完成 or 残機ゼロ営業終了）
function endGame(isCompleted = false) {
  isPlaying = false;
  isDropping = true;
  if (!isCompleted) {
    sounds.playGameOver();
  }

  if (currentHeldMesh) {
    scene.remove(currentHeldMesh);
    currentHeldMesh = null;
  }

  // ★一番上にある具材の高さ（cm）を正確に算出
  const baseTopY = basePlateY + 0.24;
  let finalTopY = baseTopY;
  let landedCount = 0;
  activeItems.forEach(it => {
    if (!it.isFallen && it.hasTouchedBelow) {
      landedCount++;
      const tY = it.body.position.y + it.def.height * 0.5;
      if (tY > finalTopY) finalTopY = tY;
    }
  });
  if (highestY > finalTopY) finalTopY = highestY;

  const heightCm = parseFloat(Math.max(0, (finalTopY - baseTopY) * 10).toFixed(1));
  const rawScore = totalScore + Math.floor(heightCm * 100);
  // ★上バンズを乗せてバーガーを完成させた場合は、獲得純利益スコアが【2倍(×2)】に！！
  const earnedScore = isCompleted ? (rawScore * 2) : rawScore;

  lastFinalEarnedScore = earnedScore;
  lastFinalHeightCm = heightCm;

  // 自己ベスト判定
  const prevBestHeight = parseFloat(localStorage.getItem(BEST_HEIGHT_KEY) || '0.0');
  const prevBestScore = parseInt(localStorage.getItem(BEST_SCORE_KEY) || '0', 10);

  if (heightCm > prevBestHeight) {
    localStorage.setItem(BEST_HEIGHT_KEY, heightCm.toFixed(1));
  }
  if (earnedScore > prevBestScore) {
    localStorage.setItem(BEST_SCORE_KEY, earnedScore.toString());
  }
  displayBestRecords();

  // モーダルヘッダー更新（完成時は2倍バッジ表示！）
  const modalBadge = document.getElementById('result-modal-badge');
  const modalTitle = document.getElementById('result-modal-title');
  const doubleBadge = document.getElementById('result-double-badge');
  if (isCompleted) {
    if (modalBadge) modalBadge.innerText = '👑 SPECIAL ORDER COMPLETE!';
    if (modalTitle) modalTitle.innerText = '🎊 特製サンドイッチ完成！！';
    if (doubleBadge) doubleBadge.style.display = 'block';
  } else {
    if (modalBadge) modalBadge.innerText = '🔔 営業終了！';
    if (modalTitle) modalTitle.innerText = '本日のサンドイッチ成果';
    if (doubleBadge) doubleBadge.style.display = 'none';
  }

  // 称号判定（高さcm基準）
  let title = isCompleted ? '👑 本日の特製サンドイッチ！' : 'お試しミニサンド';
  if (heightCm >= 50) {
    title = '🌌 宇宙に届く伝説のプクムクタワー！';
  } else if (heightCm >= 30) {
    title = isCompleted ? '👑 極上スカイツリー級メガバーガー！' : '🗼 スカイツリー級メガバーガー！';
  } else if (heightCm >= 15) {
    title = isCompleted ? '👑 特製ボリューム満点大繁盛バーガー！' : '🍔 ボリューム満点大繁盛バーガー！';
  } else if (heightCm >= 5) {
    title = isCompleted ? '👑 こんがり特製手作りバーガー！' : '🥪 なかなか見事な手作りサンド！';
  }

  // リザルト画面への反映
  document.getElementById('final-score-val').innerText = earnedScore.toLocaleString();
  document.getElementById('final-height-val').innerText = heightCm.toFixed(1);
  document.getElementById('final-count-val').innerText = `${Math.max(stackedCount, landedCount)} 個`;
  document.getElementById('final-combo-val').innerText = `${maxCombo} 連続`;
  document.getElementById('result-title-badge').innerText = title;

  // 世界ランキング登録フォーム＆ランキング一覧の準備
  prepareResultTowerRanking();

  document.getElementById('result-modal').classList.add('active');
}

// アニメーションループ
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);

  // ラグスパイクやバックグラウンド復帰時の誤タイムアウト・物理破綻を防ぐため最大0.1秒にクランプ
  const delta = Math.min(clock.getDelta(), 0.1);

  // 1. 物理演算ステップ（パンケーキタワー仕様: 働くのは重力のみ、勝手な横滑り・スライディング完全防止）
  activeItems.forEach(item => {
    if (item.isFallen) return;

    if (!item.everScored && !item.inTower) {
      // 落下中: 横風や斜め反発を完全排除し、真下に重力だけで垂直投下
      item.body.velocity.x = 0;
      item.body.velocity.z = 0;
      if (item.body.velocity.y < -1.5) {
        item.body.velocity.y = -1.5;
      }
    } else {
      // 着地後・タワー内: 勝手に横へスライドしないようX方向の微小速度を即座に減衰・ロック！
      item.body.velocity.x *= 0.5;
      item.body.velocity.z = 0;
      if (Math.abs(item.body.velocity.x) < 0.12) {
        item.body.velocity.x = 0;
      }
      // プルプル回転振動を急速収束
      item.body.angularVelocity.z *= 0.6;
    }
  });

  world.step(1 / 60, delta, 4);

  // 物理ステップ直後にもタワー内の勝手な横滑りを再ロック
  activeItems.forEach(item => {
    if (!item.isFallen && (item.inTower || item.everScored)) {
      if (Math.abs(item.body.velocity.x) < 0.12) {
        item.body.velocity.x = 0;
      }
      item.body.velocity.z = 0;
    }
  });

  // 2. トングの左右スイング更新（プレイ中＆非投下時に左右往復運動）
  if (isPlaying && !isDropping) {
    const currentSpeed = TONG_SWING_BASE_SPEED + Math.min(0.8, stackedCount * 0.04);
    tongSwingTime += delta * currentSpeed;
    window.tongX = Math.sin(tongSwingTime) * TONG_SWING_AMPLITUDE;
  }

  // 3. トングメッシュと保持中具材の同期（先端が具材をつかむ隙間0.02、投下時はtongRecoilYで軽快に跳ね上がる）
  const itemHoldY = highestY + TONG_HEIGHT_OFFSET;
  const tongBaseY = getTongVisualPlacementY(highestY, currentHeldDef) + tongRecoilY;
  if (tongMeshGroup) {
    tongMeshGroup.position.set(window.tongX, tongBaseY, 0);
  }
  if (currentHeldMesh) {
    currentHeldMesh.position.set(window.tongX, itemHoldY, 0);
  }

  // トング開閉アニメーション更新
  updateTongAnimation(delta);

  // 3b. 落下した各具材のメッシュと剛体の同期 & 着地時のぷるん弾力（Squash & Stretch）
  activeItems.forEach(item => {
    item.mesh.position.copy(item.body.position);
    item.mesh.quaternion.copy(item.body.quaternion);

    if (item.squashTime > 0 && item.baseScale) {
      item.squashTime = Math.max(0, item.squashTime - delta);
      const phase = (item.squashTime / 0.26) * Math.PI;
      const squash = Math.sin(phase) * 0.16;
      item.mesh.scale.set(
        item.baseScale.x * (1.0 + squash),
        item.baseScale.y * (1.0 - squash * 1.1),
        item.baseScale.z * (1.0 + squash)
      );
    }
  });

  // 3c. 3Dキラキラ＆ジューシーパーティクル更新
  updateParticles(delta);

  // 4. 有効タワーの再構築 & 落下判定（毎フレーム実行）
  if (isPlaying) {
    rebuildValidTower(delta);
  }

  // 5. ★純くんの全身ダイナミックアクション（左右ステップ移動・体スウェイ・交互足踏み・360度スピン・大ジャンプ）
  if (junKunMixer) {
    junKunMixer.update(delta);
  }
  if (junKun) {
    const nowSec = performance.now() * 0.001;
    // コンボや段数が増えるほど応援テンポがノリノリに！
    const danceFreq = 5.5 + Math.min(4.0, stackedCount * 0.35);

    // A. スツールの上でトングに合わせて左右にチョコチョコ元気よくステップ移動！
    const stepWalkX = Math.sin(nowSec * danceFreq * 0.5) * 0.045 + window.tongX * 0.06;
    junKun.position.x = -0.62 + stepWalkX;

    // B. スイング追従 ＋ 360度ハッピースピン！
    const baseRotY = 0.55 + window.tongX * 0.32 + Math.sin(nowSec * danceFreq * 0.5) * 0.14;
    if (junSpinTime > 0) {
      junSpinTime = Math.max(0, junSpinTime - delta);
      const spinAngle = (1.0 - (junSpinTime / 0.68)) * Math.PI * 2.0;
      junKun.rotation.y = baseRotY + spinAngle;
    } else {
      junKun.rotation.y += (baseRotY - junKun.rotation.y) * Math.min(1.0, delta * 10.0);
    }

    // C. 体を左右に可愛く揺らすダンススウェイ（Z軸傾き）
    const targetRotZ = Math.sin(nowSec * danceFreq) * 0.11 - window.tongX * 0.08;
    junKun.rotation.z += (targetRotZ - junKun.rotation.z) * Math.min(1.0, delta * 10.0);

    // D. タワーの見上げ & 投下時の注視
    if (isDropping) {
      junKun.rotation.x += (0.12 - junKun.rotation.x) * Math.min(1.0, delta * 8.0);
    } else {
      const lookUpAngle = -Math.min(0.24, Math.max(0, highestY - 0.64) * 0.05);
      junKun.rotation.x += (lookUpAngle - junKun.rotation.x) * Math.min(1.0, delta * 5.0);
    }

    // E. 脚ボーン（Leg_L / Leg_R）のパタパタ交互ステップ＆胴体ツイスト！
    // ※GLB内の脚ボーンは初期ポーズが rotation.x = -Math.PI（下向き）なので、-Math.PI を基準に揺らす！
    if (junLegL && junLegR) {
      const legSwing = Math.sin(nowSec * danceFreq) * 0.28;
      junLegL.rotation.x = -Math.PI + legSwing;
      junLegR.rotation.x = -Math.PI - legSwing;
    }
    if (junBodyNode) {
      junBodyNode.rotation.y = Math.sin(nowSec * danceFreq) * 0.15;
    }

    // F. リズミカルな応援バウンス ＋ ジャンプリアクション！
    const rhythmBounce = Math.abs(Math.sin(nowSec * danceFreq)) * 0.032;
    if (junHopTime > 0) {
      junHopTime = Math.max(0, junHopTime - delta);
      const hopOffset = Math.sin(Math.min(1.0, junHopTime / 0.48) * Math.PI) * 0.22;
      junKun.position.y = junKunBaseY + Math.max(rhythmBounce, hopOffset);
    } else {
      junKun.position.y = junKunBaseY + rhythmBounce;
    }
  }

  // 6. スマートカメラの幾何学フレーミング追従 (純くん足元〜塔上面〜トング全体をHUD内に包含)
  updateSmartCamera(delta);

  // 7. 描画
  renderer.render(scene, camera);
}

// スマートカメラの幾何学フレーミング計算（全表示対象のBox3 + 縦横FOV + 手前Z=1.22純くん足元解析解ガード）
function updateSmartCamera(delta) {
  if (!camera) return;

  const container = document.getElementById('game-container');
  const screenWidth = container ? container.clientWidth : 415;
  const screenHeight = container ? container.clientHeight : 740;
  const aspect = screenWidth / screenHeight;

  // 1. 全表示対象の3D境界（Box3）の算出
  const effectiveTopY = (diagnosticSimulatedHeight !== null) ? diagnosticSimulatedHeight : highestY;
  const currentDef = currentHeldDef || INGREDIENTS_DEF[0];
  const tongBaseY = getTongVisualPlacementY(effectiveTopY, currentDef);
  const tongTopY = tongBaseY + 1.34; // トング上端（実測1.34）

  // 画面内に常に見えるべき3D境界範囲:
  // - 下端 Ymin: 0.0 (純くんの足元スツール底面、テーブル天板)
  // - 上端 Ymax: tongTopY (トング上端)
  // - 水平 X: 純くん左端 (-0.80) 〜 お皿右端 (+1.35) ＋ トング移動余裕 (±1.10) => 幅2.70
  const yMin = 0.0;
  const yMax = tongTopY;
  const boxHeight = Math.max(2.6, yMax - yMin);
  const boxWidth = 2.70;

  // 2. スマホ画面上のセーフエリア定義（HUD上部120px・操作部下部145pxを確実に避ける有効領域）
  // NDC: 上端セーフ上限 Umax ≈ +0.67、下端セーフ下限 Umin ≈ -0.60
  const topMarginRatio = 120 / screenHeight;
  const bottomMarginRatio = 145 / screenHeight;
  const uMax = 1.0 - 2.0 * topMarginRatio; // 約 +0.67
  const uMin = -1.0 + 2.0 * bottomMarginRatio; // 約 -0.60
  const safeWidthRatio = 0.82; // 左右マージン

  // 3. 画角（FOV）から必要なカメラ距離と注視点の計算
  const fovYRad = (camera.fov * Math.PI) / 180;
  const tanHalfFovY = Math.tan(fovYRad / 2);
  const tanHalfFovX = tanHalfFovY * aspect;
  const pitch = CAMERA_PITCH_ANGLE; // 14度 (0.244 rad)
  const sinP = Math.sin(pitch);
  const cosP = Math.cos(pitch);

  // 注視点: 純くん足元(Y=0)とお皿が見切れないよう、高さの33%付近に低めに配置
  targetLookY = yMin + boxHeight * 0.33;

  // A. トング上端 (0, yMax, 0) が Umax 以内に収まる必要距離
  const dYTop = yMax - targetLookY;
  const distYTop = (dYTop * cosP) / (uMax * tanHalfFovY) + dYTop * sinP;

  // B. 手前Z=1.22の純くん足元 (X=-0.62, Y=0.0, Z=1.22) が Umin 以内に収まる必要距離（解析解）
  const absUMin = Math.abs(uMin);
  const distYJunFoot = (targetLookY * cosP + 1.22 * sinP) / (absUMin * tanHalfFovY) - targetLookY * sinP + 1.22 * cosP;

  // C. 水平方向 (X=±1.35) が収まる必要距離
  const distX = (boxWidth / 2) / (safeWidthRatio * tanHalfFovX);

  // 総合必要距離（全制約の最大値 + 6%安全マージン）
  targetCameraDistance = Math.max(distYTop, distYJunFoot, distX) * 1.06;
  targetCameraDistance = Math.max(5.2, targetCameraDistance);

  // 4. スムーズな補間追従 (急激なカクつきを防ぎ滑らかにズーム・チルト)
  const lerpSpeed = Math.min(1.0, delta * 4.5);
  currentCameraDistance += (targetCameraDistance - currentCameraDistance) * lerpSpeed;
  currentLookY += (targetLookY - currentLookY) * lerpSpeed;

  // 5. カメラ位置と向きの設定 (ピッチ角約14度で見下ろす自然な俯瞰アングル)
  const camY = currentLookY + currentCameraDistance * sinP;
  const camZ = currentCameraDistance * cosP;

  camera.position.set(0, camY, camZ);
  camera.lookAt(0, currentLookY, 0);
}

// 投影座標の診断ヘルパー（画面上のHUD・操作部セーフエリアに収まっているかを数値検証）
window.getProjectedBounds = function() {
  if (!camera) return null;
  camera.updateMatrixWorld();

  const container = document.getElementById('game-container');
  const w = container ? container.clientWidth : 415;
  const h = container ? container.clientHeight : 740;

  const effectiveTopY = (diagnosticSimulatedHeight !== null) ? diagnosticSimulatedHeight : highestY;
  const itemHoldY = effectiveTopY + TONG_HEIGHT_OFFSET;
  const currentDef = currentHeldDef || INGREDIENTS_DEF[0];
  const tongBaseY = getTongVisualPlacementY(effectiveTopY, currentDef);
  const tongTopY = tongBaseY + 1.34;

  const keyPoints = {
    stoolBase: new THREE.Vector3(-0.62, 0.0, 1.22),
    junHead: new THREE.Vector3(-0.62, 0.70, 1.22),
    plateLeft: new THREE.Vector3(-1.35, 0.33, 0),
    plateRight: new THREE.Vector3(1.35, 0.33, 0),
    plateFront: new THREE.Vector3(0, 0.33, 1.35),
    towerTop: new THREE.Vector3(0, effectiveTopY, 0),
    heldItem: new THREE.Vector3(window.tongX, itemHoldY, 0),
    tongTip: new THREE.Vector3(window.tongX, tongBaseY + 0.04, 0),
    tongTop: new THREE.Vector3(window.tongX, tongTopY, 0)
  };

  const projected = {};
  for (const [k, pt] of Object.entries(keyPoints)) {
    const clone = pt.clone().project(camera);
    // NDC: x in [-1, 1], y in [-1, 1] (y=+1 is top, y=-1 is bottom)
    // Pixel: px from left, py from top
    const px = (clone.x * 0.5 + 0.5) * w;
    const py = (-clone.y * 0.5 + 0.5) * h;
    projected[k] = {
      ndc: { x: parseFloat(clone.x.toFixed(3)), y: parseFloat(clone.y.toFixed(3)) },
      pixel: { x: Math.round(px), y: Math.round(py) }
    };
  }

  return {
    screenWidth: w,
    screenHeight: h,
    cameraDistance: parseFloat(currentCameraDistance.toFixed(2)),
    lookY: parseFloat(currentLookY.toFixed(2)),
    projected
  };
};

// リサイズ
function onWindowResize() {
  const container = document.getElementById('game-container');
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

// --- 5. 具材図鑑の描画（Blender制作3Dモデル .glb をスタジオ照明でリアルタイム3D撮影！） ---
const catalogThumbnailCache = {};
let catalogThumbScene = null;
let catalogThumbCamera = null;
let catalogThumbRoot = null;

function ensureCatalogThumbStudio() {
  if (catalogThumbScene) return;
  catalogThumbScene = new THREE.Scene();

  // 具材の焼き色や断面ディテールがくっきり映えるスタジオ照明
  const amb = new THREE.AmbientLight(0xFFF8F0, 0.85);
  catalogThumbScene.add(amb);

  const keyLight = new THREE.DirectionalLight(0xFFFFFF, 1.05);
  keyLight.position.set(2.5, 4.2, 3.0);
  catalogThumbScene.add(keyLight);

  const rimLight = new THREE.DirectionalLight(0xFFE0B2, 0.55);
  rimLight.position.set(-2.5, 2.0, -2.0);
  catalogThumbScene.add(rimLight);

  catalogThumbRoot = new THREE.Group();
  catalogThumbScene.add(catalogThumbRoot);

  // 斜め上（俯瞰38度）から具材の上面模様と厚みの両方が立体的に見えるアングル
  catalogThumbCamera = new THREE.PerspectiveCamera(34, 1.35, 0.1, 20);
}

function renderCatalogModelToDataURL(def) {
  if (!renderer) return '';
  const hasRealGLB = Boolean(loadedGLBModels[def.id]);
  if (hasRealGLB && catalogThumbnailCache[def.id]) {
    return catalogThumbnailCache[def.id];
  }

  ensureCatalogThumbStudio();

  while (catalogThumbRoot.children.length > 0) {
    catalogThumbRoot.remove(catalogThumbRoot.children[0]);
  }

  const mesh = createIngredientMesh(def);
  // 具材の美味しそうなディテール（トマトの種・パティの焼き目・玉ねぎの輪・目玉焼きの黄身）がよく見えるよう少し手前に傾ける
  mesh.rotation.set(0.22, -0.38, 0.05);
  catalogThumbRoot.add(mesh);

  // バウンディングボックスから最適なカメラ距離を自動計算
  const box = new THREE.Box3().setFromObject(mesh);
  const size = new THREE.Vector3();
  const center = new THREE.Vector3();
  box.getSize(size);
  box.getCenter(center);

  const maxDim = Math.max(size.x, size.y, size.z, 0.65);
  const dist = maxDim * 1.95;
  catalogThumbCamera.position.set(center.x + dist * 0.22, center.y + dist * 0.72, center.z + dist * 0.85);
  catalogThumbCamera.lookAt(center.x, center.y, center.z);

  // 現在のメインレンダラー状態を退避してオフスクリーン撮影
  const prevSize = new THREE.Vector2();
  renderer.getSize(prevSize);
  const prevPixelRatio = renderer.getPixelRatio();
  const prevClearColor = new THREE.Color();
  renderer.getClearColor(prevClearColor);
  const prevClearAlpha = renderer.getClearAlpha();

  renderer.setPixelRatio(2);
  renderer.setSize(216, 160, false);
  renderer.setClearColor(0x000000, 0);
  renderer.clear();
  renderer.render(catalogThumbScene, catalogThumbCamera);

  const dataUrl = renderer.domElement.toDataURL('image/png');

  // メインレンダラーを即座に元のサイズ・背景色に復元
  renderer.setPixelRatio(prevPixelRatio);
  renderer.setSize(prevSize.x, prevSize.y, false);
  renderer.setClearColor(prevClearColor, prevClearAlpha);
  if (scene && camera) {
    renderer.render(scene, camera);
  }

  if (hasRealGLB) {
    catalogThumbnailCache[def.id] = dataUrl;
  }
  return dataUrl;
}

function updateCatalogThumbnailForId(id) {
  const allItems = [...INGREDIENTS_DEF, TOP_BUN_DEF];
  const def = allItems.find(d => d.id === id);
  if (!def) return;
  const dataUrl = renderCatalogModelToDataURL(def);
  const imgEl = document.getElementById(`catalog-thumb-${id}`);
  if (imgEl && dataUrl) {
    imgEl.src = dataUrl;
  }
}

function renderIngredientCatalog() {
  const container = document.getElementById('ingredient-catalog-list');
  if (!container) return;
  container.innerHTML = '';

  const allItems = [...INGREDIENTS_DEF, TOP_BUN_DEF];
  allItems.forEach(def => {
    const heightCm = (def.height * 10).toFixed(2).replace(/0$/, '');
    const price = def.price || 300;
    const desc = def.desc || 'プクムク特製の美味しいサンドイッチ具材！';
    const isSpecial = def.isRare || def.isTopBun;

    const thumbUrl = renderCatalogModelToDataURL(def);

    const card = document.createElement('div');
    card.className = 'catalog-item-card' + (isSpecial ? ' rare-card' : '');

    let badgeHtml = '';
    if (def.isTopBun) {
      badgeHtml = '<span class="catalog-rare-badge">👑 仕上げ専用 (スコア×2)</span>';
    } else if (def.isRare) {
      badgeHtml = '<span class="catalog-rare-badge">🌟 レア具材</span>';
    }

    card.innerHTML = `
      <div class="catalog-thumb-wrap">
        <img id="catalog-thumb-${def.id}" class="catalog-thumb-img" src="${thumbUrl}" alt="${escapeHtmlSafe(def.name)}">
      </div>
      <div class="catalog-item-header">
        <span class="catalog-item-name">${def.name}</span>
        ${badgeHtml}
      </div>
      <div class="catalog-item-metrics">
        <span class="catalog-metric-pill height-pill"><span>📏 高さ</span><span>${heightCm} cm</span></span>
        <span class="catalog-metric-pill price-pill"><span>💰 値段</span><span>¥${price.toLocaleString()}</span></span>
      </div>
      <div class="catalog-item-desc">${desc}</div>
    `;
    container.appendChild(card);
  });
}

// --- 6. 世界ランキングシステム（サンドイッチタワー専用スプレッドシート Web App URL） ---
const TOWER_GAS_API_URL = 'https://script.google.com/macros/s/AKfycbxpxw0_S9XiUARODxQJ5Icv-jZ6t1kgBgbPn_6PXmApCq1JaUh5lzewaxofPPMdxqkIjg/exec';
const LOCAL_TOWER_RANKING_API = '/api/tower_ranking';
const LOCAL_TOWER_RANKING_KEY = 'pukumuku_sandwich_tower_rankings_v3';

let currentResultRankingMode = 'score'; // 'score' | 'height'
let currentModalRankingMode = 'score';  // 'score' | 'height'
let hasSubmittedCurrentTowerScore = false;
let lastSubmittedTowerRecordId = null;

function escapeHtmlSafe(str) {
  return String(str || '').replace(/[&<>"']/g, function(m) {
    return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[m];
  });
}

function getLocalTowerRankings() {
  try {
    const raw = localStorage.getItem(LOCAL_TOWER_RANKING_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}

  const defaults = [
    { id: 'def1', name: 'プクムク職人', score: 18400, height: 26.5, completed: true, date: '2026/11/08' },
    { id: 'def2', name: '純くんファン', score: 14200, height: 22.0, completed: true, date: '2026/11/08' },
    { id: 'def3', name: 'バーガー王', score: 11500, height: 19.8, completed: false, date: '2026/11/08' },
    { id: 'def4', name: 'サンドマスター', score: 8900, height: 15.4, completed: true, date: '2026/11/08' },
    { id: 'def5', name: 'たまご大好き', score: 6200, height: 11.2, completed: false, date: '2026/11/08' }
  ];
  try {
    localStorage.setItem(LOCAL_TOWER_RANKING_KEY, JSON.stringify(defaults));
  } catch (e) {}
  return defaults;
}

function saveLocalTowerRankingEntry(entry) {
  const list = getLocalTowerRankings();
  const cleanName = (entry.name || '').trim();
  const existingIdx = list.findIndex(r => (r.name || '').trim() === cleanName);
  if (existingIdx !== -1) {
    const existing = list[existingIdx];
    list[existingIdx] = {
      ...existing,
      id: entry.id,
      score: Math.max(Number(existing.score || 0), Number(entry.score || 0)),
      height: Math.max(Number(existing.height || 0), Number(entry.height || 0)),
      completed: existing.completed || entry.completed,
      date: entry.date || existing.date
    };
  } else {
    list.push(entry);
  }
  try {
    localStorage.setItem(LOCAL_TOWER_RANKING_KEY, JSON.stringify(list.slice(-100)));
  } catch (e) {}
  return list;
}

function prepareResultTowerRanking() {
  hasSubmittedCurrentTowerScore = false;
  lastSubmittedTowerRecordId = null;

  const nameInput = document.getElementById('player-name-input');
  const submitBtn = document.getElementById('submit-ranking-btn');
  const msgEl = document.getElementById('ranking-feedback') || document.getElementById('ranking-submit-msg');
  const regBox = document.getElementById('ranking-register-box');

  const savedName = localStorage.getItem('pukumuku_player_name') || '';
  if (nameInput) {
    nameInput.value = savedName;
    nameInput.disabled = false;
  }
  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.innerText = '登録！';
  }
  if (msgEl) {
    msgEl.innerText = '';
    msgEl.className = 'ranking-feedback';
  }
  if (regBox) {
    regBox.style.display = (lastFinalEarnedScore > 0 || lastFinalHeightCm > 0) ? 'block' : 'none';
  }

  fetchTowerRankings(currentResultRankingMode, 'result-ranking-list', null);
}

async function fetchTowerRankings(mode = 'score', containerId = 'modal-ranking-list', highlightId = null) {
  const listEl = document.getElementById(containerId);
  if (!listEl) return;
  listEl.innerHTML = '<div class="ranking-loading">🌐 世界ランキングを読み込み中...</div>';

  let records = [];

  // 1. ローカルサーバーAPI (/api/tower_ranking) の取得を試行
  try {
    const res = await fetch(`${LOCAL_TOWER_RANKING_API}?t=${Date.now()}`, { cache: 'no-store' });
    if (res.ok) {
      const data = await res.json();
      const arr = (mode === 'height') ? (data.heightRankings || data.rankings) : (data.scoreRankings || data.rankings);
      if (Array.isArray(arr) && arr.length > 0) {
        records.push(...arr);
      }
    }
  } catch (err) {
    // フォールバックへ
  }

  // 2. サンドイッチタワー専用スプレッドシート (Google Apps Script Web App) からも取得して統合
  if (TOWER_GAS_API_URL) {
    try {
      const gasRes = await fetch(`${TOWER_GAS_API_URL}?game=sandwich_tower&sheet=sandwich_tower&mode=${mode}&t=${Date.now()}`, { cache: 'no-store' });
      if (gasRes.ok) {
        const gasData = await gasRes.json();
        const arr = Array.isArray(gasData) ? gasData : (gasData.rankings || []);
        if (arr.length > 0) {
          const gasMapped = arr.map((r, idx) => ({
            id: r.id || `gas_${idx}_${r.name}_${r.score}`,
            name: String(r.name || '名無し職人'),
            score: Number(r.score || 0),
            height: Number(r.height || 0),
            completed: Boolean(r.completed)
          }));
          records.push(...gasMapped);
        }
      }
    } catch (err) {
      // オフライン・CORS制限時はローカルストレージと統合
    }
  }

  // 3. ローカルストレージのデータと統合し、指定モードでソート
  const localRecords = getLocalTowerRankings();
  const rawCombined = [...records, ...localRecords].map(r => ({
    id: r.id || `${r.name}_${r.score}_${r.height}`,
    name: String(r.name || '名無し職人').trim().slice(0, 12),
    score: Number(r.score || 0),
    height: Number(r.height || 0),
    completed: Boolean(r.completed),
    date: r.date || ''
  }));

  // まず指定モードで降順ソート（最高記録が先頭に来るようにする）
  if (mode === 'height') {
    rawCombined.sort((a, b) => (b.height - a.height) || (b.score - a.score));
  } else {
    rawCombined.sort((a, b) => (b.score - a.score) || (b.height - a.height));
  }

  // ★【同一名前・重複スコアの完全排除（1プレイヤー1枠・自己最高記録のみ掲載）】
  const uniqueRankings = [];
  const seenNames = new Set();
  for (const r of rawCombined) {
    if (!r.name) continue;
    if (!seenNames.has(r.name)) {
      seenNames.add(r.name);
      uniqueRankings.push(r);
    }
  }

  renderTowerRankingItems(uniqueRankings.slice(0, 30), mode, listEl, highlightId || lastSubmittedTowerRecordId);
}

function renderTowerRankingItems(items, mode, containerEl, highlightId) {
  if (!containerEl) return;
  if (!items || items.length === 0) {
    containerEl.innerHTML = '<div class="ranking-loading">まだ記録がありません。最初の記録を登録しよう！</div>';
    return;
  }

  const currentPlayerName = localStorage.getItem('pukumuku_player_name') || '';

  containerEl.innerHTML = items.map((item, idx) => {
    const rank = idx + 1;
    let rankBadge = `${rank}位`;
    let rowClass = 'ranking-item';
    if (rank === 1) { rankBadge = '🥇 1位'; rowClass += ' rank-1'; }
    else if (rank === 2) { rankBadge = '🥈 2位'; rowClass += ' rank-2'; }
    else if (rank === 3) { rankBadge = '🥉 3位'; rowClass += ' rank-3'; }

    const isMyHighlight = (highlightId && (item.id === highlightId)) ||
                          (highlightId && currentPlayerName && item.name === currentPlayerName);
    if (isMyHighlight) {
      rowClass += ' rank-me';
    }

    const safeName = escapeHtmlSafe(item.name || '名無し職人');
    const crown = item.completed ? '👑' : '🥪';
    const scoreStr = `¥${Number(item.score || 0).toLocaleString()}`;
    const heightStr = `${Number(item.height || 0).toFixed(1)} cm`;

    const primaryVal = (mode === 'height') ? `📏 ${heightStr}` : `💰 ${scoreStr}`;
    const subVal = (mode === 'height') ? `(${scoreStr})` : `(高さ ${heightStr})`;

    return `
      <div class="${rowClass}">
        <span class="rank-num">${rankBadge}</span>
        <span class="rank-name">${crown} ${safeName}</span>
        <span class="rank-val">${primaryVal} <small class="rank-sub-val">${subVal}</small></span>
      </div>
    `;
  }).join('');
}

async function submitTowerScore() {
  if (hasSubmittedCurrentTowerScore) return;

  const nameInput = document.getElementById('player-name-input');
  const submitBtn = document.getElementById('submit-ranking-btn');
  const msgEl = document.getElementById('ranking-feedback') || document.getElementById('ranking-submit-msg');

  const rawName = nameInput ? nameInput.value.trim() : '';
  const playerName = (rawName || '名無し職人').slice(0, 12);
  localStorage.setItem('pukumuku_player_name', playerName);

  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = '送信中...';
  }
  if (msgEl) {
    msgEl.innerText = '🌐 世界ランキングへ記録を送信中...';
    msgEl.className = 'ranking-feedback';
  }

  const recordId = 'rec_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6);
  const newEntry = {
    id: recordId,
    name: playerName,
    score: lastFinalEarnedScore,
    height: lastFinalHeightCm,
    completed: isGameCompletedWithBun,
    date: new Date().toLocaleDateString('ja-JP')
  };

  // 1. まずローカルストレージに即時保存
  saveLocalTowerRankingEntry(newEntry);
  lastSubmittedTowerRecordId = recordId;
  hasSubmittedCurrentTowerScore = true;

  // 2. ローカルサーバーAPI (/api/tower_ranking) に送信
  let serverRankScore = null;
  let serverRankHeight = null;
  try {
    const res = await fetch(LOCAL_TOWER_RANKING_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newEntry)
    });
    if (res.ok) {
      const data = await res.json();
      serverRankScore = data.scoreRank;
      serverRankHeight = data.heightRank;
    }
  } catch (e) {}

  // 3. スプレッドシート (Google Apps Script Web App) にも非同期で送信（sheet: 'sandwich_tower' 指定）
  if (TOWER_GAS_API_URL) {
    fetch(TOWER_GAS_API_URL, {
      method: 'POST',
      mode: 'no-cors',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify({
        game: 'sandwich_tower',
        sheet: 'sandwich_tower',
        name: playerName,
        score: lastFinalEarnedScore,
        height: lastFinalHeightCm,
        completed: isGameCompletedWithBun
      })
    }).catch(() => {});
  }

  if (nameInput) nameInput.disabled = true;
  if (submitBtn) submitBtn.innerText = '登録完了 ✓';
  if (msgEl) {
    const rankInfo = (serverRankScore && serverRankHeight)
      ? `（純利益 ${serverRankScore}位 / 高さ ${serverRankHeight}位）`
      : '';
    msgEl.innerText = `🎉 「${playerName}」で世界ランキングに登録しました！${rankInfo}`;
    msgEl.className = 'ranking-feedback ok';
  }

  // リザルト内ランキングを再描画
  fetchTowerRankings(currentResultRankingMode, 'result-ranking-list', recordId);
}

// --- ボタンイベントのバインド ---
document.getElementById('start-btn').addEventListener('click', () => startGame());
document.getElementById('restart-btn').addEventListener('click', () => startGame());

// ランキング登録ボタン
const submitRankingBtn = document.getElementById('submit-ranking-btn');
if (submitRankingBtn) {
  submitRankingBtn.addEventListener('click', () => submitTowerScore());
}
const playerNameInput = document.getElementById('player-name-input');
if (playerNameInput) {
  playerNameInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      submitTowerScore();
    }
  });
}

// リザルト画面のランキングタブ切替（純利益 / 高さ）
const resultTabScore = document.getElementById('result-tab-score');
const resultTabHeight = document.getElementById('result-tab-height');
if (resultTabScore && resultTabHeight) {
  resultTabScore.addEventListener('click', () => {
    currentResultRankingMode = 'score';
    resultTabScore.classList.add('active');
    resultTabHeight.classList.remove('active');
    fetchTowerRankings('score', 'result-ranking-list', lastSubmittedTowerRecordId);
  });
  resultTabHeight.addEventListener('click', () => {
    currentResultRankingMode = 'height';
    resultTabHeight.classList.add('active');
    resultTabScore.classList.remove('active');
    fetchTowerRankings('height', 'result-ranking-list', lastSubmittedTowerRecordId);
  });
}

// 世界ランキングモーダルの開閉＆タブ切替
const rankingModal = document.getElementById('ranking-modal');
const openRankingBtn = document.getElementById('open-ranking-btn');
const closeRankingBtn = document.getElementById('close-ranking-btn');
const modalTabScore = document.getElementById('modal-tab-score');
const modalTabHeight = document.getElementById('modal-tab-height');

if (openRankingBtn && rankingModal) {
  openRankingBtn.addEventListener('click', () => {
    rankingModal.classList.add('active');
    fetchTowerRankings(currentModalRankingMode, 'modal-ranking-list', lastSubmittedTowerRecordId);
  });
}
if (closeRankingBtn && rankingModal) {
  closeRankingBtn.addEventListener('click', () => {
    rankingModal.classList.remove('active');
  });
}
if (modalTabScore && modalTabHeight) {
  modalTabScore.addEventListener('click', () => {
    currentModalRankingMode = 'score';
    modalTabScore.classList.add('active');
    modalTabHeight.classList.remove('active');
    fetchTowerRankings('score', 'modal-ranking-list', lastSubmittedTowerRecordId);
  });
  modalTabHeight.addEventListener('click', () => {
    currentModalRankingMode = 'height';
    modalTabHeight.classList.add('active');
    modalTabScore.classList.remove('active');
    fetchTowerRankings('height', 'modal-ranking-list', lastSubmittedTowerRecordId);
  });
}

// 具材図鑑モーダルの開閉（スタート画面・HUD・リザルト画面すべてから開ける）
const catalogModal = document.getElementById('catalog-modal');
const closeCatalogBtn = document.getElementById('close-catalog-btn');
['open-catalog-btn', 'hud-catalog-btn', 'result-catalog-btn'].forEach(btnId => {
  const btn = document.getElementById(btnId);
  if (btn && catalogModal) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      renderIngredientCatalog();
      catalogModal.classList.add('active');
    });
  }
});
if (closeCatalogBtn && catalogModal) {
  closeCatalogBtn.addEventListener('click', () => {
    catalogModal.classList.remove('active');
  });
}

// 遊び方説明書モーダルの開閉（スタート画面・リザルト画面から開ける）
const manualModal = document.getElementById('manual-modal');
const closeManualBtn = document.getElementById('close-manual-btn');
['open-manual-btn', 'result-manual-btn'].forEach(btnId => {
  const btn = document.getElementById(btnId);
  if (btn && manualModal) {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      manualModal.classList.add('active');
    });
  }
});
if (closeManualBtn && manualModal) {
  closeManualBtn.addEventListener('click', () => {
    manualModal.classList.remove('active');
  });
}

const soundBtn = document.getElementById('sound-btn');
if (soundBtn) {
  soundBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const muted = sounds.toggleMute();
    soundBtn.innerText = muted ? '🔇 消音' : '🔊 サウンド';
  });
}

// テスト・検証用ヘルパー公開
window.triggerCompleteForTest = () => completeSandwichTower();

// 起動
window.addEventListener('DOMContentLoaded', () => {
  initGame();
});
