# Desktop Pet (Windows 10, Python 3.12)

A small animated pet that lives on your desktop, wanders around, sleeps,
and reacts when you click it. Built with tkinter + Pillow using the
"Tiny Pets" sprite pack.

## Project structure

```
desktop_pet/
├── main.py              # entry point
├── pet_app.py            # DesktopPet class: window, state machine, animation
├── sprite_loader.py       # slices spritesheets into frames per animation
├── speech_bubble.py       # popup bubble window used for messages
├── messages.py            # pools of message strings per event/mood
├── requirements.txt
├── README.md
└── assets/
    └── Tiny Pets/         # the sprite pack (12 pets x 4 animations x 2 sizes)
```

## Setup

Requires Python 3.12 on Windows 10.

```
cd desktop_pet
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```
python main.py
```

## Controls

- **Left-click**: pet plays "happy" and says something, +15 happiness
- **Double-click**: pet chases your cursor for ~5 seconds, then rests
- **Left-click + drag**: move the pet around the screen; it comments when you let go
- **Right-click**: context menu — switch pet (all 12), switch size
  (32/64px), **Feed** (+30 happiness / +20 energy), **Show Stats**, or quit

## How it behaves

- Starts **idle**, facing whichever way it last moved. After a random
  4–8 seconds it either **hops** (jump animation, random distance
  left/right, clamped to the screen edges, sprite mirrors to face the
  direction it's moving) or goes to **sleep**.
- Every hop/active second costs a little **energy**; sleeping restores
  it. If energy drops to 20 or below the pet naps regardless of the
  idle timer; it wakes once energy is back near full (or after its
  timer runs out, whichever comes first).
- **Happiness** slowly decays over time and rises from clicking or
  feeding. It doesn't gate behavior directly, but it picks which pool
  of idle chatter shows up (upbeat vs. neutral vs. "pet me?").
- The pet occasionally says something unprompted while idle (every
  ~15–30s) in a speech bubble above its head — the tone depends on its
  current happiness.
- Stats (happiness/energy) carry over when you switch pet or size —
  they belong to "the pet", not to a specific sprite.

## How the transparency works

Tkinter doesn't support real per-pixel alpha on arbitrary widgets, so
`sprite_loader.py` composites every sprite frame onto a solid magenta
background (`#ff00ff`), and `pet_app.py` registers that exact color as
the window's `-transparentcolor` (a Windows-only tkinter feature). The
magenta becomes invisible, leaving just the pet. If you ever see a faint
magenta fringe around a pet's edges, it's anti-aliasing in the source
PNG blending into the color key — reduce it by upgrading to a PyQt/PySide
UI with true alpha compositing (a bigger rewrite, not needed for v1).

## Packaging as a standalone .exe

```
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```

The .exe will be in `dist/main.exe`. Double-click to run — no Python
install needed on the target machine.

## Extending

- Add a "feed" or "pet" interaction with its own animation by adding a
  new state in `pet_app.py` and referencing it in `sprite_loader.py`'s
  slicing (works automatically if you add the animation name to the
  pet's `.json` file and matching spritesheet).
- Add a system tray icon instead of right-click-only using `pystray`
  if you want it to also show in the Windows notification area.
