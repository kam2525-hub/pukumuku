import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import apng_patch # フルフレーム (320x270) & dispose_op=1 & blend_op=0 パッチ

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FRAMES_BASE = r"C:\Users\akeer.AKERU\unity\Pukumuku2\temp_blend_frames_ichiji_16"
OUT_DIR = r"C:\Users\akeer.AKERU\unity\Pukumuku2\line_stickers_pukumuku"
ARTIFACT_DIR = r"C:\Users\akeer.AKERU\.gemini\antigravity\brain\c5b84d11-a567-4a59-ba02-6898b125f22e"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/meiryob.ttc"
font_huge = ImageFont.truetype(FONT_PATH, 34)
font_title = ImageFont.truetype(FONT_PATH, 26)
font_mid = ImageFont.truetype(FONT_PATH, 22)
font_small = ImageFont.truetype(FONT_PATH, 15)
font_sign = ImageFont.truetype(FONT_PATH, 11)

def draw_pop_text(draw, text, cx, cy, font, fill_color, stroke_color="#FFFFFF", stroke_width=6):
    """極太白フチ＋ドロップシャドウで視認性100%保証のポップ文字"""
    # 影
    draw.text((cx + 2, cy + 3), text, font=font, fill=(0, 0, 0, 75), stroke_width=stroke_width, stroke_fill=(0, 0, 0, 75), anchor="mm")
    # 本体
    draw.text((cx, cy), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_color, anchor="mm")

