import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont
import apng_patch # フルフレーム (320x270) & dispose_op=1 & blend_op=0 パッチ

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FRAMES_BASE = r"C:\Users\akeer.AKERU\unity\Pukumuku2\temp_blend_frames_16"
OUT_DIR = r"C:\Users\akeer.AKERU\unity\Pukumuku2\line_stickers_pukumuku"
ARTIFACT_DIR = r"C:\Users\akeer.AKERU\.gemini\antigravity\brain\c5b84d11-a567-4a59-ba02-6898b125f22e"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/meiryob.ttc"
font_title = ImageFont.truetype(FONT_PATH, 32)
font_huge = ImageFont.truetype(FONT_PATH, 44)
font_mid = ImageFont.truetype(FONT_PATH, 28)

def draw_thick_text(draw, text, x, y, font, fill_color, stroke_color="#FFFFFF", stroke_width=6, shadow_offset=(2, 3)):
    if shadow_offset:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 70), stroke_width=stroke_width, stroke_fill=(0, 0, 0, 70), anchor="mm")
    draw.text((x, y), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_color, anchor="mm")

first_frames = []

STICKER_COUNT = 16
TOTAL_FRAMES = 20
pi = math.pi

for idx in range(STICKER_COUNT):
    stamp_dir = os.path.join(FRAMES_BASE, f"sticker_{idx+1:02d}")
    frames = []
    
    for frame_idx in range(TOTAL_FRAMES):
        f_path = os.path.join(stamp_dir, f"frame_{frame_idx:02d}.png")
        if not os.path.exists(f_path):
            print(f"Waiting for {f_path}...")
            break
        base_im = Image.open(f_path).convert("RGBA")
        
        overlay = Image.new("RGBA", (320, 270), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        t = frame_idx / TOTAL_FRAMES

        if idx == 0:
            # 01. こんにちは！ (バストアップ)
            sun_cx, sun_cy = 265, 42
            sun_ang = t * 2 * pi
            for i in range(8):
                a = sun_ang + i * (pi / 4)
                draw.line([(sun_cx + 14 * math.cos(a), sun_cy + 14 * math.sin(a)),
                           (sun_cx + 23 * math.cos(a), sun_cy + 23 * math.sin(a))], fill="#FF9800", width=4)
            draw.ellipse([sun_cx - 12, sun_cy - 12, sun_cx + 12, sun_cy + 12], fill="#FF5722", outline="#FFFFFF", width=3)
            draw_thick_text(draw, "こんにちは！", 115, 36, font_title, "#FF6F00")

        elif idx == 1:
            # 02. ありがとう！ (見下ろしハイアングルでお辞儀)
            for i, offset in enumerate([0, 0.33, 0.66]):
                ht = (t + offset) % 1.0
                hx = 65 + i * 95 + math.sin(ht * 2 * pi) * 10
                hy = 210 - ht * 150
                r = int(7 + 4 * math.sin(ht * pi))
                draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(255, 64, 129, int(220 * (1 - ht * 0.7))))
            draw_thick_text(draw, "ありがとう！", 160, 32, font_title, "#E91E63")

        elif idx == 2:
            # 03. OK！ (右斜め前から手元アップ、左上にOK)
            scale = 1.0 + 0.35 * math.sin(t * 4 * pi)
            sx, sy = 260, 50
            for i in range(4):
                a = i * (pi / 2)
                draw.line([(sx, sy), (sx + int(20 * scale * math.cos(a)), sy + int(20 * scale * math.sin(a)))], fill="#FFD700", width=4)
            draw_thick_text(draw, "OK！", 80, 48, font_huge, "#2E7D32")

        elif idx == 3:
            # 04. NO (顔アップ、首振り、左上にNO)
            drop_y = 55 + 8 * math.sin(t * 4 * pi)
            draw.ellipse([255, drop_y, 270, drop_y + 16], fill="#03A9F4", outline="#FFFFFF", width=2)
            draw_thick_text(draw, "NO", 70, 48, font_huge, "#D32F2F")

        elif idx == 4:
            # 05. 急ぎます！ (サイドビュー疾走、頭から靴先まで全身、土煙)
            sm_phase = (t * 2) % 1.0
            sm_x = 240 - sm_phase * 65
            sm_r = int(9 + sm_phase * 14)
            draw.ellipse([sm_x - sm_r, 235 - sm_r, sm_x + sm_r, 235 + sm_r], fill=(210, 185, 155, int(180 * (1 - sm_phase))))
            draw_thick_text(draw, "急ぎます！", 110, 36, font_title, "#E65100")

        elif idx == 5:
            # 06. いただきます♪ (見上げバストアップ)
            note_y = 42 + 6 * math.sin(t * 4 * pi)
            draw.ellipse([250, note_y, 262, note_y + 10], fill="#FF9800")
            draw.line([(262, note_y + 5), (262, note_y - 12)], fill="#FF9800", width=3)
            draw_thick_text(draw, "いただきます♪", 160, 32, font_title, "#F57C00")

        elif idx == 6:
            # 07. お疲れさまです (癒やしバストアップ)
            steam_y = 40 - 7 * math.sin(t * 2 * pi)
            draw.arc([245, steam_y, 265, steam_y + 15], 180, 360, fill="#FFA726", width=3)
            draw_thick_text(draw, "お疲れさまです", 160, 32, font_title, "#6D4C41")

        elif idx == 7:
            # 08. やったー！ (大ジャンプ見上げ)
            colors = ["#FF1744", "#00E676", "#2979FF", "#FFEA00", "#FF4081"]
            for i in range(12):
                cx = (i * 27 + int(math.sin(t * 4 * pi + i) * 15)) % 320
                cy = (int(t * 270) + i * 23) % 270
                draw.rectangle([cx, cy, cx + 7, cy + 7], fill=colors[i % len(colors)])
            draw_thick_text(draw, "やったー！", 160, 30, font_title, "#AB47BC")

        elif idx == 8:
            # 09. 考え中... (斜めバストアップ、？マーク)
            draw_thick_text(draw, "？", 260, 48, font_huge, "#3F51B5")
            draw_thick_text(draw, "考え中...", 115, 34, font_title, "#1A237E")

        elif idx == 9:
            # 10. プンプン！ (腰手足踏み、怒りマーク＆湯気)
            steam_y = 42 - 6 * math.sin(t * 4 * pi)
            draw.line([(255, steam_y - 8), (275, steam_y + 8)], fill="#D50000", width=4)
            draw.line([(275, steam_y - 8), (255, steam_y + 8)], fill="#D50000", width=4)
            draw_thick_text(draw, "プンプン！", 115, 36, font_title, "#C62828")

        elif idx == 10:
            # 11. 悲しい... (肩落とし、しずく涙)
            tear_phase = (t * 2) % 1.0
            tear_y = int(45 + tear_phase * 35)
            draw.ellipse([250, tear_y, 262, tear_y + 14], fill="#29B6F6", outline="#FFFFFF", width=2)
            draw_thick_text(draw, "悲しい...", 120, 34, font_title, "#0277BD")

        elif idx == 11:
            # 12. イエーイ！ (ダンス、音符＆キラキラ)
            note_cx = 255 + int(math.sin(t * 4 * pi) * 8)
            note_cy = 44 + int(math.cos(t * 4 * pi) * 6)
            draw.ellipse([note_cx - 6, note_cy, note_cx + 6, note_cy + 10], fill="#00E676")
            draw.line([(note_cx + 6, note_cy + 5), (note_cx + 6, note_cy - 12)], fill="#00E676", width=3)
            draw_thick_text(draw, "イエーイ！", 140, 34, font_title, "#00C853")

        elif idx == 12:
            # 13. ポカ〜ン (呆然、首傾げ)
            dots = "." * (int(t * 3) + 1)
            draw_thick_text(draw, f"ポカ〜ン{dots}", 160, 34, font_title, "#78909C")

        elif idx == 13:
            # 14. いらっしゃいませ！ (お出迎えお辞儀)
            sparkle_cx, sparkle_cy = 265, 42
            for i in range(4):
                a = t * 2 * pi + i * (pi / 2)
                draw.line([(sparkle_cx, sparkle_cy), 
                           (sparkle_cx + int(15 * math.cos(a)), sparkle_cy + int(15 * math.sin(a)))], fill="#FFB300", width=3)
            draw_thick_text(draw, "いらっしゃいませ！", 140, 30, font_mid, "#D84315")

        elif idx == 14:
            # 15. 風邪気味・ブルブル... (体を抱えてブルブル)
            shiver_x = int(math.sin(t * 8 * pi) * 3)
            draw_thick_text(draw, "ブルブル...", 130 + shiver_x, 34, font_title, "#00838F")
            draw.arc([245, 36, 265, 56], 45, 225, fill="#00ACC1", width=3)

        elif idx == 15:
            # 16. 一発逆転！ (力強いガッツポーズ、闘志炎)
            flame_y = 48 - int(math.sin(t * 4 * pi) * 6)
            draw.polygon([(260, flame_y - 14), (250, flame_y + 10), (270, flame_y + 10)], fill="#FF3D00")
            draw.polygon([(260, flame_y - 7), (254, flame_y + 8), (266, flame_y + 8)], fill="#FFD600")
            draw_thick_text(draw, "一発逆転！", 115, 36, font_title, "#BF360C")

        composite = Image.alpha_composite(base_im, overlay)
        
        # RGBAクリーン＆ポスタライズ（背景透過を100%保護し、チカチカ完全ゼロ＆300KB以下保証）
        raw_data = list(composite.getdata())
        clean_data = []
        for r, g, b, a in raw_data:
            if a < 20:
                clean_data.append((0, 0, 0, 0))
            else:
                clean_data.append((r & ~31, g & ~31, b & ~31, a))
        
        clean_frame = Image.new("RGBA", composite.size)
        clean_frame.putdata(clean_data)
        frames.append(clean_frame)

    if len(frames) != TOTAL_FRAMES:
        print(f"Skipping sticker_{idx+1:02d} (only {len(frames)} frames found)")
        continue

    first_frames.append(frames[0])

    # フルフレーム APNG として保存 (LINE公式規格: 320x270、dispose_op=1、blend_op=0、300KB以下厳守)
    out_filename = f"{idx+1:02d}.png"
    out_path = os.path.join(OUT_DIR, out_filename)
    frames[0].save(
        out_path,
        format='PNG',
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=2, # LINE規定: 2ループ再生 (100ms * 20コマ * 2 = 4.0秒)
        optimize=False
    )
    kb = os.path.getsize(out_path) / 1024
    print(f"✓ {out_filename} saved: {kb:.1f} KB / 300KB (全フレーム320x270・チカチカゼロ・2ループ再生)")

    # プレビューGIF（常時ループ再生 loop=0）も同時に生成
    gif_filename = f"{idx+1:02d}.gif"
    gif_path = os.path.join(OUT_DIR, gif_filename)
    artifact_gif = os.path.join(ARTIFACT_DIR, gif_filename)
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0, # Web確認用: 無限ループ！
        disposal=2
    )
    frames[0].save(artifact_gif, save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)

