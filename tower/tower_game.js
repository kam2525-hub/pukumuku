// ============================================================
// 🍔 ぐらぐら！サンドイッチタワー (C) パン工房プクムク
// Three.js + Cannon-es 3D物理シミュレーション
// ============================================================

// --- 1. サウンドシステム (Web Audio API) ---
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

  // 具材投下音（ポトッ）
  playDrop() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(380, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(160, this.ctx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.25, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.13);
    } catch (e) {}
  }

  // 着地音（ポンッ・ぷるん）
  playLand() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(260, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(420, this.ctx.currentTime + 0.08);
      gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.1);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.11);
    } catch (e) {}
  }

  // 落下失敗音（ボテッ！）
  playFall() {
    if (this.isMuted || !this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(200, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(60, this.ctx.currentTime + 0.25);
      gain.gain.setValueAtTime(0.3, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.26);
    } catch (e) {}
  }

  // 終了ファンファーレ
  playGameOver() {
    if (this.isMuted || !this.ctx) return;
    const notes = [261.63, 329.63, 392.00, 523.25];
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        try {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
          gain.gain.setValueAtTime(0.25, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.35);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.36);
        } catch (e) {}
      }, idx * 120);
    });
  }
}

const sounds = new TowerSoundSystem();

// --- 2. 具材の定義 ---
const INGREDIENTS = [
  {
    id: 'patty',
    name: '肉厚パティ',
    type: 'cylinder',
    radius: 0.54,
    height: 0.18,
    color: 0x4A2E18,
    mass: 2.2,
    friction: 0.95,
    restitution: 0.0
  },
  {
    id: 'tomato',
    name: 'スライストマト',
    type: 'cylinder',
    radius: 0.52,
    height: 0.12,
    color: 0xE53935,
    mass: 1.4,
    friction: 0.85,
    restitution: 0.0
  },
  {
    id: 'cheese',
    name: 'とろけるチーズ',
    type: 'box',
    width: 0.98,
    height: 0.05,
    depth: 0.98,
    color: 0xFFC107,
    mass: 1.0,
    friction: 0.98, // 密着して滑り止めになる
    restitution: 0.0
  },
  {
    id: 'lettuce',
    name: 'フリルレタス',
    type: 'box',
    width: 1.05,
    height: 0.06,
    depth: 1.05,
    color: 0x43A047,
    mass: 0.8,
    friction: 0.9,
    restitution: 0.0
  },
  {
    id: 'egg',
    name: 'ぷるぷるたまご',
    type: 'cylinder',
    radius: 0.50,
    height: 0.14,
    color: 0xFFF9C4,
    mass: 1.2,
    friction: 0.85,
    restitution: 0.0
  },
  {
    id: 'croissant_bonus',
    name: '名物クロワッサン',
    type: 'box',
    width: 0.82,
    height: 0.22,
    depth: 0.58,
    color: 0xD87D2B,
    mass: 1.1,
    friction: 0.9,
    restitution: 0.0
  }
];

// --- 3. ゲーム管理変数 ---
let scene, camera, renderer, world;
let plateBody, baseBunBody;
let activeItems = []; // { mesh, body, counted, fallen }
let currentHeldMesh = null;
let currentHeldDef = null;

let isPlaying = false;
let isDropping = false;
let lives = 3;
let stackedCount = 0;
let highestY = 0;
let tongX = 0;
let tongSpeed = 2.4;
let tongTime = 0;

let basePlateY = 0.4;
let targetCameraY = 1.6;
let currentCameraY = 1.6;
const TONG_HEIGHT_OFFSET = 1.35; // トングの高さを適度に近づけて優しくポトッと落とす
let tongMeshGroup = null;

