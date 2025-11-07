import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from admin_portal import start_admin_portal
from user_portal import start_user_portal
from driver_portal import start_driver_portal

# =============== CONFIG ===============
DATA_FILE = "users.json"

# Initialize file if not exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"User": {}, "Driver": {}, "Admin": {}}, f)

# =============== COLORS ===============
BG_TOP = "#283E51"
BG_BOTTOM = "#1F4F82"
CARD_BG = "#1B2735"
ENTRY_BG = "#2C3E50"
ENTRY_FG = "#FFFFFF"
BTN_COLOR = "#00B894"
BTN_HOVER = "#00D1A0"
FONT = ("Segoe UI", 11)


# =============== MAIN WINDOW ===============
root = tk.Tk()
root.title("Multi-Role Login & Register Portal")
root.attributes('-fullscreen', True)
root.configure(bg=BG_BOTTOM)

# Exit with Esc
root.bind("<Escape>", lambda e: root.destroy())

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# =============== GRADIENT BACKGROUND ===============
canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
canvas.pack(fill="both", expand=True)
for i in range(screen_height):
    ratio = i / screen_height
    r1, g1, b1 = (40, 62, 81)
    r2, g2, b2 = (72, 85, 99)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    canvas.create_line(0, i, screen_width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

# =============== MAIN CARD ===============
card = tk.Frame(root, bg=CARD_BG)
card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=500)

# =============== TITLE ===============
tk.Label(card, text="🚀 Smart Login Portal", bg=CARD_BG,
         fg="white", font=("Segoe UI Semibold", 22)).pack(pady=(30, 5))
tk.Label(card, text="Choose Role and Sign In or Register", bg=CARD_BG,
         fg="#CCCCCC", font=("Segoe UI", 10)).pack(pady=(0, 15))

# =============== ROLE SELECTION ===============
selected_role = tk.StringVar(value="User")
role_box = ttk.Combobox(card, textvariable=selected_role, state="readonly",
                        values=["User", "Driver", "Admin"], font=("Segoe UI", 10))
role_box.pack(pady=10, ipadx=5)
role_box.current(0)

# =============== FRAME FOR LOGIN/REGISTER ===============
frame = tk.Frame(card, bg=CARD_BG)
frame.pack(pady=10)


# =============== ENTRY CREATOR FUNCTION ===============
def create_entry(parent, placeholder):
    e = tk.Entry(parent, bg=ENTRY_BG, fg="#BBBBBB", relief="flat",
                 font=FONT, insertbackground="white")
    e.insert(0, placeholder)
    e.pack(pady=10, ipady=8, ipadx=10, fill="x", padx=80)

    def on_focus_in(event):
        if e.get() == placeholder:
            e.delete(0, "end")
            e.config(fg=ENTRY_FG)
            if placeholder == "Password":
                e.config(show="•")

    def on_focus_out(event):
        if e.get() == "":
            e.insert(0, placeholder)
            e.config(fg="#BBBBBB")
            if placeholder == "Password":
                e.config(show="")

    e.bind("<FocusIn>", on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    return e


# =============== LOAD JSON DATA ===============
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =============== LOGIN FUNCTION ===============
def login_action():
    role = selected_role.get()
    u = username.get().strip()
    p = password.get().strip()

    data = load_data()

    if u in data[role] and data[role][u] == p:
        messagebox.showinfo("Success", f"Welcome {u} ({role})!")
        open_portal(role)
    else:
        messagebox.showerror("Error", "Invalid credentials or user not found.")


# =============== REGISTER FUNCTION ===============
def register_action():
    role = selected_role.get()
    u = username.get().strip()
    p = password.get().strip()

    if not u or not p or u == "Username" or p == "Password":
        messagebox.showwarning("Warning", "Please fill all fields.")
        return

    data = load_data()
    if u in data[role]:
        messagebox.showerror("Error", "User already exists.")
    else:
        data[role][u] = p
        save_data(data)
        messagebox.showinfo("Registered ✅", f"Account created for {u} ({role}).")


# =============== ROLE PORTALS ===============
def open_portal(role):
    new_win = tk.Toplevel(root)
    new_win.title(f"{role} Portal")
    new_win.geometry("800x500")
    new_win.config(bg="#101820")

    tk.Label(new_win, text=f"Welcome to {role} Portal", bg="#101820",
             fg="white", font=("Segoe UI Bold", 20)).pack(pady=50)

    if role == "Admin":
        tk.Label(new_win, text="Admin Controls: Manage Users, Reports, etc.",
                 bg="#101820", fg="#00B894", font=("Segoe UI", 12)).pack(pady=10)
        root.destroy()
        start_admin_portal()
    elif role == "Driver":
        tk.Label(new_win, text="Driver Dashboard: View Assignments, Routes",
                 bg="#101820", fg="#FDCB6E", font=("Segoe UI", 12)).pack(pady=10)
        root.destroy()
        start_driver_portal()
    elif role == "User":
        tk.Label(new_win, text="User Dashboard: View Services, Profile",
                 bg="#101820", fg="#74B9FF", font=("Segoe UI", 12)).pack(pady=10)
        root.destroy()
        start_user_portal()

    tk.Button(new_win, text="Logout", bg="#E74C3C", fg="white",
              font=("Segoe UI", 11), relief="flat",
              command=new_win.destroy).pack(pady=50, ipadx=10, ipady=5)


# =============== BUILD LOGIN FRAME ===============
username = create_entry(frame, "Username")
password = create_entry(frame, "Password")


def on_enter(e): login_btn.config(bg=BTN_HOVER)
def on_leave(e): login_btn.config(bg=BTN_COLOR)

login_btn = tk.Button(frame, text="Login", bg=BTN_COLOR, fg="white",
                      font=("Segoe UI Semibold", 11), relief="flat",
                      activebackground=BTN_HOVER, activeforeground="white",
                      cursor="hand2", command=login_action)
login_btn.pack(pady=(5, 5), ipadx=8, ipady=5, fill="x", padx=80)
login_btn.bind("<Enter>", on_enter)
login_btn.bind("<Leave>", on_leave)

register_btn = tk.Button(frame, text="Register", bg="#0984E3", fg="white",
                         font=("Segoe UI Semibold", 11), relief="flat",
                         activebackground="#74B9FF", activeforeground="white",
                         cursor="hand2", command=register_action)
register_btn.pack(pady=(5, 5), ipadx=8, ipady=5, fill="x", padx=80)

root.mainloop()
