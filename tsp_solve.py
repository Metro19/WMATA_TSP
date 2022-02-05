import mlrose
import networkx


def run_simulation(G: networkx.Graph):
    dists = graph_to_tlist(G)

    f_dists = mlrose.TravellingSales(distances=dists)
    prob = mlrose.TSPOpt(length=len(G.nodes), fitness_fn=f_dists, maximize=False)
    bs, bf = mlrose.genetic_alg(prob, random_state=2)

    print(bs)
    print(bf)


def graph_to_tlist(G: networkx.Graph) -> list[tuple]:
    dists = []

    # iter through edges
    for edge in G.edges:
        dists.append((edge[0], edge[1], edge[2]["weight"]))

    return dists
