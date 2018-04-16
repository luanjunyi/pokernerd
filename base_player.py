from action import Action
import random
from log import L

class BasePlayer(object):
    def __init__(self, stack):
        self.buyin = stack
        self.stack = stack
        self.is_allin = False
        self.balance = stack
        self.current_hand_bet = 0 # keep track of how many chips are bet in current hand

    def init_statistics(self):
        self.current_hand_bet = 0

    def bet_chips(self, amount):
        self.stack -= amount
        self.current_hand_bet += amount
        assert self.stack >= 0

    def sit_at_table(self, dealer, idx):
        self.dealer = dealer
        self.index = idx

    def recieve_hole_cards(self, card1, card2):
        self.hole = [card1, card2]

    def recieve_flop(self, f1, f2, f3):
        self.flop = [f1, f2, f3]

    def recieve_turn(self, turn):
        self.turn = turn

    def recieve_river(self, river):
        self.river = river

    def get_pot_size_when_call(self, pot):
        size = pot.size
        for player in self.dealer.players:
            if player.index != self.index and pot.player_bet[player.index] == pot.bet:
                size += pot.bet
        size += pot.bet # my own bet
        return size

    def get_pot_size_when_check(self, pot):
        size = pot.size
        for player in self.dealer.players:
            if player.index != self.index and pot.player_bet[player.index] == pot.bet:
                size += pot.bet
        return size

    def action(self, pot, actions):
        diff = pot.bet - pot.player_bet[self.index]
        assert diff >= 0
        if diff == 0:
            pot_size = self.get_pot_size_when_call(pot)
            #return Action('check')
            #return Action('bet', pot_size * 2 / 3)
            return random.choice([Action('check'), Action('bet', pot_size * 2 / 3)])
        if diff > 0:
            pot_size = self.get_pot_size_when_call(pot)
            #return Action('call')
            #return Action('raise', pot_size)
            return random.choice([Action('call'), Action('fold'), Action('raise', pot_size)])

    def is_alive(self):
        return self.is_allin or (self.index in self.dealer.active_player_indexes)

    def is_fold(self):
        return not self.is_alive()

    def refill(self):
        if self.stack < self.buyin * 0.7:
            fill = self.buyin - self.stack
            L.info('player %d refill %d' % (self.index, fill))
            self.stack = self.buyin
            self.balance += fill

    # SB -> 0, BB -> 1, ... used for distribute chip between tied hands
    def hand_position(self):
        sb_idx = self.dealer.sb_index()
        return (self.index - sb_idx + self.dealer.num_player) % self.dealer.num_player
