#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
純くんの焼きたてパンキャッチ！
静的ファイル配信 & 全国オンラインランキングAPIサーバー
標準ライブラリのみで動作（追加インストール不要）
"""

import http.server
import socketserver
import json
import os
import sys
import threading
from datetime import datetime
import html

# Windowsのcp932エンコードエラー防止
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'ranking_data.json')
TOWER_DATA_FILE = os.path.join(BASE_DIR, 'tower_ranking_data.json')
DASH_DATA_FILE = os.path.join(BASE_DIR, 'dash_ranking_data.json')
lock = threading.RLock()

# 初期のプクムク常連さんランキング（にぎやかしデータ）
DEFAULT_RANKINGS = [
    {"id": "puku_init_1", "name": "神の手ベーカリー", "score": 26800, "date": "11/02 14:30"},
    {"id": "puku_init_2", "name": "パンダ店長", "score": 21500, "date": "11/02 18:15"},
    {"id": "puku_init_3", "name": "クロワッサン好き", "score": 18200, "date": "11/03 09:40"},
    {"id": "puku_init_4", "name": "看板娘みく", "score": 14900, "date": "11/03 11:20"},
    {"id": "puku_init_5", "name": "早起き食パンマン", "score": 12600, "date": "11/03 12:05"},
    {"id": "puku_init_6", "name": "メロンパン太郎", "score": 10500, "date": "11/03 13:50"},
    {"id": "puku_init_7", "name": "見習いコッペ", "score": 8800, "date": "11/03 15:10"},
    {"id": "puku_init_8", "name": "プクムク常連A", "score": 6700, "date": "11/03 16:00"},
]

# サンドイッチタワー世界ランキング初期データ（高さ cm & 純利益 ¥ 両対応）
DEFAULT_TOWER_RANKINGS = [
    {"id": "tw_init_1", "name": "伝説のバーガー職人", "score": 38400, "height": 42.5, "date": "11/08 10:15"},
    {"id": "tw_init_2", "name": "プクムク店長", "score": 29600, "height": 34.2, "date": "11/08 10:30"},
    {"id": "tw_init_3", "name": "チーズ大好き純", "score": 22400, "height": 28.6, "date": "11/08 10:45"},
    {"id": "tw_init_4", "name": "BLTマスター", "score": 18500, "height": 24.0, "date": "11/08 11:00"},
    {"id": "tw_init_5", "name": "月見バーガー姫", "score": 14200, "height": 19.5, "date": "11/08 11:10"},
    {"id": "tw_init_6", "name": "金のパティハンター", "score": 11800, "height": 16.2, "date": "11/08 11:20"},
    {"id": "tw_init_7", "name": "見習いサンドマン", "score": 8400, "height": 12.4, "date": "11/08 11:25"},
    {"id": "tw_init_8", "name": "はらぺこキッズ", "score": 5200, "height": 8.5, "date": "11/08 11:30"},
]

def deduplicate_by_name(records, key_func):
    """同一プレイヤー名（ニックネーム）の重複を完全排除し、各プレイヤーの最高記録のみ残す"""
    sorted_items = sorted(records, key=key_func, reverse=True)
    seen = set()
    unique = []
    for item in sorted_items:
        clean_name = item.get('name', '').strip()
        if not clean_name:
            continue
        if clean_name not in seen:
            seen.add(clean_name)
            unique.append(item)
    return unique

def load_tower_rankings():
    with lock:
        if not os.path.exists(TOWER_DATA_FILE):
            with open(TOWER_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_TOWER_RANKINGS, f, ensure_ascii=False, indent=2)
            return list(DEFAULT_TOWER_RANKINGS)
        try:
            with open(TOWER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return list(DEFAULT_TOWER_RANKINGS)
        except Exception:
            return list(DEFAULT_TOWER_RANKINGS)

def save_tower_score(name, score, height):
    with lock:
        rankings = load_tower_rankings()
        now = datetime.now()
        date_str = now.strftime("%m/%d %H:%M")
        clean_name = html.escape(name.strip()) or "名無しバーガー職人"
        clean_name = clean_name[:10]

        entry_id = f"tw_{int(now.timestamp() * 1000)}"
        new_entry = {
            "id": entry_id,
            "name": clean_name,
            "score": int(score),
            "height": round(float(height), 1),
            "date": date_str
        }
        rankings.append(new_entry)
        # Keep up to 60 entries
        rankings = rankings[-60:]
        with open(TOWER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, ensure_ascii=False, indent=2)

        by_score = deduplicate_by_name(rankings, lambda x: (x.get('score', 0), x.get('height', 0)))
        by_height = deduplicate_by_name(rankings, lambda x: (x.get('height', 0), x.get('score', 0)))

        score_pos = next((i + 1 for i, r in enumerate(by_score) if r.get('id') == entry_id or r.get('name') == clean_name), None)
        height_pos = next((i + 1 for i, r in enumerate(by_height) if r.get('id') == entry_id or r.get('name') == clean_name), None)

        return {
            "scoreRankings": by_score[:10],
            "heightRankings": by_height[:10],
            "currentEntry": new_entry,
            "scoreRankPosition": score_pos,
            "heightRankPosition": height_pos
        }

DEFAULT_DASH_RANKINGS = [
    {"id": "d_init_1", "name": "プクムク店長", "score": 24500, "distance": 420, "date": "11/14 09:00"},
    {"id": "d_init_2", "name": "早起きパン職人", "score": 18200, "distance": 340, "date": "11/14 09:15"},
    {"id": "d_init_3", "name": "クロワッサン好き", "score": 14800, "distance": 280, "date": "11/14 09:30"},
    {"id": "d_init_4", "name": "看板娘みく", "score": 11200, "distance": 210, "date": "11/14 10:00"},
    {"id": "d_init_5", "name": "見習いコッペ", "score": 7500, "distance": 150, "date": "11/14 10:15"},
]

def load_dash_rankings():
    with lock:
        if not os.path.exists(DASH_DATA_FILE):
            with open(DASH_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_DASH_RANKINGS, f, ensure_ascii=False, indent=2)
            return list(DEFAULT_DASH_RANKINGS)
        try:
            with open(DASH_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else list(DEFAULT_DASH_RANKINGS)
        except Exception:
            return list(DEFAULT_DASH_RANKINGS)

def save_dash_score(name, score, distance):
    with lock:
        rankings = load_dash_rankings()
        now = datetime.now()
        clean_name = html.escape(name.strip()) or "名無し職人"
        clean_name = clean_name[:12]
        entry_id = f"dash_{int(now.timestamp() * 1000)}"
        new_entry = {
            "id": entry_id,
            "name": clean_name,
            "score": int(score),
            "distance": int(distance),
            "date": now.strftime("%m/%d %H:%M")
        }
        rankings.append(new_entry)
        rankings = rankings[-60:]
        with open(DASH_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, ensure_ascii=False, indent=2)
        by_score = deduplicate_by_name(rankings, lambda x: (x.get('score', 0), x.get('distance', 0)))
        by_dist = deduplicate_by_name(rankings, lambda x: (x.get('distance', 0), x.get('score', 0)))
        return {"scoreRankings": by_score[:10], "distRankings": by_dist[:10], "currentEntry": new_entry}

def load_rankings():
    with lock:
        if not os.path.exists(DATA_FILE):
            save_rankings_internal(DEFAULT_RANKINGS)
            return list(DEFAULT_RANKINGS)
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return list(DEFAULT_RANKINGS)
        except Exception as e:
            print(f"[Error loading rankings] {e}", file=sys.stderr)
            return list(DEFAULT_RANKINGS)

def save_rankings_internal(rankings):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(rankings, f, ensure_ascii=False, indent=2)

def save_score(name, score):
    with lock:
        rankings = load_rankings()
        now = datetime.now()
        date_str = now.strftime("%m/%d %H:%M")
        
        # 安全サニタイズ & 文字数制限
        clean_name = html.escape(name.strip())
        if not clean_name:
            clean_name = "名無しパン職人"
        if len(clean_name) > 10:
            clean_name = clean_name[:10]
            
        entry_id = f"entry_{int(now.timestamp() * 1000)}"
        new_entry = {
            "id": entry_id,
            "name": clean_name,
            "score": int(score),
            "date": date_str
        }
        
        rankings.append(new_entry)
        # スコア降順、同じなら新しい順
        rankings.sort(key=lambda x: (x.get('score', 0)), reverse=True)
        # 最大保存件数は50件（データ肥大化防止）
        rankings = rankings[:50]
        
        save_rankings_internal(rankings)
        
        # 同一プレイヤー名の重複を排除（1人1枠・最高得点のみ）
        unique_rankings = deduplicate_by_name(rankings, lambda x: x.get('score', 0))
        
        # ランク（順位）の特定
        rank_pos = None
        for idx, item in enumerate(unique_rankings):
            if item.get('id') == entry_id or item.get('name') == clean_name:
                rank_pos = idx + 1
                break
                
        return {
            "rankings": unique_rankings[:10],
            "currentEntry": new_entry,
            "rankPosition": rank_pos
        }


class BakeryRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/dash_ranking'):
            rankings = load_dash_rankings()
            by_score = deduplicate_by_name(rankings, lambda x: (x.get('score', 0), x.get('distance', 0)))[:10]
            by_dist = deduplicate_by_name(rankings, lambda x: (x.get('distance', 0), x.get('score', 0)))[:10]
            payload = json.dumps({
                "status": "ok",
                "scoreRankings": by_score,
                "distRankings": by_dist
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith('/api/tower_ranking'):
            rankings = load_tower_rankings()
            by_score = deduplicate_by_name(rankings, lambda x: (x.get('score', 0), x.get('height', 0)))[:10]
            by_height = deduplicate_by_name(rankings, lambda x: (x.get('height', 0), x.get('score', 0)))[:10]
            payload = json.dumps({
                "status": "ok",
                "scoreRankings": by_score,
                "heightRankings": by_height
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith('/api/ranking'):
            rankings = load_rankings()
            top10 = deduplicate_by_name(rankings, lambda x: x.get('score', 0))[:10]
            
            payload = json.dumps({"status": "ok", "rankings": top10}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/dash_ranking'):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 10240:
                self.send_response(413)
                self.end_headers()
                return
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

            name = str(data.get('name', '名無し職人'))
            try:
                score = int(data.get('score', 0))
            except (ValueError, TypeError):
                score = 0
            try:
                distance = int(data.get('distance', 0))
            except (ValueError, TypeError):
                distance = 0
            result = save_dash_score(name, max(0, min(9999999, score)), max(0, min(99999, distance)))
            payload = json.dumps({"status": "ok", **result}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith('/api/tower_ranking'):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 10240:
                self.send_response(413)
                self.end_headers()
                return
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

            name = str(data.get('name', '名無しバーガー職人'))
            try:
                score = int(data.get('score', 0))
            except (ValueError, TypeError):
                score = 0
            try:
                height = float(data.get('height', 0.0))
            except (ValueError, TypeError):
                height = 0.0

            score = max(0, min(500000, score))
            height = max(0.0, min(500.0, height))

            result = save_tower_score(name, score, height)
            payload = json.dumps({
                "status": "ok",
                **result
            }, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith('/api/ranking'):
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 10240: # 10KB上限（DoS対策）
                self.send_response(413)
                self.end_headers()
                return

            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
            except Exception:
                self.send_response(400)
                self.end_headers()
                return

            name = str(data.get('name', '名無しパン職人'))
            try:
                score = int(data.get('score', 0))
            except (ValueError, TypeError):
                score = 0

            # スコアの妥当性バリデーション（0〜200,000円）
            score = max(0, min(200000, score))

            result = save_score(name, score)

            payload = json.dumps({
                "status": "ok",
                "rankings": result["rankings"],
                "currentEntry": result["currentEntry"],
                "rankPosition": result["rankPosition"]
            }, ensure_ascii=False).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()


class ThreadingBakeryServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True
    request_queue_size = 64

def run():
    # 静的ファイルルートを確実にスクリプトのあるディレクトリに固定
    os.chdir(BASE_DIR)
    with ThreadingBakeryServer(("", PORT), BakeryRequestHandler) as httpd:
        print(f"🍞 Bakery Server with Ranking API running on http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
