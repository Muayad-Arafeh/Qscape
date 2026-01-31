import networkx as nx

# Create graph
G = nx.Graph()

# Add nodes
G.add_nodes_from(range(6))

# Add edges
edges = [
    (0, 1),
    (0, 2),
    (1, 3),
    (2, 4),
    (3, 5),
    (4, 5)
]
G.add_edges_from(edges)

# Print graph info
print("Nodes:", G.nodes())
print("Edges:", G.edges())
