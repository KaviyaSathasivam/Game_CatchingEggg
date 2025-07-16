from itertools import cycle
from random import randrange, choice
from tkinter import Canvas, Tk, messagebox, font, Button
import time

# --- Configuration ---
canvas_width = 800
canvas_height = 500

# --- Setup ---
root = Tk()
root.title("Egg Catcher Deluxe")
root.resizable(False, False)

c = Canvas(root, width=canvas_width, height=canvas_height, background="sky blue")
c.pack()

# --- Background ---
c.create_rectangle(0, canvas_height-100, canvas_width, canvas_height, fill="forest green", width=0)
c.create_oval(-100, -100, 120, 120, fill='gold', outline='orange', width=2)  # sun

# --- Config ---
egg_colors = cycle(["tomato", "gold", "violet", "cyan", "magenta"])
powerup_colors = {"extra_life": "green", "double_points": "blue"}
egg_width = 45
egg_height = 55
egg_score = 10
initial_speed = 500
initial_interval = 4000
difficulty = 0.92

catcher_width = 120
catcher_height = 120
catcher_color = "navy"

score = 0
lives_remaining = 5
level = 1
double_points = False

# --- Game Assets ---
catcher = c.create_arc(canvas_width/2 - catcher_width/2, canvas_height - catcher_height - 20,
                       canvas_width/2 + catcher_width/2, canvas_height - 20,
                       start=200, extent=140, style="arc", outline=catcher_color, width=5)

game_font = font.nametofont("TkFixedFont")
game_font.config(size=18)

score_text = c.create_text(10, 10, anchor="nw", font=game_font, fill="darkblue", text=f"Score: {score}")
lives_text = c.create_text(canvas_width - 10, 10, anchor="ne", font=game_font, fill="darkred", text=f"Lives: {lives_remaining}")
level_text = c.create_text(canvas_width/2, 10, anchor="n", font=game_font, fill="purple", text=f"Level 1")

start_button = Button(root, text="Start Game", font=("Arial", 14), command=lambda: start_game())
start_button.place(x=canvas_width//2 - 60, y=canvas_height//2 - 20)

paused = False
pause_button = Button(root, text="Pause", font=("Arial", 10), command=lambda: toggle_pause())
pause_button.place(x=10, y=canvas_height - 40)

eggs = []
powerups = []
egg_speed = initial_speed
egg_interval = initial_interval

def start_game():
    start_button.place_forget()
    root.after(1000, create_egg)
    root.after(1000, move_eggs)
    root.after(1000, check_catch)

def toggle_pause():
    global paused
    paused = not paused
    pause_button.config(text="Resume" if paused else "Pause")

def create_egg():
    if paused:
        root.after(500, create_egg)
        return
    x = randrange(10, canvas_width - egg_width - 10)
    y = 40
    new_egg = c.create_oval(x, y, x + egg_width, y + egg_height, fill=next(egg_colors), width=2)
    eggs.append(new_egg)

    if randrange(0, 10) == 0:
        ptype = choice(list(powerup_colors.keys()))
        p = c.create_oval(x, y, x + egg_width, y + egg_height, fill=powerup_colors[ptype], width=2)
        c.itemconfig(p, tags=ptype)
        powerups.append(p)

    root.after(egg_interval, create_egg)

def move_eggs():
    if paused:
        root.after(500, move_eggs)
        return

    for egg in eggs[:]:
        c.move(egg, 0, 10)
        if c.coords(egg)[3] > canvas_height:
            egg_dropped(egg)

    for p in powerups[:]:
        c.move(p, 0, 10)
        if c.coords(p)[3] > canvas_height:
            powerups.remove(p)
            c.delete(p)

    root.after(egg_speed, move_eggs)

def egg_dropped(egg):
    global lives_remaining
    eggs.remove(egg)
    c.delete(egg)
    lives_remaining -= 1
    update_ui()
    if lives_remaining <= 0:
        game_over()

def update_ui():
    c.itemconfigure(score_text, text=f"Score: {score}")
    c.itemconfigure(lives_text, text=f"Lives: {lives_remaining}")
    c.itemconfigure(level_text, text=f"Level {level}")

def check_catch():
    if paused:
        root.after(200, check_catch)
        return

    (cx1, cy1, cx2, cy2) = c.coords(catcher)
    for egg in eggs[:]:
        (ex1, ey1, ex2, ey2) = c.coords(egg)
        if cx1 < ex1 < cx2 and cy1 < ey2 < cy2:
            eggs.remove(egg)
            c.delete(egg)
            increase_score(egg_score * (2 if double_points else 1))

    for p in powerups[:]:
        (px1, py1, px2, py2) = c.coords(p)
        if cx1 < px1 < cx2 and cy1 < py2 < cy2:
            ptype = c.gettags(p)[0]
            apply_powerup(ptype)
            powerups.remove(p)
            c.delete(p)

    root.after(100, check_catch)

def apply_powerup(ptype):
    global lives_remaining, double_points
    if ptype == "extra_life":
        lives_remaining += 1
    elif ptype == "double_points":
        double_points = True
        root.after(10000, lambda: disable_double_points())
    update_ui()

def disable_double_points():
    global double_points
    double_points = False

def increase_score(points):
    global score, egg_speed, egg_interval, level
    score += points
    if score % 100 == 0:
        egg_speed = int(egg_speed * difficulty)
        egg_interval = int(egg_interval * difficulty)
        level += 1
    update_ui()

def move_left(event):
    if paused:
        return
    (x1, y1, x2, y2) = c.coords(catcher)
    if x1 > 10:
        c.move(catcher, -25, 0)

def move_right(event):
    if paused:
        return
    (x1, y1, x2, y2) = c.coords(catcher)
    if x2 < canvas_width - 10:
        c.move(catcher, 25, 0)

def game_over():
    c.create_text(canvas_width/2, canvas_height/2, text="GAME OVER", font=("Helvetica", 32, "bold"), fill="red")
    c.create_text(canvas_width/2, canvas_height/2 + 40, text=f"Final Score: {score}", font=("Helvetica", 24), fill="black")
    c.update()
    c.unbind("<Left>")
    c.unbind("<Right>")

# --- Controls ---
c.bind("<Left>", move_left)
c.bind("<Right>", move_right)
c.focus_set()

# --- Mainloop ---
root.mainloop()
#python egg_catcher_deluxe.py