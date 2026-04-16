import os
import sys
import threading
import tkinter as tk
import keyboard
import pystray
from PIL import Image, ImageDraw, ImageGrab, ImageTk

class ScreenMarkerTray:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Screen Marker Background")

        self.overlay = None
        self.bg_image = None
        self.strokes = []

        self.setup_tray()
        
        try:
            keyboard.add_hotkey('alt+d', self.trigger_drawing, suppress=True)
            print("Hotkey Alt+D activated. App is running in background.")
        except Exception as e:
            print(f"Hotkey registration error: {e}")

        self.root.mainloop()

    def create_tray_image(self):
        img = Image.new('RGB', (64, 64), color=(30, 30, 46))
        d = ImageDraw.Draw(img)
        d.rectangle([5, 5, 59, 59], outline='#FF00FF', width=4)
        d.line((15, 49, 49, 15), fill='#FF00FF', width=6)
        d.ellipse((44, 10, 54, 20), fill='#00FFFF')
        return img

    def setup_tray(self):
        image = self.create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem('Bật Bút Vẽ (Alt+D)', self.trigger_drawing_from_tray),
            pystray.MenuItem('Thoát hoàn toàn', self.quit_app)
        )
        self.icon = pystray.Icon("ScreenMarker", image, "Screen Marker", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def trigger_drawing_from_tray(self, icon, item):
        self.trigger_drawing()

    def trigger_drawing(self):
        self.root.after(0, self.open_overlay)

    def open_overlay(self):
        if self.overlay is not None:
            return
            
        self.strokes = []
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        self.overlay.config(cursor="none")
        
        w = self.overlay.winfo_screenwidth()
        h = self.overlay.winfo_screenheight()
        bg_pil = ImageGrab.grab(bbox=(0, 0, w, h))
        self.bg_image = ImageTk.PhotoImage(bg_pil)
        
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw", tags="background")
        
        self.line_color = "#FF00FF"
        self.line_width = 2
        self.last_x = None
        self.last_y = None

        # Move mode state (right-click drag)
        self.move_start_x = None
        self.move_start_y = None
        self.is_moving = False

        # --- Pencil cursor items ---
        self.cursor_tip_cone  = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#FFE0B2", tags="custom_cursor")
        self.cursor_body      = self.canvas.create_line(0, 0, 0, 0, width=5, capstyle=tk.ROUND, fill="#FFCC00", tags="custom_cursor")
        self.cursor_eraser    = self.canvas.create_line(0, 0, 0, 0, width=5, capstyle=tk.ROUND, fill="#FF6666", tags="custom_cursor")
        self.cursor_tip_point = self.canvas.create_oval(0, 0, 0, 0, fill="black", tags="custom_cursor")
        
        # --- Move cursor (shown during right-click drag) ---
        self.cursor_move_ring = self.canvas.create_oval(-18, -18, 18, 18,
                                                         outline="#00FFFF", width=2,
                                                         tags=("custom_cursor", "move_cur"))
        self.cursor_move_text = self.canvas.create_text(0, 0, text="✥",
                                                         fill="#00FFFF",
                                                         font=("Arial", 18, "bold"),
                                                         tags=("custom_cursor", "move_cur"))
        self.canvas.itemconfigure(self.cursor_move_ring, state="hidden")
        self.canvas.itemconfigure(self.cursor_move_text, state="hidden")

        # --- Hint bar ---
        hint_bg = self.canvas.create_rectangle(
            w // 2 - 305, 8, w // 2 + 305, 42,
            fill="#1a1a2e", outline="#6366f1", width=1, tags="hint"
        )
        hint_txt = self.canvas.create_text(
            w // 2, 25,
            text="✏️ Trái: Vẽ   |   Phải+Kéo: Di chuyển   |   Ctrl+Z: Undo   |   Esc: Đóng",
            fill="#FFFFFF", font=("Arial", 12, "bold"), tags="hint"
        )
        self.canvas.tag_raise("hint")

        # --- Binds ---
        # Left mouse: draw
        self.canvas.bind("<ButtonPress-1>",    self.on_draw_press)
        self.canvas.bind("<B1-Motion>",         self.on_draw_drag)
        self.canvas.bind("<ButtonRelease-1>",   self.on_draw_release)

        # Right mouse: move
        self.canvas.bind("<ButtonPress-3>",    self.on_move_press)
        self.canvas.bind("<B3-Motion>",         self.on_move_drag)
        self.canvas.bind("<ButtonRelease-3>",   self.on_move_release)

        # Mouse motion (no button): update pencil cursor
        self.canvas.bind("<Motion>", self.on_motion)

        self.overlay.bind("<Escape>",    self.on_escape)
        self.overlay.bind("<Control-z>", self.undo_stroke)
        self.overlay.focus_force()

    # ==========================================
    # PENCIL CURSOR
    # ==========================================

    def show_pencil_cursor(self):
        self.canvas.itemconfigure(self.cursor_tip_cone,  state="normal")
        self.canvas.itemconfigure(self.cursor_body,       state="normal")
        self.canvas.itemconfigure(self.cursor_eraser,     state="normal")
        self.canvas.itemconfigure(self.cursor_tip_point,  state="normal")
        self.canvas.itemconfigure(self.cursor_move_ring,  state="hidden")
        self.canvas.itemconfigure(self.cursor_move_text,  state="hidden")
        self.overlay.config(cursor="none")

    def show_move_cursor(self):
        self.canvas.itemconfigure(self.cursor_tip_cone,  state="hidden")
        self.canvas.itemconfigure(self.cursor_body,       state="hidden")
        self.canvas.itemconfigure(self.cursor_eraser,     state="hidden")
        self.canvas.itemconfigure(self.cursor_tip_point,  state="hidden")
        self.canvas.itemconfigure(self.cursor_move_ring,  state="normal")
        self.canvas.itemconfigure(self.cursor_move_text,  state="normal")
        self.overlay.config(cursor="none")

    def update_pencil_cursor(self, x, y):
        self.canvas.coords(self.cursor_tip_point, x-1, y-1, x+1, y+1)
        self.canvas.coords(self.cursor_tip_cone,  x, y, x+2, y-5, x+5, y-2)
        self.canvas.coords(self.cursor_body,       x+3, y-3, x+10, y-10)
        self.canvas.coords(self.cursor_eraser,     x+10, y-10, x+12, y-12)
        self.canvas.tag_raise("custom_cursor")
        self.canvas.tag_raise("hint")

    def update_move_cursor(self, x, y):
        self.canvas.coords(self.cursor_move_ring, x-18, y-18, x+18, y+18)
        self.canvas.coords(self.cursor_move_text, x, y)
        self.canvas.tag_raise("custom_cursor")
        self.canvas.tag_raise("hint")

    # ==========================================
    # DRAW (LEFT MOUSE)
    # ==========================================

    def on_motion(self, event):
        """Chuột di chuyển không nhấn — chỉ cập nhật pencil cursor."""
        if not self.is_moving:
            self.update_pencil_cursor(event.x, event.y)

    def on_draw_press(self, event):
        self.update_pencil_cursor(event.x, event.y)
        self.last_x, self.last_y = event.x, event.y
        self.strokes.append([])

    def on_draw_drag(self, event):
        self.update_pencil_cursor(event.x, event.y)
        if self.last_x is not None:
            line_id = self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                fill=self.line_color, width=self.line_width,
                capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True
            )
            # Keep cursor and hint on top
            self.canvas.tag_raise("custom_cursor")
            self.canvas.tag_raise("hint")
            if self.strokes:
                self.strokes[-1].append(line_id)
        self.last_x, self.last_y = event.x, event.y

    def on_draw_release(self, event):
        self.update_pencil_cursor(event.x, event.y)
        self.last_x = None
        self.last_y = None

    # ==========================================
    # MOVE (RIGHT MOUSE)
    # ==========================================

    def on_move_press(self, event):
        self.is_moving = True
        self.move_start_x = event.x
        self.move_start_y = event.y
        self.show_move_cursor()
        self.update_move_cursor(event.x, event.y)

    def on_move_drag(self, event):
        if not self.is_moving or self.move_start_x is None:
            return
        dx = event.x - self.move_start_x
        dy = event.y - self.move_start_y
        self.move_start_x = event.x
        self.move_start_y = event.y

        # Di chuyển tất cả các nét vẽ (không di chuyển background, hint, cursor)
        all_stroke_ids = [lid for stroke in self.strokes for lid in stroke]
        for lid in all_stroke_ids:
            self.canvas.move(lid, dx, dy)

        self.update_move_cursor(event.x, event.y)

    def on_move_release(self, event):
        self.is_moving = False
        self.move_start_x = None
        self.move_start_y = None
        self.show_pencil_cursor()
        self.update_pencil_cursor(event.x, event.y)

    # ==========================================
    # UNDO / ESC
    # ==========================================

    def undo_stroke(self, event=None):
        if self.strokes:
            last_stroke = self.strokes.pop()
            for line_id in last_stroke:
                self.canvas.delete(line_id)

    def on_escape(self, event=None):
        self.close_overlay()

    def close_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.bg_image = None

    def quit_app(self, icon=None, item=None):
        if self.icon:
            self.icon.stop()
        self.root.quit()
        os._exit(0)

if __name__ == "__main__":
    app = ScreenMarkerTray()
