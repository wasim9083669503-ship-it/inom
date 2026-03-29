import tkinter as tk
from tkinter import messagebox
import threading
import time
import math
import random
from datetime import datetime

# Import Astra backend
from astra import main, set_ui_callback, face_login

class AstraCompleteUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ASTRA HOLOGRAPHIC HUD - MARK VII")
        self.root.configure(bg='#000000')

        # Window state
        self.is_maximized = False
        self.normal_geometry = None
        self.normal_position = None
        self.is_running = True
        self.astra_running = False

        self.root.geometry("1300x750")
        self.center_window()
        self.root.overrideredirect(True)

        # Cinematic color scheme: Golden & Electric Blue
        self.colors = {
            'bg': '#0a0f1a',           # deep dark blue-black
            'primary': '#e6b91e',      # golden yellow
            'secondary': '#3a86ff',    # bright electric blue
            'accent': '#ff9e3a',       # orange accent
            'danger': '#ff4d4d',
            'success': '#4caf50',
            'glass': '#1a1f2e',        # Solid dark blue-gray (transparency not supported in hex)
            'glass_dark': '#0f1420',
            'title_bg': '#0a0f1a',
            'text_light': '#ffffff',
            'panel_border': '#1d3040',
        }

        # Animation
        self.is_speaking = False
        self.text_angle = 0
        self.particles = []
        self.rotating_text = "Hello Akram"

        # Build UI
        self.setup_custom_titlebar()
        self.setup_main_container()
        self.create_left_panel()
        self.create_right_panel()
        self.create_center_hud()
        self.create_voice_panel()          # new floating panel
        self.create_communication_log()
        self.create_bottom_controls()
        self.create_floating_power_btn()

        self.root.bind('<Configure>', self.on_resize)

        set_ui_callback(self.on_astra_update)
        self.start_animations()
        self.boot_sequence()

    def center_window(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        width = 1300
        height = 750
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.normal_geometry = f"{width}x{height}"
        self.normal_position = (x, y)

    # ================================================================
    # CUSTOM TITLEBAR
    # ================================================================
    def setup_custom_titlebar(self):
        self.title_bar = tk.Frame(self.root, bg=self.colors['title_bg'], height=45)
        self.title_bar.pack(fill=tk.X)
        self.title_bar.pack_propagate(False)

        left = tk.Frame(self.title_bar, bg=self.colors['title_bg'])
        left.pack(side=tk.LEFT, padx=15)
        tk.Label(left, text="▲", font=('Orbitron', 16, 'bold'),
                 fg=self.colors['primary'], bg=self.colors['title_bg']).pack(side=tk.LEFT)
        tk.Label(left, text=" ASTRA MARK VII.1", font=('Orbitron', 12, 'bold'),
                 fg=self.colors['primary'], bg=self.colors['title_bg']).pack(side=tk.LEFT, padx=5)

        sf = tk.Frame(self.title_bar, bg=self.colors['title_bg'])
        sf.pack(side=tk.LEFT, padx=20)
        for text, color in [("CORE", self.colors['success']),
                            ("HUD", self.colors['primary']),
                            ("AI", self.colors['secondary'])]:
            f = tk.Frame(sf, bg=self.colors['title_bg'])
            f.pack(side=tk.LEFT, padx=5)
            tk.Label(f, text="●", font=('Arial', 8), fg=color,
                     bg=self.colors['title_bg']).pack(side=tk.LEFT)
            tk.Label(f, text=text, font=('Orbitron', 9), fg=self.colors['primary'],
                     bg=self.colors['title_bg']).pack(side=tk.LEFT, padx=2)

        self.time_label = tk.Label(self.title_bar, font=('Orbitron', 10),
                                   fg=self.colors['primary'], bg=self.colors['title_bg'])
        self.time_label.pack(side=tk.RIGHT, padx=10)

        ctrl = tk.Frame(self.title_bar, bg=self.colors['title_bg'])
        ctrl.pack(side=tk.RIGHT, padx=5)

        self.min_btn = tk.Button(ctrl, text="─", font=('Arial', 12, 'bold'),
                                  fg='white', bg=self.colors['title_bg'], bd=0,
                                  padx=12, cursor='hand2', command=self.minimize_window)
        self.min_btn.pack(side=tk.LEFT)

        self.max_btn = tk.Button(ctrl, text="□", font=('Arial', 12, 'bold'),
                                  fg='white', bg=self.colors['title_bg'], bd=0,
                                  padx=12, cursor='hand2', command=self.toggle_maximize)
        self.max_btn.pack(side=tk.LEFT)

        self.close_btn = tk.Button(ctrl, text="✕", font=('Arial', 10, 'bold'),
                                    fg='white', bg=self.colors['title_bg'], bd=0,
                                    padx=12, cursor='hand2', command=self.terminate_system)
        self.close_btn.pack(side=tk.LEFT)

        # Hover
        self.min_btn.bind('<Enter>', lambda e: self.min_btn.config(bg='#333333'))
        self.min_btn.bind('<Leave>', lambda e: self.min_btn.config(bg=self.colors['title_bg']))
        self.max_btn.bind('<Enter>', lambda e: self.max_btn.config(bg='#333333'))
        self.max_btn.bind('<Leave>', lambda e: self.max_btn.config(bg=self.colors['title_bg']))
        self.close_btn.bind('<Enter>', lambda e: self.close_btn.config(bg='#ff0055'))
        self.close_btn.bind('<Leave>', lambda e: self.close_btn.config(bg=self.colors['title_bg']))

        # Drag
        for w in [self.title_bar, left, sf]:
            w.bind('<Button-1>', self.start_move)
            w.bind('<B1-Motion>', self.on_move)

    def minimize_window(self):
        """Minimize with overrideredirect workaround"""
        self.root.overrideredirect(False)
        self.root.iconify()
        # Restore overrideredirect when window is shown again
        def on_map(event):
            self.root.overrideredirect(True)
            self.root.unbind('<Map>')
        self.root.bind('<Map>', on_map)

    def toggle_maximize(self):
        if self.is_maximized:
            self.root.geometry(self.normal_geometry)
            x, y = self.normal_position
            self.root.geometry(f"+{x}+{y}")
            self.max_btn.config(text="□")
            self.is_maximized = False
        else:
            self.normal_geometry = self.root.geometry()
            self.normal_position = (self.root.winfo_x(), self.root.winfo_y())
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.root.geometry(f"{sw}x{sh}+0+0")
            self.max_btn.config(text="❐")
            self.is_maximized = True

    def start_move(self, event):
        if not self.is_maximized:
            self.drag_x = event.x
            self.drag_y = event.y

    def on_move(self, event):
        if not self.is_maximized:
            x = self.root.winfo_x() + event.x - self.drag_x
            y = self.root.winfo_y() + event.y - self.drag_y
            self.root.geometry(f"+{x}+{y}")

    def on_resize(self, event=None):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        if hasattr(self, 'left_panel'):
            self.left_panel.place(x=20, y=60, width=320, height=min(380, h - 150))
        if hasattr(self, 'right_panel'):
            self.right_panel.place(x=w - 320, y=60, width=300, height=min(500, h - 150))
        if hasattr(self, 'center_frame'):
            self.center_frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
        if hasattr(self, 'log_frame'):
            self.log_frame.place(x=20, y=h - 200, width=500, height=150)
        if hasattr(self, 'bottom_frame'):
            self.bottom_frame.place(x=0, y=h - 70, relwidth=1, height=70)
        if hasattr(self, 'voice_panel') and hasattr(self, 'voice_panel_visible') and self.voice_panel_visible:
            self.voice_panel.place(x=w//2 - 150, y=h//2 - 60, width=300, height=120)

    # ================================================================
    # MAIN CONTAINER & PANELS
    # ================================================================
    def setup_main_container(self):
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.grid_canvas = tk.Canvas(self.main_container, bg=self.colors['bg'],
                                     highlightthickness=0)
        self.grid_canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def create_left_panel(self):
        self.left_panel = tk.Frame(self.main_container, bg=self.colors['glass'],
                                   highlightthickness=1,
                                   highlightbackground=self.colors['panel_border'])
        self.left_panel.place(x=20, y=60, width=320, height=380)

        tk.Label(self.left_panel, text="SYSTEM STATUS", font=('Orbitron', 12, 'bold'),
                 fg=self.colors['primary'], bg=self.colors['glass']).pack(pady=10)

        self.create_status_item(self.left_panel, "CORE PROCESSOR", "ONLINE", self.colors['success'])

        sub = tk.Frame(self.left_panel, bg=self.colors['glass'])
        sub.pack(fill=tk.X, padx=30, pady=5)
        self.create_status_item(sub, "  • Hologram Mem", "84%", self.colors['primary'], True)
        self.create_status_item(sub, "  • QUANTUM LINK", "STABLE", self.colors['success'], True)
        self.create_status_item(sub, "  • NEURAL NET", "SYNCED", self.colors['success'], True)

        tk.Frame(self.left_panel, height=1, bg=self.colors['panel_border']).pack(
            fill=tk.X, padx=10, pady=10)

        tk.Label(self.left_panel, text="NETWORK STATS", font=('Orbitron', 10, 'bold'),
                 fg=self.colors['accent'], bg=self.colors['glass']).pack(pady=5)
        tk.Label(self.left_panel, text="↑ 83.9 Kbps  |  ↓ 4.5 Mbps",
                 font=('Orbitron', 9), fg=self.colors['primary'],
                 bg=self.colors['glass']).pack()

    def create_right_panel(self):
        w = self.root.winfo_width()
        self.right_panel = tk.Frame(self.main_container, bg=self.colors['glass'],
                                    highlightthickness=1,
                                    highlightbackground=self.colors['panel_border'])
        self.right_panel.place(x=w - 320, y=60, width=300, height=500)

        tk.Label(self.right_panel, text="SECURITY PROTOCOLS", font=('Orbitron', 12, 'bold'),
                 fg=self.colors['primary'], bg=self.colors['glass']).pack(pady=10)

        rf = tk.Frame(self.right_panel, bg=self.colors['glass_dark'],
                      highlightthickness=1, highlightbackground=self.colors['panel_border'])
        rf.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(rf, text="ROUTER", font=('Orbitron', 10, 'bold'),
                 fg=self.colors['accent'], bg=self.colors['glass_dark']).pack(pady=5)
        for name, status in [("CORE", "ACTIVE"), ("HUD", "ACTIVE"), ("AI", "ACTIVE")]:
            row = tk.Frame(rf, bg=self.colors['glass_dark'])
            row.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(row, text=name, font=('Orbitron', 9), fg=self.colors['primary'],
                     bg=self.colors['glass_dark']).pack(side=tk.LEFT)
            tk.Label(row, text=status, font=('Orbitron', 8), fg=self.colors['success'],
                     bg=self.colors['glass_dark']).pack(side=tk.RIGHT)

        tk.Frame(self.right_panel, height=1, bg=self.colors['panel_border']).pack(
            fill=tk.X, padx=10, pady=10)

        of = tk.Frame(self.right_panel, bg=self.colors['glass'])
        of.pack(fill=tk.X, padx=15, pady=10)
        tk.Label(of, text="OPTIONS", font=('Orbitron', 10, 'bold'),
                 fg=self.colors['accent'], bg=self.colors['glass']).pack(pady=5)
        for opt in ["FACE RECOGNITION", "VOICE AUTH", "NEURAL SCAN", "BIOMETRIC"]:
            row = tk.Frame(of, bg=self.colors['glass'])
            row.pack(fill=tk.X, padx=15, pady=2)
            tk.Label(row, text=opt, font=('Orbitron', 9), fg=self.colors['primary'],
                     bg=self.colors['glass']).pack(side=tk.LEFT)
            tk.Label(row, text="ACTIVE", font=('Orbitron', 8, 'bold'),
                     fg=self.colors['success'], bg=self.colors['glass']).pack(side=tk.RIGHT)

    def create_status_item(self, parent, label, value, color, is_sub=False):
        f = tk.Frame(parent, bg=self.colors['glass'])
        f.pack(fill=tk.X, padx=(0 if is_sub else 15), pady=3)
        tk.Label(f, text=label, font=('Orbitron', 9 if is_sub else 10),
                 fg=self.colors['primary'], bg=self.colors['glass']).pack(side=tk.LEFT)
        tk.Label(f, text=value, font=('Orbitron', 9 if is_sub else 10, 'bold'),
                 fg=color, bg=self.colors['glass']).pack(side=tk.RIGHT)

    # ================================================================
    # CENTER HUD
    # ================================================================
    def create_center_hud(self):
        self.center_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        self.center_frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        self.cx, self.cy = 125, 125
        self.circle_r = 100

        self.voice_canvas = tk.Canvas(self.center_frame, width=250, height=250,
                                       bg=self.colors['bg'], highlightthickness=0)
        self.voice_canvas.pack()

        # Main circle
        self.center_circle = self.voice_canvas.create_oval(
            self.cx - self.circle_r, self.cy - self.circle_r,
            self.cx + self.circle_r, self.cy + self.circle_r,
            outline=self.colors['primary'], fill='', width=3)

        # Dash rings
        self.rings = []
        for i in range(3):
            r = 60 + i * 15
            ring = self.voice_canvas.create_oval(self.cx - r, self.cy - r,
                                                  self.cx + r, self.cy + r,
                                                  outline=self.colors['secondary'],
                                                  width=1, dash=(5, 5))
            self.rings.append(ring)

        # Radial lines
        self.radial_lines = []
        for i in range(12):
            a = math.radians(i * 30)
            r1, r2 = self.circle_r - 10, self.circle_r + 8
            x1 = self.cx + r1 * math.cos(a)
            y1 = self.cy + r1 * math.sin(a)
            x2 = self.cx + r2 * math.cos(a)
            y2 = self.cy + r2 * math.sin(a)
            line = self.voice_canvas.create_line(x1, y1, x2, y2,
                                                  fill=self.colors['primary'], width=2)
            self.radial_lines.append(line)

        # Central orb
        self.central_orb = self.voice_canvas.create_oval(
            self.cx - 18, self.cy - 18, self.cx + 18, self.cy + 18,
            fill=self.colors['primary'], outline=self.colors['secondary'], width=2)

        # Labels
        self.listening_label = tk.Label(self.center_frame, text="LISTENING",
                                         font=('Orbitron', 14, 'bold'),
                                         fg=self.colors['primary'], bg=self.colors['bg'])
        self.listening_label.pack(pady=5)

        self.voice_status = tk.Label(self.center_frame, text="Voice capture active",
                                      font=('Orbitron', 9), fg=self.colors['secondary'],
                                      bg=self.colors['bg'])
        self.voice_status.pack()

        # Particles
        self.particles = []
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(0, self.circle_r + 20)
            x = self.cx + radius * math.cos(angle)
            y = self.cy + radius * math.sin(angle)
            pid = self.voice_canvas.create_oval(x - 1, y - 1, x + 1, y + 1,
                                                 fill=self.colors['primary'], outline='')
            self.particles.append({'id': pid, 'radius': radius, 'angle': angle,
                                   'speed': random.uniform(0.5, 2)})

    # ================================================================
    # LOG & CONTROLS
    # ================================================================
    def create_communication_log(self):
        h = self.root.winfo_height()
        self.log_frame = tk.Frame(self.main_container, bg=self.colors['glass'],
                                   highlightthickness=1,
                                   highlightbackground=self.colors['panel_border'])
        self.log_frame.place(x=20, y=h - 200, width=500, height=150)

        hdr = tk.Frame(self.log_frame, bg=self.colors['glass'])
        hdr.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(hdr, text="COMMUNICATION LOG", font=('Orbitron', 10, 'bold'),
                 fg=self.colors['primary'], bg=self.colors['glass']).pack(side=tk.LEFT)
        tk.Button(hdr, text="CLEAR", font=('Orbitron', 8), fg=self.colors['accent'],
                  bg=self.colors['glass'], bd=0, cursor='hand2',
                  command=lambda: [self.log_text.delete(1.0, tk.END),
                                   self.add_log("LOG CLEARED")]).pack(side=tk.RIGHT)

        self.log_text = tk.Text(self.log_frame, bg='#030810', fg=self.colors['primary'],
                                 font=('Courier', 9), bd=0, wrap=tk.WORD, padx=10, pady=5)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def create_bottom_controls(self):
        h = self.root.winfo_height()
        self.bottom_frame = tk.Frame(self.main_container, bg='#111111')
        self.bottom_frame.place(x=0, y=h - 70, relwidth=1, height=70)

        bf = tk.Frame(self.bottom_frame, bg='#111111')
        bf.pack(expand=True)

        # Buttons list - make sure TERMINATE is included
        buttons = [
            ("CORE ONLINE", self.colors['success'], self.core_online),
            ("HOLOGRAM", self.colors['primary'], self.hologram_mode),
            ("TERMINATE", self.colors['danger'], self.terminate_system)   # ✅ Terminate button
        ]

        for text, color, cmd in buttons:
            btn = tk.Button(bf, text=text, command=cmd, font=('Orbitron', 11, 'bold'),
                            fg=color, bg='#000000', bd=2, relief=tk.FLAT,
                            cursor='hand2', padx=25, pady=8)
            btn.pack(side=tk.LEFT, padx=15)
            btn.bind('<Enter>', lambda e, b=btn, c=color: b.config(fg='black', bg=c))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(fg=c, bg='#000000'))

    def create_floating_power_btn(self):
        """Small floating icon to terminate the system"""
        self.pwr_frame = tk.Frame(self.main_container, bg=self.colors['bg'], bd=0)
        self.pwr_frame.place(relx=0.96, rely=0.88, anchor=tk.CENTER)

        self.pwr_btn = tk.Button(self.pwr_frame, text="⏻", font=('Orbitron', 18, 'bold'),
                                  fg=self.colors['danger'], bg=self.colors['bg'],
                                  bd=1, relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground=self.colors['danger'],
                                  padx=10, pady=5, cursor='hand2',
                                  command=self.terminate_system)
        self.pwr_btn.pack()

        # Hover effects
        self.pwr_btn.bind('<Enter>', lambda e: self.pwr_btn.config(bg=self.colors['danger'], fg='black'))
        self.pwr_btn.bind('<Leave>', lambda e: self.pwr_btn.config(bg=self.colors['bg'], fg=self.colors['danger']))

    # ================================================================
    # ANIMATIONS
    # ================================================================
    def start_animations(self):
        self.animate_rotating_text()
        self.animate_glow()
        self.animate_particles()
        self.animate_radial()
        self.animate_grid()
        self.update_time()

    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)

    def animate_rotating_text(self):
        if not self.is_running: return
        self.voice_canvas.delete("rot")

        tr = self.circle_r + 25
        color = self.colors['secondary'] if self.is_speaking else self.colors['primary']
        fs = 10 if self.is_speaking else 8
        full = f"  {self.rotating_text}  ·  ASTRA ONLINE  ·  "
        step = (2 * math.pi) / max(len(full), 1)
        off = math.radians(self.text_angle)

        for i, ch in enumerate(full):
            a = off + i * step
            x = self.cx + tr * math.cos(a)
            y = self.cy + tr * math.sin(a)
            self.voice_canvas.create_text(x, y, text=ch, font=('Consolas', fs),
                                           fill=color, tags="rot")
        self.text_angle = (self.text_angle + 1) % 360
        self.root.after(50, self.animate_rotating_text)

    def animate_glow(self):
        if not self.is_running: return
        t = time.time()

        if self.is_speaking:
            pw = 3 + 3 * math.sin(t * 12)
            self.voice_canvas.itemconfig(self.center_circle, width=pw)
            orb_r = 18 + 8 * abs(math.sin(t * 8))
            self.voice_canvas.coords(self.central_orb,
                                      self.cx - orb_r, self.cy - orb_r,
                                      self.cx + orb_r, self.cy + orb_r)
            self.voice_canvas.itemconfig(self.central_orb, fill=self.colors['secondary'],
                                          outline='white')
            for i, ring in enumerate(self.rings):
                w = 2 + math.sin(t * 10 + i)
                self.voice_canvas.itemconfig(ring, width=w,
                                              dash=(max(1, int(t * 10) % 20), 5))
        else:
            pw = 2 + 1 * math.sin(t * 2)
            self.voice_canvas.itemconfig(self.center_circle, width=pw)
            orb_r = 18 + 3 * math.sin(t * 1.5)
            self.voice_canvas.coords(self.central_orb,
                                      self.cx - orb_r, self.cy - orb_r,
                                      self.cx + orb_r, self.cy + orb_r)
            self.voice_canvas.itemconfig(self.central_orb, fill=self.colors['primary'],
                                          outline=self.colors['secondary'])
            for ring in self.rings:
                self.voice_canvas.itemconfig(ring, width=1, dash=(5, 5))

        self.root.after(40, self.animate_glow)

    def animate_particles(self):
        if not self.is_running: return
        pc = self.colors['secondary'] if self.is_speaking else self.colors['primary']
        for p in self.particles:
            p['radius'] += p['speed'] * (0.6 if self.is_speaking else 0.3)
            if p['radius'] > self.circle_r + 30:
                p['radius'] = 0
            x = self.cx + p['radius'] * math.cos(p['angle'])
            y = self.cy + p['radius'] * math.sin(p['angle'])
            self.voice_canvas.coords(p['id'], x - 1, y - 1, x + 1, y + 1)
            self.voice_canvas.itemconfig(p['id'], fill=pc)
        self.root.after(50, self.animate_particles)

    def animate_radial(self):
        if not self.is_running: return
        if self.is_speaking:
            rot = time.time() * 60
            for i, line in enumerate(self.radial_lines):
                a = math.radians(i * 30 + rot)
                r1 = self.circle_r - 10
                r2 = self.circle_r + 8 + 6 * math.sin(time.time() * 5 + i)
                self.voice_canvas.coords(line,
                    self.cx + r1 * math.cos(a), self.cy + r1 * math.sin(a),
                    self.cx + r2 * math.cos(a), self.cy + r2 * math.sin(a))
                self.voice_canvas.itemconfig(line, width=3)
        else:
            for i, line in enumerate(self.radial_lines):
                a = math.radians(i * 30)
                r1, r2 = self.circle_r - 10, self.circle_r + 8
                self.voice_canvas.coords(line,
                    self.cx + r1 * math.cos(a), self.cy + r1 * math.sin(a),
                    self.cx + r2 * math.cos(a), self.cy + r2 * math.sin(a))
                self.voice_canvas.itemconfig(line, width=2)
        self.root.after(40, self.animate_radial)

    def animate_grid(self):
        if not self.is_running: return
        self.grid_canvas.delete("grid")
        # Grid lines removed for cinematic look
        self.root.after(500, self.animate_grid)

    # ================================================================
    # ASTRA INTEGRATION
    # ================================================================
    def on_astra_update(self, text):
        """Thread-safe UI update using after()"""
        self.root.after(0, self._update_ui_state, text)

    def _update_ui_state(self, text):
        raw = text.lower()
        if "password bolo" in raw:
            self.listening_label.config(text="SAY PASSWORD 🎤", fg=self.colors['danger'])
            self.voice_status.config(text="Microphone listening...")
            self.add_log(f"🤖 {text}")
        elif "listening" in raw or "🎙️" in raw:
            self.is_speaking = False
            self.listening_label.config(text="🎤 LISTENING", fg=self.colors['primary'])
            self.voice_status.config(text="Voice capture active")
        elif "thinking" in raw or "processing" in raw or "🧠" in raw:
            self.is_speaking = True
            self.listening_label.config(text="🧠 THINKING", fg=self.colors['secondary'])
            self.voice_status.config(text="Generating response...")
        elif "speaking" in raw:
            self.is_speaking = True
            self.listening_label.config(text="🔊 SPEAKING", fg=self.colors['primary'])
            self.voice_status.config(text="Transmitting audio...")
        else:
            self.add_log(f"🤖 {text}")
            self.is_speaking = True
            # Update panel with Astra's response
            self.show_voice_panel(f"🤖 Astra: {text}")
            # Stay in speaking/glow state for a few seconds
            self.root.after(4000, self.reset_idle)

    def create_voice_panel(self):
        """Floating panel that shows real-time voice interaction"""
        self.voice_panel = tk.Frame(self.main_container, bg='#1a1f2e', bd=2, relief=tk.SOLID)
        self.voice_panel.config(highlightbackground=self.colors['primary'], highlightthickness=2)
        self.voice_panel.place_forget()
        self.voice_panel_visible = False
        
        self.voice_panel_label = tk.Label(self.voice_panel, text="",
                                          font=('Orbitron', 10),
                                          fg=self.colors['primary'],
                                          bg='#1a1f2e',
                                          wraplength=280,
                                          justify=tk.CENTER)
        self.voice_panel_label.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def show_voice_panel(self, message):
        """Show the voice panel with a message"""
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.voice_panel_label.config(text=message)
        self.voice_panel.place(x=w//2 - 150, y=h//2 - 60, width=300, height=120)
        self.voice_panel.lift()
        self.voice_panel_visible = True
        
        # Auto-hide after 3.5 seconds
        self.root.after(3500, self.hide_voice_panel)

    def hide_voice_panel(self):
        if hasattr(self, 'voice_panel'):
            self.voice_panel.place_forget()
        self.voice_panel_visible = False

    def reset_idle(self):
        # Only reset if we're not currently busy
        if hasattr(self, 'current_state') and self.current_state in ["THINKING", "SPEAKING"]:
             return
        self.is_speaking = False
        self.listening_label.config(text="LISTENING", fg=self.colors['primary'])
        self.voice_status.config(text="Voice capture active")

    def add_log(self, msg):
        ts = datetime.now().strftime("[%H:%M:%S]")
        self.log_text.insert(tk.END, f"{ts} ➔ {msg}\n")
        self.log_text.see(tk.END)

    def boot_sequence(self):
        msgs = ["⚙️ SYSTEM BOOT: HOLOGRAPHIC INTERFACE ONLINE",
                "⚙️ QUANTUM PROCESSOR: ACTIVE",
                "⚙️ NEURAL LINK: ESTABLISHED",
                "🤖 WELCOME, AKRAM. SYSTEM INITIALIZING..."]
        def show(i=0):
            if i < len(msgs):
                self.add_log(msgs[i])
                self.root.after(1000, lambda: show(i + 1))
            else:
                self.start_astra()
        self.root.after(500, show)

    def start_astra(self):
        if self.astra_running: return
        def run():
            self.astra_running = True
            self.add_log("⚙️ INITIATING VOICE ENGINE")
            if face_login():
                self.add_log("🤖 VOICE SYSTEM ONLINE.")
                self.is_speaking = True
                self.root.after(2000, self.reset_idle)
                main()
            else:
                self.add_log("🤖 ACCESS DENIED.")
                self.astra_running = False
        threading.Thread(target=run, daemon=True).start()

    def core_online(self):
        self.add_log("CORE SYSTEM: INITIALIZED")
        self.start_astra()

    def hologram_mode(self):
        self.add_log("HOLOGRAM MODE: ACTIVATED")
        self.is_speaking = True
        self.root.after(2000, self.reset_idle)

    def terminate_system(self):
        if messagebox.askyesno("Terminate", "Are you sure you want to terminate the system?"):
            self.add_log("SYSTEM: SHUTTING DOWN...")
            self.is_running = False
            self.root.after(500, self.root.destroy)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AstraCompleteUI()
    app.run()
