import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random, threading, time

# =================== SIMULATION CLASS ===================
class GarbageMapSimulation:
    def __init__(self, parent, request_listbox):
        self.parent = parent
        self.request_listbox = request_listbox
        self.running = True

        # Create realistic imperfect layout of bins (map)
        self.G = nx.Graph()
        self.bins = [
            "B1", "B2", "B3", "B4", "B5",
            "B6", "B7", "B8", "B9", "B10"
        ]
        self.G.add_nodes_from(self.bins)

        # Imperfect map coordinates (like a city sector)
        self.positions = {
            "B1": (0, 5), "B2": (2, 6), "B3": (4, 6), "B4": (6, 5),
            "B5": (8, 4), "B6": (6, 3), "B7": (4, 2), "B8": (2, 2),
            "B9": (0, 3), "B10": (1, 4)
        }

        # Add realistic roads (not all bins directly connected)
        self.G.add_edges_from([
            ("B1", "B2"), ("B2", "B3"), ("B3", "B4"),
            ("B4", "B5"), ("B5", "B6"), ("B6", "B7"),
            ("B7", "B8"), ("B8", "B9"), ("B9", "B1"),
            ("B2", "B10"), ("B10", "B8"), ("B10", "B6")
        ])

        # Roads truck cannot take (blocked / no direct route)
        self.blocked_edges = [("B3", "B7"), ("B5", "B9")]

        # Remove blocked routes
        for edge in self.blocked_edges:
            if self.G.has_edge(*edge):
                self.G.remove_edge(*edge)

        # Initial fill levels
        self.fill_levels = {b: random.randint(10, 60) for b in self.bins}
        self.truck_position = random.choice(self.bins)

        # Matplotlib setup
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Start background simulation
        threading.Thread(target=self.simulate, daemon=True).start()

    def color_for_fill(self, level):
        if level < 40:
            return "green"
        elif level < 70:
            return "yellow"
        else:
            return "red"

    def update_graph(self):
        self.ax.clear()
        colors = [self.color_for_fill(self.fill_levels[b]) for b in self.bins]
        node_sizes = [1000 if b == self.truck_position else 700 for b in self.bins]

        nx.draw(
            self.G, pos=self.positions, ax=self.ax,
            node_color=colors, node_size=node_sizes,
            with_labels=True, font_color="white", edge_color="#AAAAAA", width=2
        )

        # Highlight blocked routes
        nx.draw_networkx_edges(
            self.G, pos=self.positions, ax=self.ax,
            edgelist=self.blocked_edges, edge_color="red", style="dashed", width=2
        )

        self.ax.set_title("Sector Map: Garbage Collection Routes", color="white", fontsize=14)
        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        self.canvas.draw()

    def move_truck(self, target):
        try:
            path = nx.shortest_path(self.G, self.truck_position, target)
            for step in path:
                self.truck_position = step
                self.update_graph()
                time.sleep(0.5)
        except nx.NetworkXNoPath:
            # No valid route
            pass

    def simulate(self):
        while self.running:
            time.sleep(1.5)
            # Random fill growth
            for b in self.bins:
                self.fill_levels[b] = min(100, self.fill_levels[b] + random.randint(0, 8))

            # Truck collects from full bins
            full_bins = [b for b, lvl in self.fill_levels.items() if lvl >= 75]
            if full_bins:
                target = random.choice(full_bins)
                self.move_truck(target)
                self.fill_levels[target] = random.randint(5, 20)

            self.update_graph()

    def stop(self):
        self.running = False


# =================== ADMIN PORTAL CLASS ===================
class AdminPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Portal - Smart City Waste Management")
        self.root.geometry("1400x800")
        self.root.config(bg="#0E1623")

        tk.Label(
            root, text="Admin Dashboard - City Sector Map",
            bg="#0E1623", fg="white", font=("Segoe UI Semibold", 20)
        ).pack(pady=20)

        # Layout split
        main_frame = tk.Frame(root, bg="#0E1623")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: Map visualization
        map_frame = tk.Frame(main_frame, bg="#0E1623")
        map_frame.pack(side="left", fill="both", expand=True)

        # Right: Side panel (Requests)
        side_panel = tk.Frame(main_frame, bg="#111B2B", width=300)
        side_panel.pack(side="right", fill="y")
        tk.Label(
            side_panel, text="📩 View Requests",
            bg="#111B2B", fg="white", font=("Segoe UI Bold", 14)
        ).pack(pady=10)

        self.request_listbox = tk.Listbox(side_panel, bg="#192A3C", fg="white", font=("Segoe UI", 11),
                                          height=25, width=30, selectbackground="#00B894")
        self.request_listbox.pack(padx=10, pady=10, fill="both")

        # Add dummy requests (these will come from user module later)
        self.sample_requests = ["Bin B3 - Overflow reported", "Bin B7 - Missed pickup",
                                "Bin B9 - Full for 2 days"]
        for req in self.sample_requests:
            self.request_listbox.insert("end", req)

        tk.Button(
            side_panel, text="Refresh Requests", bg="#00B894", fg="white",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            command=self.refresh_requests
        ).pack(pady=5)

        tk.Button(
            side_panel, text="Close", bg="#E74C3C", fg="white",
            font=("Segoe UI", 10), relief="flat", cursor="hand2",
            command=root.destroy
        ).pack(pady=5)

        # Simulation
        self.simulation = GarbageMapSimulation(map_frame, self.request_listbox)

    def refresh_requests(self):
        self.request_listbox.delete(0, "end")
        # In future: read from user requests file or backend
        new_requests = ["Bin B4 - Reported by User", "Bin B1 - Overflow", "Bin B8 - Delay complaint"]
        for req in new_requests:
            self.request_listbox.insert("end", req)


# =================== RUN ADMIN PORTAL ===================
def start_admin_portal():
    app = tk.Tk()
    AdminPortal(app)
    app.mainloop()

if __name__ == "__main__":
    start_admin_portal()
