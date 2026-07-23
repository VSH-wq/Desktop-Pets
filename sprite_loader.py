"""
sprite_loader.py

Loads a pet's spritesheets (from the Tiny Pets asset pack) and slices them
into individual animation frames ready for use in a tkinter Label.

Tkinter doesn't support true per-pixel transparency for arbitrary widget
backgrounds, so we use the standard "color-key" trick: every frame is
composited onto a solid background color (magenta by default), and that
exact color is later registered as the window's -transparentcolor on
Windows, making it disappear.
"""

import json
from pathlib import Path
from PIL import Image, ImageTk

ASSETS_DIR = Path(__file__).parent / "assets" / "Tiny Pets"

# Pets available in the pack (folder names match these exactly)
PETS = [
    "Bear", "Bunny", "Cat", "Chick", "Dog", "Dragon",
    "Fox", "Frog", "Ghost", "Panda", "Penguin", "Slime",
]


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


class SpriteSet:
    """Holds every animation's frame list for one pet at one render size."""

    def __init__(self, pet_name: str, size: int = 64, bg_color: str = "#ff00ff"):
        if pet_name not in PETS:
            raise ValueError(f"Unknown pet '{pet_name}'. Available: {PETS}")

        self.pet_name = pet_name
        self.size = size
        self.bg_color = bg_color

        pet_dir = ASSETS_DIR / pet_name
        json_path = pet_dir / f"{pet_name.lower()}.json"
        with open(json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.fps = meta["fps"]
        self.frame_count = meta["frames"]
        self.frames = {}  # animation name -> list[ImageTk.PhotoImage]

        bg_rgb = _hex_to_rgb(bg_color) + (255,)
        size_key = str(size)

        for anim_name, filename in meta["files"][size_key].items():
            sheet_path = pet_dir / filename
            sheet = Image.open(sheet_path).convert("RGBA")
            frame_w = sheet.width // self.frame_count
            frame_h = sheet.height

            frames = []
            for i in range(self.frame_count):
                box = (i * frame_w, 0, (i + 1) * frame_w, frame_h)
                frame = sheet.crop(box)

                bg = Image.new("RGBA", frame.size, bg_rgb)
                composed = Image.alpha_composite(bg, frame).convert("RGB")
                frames.append(ImageTk.PhotoImage(composed))

            self.frames[anim_name] = frames

    def animation_names(self):
        return list(self.frames.keys())
