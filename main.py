# main.py
import tkinter as tk
from ui import BlackjackUI

def main():
    root = tk.Tk()
    app = BlackjackUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
