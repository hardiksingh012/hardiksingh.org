"""
Generates og-image.png (1200x630) for LinkedIn / Twitter / WhatsApp previews.

Matches the portfolio site's aesthetic:
  - Soft-black background (#0E0E10)
  - Warm off-white text (#F5F5F0)
  - Circular avatar (linkedin-avatar.jpeg)
  - Brand-consistent typography

Technique: Renders at 2x (2400x1260), then downsamples with LANCZOS.
This gives crisp, anti-aliased text that the native PIL renderer can't
produce on its own at small sizes.

Run:
    python generate_og_image.py

Outputs:
    og-image.png  (1200 x 630, ~150-250 KB)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# ── Render at 2x for crisp downsampled output ─────────────
SCALE = 2
W, H = 1200 * SCALE, 630 * SCALE

# Colors
BG          = (14, 14, 16)
SURFACE     = (24, 24, 27)
TEXT        = (245, 245, 240)
MUTED_BRIGHT = (170, 170, 174)     # brighter than --muted for OG readability
ACCENT_SOFT = (220, 220, 213)      # slightly brighter than --gold-soft
BORDER      = (52, 52, 58)
GREEN       = (16, 185, 129)

OUT_PATH    = "og-image.png"
AVATAR_PATH = "linkedin-avatar.jpeg"

# ── Font loader (Windows / mac / linux) ───────────────────
def load(name, size):
    candidates = [
        f"C:/Windows/Fonts/{name}",
        f"/Library/Fonts/{name}",
        f"/System/Library/Fonts/{name}",
        f"/usr/share/fonts/{name}",
        f"/usr/share/fonts/truetype/dejavu/{name}",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

# Sizes are doubled (rendering at 2x). Final output is half these dims.
FONT_NAME   = load("arialbd.ttf", 172)   # Arial Bold - big headline
FONT_ROLE   = load("arialbd.ttf",  76)   # bolder role text
FONT_META   = load("consola.ttf",  46)   # mono meta line
FONT_BADGE  = load("consolab.ttf", 36)   # mono bold pill
FONT_HS     = load("arialbd.ttf", 120)   # avatar fallback initials
FONT_DOMAIN = load("consolab.ttf", 38)   # mono bold domain tag

# ── Base canvas ───────────────────────────────────────────
img = Image.new("RGB", (W, H), BG)

# Subtle warm-white radial glow in the top-right
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gdraw = ImageDraw.Draw(glow)
for r, alpha in [(720 * SCALE, 6), (520 * SCALE, 9), (360 * SCALE, 12), (220 * SCALE, 16)]:
    gdraw.ellipse(
        (W - r, -r // 3, W + r, r - r // 3),
        fill=(245, 245, 240, alpha),
    )
glow = glow.filter(ImageFilter.GaussianBlur(40 * SCALE))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img)

# Top accent stripe
for i in range(2 * SCALE):
    draw.line([(0, i), (W, i)], fill=ACCENT_SOFT, width=1)

# ── Circular avatar ───────────────────────────────────────
AVATAR_SIZE = 320 * SCALE
AVATAR_X = 90 * SCALE
AVATAR_Y = (H - AVATAR_SIZE) // 2

if os.path.exists(AVATAR_PATH):
    avatar = Image.open(AVATAR_PATH).convert("RGB")
    aw, ah = avatar.size
    side = min(aw, ah)
    avatar = avatar.crop(
        ((aw - side) // 2, (ah - side) // 2,
         (aw + side) // 2, (ah + side) // 2)
    ).resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)

    ring_pad = 8 * SCALE
    ring_box = (
        AVATAR_X - ring_pad,
        AVATAR_Y - ring_pad,
        AVATAR_X + AVATAR_SIZE + ring_pad,
        AVATAR_Y + AVATAR_SIZE + ring_pad,
    )
    draw.ellipse(ring_box, outline=ACCENT_SOFT, width=3 * SCALE)

    img.paste(avatar, (AVATAR_X, AVATAR_Y), mask)
else:
    draw.ellipse(
        (AVATAR_X, AVATAR_Y, AVATAR_X + AVATAR_SIZE, AVATAR_Y + AVATAR_SIZE),
        fill=ACCENT_SOFT,
    )
    bbox = draw.textbbox((0, 0), "HS", font=FONT_HS)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        (AVATAR_X + (AVATAR_SIZE - tw) // 2,
         AVATAR_Y + (AVATAR_SIZE - th) // 2 - 8 * SCALE),
        "HS", fill=BG, font=FONT_HS,
    )

# ── Right-column text ─────────────────────────────────────
TX = AVATAR_X + AVATAR_SIZE + 70 * SCALE

# "AVAILABLE FOR PROJECTS" pill
pill_text = "AVAILABLE FOR PROJECTS"
pbbox = draw.textbbox((0, 0), pill_text, font=FONT_BADGE)
pw, ph = pbbox[2] - pbbox[0], pbbox[3] - pbbox[1]
PILL_Y = 130 * SCALE
DOT_R = 10 * SCALE
draw.ellipse(
    (TX + 22 * SCALE - DOT_R, PILL_Y + ph // 2 - DOT_R + 8 * SCALE,
     TX + 22 * SCALE + DOT_R, PILL_Y + ph // 2 + DOT_R + 8 * SCALE),
    fill=GREEN,
)
draw.rounded_rectangle(
    (TX, PILL_Y - 16 * SCALE,
     TX + 50 * SCALE + pw + 32 * SCALE, PILL_Y + ph + 16 * SCALE),
    radius=999,
    outline=BORDER,
    width=2 * SCALE,
)
draw.text((TX + 50 * SCALE, PILL_Y - 4 * SCALE), pill_text,
          fill=ACCENT_SOFT, font=FONT_BADGE)

# Headline
NAME_Y = PILL_Y + 70 * SCALE
draw.text((TX, NAME_Y), "Hardik Singh", fill=TEXT, font=FONT_NAME)

# Role - placed below the headline accounting for its actual rendered height
nbbox = draw.textbbox((TX, NAME_Y), "Hardik Singh", font=FONT_NAME)
ROLE_Y = nbbox[3] + 28 * SCALE
draw.text((TX, ROLE_Y), "Python Web Scraping Specialist",
          fill=ACCENT_SOFT, font=FONT_ROLE)

# Meta line - placed below the role
rbbox = draw.textbbox((TX, ROLE_Y), "Python Web Scraping Specialist", font=FONT_ROLE)
META_Y = rbbox[3] + 28 * SCALE
meta_text = "Clean data  ·  24h delivery  ·  2,500+ records"
draw.text((TX, META_Y), meta_text, fill=MUTED_BRIGHT, font=FONT_META)

# Domain tag bottom-right
domain = "hardiksingh.org"
dbbox = draw.textbbox((0, 0), domain, font=FONT_DOMAIN)
dw, dh = dbbox[2] - dbbox[0], dbbox[3] - dbbox[1]
draw.text(
    (W - dw - 60 * SCALE, H - dh - 50 * SCALE),
    domain, fill=ACCENT_SOFT, font=FONT_DOMAIN,
)

# ── Downsample to 1200x630 with LANCZOS for crisp output ──
final = img.resize((1200, 630), Image.LANCZOS)
final.save(OUT_PATH, "PNG", optimize=True)
print(f"Wrote {OUT_PATH}  ({os.path.getsize(OUT_PATH) // 1024} KB)")
