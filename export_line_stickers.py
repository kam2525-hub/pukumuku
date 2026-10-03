import os
import io
import sys
import base64
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"C:\Users\akeer.AKERU\unity\Pukumuku2"
OUT_DIR = os.path.join(WORKSPACE_DIR, "line_stickers_pukumuku")
os.makedirs(OUT_DIR, exist_ok=True)

print(f"=== LINE公式アニメーションスタンプ 自動生成パイプライン ===", flush=True)
print(f"作業ディレクトリ: {WORKSPACE_DIR}", flush=True)
print(f"出力先フォルダ: {OUT_DIR}", flush=True)

# 空きポートを探す
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

port = find_free_port()

class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE_DIR, **kwargs)
    def log_message(self, format, *args):
        pass # 静音化

httpd = HTTPServer(('127.0.0.1', port), QuietHandler)
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
print(f"✓ ローカルWebサーバー起動完了: http://127.0.0.1:{port}", flush=True)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}", flush=True))
        page.on("pageerror", lambda err: print(f"[Browser PageError] {err}", flush=True))
        
        url = f"http://127.0.0.1:{port}/stamp_generator.html"
        print(f"スタンプレンダラーに接続中: {url}", flush=True)
        page.goto(url)
        
        # 3Dモデル読み込み完了を待機
        print("3Dモデルとテクスチャの読み込み待機中...", flush=True)
        for _ in range(30):
            err = page.evaluate("() => window.modelLoadError")
            if err:
                raise RuntimeError(f"3Dモデルのロード失敗: {err}")
            ready = page.evaluate("() => window.isModelReady === true")
            if ready:
                break
            time.sleep(1)
        else:
            raise TimeoutError("3Dモデルの読み込みがタイムアウトしました。")
            
        print("✓ 3Dモデル準備完了！レンダリングを開始します。", flush=True)

        stamp_names = [
            "01_hello (こんにちは！)",
            "02_thankyou (ありがとう！)",
            "03_ok (OK！)",
            "04_no (NO)",
            "05_hurry (急ぎます！)",
            "06_itadakimasu (いただきます)",
            "07_otsukare (お疲れさまです)",
            "08_yatta (やったー！)"
        ]

        first_frames = []

        for idx in range(8):
            name = stamp_names[idx]
            print(f"\n[{idx+1}/8] {name} をレンダリング中...")
            
            # 20フレームを一括生成
            b64_list = page.evaluate("(idx) => window.renderAllFramesForSticker(idx)", idx)
            
            images = []
            for b64 in b64_list:
                header, data = b64.split(',', 1)
                raw = base64.b64decode(data)
                im = Image.open(io.BytesIO(raw)).convert('RGBA')
                images.append(im)
                
            first_frames.append(images[0])
            
            # LINE公式指定ファイル名: 01.png ~ 08.png
            out_filename = f"{idx+1:02d}.png"
            out_path = os.path.join(OUT_DIR, out_filename)
            
            # APNGとして保存（2秒 / 10fps / loop=2）
            # LINEの規定: 再生時間は1〜4秒の整数。ここでは2秒のアニメーションを2回ループして計4秒。
            images[0].save(
                out_path,
                format='PNG',
                save_all=True,
                append_images=images[1:],
                duration=100, # 100ms / frame = 10fps
                loop=2,       # 2回ループ = 4.0秒（LINE規定上限以内）
                optimize=True
            )
            
            file_size_kb = os.path.getsize(out_path) / 1024
            print(f"  ✓ {out_filename} 保存完了: {file_size_kb:.1f} KB / 300KB (W320 x H270, 20フレーム, 2秒ループ×2)")
            if file_size_kb > 300:
                print(f"  ⚠️ 警告: 容量が300KBを超えています！")

        # メイン画像 (main.png: W240 x H240) の生成
        print("\n[メイン画像 main.png] を生成中 (240x240 px)...")
        main_im = first_frames[0].copy() # 01_hello の第1フレームを使用
        # 320x270 から中央 240x240 をクロップ
        crop_x = (320 - 240) // 2
        crop_y = (270 - 240) // 2
        main_im = main_im.crop((crop_x, crop_y, crop_x + 240, crop_y + 240))
        main_path = os.path.join(OUT_DIR, "main.png")
        main_im.save(main_path, format='PNG', optimize=True)
        print(f"  ✓ main.png 保存完了: {os.path.getsize(main_path)/1024:.1f} KB (W240 x H240)")

        # トークルームタブ画像 (tab.png: W96 x H74) の生成
        print("\n[トークルームタブ画像 tab.png] を生成中 (96x74 px)...")
        # 純くんの顔のアップを 96x74 に切り抜き＆縮小
        tab_src = first_frames[0].copy()
        # 純くんの顔付近 (中央左)
        face_box = (40, 40, 200, 164) # 160 x 124 (約96:74比率)
        tab_im = tab_src.crop(face_box).resize((96, 74), Image.Resampling.LANCZOS)
        tab_path = os.path.join(OUT_DIR, "tab.png")
        tab_im.save(tab_path, format='PNG', optimize=True)
        print(f"  ✓ tab.png 保存完了: {os.path.getsize(tab_path)/1024:.1f} KB (W96 x H74)")

        browser.close()

    print("\n🎉 全スタンプパッケージの生成が正常に完了しました！")

finally:
    httpd.shutdown()
    print("✓ ローカルWebサーバーを停止しました。")
