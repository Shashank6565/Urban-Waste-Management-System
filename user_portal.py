import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import threading, time, os

# Shared absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_STATUS_FILE = os.path.join(BASE_DIR, "bin_status.txt")
REQUEST_FILE = os.path.join(BASE_DIR, "requests.txt")

# Styling
BG = "#07121A"
PANEL = "#0B2632"
CARD = "#071A24"
NEON = "#00E5FF"
TEXT = "#E6F7FA"
MUTED = "#9fb4be"

class UserPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("User Portal - Smart City Waste Management")
        self.root.geometry("1200x800")
        self.root.config(bg=BG)

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=(14,6))
        tk.Label(header, text="USER DASHBOARD", bg=BG, fg=NEON, font=("Segoe UI Black", 20)).pack()
        tk.Label(header, text="Report overflowing or damaged bins", bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(pady=(2,8))

        # Main layout
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=8)

        # Left: Map Card
        map_card = tk.Frame(main, bg=PANEL)
        map_card.pack(side="left", fill="both", expand=True, padx=(0,12), pady=6)
        tk.Label(map_card, text="📍 City Bin Map - Click to Select", bg=PANEL, fg=NEON, font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12, pady=(10,6))
        tk.Frame(map_card, bg=NEON, height=2).pack(fill="x", padx=12, pady=(0,10))

        # Graph setup
        self.G = nx.Graph()
        self.bins = ["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10"]
        self.positions = {"B1":(0,5),"B2":(2,6),"B3":(4,6),"B4":(6,5),
                          "B5":(8,4),"B6":(6,3),"B7":(4,2),"B8":(2,2),
                          "B9":(0,3),"B10":(1,4)}
        self.G.add_edges_from([("B1","B2"),("B2","B3"),("B3","B4"),("B4","B5"),
                               ("B5","B6"),("B6","B7"),("B7","B8"),("B8","B9"),
                               ("B9","B1"),("B2","B10"),("B10","B8"),("B10","B6")])
        self.blocked_edges = [("B3","B7"),("B5","B9")]
        for e in self.blocked_edges:
            if self.G.has_edge(*e):
                self.G.remove_edge(*e)

        self.selected_bin = None
        self.bin_levels = {b: 0 for b in self.bins}
        self.urgent_bins = set()

        self.fig, self.ax = plt.subplots(figsize=(9,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0,12))
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Right: Control Card
        ctrl_card = tk.Frame(main, bg=CARD, width=320)
        ctrl_card.pack(side="right", fill="y", pady=6)
        ctrl_card.pack_propagate(False)

        tk.Label(ctrl_card, text="Report", bg=CARD, fg=NEON, font=("Segoe UI Semibold", 14)).pack(pady=(16,6))
        tk.Frame(ctrl_card, bg=NEON, height=2).pack(fill="x", padx=12, pady=(0,12))

        self.info_label = tk.Label(ctrl_card, text="Select a bin on the map and click Report", bg=CARD, fg=MUTED, wraplength=260, justify="left", font=("Segoe UI",10))
        self.info_label.pack(padx=12, pady=(6,12))

        self.report_btn = tk.Button(ctrl_card, text="Report Selected Bin (Mark URGENT)", bg=NEON, fg="black",
                                    font=("Segoe UI Semibold", 11), relief="flat", command=self.report_bin)
        self.report_btn.pack(fill="x", padx=14, pady=(6,10))

        self.exit_btn = tk.Button(ctrl_card, text="Exit", bg="#E05353", fg="white", font=("Segoe UI",11), relief="flat", command=self.root.destroy)
        self.exit_btn.pack(fill="x", padx=14, pady=(6,14))

        # Legend
        legend = tk.Frame(ctrl_card, bg=CARD)
        legend.pack(fill="x", padx=12, pady=(8,12))

        # Start sync
        self.load_bin_status()
        self.load_urgent_bins()
        self.update_map()
        threading.Thread(target=self.sync_data_loop, daemon=True).start()

    def _legend_item(self, parent, color, label):
        f = tk.Frame(parent, bg=CARD)
        f.pack(side="left", padx=6)
        sw = tk.Canvas(f, width=18, height=14, bg=CARD, highlightthickness=0)
        sw.create_rectangle(0,0,18,14, fill=color, outline=color)
        sw.pack(side="left")
        tk.Label(f, text=label, bg=CARD, fg=MUTED, font=("Segoe UI",10)).pack(side="left", padx=6)

    # Sync
    def sync_data_loop(self):
        while True:
            time.sleep(2)
            try:
                if os.path.exists(BIN_STATUS_FILE):
                    self.load_bin_status()
                    self.root.after(0, self.update_map)
                self.load_urgent_bins()  # keep urgent set updated
            except Exception as e:
                print("⚠️ Sync error in User Portal:", e)

    def load_bin_status(self):
        if not os.path.exists(BIN_STATUS_FILE):
            return
        try:
            with open(BIN_STATUS_FILE, "r") as f:
                for line in f:
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        b, lvl = parts
                        if b in self.bin_levels:
                            try:
                                self.bin_levels[b] = int(lvl)
                            except:
                                pass
        except Exception as e:
            print("⚠️ Error reading bin_status.txt:", e)

    def load_urgent_bins(self):
        new_set = set()
        try:
            if os.path.exists(REQUEST_FILE):
                with open(REQUEST_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        ln = line.strip()
                        if ln.endswith(":URGENT"):
                            bid = ln.split(":")[0]
                            if bid in self.bins:
                                new_set.add(bid)
        except Exception as e:
            print("⚠️ Error reading requests:", e)

        if new_set != self.urgent_bins:
            self.urgent_bins = new_set
            self.root.after(0, self.update_map)

    # Actions
    def on_click(self, event):
        if event.inaxes == self.ax:
            x,y = event.xdata, event.ydata
            nearest, md = None, float("inf")
            for node,(nx_,ny_) in self.positions.items():
                d = ((x-nx_)**2 + (y-ny_)**2)**0.5
                if d < md:
                    md = d; nearest = node
            self.selected_bin = nearest
            self.root.after(0, self.update_map)

    def report_bin(self):
        if not self.selected_bin:
            messagebox.showwarning("No Selection", "Please select a bin to report.")
            return
        # Write a clean URGENT entry
        try:
            with open(REQUEST_FILE, "a", encoding="utf-8") as f:
                f.write(f"{self.selected_bin}:URGENT\n")
            messagebox.showinfo("Reported", f"{self.selected_bin} marked as URGENT.")
            self.selected_bin = None
            self.root.after(0, self.update_map)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write report: {e}")

    # Visualization
    def update_map(self):
        self.ax.clear()
        colors = []
        for b in self.bins:
            if b in self.urgent_bins:
                colors.append("#D50000")
            elif b == self.selected_bin:
                colors.append("#FFC400")
            else:
                lvl = self.bin_levels.get(b,0)
                if lvl < 40: colors.append("#2ECC71")
                elif lvl < 70: colors.append("#F1C40F")
                else: colors.append("#E74C3C")

        node_sizes = [900 if b==self.selected_bin else 700 for b in self.bins]

        nx.draw(self.G, pos=self.positions, ax=self.ax,
                node_color=colors, node_size=node_sizes,
                with_labels=True, font_color="white",
                edge_color="#81D4FA", width=1.6)

        nx.draw_networkx_edges(self.G, pos=self.positions, ax=self.ax,
                               edgelist=self.blocked_edges, edge_color="#FF6F00",
                               style="dashed", width=2)

        for b in self.urgent_bins:
            if b in self.positions:
                x,y = self.positions[b]
                self.ax.text(x, y-0.28, "URGENT", color="#FF1744",
                             fontsize=10, fontweight="bold", ha="center")

        self.ax.set_facecolor(PANEL)
        self.fig.patch.set_facecolor(PANEL)
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

        try:
            self.canvas.draw()
        except Exception:
            pass

def start_user_portal():
    root = tk.Tk()
    UserPortal(root)
    root.mainloop()

if __name__ == "__main__":
    start_user_portal()
