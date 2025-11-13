# driver_portal.py
import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import threading, time, os, random

BIN_STATUS_FILE = "bin_status.txt"
TRUCK_STATUS_FILE = "truck_status.txt"

class DriverPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Driver Portal - Smart City Waste Management")
        self.root.geometry("1200x800")
        self.root.config(bg="#0E1623")

        tk.Label(root, text="Driver Dashboard - Active Bin Pickup Map",
                 bg="#0E1623", fg="white", font=("Segoe UI Semibold", 20)).pack(pady=20)

        # Graph
        self.G = nx.Graph()
        self.bins = ["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10"]
        self.positions = {
            "B1": (0,5),"B2": (2,6),"B3": (4,6),"B4": (6,5),
            "B5": (8,4),"B6": (6,3),"B7": (4,2),"B8": (2,2),
            "B9": (0,3),"B10": (1,4)
        }
        self.G.add_edges_from([
            ("B1","B2"),("B2","B3"),("B3","B4"),("B4","B5"),("B5","B6"),
            ("B6","B7"),("B7","B8"),("B8","B9"),("B9","B1"),
            ("B2","B10"),("B10","B8"),("B10","B6")
        ])
        self.blocked_edges = [("B3","B7"),("B5","B9")]
        for e in self.blocked_edges:
            if self.G.has_edge(*e):
                self.G.remove_edge(*e)

        self.selected_bin = None
        self.truck_position = "B1"
        self.bin_levels = {b: 0 for b in self.bins}

        # Plot
        self.fig, self.ax = plt.subplots(figsize=(8,6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_click)

        # Controls
        control_frame = tk.Frame(root, bg="#0E1623")
        control_frame.pack(pady=15)

        tk.Button(control_frame, text="Picked Up", bg="#00B894", fg="white",
                  font=("Segoe UI", 12), relief="flat", command=self.mark_picked_up)\
            .pack(side="left", padx=10)

        tk.Button(control_frame, text="Truck Full - Going to Unload", bg="#E67E22", fg="white",
                  font=("Segoe UI", 12), relief="flat", command=self.truck_full)\
            .pack(side="left", padx=10)

        tk.Button(control_frame, text="Exit", bg="#E74C3C", fg="white",
                  font=("Segoe UI", 12), relief="flat", command=self.root.destroy)\
            .pack(side="left", padx=10)

        # initialize from file if exists
        self.load_bin_status()
        self.load_truck_status()
        # initial draw
        self.update_map()

        # start background sync
        threading.Thread(target=self.sync_from_admin, daemon=True).start()

    # ------------------------ SYNC ------------------------
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
                        # schedule safe redraw
                        try:
                            self.root.after(0, self.update_map)
                        except Exception:
                            pass
                if os.path.exists(TRUCK_STATUS_FILE):
                    self.load_truck_status()
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
                        bin_id, lvl = parts
                        if bin_id in self.bin_levels:
                            self.bin_levels[bin_id] = int(lvl)
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

    # ------------------------ ACTIONS ------------------------
    def on_click(self, event):
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            min_dist = float("inf")
            nearest = None
            for node, (nx_, ny_) in self.positions.items():
                dist = ((x - nx_) ** 2 + (y - ny_) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest = node
            if nearest:
                self.selected_bin = nearest
                try:
                    self.root.after(0, self.update_map)
                except Exception:
                    pass

    def mark_picked_up(self):
        if not self.selected_bin:
            messagebox.showwarning("No Selection", "Select a bin first.")
            return

        # Manually empty the bin (small residual)
        self.bin_levels[self.selected_bin] = random.randint(0, 10)
        self.truck_position = self.selected_bin
        # write files immediately
        self.update_bin_status_file()
        self.update_truck_status_file()
        # redraw safely
        try:
            self.root.after(0, self.update_map)
        except Exception:
            pass
        messagebox.showinfo("Success", f"Bin {self.selected_bin} emptied successfully.")
        self.selected_bin = None

    def truck_full(self):
        self.truck_position = "Depot"
        self.update_truck_status_file()
        try:
            self.root.after(0, self.update_map)
        except Exception:
            pass
        messagebox.showinfo("Truck Status", "Truck is going to unload. Pickups paused temporarily.")

    # ------------------------ FILE WRITES ------------------------
    def update_bin_status_file(self):
        tmp = BIN_STATUS_FILE + ".tmp"
        try:
            with open(tmp, "w") as f:
                for b, lvl in self.bin_levels.items():
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

    # ------------------------ Visualization ------------------------
    def update_map(self):
        self.ax.clear()
        colors = []
        for b in self.bins:
            lvl = self.bin_levels.get(b, 0)
            if b == self.selected_bin:
                colors.append("#F1C40F")
            else:
                if lvl < 40:
                    colors.append("green")
                elif lvl < 70:
                    colors.append("yellow")
                else:
                    colors.append("red")

        node_sizes = [1000 if b == self.truck_position else 700 for b in self.bins]

        nx.draw(self.G, pos=self.positions, ax=self.ax,
                node_color=colors, node_size=node_sizes,
                with_labels=True, font_color="white", edge_color="#AAAAAA", width=2)

        nx.draw_networkx_edges(self.G, pos=self.positions, ax=self.ax,
                               edgelist=self.blocked_edges, edge_color="red",
                               style="dashed", width=2)

        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.ax.set_title(f"Truck at: {self.truck_position}", color="white", fontsize=14)
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        try:
            self.canvas.draw()
        except Exception:
            pass


def start_driver_portal():
    root = tk.Tk()
    DriverPortal(root)
    root.mainloop()


if __name__ == "__main__":
    start_driver_portal()
