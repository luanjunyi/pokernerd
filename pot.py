from collections import defaultdict
from log import L

DEBUG = False

class Pot(object):
    def __init__(self, dealer):
        self.size = 0
        self.bet = 0
        self.player_bet = [0] * dealer.num_player
        self.player_share = [0] * dealer.num_player
        self.dealer = dealer

    def post_blinds(self, sb_idx, bb_idx):
        self.size = 0
        self.bet = 2
        self.player_bet[sb_idx] = 1
        self.player_bet[bb_idx] = 2
        self.dealer.players[sb_idx].bet_chips(1)
        self.dealer.players[bb_idx].bet_chips(2)
        self.palyer_share = [0] * self.dealer.num_player
        L.info('player %d post 1' % sb_idx)
        L.info('player %d post 2' % bb_idx)

    def post_street_update(self):
        if DEBUG:
            print 'player bets:'
            for idx, v in enumerate(self.player_bet):
                print idx, v, 'alive', self.dealer.players[idx].is_alive()
            print 'actions'
            for idx, name, amount in self.dealer.actions:
                print idx, name, amount
        original_pot_size = self.size
        base_size = self.size
        # first collect dead money
        for idx, player in enumerate(self.dealer.players):
            if self.player_bet[idx] > 0 and player.is_fold():
                base_size += self.player_bet[idx]

        bet_list = defaultdict(list)
        num_new_bets = 0
        for idx, player in enumerate(self.dealer.players):
            if player.is_fold():
                # players already fold, set their share to zero
                self.player_share[idx] = 0
            elif player.is_allin and self.player_bet[idx] == 0:
                # players allin in previous street, keep their share
                continue
            else:
                # players have bet in current street
                num_new_bets += 1
                bet = self.player_bet[idx]
                if bet < self.bet:
                    assert player.is_allin, "player %d have bet %d, less than pot bet %d and she is not allin" % (idx, bet, self.bet)
                bet_list[bet].append(idx)

        bet_list = sorted(bet_list.items())
        num_processed = 0
        inc = 0
        for bet, player_indexes in bet_list: 
           inc = bet - inc
           share = base_size + inc * (num_new_bets - num_processed)
           base_size = share
           num_processed += len(player_indexes)
           for idx in player_indexes:
               self.player_share[idx] = share
               inc = bet
        assert num_new_bets == num_processed
        self.size += sum(self.player_bet)
        assert self.size == share == max(self.player_share), 'pot size %d != max share %d' % (self.size, share)
        self.bet = 0        
        self.player_bet = [0] * self.dealer.num_player
