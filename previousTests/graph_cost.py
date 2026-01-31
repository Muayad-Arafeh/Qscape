import networkx as nx

# Create graph
G = nx.Graph()

# Add nodes
G.add_nodes_from(range(6))

# Add edges with cost
edges = [
    (0, 1, {"cost": 3}),
    (0, 2, {"cost": 1}),
    (1, 3, {"cost": 2}),
    (2, 4, {"cost": 4}),
    (3, 5, {"cost": 3}),
    (4, 5, {"cost": 1})
]
G.add_edges_from(edges)

# Print edges with cost
for u, v, data in G.edges(data=True):
    print(f"{u} -> {v} | cost = {data['cost']}")
