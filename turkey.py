""" Module for matching customers and turkeys. """

from itertools import permutations

""" Price per kilogram of turkey. """
PRICE_PER_KILO = 1.0

"""
Value of a turkey that could not be sold to a customer.

0.0 = no value.
0.5 = half of price.
1.0 = equal to price.
"""
LEFTOVER_VALUE = 0.5


def calc_price(weight):
    """ Calculate the price of a turkey at a given weight. """
    return weight * PRICE_PER_KILO


def calc_profit(turkeys, customers, pairing):
    """
    Calculate profit from a given pairing of turkeys and customers.

    Args:
        turkeys ([Turkey]): A list of turkeys available.
        customers ([Customer]): A list of customers wanting turkeys.
        pairing ({Turkey: Customer}): Pairing turkeys to customers.
    """
    leftovers = set(turkeys) - set(pairing.keys())
    leftover_value = sum(turkey.leftover_value() for turkey in leftovers)

    sell_profit = sum(c.agreed_price(t) for t, c in pairing.iteritems())

    return sell_profit + leftover_value


def best_pairing(turkeys, customers):
    """ Return the best pairing for the given customers and turkeys. """
    perms = permutations(turkeys, len(customers))
    pairings = [dict(zip(ts, customers)) for ts in perms]

    # profit calculation
    def profit(pairing): return calc_profit(turkeys, customers, pairing)
    # maximimize profit, try every pairing
    return max(pairings, key=profit)


class Turkey:

    """ A big, delicious turkey. """

    def __init__(self, weight):
        """ Create a new turkey with a given weight. """
        self.weight = weight

    def price(self):
        """ The price of this turkey. """
        return calc_price(self.weight)

    def leftover_value(self):
        """ The leftover value of this turkey if not sold. """
        return self.price() * LEFTOVER_VALUE

    def __repr__(self):
        return "Turkey({})".format(self.weight)


class Customer:

    """ A starving, hungry customer. """

    def __init__(self, name, target_weight):
        """ Create a new customer with the weight of turkey they want. """
        self.name = name
        self.target_weight = target_weight

    def max_price(self):
        """ The max price the customer is willing to pay. """
        return calc_price(self.target_weight)

    def agreed_price(self, turkey):
        """ Return how much this customer will pay for a given turkey. """
        return min(self.max_price(), turkey.price())

    def __repr__(self):
        return "Customer({}, {})".format(self.name, self.target_weight)
