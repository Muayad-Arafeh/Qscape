import networkx as nx

# Create graph
G = nx.Graph()
G.add_nodes_from(range(6))

edges = [
    (0, 1, {"cost": 3}),
    (0, 2, {"cost": 1}),
    (1, 3, {"cost": 2}),
    (2, 4, {"cost": 4}),
    (3, 5, {"cost": 3}),
    (4, 5, {"cost": 1})
]
G.add_edges_from(edges)

# Dijkstra shortest path
path = nx.dijkstra_path(G, source=0, target=5, weight="cost")
cost = nx.dijkstra_path_length(G, source=0, target=5, weight="cost")

print("Classical shortest path:", path)
print("Total cost:", cost)
