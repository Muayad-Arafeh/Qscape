const API_BASE = 'http://localhost:8000';

let graphData = null;
let selectedStart = 0;
let selectedEnd = 23;
let solvedPath = null;
let canvas = null;
let ctx = null;
let hazardNodes = new Set();
let timeWeight = 1.0;
let riskWeight = 0.5;

const nodeRadius = 12;
const padding = 50;

async function initializeApp() {
    canvas = document.getElementById('graphCanvas');
    ctx = canvas.getContext('2d');

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    try {
        const response = await fetch(`${API_BASE}/graph`);
        graphData = await response.json();
        drawGraph();
    } catch (error) {
        console.error('Failed to load graph:', error);
        alert('Error: Could not connect to backend. Make sure the server is running on port 8000.');
    }

    // Event listeners
    document.getElementById('solveBtn').addEventListener('click', solveRouting);
    document.getElementById('compareBtn').addEventListener('click', compareAlgorithms);
    document.getElementById('resetBtn').addEventListener('click', resetVisualization);
    document.getElementById('hazardZoneB').addEventListener('click', toggleZoneBHazard);

    document.getElementById('startNode').addEventListener('change', (e) => {
        selectedStart = parseInt(e.target.value);
        drawGraph();
    });

    document.getElementById('endNode').addEventListener('change', (e) => {
        selectedEnd = parseInt(e.target.value);
        drawGraph();
    });

    document.getElementById('timeWeight').addEventListener('input', (e) => {
        timeWeight = parseFloat(e.target.value);
        document.getElementById('timeWeightValue').textContent = timeWeight.toFixed(1);
    });

    document.getElementById('riskWeight').addEventListener('input', (e) => {
        riskWeight = parseFloat(e.target.value);
        document.getElementById('riskWeightValue').textContent = riskWeight.toFixed(1);
    });

    canvas.addEventListener('click', handleCanvasClick);
}

function resizeCanvas() {
    const container = canvas.parentElement;
    canvas.width = container.clientWidth - 8;
    canvas.height = container.clientHeight - 8;
    if (graphData) drawGraph();
}

function getScreenCoords(node) {
    const minX = Math.min(...graphData.nodes.map(n => n.x));
    const maxX = Math.max(...graphData.nodes.map(n => n.x));
    const minY = Math.min(...graphData.nodes.map(n => n.y));
    const maxY = Math.max(...graphData.nodes.map(n => n.y));

    const width = canvas.width - 2 * padding;
    const height = canvas.height - 2 * padding;

    const scaleX = (maxX - minX) > 0 ? width / (maxX - minX) : 1;
    const scaleY = (maxY - minY) > 0 ? height / (maxY - minY) : 1;

    const screenX = padding + (node.x - minX) * scaleX;
    const screenY = padding + (node.y - minY) * scaleY;

    return { x: screenX, y: screenY };
}

function drawGraph() {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawEdges();
    drawNodes();
}

function drawEdges() {
    graphData.edges.forEach(edge => {
        const fromNode = graphData.nodes.find(n => n.id === edge.from);
        const toNode = graphData.nodes.find(n => n.id === edge.to);

        const fromCoords = getScreenCoords(fromNode);
        const toCoords = getScreenCoords(toNode);

        const isInPath = solvedPath && solvedPath.path.includes(edge.from) && solvedPath.path.includes(edge.to);
        const pathIndex1 = solvedPath ? solvedPath.path.indexOf(edge.from) : -1;
        const pathIndex2 = solvedPath ? solvedPath.path.indexOf(edge.to) : -1;
        const isSequential = pathIndex1 !== -1 && pathIndex2 !== -1 && Math.abs(pathIndex1 - pathIndex2) === 1;

        // Color based on hazard/blocked status
        let strokeColor = '#ccc';
        let lineWidth = 2;

        if (edge.blocked) {
            strokeColor = '#000000';
            lineWidth = 3;
        } else if (edge.hazard) {
            strokeColor = '#ff6b6b';
            lineWidth = 2;
        } else if (isSequential) {
            strokeColor = '#ffd43b';
            lineWidth = 4;
        }

        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(fromCoords.x, fromCoords.y);
        ctx.lineTo(toCoords.x, toCoords.y);
        ctx.stroke();
    });
}

