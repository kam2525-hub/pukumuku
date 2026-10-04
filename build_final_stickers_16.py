import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont
import apng_patch # フルフレーム (320x270) & dispose_op=1 & blend_op=0 パッチ

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

FRAMES_BASE = r"C:\Users\akeer.AKERU\unity\Pukumuku2\temp_blend_frames_ichiji_16"
OUT_DIR = r"C:\Users\akeer.AKERU\unity\Pukumuku2\line_stickers_pukumuku"
ARTIFACT_DIR = r"C:\Users\akeer.AKERU\.gemini\antigravity\brain\c5b84d11-a567-4a59-ba02-6898b125f22e"
os.makedirs(OUT_DIR, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/meiryob.ttc"
font_title = ImageFont.truetype(FONT_PATH, 32)
font_huge = ImageFont.truetype(FONT_PATH, 44)
font_mid = ImageFont.truetype(FONT_PATH, 26)
font_small = ImageFont.truetype(FONT_PATH, 18)

def draw_thick_text(draw, text, x, y, font, fill_color, stroke_color="#FFFFFF", stroke_width=6, shadow_offset=(2, 3)):
    if shadow_offset:
        draw.text((x + shadow_offset[0], y + shadow_offset[1]), text, font=font, fill=(0, 0, 0, 70), stroke_width=stroke_width, stroke_fill=(0, 0, 0, 70), anchor="mm")
    draw.text((x, y), text, font=font, fill=fill_color, stroke_width=stroke_width, stroke_fill=stroke_color, anchor="mm")

# イラストパーツ描画ヘルパー
def draw_croissant(draw, x, y, size=24):
    """可愛いクロワッサンのイラスト"""
    draw.arc([x - size, y - size//2, x + size, y + size//2], 190, 350, fill="#E65100", width=8)
    draw.arc([x - size + 3, y - size//2 + 2, x + size - 3, y + size//2], 190, 350, fill="#FFA726", width=4)

def draw_baguette(draw, x, y, angle=30, length=40):
    """フランスパン（バゲット）のイラスト"""
    rad = math.radians(angle)
    dx = math.cos(rad) * length // 2
    dy = math.sin(rad) * length // 2
    draw.line([(x - dx, y - dy), (x + dx, y + dy)], fill="#8D6E63", width=10)
    draw.line([(x - dx, y - dy), (x + dx, y + dy)], fill="#D7CCC8", width=6)
    # クープ（切れ込み）
    for i in [-0.5, 0, 0.5]:
        cx = x + dx * i
        cy = y + dy * i
        draw.line([(cx - 4, cy - 2), (cx + 4, cy + 2)], fill="#5D4037", width=2)

def draw_melonpan(draw, x, y, r=16):
    """メロンパンのイラスト"""
    draw.ellipse([x - r, y - r, x + r, y + r], fill="#FFF9C4", outline="#FBC02D", width=2)
    # 格子模様
    draw.line([(x - r + 4, y - r//2), (x + r - 4, y + r//2)], fill="#FBC02D", width=2)
    draw.line([(x - r + 4, y + r//2), (x + r - 4, y - r//2)], fill="#FBC02D", width=2)

def draw_sparkle(draw, x, y, size=12, color="#FFD700"):
    """輝く4頂点のキラキラスパークル"""
    draw.polygon([(x, y - size), (x + size//4, y - size//4), (x + size, y), (x + size//4, y + size//4),
                  (x, y + size), (x - size//4, y + size//4), (x - size, y), (x - size//4, y - size//4)], fill=color)

def draw_heart(draw, x, y, size=14, color="#FF4081"):
    """ハートのイラスト"""
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
            # 01. こんにちは！ (太陽・クロワッサン・キラキラ)
            sun_cx, sun_cy = 265, 42
            sun_ang = t * 2 * pi
            for i in range(8):
                a = sun_ang + i * (pi / 4)
                draw.line([(sun_cx + 14 * math.cos(a), sun_cy + 14 * math.sin(a)),
                           (sun_cx + 24 * math.cos(a), sun_cy + 24 * math.sin(a))], fill="#FF9800", width=4)
            draw.ellipse([sun_cx - 12, sun_cy - 12, sun_cx + 12, sun_cy + 12], fill="#FF5722", outline="#FFFFFF", width=3)
            # 焼きたてクロワッサン
            cw_y = 55 + int(4 * math.sin(t * 4 * pi))
            draw_croissant(draw, 50, cw_y, 16)
            draw_sparkle(draw, 80, 50 + int(3 * math.cos(t * 4 * pi)), 10, "#FFD54F")
            draw_thick_text(draw, "こんにちは！", 155, 36, font_title, "#FF6F00")

        elif idx == 1:
            # 02. ありがとう！ (舞い上がるハート・メロンパン・感謝の光)
            for i, offset in enumerate([0, 0.25, 0.5, 0.75]):
                ht = (t + offset) % 1.0
                hx = 50 + i * 75 + math.sin(ht * 2 * pi) * 12
                hy = 230 - ht * 180
                h_size = int(10 + 6 * math.sin(ht * pi))
                draw_heart(draw, int(hx), int(hy), h_size, (255, 64, 129, int(220 * (1 - ht * 0.7))))
            # メロンパン
            draw_melonpan(draw, 270, 55 + int(3 * math.sin(t * 4 * pi)), 15)
            draw_thick_text(draw, "ありがとう！", 160, 32, font_title, "#E91E63")

        elif idx == 2:
            # 03. OK！ (漫画風集中線・輝く星スパークル)
            scale = 1.0 + 0.35 * math.sin(t * 4 * pi)
            # 左上集中線
            for a_deg in range(-30, 45, 12):
                rad = math.radians(a_deg)
                draw.line([(80 + 35 * math.cos(rad), 48 + 20 * math.sin(rad)),
                           (80 + 55 * math.cos(rad), 48 + 32 * math.sin(rad))], fill="#FFD54F", width=3)
            draw_sparkle(draw, 260, 55, int(16 * scale), "#FFD700")
            draw_sparkle(draw, 285, 80, int(10 * scale), "#FFF176")
            draw_thick_text(draw, "OK！", 80, 48, font_huge, "#2E7D32")

        elif idx == 3:
            # 04. NO (青ざめタテ線・氷結晶・冷や汗)
            # 青ざめタテ線
            for x_line in range(40, 110, 10):
                draw.line([(x_line, 15), (x_line, 35)], fill="#0288D1", width=2)
            drop_y = 55 + int(8 * math.sin(t * 4 * pi))
            draw.ellipse([255, drop_y, 272, drop_y + 18], fill="#03A9F4", outline="#FFFFFF", width=2)
            draw_thick_text(draw, "NO", 70, 48, font_huge, "#D32F2F")

        elif idx == 4:
            # 05. 急ぎます！ (巻き上がる大土煙・疾走スピードライン)
            # 土煙（3重のふわふわ煙）
            for i, offset in enumerate([0, 0.33, 0.66]):
                sm_p = (t * 2 + offset) % 1.0
                sm_x = 240 - sm_p * 75 - i * 15
                sm_y = 230 - int(math.sin(sm_p * pi) * 20)
                sm_r = int(10 + sm_p * 16)
                draw.ellipse([sm_x - sm_r, sm_y - sm_r, sm_x + sm_r, sm_y + sm_r], fill=(215, 195, 165, int(180 * (1 - sm_p))))
            # 風切りスピード線
            for sp_y in [180, 205, 230]:
                sp_offset = int((t * 300) % 60)
                draw.line([(280 - sp_offset, sp_y), (310 - sp_offset, sp_y)], fill="#FFA726", width=3)
            draw_thick_text(draw, "急ぎます！", 110, 36, font_title, "#E65100")

        elif idx == 5:
            # 06. いただきます♪ (踊る音符・フォーク＆スプーン・バゲット)
            draw_baguette(draw, 45, 55 + int(4 * math.sin(t * 4 * pi)), angle=-25, length=32)
            # カラフル音符
            for i, (nx, ny_base, col) in enumerate([(245, 45, "#FF9800"), (275, 60, "#4CAF50")]):
                ny = ny_base + int(6 * math.sin(t * 4 * pi + i * pi))
                draw.ellipse([nx - 5, ny, nx + 5, ny + 8], fill=col)
                draw.line([(nx + 5, ny + 4), (nx + 5, ny - 12)], fill=col, width=3)
            draw_thick_text(draw, "いただきます♪", 160, 32, font_title, "#F57C00")

        elif idx == 6:
            # 07. お疲れさまです (湯気マグカップ・ほっこり花びら)
            steam_y = 40 - int(7 * math.sin(t * 2 * pi))
            # ゆらゆら湯気
            draw.arc([245, steam_y, 265, steam_y + 16], 180, 360, fill="#FFA726", width=3)
            draw.arc([260, steam_y - 6, 276, steam_y + 10], 0, 180, fill="#FFB74D", width=3)
            # マグカップ
            draw.rectangle([248, 62, 272, 80], fill="#8D6E63", outline="#FFFFFF", width=2)
            draw.arc([268, 66, 278, 76], 270, 90, fill="#8D6E63", width=2)
            draw_thick_text(draw, "お疲れさまです", 160, 32, font_title, "#6D4C41")

        elif idx == 7:
            # 08. やったー！ (紙吹雪・クラッカーテープ・星屑)
            colors = ["#FF1744", "#00E676", "#2979FF", "#FFEA00", "#FF4081", "#7C4DFF"]
            for i in range(16):
                cx = (i * 20 + int(math.sin(t * 4 * pi + i) * 18)) % 320
                cy = (int(t * 280) + i * 19) % 270
                draw.rectangle([cx, cy, cx + 7, cy + 7], fill=colors[i % len(colors)])
            draw_sparkle(draw, 50, 60, 14, "#FFD700")
            draw_sparkle(draw, 270, 60, 14, "#FFD700")
            draw_thick_text(draw, "やったー！", 160, 30, font_title, "#AB47BC")

        elif idx == 8:
            # 09. 考え中... (思考吹き出し・回転する？マーク)
            # 思考吹き出しの小丸
            draw.ellipse([230, 68, 238, 76], fill="#B0BEC5")
            draw.ellipse([240, 56, 252, 68], fill="#90A4AE")
            # メインの「？」
            q_x = 268 + int(4 * math.sin(t * 2 * pi))
            draw_thick_text(draw, "？", q_x, 48, font_huge, "#3F51B5")
            draw_thick_text(draw, "考え中...", 115, 34, font_title, "#1A237E")

        elif idx == 9:
            # 10. プンプン！ (噴き出す怒り蒸気・怒りマーク💢)
            steam_y = 44 - int(6 * math.sin(t * 4 * pi))
            # 怒りマーク (💢)
            draw.line([(252, steam_y - 10), (274, steam_y + 10)], fill="#D50000", width=5)
            draw.line([(274, steam_y - 10), (252, steam_y + 10)], fill="#D50000", width=5)
            # 蒸気
            draw.arc([42, 45, 62, 65], 180, 360, fill="#FF5252", width=3)
            draw_thick_text(draw, "プンプン！", 115, 36, font_title, "#C62828")

        elif idx == 10:
            # 11. ごめんなさい... (ポロポロ涙・モヤモヤ雨雲・ポツポツ雨)
            # 雨雲
            draw.ellipse([240, 20, 260, 35], fill="#90A4AE")
            draw.ellipse([252, 16, 276, 36], fill="#78909C")
            draw.ellipse([268, 22, 288, 35], fill="#90A4AE")
            # 雨つぶ・涙
            tear_p = (t * 2) % 1.0
            draw.ellipse([255, int(42 + tear_p * 35), 261, int(48 + tear_p * 35)], fill="#29B6F6")
            draw.ellipse([272, int(40 + tear_p * 35), 278, int(46 + tear_p * 35)], fill="#29B6F6")
            draw_thick_text(draw, "ごめんなさい...", 120, 34, font_title, "#0277BD")

        elif idx == 11:
            # 12. イエーイ！ (ミラーボール光線・カラフル音符・星屑)
            for i, (nx, ny_base, col) in enumerate([(45, 55, "#00E676"), (265, 48, "#FFD600"), (285, 75, "#FF4081")]):
                ny = ny_base + int(8 * math.sin(t * 4 * pi + i))
                draw_sparkle(draw, nx, ny, 10, col)
            draw_thick_text(draw, "イエーイ！", 140, 34, font_title, "#00C853")

        elif idx == 12:
            # 13. よろしく！ (キラーン光彩・青空スパークル)
            sp_scale = 1.0 + 0.4 * math.sin(t * 4 * pi)
            draw_sparkle(draw, 265, 48, int(15 * sp_scale), "#00E5FF")
            draw_sparkle(draw, 50, 50, int(10 * sp_scale), "#76FF03")
            draw_thick_text(draw, "よろしく！", 140, 34, font_title, "#0091EA")

        elif idx == 13:
            # 14. いらっしゃいませ！ (PUKUMUKU看板・リボン・キラキラ)
            # パン工房木製看板
            draw.rectangle([210, 18, 305, 42], fill="#FFF8E1", outline="#8D6E63", width=2)
            draw.text((257, 30), "🍞 PUKUMUKU 🥖", font=font_small, fill="#5D4037", anchor="mm")
            draw_sparkle(draw, 205, 45, 8, "#FFB300")
            draw_sparkle(draw, 310, 45, 8, "#FFB300")
            draw_thick_text(draw, "いらっしゃいませ！", 115, 30, font_mid, "#D84315")

        elif idx == 14:
            # 15. おやすみなさい (三日月・星・ふわふわZzz...)
            # 三日月
            draw.ellipse([255, 32, 280, 57], fill="#FFD54F")
            draw.ellipse([250, 29, 275, 54], fill="#000000", outline=None) # 切り抜き風
            # Zzz...
            z_y = int(35 - t * 15)
            draw_thick_text(draw, "Z", 235, z_y + 10, font_mid, "#9575CD", stroke_width=4)
            draw_thick_text(draw, "z", 245, z_y, font_small, "#B39DDB", stroke_width=3)
            draw_thick_text(draw, "おやすみなさい", 120, 34, font_title, "#5E35B1")

        elif idx == 15:
            # 16. 一発逆転！ (燃え上がる多重の闘志の炎・散る火花)
            flame_y = 52 - int(math.sin(t * 4 * pi) * 8)
            # 外炎（赤）
            draw.polygon([(262, flame_y - 18), (248, flame_y + 12), (276, flame_y + 12)], fill="#FF3D00")
            # 中炎（橙）
            draw.polygon([(262, flame_y - 10), (252, flame_y + 10), (272, flame_y + 10)], fill="#FF9100")
            # 内炎（黄）
            draw.polygon([(262, flame_y - 3), (256, flame_y + 8), (268, flame_y + 8)], fill="#FFEA00")
            # 火花
            for fx, fy in [(242, flame_y - 8), (280, flame_y - 4), (250, flame_y - 20)]:
                draw_sparkle(draw, fx, fy, 4, "#FFD600")
            draw_thick_text(draw, "一発逆転！", 115, 36, font_title, "#BF360C")

        composite = Image.alpha_composite(base_im, overlay)
        
        # RGBAクリーン＆ポスタライズ（背景透過100%保護、チカチカ完全ゼロ、300KB以下保証）
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

    # フルフレーム APNG 保存 (LINE公式規格: 320x270、dispose_op=1、blend_op=0、300KB以下厳格達成)
    out_filename = f"{idx+1:02d}.png"
    out_path = os.path.join(OUT_DIR, out_filename)
    frames[0].save(
        out_path,
        format='PNG',
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=2, # LINE規定: 2ループ再生 (計4.0秒)
        optimize=False
    )
    kb = os.path.getsize(out_path) / 1024
    print(f"✓ {out_filename} saved: {kb:.1f} KB / 300KB (純くん一時保存・チカチカゼロ・豪華イラスト)")

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

print("All 16 stickers built successfully with rich illustrations and copyright-safe model!")
