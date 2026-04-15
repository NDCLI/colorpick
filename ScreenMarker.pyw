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
        self.root.withdraw() # Ẩn cửa sổ chính để chạy ngầm
        self.root.title("Screen Marker Background")

        self.overlay = None
        self.bg_image = None
        self.strokes = []

        # Tạo System Tray Icon
        self.setup_tray()
        
        # Đăng ký phím tắt Alt+D toàn cục
        try:
            keyboard.add_hotkey('alt+d', self.trigger_drawing, suppress=True)
            print("Hotkey Alt+D activated. App is running in background.")
        except Exception as e:
            print(f"Hotkey registration error: {e}")

        # Vòng lặp chính của GUI luôn chạy ngầm
        self.root.mainloop()

    def create_tray_image(self):
        # Tạo icon riêng cho App hiển thị dưới góc màn hình
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
        
        # Chạy Tray Icon trong luồng riêng để không chặn luồng chính Tkinter
        threading.Thread(target=self.icon.run, daemon=True).start()

    def trigger_drawing_from_tray(self, icon, item):
        self.trigger_drawing()

    def trigger_drawing(self):
        # Các lệnh Tkinter phải gọi qua luồng chính để tránh crash
        self.root.after(0, self.open_overlay)

    def open_overlay(self):
        # Nếu đang vẽ rồi thì bỏ qua
        if self.overlay is not None:
            return
            
        self.strokes = []
        self.overlay = tk.Toplevel(self.root)
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-topmost', True)
        
        # Hide the real cursor to use our custom one
        self.overlay.config(cursor="none")
        
        # Chụp màn hình khoanh vùng
        w = self.overlay.winfo_screenwidth()
        h = self.overlay.winfo_screenheight()
        bg_pil = ImageGrab.grab(bbox=(0, 0, w, h))
        self.bg_image = ImageTk.PhotoImage(bg_pil)
        
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        self.line_color = "#FF00FF"
        self.line_width = 2
        self.last_x = None
        self.last_y = None
        
        # Create custom pencil cursor (tilted right, rounded body)
        # 1. Pencil Tip (Cone)
        self.cursor_tip_cone = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#FFE0B2", tags="custom_cursor")
        # 2. Pencil Body (Rounded)
        self.cursor_body = self.canvas.create_line(0, 0, 0, 0, width=5, capstyle=tk.ROUND, fill="#FFCC00", tags="custom_cursor")
        # 3. Eraser (Round cap)
        self.cursor_eraser = self.canvas.create_line(0, 0, 0, 0, width=5, capstyle=tk.ROUND, fill="#FF6666", tags="custom_cursor")
        # 4. Lead point
        self.cursor_tip_point = self.canvas.create_oval(0, 0, 0, 0, fill="black", tags="custom_cursor")
        
        # Gắn phím tắt cho giao diện vẽ overlay
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.update_cursor) # Follow mouse
        self.overlay.bind("<Escape>", self.on_escape)
        self.overlay.bind("<Control-z>", self.undo_stroke)
        
        # Ép màn hình vẽ lên trên cùng ngay lập tức
        self.overlay.focus_force()

    def update_cursor(self, event):
        """Updates the position of the custom rounded pencil cursor."""
        x, y = event.x, event.y
        # 1. Lead point (tiny dot)
        self.canvas.coords(self.cursor_tip_point, x-1, y-1, x+1, y+1)
        # 2. Sharpened cone (polygon)
        self.canvas.coords(self.cursor_tip_cone, 
            x, y, 
            x+2, y-5, 
            x+5, y-2
        )
        # 3. Rounded body (Line)
        # Offset slightly to meet the cone
        self.canvas.coords(self.cursor_body, x+3, y-3, x+10, y-10)
        # 4. Eraser (small bit at the end)
        self.canvas.coords(self.cursor_eraser, x+10, y-10, x+12, y-12)
        
        # Raise all cursor parts above lines
        self.canvas.tag_raise("custom_cursor")

    def on_press(self, event):
        self.update_cursor(event)
        self.last_x, self.last_y = event.x, event.y
        self.strokes.append([])

    def on_drag(self, event):
        self.update_cursor(event)
        if self.last_x is not None and self.last_y is not None:
            line_id = self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                fill=self.line_color, width=self.line_width,
                capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True
            )
            if self.strokes:
                self.strokes[-1].append(line_id)
        self.last_x, self.last_y = event.x, event.y

    def on_release(self, event):
        self.update_cursor(event)
        self.last_x = None
        self.last_y = None

    def undo_stroke(self, event=None):
        if self.strokes:
            last_stroke = self.strokes.pop()
            for line_id in last_stroke:
                self.canvas.delete(line_id)

    def on_escape(self, event=None):
        # Tắt bút vẽ -> ẩn overlay, app lại ngầm đợi Alt+D
        self.close_overlay()

    def close_overlay(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
            self.bg_image = None # Giảm tối đa RAM

    def quit_app(self, icon=None, item=None):
        """Thoát hoàn toàn dọn dẹp bộ nhớ"""
        if self.icon:
            self.icon.stop()
        self.root.quit()
        os._exit(0)

if __name__ == "__main__":
    app = ScreenMarkerTray()