function drawNodes() {
    graphData.nodes.forEach(node => {
        const coords = getScreenCoords(node);

        let fillColor = '#667eea';
        let textColor = '#ffffff';
        let opacity = 1.0;

        if (node.id === selectedStart) {
            fillColor = '#51cf66';
        } else if (node.id === selectedEnd) {
            fillColor = '#ff6b6b';
        } else if (node.hazard || hazardNodes.has(node.id)) {
            fillColor = '#ff6b6b';
            textColor = '#ffffff';
        } else if (solvedPath && solvedPath.path.includes(node.id)) {
            fillColor = '#ffd43b';
            textColor = '#333333';
        }

        // Dim Zone B nodes if they have hazard
        if (node.zone === 'B' && (node.hazard || hazardNodes.has(node.id))) {
            opacity = 0.8;
        }

        ctx.globalAlpha = opacity;

        ctx.fillStyle = fillColor;
        ctx.beginPath();
        ctx.arc(coords.x, coords.y, nodeRadius, 0, 2 * Math.PI);
        ctx.fill();

        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = textColor;
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(node.id, coords.x, coords.y);
    });

    ctx.globalAlpha = 1;
}

function handleCanvasClick(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    let closestNode = null;
    let closestDistance = nodeRadius + 5;

    graphData.nodes.forEach(node => {
        const coords = getScreenCoords(node);
        const distance = Math.sqrt((x - coords.x) ** 2 + (y - coords.y) ** 2);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestNode = node;
        }
    });

    if (closestNode) {
        selectedStart = closestNode.id;
        document.getElementById('startNode').value = selectedStart;
        drawGraph();
    }
}

async function solveRouting() {
    try {
        const algorithm = document.getElementById('algorithmSelect').value;

        const response = await fetch(`${API_BASE}/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: selectedStart,
                end: selectedEnd,
                algorithm: algorithm,
                avoid_hazards: false,
                risk_weight: riskWeight,
                hazard_weight: 0.0
            })
        });

        if (!response.ok) {
            alert('No path found between selected nodes');
            return;
        }

        solvedPath = await response.json();
        drawGraph();

        document.getElementById('algoDisplay').textContent = solvedPath.algorithm.toUpperCase();
        document.getElementById('timeDisplay').textContent = solvedPath.execution_time_ms;
        document.getElementById('pathDisplay').textContent = solvedPath.path.join(' → ');
        document.getElementById('costDisplay').textContent = solvedPath.cost.toFixed(2);
        document.getElementById('optimalDisplay').textContent = solvedPath.is_optimal ? '✓ Optimal' : '⚠ Heuristic';
        document.getElementById('quantumModeDisplay').textContent = solvedPath.quantum_mode || '—';
        document.getElementById('results').style.display = 'block';
        document.getElementById('comparison').style.display = 'none';
    } catch (error) {
        console.error('Error solving routing:', error);
        alert('Error: Could not solve routing');
    }
}

async function compareAlgorithms() {
    try {
        const response = await fetch(`${API_BASE}/solve/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: selectedStart,
                end: selectedEnd,
                algorithm: 'dijkstra',
                avoid_hazards: false,
                risk_weight: riskWeight,
                hazard_weight: 0.0
            })
        });

        if (!response.ok) {
            alert('Comparison failed');
            return;
        }

        const comparisonResults = await response.json();
        displayComparison(comparisonResults.algorithms);
        document.getElementById('results').style.display = 'none';
        document.getElementById('comparison').style.display = 'block';
    } catch (error) {
        console.error('Error comparing algorithms:', error);
        alert('Error: Could not compare algorithms');
    }
}

