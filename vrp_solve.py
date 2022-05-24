# WMATA TSP - wmata.py
# Calculate the fastest route through all Metro stations
# (c) Zack Bamford
# (Not affiliated in any way with the Washington Metropolitan Area Transportation Authority)

import networkx
import numpy
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt  # TODO: REMOVE

# SETTINGS
import wmata

NUM_VEHICLES = 1  # set to one for this scenario
DEPOT = 0  # To Appease Google™


# def dist_matrix(G: networkx.Graph) -> list[list[int]]:
#     grid = numpy.zeros(G.size(), G.size()).tolist()
#
#     # fill grid
#     for r_loc, r_node in enumerate(G.nodes):
#         for c_loc, c_node in enumerate(G.nodes):

class Solver:
    # vars
    G: networkx.Graph
    stations_by_index: list[str]
    sts_obj: wmata.StationToStation

    def __init__(self, G: networkx.Graph):
        self.G = G

        # save in a format for Google
        names = []
        for node in self.G.nodes:
            names.append(node)
        self.stations_by_index = names

        # TODO: REMOVE
        # visualize
        networkx.draw(G, with_labels=True)
        plt.show()

        # create StationToStation information object
        self.sts_obj = wmata.StationToStation()

    def distance_callback(self, start_index, end_index) -> int:
        """
        Get the distance between two nodes.

        :param start_index: Starting index
        :param end_index: Ending index
        :return: Total distance or -1 if not found
        """
        # convert index to string
        start_node = self.stations_by_index[start_index - 1]
        end_node = self.stations_by_index[end_index - 1]

        # print(start_node, end_node)
        # check if start_node is a depot
        if start_node == 0:
            print(start_node, end_node, "->", "Depot")
            return 0

        # check for both nodes
        if not self.G.has_node(start_node) and not self.G.has_node(end_node):
            print(start_node, end_node, "->", "Node fail")
            return -1

        # get path
        try:
            return self.sts_obj.station_to_station_predicted_time(start_node, end_node)
        except networkx.NetworkXNoPath:
            print(start_node, end_node, "->", "No Path")
            return -1

    def main(self):
        """
        Main VRP solver

        :return:
        """

        # setup model
        manager = pywrapcp.RoutingIndexManager(len(self.stations_by_index), NUM_VEHICLES, DEPOT)
        routing = pywrapcp.RoutingModel(manager)

        # setup distance information
        dist_callback = routing.RegisterTransitCallback(self.distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)

        # solve params
        params = pywrapcp.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        # solve
        sol = routing.SolveWithParameters(params)

        # check for valid solution
        if sol:
            print(True)
        else:
            print(False)

    def solution(self):
        pass

    # TODO: Print solution


def run_simulation(G: networkx.Graph):
    """
    Run a VRP simulation

    :param G: Graph to run off of
    :return:
    """
    solve = Solver(G)
    solve.main()
    # main(G)
