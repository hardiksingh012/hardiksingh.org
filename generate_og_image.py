"""
Generates og-image.png (1200x630) for LinkedIn / Twitter / WhatsApp link previews.

Matches the portfolio site's aesthetic:
  - Soft-black background (#0E0E10)
  - Warm off-white text (#F5F5F0)
  - Circular avatar (linkedin-avatar.jpeg)
  - Brand-consistent typography

Run:
    python generate_og_image.py

Outputs:
    og-image.png  (1200 x 630, ~80-150 KB)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# ── Canvas ────────────────────────────────────────────────
W, H = 1200, 630
BG          = (14, 14, 16)         # --bg        #0E0E10
SURFACE     = (24, 24, 27)         # --card      #18181B
TEXT        = (245, 245, 240)      # --text      #F5F5F0
MUTED       = (138, 138, 144)      # --muted     #8A8A90
ACCENT_SOFT = (200, 200, 194)      # --gold-soft #C8C8C2
BORDER      = (38, 38, 43)         # --border    #26262B

OUT_PATH    = "og-image.png"
AVATAR_PATH = "linkedin-avatar.jpeg"

# ── Font loader (Windows system fonts) ────────────────────
def load(name, size):
    candidates = [
        f"C:/Windows/Fonts/{name}",
        f"/Library/Fonts/{name}",
        f"/usr/share/fonts/{name}",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# Heavy display font for the name, regular for the rest
FONT_NAME     = load("arialbd.ttf", 86)   # Arial Bold
FONT_ROLE     = load("arial.ttf", 36)
FONT_META     = load("consola.ttf", 22)   # Consolas (mono)
FONT_BADGE    = load("consolab.ttf", 18)  # Consolas Bold (mono)
FONT_HS       = load("arialbd.ttf", 60)   # avatar fallback initials
FONT_DOMAIN   = load("consola.ttf", 20)

# ── Base canvas ───────────────────────────────────────────
img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# Subtle radial vignette (warm white in the top-right, fading out)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for r, alpha in [(720, 6), (520, 10), (360, 14), (220, 18)]:
    gdraw.ellipse(
        (W - r, -r // 3, W + r, r - r // 3),
        fill=(245, 245, 240, alpha),
    )
glow = glow.filter(ImageFilter.GaussianBlur(40))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)

# Top accent stripe (very subtle gold-soft horizontal line)
stripe_y = 0
for i in range(2):
    draw.line([(0, stripe_y + i), (W, stripe_y + i)], fill=ACCENT_SOFT, width=1)

# ── Circular avatar ───────────────────────────────────────
AVATAR_SIZE = 320
AVATAR_X = 90
AVATAR_Y = (H - AVATAR_SIZE) // 2

if os.path.exists(AVATAR_PATH):
    avatar = Image.open(AVATAR_PATH).convert("RGB")
    # Center-crop to square first
    aw, ah = avatar.size
    side = min(aw, ah)
    avatar = avatar.crop(
        ((aw - side) // 2, (ah - side) // 2,
         (aw + side) // 2, (ah + side) // 2)
    ).resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    # Circular mask
    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)

    # Soft outer ring (border + glow)
    ring_pad = 8
    ring_box = (
        AVATAR_X - ring_pad,
        AVATAR_Y - ring_pad,
        AVATAR_X + AVATAR_SIZE + ring_pad,
        AVATAR_Y + AVATAR_SIZE + ring_pad,
    )
    draw.ellipse(ring_box, outline=ACCENT_SOFT, width=3)

    img.paste(avatar, (AVATAR_X, AVATAR_Y), mask)
else:
    # Fallback: gradient circle with "HS" initials
    draw.ellipse(
        (AVATAR_X, AVATAR_Y, AVATAR_X + AVATAR_SIZE, AVATAR_Y + AVATAR_SIZE),
        fill=ACCENT_SOFT,
    )
    bbox = draw.textbbox((0, 0), "HS", font=FONT_HS)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (AVATAR_X + (AVATAR_SIZE - tw) // 2,
         AVATAR_Y + (AVATAR_SIZE - th) // 2 - 8),
        "HS", fill=BG, font=FONT_HS,
    )

# ── Right column text ─────────────────────────────────────
TX = AVATAR_X + AVATAR_SIZE + 70  # text column starts here

# Small "AVAILABLE" pill at the top
pill_text = "AVAILABLE FOR PROJECTS"
pbbox = draw.textbbox((0, 0), pill_text, font=FONT_BADGE)
pw, ph = pbbox[2] - pbbox[0], pbbox[3] - pbbox[1]
PILL_PAD_X, PILL_PAD_Y = 16, 8
PILL_Y = 130
# Dot
DOT_R = 5
draw.ellipse(
    (TX + 14 - DOT_R, PILL_Y + ph // 2 - DOT_R + 4,
     TX + 14 + DOT_R, PILL_Y + ph // 2 + DOT_R + 4),
    fill=(16, 185, 129),  # green
)
draw.rounded_rectangle(
    (TX, PILL_Y - PILL_PAD_Y,
     TX + 30 + pw + PILL_PAD_X, PILL_Y + ph + PILL_PAD_Y),
    radius=999,
    outline=BORDER,
    width=1,
)
draw.text((TX + 30, PILL_Y - 2), pill_text, fill=ACCENT_SOFT, font=FONT_BADGE)

# Main name
NAME_Y = PILL_Y + 56
draw.text((TX, NAME_Y), "Hardik Singh", fill=TEXT, font=FONT_NAME)

# Role
ROLE_Y = NAME_Y + 110
draw.text(
    (TX, ROLE_Y),
    "Python Web Scraping Specialist",
    fill=ACCENT_SOFT,
    font=FONT_ROLE,
)

# Meta line  (mono)
META_Y = ROLE_Y + 60
meta_text = "Clean data  ·  24h delivery  ·  2,500+ records"
draw.text((TX, META_Y), meta_text, fill=MUTED, font=FONT_META)

# Bottom-right domain
domain = "hardiksingh.org"
dbbox = draw.textbbox((0, 0), domain, font=FONT_DOMAIN)
dw, dh = dbbox[2] - dbbox[0], dbbox[3] - dbbox[1]
draw.text(
    (W - dw - 60, H - dh - 50),
    domain,
    fill=ACCENT_SOFT,
    font=FONT_DOMAIN,
)

# ── Save ──────────────────────────────────────────────────
img.save(OUT_PATH, "PNG", optimize=True)
print(f"Wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH) // 1024} KB)")
