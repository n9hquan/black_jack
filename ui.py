# ui.py
import tkinter as tk
from tkinter import ttk
import os
from deck import card_image_path, back_image_path
from player import hand_value
from game import Game
from probability import probability_bust_next, probability_reach_21_next, monte_carlo_outcomes
import time

CARD_W = 80
CARD_H = 110
ASSETS_DIR = os.path.join("assets","cards")

class BlackjackUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Blackjack Probability Assistant")
        self.game = Game()

        # try load back image and a test image; if not found, fallback to text
        self.card_images = {}  # cache PhotoImage
        self.back_image = None
        self.load_back_image()

        # top frames
        top = tk.Frame(root)
        top.pack(pady=6)

        # dealer area
        self.dealer_label = tk.Label(top, text="Dealer", font=("Arial", 14))
        self.dealer_label.grid(row=0, column=0)
        self.dealer_canvas = tk.Canvas(top, width=500, height=150, bg="#0b7", highlightthickness=0)
        self.dealer_canvas.grid(row=1, column=0, padx=10)

        # player area
        self.player_label = tk.Label(top, text="Player", font=("Arial", 14))
        self.player_label.grid(row=2, column=0)
        self.player_canvas = tk.Canvas(top, width=500, height=150, bg="#7bf", highlightthickness=0)
        self.player_canvas.grid(row=3, column=0, padx=10)

        # control & prob area
        ctrl = tk.Frame(root)
        ctrl.pack(pady=8)

        self.hit_btn = ttk.Button(ctrl, text="Hit", command=self.on_hit)
        self.hit_btn.grid(row=0, column=0, padx=6)
        self.stand_btn = ttk.Button(ctrl, text="Stand", command=self.on_stand)
        self.stand_btn.grid(row=0, column=1, padx=6)
        self.new_btn = ttk.Button(ctrl, text="New Game", command=self.on_new)
        self.new_btn.grid(row=0, column=2, padx=6)

        # probability text
        self.prob_text = tk.Text(root, width=60, height=6)
        self.prob_text.pack(pady=6)
        self.prob_text.config(state=tk.DISABLED)

        # result label
        self.result_label = tk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack()

        # start
        self.on_new()

    # -----------------------
    # image helpers
    # -----------------------
    def load_back_image(self):
        try:
            path = back_image_path(ASSETS_DIR)
            if os.path.exists(path):
                self.back_image = tk.PhotoImage(file=path)
                # scale to card size if necessary using subsample
                # naive subsample: adjust if too big
                if self.back_image.width() > CARD_W or self.back_image.height() > CARD_H:
                    xsubs = max(1, self.back_image.width() // CARD_W)
                    ysubs = max(1, self.back_image.height() // CARD_H)
                    self.back_image = self.back_image.subsample(xsubs, ysubs)
            else:
                self.back_image = None
        except Exception as e:
            print("Back image load failed:", e)
            self.back_image = None

    def get_card_image(self, card):
        """
        Return a PhotoImage if exists, otherwise None.
        We cache PhotoImage objects to prevent GC.
        """
        path = card_image_path(card, ASSETS_DIR)
        if path in self.card_images:
            return self.card_images[path]
        if os.path.exists(path):
            try:
                img = tk.PhotoImage(file=path)
                if img.width() > CARD_W or img.height() > CARD_H:
                    xsubs = max(1, img.width() // CARD_W)
                    ysubs = max(1, img.height() // CARD_H)
                    img = img.subsample(xsubs, ysubs)
                self.card_images[path] = img
                return img
            except Exception as e:
                print("Image load failed for", path, e)
                return None
        return None

    # -----------------------
    # UI actions
    # -----------------------
    def on_new(self):
        self.game.start_new()
        self.result_label.config(text="")
        self.clear_canvases()
        self.draw_hands(initial=True)
        self.update_probabilities()
        self.hit_btn.config(state=tk.NORMAL)
        self.stand_btn.config(state=tk.NORMAL)

    def on_hit(self):
        if self.game.player.busted:
            return
        # animate draw: we draw from deck visually
        if not self.game.deck:
            return
        card = self.game.deck[-1]  # peek top
        self.animate_draw(card, to_player=True, callback=self.after_hit)

    def after_hit(self):
        self.game.player_hit()
        self.draw_hands()
        self.update_probabilities()
        if self.game.player.busted:
            self.end_round()

    def on_stand(self):
        self.game.player_stand()
        # dealer plays automatically with animation
        self.dealer_play_with_animation()

    # -----------------------
    # Drawing & animation
    # -----------------------
    def clear_canvases(self):
        self.dealer_canvas.delete("all")
        self.player_canvas.delete("all")

    def draw_hands(self, initial=False):
        self.clear_canvases()
        # dealer: show upcard and back for second card (no reveal)
        dx = 10
        for i, c in enumerate(self.game.dealer.hand):
            x = dx + i * (CARD_W + 10)
            y = 10
            if i == 1:  # second card face-down (casino style)
                # draw back image
                if self.back_image:
                    self.dealer_canvas.create_image(x, y, anchor="nw", image=self.back_image)
                else:
                    self.draw_card_rect(self.dealer_canvas, x, y, text="Hidden")
            else:
                img = self.get_card_image(c)
                if img:
                    self.dealer_canvas.create_image(x, y, anchor="nw", image=img)
                else:
                    self.draw_card_rect(self.dealer_canvas, x, y, text=f"{c['rank']}{c['suit']}")
        # player
        dx = 10
        for i, c in enumerate(self.game.player.hand):
            x = dx + i * (CARD_W + 10)
            y = 10
            img = self.get_card_image(c)
            if img:
                self.player_canvas.create_image(x, y, anchor="nw", image=img)
            else:
                self.draw_card_rect(self.player_canvas, x, y, text=f"{c['rank']}{c['suit']}")
        # show numeric totals (dealer shows only upcard value)
        upcard_val = 0
        if len(self.game.dealer.hand) > 0:
            upcard_val = hand_value([self.game.dealer.hand[0]])
        self.dealer_canvas.create_text(400, 20, text=f"Upcard value: {upcard_val}", anchor="nw", font=("Arial",12,"bold"))
        self.player_canvas.create_text(400, 20, text=f"Value: {self.game.player.value()}", anchor="nw", font=("Arial",12,"bold"))

    def draw_card_rect(self, canvas, x, y, text=""):
        canvas.create_rectangle(x, y, x+CARD_W, y+CARD_H, fill="white", outline="black", width=2, radius=5 if hasattr(canvas, "create_rounded_rectangle") else None)
        canvas.create_text(x+CARD_W/2, y+CARD_H/2, text=text, font=("Arial",12,"bold"))

    def animate_draw(self, card, to_player=True, callback=None):
        """
        Simple slide-in animation: create image at left outside canvas and move to target slot.
        We'll pop the real card from deck on animation completion (to keep state consistent).
        """
        src_x = -CARD_W - 20
        if to_player:
            canvas = self.player_canvas
            hand = self.game.player.hand
            slot_index = len(hand)  # new card goes at end
            target_x = 10 + slot_index * (CARD_W + 10)
            target_y = 10
        else:
            canvas = self.dealer_canvas
            hand = self.game.dealer.hand
            slot_index = len(hand)
            target_x = 10 + slot_index * (CARD_W + 10)
            target_y = 10

        img = self.get_card_image(card)
        if img:
            obj = canvas.create_image(src_x, target_y, anchor="nw", image=img)
        else:
            # draw text rect
            obj = canvas.create_rectangle(src_x, target_y, src_x+CARD_W, target_y+CARD_H, fill="white", outline="black")
            txt = canvas.create_text(src_x+CARD_W/2, target_y+CARD_H/2, text=f"{card['rank']}{card['suit']}", font=("Arial",12,"bold"))

        steps = 30
        dx = (target_x - src_x) / steps
        def step(i=0):
            if i >= steps:
                # finish: actually remove card from deck and add to hand
                self.game.deck.pop()  # remove top (we used peek earlier)
                if to_player:
                    self.game.player.add_card(card)
                else:
                    self.game.dealer.add_card(card)
                self.draw_hands()
                if callback:
                    self.root.after(150, callback)
                return
            canvas.move(obj, dx, 0)
            if img is None:
                canvas.move(txt, dx, 0)
            self.root.after(12, lambda: step(i+1))
        step()

    def dealer_play_with_animation(self):
        # dealer will draw until >=17. Animate draws one by one.
        def single_draw():
            if self.game.dealer.should_hit_by_rule() and self.game.deck:
                card = self.game.deck[-1]
                # animate draw to dealer
                self.animate_draw(card, to_player=False, callback=single_draw)
            else:
                # finish dealer play
                self.draw_hands()
                self.finish_round()
        # start sequence
        single_draw()

    def finish_round(self):
        res = self.game.result()
        if res == "player":
            text = "Player wins!"
        elif res == "dealer":
            text = "Dealer wins!"
        else:
            text = "Tie!"
        self.result_label.config(text=text)
        self.hit_btn.config(state=tk.DISABLED)
        self.stand_btn.config(state=tk.DISABLED)
        self.update_probabilities(final=True)

    def end_round(self):
        # player busted or similar -> finish by revealing dealer automatically (no animation)
        # Dealer still plays after player bust? Real blackjack ends when player busts.
        if self.game.player.busted:
            self.result_label.config(text="Player busted. Dealer wins.")
            self.hit_btn.config(state=tk.DISABLED)
            self.stand_btn.config(state=tk.DISABLED)
            self.update_probabilities(final=True)

    # -----------------------
    # Probability display
    # -----------------------
    def update_probabilities(self, final=False):
        self.prob_text.config(state=tk.NORMAL)
        self.prob_text.delete("1.0", tk.END)
        deck = list(self.game.deck)  # remaining cards

        # Player next-card stats
        pbust = probability_bust_next(deck, self.game.player.hand)
        preach21 = probability_reach_21_next(deck, self.game.player.hand)

        self.prob_text.insert(tk.END, f"Player next-card probability (if hit once):\n")
        self.prob_text.insert(tk.END, f" - Bust: {pbust*100:.2f}%\n")
        self.prob_text.insert(tk.END, f" - Reach exactly 21: {preach21*100:.2f}%\n\n")

        # Monte Carlo outcome estimates of finishing the round (current state)
        mc = monte_carlo_outcomes(deck, self.game.player.hand, self.game.dealer.hand, trials=1200)
        self.prob_text.insert(tk.END, f"Estimated outcomes (Monte Carlo):\n")
        self.prob_text.insert(tk.END, f" - Player win: {mc['player_win']*100:.2f}%\n")
        self.prob_text.insert(tk.END, f" - Dealer win: {mc['dealer_win']*100:.2f}%\n")
        self.prob_text.insert(tk.END, f" - Tie: {mc['tie']*100:.2f}%\n")
        self.prob_text.insert(tk.END, f" - Player bust prob: {mc['player_bust']*100:.2f}%\n")
        self.prob_text.insert(tk.END, f" - Dealer bust prob: {mc['dealer_bust']*100:.2f}%\n")

        if final:
            self.prob_text.insert(tk.END, "\nFinal hands revealed for outcome.\n")

        self.prob_text.config(state=tk.DISABLED)
