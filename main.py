"""
main.py

Entry point. Run with:  python main.py
Right-click the pet to switch pets/size or quit. Left-click makes it happy.
Drag with left-click held to move it.
"""

import tkinter as tk
from pet_app import DesktopPet

DEFAULT_PET = "Cat"
DEFAULT_SIZE = 64


def main():
    root = tk.Tk()
    DesktopPet(root, pet_name=DEFAULT_PET, size=DEFAULT_SIZE)
    root.mainloop()


if __name__ == "__main__":
    main()
