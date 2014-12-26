""" Module for matching customers and turkeys. """

from itertools import permutations
import csv
import hungarian
import numpy as np

# Price per kilogram of turkey.
PRICE_PER_KILO = 1.0

"""
Value of a turkey that could not be sold to a customer.

0.0 = no value.
0.5 = half of price.
1.0 = equal to price.
"""
LEFTOVER_VALUE = 0.5


def load_turkeys(path):
    with open(path, 'r') as f:
        r = csv.DictReader(f, delimiter='\t')
        return [Turkey(float(line['Turkey weight (kg)'])) for line in r]


def load_customers(path):
    with open(path, 'r') as f:
        r = csv.DictReader(f, delimiter='\t')
        return [Customer(row['Name'], float(row['Orders (kg)']), row['Notes'])
                for row in r]


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
    assert set(leftovers) <= set(turkeys)

    leftover_value = sum(turkey.leftover_value() for turkey in leftovers)

    sell_profit = sum(c.agreed_price(t) for t, c in pairing.iteritems())
    assert sell_profit >= 0

    return sell_profit + leftover_value


def brute_pairing(turkeys, customers):
    """ Return the best pairing for the given customers and turkeys. """
    perms = permutations(turkeys, min(len(customers), len(turkeys)))
    pairings = [dict(zip(ts, customers)) for ts in perms]

    def profit(pairing):
        """ Profit calculation of pairing. """
        return calc_profit(turkeys, customers, pairing)

    # maximimize profit, try every pairing
    return max(pairings, key=profit)


def hungarian_pairing(turkeys, customers):
    """ Use the Hungarian algorithm to quickly pair. """
    size = max(len(turkeys), len(customers))
    matrix = np.matrix([[0.0] * size] * size)

    for t in range(size):
        for c in range(size):
            try:
                customer = customers[c]
            except IndexError:
                customer = None
            try:
                turkey = turkeys[t]
            except IndexError:
                turkey = None

            # calculate cost for this pairing
            if customer is None:
                # spare turkey, still has some value
                cost = -turkey.leftover_value()
            elif turkey is None:
                # no turkey for this customer, must buy him one
                # assume turkey is bought and sold with no profit made
                cost = 0
            else:
                cost = -customer.agreed_price(turkey)

            matrix[c, t] = cost

    np.set_printoptions(threshold=np.nan)
    t_to_c, c_to_t = hungarian.lap(matrix)

    assign_t_to_c = {}
    assign_c_to_t = {}

    for t, c in enumerate(c_to_t):
        try:
            customer = customers[c]
        except IndexError:
            customer = None
        try:
            turkey = turkeys[t]
        except IndexError:
            turkey = None

        if turkey is not None:
            assign_t_to_c[turkey] = customer

        if customer is not None:
            assign_c_to_t[customer] = turkey

    return assign_t_to_c, assign_c_to_t


class Turkey(object):

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


class Customer(object):

    """ A starving, hungry customer. """

    def __init__(self, name, target_weight, notes=None):
        """ Create a new customer with the weight of turkey they want. """
        self.name = name
        self.target_weight = target_weight
        self.notes = notes

    def ideal_price(self):
        """ The ideal price the customer is willing to pay. """
        return calc_price(self.target_weight)

    def agreed_price(self, turkey):
        """ Return how much this customer will pay for a given turkey. """
        if self.target_weight > turkey.weight:
            return turkey.price()
        else:
            return (self.ideal_price() + turkey.price()) / 2.0

    def __repr__(self):
        return "Customer({}, {}, {})".format(self.name, self.target_weight,
                                             self.notes)


if __name__ == '__main__':
    turkeys = load_turkeys('turkeys.tsv')
    customers = load_customers('customers.tsv')

    print '\nTurkeys:'
    for turkey in turkeys:
        print turkey

    print '\nCustomers:'
    for customer in customers:
        print customer

    print '\nPairing:'
    turk_to_cust, cust_to_turk = hungarian_pairing(turkeys, customers)

    for customer, turkey in cust_to_turk.iteritems():
        print '{}\t{}'.format(customer, turkey)

    print '\nLeftover turkeys:'
    for turkey in turk_to_cust:
        if turk_to_cust[turkey] is None:
            print turkey

    print '\nAbandoned customers:'
    for customer in cust_to_turk:
        if cust_to_turk[customer] is None:
            print customer

    with open('assignment.tsv', 'w') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['Name', 'Order (kg)', 'Notes', 'Assigned (kg)'])

        for customer, turkey in cust_to_turk.iteritems():
            if turkey is None:
                weight = 'None assigned'
            else:
                weight = turkey.weight

            w.writerow([customer.name, customer.target_weight, customer.notes,
                        weight])

    print '\nWritten to assignment.tsv file'
