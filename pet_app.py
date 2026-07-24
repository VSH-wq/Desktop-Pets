"""
pet_app.py

DesktopPet: a borderless, always-on-top, transparent-background tkinter
window that displays an animated pet, wanders around, and reacts to you.

States: idle, jump (random hop), sleep, happy, chase (double-click).

Stats:
    happiness (0-100) - rises on click/feed, decays slowly over time
    energy    (0-100) - falls while active, restored by sleeping

Stats drive both idle chatter mood and how often the pet naps.
"""

import random
import tkinter as tk

from sprite_loader import SpriteSet, PETS
from speech_bubble import SpeechBubble
import messages

TRANSPARENT_KEY = "#ff00ff"  # magenta color-key used for the transparency trick

# The sprite pack only has idle/jump/sleep/happy animations. "chase" is a
# behavior state, not a sprite - it reuses the jump animation for its frames.
ANIM_FOR_STATE = {
    "idle": "idle", "jump": "jump", "sleep": "sleep",
    "happy": "happy", "chase": "jump",
}

CHASE_DURATION_S = 5
CHASE_STEP_MS = 40
CHASE_SPEED_PX = 12


class DesktopPet:
    def __init__(self, root: tk.Tk, pet_name: str = "Cat", size: int = 64):
        self.root = root
        self.size = size
        self.pet_name = pet_name
        self.sprites = SpriteSet(pet_name, size, TRANSPARENT_KEY)
        self.bubble = SpeechBubble(root)

        self.state = "idle"
        self.frame_index = 0
        self.idle_timer = 0
        self.facing_right = True
        self.dragging = False
        self._drag_start = (0, 0)
        self._click_job = None
        self._chase_ticks_left = 0

        self.happiness = 80
        self.energy = 100

        self._next_idle_threshold = random.randint(4, 8)
        self._next_sleep_threshold = random.randint(6, 12)
        self._next_chatter_delay = random.randint(15, 30)
        self._chatter_countdown = self._next_chatter_delay

        self._setup_window()
        self._build_context_menu()

        self._animate()
        self._tick_behavior()

        self.root.after(600, lambda: self._say(messages.pick(messages.GREETING)))

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------
    def _setup_window(self):
        self.root.overrideredirect(True)          # no title bar / borders
        self.root.attributes("-topmost", True)     # always on top
        try:
            # Windows-only attribute: makes TRANSPARENT_KEY pixels see-through.
            self.root.attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            # Not on Windows (e.g. testing on Linux/Mac) - window will show
            # a solid magenta background instead of being transparent, but
            # everything else still works.
            pass
        self.root.config(bg=TRANSPARENT_KEY)

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        start_x = screen_w // 2
        start_y = screen_h - self.size - 60  # sit near the taskbar
        self.root.geometry(f"{self.size}x{self.size}+{start_x}+{start_y}")

        self.label = tk.Label(self.root, bg=TRANSPARENT_KEY, bd=0, highlightthickness=0)
        self.label.pack(fill="both", expand=True)

        self.label.bind("<ButtonPress-1>", self._on_press)
        self.label.bind("<B1-Motion>", self._on_drag)
        self.label.bind("<ButtonRelease-1>", self._on_release)
        self.label.bind("<Double-Button-1>", self._on_double_click)
        self.label.bind("<Button-3>", self._show_menu)

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)

        pet_menu = tk.Menu(self.menu, tearoff=0)
        for pet in PETS:
            pet_menu.add_command(label=pet, command=lambda p=pet: self.switch_pet(p))
        self.menu.add_cascade(label="Switch Pet", menu=pet_menu)

        size_menu = tk.Menu(self.menu, tearoff=0)
        for s in (32, 64):
            size_menu.add_command(label=f"{s}px", command=lambda s=s: self.switch_size(s))
        self.menu.add_cascade(label="Size", menu=size_menu)

        self.menu.add_separator()
        self.menu.add_command(label="Feed", command=self.feed)
        self.menu.add_command(label="Show Stats", command=self.show_stats)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.root.destroy)

    def _show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    # ------------------------------------------------------------------
    # Pet switching (stats carry over across pets/sizes)
    # ------------------------------------------------------------------
    def switch_pet(self, pet_name: str):
        self.pet_name = pet_name
        self.sprites = SpriteSet(pet_name, self.size, TRANSPARENT_KEY)
        self._set_state("idle")

    def switch_size(self, size: int):
        self.size = size
        self.sprites = SpriteSet(self.pet_name, size, TRANSPARENT_KEY)
        x, y = self.root.winfo_x(), self.root.winfo_y()
        self.root.geometry(f"{size}x{size}+{x}+{y}")
        self._set_state("idle")

    # ------------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------------
    def _on_press(self, event):
        self._drag_start = (event.x, event.y)
        self.dragging = False

    def _on_drag(self, event):
        self.dragging = True
        new_x = self.root.winfo_x() + event.x - self._drag_start[0]
        new_y = self.root.winfo_y() + event.y - self._drag_start[1]
        self.root.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event):
        if self.dragging:
            self.dragging = False
            self._say(messages.pick(messages.DRAG))
            return
        # Delay the single-click reaction briefly so a double-click
        # (chase) can cancel it instead of both firing.
        if self._click_job is not None:
            self.root.after_cancel(self._click_job)
        self._click_job = self.root.after(220, self._handle_single_click)

    def _handle_single_click(self):
        self._click_job = None
        self.happiness = min(100, self.happiness + 15)
        self._set_state("happy")
        self._say(messages.pick(messages.HAPPY_CLICK))

    def _on_double_click(self, event):
        if self._click_job is not None:
            self.root.after_cancel(self._click_job)
            self._click_job = None
        self._start_chase()

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------
    def _set_state(self, state: str):
        self.state = state
        self.frame_index = 0
        self.idle_timer = 0
        if state == "idle":
            self._next_idle_threshold = random.randint(4, 8)
        elif state == "sleep":
            self._next_sleep_threshold = random.randint(6, 12)

    def _animate(self):
        anim_name = ANIM_FOR_STATE[self.state]
        frames = self.sprites.frames_for(anim_name, self.facing_right)
        self.label.config(image=frames[self.frame_index % len(frames)])
        self.frame_index += 1

        fps = self.sprites.fps[anim_name]
        delay_ms = max(1, int(1000 / fps))
        self.root.after(delay_ms, self._animate)

    def _tick_behavior(self):
        """Runs once a second: state transitions, stat decay, idle chatter."""
        if not self.dragging:
            self.idle_timer += 1
            self._update_stats()

            if self.state == "idle" and self.energy <= 20:
                self._set_state("sleep")
                self._say(messages.pick(messages.SLEEP))
            elif self.state == "idle" and self.idle_timer > self._next_idle_threshold:
                if random.random() < 0.65:
                    self._start_hop()
                else:
                    self._set_state("sleep")
                    self._say(messages.pick(messages.SLEEP))
            elif self.state == "sleep" and (
                self.energy >= 90 or self.idle_timer > self._next_sleep_threshold
            ):
                self._set_state("idle")
                self._say(messages.pick(messages.WAKE))
            elif self.state == "happy" and self.idle_timer > 2:
                self._set_state("idle")

            self._tick_idle_chatter()

        self.root.after(1000, self._tick_behavior)

    def _update_stats(self):
        if self.state == "sleep":
            self.energy = min(100, self.energy + 3)
        elif self.state in ("jump", "chase"):
            self.energy = max(0, self.energy - 2)
        else:
            self.energy = max(0, self.energy - 1)

        if self.idle_timer % 3 == 0:
            self.happiness = max(0, self.happiness - 1)

    def _tick_idle_chatter(self):
        if self.state not in ("idle",):
            return
        self._chatter_countdown -= 1
        if self._chatter_countdown <= 0:
            self._say(messages.idle_chatter_for_mood(self.happiness))
            self._chatter_countdown = random.randint(15, 30)

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------
    def _start_hop(self):
        self._set_state("jump")
        direction = random.choice([-1, 1])
        self.facing_right = direction > 0
        distance = random.randint(60, 160)
        steps = 20
        step_dist = (distance * direction) // steps
        screen_w = self.root.winfo_screenwidth()

        if random.random() < 0.3:
            self._say(messages.pick(messages.HOP))

        def step(n=0):
            if self.state != "jump" or n >= steps:
                if self.state == "jump":
                    self._set_state("idle")
                return
            new_x = self.root.winfo_x() + step_dist
            new_x = max(0, min(new_x, screen_w - self.size))
            self.root.geometry(f"+{new_x}+{self.root.winfo_y()}")
            self.root.after(40, lambda: step(n + 1))

        step()

    def _start_chase(self):
        self._set_state("chase")
        self._chase_ticks_left = int(CHASE_DURATION_S * 1000 / CHASE_STEP_MS)
        self._say(messages.pick(messages.CHASE_START))
        self._chase_step()

    def _chase_step(self):
        if self.state != "chase" or self._chase_ticks_left <= 0:
            if self.state == "chase":
                self._set_state("idle")
                self._say(messages.pick(messages.CHASE_END))
            return

        self._chase_ticks_left -= 1
        pointer_x = self.root.winfo_pointerx()
        cur_x = self.root.winfo_x()
        target_x = pointer_x - self.size // 2

        if abs(target_x - cur_x) > CHASE_SPEED_PX:
            direction = 1 if target_x > cur_x else -1
            self.facing_right = direction > 0
            new_x = cur_x + direction * CHASE_SPEED_PX
        else:
            new_x = cur_x

        screen_w = self.root.winfo_screenwidth()
        new_x = max(0, min(new_x, screen_w - self.size))
        self.root.geometry(f"+{new_x}+{self.root.winfo_y()}")

        self.root.after(CHASE_STEP_MS, self._chase_step)

    # ------------------------------------------------------------------
    # Feed / stats / speech bubble helpers
    # ------------------------------------------------------------------
    def feed(self):
        self.happiness = min(100, self.happiness + 30)
        self.energy = min(100, self.energy + 20)
        self._set_state("happy")
        self._say(messages.pick(messages.FEED))

    def show_stats(self):
        self._say(f"Happiness: {self.happiness}  Energy: {self.energy}", duration_ms=3000)

    def _say(self, text: str, duration_ms: int = 2200):
        anchor_x = self.root.winfo_x() + self.size // 2
        anchor_y = self.root.winfo_y()
        self.bubble.show(text, anchor_x, anchor_y, duration_ms)
