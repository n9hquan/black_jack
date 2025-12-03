# deck.py
import random
import os

RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
SUITS = ["H","D","C","S"]  # Hearts, Diamonds, Clubs, Spades

def new_deck():
    deck = [{"rank": r, "suit": s} for r in RANKS for s in SUITS]
    random.shuffle(deck)
    return deck

def card_name(card):
    return f"{card['rank']}{card['suit']}"

def card_image_path(card, assets_dir="assets/cards"):
    # maps to files like "AH.png"
    fname = card_name(card) + ".png"
    path = os.path.join(assets_dir, fname)
    return path

def back_image_path(assets_dir="assets/cards"):
    return os.path.join(assets_dir, "back.png")
