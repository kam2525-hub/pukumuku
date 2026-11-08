const BREAD_TYPES = {
  bread_croissant: { name: "クロワッサン", score: 200, scale: 0.22, towerScale: 0.15, speed: 4.0, prob: 0.13 },
  bread_melon: { name: "メロンパン", score: 300, scale: 0.26, towerScale: 0.16, speed: 3.8, prob: 0.13 },
  bread_cream: { name: "クリームパン", score: 250, scale: 0.26, towerScale: 0.16, speed: 3.7, prob: 0.12 },
  bread_burger: { name: "プクムクバーガー", score: 350, scale: 0.26, towerScale: 0.15, speed: 3.9, prob: 0.11 },
  bread_egg: { name: "たまごパン", score: 280, scale: 0.26, towerScale: 0.16, speed: 3.8, prob: 0.11, power: "fever" },
  bread_mushroom: { name: "きのこパン", score: 260, scale: 0.26, towerScale: 0.16, speed: 3.7, prob: 0.10, power: "mega_box" },
  bread_negi: { name: "ねぎパン", score: 240, scale: 0.26, towerScale: 0.16, speed: 3.9, prob: 0.10, power: "speed_up" },
  bread_cocoa: { name: "ココアパン", score: 270, scale: 0.26, towerScale: 0.16, speed: 3.6, prob: 0.09 },
  bread_gold: { name: "金のプクムクパン", score: 1000, scale: 0.38, towerScale: 0.24, speed: 4.8, prob: 0.04 },
  bread_cream_melon: { name: "クリームメロン", score: 330, scale: 0.27, towerScale: 0.16, speed: 3.8, prob: 0.075 },
  bread_potato: { name: "じゃがいもぱん", score: 290, scale: 0.27, towerScale: 0.16, speed: 3.8, prob: 0.075 },
  bread_chocolate: { name: "チョコぱん", score: 310, scale: 0.27, towerScale: 0.16, speed: 4.0, prob: 0.075 },
  bread_pumpkin: { name: "かぼちゃモンブラン", score: 370, scale: 0.27, towerScale: 0.16, speed: 3.7, prob: 0.075 },
  bread_sweet_potato: { name: "さつまいもぱん", score: 300, scale: 0.27, towerScale: 0.16, speed: 3.9, prob: 0.075 },
  bread_burnt: { name: "コゲパン", score: -100, scale: 0.28, towerScale: 0.18, speed: 4.3, prob: 0.07, power: "burnt" }
};

// 添付の手描きメニューを参考に造形したオリジナルモデル。ゲーム内得点は実際の価格ではない。
const MENU_BREADS = [
  ['bread_shokupan', '食ぱん'],
  ['bread_raisin_shokupan', 'レーズン食ぱん'],
  ['bread_petit_roll', 'プチロール'],
  ['bread_petit_an', 'プチあん'],
  ['bread_petit_cheese', 'プチチーズ'],
  ['bread_wiener_croissant', 'ウインナークロワッサン'],
  ['bread_tomato', 'トマトぱん'],
  ['bread_curry', 'カレーパン'],
  ['bread_cheese_corn', 'チーズコーンマヨ'],
  ['bread_corn_mayo', 'コーンマヨネーズ'],
  ['bread_egg_salad', 'たまごサラダ'],
  ['bread_yakisoba', 'やきそばぱん'],
  ['bread_gratin', 'グラタン'],
  ['bread_choco_danish', 'チョコデニッシュ'],
  ['bread_apple_danish', 'りんごデニッシュ'],
  ['bread_sweet_potato_montblanc', 'さつまいもモンブラン'],
  ['bread_bacon_egg_pie', 'ベーコンエッグパイ'],
  ['bread_mexican', 'メキシカンぱん'],
  ['bread_cinnamon_apple', 'シナモンアップル'],
  ['bread_pumpkin_bun', 'かぼちゃぱん'],
  ['bread_koshian', 'こしあんぱん'],
  ['bread_shrimp_avocado', 'えびアボカドのグラタン'],
  ['bread_tuna', 'ツナぱん'],
  ['bread_broccoli_pizza', 'ブロッコリーピザ'],
  ['bread_fish_burger', 'さばかつバーガー'],
  ['bread_ginger_burger', 'しょうがバーガー'],
  ['bread_teriyaki_burger', 'てりやきバーガー'],
  ['bread_cheese_burger', 'チーズバーガー'],
  ['bread_choco_cream', 'チョコクリーム'],
  ['bread_lemon', 'レモンぱん'],
  ['bread_fruit_cheese', 'フルーツチーズ'],
  ['bread_nandai_raisin', '南台レーズンサンド'],
  ['bread_raisin_caramel_danish', 'レーズンキャラメルデニッシュ'],
  ['bread_salt_anko', '塩あんぱん'],
  ['bread_frog_matcha', 'カエルまっちゃビスケット'],
  ['bread_panda_choco', 'パンダチョコビスケット']
];
for (const [key, name] of MENU_BREADS) {
  BREAD_TYPES[key] = { name, score: 220 + (Object.keys(BREAD_TYPES).length % 7) * 20,
    scale: 0.27, towerScale: 0.16, speed: 3.8, prob: 0.042 };
}