// --- 4. 初期化 ---
function initGame() {
  const container = document.getElementById('game-container');
  const canvas = document.getElementById('webgl-canvas');
  const width = container.clientWidth;
  const height = container.clientHeight;

  // 1. Three.js シーン
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xFFF8E7);
  scene.fog = new THREE.FogExp2(0xFFF8E7, 0.025);

  // 2. カメラ (スマホ縦画面に最適化)
  camera = new THREE.PerspectiveCamera(54, width / height, 0.1, 100);
  camera.position.set(0, currentCameraY, 4.0);
  camera.lookAt(0, currentCameraY - 0.1, 0);

  // 3. レンダラー
  renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // 4. 照明
  const ambientLight = new THREE.AmbientLight(0xFFF5E6, 0.85);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0xFFFAF0, 1.0);
  dirLight.position.set(4, 10, 5);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 1024;
  dirLight.shadow.mapSize.height = 1024;
  dirLight.shadow.camera.near = 0.5;
  dirLight.shadow.camera.far = 25;
  dirLight.shadow.camera.left = -3;
  dirLight.shadow.camera.right = 3;
  dirLight.shadow.camera.top = 10;
  dirLight.shadow.camera.bottom = -2;
  scene.add(dirLight);

  // 5. Cannon 物理ワールド
  world = new CANNON.World();
  world.gravity.set(0, -9.82, 0);
  world.broadphase = new CANNON.NaiveBroadphase();
  world.solver.iterations = 14;

  // ★反発ゼロ＆高摩擦設定（具材が弾かれず、しっとりピタッと重なる！）
  world.defaultContactMaterial.friction = 0.85;
  world.defaultContactMaterial.restitution = 0.0;
  world.defaultContactMaterial.contactEquationStiffness = 1e7;
  world.defaultContactMaterial.contactEquationRelaxation = 3;

  // 6. テーブルとお皿の作成
  createTableAndPlate();
  createTongModel();

  // 7. リサイズ処理
  window.addEventListener('resize', onWindowResize);

  // 8. タップイベント（画面全体）
  container.addEventListener('pointerdown', (e) => {
    // ボタンクリック時は除外
    if (e.target.closest('button') || e.target.closest('a') || e.target.closest('.modal-card')) return;
    sounds.init();
    if (isPlaying && !isDropping) {
      dropCurrentItem();
    }
  });

  // 9. ループ開始
  requestAnimationFrame(animate);
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

  // お皿（Three.js）
  const plateGeo = new THREE.CylinderGeometry(1.35, 1.1, 0.14, 32);
  const plateMat = new THREE.MeshStandardMaterial({ color: 0xFFFFFF, roughness: 0.2, metalness: 0.1 });
  const plateMesh = new THREE.Mesh(plateGeo, plateMat);
  plateMesh.position.set(0, basePlateY - 0.07, 0);
  plateMesh.receiveShadow = true;
  scene.add(plateMesh);

  // お皿の物理ボディ (Static)
  const plateShape = new CANNON.Cylinder(1.35, 1.1, 0.14, 24);
  plateBody = new CANNON.Body({ mass: 0 }); // 静的剛体
  plateBody.addShape(plateShape);
  plateBody.position.set(0, basePlateY - 0.07, 0);
  plateBody.material = new CANNON.Material({ friction: 0.95, restitution: 0.0 });
  world.addBody(plateBody);

  // お皿の上の「土台バンズ（底のパン）」
  createBaseBun();
}

// トングの3Dモデル（金属製アーム）
function createTongModel() {
  tongMeshGroup = new THREE.Group();

  const metalMat = new THREE.MeshStandardMaterial({
    color: 0xCFD8DC,
    metalness: 0.85,
    roughness: 0.25
  });

  // 左アーム
  const armGeo = new THREE.CylinderGeometry(0.035, 0.035, 1.2, 12);
  const leftArm = new THREE.Mesh(armGeo, metalMat);
  leftArm.position.set(-0.35, 0.45, 0);
  leftArm.rotation.z = -0.15;
  tongMeshGroup.add(leftArm);

  // 右アーム
  const rightArm = new THREE.Mesh(armGeo, metalMat);
  rightArm.position.set(0.35, 0.45, 0);
  rightArm.rotation.z = 0.15;
  tongMeshGroup.add(rightArm);

  // 上部の持ち手（アーチ）
  const topGeo = new THREE.CylinderGeometry(0.04, 0.04, 0.45, 12);
  const topArch = new THREE.Mesh(topGeo, metalMat);
  topArch.position.set(0, 1.0, 0);
  topArch.rotation.z = Math.PI / 2;
  tongMeshGroup.add(topArch);

  // 先端のグリップ
  const tipGeo = new THREE.BoxGeometry(0.12, 0.08, 0.25);
  const leftTip = new THREE.Mesh(tipGeo, metalMat);
  leftTip.position.set(-0.25, -0.1, 0);
  tongMeshGroup.add(leftTip);

  const rightTip = new THREE.Mesh(tipGeo, metalMat);
  rightTip.position.set(0.25, -0.1, 0);
  tongMeshGroup.add(rightTip);

  tongMeshGroup.position.set(0, 3.5, 0);
  scene.add(tongMeshGroup);
}

