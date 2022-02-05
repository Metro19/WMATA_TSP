import networkx as nx
from vrpy import VehicleRoutingProblem

START_END_PENALTY = 9999999999

def add_source_sink(G: nx.DiGraph):
    # Create nodes
    G.add_node("Source")
    G.add_node("Sink")

    # add source to all nodes with cost of zero
    for station in G.nodes:
        if station != "Sink" and station != "Source":
            G.add_edge("Source", station, cost=START_END_PENALTY)

    # add sink to all nodes with cost of zero
    for station in G.nodes:
        if station != "Sink" and station != "Source":
            G.add_edge(station, "Sink", cost=START_END_PENALTY)


def run_simulation(G: nx.DiGraph):
    add_source_sink(G)

    # generate and solve problem
    prob = VehicleRoutingProblem(G, load_capacity=len(G.nodes) + 1)
    prob.num_vehicles = 1  # limit to one vehicle
    prob.solve()

    # TODO: Get program to finish running

    print(prob.best_routes)
    print(prob.best_routes_cost - (START_END_PENALTY * 2))
