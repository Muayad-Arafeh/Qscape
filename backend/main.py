from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))
from graph import get_graph
from algorithms import (
    QuantumSolver,
    GeneticAlgorithmSolver,
    PathCache,
    dijkstra,
    dynamic_programming,
    astar,
)
from models import (
    RoutingRequest,
    PathResponse,
    GraphModel,
    GraphUpdate,
    HazardUpdate,
    ConstraintsUpdate,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


graph_data = get_graph()
quantum_solver = QuantumSolver()
genetic_solver = GeneticAlgorithmSolver(population_size=15, generations=8)
path_cache = PathCache()


@app.get("/graph", response_model=GraphModel)
def get_graph_endpoint():
    return graph_data


@app.post("/graph/update", response_model=GraphModel)
def update_graph(payload: GraphUpdate):
    global graph_data

    if payload.nodes is not None:
        graph_data["nodes"] = [node.model_dump(by_alias=True) for node in payload.nodes]

    if payload.edges is not None:
        graph_data["edges"] = [edge.model_dump(by_alias=True) for edge in payload.edges]

    if payload.start is not None:
        graph_data["start"] = payload.start

    if payload.end is not None:
        graph_data["end"] = payload.end

    rebuild_path_cache()
    return graph_data


@app.post("/graph/hazards", response_model=GraphModel)
def update_hazards(payload: HazardUpdate):
    nodes_by_id = {node["id"]: node for node in graph_data["nodes"]}
    for node_id in payload.node_ids:
        if node_id in nodes_by_id:
            nodes_by_id[node_id]["hazard"] = payload.set_to

    for edge_ref in payload.edge_ids:
        for edge in graph_data["edges"]:
            if edge["from"] == edge_ref.from_node and edge["to"] == edge_ref.to:
                edge["hazard"] = payload.set_to
                break

    return graph_data


@app.post("/graph/constraints", response_model=GraphModel)
def update_constraints(payload: ConstraintsUpdate):
    nodes_by_id = {node["id"]: node for node in graph_data["nodes"]}
    for node_id in payload.blocked_nodes:
        if node_id in nodes_by_id:
            nodes_by_id[node_id]["hazard"] = True

    for edge_ref in payload.blocked_edges:
        for edge in graph_data["edges"]:
            if edge["from"] == edge_ref.from_node and edge["to"] == edge_ref.to:
                edge["blocked"] = True
                break

    return graph_data


@app.post("/solve", response_model=PathResponse)
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
            path, cost = dijkstra(
                request.start,
                request.end,
                graph_data,
                request.avoid_hazards,
                request.risk_weight,
                request.hazard_weight,
            )
            is_optimal = True
    
    elif algorithm == "quantum":
        path, cost = quantum_solver.solve(request.start, request.end, graph_data)
        is_optimal = True
    
    elif algorithm == "genetic":
        path, cost = genetic_solver.solve(request.start, request.end, graph_data)
        is_optimal = False
    
    else:
        path, cost = dijkstra(
            request.start,
            request.end,
            graph_data,
            request.avoid_hazards,
            request.risk_weight,
            request.hazard_weight,
        )
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


class ComparisonResponse(BaseModel):
    algorithms: Dict[str, Dict]


@app.post("/solve/compare")
def compare_algorithms(request: RoutingRequest):
    """
    Run all available algorithms and return comparison results.
    Returns cost, execution time, and optimality for each.
    """
    if request.start not in {node["id"] for node in graph_data["nodes"]}:
        raise HTTPException(status_code=400, detail="Invalid start node")

    if request.end not in {node["id"] for node in graph_data["nodes"]}:
        raise HTTPException(status_code=400, detail="Invalid end node")

    results = {}

    # Dijkstra
    start_time = time.time()
    try:
        path, cost = dijkstra(
            request.start,
            request.end,
            graph_data,
            request.avoid_hazards,
            request.risk_weight,
            request.hazard_weight,
        )
        execution_time = (time.time() - start_time) * 1000
        results["dijkstra"] = {
            "path": path if cost != float("inf") else [],
            "cost": cost,
            "execution_time_ms": round(execution_time, 2),
            "is_optimal": True,
        }
    except Exception as e:
        results["dijkstra"] = {"error": str(e)}

    # Dynamic Programming
    start_time = time.time()
    try:
        path, cost = dynamic_programming(
            request.start,
            request.end,
            graph_data,
            request.avoid_hazards,
            request.risk_weight,
            request.hazard_weight,
        )
        execution_time = (time.time() - start_time) * 1000
        results["dynamic_programming"] = {
            "path": path if cost != float("inf") else [],
            "cost": cost,
            "execution_time_ms": round(execution_time, 2),
            "is_optimal": True,
        }
    except Exception as e:
        results["dynamic_programming"] = {"error": str(e)}

    # A* Heuristic
    start_time = time.time()
    try:
        path, cost = astar(
            request.start,
            request.end,
            graph_data,
            request.avoid_hazards,
            request.risk_weight,
            request.hazard_weight,
        )
        execution_time = (time.time() - start_time) * 1000
        results["astar"] = {
            "path": path if cost != float("inf") else [],
            "cost": cost,
            "execution_time_ms": round(execution_time, 2),
            "is_optimal": True,
        }
    except Exception as e:
        results["astar"] = {"error": str(e)}

    # Quantum QAOA/Simulation
    start_time = time.time()
    try:
        path, cost = quantum_solver.solve(request.start, request.end, graph_data)
        execution_time = (time.time() - start_time) * 1000
        results["quantum"] = {
            "path": path if cost != float("inf") else [],
            "cost": cost,
            "execution_time_ms": round(execution_time, 2),
            "is_optimal": False,
        }
    except Exception as e:
        results["quantum"] = {"error": str(e)}

    # Genetic Algorithm
    start_time = time.time()
    try:
        path, cost = genetic_solver.solve(request.start, request.end, graph_data)
        execution_time = (time.time() - start_time) * 1000
        results["genetic"] = {
            "path": path if cost != float("inf") else [],
            "cost": cost,
            "execution_time_ms": round(execution_time, 2),
            "is_optimal": False,
        }
    except Exception as e:
        results["genetic"] = {"error": str(e)}

    return {"algorithms": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
