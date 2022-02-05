# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)
import networkx as nx
import wmata
from vrp import run_simulation
# vars
# TODO: Move to a txt or easy edit file
TRAIN_WAIT_TIME = 6


def create_graph():
    # init graph
    G = nx.DiGraph()

    # add all stations
    for s in wmata.get_all_stations():
        G.add_node(s.station_code, object=s)
        print(s.station_code)

    # add all edges
    for e in wmata.get_all_paths_between_stations():
        G.add_edge(e.start_code, e.end_code, cost=e.distance, object=e)
        G.add_edge(e.end_code, e.start_code, cost=e.distance, object=e)
        print(e.start_code, e.end_code)

    for edge in G.edges:
        print(G[edge[0]][edge[1]])

    run_simulation(G)


if __name__ == "__main__":
    create_graph()
