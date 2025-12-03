# player.py
from deck import RANKS
from copy import deepcopy

def card_value_single(card_rank):
    if card_rank == "A":
        return 11
    if card_rank in ["J","Q","K"]:
        return 10
    return int(card_rank)

def hand_value(hand):
    total = 0
    aces = 0
    for c in hand:
        v = card_value_single(c["rank"])
        total += v
        if c["rank"] == "A":
            aces += 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.hand = []
        self.stand = False
        self.busted = False

    def reset(self):
        self.hand = []
        self.stand = False
        self.busted = False

    def add_card(self, card):
        self.hand.append(card)
        if hand_value(self.hand) > 21:
            self.busted = True

    def value(self):
        return hand_value(self.hand)

    def should_hit_by_rule(self):
        """
        Blackjack dealer rule: hit on 16 or less, stand on 17 or more.
        We will use this rule for both dealer (auto) and optionally for player's suggested AI.
        """
        return self.value() <= 16
