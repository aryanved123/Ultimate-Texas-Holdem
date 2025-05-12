import random
from collections import Counter

class Player:
    def __init__(self, buyIn):
        self.buyIn = buyIn
        self.hand = []  # Stores player's cards
    
    def get_cards(self, displayed_cards):
        """Generates a unique random card (value, suit) that hasn't been used."""
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in displayed_cards:
                displayed_cards[card] = True
                return card

    def place_bet(self, amount):  
        if amount > self.buyIn:
            print("Not enough balance to place this bet.")
            return False
        self.buyIn -= amount
        return True

class Dealer:
    def __init__(self):
        self.hand = []

    def get_cards(self, displayed_cards):
        """Dealer gets a unique card from the deck."""
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
    
    def reset_displayed_cards(self):
        """Resets the displayed cards dictionary for the next round."""
        self.displayed_cards = {}

    def get_card(self):
        """Fetches a unique random card."""
        value_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_list = ['Hearts', 'Clubs', 'Spades', 'Diamonds']
        
        while True:
            card = (random.choice(value_list), random.choice(suit_list))
            if card not in self.displayed_cards:
                self.displayed_cards[card] = True
                return card
    
    def next_card(self):
        """Deals the next community card."""
        print("Dealing next community card...")
        card = self.get_card()
        self.community_cards.append(card)
        print(f"Community card: {card}")

    def evaluate_hand(self, hand):
        """Determines the best hand ranking"""
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        sorted_hand = sorted([values[card[0]] for card in hand], reverse=True)
        suits = [card[1] for card in hand]
        value_counts = Counter(sorted_hand)
        is_flush = len(set(suits)) == 1
        self.multiplier = 1  # Reset multiplier before evaluating
        is_straight = len(value_counts) == 5 and (max(sorted_hand) - min(sorted_hand) == 4)
        
        if is_straight and is_flush:
            self.multiplier = 20
            return (8, max(sorted_hand))  # Straight Flush
        if 4 in value_counts.values():
            self.multiplier = 10
            return (7, max(k for k, v in value_counts.items() if v == 4))  # Four of a Kind
        if 3 in value_counts.values() and 2 in value_counts.values():
            self.multiplier = 5
            return (6, max(k for k, v in value_counts.items() if v == 3))  # Full House
        if is_flush:
            self.multiplier = 3
            return (5, sorted_hand)  # Flush
        if is_straight:
            self.multiplier = 1
            return (4, max(sorted_hand))  # Straight
        if 3 in value_counts.values():
            self.multiplier = 1
            return (3, max(k for k, v in value_counts.items() if v == 3))  # Three of a Kind
        if list(value_counts.values()).count(2) == 2:
            self.multiplier = 1
            return (2, max(k for k, v in value_counts.items() if v == 2))  # Two Pair
        if 2 in value_counts.values():
            self.multiplier = 1
            return (1, max(k for k, v in value_counts.items() if v == 2))  # One Pair
        return (0, max(sorted_hand))  # High Card

    def play_hand(self):
        self.reset_displayed_cards()  # Reset the cards for the new round
        
        self.player.hand = [self.player.get_cards(self.displayed_cards), self.player.get_cards(self.displayed_cards)]
        self.dealer.hand = [self.dealer.get_cards(self.displayed_cards), self.dealer.get_cards(self.displayed_cards)]
        
        print(f"Player's hand: {self.player.hand}")
        print(f"Blind: ${self.blind}")
        
        print(f"Initial Pot: {self.pot}")
        self.player.buyIn -= self.blind
        print("You Have", '$', self.player.buyIn, "Left")

        # Pre-Flop
        action = int(input("Check = 1, Bet 4x = 2: "))
        if action == 2:
            bet = 4 * self.ante
            if self.player.place_bet(bet):
                self.pot += bet
            print("Current Pot:", self.pot)
            print("You Have", self.player.buyIn, "Left")
        
        # Flop
        for _ in range(3):
            self.next_card()
        
        if action != 2:
            action = int(input("Check = 1, Bet 2x = 2: "))
            if action == 2:
                bet = 2 * self.ante
                if self.player.place_bet(bet):
                    self.pot += bet
                print("Current Pot:", self.pot)
                print("You Have", self.player.buyIn, "Left")
        
        # Turn & River
        for _ in range(2):
            self.next_card()
        
        if action != 2:
            action = int(input("Fold = 1, Bet 1x = 2: "))
            if action == 2:
                bet = self.ante
                if self.player.place_bet(bet):
                    self.pot += bet
            else:
                print("Player folds. Dealer wins this round.")
                print("You Have", '$', self.player.buyIn, "Left")
                return  # End the round immediately

        # Determine winner
        player_best_hand = self.evaluate_hand(self.player.hand + self.community_cards)
        dealer_best_hand = self.evaluate_hand(self.dealer.hand + self.community_cards)

        print(f"Dealer's hand: {self.dealer.hand}")
        print(f"Final Pot: {self.pot}")

        if player_best_hand > dealer_best_hand:
            print("Player Wins!")
            self.player.buyIn += self.pot * self.multiplier
            print("You Have", '$', self.player.buyIn, "Left")
            
        elif player_best_hand < dealer_best_hand:
            print("Dealer Wins!")
            print("You Have", '$', self.player.buyIn, "Left")
        else:
            print("It's a Tie!")
            self.player.buyIn += self.pot - self.blind
            print("You Have", '$', self.player.buyIn, "Left")
        return self.player.buyIn


#---------MAIN-------------

bln = True
buy_in = int(input("Enter Buy-in Amount: "))
game = Game(buy_in)

while bln:
    game.play_hand()  # Play the hand without resetting the game instance
    leave = int(input("Keep Playing?: YES == 1, NO == 2 "))
    if leave != 1:
        bln = False