// 土台バンズ
function createBaseBun() {
  const radius = 0.68;
  const height = 0.24;
  const bunGeo = new THREE.CylinderGeometry(radius, radius * 0.95, height, 28);
  const bunMat = new THREE.MeshStandardMaterial({ color: 0xDDA15E, roughness: 0.5 });
  const bunMesh = new THREE.Mesh(bunGeo, bunMat);
  bunMesh.position.set(0, basePlateY + height / 2, 0);
  bunMesh.castShadow = true;
  bunMesh.receiveShadow = true;
  scene.add(bunMesh);

  // 土台バンズの剛体 (Static)
  const bunShape = new CANNON.Cylinder(radius, radius * 0.95, height, 20);
  baseBunBody = new CANNON.Body({ mass: 0 });
  baseBunBody.addShape(bunShape);
  baseBunBody.position.set(0, basePlateY + height / 2, 0);
  baseBunBody.material = new CANNON.Material({ friction: 0.95, restitution: 0.0 });
  world.addBody(baseBunBody);

  highestY = basePlateY + height;
}

// 具材のThree.jsメッシュ生成ヘルパー
function createIngredientMesh(def) {
  let geo;
  if (def.type === 'cylinder') {
    geo = new THREE.CylinderGeometry(def.radius, def.radius, def.height, 24);
  } else if (def.type === 'box') {
    geo = new THREE.BoxGeometry(def.width, def.height, def.depth);
  }

  const mat = new THREE.MeshStandardMaterial({
    color: def.color,
    roughness: 0.45,
    metalness: 0.05
  });

  const mesh = new THREE.Mesh(geo, mat);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  // ディテール追加
  if (def.id === 'egg') {
    // 黄身の追加
    const yolkGeo = new THREE.SphereGeometry(0.18, 16, 16);
    const yolkMat = new THREE.MeshStandardMaterial({ color: 0xFFA000, roughness: 0.2 });
    const yolkMesh = new THREE.Mesh(yolkGeo, yolkMat);
    yolkMesh.scale.set(1, 0.5, 1);
    yolkMesh.position.set(0, def.height / 2 + 0.04, 0);
    mesh.add(yolkMesh);
  } else if (def.id === 'tomato') {
    // トマトのタネ風
    const centerGeo = new THREE.CylinderGeometry(def.radius * 0.8, def.radius * 0.8, def.height * 1.01, 16);
    const centerMat = new THREE.MeshStandardMaterial({ color: 0xC62828, roughness: 0.3 });
    const centerMesh = new THREE.Mesh(centerGeo, centerMat);
    mesh.add(centerMesh);
  }

  return mesh;
}

// トングで掴んでいる具材の準備
function prepareNextItem() {
  if (!isPlaying) return;
  const def = INGREDIENTS[Math.floor(Math.random() * INGREDIENTS.length)];
  currentHeldDef = def;

  if (currentHeldMesh) {
    scene.remove(currentHeldMesh);
  }
  currentHeldMesh = createIngredientMesh(def);
  scene.add(currentHeldMesh);
  isDropping = false;
}

