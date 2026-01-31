# Qscape - Quantum-Optimized Evacuation Routing

A hackathon prototype for quantum-accelerated routing optimization in evacuation scenarios.

## Project Structure

```
Qscape/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── graph.py          # Graph data and routing logic
│   ├── quantum_solver.py # (Coming) Quantum solver integration
│   ├── models.py         # (Coming) Data models
│   └── __init__.py
├── frontend/
│   ├── index.html        # UI interface
│   ├── app.js            # Graph visualization & API calls
│   └── style.css         # Styling
├── requirements.txt      # Python dependencies
└── README.md            # This file
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

Open `frontend/index.html` in a web browser (or use a local server):

```bash
# Option A: Using Python
python -m http.server 8080 --directory frontend

# Then visit: http://localhost:8080
```

## Testing

### Quick Test

1. **Backend API test:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/graph
   ```

2. **Frontend test:**
   - Open frontend in browser
   - Click "Find Path" button (should use default: node 0 → node 23)
   - Verify path highlights in yellow and cost displays
   - Try clicking different nodes on the canvas
   - Change start/end inputs and click "Find Path"

### Full End-to-End

```bash
# Terminal 1: Start backend
python backend/main.py

# Terminal 2: Start frontend server
python -m http.server 8080 --directory frontend

# Terminal 3: Test routing
curl -X POST http://localhost:8000/solve -H "Content-Type: application/json" -d '{"start": 0, "end": 23}'
```

## Features

- ✅ Interactive graph visualization
- ✅ Dijkstra shortest path algorithm
- ✅ Zone-based graph (Safe → Danger → Safe → Exit)
- ✅ RESTful API
- 🔄 Quantum solver (in progress)

## Architecture

**Backend:** FastAPI + Dijkstra routing
**Frontend:** Canvas-based graph rendering + fetch API
**Data:** Static evacuation graph with 24 nodes across 3 zones + exit