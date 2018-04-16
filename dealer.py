from deuces import Deck, Card, Evaluator
from pot import Pot
from action import Action
import random
from log import L

MAX_PLAYER_NUM = 9

class Dealer(object):
    def __init__(self, players, verbose=False):
        self.num_player = len(players)
        self.players = players
        assert 1 < self.num_player <= MAX_PLAYER_NUM
        self.btn_index = random.randint(0, self.num_player - 1)
        for idx, player in enumerate(players):
            player.sit_at_table(self, idx)
        self.active_player_indexes = set(xrange(self.num_player))
        self.evaluator = Evaluator()
        self.verbose = verbose
        
    ###################### UTILS ########################
    def bb_index(self):
        return (self.btn_index + 2)  % self.num_player if self.num_player > 2 else (self.btn_index + 1) % self.num_player

    def sb_index(self):
        return (self.btn_index + 1)  % self.num_player if self.num_player > 2 else self.btn_index

    def utg_index(self):
        return (self.btn_index + 3)  % self.num_player if self.num_player > 2 else self.sb_index()

    def pre_index(self, idx):
        return (idx-1) % self.num_player

    def next_index(self, idx):
        return (idx+1) % self.num_player

    def next_active_index(self, idx):
        while True:
            idx = self.next_index(idx)
            if idx in self.active_player_indexes:
                return idx
            
    def pre_active_index(self, idx):
        while True:
            idx = self.pre_index(idx)
            if idx in self.active_player_indexes:
                return idx

    def init_hand(self):
        self.active_player_indexes = set(xrange(self.num_player))
        for player in self.players:
            player.is_allin = False
            player.refill()
            player.init_statistics()
        
        self.pot = Pot(self)
        self.pot.post_blinds(self.sb_index(), self.bb_index())
        self.actions = []

    def execute_action(self, player_index, action):
        L.info('player %d %s %d' % (player_index, action.name, action.amount))
        pot = self.pot
        player = self.players[player_index]
        if action.name == 'fold':
            self.active_player_indexes.remove(player_index)
        elif action.name == 'call':
            amount = pot.bet - pot.player_bet[player_index]
            if amount > player.stack:
                amount = player.stack                

            pot.player_bet[player_index] += amount
            player.bet_chips(amount)

        elif action.name == 'check':
            if pot.bet != pot.player_bet[player_index]:
                L.info('Can not check!!! Force to fold')
                return self.execute_action(player_index, Action('fold'))
        else:
            assert action.name in ('bet', 'raise')
            if action.amount > player.stack:
                L.info('stack(%d) raise (%d), set to allin' % (player.stack, action.amount))
                action.amount = player.stack
                return self.execute_action(player_index, action)

            if pot.player_bet[player_index] + action.amount < pot.bet:
                L.info('raise amount less than call, will execute call')
                return self.execute_action(player_index, Action('call'))
            
            increase_amount = action.amount - (pot.bet - pot.player_bet[player_index])
            if increase_amount < self.min_raise_size and player.stack > action.amount:
                L.info('Bet/Raise size(%d) smaller than min raise(%d), will execute call' % (increase_amount, self.min_raise_size))
                return self.execute_action(player_index, Action('call'))

            self.min_raise_size = max(increase_amount, self.min_raise_size)
            pot.bet += increase_amount
            player.bet_chips(action.amount)
            pot.player_bet[player_index] += action.amount

        assert player.stack >= 0, 'player stack(%d) is negative' % player.stack
        if player.stack == 0:
            player.is_allin = True
            self.active_player_indexes.remove(player_index)
        self.actions.append((player_index, action.name, action.amount))
        return action.name in ('raise', 'bet')

    # play a hand
    def play(self):
        # move button
        self.btn_index = (self.btn_index + 1) % self.num_player
        L.info('BTN is at %d' % self.btn_index)
        # shuffled deck
        self.deck = Deck()
        # post blinds
        self.init_hand()

        # deal hole cards
        self.deal_preflop()
        # preflop actions
        self.play_preflop()

        self.deal_flop()
        #self.play_flop()

        self.deal_turn()
        #self.play_turn()

        self.deal_river()
        #self.play_river()

        wins = self.close_hand()

        L.info('winnings: ' + str(wins))
        for i in xrange(self.num_player):
            self.players[i].stack += wins[i]
        L.info('stacks: ' +  str([p.stack for p in self.players]))

    def play_one_street(self, action_player_idx):
        self.min_raise_size = 2        
        if action_player_idx not in self.active_player_indexes:
            action_player_idx = self.next_active_index(action_player_idx)
        close_action_idx = self.pre_active_index(action_player_idx)
        #L.info('action will close at %d' % close_action_idx)
        while True:
            action = self.players[action_player_idx].action(self.pot, self.actions)
            is_aggresion = self.execute_action(action_player_idx, action)
            # print '%d player is active' % len(self.active_player_indexes)
            if is_aggresion:
                if len(self.active_player_indexes) == 0 or \
                   (len(self.active_player_indexes) == 1 and action_player_idx in self.active_player_indexes):
                    break
                close_action_idx = self.pre_active_index(action_player_idx)
                L.info('action will close at %d' % close_action_idx                )
            else:
                if close_action_idx == action_player_idx:
                    break
            L.info('pot size: %d' % (self.pot.size + sum(self.pot.player_bet)))
            action_player_idx = self.next_active_index(action_player_idx)

        # update pot status
        self.pot.post_street_update()
        L.info('street complete, pot size: %d' % (self.pot.size))
        L.info('player share and stack: ' + str([(self.pot.player_share[p.index], p.stack)for p in self.players]))
        
    def play_preflop(self):
        if len(self.active_player_indexes) <= 1:
            return
        self.play_one_street(self.utg_index())

    def play_flop(self):
        if len(self.active_player_indexes) <= 1:
            return
        self.play_one_street(self.sb_index())

        
    def play_turn(self):
        if len(self.active_player_indexes) <= 1:
            return
        self.play_one_street(self.sb_index())

    def play_river(self):
        if len(self.active_player_indexes) <= 1:
            return
        self.play_one_street(self.sb_index())
        
    # send hole cards to players
    def deal_preflop(self):
        self.deck_idx = 0
        for player in self.players:
            hole = self.deck.cards[self.deck_idx : self.deck_idx+2]
            self.deck_idx += 2
            player.recieve_hole_cards(*hole)


    # send flop cards to players
    def deal_flop(self):
        flop = self.deck.cards[self.deck_idx : self.deck_idx + 3]
        self.deck_idx += 3
        for player in self.players:
            player.recieve_flop(*flop)
        self.flop = flop

    # send turn card to players
    def deal_turn(self):
        turn = self.deck.cards[self.deck_idx]
        self.deck_idx += 1
        for player in self.players:
            player.recieve_turn(turn)
        self.turn = turn

    # send river card to players
    def deal_river(self):
        river = self.deck.cards[self.deck_idx]
        self.deck_idx += 1
        for player in self.players:
            player.recieve_river(river)
        self.river = river

    # distribute pot according to show down
    def close_hand(self):
        pot = self.pot
        
        shares = sorted(pot.player_share)
        for i in xrange(len(shares) - 1, -1, -1):
            if shares.count(shares[i]) > 1 or (i < len(shares) - 1 and shares[i] < shares[i+1]):
                self.effective_pot_size = shares[i]
                #print 'player share: %s, effective stack size: %d' % (pot.player_share, self.effective_pot_size)
                break
        assert pot.size == sum([p.current_hand_bet for p in self.players]), 'pot size(%d) != all bet size(%d)' % \
            (pot.size, sum([p.current_hand_bet for p in self.players]))
        
        board = self.flop + [self.turn,] + [self.river,]

        # sort players who hadn't fold by this key: (hand, hand position)
        lst = sorted([(self.evaluator.evaluate(board, p.hole),
                       p.hand_position(),
                       pot.player_share[p.index],
                       p) for p in self.players if p.is_alive()],
                     key = lambda x: (x[0], x[1]))
        L.info("pot: %d, player stack: %s" % (pot.size, str([t.stack for t in self.players])))
        L.info("alive players: " + str(lst))
        win = [0] * self.num_player
        low = 0
        money = pot.size
        money_distributed = 0
        while low < len(lst) and money > 0:
            high = low + 1
            while high < len(lst) and lst[high][0] == lst[low][0]:
                high += 1

            # distribute the chips between players in lst[low: high)                
            amounts = [0,]
            for i in xrange(low, high):
                player = lst[i][-1]
                pot.player_share[player.index] -= money_distributed
                pot.player_share[player.index] = max(pot.player_share[player.index], 0)
                if pot.player_share[player.index] > 0:
                    amounts.append(pot.player_share[player.index])
            amounts.sort()
            amounts = [amounts[i] - amounts[i-1] for i in xrange(1, len(amounts))]

            for amount in amounts:
                if amount == 0:
                    continue
                assert amount > 0, 'amount(%d) is negative'
                in_money = set()
                # distribute amount evenly to players, SB takes precedence, followed by BB, UTG...

                for i in xrange(low, high):
                    if pot.player_share[lst[i][-1].index] > 0:
                        assert pot.player_share[lst[i][-1].index] >= amount
                        in_money.add(lst[i][-1].index)

                sz = len(in_money)                        
                share = amount / sz
                extra = amount % sz
                assert share * sz + extra == amount, 'arithmatic error in close hand chip counting'
                for i in xrange(low, high):
                    player = lst[i][-1]                    
                    if player.index in in_money:
                        win[player.index] += share
                for i in xrange(low, high):
                    if extra == 0:
                        break
                    player = lst[i][-1]
                    if player.index in in_money:                    
                        win[player.index] += 1
                        extra -= 1

                money_distributed += amount
                money -= amount
                for idx in in_money:
                    pot.player_share[idx] -= amount
                
            low = high

        assert money == 0 and money_distributed == pot.size == sum(win), \
            'money = %d, distributed = %d, pot size = %d, sum(win) = %d(%s)' % (money, money_distributed, pot.size, sum(win), win)
        return win
        
        