// 具材の投下
function dropCurrentItem() {
  if (!currentHeldMesh || !currentHeldDef || isDropping) return;
  isDropping = true;
  sounds.playDrop();

  const def = currentHeldDef;
  const spawnY = highestY + TONG_HEIGHT_OFFSET;
  const spawnX = tongX;

  // Cannon 剛体の生成
  let shape;
  if (def.type === 'cylinder') {
    shape = new CANNON.Cylinder(def.radius, def.radius, def.height, 16);
  } else if (def.type === 'box') {
    shape = new CANNON.Box(new CANNON.Vec3(def.width / 2, def.height / 2, def.depth / 2));
  }

  const mat = new CANNON.Material({ friction: def.friction, restitution: 0.0 });
  const body = new CANNON.Body({
    mass: def.mass,
    shape: shape,
    material: mat,
    position: new CANNON.Vec3(spawnX, spawnY, 0),
    linearDamping: 0.45,
    angularDamping: 0.65
  });

  // 初速は水平に安定して落とす（激しい回転による弾きを防止）
  body.angularVelocity.set(
    (Math.random() - 0.5) * 0.08,
    (Math.random() - 0.5) * 0.1,
    (Math.random() - 0.5) * 0.08
  );

  world.addBody(body);

  // メッシュとのバインド
  const droppedMesh = currentHeldMesh;
  currentHeldMesh = null;

  activeItems.push({
    def: def,
    mesh: droppedMesh,
    body: body,
    counted: false,
    fallen: false
  });

  // 着地音のバインド
  body.addEventListener('collide', () => {
    sounds.playLand();
  });

  // 次の具材を少し遅れて装填
  setTimeout(() => {
    if (isPlaying) {
      prepareNextItem();
    }
  }, 450);
}

// 落下・スタックの判定
function checkStackAndFalls() {
  const plateLimitY = -1.5;
  let currentMaxY = basePlateY + 0.22;
  let newStackedThisFrame = 0;

  activeItems.forEach((item) => {
    // 1. お皿から落下したか判定
    if (!item.fallen && item.body.position.y < plateLimitY) {
      item.fallen = true;
      sounds.playFall();
      onItemFall(item);
    }

    // 2. 着地して静止したか判定
    if (!item.fallen && !item.counted) {
      const vel = item.body.velocity.length();
      if (item.body.position.y > basePlateY && vel < 0.25) {
        item.counted = true;
        stackedCount++;
        newStackedThisFrame++;
        updateStatsUI();
      }
    }

    // 3. 有効な具材の最高点を追跡
    if (!item.fallen && item.body.position.y > basePlateY) {
      const topY = item.body.position.y + 0.1;
      if (topY > currentMaxY) {
        currentMaxY = topY;
      }
    }
  });

  highestY = currentMaxY;

  // カメラターゲットの上昇
  targetCameraY = Math.max(1.6, highestY + 0.8);

  if (newStackedThisFrame > 0 && stackedCount % 5 === 0) {
    showToast(`✨ ${stackedCount}段突破！いい調子！`, 'good');
  }
}

// 具材が落下したときの処理（3アウト制）
function onItemFall(item) {
  lives--;
  updateLivesUI();
  showToast('⚠️ 具材が落下！', 'bad');

  // 物理ワールドとシーンから削除
  world.removeBody(item.body);
  scene.remove(item.mesh);

  if (lives <= 0) {
    endGame();
  }
}