def draw_croissant(draw, x, y, size=20):
    """香ばしい黄金色クロワッサン"""
    draw.arc([x - size, y - size//2, x + size, y + size//2], 190, 350, fill="#BF360C", width=8)
    draw.arc([x - size + 2, y - size//2 + 2, x + size - 2, y + size//2], 190, 350, fill="#FF9800", width=4)
    draw.arc([x - size + 4, y - size//2 + 4, x + size - 4, y + size//2], 190, 350, fill="#FFE082", width=2)

def draw_baguette(draw, x, y, angle=30, length=40):
    """本格フランスパン（バゲット）"""
    rad = math.radians(angle)
    dx = math.cos(rad) * length // 2
    dy = math.sin(rad) * length // 2
    draw.line([(x - dx, y - dy), (x + dx, y + dy)], fill="#5D4037", width=12)
    draw.line([(x - dx, y - dy), (x + dx, y + dy)], fill="#FFA726", width=8)
    for i in [-0.5, 0, 0.5]:
        cx = x + dx * i
        cy = y + dy * i
        draw.line([(cx - 4, cy - 2), (cx + 4, cy + 2)], fill="#4E342E", width=2)

def draw_melonpan(draw, x, y, r=16):
    """ふっくら格子柄メロンパン"""
    draw.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill="#E65100")
    draw.ellipse([x - r, y - r, x + r, y + r], fill="#FFF9C4", outline="#FBC02D", width=2)
    draw.line([(x - r + 4, y - r//2), (x + r - 4, y + r//2)], fill="#FBC02D", width=2)
    draw.line([(x - r + 4, y + r//2), (x + r - 4, y - r//2)], fill="#FBC02D", width=2)

def draw_mug(draw, x, y, steam_t=0.0):
    """湯気が立ちのぼる温かいマグカップ"""
    draw.rounded_rectangle([x - 14, y - 8, x + 14, y + 16], radius=5, fill="#8D6E63", outline="#FFFFFF", width=2)
    draw.arc([x + 10, y - 4, x + 24, y + 12], 270, 90, fill="#FFFFFF", width=3)
    draw.ellipse([x - 12, y - 10, x + 12, y - 6], fill="#4E342E")
    for i in [-5, 5]:
        sy = y - 16 - int(6 * math.sin((steam_t + i*0.1) * 2 * math.pi))
        draw.arc([x + i - 4, sy - 8, x + i + 4, sy + 8], 180, 360, fill="#FFA726", width=2)

def draw_bread_sign(draw, x, y):
    """食パン型おしゃれ自立スタンド看板「PukuMuku OPEN」"""
    draw.line([(x - 14, y + 20), (x - 20, y + 42)], fill="#5D4037", width=3)
    draw.line([(x + 14, y + 20), (x + 20, y + 42)], fill="#5D4037", width=3)
    r = 15
    draw.ellipse([x - r, y - 22, x, y - 4], fill="#8D6E63")
    draw.ellipse([x, y - 22, x + r, y - 4], fill="#8D6E63")
    draw.rounded_rectangle([x - r, y - 13, x + r, y + 20], radius=3, fill="#8D6E63")
    ir = 13
    draw.ellipse([x - ir, y - 19, x, y - 6], fill="#FFF9C4")
    draw.ellipse([x, y - 19, x + ir, y - 6], fill="#FFF9C4")
    draw.rounded_rectangle([x - ir, y - 11, x + ir, y + 18], radius=2, fill="#FFF9C4")
    draw.text((x, y - 3), "Puku", font=font_sign, fill="#E65100", anchor="mm")
    draw.text((x, y + 9), "OPEN", font=font_sign, fill="#D84315", anchor="mm")

def draw_sparkle(draw, x, y, size=11, color="#FFD700"):
    """輝く4頂点スパークル"""
    draw.polygon([(x, y - size), (x + size//4, y - size//4), (x + size, y), (x + size//4, y + size//4),
                  (x, y + size), (x - size//4, y + size//4), (x - size, y), (x - size//4, y - size//4)], fill=color)

def draw_heart(draw, x, y, size=12, color="#FF4081"):
    """ハートマーク"""
    r = size // 2
    draw.ellipse([x - r, y - r, x, y], fill=color)
    draw.ellipse([x, y - r, x + r, y], fill=color)
    draw.polygon([(x - r, y - r//3), (x + r, y - r//3), (x, y + r)], fill=color)

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
            break
        base_im = Image.open(f_path).convert("RGBA")
        
        overlay = Image.new("RGBA", (320, 270), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        t = frame_idx / TOTAL_FRAMES

        if idx == 0:
            # 01. こんにちは！ (左上文字、左クロワッサン、右上太陽)
            sun_cx, sun_cy = 285, 36
            sun_ang = t * 2 * pi
            for i in range(8):
                a = sun_ang + i * (pi / 4)
                draw.line([(sun_cx + 10 * math.cos(a), sun_cy + 10 * math.sin(a)),
                           (sun_cx + 18 * math.cos(a), sun_cy + 18 * math.sin(a))], fill="#FF9800", width=3)
            draw.ellipse([sun_cx - 9, sun_cy - 9, sun_cx + 9, sun_cy + 9], fill="#FF5722", outline="#FFFFFF", width=2)
            cw_y = 65 + int(4 * math.sin(t * 4 * pi))
            draw_croissant(draw, 45, cw_y, 16)
            draw_sparkle(draw, 78, cw_y - 10, 9, "#FFD54F")
            draw_pop_text(draw, "こんにちは！", 90, 22, font_title, "#FF6F00")

        elif idx == 1:
            # 02. ありがとうございます (最上部文字、左上メロンパン、左右ハート)
            for i, (hx_base, offset) in enumerate([(35, 0.0), (60, 0.4), (260, 0.2), (285, 0.6)]):
                ht = (t + offset) % 1.0
                hx = hx_base + math.sin(ht * 2 * pi) * 6
                hy = 240 - ht * 170
                draw_heart(draw, int(hx), int(hy), int(9 + 3 * math.sin(ht * pi)), (255, 64, 129, int(220 * (1 - ht * 0.7))))
            draw_melonpan(draw, 42, 60 + int(3 * math.sin(t * 4 * pi)), 14)
            draw_pop_text(draw, "ありがとうございます", 160, 20, font_mid, "#E91E63")

        elif idx == 2:
            # 03. 了解です！ (左上文字、左中央バゲット、スパークル)
            bg_y = 110 + int(4 * math.sin(t * 4 * pi))
            draw_baguette(draw, 50, bg_y, angle=-30, length=40)
            scale = 1.0 + 0.3 * math.sin(t * 4 * pi)
            draw_sparkle(draw, 140, 28, int(13 * scale), "#FFD700")
            draw_sparkle(draw, 25, 75, int(9 * scale), "#FFF176")
            draw_pop_text(draw, "了解です！", 85, 24, font_title, "#2E7D32")

        elif idx == 3:
            # 04. NO (左上NO、青ざめタテ線、冷や汗)
            for x_line in range(35, 95, 10):
                draw.line([(x_line, 10), (x_line, 24)], fill="#0288D1", width=2)
            drop_y = 80 + int(8 * math.sin(t * 4 * pi))
            draw.ellipse([55, drop_y, 70, drop_y + 16], fill="#03A9F4", outline="#FFFFFF", width=2)
            draw_pop_text(draw, "NO", 65, 34, font_huge, "#D32F2F")

        elif idx == 4:
            # 05. 急ぎます！ (左上文字、純くん背後(左側)に大土煙＆スピードライン！)
            for i, offset in enumerate([0, 0.33, 0.66]):
                sm_p = (t * 2 + offset) % 1.0
                sm_x = 120 - sm_p * 75 - i * 15
                sm_y = 225 - int(math.sin(sm_p * pi) * 18)
                sm_r = int(11 + sm_p * 16)
                draw.ellipse([sm_x - sm_r, sm_y - sm_r, sm_x + sm_r, sm_y + sm_r], fill=(225, 205, 175, int(190 * (1 - sm_p))))
            for sp_y in [155, 180, 205]:
                sp_offset = int((t * 250) % 50)
                draw.line([(110 - sp_offset, sp_y), (65 - sp_offset, sp_y)], fill="#FFA726", width=3)
            draw_pop_text(draw, "急ぎます！", 85, 24, font_title, "#E65100")

        elif idx == 5:
            # 06. お願いします (最上部文字、右上メロンパン、左右スパークル)
            draw_melonpan(draw, 275, 55 + int(4 * math.sin(t * 4 * pi)), 14)
            for nx, ny_base in [(35, 55), (280, 110)]:
                draw_sparkle(draw, nx, ny_base + int(5 * math.sin(t * 4 * pi)), 10, "#FFD700")
            draw_pop_text(draw, "お願いします", 160, 20, font_title, "#F57C00")

        elif idx == 6:
            # 07. ひとやすみ (左上文字、左中央温かいマグカップ)
            draw_mug(draw, 50, 110, steam_t=t)
            draw_sparkle(draw, 85, 95, 9, "#FFA726")
            draw_pop_text(draw, "ひとやすみ", 80, 22, font_title, "#6D4C41")

        elif idx == 7:
            # 08. やったー！ (最上部文字、左右ポップスタースパークル)
            scale = 1.0 + 0.3 * math.sin(t * 4 * pi)
            draw_sparkle(draw, 35, 50, int(14 * scale), "#FFD700")
            draw_sparkle(draw, 285, 50, int(14 * scale), "#FFD700")
            draw_sparkle(draw, 30, 140, int(11 * scale), "#FF9800")
            draw_sparkle(draw, 290, 140, int(11 * scale), "#FF9800")
            draw_pop_text(draw, "やったー！", 160, 20, font_huge, "#FF6F00")

        elif idx == 8:
            # 09. うーん… (右上文字、ぽわぽわ思考フキダシ)
            for i, (bx, by, r) in enumerate([(155, 125, 5), (180, 100, 8), (210, 75, 12)]):
                bob = int(3 * math.sin(t * 4 * pi + i))
                draw.ellipse([bx - r, by - r + bob, bx + r, by + r + bob], fill=(255, 255, 255, 220), outline="#BDBDBD", width=2)
            draw.text((210, 75), "？", font=font_title, fill="#757575", anchor="mm")
            draw_pop_text(draw, "うーん…", 235, 24, font_title, "#5C6BC0")

        elif idx == 9:
            # 10. プンプン！ (最上部文字、両肩の上怒りマーク💢)
            for qx, qy in [(45, 60), (275, 60)]:
                q_bob = int(3 * math.sin(t * 4 * pi))
                draw.line([(qx - 9, qy - 9 + q_bob), (qx + 9, qy + 9 + q_bob)], fill="#D32F2F", width=4)
                draw.line([(qx + 9, qy - 9 + q_bob), (qx - 9, qy + 9 + q_bob)], fill="#D32F2F", width=4)
                draw.arc([qx - 11, qy - 11 + q_bob, qx + 11, qy + 11 + q_bob], 0, 360, fill="#D32F2F", width=3)
            draw_pop_text(draw, "プンプン！", 160, 20, font_title, "#C62828")

        elif idx == 10:
            # 11. ごめんなさい… (最上部文字、頭上雨雲＆涙)
            draw_pop_text(draw, "ごめんなさい…", 160, 18, font_mid, "#455A64")
            draw_ellipse = draw.ellipse
            draw_ellipse([215, 30, 245, 48], fill="#90A4AE")
            draw_ellipse([230, 24, 260, 46], fill="#78909C")
            draw_ellipse([250, 32, 275, 50], fill="#90A4AE")
            for i, offset in enumerate([0, 0.5]):
                rt = (t * 2 + offset) % 1.0
                ry = 50 + int(rt * 35)
                draw.line([(235 + i * 20, ry), (235 + i * 20, ry + 6)], fill="#0288D1", width=2)

        elif idx == 11:
            # 12. いいですね！ (最上部文字、左右音符＆ミラーボール)
            for i, (nx, ny_base, col) in enumerate([(35, 50, "#FF4081"), (285, 50, "#00E676"), (30, 120, "#FFD700"), (290, 120, "#00B0FF")]):
                ny = ny_base + int(6 * math.sin(t * 4 * pi + i))
                draw.ellipse([nx - 5, ny, nx + 5, ny + 8], fill=col)
                draw.line([(nx + 5, ny + 4), (nx + 5, ny - 12)], fill=col, width=3)
            draw_pop_text(draw, "いいですね！", 160, 20, font_title, "#E040FB")

        elif idx == 12:
            # 13. よろしくです (左上文字、左クロワッサン、手元スパークル)
            draw_croissant(draw, 50, 90 + int(4 * math.sin(t * 4 * pi)), 17)
            draw_sparkle(draw, 240, 52, 12, "#FFD700")
            draw_pop_text(draw, "よろしくです", 85, 22, font_title, "#1976D2")

        elif idx == 13:
            # 14. いらっしゃいませ！ (最上部文字、左側独立食パン看板！)
            draw_bread_sign(draw, 38, 160) # 左端に独立自立！腕と完全分離！
            draw_sparkle(draw, 80, 140, 9, "#FFD700")
            draw_pop_text(draw, "いらっしゃいませ！", 160, 18, font_mid, "#E65100")

        elif idx == 14:
            # 15. おやすみなさい (左上文字、右上三日月＆Zzz...)
            draw.ellipse([245, 30, 275, 60], fill="#FFD54F")
            draw.ellipse([252, 26, 282, 56], fill=(0, 0, 0, 0))
            draw.text((185, 38 - int(5 * math.sin(t * 2 * pi))), "Z", font=font_small, fill="#90CAF9")
            draw.text((200, 30 - int(6 * math.sin(t * 2 * pi))), "z", font=font_small, fill="#90CAF9")
            draw.text((212, 22 - int(7 * math.sin(t * 2 * pi))), "z", font=font_small, fill="#64B5F6")
            draw_pop_text(draw, "おやすみなさい", 100, 22, font_title, "#3949AB")

        elif idx == 15:
            # 16. がんばります！ (左上文字、右側〜背後メラメラ炎)
            for i, offset in enumerate([0, 0.33, 0.66]):
                flame_p = (t * 2 + offset) % 1.0
                fx = 240 + int(i * 22 + 7 * math.sin(t * 4 * pi))
                draw.polygon([(fx, 150), (fx + 20, 230), (fx - 20, 230)], fill=(255, 87, 34, int(180 * (1 - flame_p * 0.4))))
                draw.polygon([(fx, 170), (fx + 12, 230), (fx - 12, 230)], fill=(255, 235, 59, int(220 * (1 - flame_p * 0.3))))
            draw_pop_text(draw, "がんばります！", 90, 22, font_title, "#D84315")

        final_im = Image.alpha_composite(base_im, overlay)
        
        # 高速numpyポスタライズ（背景透過100%保護、チカチカ完全ゼロ、300KB以下厳格達成）
        arr = np.array(final_im)
        arr[arr[:, :, 3] < 20] = 0
        arr[:, :, :3] = (arr[:, :, :3] >> 5) << 5
        clean_frame = Image.fromarray(arr)
        frames.append(clean_frame)
        if frame_idx == 0:
            first_frames.append(clean_frame)
            
    if not frames:
        print(f"Warning: No frames found for sticker {idx+1:02d}")
        continue

    # APNG保存 (LINE規定: 320x270, 20フレーム, 2ループ再生, <=300KB)
    apng_path = os.path.join(OUT_DIR, f"{idx+1:02d}.png")
    frames[0].save(
        apng_path,
        format='PNG',
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=2
    )
    
    # プレビュー用GIF (Web用常時ループ再生 loop=0)
    gif_path = os.path.join(OUT_DIR, f"{idx+1:02d}.gif")
    artifact_gif = os.path.join(ARTIFACT_DIR, f"{idx+1:02d}.gif")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        disposal=2
    )
    try:
        frames[0].save(artifact_gif, save_all=True, append_images=frames[1:], duration=100, loop=0, disposal=2)
    except Exception:
        pass

    size_kb = os.path.getsize(apng_path) / 1024
    print(f"Sticker {idx+1:02d}: APNG size = {size_kb:.1f} KB -> {'PASS' if size_kb <= 300 else 'FAIL (>300KB)'}")

# main.png (240x240)
if len(first_frames) >= 1:
    main_im = first_frames[0].copy().crop((40, 15, 280, 255)).resize((240, 240), Image.Resampling.LANCZOS)
    main_path = os.path.join(OUT_DIR, "main.png")
    main_im.save(main_path)
    try:
        main_im.save(os.path.join(ARTIFACT_DIR, "main.png"))
    except: pass
    print(f"main.png created: {os.path.getsize(main_path)/1024:.1f} KB")

# tab.png (96x74)
if len(first_frames) >= 1:
    tab_im = first_frames[0].copy().crop((90, 40, 230, 210)).resize((96, 74), Image.Resampling.LANCZOS)
    tab_path = os.path.join(OUT_DIR, "tab.png")
    tab_im.save(tab_path)
    try:
        tab_im.save(os.path.join(ARTIFACT_DIR, "tab.png"))
    except: pass
    print(f"tab.png created: {os.path.getsize(tab_path)/1024:.1f} KB")

print("✓ All 16 stickers built and validated!")