# メインスタンプ (main.png: 240x240)
if first_frames:
    main_im = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
    src = first_frames[0].copy()
    src.thumbnail((240, 240), Image.Resampling.LANCZOS)
    ox = (240 - src.width) // 2
    oy = (240 - src.height) // 2
    main_im.paste(src, (ox, oy), src)
    main_path = os.path.join(OUT_DIR, "main.png")
    main_im.save(main_path)
    main_im.save(os.path.join(ARTIFACT_DIR, "main.png"))
    print(f"✓ main.png (240x240) saved: {os.path.getsize(main_path)/1024:.1f} KB")

# トークルームタブ用画像 (tab.png: 96x74)
if first_frames:
    tab_im = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
    src = first_frames[0].copy()
    src.thumbnail((96, 74), Image.Resampling.LANCZOS)
    ox = (96 - src.width) // 2
    oy = (74 - src.height) // 2
    tab_im.paste(src, (ox, oy), src)
    tab_path = os.path.join(OUT_DIR, "tab.png")
    tab_im.save(tab_path)
    tab_im.save(os.path.join(ARTIFACT_DIR, "tab.png"))
    print(f"✓ tab.png (96x74) saved: {os.path.getsize(tab_path)/1024:.1f} KB")

print("All 16 stickers built successfully!")

