# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

import mlrose
import networkx

# Timing Vars
import numpy

OSI_TIME = 10
LINE_SWITCH = 7


def numeric_station_code(code: str, nodes: list) -> int:
    """
    Convert the station code into an integer for mlrose

    :param nodes: A list of the Graph nodes
    :param code: Station code
    :return: Unique numeric code for each station code
    """
    full = nodes.index(code)
    return int(full)


def graph_to_tlist(G: networkx.Graph) -> list[tuple]:
    """
    Convert a graph into a list of tuples for mlrose

    :param G: Graph of system
    :return: List of tuples for mlrose
    """
    dists = []

    # iter through edges
    for edge in G.edges(data=True):
        # print(edge)
        dists.append((numeric_station_code(edge[0], list(G.nodes)), numeric_station_code(edge[1], list(G.nodes)),
                      edge[2]["weight"]))

    return dists


def run_simulation(G: networkx.Graph):
    """
    Run a tsp simulation

    :param G: Graph to run off of
    :return:
    """

    # verify complete graph
    # prep data
    dists = graph_to_tlist(G)

    # run solutions
    f_dists = mlrose.TravellingSales(distances=dists)
    prob = mlrose.TSPOpt(length=len(G.nodes), fitness_fn=f_dists, maximize=False)
    bs, bf = mlrose.genetic_alg(prob, random_state=2, mutation_prob=.75)

    # print data
    print(bs)
    print(bf)

    # TODO: Check why fitness returns infinity
    """Solving this problem would require adding connections from
    every station to every station to simulate a 2D Plane"""
