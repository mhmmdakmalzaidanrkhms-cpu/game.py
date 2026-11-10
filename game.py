
import tkinter as tk
import random
import math


W, H = 600, 500
FPS = 60
SPEED = 5

PADDLE_W = 90
PADDLE_H = 10
PADDLE_Y = H - 40

RADIUS = 7
TRAIL = 10
COLS, ROWS = 10, 5

BG = "#0f1117"
WHITE = "#ffffff"
STRONG = "#dee2e6"

ROW_COLORS = [
    "#f06595",
    "#cc5de8",
    "#845ef7",
    "#5c7cfa",
    "#339af0"
]


def blend(c1, c2, t):
    a = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i+2], 16) for i in (1, 3, 5)]

    return "#%02x%02x%02x" % tuple(
        int(x + (y - x) * t)
        for x, y in zip(a, b)
    )


class Game:

    def __init__(self, root):
        self.root = root
        root.title("BLOCK BREAKER")
        root.resizable(False, False)

        self.c = tk.Canvas(
            root,
            width=W,
            height=H,
            bg=BG,
            highlightthickness=0
        )
        self.c.pack()

        self.keys = set()

        root.bind("<KeyPress>", self.key_down)
        root.bind(
            "<KeyRelease>",
            lambda e: self.keys.discard(e.keysym)
        )

        # ---------- TEKS GAME ----------
        font = ("Helvetica", 12, "bold")

        self.score_text = self.c.create_text(
            20, 20,
            anchor="w",
            fill=WHITE,
            font=font
        )

        self.lives_text = self.c.create_text(
            W - 20, 20,
            anchor="e",
            fill=WHITE,
            font=font
        )

        self.msg_text = self.c.create_text(
            W // 2, H // 2 + 60,
            fill=WHITE,
            font=("Helvetica", 14),
            justify="center"
        )

        # ---------- OBJEK GAME ----------
        self.trail = [
            self.c.create_oval(
                0, 0, 0, 0,
                outline=""
            )
            for _ in range(TRAIL)
        ]

        self.ball = self.c.create_oval(
            0, 0, 0, 0,
            fill=WHITE,
            outline=""
        )

        self.paddle = self.c.create_rectangle(
            0, 0, 0, 0,
            fill=WHITE,
            outline=""
        )

        self.blocks = []
        self.particles = []

        # ---------- EFEK GAME OVER ----------
        self.overlay = self.c.create_rectangle(
            0, 0, W, H,
            fill="#000000",
            stipple="gray50",
            outline="",
            state="hidden"
        )

        self.game_over_title = self.c.create_text(
            W // 2, H // 2 - 55,
            text="GAME OVER",
            fill="#ff4757",
            font=("Helvetica", 30, "bold"),
            state="hidden"
        )

        self.game_over_score = self.c.create_text(
            W // 2, H // 2,
            text="SKOR AKHIR: 0",
            fill=WHITE,
            font=("Helvetica", 17, "bold"),
            state="hidden"
        )

        self.game_over_hint = self.c.create_text(
            W // 2, H // 2 + 55,
            text="TEKAN SPASI UNTUK MAIN LAGI",
            fill="#feca57",
            font=("Helvetica", 11, "bold"),
            state="hidden"
        )

        self.blink_counter = 0
        self.game_over_scale = 0

        self.new_game()
        self.loop()

    # ---------- GAME BARU ----------
    def new_game(self):
        self.score = 0
        self.lives = 3

        self.px = (W - PADDLE_W) / 2

        self.particles.clear()

        for p in self.particles:
            self.c.delete(p["id"])

        self.reset_ball()
        self.make_blocks()

    def reset_ball(self):
        self.state = "ready"

        self.bx = self.px + PADDLE_W / 2
        self.by = PADDLE_Y - RADIUS

        self.vx = 0
        self.vy = 0

        self.history = []

    # ---------- MEMBUAT BLOCK ----------
    def make_blocks(self):
        for b in self.blocks:
            self.c.delete(b["id"])

        self.blocks = []

        bw = W // COLS

        for row in range(ROWS):
            for col in range(COLS):

                x = col * bw
                y = 50 + row * 26

                strong = random.random() < 0.25

                rect = (
                    x + 2,
                    y,
                    x + bw - 2,
                    y + 20
                )

                item = self.c.create_rectangle(
                    *rect,
                    outline="",
                    fill=STRONG if strong else ROW_COLORS[row]
                )

                self.blocks.append({
                    "id": item,
                    "rect": rect,
                    "color": ROW_COLORS[row],
                    "hp": 2 if strong else 1
                })

    # ---------- INPUT KEYBOARD ----------
    def key_down(self, e):
        self.keys.add(e.keysym)

        if e.keysym == "space":

            if self.state == "ready":

                self.vx = random.choice([-1, 1]) * SPEED * 0.5

                self.vy = -math.sqrt(
                    SPEED ** 2 - self.vx ** 2
                )

                self.state = "play"

            elif self.state == "over":
                self.new_game()

    # ---------- CEK TABRAKAN ----------
    def hits(self, rect):
        x1, y1, x2, y2 = rect

        return (
            x1 - RADIUS < self.bx < x2 + RADIUS
            and
            y1 - RADIUS < self.by < y2 + RADIUS
        )

    # ---------- EFEK PARTIKEL ----------
    def create_particles(self, x, y, color):
        for _ in range(8):

            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)

            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed

            item = self.c.create_oval(
                x, y, x + 5, y + 5,
                fill=color,
                outline=""
            )

            self.particles.append({
                "id": item,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "life": 25
            })

    def update_particles(self):
        for p in self.particles[:]:

            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1

            self.c.coords(
                p["id"],
                p["x"],
                p["y"],
                p["x"] + 5,
                p["y"] + 5
            )

            if p["life"] <= 0:
                self.c.delete(p["id"])
                self.particles.remove(p)

    # ---------- GERAK BOLA ----------
    def move_ball(self):

        self.bx += self.vx
        self.by += self.vy

        # Dinding kiri dan kanan
        if self.bx < RADIUS or self.bx > W - RADIUS:

            self.bx = max(
                RADIUS,
                min(W - RADIUS, self.bx)
            )

            self.vx *= -1

        # Dinding atas
        if self.by < RADIUS:
            self.by = RADIUS
            self.vy = abs(self.vy)

        # Paddle
        if self.vy > 0 and self.hits((
            self.px,
            PADDLE_Y,
            self.px + PADDLE_W,
            PADDLE_Y + PADDLE_H
        )):

            off = (
                self.bx - self.px - PADDLE_W / 2
            ) / (PADDLE_W / 2)

            self.vx = max(-1, min(1, off)) * SPEED * 0.8

            self.vy = -math.sqrt(
                SPEED ** 2 - self.vx ** 2
            )

            self.by = PADDLE_Y - RADIUS

        # Block
        for b in self.blocks:

            if self.hits(b["rect"]):

                self.vy *= -1
                b["hp"] -= 1

                x1, y1, x2, y2 = b["rect"]

                if b["hp"] == 0:

                    self.create_particles(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        b["color"]
                    )

                    self.c.delete(b["id"])
                    self.blocks.remove(b)

                    self.score += 10

                else:
                    self.c.itemconfig(
                        b["id"],
                        fill=b["color"]
                    )

                break

        # Semua block hancur
        if not self.blocks:
            self.make_blocks()

        # Bola jatuh
        if self.by > H + RADIUS:

            self.lives -= 1

            if self.lives == 0:

                self.state = "over"
                self.blink_counter = 0
                self.game_over_scale = 0

            else:
                self.reset_ball()

    # ---------- UPDATE GAME ----------
    def step(self):

        move = (
            int(bool(self.keys & {"Right", "d", "D"}))
            -
            int(bool(self.keys & {"Left", "a", "A"}))
        ) * 7

        self.px = max(
            0,
            min(W - PADDLE_W, self.px + move)
        )

        if self.state == "ready":

            self.bx = self.px + PADDLE_W / 2
            self.by = PADDLE_Y - RADIUS

        elif self.state == "play":

            self.move_ball()

        self.update_particles()
        self.draw()

    # ---------- EFEK GAME OVER ----------
    def draw_game_over(self):

        self.blink_counter += 1

        self.game_over_scale = min(
            self.game_over_scale + 0.08,
            1
        )

        # Layar gelap
        self.c.itemconfig(
            self.overlay,
            state="normal"
        )

        # Animasi berkedip
        if (self.blink_counter // 20) % 2 == 0:
            color = "#ff4757"
        else:
            color = "#ffffff"

        # Efek ukuran tulisan
        size = int(20 + 14 * self.game_over_scale)

        self.c.itemconfig(
            self.game_over_title,
            state="normal",
            fill=color,
            font=("Helvetica", size, "bold")
        )

        self.c.itemconfig(
            self.game_over_score,
            state="normal",
            text=f"SKOR AKHIR: {self.score}"
        )

        self.c.itemconfig(
            self.game_over_hint,
            state="normal"
        )

        # Sembunyikan pesan awal
        self.c.itemconfig(
            self.msg_text,
            text=""
        )

    def hide_game_over(self):

        self.c.itemconfig(self.overlay, state="hidden")
        self.c.itemconfig(self.game_over_title, state="hidden")
        self.c.itemconfig(self.game_over_score, state="hidden")
        self.c.itemconfig(self.game_over_hint, state="hidden")

    # ---------- TAMPILAN ----------
    def draw(self):

        c = self.c

        c.coords(
            self.paddle,
            self.px,
            PADDLE_Y,
            self.px + PADDLE_W,
            PADDLE_Y + PADDLE_H
        )

        c.coords(
            self.ball,
            self.bx - RADIUS,
            self.by - RADIUS,
            self.bx + RADIUS,
            self.by + RADIUS
        )

        # Jejak bola
        self.history = (
            self.history + [(self.bx, self.by)]
        )[-TRAIL:]

        for i, (x, y) in enumerate(self.history):

            t = (i + 1) / len(self.history)
            r = RADIUS * t

            c.coords(
                self.trail[i],
                x - r,
                y - r,
                x + r,
                y + r
            )

            c.itemconfig(
                self.trail[i],
                fill=blend(BG, WHITE, t * 0.5)
            )

        # Skor dan nyawa
        c.itemconfig(
            self.score_text,
            text=f"SCORE  {self.score}"
        )

        c.itemconfig(
            self.lives_text,
            text="●  " * self.lives
        )

        messages = {
            "ready": "SPASI untuk mulai\n← → atau A D untuk gerak",
            "play": "",
            "over": ""
        }

        c.itemconfig(
            self.msg_text,
            text=messages[self.state]
        )

        # Efek Game Over
        if self.state == "over":
            self.draw_game_over()
        else:
            self.hide_game_over()

    # ---------- LOOP GAME ----------
    def loop(self):

        self.step()

        self.root.after(
            1000 // FPS,
            self.loop
        )


# ---------- JALANKAN GAME ----------
if __name__ == "__main__":

    root = tk.Tk()
    Game(root)
    root.mainloop()
