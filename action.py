class Action(object):
    def __init__(self, name, amount = 0):
        assert name in ('check', 'call', 'bet', 'raise', 'fold')
        if name in ('check', 'call', 'fold'):
            assert amount == 0
        else:
            assert amount > 0, '%s: amount(%d) <= 0' % (name, amount)
        self.name = name
        self.amount = amount
