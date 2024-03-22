def is_complete(G):
    """ checks if graph G is complete """
    n = G.order()
    return n*(n-1)/2 == G.size()


def check_monochromatic_clique(G, clique_size):
    """ checks if there is monochromatic clique in graph G"""
    return False