// 同じ効果でもパンの見た目と具材から連想できる組み合わせにする。
const BREAD_POWER_GROUPS = {
  fever: ['bread_egg', 'bread_cream_melon', 'bread_egg_salad', 'bread_bacon_egg_pie'],
  mega_box: ['bread_mushroom', 'bread_shokupan', 'bread_petit_cheese'],
  speed_up: ['bread_negi', 'bread_croissant', 'bread_petit_roll', 'bread_wiener_croissant', 'bread_ginger_burger'],
  time: ['bread_melon', 'bread_pumpkin', 'bread_sweet_potato', 'bread_apple_danish',
    'bread_sweet_potato_montblanc', 'bread_cinnamon_apple', 'bread_pumpkin_bun',
    'bread_lemon', 'bread_fruit_cheese'],
  shield: ['bread_potato', 'bread_raisin_shokupan', 'bread_curry'],
  slow_fall: ['bread_gratin', 'bread_frog_matcha', 'bread_broccoli_pizza'],
  combo: ['bread_burger', 'bread_tomato', 'bread_cheese_corn', 'bread_corn_mayo',
    'bread_yakisoba', 'bread_mexican', 'bread_shrimp_avocado', 'bread_tuna',
    'bread_fish_burger', 'bread_teriyaki_burger', 'bread_cheese_burger'],
  bonus: ['bread_cream', 'bread_cocoa', 'bread_chocolate', 'bread_petit_an',
    'bread_choco_danish', 'bread_koshian', 'bread_choco_cream', 'bread_nandai_raisin',
    'bread_raisin_caramel_danish', 'bread_salt_anko', 'bread_panda_choco'],
  jackpot: ['bread_gold'],
  burnt: ['bread_burnt']
};
for (const [power, keys] of Object.entries(BREAD_POWER_GROUPS)) {
  for (const key of keys) BREAD_TYPES[key].power = power;
}

const CATCH_BREAD_ASSET_ROOT = new URL('models/catch_breads/', document.currentScript.src);
const CATCH_BREAD_ASSET_VERSION = '20261109allmenu';

function catchBreadAsset(key, extension) {
  return new URL(`${key}.${extension}?v=${CATCH_BREAD_ASSET_VERSION}`, CATCH_BREAD_ASSET_ROOT).href;
}

const breadPowerNotes = {
  fever: '8秒間、得点2倍',
  mega_box: '8秒間、木箱が大きくなる',
  speed_up: '8秒間、移動が速くなる',
  time: '残り時間+1秒（合計+8秒まで）',
  shield: '次のコゲパンを1回防ぐ',
  slow_fall: '6秒間、パンがゆっくり落ちる',
  combo: 'コンボが2つ進む',
  bonus: 'おまけの純利益+¥60',
  jackpot: '1個で¥1,000の高得点',
  burnt: 'コンボとフィーバーが終了。お守りで防げる'
};

for (const catalog of document.querySelectorAll('.catch-bread-grid')) {
  const search = catalog.closest('.modal-card')?.querySelector('.catch-bread-search');
  const cards = [];
  for (const [key, bread] of Object.entries(BREAD_TYPES)) {
    const card = document.createElement('li');
    card.className = 'catch-bread-entry';
    const photo = document.createElement('img');
    photo.src = catchBreadAsset(key, 'webp');
    photo.alt = '';
    photo.width = 320;
    photo.height = 320;
    photo.decoding = 'async';

    const name = document.createElement('strong');
    name.textContent = bread.name;
    const score = document.createElement('span');
    score.className = bread.score < 0 ? 'catch-bread-score penalty' : 'catch-bread-score';
    score.textContent = `${bread.score < 0 ? '−' : '+'}¥${Math.abs(bread.score).toLocaleString('ja-JP')}`;

    card.append(photo, name, score);
    if (bread.power) {
      const note = document.createElement('small');
      note.textContent = breadPowerNotes[bread.power];
      card.append(note);
    }
    catalog.append(card);
    cards.push([card, bread.name]);
  }
  search?.addEventListener('input', () => {
    const query = search.value.trim().toLocaleLowerCase('ja-JP');
    for (const [card, name] of cards) card.hidden = !name.toLocaleLowerCase('ja-JP').includes(query);
  });
}
