import random
import networkx as nx
from config import Config


class Strategy:

    def __init__(self):
        pass

    @staticmethod
    def choose_color(G: nx.Graph) -> int:
        """ chooses color based on implemented strategy """
        # TODO
        if random.randint(0, 1) == 0:
            return Config.FIRST_COLOR
        else:
            return Config.SECOND_COLOR


def is_complete(G: nx.Graph):
    """ checks if graph G is complete """
    n = G.order()
    return n*(n-1)/2 == G.size()


def check_monochromatic_clique(G: nx.Graph, clique_size):
    """ checks if there is a monochromatic clique of size clique_size in graph G """
    # TODO
    return False
