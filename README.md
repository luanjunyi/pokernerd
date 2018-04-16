# pokernerd

I'm building an AI for No Limit Texas Holdem. I'll periodically share some results/resources in this repo.

## Allin Equity(allin_equity.dat)

When headsup if allin preflop, there's 1,712,304 boards. I simulated each board every possible 812,175 confrontation. 
Each line describe the confrontation of one pair of hands. For example, 

`5s4h JsTh 598173 1092422 21709`

Means when 5s4h and JsTh go allin preflow, 5s4h will win 598173 times and lose 1092422 times. For 21709 times, it will be a tie.

This data is vital to any range equity calculation and solving many games. 'Jam or Fold' with short stacks, for example.
