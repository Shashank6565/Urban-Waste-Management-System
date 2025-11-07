import tkinter as tk
from tkinter import messagebox
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import random

REQUEST_FILE = "requests.txt"  # Shared file between User & Admin portals

class UserPortal:
    def __init__(self, root):
        self.root = root
        self.root.title("User Portal - Smart City Waste Management")
        self.root.geometry("1200x800")
        self.root.config(bg="#0E1623")

        tk.Label(
            root, text="User Dashboard - Report Overflowing Bin",
            bg="#0E1623", fg="white", font=("Segoe UI Semibold", 20)
        ).pack(pady=20)

        # Graph setup
        frame = tk.Frame(root, bg="#0E1623")
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Map initialization (same layout as Admin)
        self.G = nx.Graph()
        self.bins = [
            "B1", "B2", "B3", "B4", "B5",
            "B6", "B7", "B8", "B9", "B10"
        ]
        self.positions = {
            "B1": (0, 5), "B2": (2, 6), "B3": (4, 6), "B4": (6, 5),
            "B5": (8, 4), "B6": (6, 3), "B7": (4, 2), "B8": (2, 2),
            "B9": (0, 3), "B10": (1, 4)
        }

        # Edges (roads)
        self.G.add_edges_from([
            ("B1", "B2"), ("B2", "B3"), ("B3", "B4"),
            ("B4", "B5"), ("B5", "B6"), ("B6", "B7"),
            ("B7", "B8"), ("B8", "B9"), ("B9", "B1"),
            ("B2", "B10"), ("B10", "B8"), ("B10", "B6")
        ])
        self.blocked_edges = [("B3", "B7"), ("B5", "B9")]

        for edge in self.blocked_edges:
            if self.G.has_edge(*edge):
                self.G.remove_edge(*edge)

        self.selected_bin = None
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.draw_map()

        # Bind click event
        self.cid = self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # Controls
        control_frame = tk.Frame(root, bg="#0E1623")
        control_frame.pack(pady=10)
        self.report_button = tk.Button(
            control_frame, text="Report Selected Bin", bg="#E67E22", fg="white",
            font=("Segoe UI", 12), relief="flat", command=self.report_bin
        )
        self.report_button.pack(side="left", padx=10)
        tk.Button(
            control_frame, text="Exit", bg="#E74C3C", fg="white",
            font=("Segoe UI", 12), relief="flat", command=self.root.destroy
        ).pack(side="left", padx=10)

    def draw_map(self):
        self.ax.clear()

        nx.draw(
            self.G,
            pos=self.positions,
            ax=self.ax,
            with_labels=True,
            node_color=["#4CAF50"] * len(self.bins),
            node_size=700,
            font_color="white",
            edge_color="#999999",
            width=2
        )

        # Draw blocked roads (red dashed)
        nx.draw_networkx_edges(
            self.G,
            pos=self.positions,
            ax=self.ax,
            edgelist=self.blocked_edges,
            edge_color="red",
            style="dashed",
            width=2
        )

        self.ax.set_title("Sector Map - Select a Bin to Report", color="white", fontsize=14)
        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        self.canvas.draw()

    def on_click(self, event):
        # Find nearest node to mouse click
        if event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            min_dist = float("inf")
            nearest_node = None
            for node, (nx_, ny_) in self.positions.items():
                dist = ((x - nx_) ** 2 + (y - ny_) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = node

            if nearest_node:
                self.selected_bin = nearest_node
                self.highlight_selected_bin()

    def highlight_selected_bin(self):
        self.ax.clear()

        colors = []
        for node in self.bins:
            if node == self.selected_bin:
                colors.append("#F1C40F")  # Highlight yellow
            else:
                colors.append("#4CAF50")

        nx.draw(
            self.G,
            pos=self.positions,
            ax=self.ax,
            with_labels=True,
            node_color=colors,
            node_size=700,
            font_color="white",
            edge_color="#999999",
            width=2
        )

        nx.draw_networkx_edges(
            self.G,
            pos=self.positions,
            ax=self.ax,
            edgelist=self.blocked_edges,
            edge_color="red",
            style="dashed",
            width=2
        )

        self.ax.set_title(f"Selected: {self.selected_bin}", color="white", fontsize=14)
        self.ax.set_facecolor("#0E1623")
        self.fig.patch.set_facecolor("#0E1623")
        self.canvas.draw()

    def report_bin(self):
        if not self.selected_bin:
            messagebox.showwarning("No Selection", "Please select a bin to report.")
            return

        report_text = f"Bin {self.selected_bin} - Overflow reported by user"
        with open(REQUEST_FILE, "a") as f:
            f.write(report_text + "\n")

        messagebox.showinfo("Reported ✅", f"You have reported {self.selected_bin} successfully!")

        # Reset selection
        self.selected_bin = None
        self.draw_map()


def start_user_portal():
    root = tk.Tk()
    UserPortal(root)
    root.mainloop()


if __name__ == "__main__":
    start_user_portal()
