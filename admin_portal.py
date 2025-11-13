# admin_portal.py
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

# =================== PORTAL ===================
class AdminPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Portal - Smart City Waste Management")
        self.root.geometry("1400x800")
        self.root.config(bg="#0E1623")

        tk.Label(root, text="Admin Dashboard - City Sector Map",
                 bg="#0E1623", fg="white", font=("Segoe UI Semibold", 20)).pack(pady=20)

        # ======= Layout =======
        main_frame = tk.Frame(root, bg="#0E1623")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        map_frame = tk.Frame(main_frame, bg="#0E1623")
        map_frame.pack(side="left", fill="both", expand=True)

        side_panel = tk.Frame(main_frame, bg="#111B2B", width=300)
        side_panel.pack(side="right", fill="y")

        tk.Label(side_panel, text="📩 View User Reports",
                 bg="#111B2B", fg="white", font=("Segoe UI Bold", 14)).pack(pady=10)

        self.request_listbox = tk.Listbox(side_panel, bg="#192A3C", fg="white",
                                          font=("Segoe UI", 11), height=25,
                                          selectbackground="#00B894")
        self.request_listbox.pack(padx=10, pady=10, fill="both")

        tk.Button(side_panel, text="Refresh Reports", bg="#00B894", fg="white",
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  command=self.refresh_requests).pack(pady=5)
        tk.Button(side_panel, text="Close", bg="#E74C3C", fg="white",
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  command=root.destroy).pack(pady=5)

        # ----- mode label
        self.mode_label = tk.Label(side_panel, text="Mode: Hybrid (Auto-Fill, Manual Pickup)",
                                   bg="#111B2B", fg="#74B9FF", font=("Segoe UI", 10))
        self.mode_label.pack(pady=(6, 12), padx=10)

        # ======= Map & Backend =======
        self.G = self.create_graph()
        self.positions = self.get_positions()
        self.bins = list(self.G.nodes)
        self.truck_position = "B1"
        self.fill_levels = {b: 0 for b in self.bins}

        # Matplotlib setup (must be created in main thread)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # ======= Try loading backend =======
        self.have_backend = False
        try:
            self.backend = CDLL(BACKEND_FILE)
            if hasattr(self.backend, "init_heap"):
                self.have_backend = True
                print("✅ Backend connected successfully!")
        except Exception as e:
            print("⚠️ Failed to load backend:", e)
            print("Running in simulation mode.")

        # Hybrid flags (Admin fills, Driver empties)
        self.simulation_running = True   # bins will auto-fill
        self.auto_pickup = False         # no auto pickup in Hybrid mode

        # Start background threads
        threading.Thread(target=self.simulate, daemon=True).start()
        threading.Thread(target=self.sync_from_driver, daemon=True).start()

    # =================== Map Setup ===================
    def create_graph(self):
        G = nx.Graph()
        edges = [
            ("B1", "B2"), ("B2", "B3"), ("B3", "B4"),
            ("B4", "B5"), ("B5", "B6"), ("B6", "B7"),
            ("B7", "B8"), ("B8", "B9"), ("B9", "B1"),
            ("B2", "B10"), ("B10", "B8"), ("B10", "B6")
        ]
        G.add_edges_from(edges)
        return G

    def get_positions(self):
        return {
            "B1": (0, 5), "B2": (2, 6), "B3": (4, 6), "B4": (6, 5),
            "B5": (8, 4), "B6": (6, 3), "B7": (4, 2), "B8": (2, 2),
            "B9": (0, 3), "B10": (1, 4)
        }

    # =================== Simulation (Hybrid) ===================
    def simulate(self):
        """Admin auto-fills bins; does NOT auto-empty (Driver empties manually)."""
        while True:
            time.sleep(2)
            if self.have_backend:
                # Read backend values (if available)
                for i, b in enumerate(self.bins):
                    try:
                        level = int(self.backend.get_bin_fill_level(c_int(i)))
                        self.fill_levels[b] = level
                    except Exception:
                        pass
                # truck position from backend if available
                try:
                    pos = self.backend.get_truck_position().decode()
                    if pos:
                        self.truck_position = pos
                except Exception:
                    pass
            else:
                # Simple auto-increment fill only
                if self.simulation_running:
                    for b in self.bins:
                        if self.fill_levels[b] < 100:
                            self.fill_levels[b] = min(100, self.fill_levels[b] + random.randint(0, 8))
                # NO auto-pickup in Hybrid mode

            # Save for Driver/User sync (always overwrite atomically)
            try:
                self.save_status_files()
            except Exception:
                pass

            # Schedule safe GUI update on main thread
            try:
                self.root.after(0, self.update_map)
            except Exception:
                break

    # =================== File Sync ===================
    def save_status_files(self):
        tmp = BIN_STATUS_FILE + ".tmp"
        with open(tmp, "w") as f:
            for b in self.bins:
                f.write(f"{b}:{self.fill_levels[b]}\n")
        os.replace(tmp, BIN_STATUS_FILE)

        tmp2 = TRUCK_STATUS_FILE + ".tmp"
        with open(tmp2, "w") as f:
            f.write(f"TruckAt:{self.truck_position}\n")
        os.replace(tmp2, TRUCK_STATUS_FILE)

    # =================== Sync from Driver ===================
    def sync_from_driver(self):
        """Continuously read latest bin levels written by driver (if any)."""
        last_mtime = 0
        while True:
            time.sleep(2)
            try:
                if os.path.exists(BIN_STATUS_FILE):
                    mtime = os.path.getmtime(BIN_STATUS_FILE)
                    if mtime != last_mtime:
                        last_mtime = mtime
                        with open(BIN_STATUS_FILE, "r") as f:
                            changed = False
                            for line in f:
                                parts = line.strip().split(":")
                                if len(parts) == 2:
                                    b, lvl = parts
                                    if b in self.fill_levels:
                                        val = int(lvl)
                                        if self.fill_levels[b] != val:
                                            self.fill_levels[b] = val
                                            changed = True
                        if changed:
                            # update GUI safely
                            try:
                                self.root.after(0, self.update_map)
                            except Exception:
                                pass
            except Exception as e:
                print("⚠️ Sync error in Admin Portal:", e)

    # =================== Visualization ===================
    def update_map(self):
        self.ax.clear()
        colors = [self.color_for_fill(self.fill_levels[b]) for b in self.bins]
        node_sizes = [900 if b == self.truck_position else 700 for b in self.bins]

        nx.draw(self.G, pos=self.positions, ax=self.ax,
                node_color=colors, node_size=node_sizes,
                with_labels=True, font_color="white",
                edge_color="#AAAAAA", width=2)

        self.ax.set_title("Admin Live Map - Backend + File Sync", color="white", fontsize=14)
        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        try:
            self.canvas.draw()
        except Exception:
            pass

    def color_for_fill(self, level):
        if level < 40:
            return "green"
        elif level < 70:
            return "yellow"
        else:
            return "red"

    def refresh_requests(self):
        self.request_listbox.delete(0, "end")
        try:
            with open("requests.txt", "r") as f:
                for line in f:
                    self.request_listbox.insert("end", line.strip())
        except FileNotFoundError:
            self.request_listbox.insert("end", "No requests yet.")


# =================== RUN ADMIN PORTAL ===================
def start_admin_portal():
    app = tk.Tk()
    AdminPortal(app)
    app.mainloop()


if __name__ == "__main__":
    start_admin_portal()
