# Qscape - Quantum-Optimized Evacuation Routing

A quantum-accelerated escape planning system combining classical algorithms, AI heuristics, and quantum computing for fast, safe route optimization in crisis scenarios.

## Features

- ✅ **Interactive Graph Visualization** – Canvas-based real-time visualization with hazard indicators
- ✅ **Multiple Algorithms** – Dijkstra, Dynamic Programming, A*, Quantum QAOA, Genetic Algorithm
- ✅ **Algorithm Comparison** – Run all algorithms simultaneously and compare performance
- ✅ **Hazard Management** – Mark zones/nodes as hazardous, visualize risk levels
- ✅ **Risk-Aware Routing** – Weighted objective combining time and risk
- ✅ **Quantum QAOA** – Real quantum-inspired QAOA circuit with Ising Hamiltonian formulation
- ✅ **RESTful API** – FastAPI backend with graph mutation and constraint endpoints
- ✅ **Tailwind CSS UI** – Modern, responsive interface

## Project Structure

```
Qscape/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI server
│   ├── graph.py             # Graph data with risk/hazard attributes
│   ├── models.py            # Pydantic data models
│   └── algorithms/          # Algorithm implementations
│       ├── __init__.py
│       ├── dijkstra.py      # Dijkstra shortest path
│       ├── dynamic_programming.py  # Bellman-Ford DP
│       ├── astar.py         # A* with Euclidean heuristic
│       ├── quantum.py       # QAOA solver
│       ├── genetic.py       # Genetic Algorithm
│       └── objective.py     # Multi-objective cost function
├── frontend/
│   ├── index.html           # Tailwind CSS UI
│   ├── app.js               # Graph visualization & API interaction
│   └── style.css            # (deprecated, using Tailwind)
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Backend Server

```bash
python backend/main.py
```

Server runs on `http://localhost:8000`

### 3. Open Frontend

```bash
# Option A: Using Python HTTP server
python -m http.server 8080 --directory frontend

# Then visit: http://localhost:8080
```

## API Endpoints

### Graph Management

- **GET `/graph`** – Retrieve current graph data
- **POST `/graph/update`** – Update nodes, edges, start/end points
- **POST `/graph/hazards`** – Mark nodes/edges as hazardous
- **POST `/graph/constraints`** – Block nodes/edges

### Routing

- **POST `/solve`** – Solve single routing request
  ```json
  {
    "start": 0,
    "end": 23,
    "algorithm": "dijkstra",
    "avoid_hazards": false,
    "risk_weight": 0.5,
    "hazard_weight": 0.0
  }
  ```

- **POST `/solve/compare`** – Run all algorithms and compare
  ```json
  {
    "start": 0,
    "end": 23,
    "algorithm": "dijkstra",
    "avoid_hazards": false,
    "risk_weight": 0.5,
    "hazard_weight": 0.0
  }
  ```

- **GET `/health`** – Health check

## Algorithms

### Classical Approaches
1. **Dijkstra** – Optimal shortest path (O(E log V))
2. **Dynamic Programming** – Bellman-Ford relaxation for general graphs
3. **A*** – Heuristic search with Euclidean distance guidance

### Quantum & Heuristic
4. **Quantum QAOA** – Variational quantum algorithm with:
   - Ising Hamiltonian encoding edge costs
   - 2-layer QAOA ansatz
   - ZZ interactions for node coupling
   - Fallback to quantum annealing simulation if Qiskit unavailable

5. **Genetic Algorithm** – Population-based metaheuristic with crossover/mutation

### Multi-Objective Cost Function

C = α·time + β·risk + γ·hazard_penalty

Where:
- `time` = edge travel cost
- `risk` = edge risk coefficient
- `hazard_penalty` = additional cost if node/edge marked hazardous
- Weights: α (time_weight), β (risk_weight), γ (hazard_weight) are configurable

## Testing

### API Test

```bash
# Health check
curl http://localhost:8000/health

# Get graph
curl http://localhost:8000/graph

# Single solve
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{"start": 0, "end": 23, "algorithm": "dijkstra"}'

# Compare all algorithms
curl -X POST http://localhost:8000/solve/compare \
  -H "Content-Type: application/json" \
  -d '{"start": 0, "end": 23}'
```

### Frontend Test

1. Open frontend in browser
2. Graph displays 24 nodes in 4 zones (A, B, C, Exit)
3. Click "Find Path" to solve with selected algorithm
4. Click "Compare All" to benchmark all algorithms
5. Use sliders to adjust time/risk weighting
6. Click "Toggle Zone B as Hazard" to mark danger zone
7. Watch visual updates: path highlighted in yellow, hazards in red

## Architecture

```
┌─────────────┐
│  Frontend   │  (Tailwind + Canvas visualization)
│  HTML/JS    │
└──────┬──────┘
       │ REST API
       ▼
┌─────────────────────────────┐
│   FastAPI Backend           │
├─────────────────────────────┤
│  Algorithm Layer:           │
│  • Dijkstra                 │
│  • Dynamic Programming      │
│  • A*                       │
│  • Quantum QAOA (Qiskit)    │
│  • Genetic Algorithm        │
├─────────────────────────────┤
│  Data Layer:                │
│  • Graph (24 nodes, edges)  │
│  • Risk/Hazard attributes   │
│  • Multi-objective costing  │
└─────────────────────────────┘
```

## Performance Notes

**24-node graph:** All algorithms complete in < 100ms
- Dijkstra: ~1-2ms (optimal)
- A*: ~1-3ms (optimal, guided search)
- DP: ~3-5ms (optimal)
- Quantum QAOA: ~10-20ms (heuristic, Qiskit simulation overhead)
- Genetic: ~5-15ms (heuristic, population-based)

**Quantum Advantage:** True quantum advantage requires:
- Much larger graphs (100+ nodes, 1000+ edges)
- Hard constraints / complex topologies
- Real quantum hardware (not simulation)

Current implementation uses Qiskit simulator for exploration and learning.

## Objective Weighting Examples

### Safety-First Evacuation
```
time_weight = 1.0
risk_weight = 2.0  # Prioritize avoiding risk
```
Objective: C = 1.0·time + 2.0·risk

### Speed-First Evacuation
```
time_weight = 2.0
risk_weight = 0.1  # Minor risk concern
```
Objective: C = 2.0·time + 0.1·risk

### Balanced Approach
```
time_weight = 1.0
risk_weight = 0.5  # Equal emphasis
```
Objective: C = 1.0·time + 0.5·risk

## Future: AI Integration

Next phase will add:
- **Hazard Prediction AI** – Neural network predicts blocked areas from real-time data
- **Dynamic Graph Update** – AI triggers route recalculation based on changing conditions
- **Risk Assessment Model** – ML model estimates risk scores from environmental factors
- **Adaptive Weighting** – AI adjusts time/risk weights based on scenario

## License

Hackathon prototype – Educational use