// UI更新
function updateStatsUI() {
  // 高さ計算 (実寸換算: 1ユニット = 約 10cm)
  const heightCm = Math.max(0, (highestY - (basePlateY + 0.22)) * 10).toFixed(1);
  const heightEl = document.getElementById('height-val');
  const countEl = document.getElementById('count-val');

  if (heightEl) heightEl.innerText = heightCm;
  if (countEl) countEl.innerText = stackedCount;
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

// トースト通知表示
function showToast(text, type = 'good') {
  const toast = document.getElementById('toast-msg');
  if (!toast) return;
  toast.innerText = text;
  toast.className = type === 'good' ? 'toast-good show' : 'toast-bad show';
  setTimeout(() => {
    toast.classList.remove('show');
  }, 1200);
}

// ゲームスタート
function startGame() {
  isPlaying = true;
  isDropping = false;
  lives = 3;
  stackedCount = 0;
  highestY = basePlateY + 0.22;
  targetCameraY = 1.6;
  currentCameraY = 1.6;

  // 既存具材のクリア
  activeItems.forEach(item => {
    world.removeBody(item.body);
    scene.remove(item.mesh);
  });
  activeItems = [];

  updateLivesUI();
  updateStatsUI();

  document.getElementById('start-modal').classList.remove('active');
  document.getElementById('result-modal').classList.remove('active');

  sounds.init();
  prepareNextItem();
}

// ゲームオーバー（営業終了）
function endGame() {
  isPlaying = false;
  isDropping = true;
  sounds.playGameOver();

  if (currentHeldMesh) {
    scene.remove(currentHeldMesh);
    currentHeldMesh = null;
  }

  const heightCm = Math.max(0, (highestY - (basePlateY + 0.22)) * 10);
  const finalScore = Math.floor((heightCm * 120) + (stackedCount * 300));

  // 称号判定
  let title = 'お試しミニサンド';
  if (heightCm > 80 || stackedCount >= 18) {
    title = '🌌 宇宙に届く伝説のプクムクタワー！';
  } else if (heightCm > 50 || stackedCount >= 12) {
    title = '🗼 スカイツリー級メガバーガー！';
  } else if (heightCm > 25 || stackedCount >= 6) {
    title = '🍔 ボリューム満点大繁盛バーガー！';
  } else if (stackedCount >= 3) {
    title = '🥪 なかなか見事な手作りサンド！';
  }

  // リザルト画面への反映
  document.getElementById('final-score-val').innerText = finalScore.toLocaleString();
  document.getElementById('final-height-val').innerText = `${heightCm.toFixed(1)} cm`;
  document.getElementById('final-count-val').innerText = `${stackedCount} 個`;
  document.getElementById('result-title-badge').innerText = title;

  document.getElementById('result-modal').classList.add('active');
}

// アニメーションループ
const timeStep = 1 / 60;
function animate() {
  requestAnimationFrame(animate);

  // 1. 物理演算ステップ
  world.step(timeStep);

  // 2. トングの往復移動（スマホ画面幅に合わせた振れ幅）
  tongTime += 0.035;
  tongX = Math.sin(tongTime * tongSpeed) * 0.82;

  const currentTongY = highestY + TONG_HEIGHT_OFFSET;

  // 3. トングメッシュと保持中の具材の同期
  if (tongMeshGroup) {
    tongMeshGroup.position.set(tongX, currentTongY + 0.35, 0);
  }
  if (currentHeldMesh) {
    currentHeldMesh.position.set(tongX, currentTongY, 0);
    currentHeldMesh.rotation.y = Math.sin(tongTime) * 0.25;
  }

  // 4. 落下した各具材のメッシュと剛体の同期
  activeItems.forEach(item => {
    item.mesh.position.copy(item.body.position);
    item.mesh.quaternion.copy(item.body.quaternion);
  });

  // 5. スタックおよび落下の判定
  if (isPlaying) {
    checkStackAndFalls();
  }

  // 6. カメラのスムーズ追従
  currentCameraY += (targetCameraY - currentCameraY) * 0.05;
  camera.position.y = currentCameraY;
  camera.lookAt(0, currentCameraY - 0.2, 0);

  // 7. 描画
  renderer.render(scene, camera);
}

// リサイズ
function onWindowResize() {
  const container = document.getElementById('game-container');
  const width = container.clientWidth;
  const height = container.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

// --- ボタンイベントのバインド ---
document.getElementById('start-btn').addEventListener('click', () => startGame());
document.getElementById('restart-btn').addEventListener('click', () => startGame());

const soundBtn = document.getElementById('sound-btn');
if (soundBtn) {
  soundBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    const muted = sounds.toggleMute();
    soundBtn.innerText = muted ? '🔇 消音' : '🔊 サウンド';
  });
}

// 起動
window.addEventListener('DOMContentLoaded', () => {
  initGame();
});
