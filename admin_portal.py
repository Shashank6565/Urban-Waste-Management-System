# ----------------------------------------------
#  ADMIN PORTAL – Neo Dark Tech (Balanced Neon, map neon outline)
#  UI polished only — no backend/logic changes
# ----------------------------------------------

import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random, threading, time, os
from ctypes import CDLL, c_int

# =================== CONFIG ===================
BACKEND_FILE = "./backend.dll"
BIN_STATUS_FILE = "bin_status.txt"
TRUCK_STATUS_FILE = "truck_status.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REQUEST_FILE = os.path.join(BASE_DIR, "requests.txt")

# =================== THEME (Neo Dark Tech - Balanced Neon) ===================
BG = "#07121A"
PANEL = "#0B2632"
CARD = "#071A24"
MAP_BG = "#0F1B24"
NEON = "#00E5FF"
NEON_DIM = "#00BFA5"
TEXT = "#E6F7FA"
MUTED = "#9fb4be"
ACCENT = "#74B9FF"

# =================== PORTAL ===================
class AdminPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Portal - Smart City Waste Management")
        self.root.geometry("1500x850")
        self.root.config(bg=BG)

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=(14, 6))
        tk.Label(header, text="ADMIN DASHBOARD", bg=BG, fg=NEON,
                 font=("Segoe UI Black", 26)).pack()
        tk.Label(header, text="City Sector Waste Monitoring Panel", bg=BG, fg=MUTED,
                 font=("Segoe UI", 13)).pack(pady=(2, 12))

        # Main container
        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True, padx=18, pady=8)

        # ======= LEFT: Map area with neon outline =======
        # Neon outline frame (simulates neon border)
        neon_border = tk.Frame(container, bg=NEON, bd=0)
        neon_border.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=6)

        # inner map card (slightly inset to show neon border)
        map_card = tk.Frame(neon_border, bg=MAP_BG, bd=0, relief="flat")
        map_card.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Label(map_card, text="📍 Live Smart City Map", bg=MAP_BG,
                 fg=ACCENT, font=("Segoe UI Semibold", 15)).pack(pady=10, anchor="w", padx=12)

        # ======= RIGHT: Reports / Controls card =======
        right_card = tk.Frame(container, bg=CARD, bd=0, relief="flat", width=360)
        right_card.pack(side="right", fill="y", pady=6)
        right_card.pack_propagate(False)

        tk.Label(right_card, text="📩 User Reports", bg=CARD, fg=NEON,
                 font=("Segoe UI Semibold", 15)).pack(pady=(18, 6))

        # request listbox with polished scrollbar
        list_frame = tk.Frame(right_card, bg=CARD)
        list_frame.pack(padx=14, pady=(4,12), fill="both", expand=False)

        self.request_listbox = tk.Listbox(
            list_frame,
            bg="#072027",
            fg=TEXT,
            font=("Segoe UI", 11),
            height=18,
            selectbackground=NEON_DIM,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.request_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.request_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.request_listbox.config(yscrollcommand=scrollbar.set)

        # Buttons Group (polished)
        btn_frame = tk.Frame(right_card, bg=CARD)
        btn_frame.pack(pady=(6, 12), padx=14, fill="x")

        tk.Button(
            btn_frame,
            text="Refresh Reports",
            bg=NEON_DIM,
            fg="black",
            font=("Segoe UI Semibold", 10),
            width=18,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6,
            bd=0,
            command=self.refresh_requests
        ).pack(pady=6, fill="x")

        tk.Button(
            btn_frame,
            text="Close",
            bg="#E05353",
            fg="white",
            font=("Segoe UI Semibold", 10),
            width=18,
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=6,
            bd=0,
            command=root.destroy,
        ).pack(pady=6, fill="x")

        # Mode label
        self.mode_label = tk.Label(right_card,
                                   text="Mode: Hybrid (Auto Fill + Manual Pickup)",
                                   bg=CARD, fg=ACCENT, font=("Segoe UI", 11))
        self.mode_label.pack(pady=(8, 14), padx=14, anchor="w")

        # ======= Map & Backend =======
        self.G = self.create_graph()
        self.positions = self.get_positions()
        self.bins = list(self.G.nodes)
        self.truck_position = "B1"
        self.fill_levels = {b: 0 for b in self.bins}
        self.urgent_bins = set()

        # Matplotlib setup inside map_card
        self.fig, self.ax = plt.subplots(figsize=(9, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=(6, 12), padx=8)

        # ======= Load backend =======
        self.have_backend = False
        try:
            self.backend = CDLL(BACKEND_FILE)
            if hasattr(self.backend, "init_heap"):
                self.have_backend = True
                print("Backend Connected!")
        except Exception:
            print("Backend not found. Simulation mode active.")

        # Simulation flags
        self.simulation_running = True
        self.auto_pickup = False

        # Start threads
        threading.Thread(target=self.simulate, daemon=True).start()
        threading.Thread(target=self.sync_from_driver, daemon=True).start()
        threading.Thread(target=self.auto_refresh_reports, daemon=True).start()

    # =================== Graph Setup ===================
    def create_graph(self):
        G = nx.Graph()
        edges = [
            ("B1","B2"),("B2","B3"),("B3","B4"),("B4","B5"),
            ("B5","B6"),("B6","B7"),("B7","B8"),("B8","B9"),
            ("B9","B1"),("B2","B10"),("B10","B8"),("B10","B6")
        ]
        G.add_edges_from(edges)
        return G

    def get_positions(self):
        return {
            "B1":(0,5),"B2":(2,6),"B3":(4,6),"B4":(6,5),"B5":(8,4),
            "B6":(6,3),"B7":(4,2),"B8":(2,2),"B9":(0,3),"B10":(1,4)
        }

    # =================== Simulation ===================
    def simulate(self):
        while True:
            time.sleep(2)
            if self.have_backend:
                # Read from backend
                for i, b in enumerate(self.bins):
                    try:
                        level = int(self.backend.get_bin_fill_level(c_int(i)))
                        self.fill_levels[b] = level
                    except:
                        pass

                try:
                    pos = self.backend.get_truck_position().decode()
                    if pos:
                        self.truck_position = pos
                except:
                    pass
            else:
                if self.simulation_running:
                    for b in self.bins:
                        self.fill_levels[b] = min(100, self.fill_levels[b] + random.randint(0, 7))

            # Save & update
            try: self.save_status_files()
            except: pass

            try: self.root.after(0, self.update_map)
            except: break

    # =================== File Sync ===================
    def save_status_files(self):
        # Bins
        tmp = BIN_STATUS_FILE + ".tmp"
        with open(tmp, "w") as f:
            for b in self.bins:
                f.write(f"{b}:{self.fill_levels[b]}\n")
        os.replace(tmp, BIN_STATUS_FILE)

        # Truck
        tmp2 = TRUCK_STATUS_FILE + ".tmp"
        with open(tmp2, "w") as f:
            f.write(f"TruckAt:{self.truck_position}\n")
        os.replace(tmp2, TRUCK_STATUS_FILE)

    # =================== Sync from Driver ===================
    def sync_from_driver(self):
        last_mtime = 0
        while True:
            time.sleep(2)
            try:
                if os.path.exists(BIN_STATUS_FILE):
                    mtime = os.path.getmtime(BIN_STATUS_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(BIN_STATUS_FILE, "r") as f:
                            for line in f:
                                try:
                                    b, lvl = line.strip().split(":")
                                    lvl = int(lvl)
                                    if b in self.fill_levels:
                                        self.fill_levels[b] = lvl
                                except:
                                    pass
                        self.root.after(0, self.update_map)
                # keep truck status in sync
                if os.path.exists(TRUCK_STATUS_FILE):
                    self.load_truck_status()
                # keep urgent list synced too
                self.refresh_requests()
            except:
                pass

    # =================== Visualization ===================
    def update_map(self):
        self.ax.clear()

        node_colors = []
        for b in self.bins:
            if hasattr(self, "urgent_bins") and b in self.urgent_bins:
                node_colors.append("#D32F2F")   # urgent red
            else:
                lvl = self.fill_levels[b]
                if lvl < 40:
                    node_colors.append("#2ECC71")   # green
                elif lvl < 70:
                    node_colors.append("#F1C40F")   # yellow
                else:
                    node_colors.append("#E74C3C")   # full red

        node_sizes = [980 if b == self.truck_position else 700 for b in self.bins]

        nx.draw(
            self.G,
            pos=self.positions,
            ax=self.ax,
            node_color=node_colors,
            node_size=node_sizes,
            with_labels=True,
            font_color="white",
            edge_color="#95A5A6",
            width=2
        )

        # urgent label text
        if hasattr(self, "urgent_bins"):
            for b in self.urgent_bins:
                if b in self.positions:
                    x, y = self.positions[b]
                    self.ax.text(
                        x, y - 0.25, "URGENT",
                        color="#FF5252",
                        fontsize=10,
                        fontweight="bold",
                        ha="center"
                    )

        # subtle neon footer for map
        self.ax.set_title("Live City Waste Status", fontsize=14, color=TEXT)
        self.ax.set_facecolor(MAP_BG)
        self.fig.patch.set_facecolor(MAP_BG)

        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        try:
            self.canvas.draw()
        except:
            pass

    def color_for_fill(self, lvl):
        if lvl < 40: return "#2ECC71"
        elif lvl < 70: return "#F1C40F"
        else: return "#E74C3C"

    # =================== Reports ===================
    def refresh_requests(self):
        self.request_listbox.delete(0, "end")
        self.urgent_bins = set()

        try:
            if os.path.exists(REQUEST_FILE):
                with open(REQUEST_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        if ":URGENT" in line:
                            bin_id = line.split(":")[0]
                            self.urgent_bins.add(bin_id)
                            self.request_listbox.insert("end", f"{bin_id} - URGENT")
                        else:
                            self.request_listbox.insert("end", line)

            if not self.urgent_bins and self.request_listbox.size() == 0:
                self.request_listbox.insert("end", "No requests yet.")

        except Exception as e:
            self.request_listbox.insert("end", f"Error: {e}")

    # =================== Auto Refresh ===================
    def auto_refresh_reports(self):
        while True:
            time.sleep(2)
            try:
                self.root.after(0, self.refresh_requests)
            except:
                pass

# =================== RUN ===================
def start_admin_portal():
    app = tk.Tk()
    AdminPortal(app)
    app.mainloop()

if __name__ == "__main__":
    start_admin_portal()
