const API_BASE = 'http://localhost:8000';

let graphData = null;
let selectedStart = 0;
let selectedEnd = 23;
let solvedPath = null;
let canvas = null;
let ctx = null;

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

    document.getElementById('solveBtn').addEventListener('click', solveRouting);
    document.getElementById('resetBtn').addEventListener('click', resetVisualization);
    document.getElementById('startNode').addEventListener('change', (e) => {
        selectedStart = parseInt(e.target.value);
        drawGraph();
    });
    document.getElementById('endNode').addEventListener('change', (e) => {
        selectedEnd = parseInt(e.target.value);
        drawGraph();
    });
    canvas.addEventListener('click', handleCanvasClick);
}

function resizeCanvas() {
    const container = document.querySelector('.canvas-container');
    canvas.width = container.clientWidth - 4;
    canvas.height = container.clientHeight - 4;
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

        ctx.strokeStyle = isSequential ? '#ff6b6b' : '#ccc';
        ctx.lineWidth = isSequential ? 4 : 2;
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

        if (node.id === selectedStart) {
            fillColor = '#51cf66';
        } else if (node.id === selectedEnd) {
            fillColor = '#ff6b6b';
        } else if (solvedPath && solvedPath.path.includes(node.id)) {
            fillColor = '#ffd43b';
            textColor = '#333333';
        }

        if (node.zone === 'B') {
            ctx.globalAlpha = solvedPath && solvedPath.path.includes(node.id) ? 1 : 0.6;
        } else {
            ctx.globalAlpha = 1;
        }

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
                algorithm: algorithm
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
        document.getElementById('results').style.display = 'block';
    } catch (error) {
        console.error('Error solving routing:', error);
        alert('Error: Could not solve routing');
    }
}

function resetVisualization() {
    selectedStart = 0;
    selectedEnd = 23;
    solvedPath = null;
    document.getElementById('startNode').value = 0;
    document.getElementById('endNode').value = 23;
    document.getElementById('results').style.display = 'none';
    drawGraph();
}

document.addEventListener('DOMContentLoaded', initializeApp);