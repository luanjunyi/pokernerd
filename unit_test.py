import sys
import numpy as np
from pot import Pot
from dealer import Dealer
from base_player import BasePlayer
from matplotlib import pyplot as plt

NUM_PLAYER = 2
STACK = 1000
SIM_NUM = int(sys.argv[1])

def simulate():
    players = [BasePlayer(STACK) for _ in xrange(NUM_PLAYER)]
    dealer = Dealer(players)
    print 'simulating %d hands' % SIM_NUM
    win_rate = {}
    var = 0
    for i in xrange(SIM_NUM):
        n = i + 1        
        dealer.play()
        x = players[0].current_hand_bet * 2
        var += x ** 2
        std = 100.0 / n * np.sqrt(var)

        
        if n % 5000 == 0:
            win_rate = (players[0].stack - players[0].balance) / 2.0 * 100 / n
            print "%d hands, win rate: %.4fbb/100, stddev: %.4f" % (n, win_rate, std)
            print players[0].current_hand_bet

    balances = [p.stack - p.balance for p in dealer.players]
    assert sum(balances) == 0

    #plt.plot(win_rate[10000:])
    #plt.show()

    
simulate()

# rec = {}
# for sim_num in [1000, 3000, 10000, 50000, 100000, 300000, 1000000]:
#     players = [BasePlayer(STACK) for _ in xrange(NUM_PLAYER)]
#     dealer = Dealer(players)
#     sys.stderr.write('simulating %d hands\n' % sim_num)
#     for i in xrange(sim_num):
#         dealer.play()
#     t = max([(p.stack - p.balance) / 2.0 * 100 / sim_num for p in players])
#     sys.stderr.write("%d: %.3f\n" % (sim_num, t))
#     rec[sim_num] = t

# sys.stderr.write(str(sorted(rec.items())))
