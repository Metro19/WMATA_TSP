# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

import os
import networkx as nx
import wmata
from tsp_solve import run_simulation
import pickle

# vars
# TODO: Move to a txt or easy edit file
TRAIN_WAIT_TIME = 6


def create_graph():
    if os.path.exists("wmata_graph.p"):
        print("Using Pickled Version")
        return pickle.load(open("wmata_graph.p", "rb"))

    else:
        # init graph
        G = nx.DiGraph()

        # add all stations
        for s in wmata.get_all_stations():
            G.add_node(s.station_code, object=s)
            print(s.station_code)

        # add all edges
        for e in wmata.get_all_paths_between_stations():
            G.add_edge(e.start_code, e.end_code, weight=e.distance, object=e)
            G.add_edge(e.end_code, e.start_code, weight=e.distance, object=e)
            print(e.start_code, e.end_code)

        for edge in G.edges:
            print(G[edge[0]][edge[1]])

        # pickle
        pickle.dump(G, open("wmata_graph.p", "wb"))
        return G


if __name__ == "__main__":
    G = create_graph()
    run_simulation(G)