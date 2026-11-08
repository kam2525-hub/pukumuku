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

const CATCH_BREAD_ASSET_ROOT = new URL('models/catch_breads/', document.currentScript.src);
const CATCH_BREAD_ASSET_VERSION = '20261109menu';

function catchBreadAsset(key, extension) {
  return new URL(`${key}.${extension}?v=${CATCH_BREAD_ASSET_VERSION}`, CATCH_BREAD_ASSET_ROOT).href;
}

const breadPowerNotes = {
  fever: '8秒間、得点2倍',
  mega_box: '8秒間、木箱が大きくなる',
  speed_up: '8秒間、移動が速くなる',
  burnt: 'コンボとフィーバーが終了'
};

for (const catalog of document.querySelectorAll('.catch-bread-grid')) {
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
  }
}
