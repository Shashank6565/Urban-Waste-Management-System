"""
Final Login Portal - Frosted White Glass Style (Option A)
Keeps all existing login/register logic and portal launches intact.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import json
import os
import threading

# ---------------- CONFIG ----------------
DATA_FILE = "users.json"
# Path to your background image (update if needed)
bg_path = r"C:\Users\933si\Downloads\Gemini_Generated_Image_9thjlf9thjlf9thj.png"

# Ensure users file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"User": {}, "Driver": {}, "Admin": {}}, f, indent=2)

# ---------------- Helpers ----------------
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- Create main window ----------------
root = tk.Tk()
root.title("Smart City Waste Management - Login Portal")
WIN_W, WIN_H = 1200, 800
root.geometry(f"{WIN_W}x{WIN_H}")
root.resizable(False, False)

# ---------------- Load background image and create blurred version ----------------
def safe_open_image(path, target_size=(WIN_W, WIN_H)):
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize(target_size, Image.LANCZOS)
        return img
    except Exception as e:
        print("Warning: background image not found or failed to open:", e)
        # create a subtle gradient fallback
        fallback = Image.new("RGB", target_size, "#0B1220")
        return fallback

bg_original = safe_open_image(bg_path)
bg_blurred = bg_original.filter(ImageFilter.GaussianBlur(radius=6))
bg_tk = ImageTk.PhotoImage(bg_blurred)

# Put blurred image as background using a Canvas (so we can layer items)
canvas = tk.Canvas(root, width=WIN_W, height=WIN_H, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas_bg = canvas.create_image(0, 0, anchor="nw", image=bg_tk)

# ---------------- Create frosted rounded panel image dynamically ----------------
CARD_W, CARD_H = 520, 460
card_x = WIN_W // 2
card_y = WIN_H // 2

def create_frosted_panel(bg_img, center_x, center_y, w, h,
                         corner_radius=22, blur_amount=8, white_alpha=180,
                         border_color="#ffffff", border_width=2, glow_color="#e6f3ff"):
    """
    Create a frosted glass panel image:
      - crop region from background (so the panel inherits scene colors)
      - blur the crop
      - overlay semi-transparent white to create frosted look
      - apply rounded mask
      - draw subtle border (and optional glow)
    Returns a PIL.Image with RGBA.
    """
    left = max(0, center_x - w//2)
    top = max(0, center_y - h//2)
    right = left + w
    bottom = top + h

    # Crop from original (not the already-blurred) for more realistic frosted look
    crop = bg_original.crop((left, top, right, bottom)).filter(ImageFilter.GaussianBlur(radius=blur_amount))

    panel = Image.new("RGBA", (w, h), (255,255,255,0))

    # Overlay the blurred crop
    panel.paste(crop.convert("RGBA"), (0,0))

    # overlay semi-transparent white
    overlay = Image.new("RGBA", (w, h), (255,255,255,white_alpha))
    panel = Image.alpha_composite(panel, overlay)

    # rounded mask
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0,0),(w-1,h-1)], radius=corner_radius, fill=255)

    # apply mask to panel (keeping rounded corners transparent outside)
    panel.putalpha(mask)

    # Create final image with border and slight glow underlay
    final = Image.new("RGBA", (w+12, h+12), (0,0,0,0))
    glow = Image.new("RGBA", (w+12, h+12), (0,0,0,0))
    gdraw = ImageDraw.Draw(glow)
    # faint outer glow (soft)
    gx0, gy0 = 6, 6
    gdraw.rounded_rectangle([(gx0,gy0),(gx0+w-1,gy0+h-1)], radius=corner_radius+2,
                             fill=(230,243,255,30))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    final = Image.alpha_composite(final, glow)

    # paste panel onto final (centered with 6px padding)
    final.paste(panel, (6,6), panel)

    # draw crisp border
    bdraw = ImageDraw.Draw(final)
    bdraw.rounded_rectangle([(6,6),(6+w-1,6+h-1)],
                        radius=corner_radius,
                        outline=border_color,
                        width=border_width)


    return final

frosted_img = create_frosted_panel(bg_original, card_x, card_y, CARD_W, CARD_H,
                                   corner_radius=20, blur_amount=10, white_alpha=160,
                                   border_color="#FFFFFF", border_width=1)
frosted_tk = ImageTk.PhotoImage(frosted_img)
# Keep reference alive
canvas.frosted_tk = frosted_tk

# Place frosted panel on canvas (centered)
panel_img_id = canvas.create_image(card_x - (frosted_img.width//2),
                                   card_y - (frosted_img.height//2),
                                   anchor="nw", image=frosted_tk)

# ---------------- Place widgets onto the canvas (so they appear on top of panel) ----------------
# We'll create a Frame (without visible background) and place it on the canvas.
ui_frame = tk.Frame(root, bg="#f0f3f6", bd=0)  # background will match panel tones
ui_width = CARD_W - 80
ui_height = CARD_H - 80

# Canvas window; position so the frame fits inside the rounded panel
frame_window = canvas.create_window(card_x, card_y, window=ui_frame, width=ui_width, height=ui_height, anchor="center")

# ---------- UI content styling ----------
TITLE_FONT = ("Segoe UI Black", 22)
SUB_FONT = ("Segoe UI", 11)
ENTRY_FONT = ("Segoe UI", 11)
BTN_FONT = ("Segoe UI Semibold", 11)

# Title
title_lbl = tk.Label(ui_frame, text="SMART CITY LOGIN", bg="#f0f3f6", fg="#1b2b3a", font=TITLE_FONT)
title_lbl.pack(pady=(18, 6))

subtitle_lbl = tk.Label(ui_frame, text="Access User • Driver • Admin Portals", bg="#f0f3f6",
                        fg="#6d7b83", font=SUB_FONT)
subtitle_lbl.pack(pady=(0, 18))

# Role combobox
selected_role = tk.StringVar(value="Admin")
role_box = ttk.Combobox(ui_frame, textvariable=selected_role, state="readonly",
                        values=["Admin", "User", "Driver"], font=ENTRY_FONT, width=20)
role_box.pack(pady=6)
role_box.current(0)

# Entry creator (clean flat entries)
def create_entry(parent, placeholder, show=None):
    var = tk.StringVar()
    ent = tk.Entry(parent, textvariable=var, font=ENTRY_FONT,
                   bg="#f7f9fb", fg="#213242", relief="flat", justify="center")
    ent.insert(0, placeholder)
    ent.bind("<FocusIn>", lambda e, s=placeholder: ent.delete(0, tk.END) if ent.get()==s else None)
    ent.bind("<FocusOut>", lambda e, s=placeholder: ent.insert(0, s) if ent.get()=="" else None)
    if show:
        # Will set show when user focuses and typed; we simulate by toggling on focus
        def on_in(e):
            if ent.get() == placeholder:
                ent.delete(0, tk.END)
            ent.config(show="•")
        def on_out(e):
            if ent.get() == "":
                ent.insert(0, placeholder)
                ent.config(show="")
        ent.bind("<FocusIn>", on_in)
        ent.bind("<FocusOut>", on_out)
    ent.pack(pady=10, ipady=8, ipadx=6, fill="x", padx=30)
    return ent

username = create_entry(ui_frame, "Username")
password = create_entry(ui_frame, "Password", show=True)

# Buttons - styled to look like subtle glass neon
def make_button(parent, text, bg="#00BFA5", cmd=None):
    b = tk.Button(parent, text=text, bg=bg, fg="white", font=BTN_FONT,
                  activebackground=bg, activeforeground="white",
                  relief="flat", bd=0, command=cmd)
    b.pack(pady=10, ipadx=5, ipady=8, fill="x", padx=30)
    return b

# ----- load portal starter functions lazily to avoid import issues -----
def start_admin_portal():
    # import here to avoid circular import issues when running modules separately
    from admin_portal import start_admin_portal as s
    s()

def start_driver_portal_threaded():
    from driver_portal import start_driver_portal as s
    threading.Thread(target=s, daemon=True).start()

def start_user_portal_threaded():
    from user_portal import start_user_portal as s
    threading.Thread(target=s, daemon=True).start()

# Button callbacks (preserve original logic)
def login_action():
    role = selected_role.get()
    u = username.get().strip()
    p = password.get().strip()
    try:
        data = load_data()
    except Exception:
        messagebox.showerror("Error", "Failed to load user data.")
        return

    if u in data.get(role, {}) and data[role][u] == p:
        messagebox.showinfo("Success", f"Welcome {u} ({role})!")
        # open appropriate portal
        if role == "Admin":
            # admin opens in main thread
            start_admin_portal()
        elif role == "Driver":
            start_driver_portal_threaded()
        else:
            start_user_portal_threaded()
    else:
        messagebox.showerror("Error", "Invalid credentials or user not found.")

def register_action():
    role = selected_role.get()
    u = username.get().strip()
    p = password.get().strip()
    if not u or not p or u == "Username" or p == "Password":
        messagebox.showwarning("Warning", "Please fill all fields.")
        return
    data = load_data()
    if u in data.get(role, {}):
        messagebox.showerror("Error", "User already exists.")
        return
    data.setdefault(role, {})[u] = p
    save_data(data)
    messagebox.showinfo("Registered", f"Account created for {u} ({role}).")

login_btn = make_button(ui_frame, "Login", bg="#00BFA5", cmd=login_action)
register_btn = make_button(ui_frame, "Register", bg="#2979FF", cmd=register_action)
register_btn.pack(pady=(0, 5))

# Small footer hint
hint = tk.Label(ui_frame, text="Press Esc to close", bg="#f0f3f6", fg="#9aa6af", font=("Segoe UI",10))
hint.pack(side="bottom", pady=(8,6))

# Close on Escape
root.bind("<Escape>", lambda e: root.destroy())

# Keep image references to avoid GC
root._bg_tk = bg_tk
root._frosted_tk = frosted_tk

# ---------------- Main loop ----------------
if __name__ == "__main__":
    root.mainloop()
