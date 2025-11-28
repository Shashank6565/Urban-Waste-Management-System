import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import threading, time, os, random

# Shared absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_STATUS_FILE = os.path.join(BASE_DIR, "bin_status.txt")
TRUCK_STATUS_FILE = os.path.join(BASE_DIR, "truck_status.txt")
REQUEST_FILE = os.path.join(BASE_DIR, "requests.txt")

# Styling (Neo Dark Tech - Balanced Neon)
BG = "#07121A"            # page background
CARD = "#071A24"          # card background
PANEL = "#0B2632"         # panel background
NEON = "#00E5FF"          # neon cyan
BTN_NEON = "#00BFA5"
TEXT = "#E6F7FA"
MUTED = "#9fb4be"

class DriverPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Driver Portal - Smart City Waste Management")
        self.root.geometry("1360x820")
        self.root.config(bg=BG)

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=(12,6))
        tk.Label(header, text="DRIVER DASHBOARD", bg=BG, fg=NEON,
                 font=("Segoe UI Black", 22)).pack()
        tk.Label(header, text="Active Bin Pickup • Priority: URGENT", bg=BG, fg=MUTED,
                 font=("Segoe UI", 11)).pack(pady=(2,8))

        # Main layout
        main = tk.Frame(root, bg=BG)
        main.pack(fill="both", expand=True, padx=18, pady=8)

        # Left: Map Card
        map_card = tk.Frame(main, bg=PANEL, bd=0, relief="flat")
        map_card.pack(side="left", fill="both", expand=True, padx=(0, 12), pady=6)

        # Map card header (neon underline)
        mh = tk.Frame(map_card, bg=PANEL)
        mh.pack(fill="x", pady=(8,0))
        tk.Label(mh, text="📍 City Bin Map", bg=PANEL, fg=NEON,
                 font=("Segoe UI Semibold", 14)).pack(anchor="w", padx=12)
        tk.Frame(mh, bg=NEON, height=2).pack(fill="x", padx=12, pady=(6,8))

        # Matplotlib canvas
        self.G = nx.Graph()
        self.bins = ["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10"]
        self.positions = {"B1":(0,5),"B2":(2,6),"B3":(4,6),"B4":(6,5),
                          "B5":(8,4),"B6":(6,3),"B7":(4,2),"B8":(2,2),
                          "B9":(0,3),"B10":(1,4)}
        self.G.add_edges_from([("B1","B2"),("B2","B3"),("B3","B4"),("B4","B5"),
                               ("B5","B6"),("B6","B7"),("B7","B8"),("B8","B9"),
                               ("B9","B1"),("B2","B10"),("B10","B8"),("B10","B6")])
        self.blocked_edges = [("B3","B7"),("B5","B9")]
        self.blocked = list(self.blocked_edges)
        for e in self.blocked_edges:
            if self.G.has_edge(*e):
                self.G.remove_edge(*e)

        self.selected_bin = None
        self.truck_position = "B1"
        self.bin_levels = {b: 0 for b in self.bins}
        self.urgent_bins = set()

        self.fig, self.ax = plt.subplots(figsize=(9,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_card)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0,12))
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Right: Controls Card
        ctrl_card = tk.Frame(main, bg=CARD, width=320)
        ctrl_card.pack(side="right", fill="y", pady=6)
        ctrl_card.pack_propagate(False)

        tk.Label(ctrl_card, text="Controls", bg=CARD, fg=NEON, font=("Segoe UI Semibold", 14)).pack(pady=(16,6))
        tk.Frame(ctrl_card, bg=NEON, height=2).pack(fill="x", padx=12, pady=(0,12))

        # Urgent list
        tk.Label(ctrl_card, text="Urgent Bins", bg=CARD, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w", padx=14)
        self.urgent_list = tk.Listbox(ctrl_card, bg="#072027", fg=TEXT, height=8, bd=0, highlightthickness=0,
                                     selectbackground=BTN_NEON)
        self.urgent_list.pack(fill="x", padx=14, pady=(6,12))

        # Buttons (neon style)
        btn_frame = tk.Frame(ctrl_card, bg=CARD)
        btn_frame.pack(fill="x", padx=14)

        self._make_button(btn_frame, "Mark Picked Up", BTN_NEON, self.mark_picked_up).pack(fill="x", pady=8)
        self._make_button(btn_frame, "Truck Full → Unload", "#FF8A50", self.truck_full).pack(fill="x", pady=8)
        self._make_button(btn_frame, "Refresh Status", NEON, self.manual_refresh).pack(fill="x", pady=8)
        self._make_button(btn_frame, "Exit", "#E05353", root.destroy).pack(fill="x", pady=8)

        # Legend
        legend = tk.Frame(ctrl_card, bg=CARD)
        legend.pack(fill="x", padx=14, pady=(12,14))
        self._legend_item(legend, "#2ECC71", "Low")
        self._legend_item(legend, "#F1C40F", "Medium")
        self._legend_item(legend, "#E74C3C", "High")
        self._legend_item(legend, "#D50000", "URGENT")

        # Initialize & start sync
        self.load_bin_status()
        self.load_truck_status()
        self.load_urgent_bins()
        self.update_map()
        threading.Thread(target=self.sync_from_admin, daemon=True).start()

    # small helpers
    def _make_button(self, parent, text, color, cmd):
        b = tk.Button(parent, text=text, bg=color, fg="white", relief="flat",
                      activebackground=color, activeforeground="white", font=("Segoe UI", 11),
                      command=cmd, bd=0)
        return b

    def _legend_item(self, parent, color, label):
        f = tk.Frame(parent, bg=CARD)
        f.pack(side="left", padx=6)
        sw = tk.Canvas(f, width=18, height=14, bg=CARD, highlightthickness=0)
        sw.create_rectangle(0,0,18,14, fill=color, outline=color)
        sw.pack(side="left")
        tk.Label(f, text=label, bg=CARD, fg=MUTED, font=("Segoe UI",10)).pack(side="left", padx=6)

    # Sync / IO
    def sync_from_admin(self):
        last_mtime = 0
        while True:
            time.sleep(2)
            try:
                if os.path.exists(BIN_STATUS_FILE):
                    mtime = os.path.getmtime(BIN_STATUS_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        self.load_bin_status()
                        self.root.after(0, self.update_map)
                if os.path.exists(TRUCK_STATUS_FILE):
                    self.load_truck_status()
                self.load_urgent_bins()
            except Exception as e:
                print("⚠️ Sync error in Driver Portal:", e)

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

    def load_truck_status(self):
        if not os.path.exists(TRUCK_STATUS_FILE):
            return
        try:
            with open(TRUCK_STATUS_FILE, "r") as f:
                for line in f:
                    if line.startswith("TruckAt:"):
                        self.truck_position = line.strip().split(":",1)[1]
        except Exception as e:
            print("⚠️ Error reading truck_status.txt:", e)

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
            self.update_urgent_list()
            try:
                self.root.after(0, self.update_map)
            except:
                pass

    def update_urgent_list(self):
        self.urgent_list.delete(0, "end")
        if not self.urgent_bins:
            self.urgent_list.insert("end", "No urgent bins")
        else:
            for b in sorted(self.urgent_bins):
                self.urgent_list.insert("end", f"{b} (URGENT)")

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

    def mark_picked_up(self):
        if not self.selected_bin:
            messagebox.showwarning("No Selection", "Select a bin first.")
            return
        self.bin_levels[self.selected_bin] = random.randint(0,10)
        self.truck_position = self.selected_bin
        self.remove_urgent(self.selected_bin)
        self.update_bin_status_file()
        self.update_truck_status_file()
        messagebox.showinfo("Success", f"Collected bin {self.selected_bin}. URGENT cleared.")
        self.selected_bin = None
        self.root.after(0, self.update_map)

    def truck_full(self):
        self.truck_position = "Depot"
        try:
            self.update_truck_status_file()
        except:
            pass
        try:
            self.root.after(0, self.update_map)
        except:
            pass
        messagebox.showinfo("Truck Status", "Truck marked as FULL and is going to unload.")


    def manual_refresh(self):
        """Manual refresh for urgent bins, bin levels and truck position."""
        try:
            self.load_bin_status()
            self.load_truck_status()
            self.load_urgent_bins()
            self.update_map()
        except Exception as e:
            print("⚠️ Manual refresh error:", e)

    # File writes
    def update_bin_status_file(self):
        tmp = BIN_STATUS_FILE + ".tmp"
        try:
            with open(tmp, "w") as f:
                for b,lvl in self.bin_levels.items():
                    f.write(f"{b}:{lvl}\n")
            os.replace(tmp, BIN_STATUS_FILE)
        except Exception as e:
            print("⚠️ Failed to write bin status:", e)

    def update_truck_status_file(self):
        tmp = TRUCK_STATUS_FILE + ".tmp"
        try:
            with open(tmp, "w") as f:
                f.write(f"TruckAt:{self.truck_position}\n")
            os.replace(tmp, TRUCK_STATUS_FILE)
        except Exception as e:
            print("⚠️ Failed to write truck status:", e)

    def remove_urgent(self, bin_id):
        if os.path.exists(REQUEST_FILE):
            try:
                with open(REQUEST_FILE, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open(REQUEST_FILE, "w", encoding="utf-8") as f:
                    for line in lines:
                        if not line.strip().startswith(f"{bin_id}:URGENT"):
                            f.write(line)
                self.load_urgent_bins()
            except Exception as e:
                print("⚠️ Failed to update requests:", e)

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

        sizes = [1100 if b==self.truck_position else 700 for b in self.bins]

        nx.draw(self.G, pos=self.positions, ax=self.ax,
                node_color=colors, node_size=sizes,
                with_labels=True, font_color="white",
                edge_color="#81D4FA", width=1.6)

        # blocked edges
        nx.draw_networkx_edges(self.G, pos=self.positions, ax=self.ax,
                               edgelist=self.blocked, edge_color="#FF6F00",
                               style="dashed", width=2)

        # urgent labels
        for b in self.urgent_bins:
            if b in self.positions:
                x,y = self.positions[b]
                self.ax.text(x, y-0.25, "URGENT", color="#FF1744",
                             fontsize=10, fontweight="bold", ha="center")

        self.ax.set_facecolor(PANEL)
        self.fig.patch.set_facecolor(PANEL)
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        try:
            self.canvas.draw()
        except:
            pass

def start_driver_portal():
    root = tk.Tk()
    DriverPortal(root)
    root.mainloop()

if __name__ == "__main__":
    start_driver_portal()
