"""
speech_bubble.py

A small borderless, always-on-top window that pops up above the pet to
show a short message, then hides itself again after a delay.
"""

import tkinter as tk


class SpeechBubble:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.attributes("-topmost", True)
        self.top.withdraw()  # start hidden

        self.frame = tk.Frame(
            self.top, bg="#fffbe6",
            highlightbackground="#444", highlightthickness=1,
        )
        self.frame.pack()
        self.label = tk.Label(
            self.frame, text="", bg="#fffbe6", fg="#222",
            font=("Segoe UI", 9), wraplength=170, justify="left",
            padx=8, pady=4,
        )
        self.label.pack()

        self._hide_job = None

    def show(self, text: str, anchor_x: int, anchor_y: int, duration_ms: int = 2200):
        """anchor_x/anchor_y: the point (in screen coords) the bubble should
        point at from above — typically the top-center of the pet window."""
        self.label.config(text=text)
        self.top.update_idletasks()
        w = self.top.winfo_reqwidth()
        h = self.top.winfo_reqheight()

        screen_w = self.root.winfo_screenwidth()
        x = anchor_x - w // 2
        x = max(4, min(x, screen_w - w - 4))
        y = max(4, anchor_y - h - 10)

        self.top.geometry(f"{w}x{h}+{x}+{y}")
        self.top.deiconify()
        self.top.lift()

        if self._hide_job is not None:
            self.root.after_cancel(self._hide_job)
        self._hide_job = self.root.after(duration_ms, self.hide)

    def hide(self):
        self.top.withdraw()
        self._hide_job = None