function displayComparison(algorithms) {
    const tableBody = document.getElementById('comparisonTable');
    tableBody.innerHTML = '';

    const algoOrder = ['dijkstra', 'dynamic_programming', 'astar', 'quantum', 'genetic'];
    const algoNames = {
        'dijkstra': 'Dijkstra',
        'dynamic_programming': 'Dynamic Programming',
        'astar': 'A* Heuristic',
        'quantum': 'Quantum QAOA',
        'genetic': 'Genetic Algorithm'
    };

    algoOrder.forEach(algoKey => {
        const result = algorithms[algoKey];
        if (!result) return;

        const row = document.createElement('tr');
        row.className = 'border-b border-gray-300 hover:bg-gray-100';

        if (result.error) {
            row.innerHTML = `
                <td class="border border-green-300 p-3 font-semibold">${algoNames[algoKey]}</td>
                <td colspan="4" class="border border-green-300 p-3 text-red-600">Error: ${result.error}</td>
            `;
        } else {
            const modeText = result.mode ? ` (${result.mode})` : '';
            row.innerHTML = `
                <td class="border border-green-300 p-3 font-semibold">${algoNames[algoKey]}</td>
                <td class="border border-green-300 p-3 text-right font-mono">${result.cost === Infinity ? '∞' : result.cost.toFixed(2)}</td>
                <td class="border border-green-300 p-3 text-right font-mono">${result.execution_time_ms.toFixed(2)}</td>
                <td class="border border-green-300 p-3 text-center">${result.is_optimal ? '✓' : '✗'}</td>
                <td class="border border-green-300 p-3 text-sm">${modeText || '—'}</td>
            `;
        }

        tableBody.appendChild(row);
    });
}

async function toggleZoneBHazard() {
    try {
        // Zone B nodes: 6-13
        const zoneBNodes = [6, 7, 8, 9, 10, 11, 12, 13];
        const newHazardState = !Array.from(hazardNodes).some(n => zoneBNodes.includes(n));

        const response = await fetch(`${API_BASE}/graph/hazards`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                node_ids: zoneBNodes,
                edge_ids: [],
                set_to: newHazardState
            })
        });

        if (response.ok) {
            if (newHazardState) {
                zoneBNodes.forEach(n => hazardNodes.add(n));
                document.getElementById('hazardZoneB').classList.remove('bg-red-500', 'hover:bg-red-600');
                document.getElementById('hazardZoneB').classList.add('bg-green-500', 'hover:bg-green-600');
                document.getElementById('hazardZoneB').textContent = 'Zone B Hazard: ON';
            } else {
                zoneBNodes.forEach(n => hazardNodes.delete(n));
                document.getElementById('hazardZoneB').classList.remove('bg-green-500', 'hover:bg-green-600');
                document.getElementById('hazardZoneB').classList.add('bg-red-500', 'hover:bg-red-600');
                document.getElementById('hazardZoneB').textContent = 'Toggle Zone B as Hazard';
            }
            graphData = await response.json();
            drawGraph();
        }
    } catch (error) {
        console.error('Error updating hazards:', error);
    }
}

function resetVisualization() {
    selectedStart = 0;
    selectedEnd = 23;
    solvedPath = null;
    hazardNodes.clear();
    document.getElementById('startNode').value = 0;
    document.getElementById('endNode').value = 23;
    document.getElementById('results').style.display = 'none';
    document.getElementById('comparison').style.display = 'none';
    document.getElementById('hazardZoneB').classList.remove('bg-green-500', 'hover:bg-green-600');
    document.getElementById('hazardZoneB').classList.add('bg-red-500', 'hover:bg-red-600');
    document.getElementById('hazardZoneB').textContent = 'Toggle Zone B as Hazard';
    drawGraph();
}

document.addEventListener('DOMContentLoaded', initializeApp);