# game.py
from deck import new_deck
from player import Player
import random
from copy import deepcopy

class Game:
    def __init__(self):
        self.deck = []
        self.player = Player("Player")
        self.dealer = Player("Dealer")
        self.history = []

    def start_new(self):
        self.deck = new_deck()
        self.player.reset()
        self.dealer.reset()
        # Deal two cards each: player first then dealer
        self.player.add_card(self.deck.pop())
        self.dealer.add_card(self.deck.pop())
        self.player.add_card(self.deck.pop())
        self.dealer.add_card(self.deck.pop())
        self.history = []

    def player_hit(self):
        if not self.player.stand and not self.player.busted:
            if self.deck:
                self.player.add_card(self.deck.pop())
            self.history.append(("player_hit",))
            return True
        return False

    def player_stand(self):
        self.player.stand = True
        self.history.append(("player_stand",))

    def dealer_play_auto(self):
        """
        Dealer plays according to rule: hit on <=16, stand on >=17.
        Called after player_stand or player busted.
        """
        while self.dealer.should_hit_by_rule():
            if not self.deck:
                break
            self.dealer.add_card(self.deck.pop())
        # done

    def is_round_over(self):
        # round over when player busted or player stood and dealer finished
        if self.player.busted:
            return True
        if self.player.stand:
            # check dealer either finished or will still play
            # after dealer_play_auto called from UI
            return True
        return False

    def result(self):
        p = self.player.value()
        d = self.dealer.value()
        if p > 21:
            return "dealer"
        if d > 21:
            return "player"
        if p > d:
            return "player"
        if d > p:
            return "dealer"
        return "tie"
