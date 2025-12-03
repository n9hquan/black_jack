# probability.py
import random
from copy import deepcopy
from player import hand_value, card_value_single

def probability_bust_next(deck, hand):
    """
    Probability that drawing ONE more card from deck will make `hand` bust.
    deck: list of remaining card dicts
    hand: list of card dicts the player currently has
    """
    current = hand_value(hand)
    if len(deck) == 0:
        return 0.0
    bust_count = 0
    for c in deck:
        v = card_value_single(c["rank"])
        # compute as if Ace counted as 11 then adjust
        # but for next-card bust test we must account for Ace flexibility
        # simulate new hand quickly:
        new_total = current + v
        # if v == 11 (Ace), it might be 1 instead if needed
        if new_total > 21 and c["rank"] == "A":
            new_total -= 10
        if new_total > 21:
            bust_count += 1
    return bust_count / len(deck)

def probability_reach_21_next(deck, hand):
    """Probability that next card makes the hand exactly 21."""
    current = hand_value(hand)
    if len(deck) == 0:
        return 0.0
    success = 0
    for c in deck:
        v = card_value_single(c["rank"])
        new_total = current + v
        if c["rank"] == "A" and new_total > 21:
            new_total -= 10
        if new_total == 21:
            success += 1
    return success / len(deck)

def monte_carlo_outcomes(deck, player_hand, dealer_hand, policy_player=None, policy_dealer=None, trials=2000):
    """
    Monte Carlo simulate remainder of game (player plays first until stand/bust, then dealer).
    deck: remaining deck list (will be copied)
    player_hand/dealer_hand: current hands (copied inside)
    policy_player/policy_dealer: functions(player_hand, deck) -> True if should hit
    Returns estimated probabilities: {'player_win', 'dealer_win', 'tie', 'player_bust', 'dealer_bust'}
    """
    if policy_player is None:
        # default policy: hit if <=16
        policy_player = lambda hand, d: hand_value(hand) <= 16
    if policy_dealer is None:
        policy_dealer = lambda hand, d: hand_value(hand) <= 16

    p_win = d_win = tie = p_bust = d_bust = 0
    for _ in range(trials):
        dk = deepcopy(deck)
        random.shuffle(dk)
        ph = deepcopy(player_hand)
        dh = deepcopy(dealer_hand)

        # player turn
        while not (hand_value(ph) > 21) and policy_player(ph, dk):
            if not dk: break
            ph.append(dk.pop())
        # dealer turn
        while not (hand_value(dh) > 21) and policy_dealer(dh, dk):
            if not dk: break
            dh.append(dk.pop())

        pv = hand_value(ph)
        dv = hand_value(dh)
        if pv > 21:
            p_bust += 1
            d_win += 1
        elif dv > 21:
            d_bust += 1
            p_win += 1
        else:
            if pv > dv:
                p_win += 1
            elif pv < dv:
                d_win += 1
            else:
                tie += 1

    total = trials
    return {
        "player_win": p_win/total,
        "dealer_win": d_win/total,
        "tie": tie/total,
        "player_bust": p_bust/total,
        "dealer_bust": d_bust/total
    }
