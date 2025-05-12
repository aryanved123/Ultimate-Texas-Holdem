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
        self.has_bet = {"pre-flop": False, "flop": False, "turn": False}
        self.player_bet_total = 0

    def reset_for_new_hand(self):
        self.displayed_cards = {}
        self.community_cards = []
        self.player.hand = []
        self.dealer.hand = []
        self.pot = self.blind
        self.action_stage = "pre-flop"
        self.multiplier = 1
        self.has_bet = {"pre-flop": False, "flop": False, "turn": False}
        self.player_bet_total = 0

    def start_hand(self):
        self.reset_for_new_hand()

        if self.player.buyIn < self.blind:
            return {"error": "Insufficient balance to start a new hand."}

        self.player.hand = [self.player.get_cards(self.displayed_cards), self.player.get_cards(self.displayed_cards)]
        self.dealer.hand = [self.dealer.get_cards(self.displayed_cards), self.dealer.get_cards(self.displayed_cards)]
        self.player.buyIn -= self.blind
        self.action_stage = "pre-flop"

        return {
            "player_hand": self.player.hand,
            "dealer_hand": [],
            "balance": self.player.buyIn,
            "pot": self.pot,
            "stage": self.action_stage
        }

    def place_bet(self, multiplier):
        amount = multiplier * self.ante
        success = self.player.place_bet(amount)
        if not success:
            return {
                "success": False,
                "message": "Not enough balance"
            }

        self.pot += amount
        self.player_bet_total += amount
        self.has_bet[self.action_stage] = True

        if len(self.community_cards) < 3:
            self.deal_flop()
        while len(self.community_cards) < 5:
            self.deal_turn_or_river()

        self.action_stage = "complete"

        result = self.determine_winner()

        return {
            "success": True,
            "pot": self.pot,
            "balance": self.player.buyIn,
            "player_hand": self.player.hand,
            "dealer_hand": self.dealer.hand,
            "community_cards": self.community_cards,
            "winner": result["winner"]
        }

    def check(self):
        if self.action_stage == "river" or self.has_bet.get(self.action_stage):
            return {"error": "Cannot check at this stage."}

        if self.action_stage == "pre-flop":
            cards = self.deal_flop()
            self.action_stage = "flop"
            return {"cards": cards, "stage": self.action_stage}

        elif self.action_stage == "flop":
            card = self.deal_turn_or_river()
            return {"card": card, "stage": self.action_stage}

        elif self.action_stage == "turn":
            card = self.deal_turn_or_river()
            self.action_stage = "complete"
            result = self.determine_winner()
            return {
                "card": card,
                "stage": "complete",
                "dealer_hand": self.dealer.hand,
                "player_hand": self.player.hand,
                "community_cards": self.community_cards,
                "winner": result["winner"],
                "balance": result["balance"]
            }

        return {"error": "Invalid check."}

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
        else:
            self.action_stage = "turn"
        return card

    def fold(self):
        return {"winner": "dealer", "balance": self.player.buyIn}

    def evaluate_hand(self, hand):
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                  '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        sorted_vals = sorted([values[card[0]] for card in hand], reverse=True)
        suits = [card[1] for card in hand]
        value_counts = Counter(sorted_vals)
        unique_vals = list(set(sorted_vals))
        is_flush = len(set(suits)) == 1
        is_straight = len(unique_vals) == 5 and max(unique_vals) - min(unique_vals) == 4
        is_royal = sorted_vals == [14, 13, 12, 11, 10]

        self.multiplier = 1

        if is_flush and is_royal:
            self.multiplier = 20
            return (9, sorted_vals)  # Royal Flush
        if is_flush and is_straight:
            self.multiplier = 10
            return (8, sorted_vals)  # Straight Flush
        if 4 in value_counts.values():
            self.multiplier = 5
            quad = [k for k, v in value_counts.items() if v == 4]
            return (7, quad + sorted_vals)
        if 3 in value_counts.values() and 2 in value_counts.values():
            self.multiplier = 4
            triple = [k for k, v in value_counts.items() if v == 3]
            return (6, triple + sorted_vals)
        if is_flush:
            self.multiplier = 3
            return (5, sorted_vals)
        if is_straight:
            self.multiplier = 2
            return (4, sorted_vals)
        if 3 in value_counts.values():
            triple = [k for k, v in value_counts.items() if v == 3]
            return (3, triple + sorted_vals)
        if list(value_counts.values()).count(2) == 2:
            pairs = [k for k, v in value_counts.items() if v == 2]
            return (2, sorted(pairs, reverse=True) + sorted_vals)
        if 2 in value_counts.values():
            pair = [k for k, v in value_counts.items() if v == 2]
            return (1, pair + sorted_vals)
        return (0, sorted_vals)

    def determine_winner(self):
        player_hand_value = self.evaluate_hand(self.player.hand + self.community_cards)
        dealer_hand_value = self.evaluate_hand(self.dealer.hand + self.community_cards)

        bonus = self.blind * self.multiplier

        if player_hand_value > dealer_hand_value:
            payout = self.player_bet_total + self.player_bet_total + bonus
            self.player.buyIn += payout
            return {"winner": "player", "balance": self.player.buyIn}
        elif dealer_hand_value > player_hand_value:
            return {"winner": "dealer", "balance": self.player.buyIn}
        else:
            self.player.buyIn += self.player_bet_total + self.blind
            return {"winner": "tie", "balance": self.player.buyIn}