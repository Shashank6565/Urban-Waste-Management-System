import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random
import os

BIN_STATUS_FILE = "bin_status.txt"
DRIVER_STATUS_FILE = "driver_status.txt"

class DriverPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Driver Portal - Smart City Waste Management")
        self.root.geometry("1200x800")
        self.root.config(bg="#0E1623")

        tk.Label(
            root, text="Driver Dashboard - Active Bin Pickup Map",
            bg="#0E1623", fg="white", font=("Segoe UI Semibold", 20)
        ).pack(pady=20)

        # Frame for map
        frame = tk.Frame(root, bg="#0E1623")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create map
        self.G = nx.Graph()
        self.bins = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10"]
        self.positions = {
            "B1": (0, 5), "B2": (2, 6), "B3": (4, 6), "B4": (6, 5),
            "B5": (8, 4), "B6": (6, 3), "B7": (4, 2), "B8": (2, 2),
            "B9": (0, 3), "B10": (1, 4)
        }
        self.G.add_edges_from([
            ("B1", "B2"), ("B2", "B3"), ("B3", "B4"),
            ("B4", "B5"), ("B5", "B6"), ("B6", "B7"),
            ("B7", "B8"), ("B8", "B9"), ("B9", "B1"),
            ("B2", "B10"), ("B10", "B8"), ("B10", "B6")
        ])
        self.blocked_edges = [("B3", "B7"), ("B5", "B9")]
        for e in self.blocked_edges:
            if self.G.has_edge(*e):
                self.G.remove_edge(*e)

        self.selected_bin = None
        self.truck_status = "Active"
        self.bin_levels = {b: random.randint(10, 100) for b in self.bins}

        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.update_map()

        # Buttons
        control_frame = tk.Frame(root, bg="#0E1623")
        control_frame.pack(pady=20)

        tk.Button(control_frame, text="Picked Up", bg="#00B894", fg="white",
                  font=("Segoe UI", 12), relief="flat",
                  command=self.mark_picked_up).pack(side="left", padx=10)

        tk.Button(control_frame, text="Truck Full - Going to Unload", bg="#E67E22", fg="white",
                  font=("Segoe UI", 12), relief="flat",
                  command=self.truck_full).pack(side="left", padx=10)

        tk.Button(control_frame, text="Exit", bg="#E74C3C", fg="white",
                  font=("Segoe UI", 12), relief="flat",
                  command=self.root.destroy).pack(side="left", padx=10)

        # Save initial data
        self.save_bin_status()
        self.save_driver_status()

    # ------------------------ MAP DRAW ------------------------
    def update_map(self):
        self.ax.clear()
        colors = []
        for b in self.bins:
            lvl = self.bin_levels[b]
            if lvl < 40:
                colors.append("green")
            elif lvl < 70:
                colors.append("yellow")
            else:
                colors.append("red")

        node_sizes = [1000 if b == self.selected_bin else 700 for b in self.bins]

        nx.draw(self.G, pos=self.positions, ax=self.ax,
                node_color=colors, node_size=node_sizes,
                with_labels=True, font_color="white", edge_color="#AAAAAA", width=2)

        nx.draw_networkx_edges(self.G, pos=self.positions, ax=self.ax,
                               edgelist=self.blocked_edges, edge_color="red",
                               style="dashed", width=2)

        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.ax.set_title(f"Truck Status: {self.truck_status}", color="white", fontsize=14)
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        self.canvas.draw()

    # ------------------------ CLICK NODE ------------------------
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
                self.update_map()

    # ------------------------ ACTIONS ------------------------
    def mark_picked_up(self):
        if not self.selected_bin:
            messagebox.showwarning("No Selection", "Select a bin first.")
            return

        self.bin_levels[self.selected_bin] = random.randint(0, 10)
        self.truck_status = f"Picked up {self.selected_bin}"
        self.update_map()
        self.save_bin_status()
        self.save_driver_status()
        messagebox.showinfo("Success", f"Bin {self.selected_bin} emptied successfully.")
        self.selected_bin = None

    def truck_full(self):
        self.truck_status = "Truck Full - Unloading"
        self.update_map()
        self.save_driver_status()
        messagebox.showinfo("Truck Status", "Truck is going to unload. Pickups paused temporarily.")

    # ------------------------ FILE SYNC ------------------------
    def save_bin_status(self):
        """Save the current bin fill levels so Admin/User can access"""
        with open(BIN_STATUS_FILE, "w") as f:
            for b, lvl in self.bin_levels.items():
                f.write(f"{b}:{lvl}\n")

    def save_driver_status(self):
        """Save truck state for Admin"""
        with open(DRIVER_STATUS_FILE, "w") as f:
            f.write(f"TruckStatus:{self.truck_status}\n")


def start_driver_portal():
    root = tk.Tk()
    DriverPortal(root)
    root.mainloop()


if __name__ == "__main__":
    start_driver_portal()
