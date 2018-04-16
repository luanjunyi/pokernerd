# pokernerd

I'm building an AI for No Limit Texas Holdem. I'll periodically share some results/resources in this repo.

## Game Logic
All rules of NLTH is implemented. You can build a bot by creating a subclass of BasePlayer. BasePlayer will just play randomly. The code below will shows how to simulate a 6MAX game with 1000 hands. The blind is 1/2.

```python
STACK = 200
NUM_PLAYER = 6
SIM_NUM = 1000
players = [BasePlayer(STACK) for _ in xrange(NUM_PLAYER)]
dealer = Dealer(players)
print 'simulating %d hands' % SIM_NUM

for i in xrange(SIM_NUM):       
    dealer.play()
    
balances = [p.stack - p.balance for p in dealer.players]
print balances
```

## Allin Equity(allin_equity.dat)

When headsup if allin preflop, there's 1,712,304 boards. I simulated each board every possible 812,175 confrontation. 
Each line describe the confrontation of one pair of hands. For example, 

`5s4h JsTh 598173 1092422 21709`

Means when 5s4h and JsTh go allin preflow, 5s4h will win 598173 times and lose 1092422 times. For 21709 times, it will be a tie.

This data is vital to any range equity calculation and solving many games. 'Jam or Fold' with short stacks, for example.
