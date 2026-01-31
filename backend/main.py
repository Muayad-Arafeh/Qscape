from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import heapq
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from graph import get_graph
from quantum_solver import QuantumSolver, GeneticAlgorithmSolver, PathCache

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RoutingRequest(BaseModel):
    start: int
    end: int
    algorithm: str = "dijkstra"


class PathResponse(BaseModel):
    path: List[int]
    cost: float
    nodes: List[Dict]
    edges: List[Dict]
    algorithm: str
    execution_time_ms: float
    is_optimal: bool


def dijkstra(start: int, end: int, graph_data: Dict) -> tuple:
    nodes = {node["id"]: node for node in graph_data["nodes"]}
    edges = graph_data["edges"]
    
    adjacency = {node["id"]: [] for node in graph_data["nodes"]}
    for edge in edges:
        adjacency[edge["from"]].append((edge["to"], edge["cost"]))
    
    distances = {node_id: float('inf') for node_id in nodes}
    distances[start] = 0
    parent = {node_id: None for node_id in nodes}
    pq = [(0, start)]
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current_dist > distances[current]:
            continue
        
        if current == end:
            break
        
        for neighbor, cost in adjacency[current]:
            new_dist = current_dist + cost
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    
    return path, distances[end]


graph_data = get_graph()
quantum_solver = QuantumSolver()
genetic_solver = GeneticAlgorithmSolver(population_size=15, generations=8)
path_cache = PathCache()
path_cache.precompute_paths(graph_data, dijkstra)


@app.get("/graph")
def get_graph_endpoint():
    return graph_data


@app.post("/solve")
def solve_routing(request: RoutingRequest):
    if request.start not in {node["id"] for node in graph_data["nodes"]}:
        raise HTTPException(status_code=400, detail="Invalid start node")
    
    if request.end not in {node["id"] for node in graph_data["nodes"]}:
        raise HTTPException(status_code=400, detail="Invalid end node")
    
    algorithm = request.algorithm.lower()
    path = None
    cost = None
    execution_time = 0.0
    is_optimal = False
    
    start_time = time.time()
    
    if algorithm == "cache":
        result = path_cache.get(request.start, request.end)
        if result[2]:
            path, cost = result[0], result[1]
            is_optimal = True
        else:
            path, cost = dijkstra(request.start, request.end, graph_data)
            is_optimal = True
    
    elif algorithm == "quantum":
        path, cost = quantum_solver.solve(request.start, request.end, graph_data)
        is_optimal = True
    
    elif algorithm == "genetic":
        path, cost = genetic_solver.solve(request.start, request.end, graph_data)
        is_optimal = False
    
    else:
        path, cost = dijkstra(request.start, request.end, graph_data)
        is_optimal = True
    
    execution_time = (time.time() - start_time) * 1000
    
    if cost == float('inf'):
        raise HTTPException(status_code=400, detail="No path exists between nodes")
    
    path_nodes = [node for node in graph_data["nodes"] if node["id"] in path]
    path_edges = [
        edge for edge in graph_data["edges"]
        if (edge["from"], edge["to"]) in [(path[i], path[i+1]) for i in range(len(path)-1)]
    ]
    
    return {
        "path": path,
        "cost": cost,
        "nodes": path_nodes,
        "edges": path_edges,
        "algorithm": algorithm,
        "execution_time_ms": round(execution_time, 2),
        "is_optimal": is_optimal
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
