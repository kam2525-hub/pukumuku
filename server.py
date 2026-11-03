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
        
        # ランク（順位）の特定
        rank_pos = None
        for idx, item in enumerate(rankings):
            if item.get('id') == entry_id:
                rank_pos = idx + 1
                break
                
        return {
            "rankings": rankings[:10],
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
        if self.path.startswith('/api/ranking'):
            rankings = load_rankings()
            rankings.sort(key=lambda x: x.get('score', 0), reverse=True)
            top10 = rankings[:10]
            
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


def run():
    socketserver.TCPServer.allow_reuse_address = True
    # 静的ファイルルートを確実にスクリプトのあるディレクトリに固定
    os.chdir(BASE_DIR)
    with socketserver.TCPServer(("", PORT), BakeryRequestHandler) as httpd:
        print(f"🍞 Bakery Server with Ranking API running on http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
