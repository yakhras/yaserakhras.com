"""Generate the browser/tab icons PaperMod links to, from assets/images/photo.jpg.

Run again after replacing the photo:
    .venv/Scripts/python -m pip install Pillow
    .venv/Scripts/python scripts/make_favicons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PHOTO = ROOT / "assets" / "images" / "photo.jpg"
STATIC = ROOT / "static"

# Safari's pinned-tab mask is a single-colour shape: a plain circle, echoing the round photo.
SAFARI_MASK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
<circle cx="8" cy="8" r="8"/>
</svg>
"""


def round_photo(size):
    """Square photo scaled to size x size, outside the circle transparent."""
    photo = Image.open(PHOTO).convert("RGBA")
    side = min(photo.size)
    left, top = (photo.width - side) // 2, (photo.height - side) // 2
    photo = photo.crop((left, top, left + side, top + side))
    # Draw the mask at 4x and downscale for a smooth edge.
    mask = Image.new("L", (side * 4, side * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, side * 4 - 1, side * 4 - 1), fill=255)
    photo.putalpha(mask.resize((side, side), Image.LANCZOS))
    return photo.resize((size, size), Image.LANCZOS)


def main():
    round_photo(16).save(STATIC / "favicon-16x16.png")
    round_photo(32).save(STATIC / "favicon-32x32.png")
    round_photo(48).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # iOS draws its own rounded corners and doesn't support transparency: use the full square photo.
    Image.open(PHOTO).convert("RGB").resize((180, 180), Image.LANCZOS).save(STATIC / "apple-touch-icon.png")
    (STATIC / "safari-pinned-tab.svg").write_text(SAFARI_MASK, encoding="utf-8")
    print("icons written to", STATIC)


if __name__ == "__main__":
    main()
