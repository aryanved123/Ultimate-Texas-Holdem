import random
from collections import Counter

class Player:
    def __init__(self, buyIn):
        self.buyIn = buyIn
        self.hand = []

    def get_cards(self, displayed_cards):
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in displayed_cards:
                displayed_cards[card] = True
                return card

    def place_bet(self, amount):
        if amount > self.buyIn:
            return False
        self.buyIn -= amount
        return True

class Dealer:
    def __init__(self):
        self.hand = []

    def get_cards(self, displayed_cards):
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in displayed_cards:
                displayed_cards[card] = True
                return card

class Game:
    def __init__(self, buy_in):
        self.player = Player(buy_in)
        self.dealer = Dealer()
        self.ante = buy_in // 30
        self.blind = self.ante
        self.pot = self.blind
        self.displayed_cards = {}
        self.community_cards = []
        self.action_stage = "pre-flop"
        self.multiplier = 1

    def reset_for_new_hand(self):
        self.displayed_cards = {}
        self.community_cards = []
        self.player.hand = []
        self.dealer.hand = []
        self.pot = self.blind
        self.action_stage = "pre-flop"
        self.multiplier = 1

    def start_hand(self):
        self.reset_for_new_hand()
        self.player.hand = [self.player.get_cards(self.displayed_cards), self.player.get_cards(self.displayed_cards)]
        self.dealer.hand = [self.dealer.get_cards(self.displayed_cards), self.dealer.get_cards(self.displayed_cards)]
        self.player.buyIn -= self.blind
        return {
            "player_hand": self.player.hand,
            "dealer_hand": self.dealer.hand,
            "balance": self.player.buyIn,
            "pot": self.pot,
            "stage": self.action_stage
        }

    def place_bet(self, multiplier):
        amount = multiplier * self.ante
        success = self.player.place_bet(amount)
        if success:
            self.pot += amount
        return {
            "success": success,
            "pot": self.pot,
            "balance": self.player.buyIn
        }

    def deal_flop(self):
        for _ in range(3):
            card = self.player.get_cards(self.displayed_cards)
            self.community_cards.append(card)
        self.action_stage = "flop"
        return self.community_cards

    def deal_turn_or_river(self):
        card = self.player.get_cards(self.displayed_cards)
        self.community_cards.append(card)
        if len(self.community_cards) == 5:
            self.action_stage = "river"
        return card

    def fold(self):
        return {"winner": "dealer", "balance": self.player.buyIn}

    def evaluate_hand(self, hand):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                  '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        sorted_hand = sorted([values[card[0]] for card in hand], reverse=True)
        suits = [card[1] for card in hand]
        value_counts = Counter(sorted_hand)
        is_flush = len(set(suits)) == 1
        is_straight = len(value_counts) == 5 and (max(sorted_hand) - min(sorted_hand) == 4)
        self.multiplier = 1

        if is_straight and is_flush:
            self.multiplier = 20
            return (8, max(sorted_hand))
        if 4 in value_counts.values():
            self.multiplier = 10
            return (7, max(k for k, v in value_counts.items() if v == 4))
        if 3 in value_counts.values() and 2 in value_counts.values():
            self.multiplier = 5
            return (6, max(k for k, v in value_counts.items() if v == 3))
        if is_flush:
            self.multiplier = 3
            return (5, sorted_hand)
        if is_straight:
            self.multiplier = 1
            return (4, max(sorted_hand))
        if 3 in value_counts.values():
            self.multiplier = 1
            return (3, max(k for k, v in value_counts.items() if v == 3))
        if list(value_counts.values()).count(2) == 2:
            self.multiplier = 1
            return (2, max(k for k, v in value_counts.items() if v == 2))
        if 2 in value_counts.values():
            self.multiplier = 1
            return (1, max(k for k, v in value_counts.items() if v == 2))
        return (0, max(sorted_hand))

    def determine_winner(self):
        player_best = self.evaluate_hand(self.player.hand + self.community_cards)
        dealer_best = self.evaluate_hand(self.dealer.hand + self.community_cards)

        if player_best > dealer_best:
            self.player.buyIn += self.pot * self.multiplier
            return {"winner": "player", "balance": self.player.buyIn}
        elif dealer_best > player_best:
            return {"winner": "dealer", "balance": self.player.buyIn}
        else:
            self.player.buyIn += self.pot - self.blind
            return {"winner": "tie", "balance": self.player.buyIn}
