const API_BASE = 'http://localhost:8000';

let graphData = null;
let selectedStart = null;
let selectedEnd = null;
let solvedPath = null;
let map = null;
let nodeLayer = null;
let edgeLayer = null;
let pathLayer = null;
let legendControl = null;
let hazardNodes = new Set();
let blockedNodes = new Set();
let editMode = 'start';
let trafficData = null;
let hazardPredictions = null;
let routeQualityData = null;
const mapBounds = {
    minLat: 24.70,
    maxLat: 24.90,
    minLng: 46.60,
    maxLng: 46.90
};

const CLASSICAL_ALGOS = new Set(['dijkstra', 'dynamic_programming', 'astar', 'genetic']);
const ALGO_MULTIPLIERS = {
    dijkstra: 150,
    astar: 100,
    dynamic_programming: 170,
    genetic: 220,
    quantum: 1
};

const DEFAULT_WEIGHTS = {
    distance_weight: 1.0,
    risk_weight: 0.5,
    hazard_weight: 0.7,
    congestion_weight: 0.5
};
const REGION_COLORS = {
    'Residential Zone': { fill: '#3b82f6', border: '#1d4ed8' },
    'Transition Zone': { fill: '#9ca3af', border: '#6b7280' },
    'High-Risk Zone': { fill: '#ef4444', border: '#b91c1c' },
    'Conflict / Control Zone': { fill: '#111827', border: '#7f1d1d' },
    'Safe Zone': { fill: '#22c55e', border: '#15803d' },
    default: { fill: '#64748b', border: '#e2e8f0' }
};

function isConflictRegion(regionA, regionB) {
    if (!regionA || !regionB) return false;
    const key = `${regionA}::${regionB}`;
    const conflicts = new Set([
        'Residential Zone::High-Risk Zone',
        'High-Risk Zone::Residential Zone',
        'Safe Zone::High-Risk Zone',
        'High-Risk Zone::Safe Zone',
        'Residential Zone::Conflict / Control Zone',
        'Conflict / Control Zone::Residential Zone'
        // Safe Zone <-> Conflict / Control Zone removed (no overlap)
    ]);
    return conflicts.has(key);
}
function showToast(message, type = 'info', timeout = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    const baseClasses = 'px-5 py-4 rounded shadow-lg text-base font-semibold border';
    const typeClasses = {
        info: 'bg-blue-50 text-blue-800 border-blue-200',
        success: 'bg-green-50 text-green-800 border-green-200',
        warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
        error: 'bg-red-50 text-red-800 border-red-200'
    };
    toast.className = `${baseClasses} ${typeClasses[type] || typeClasses.info}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, timeout);
}

function showConfirm(title, message) {
    return new Promise((resolve) => {
        const overlay = document.getElementById('confirmOverlay');
        const titleEl = document.getElementById('confirmTitle');
        const messageEl = document.getElementById('confirmMessage');
        const okBtn = document.getElementById('confirmOk');
        const cancelBtn = document.getElementById('confirmCancel');

        if (!overlay || !titleEl || !messageEl || !okBtn || !cancelBtn) {
            resolve(false);
            return;
        }

        titleEl.textContent = title;
        messageEl.textContent = message;
        overlay.classList.remove('hidden');
        overlay.style.display = 'flex';

        const cleanup = () => {
            overlay.classList.add('hidden');
            overlay.style.display = 'none';
            okBtn.removeEventListener('click', onOk);
            cancelBtn.removeEventListener('click', onCancel);
        };

        const onOk = () => {
            cleanup();
            resolve(true);
        };

        const onCancel = () => {
            cleanup();
            resolve(false);
        };

        okBtn.addEventListener('click', onOk);
        cancelBtn.addEventListener('click', onCancel);
    });
}

function setSolveStatus(message) {
    const statusEl = document.getElementById('solveStatus');
    const overlayEl = document.getElementById('loadingOverlay');
    const overlayText = document.getElementById('loadingText');
    if (!statusEl) return;
    if (message) {
        statusEl.textContent = message;
        statusEl.classList.remove('hidden');
        statusEl.style.display = 'block';
        if (overlayText) overlayText.textContent = message;
        if (overlayEl) {
            overlayEl.classList.remove('hidden');
            overlayEl.style.display = 'flex';
        }
    } else {
        statusEl.textContent = '';
        statusEl.classList.add('hidden');
        statusEl.style.display = 'none';
        if (overlayEl) {
            overlayEl.classList.add('hidden');
            overlayEl.style.display = 'none';
        }
    }
}

async function initializeApp() {
    initMap();

    try {
        const response = await fetch(`${API_BASE}/graph`);
        graphData = await response.json();
        hazardNodes = new Set(graphData.nodes.filter(n => n.hazard).map(n => n.id));
        drawGraph();
    } catch (error) {
        console.error('Failed to load graph:', error);
        showToast('Could not connect to backend. Make sure the server is running on port 9000.', 'error');
    }



    // Event listeners
    document.getElementById('solveBtn').addEventListener('click', solveRouting);
    document.getElementById('resetBtn').addEventListener('click', resetVisualization);

    document.getElementById('modeStart').addEventListener('click', () => setEditMode('start'));
    document.getElementById('modeEnd').addEventListener('click', () => setEditMode('end'));
    document.getElementById('modeBlocked').addEventListener('click', () => setEditMode('blocked'));

    setEditMode('start');
}

function setEditMode(mode) {
    editMode = mode;
    const buttons = {
        start: document.getElementById('modeStart'),
        end: document.getElementById('modeEnd'),
        blocked: document.getElementById('modeBlocked')
    };

    Object.entries(buttons).forEach(([key, button]) => {
        if (!button) return;
        if (key === mode) {
            button.classList.add('ring-2', 'ring-offset-2', 'ring-purple-500');
        } else {
            button.classList.remove('ring-2', 'ring-offset-2', 'ring-purple-500');
        }
    });
}

function initMap() {
    map = L.map('graphMap', { zoomControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    edgeLayer = L.layerGroup().addTo(map);
    nodeLayer = L.layerGroup().addTo(map);
    pathLayer = L.layerGroup().addTo(map);

    window.addEventListener('resize', () => {
        if (map) map.invalidateSize();
    });
}

function getGraphBounds() {
    const minX = Math.min(...graphData.nodes.map(n => n.x));
    const maxX = Math.max(...graphData.nodes.map(n => n.x));
    const minY = Math.min(...graphData.nodes.map(n => n.y));
    const maxY = Math.max(...graphData.nodes.map(n => n.y));
    return { minX, maxX, minY, maxY };
}

function nodeToLatLng(node) {
    const { minX, maxX, minY, maxY } = getGraphBounds();
    const xRange = maxX - minX || 1;
    const yRange = maxY - minY || 1;
    const xRatio = (node.x - minX) / xRange;
    const yRatio = (node.y - minY) / yRange;

    const lat = mapBounds.maxLat - yRatio * (mapBounds.maxLat - mapBounds.minLat);
    const lng = mapBounds.minLng + xRatio * (mapBounds.maxLng - mapBounds.minLng);
    return [lat, lng];
}

function toLatLng(node) {
    return nodeToLatLng(node);
}

function drawGraph() {
    if (!map || !graphData) return;

    edgeLayer.clearLayers();
    nodeLayer.clearLayers();
    pathLayer.clearLayers();

    drawEdgesMap();
    drawPathMap();
    drawNodesMap();
    drawLegendMap();

    const bounds = L.latLngBounds([
        [mapBounds.minLat, mapBounds.minLng],
        [mapBounds.maxLat, mapBounds.maxLng]
    ]);
    map.fitBounds(bounds, { padding: [20, 20] });
}

function drawEdgesMap() {
    graphData.edges.forEach(edge => {
        const fromNode = graphData.nodes.find(n => n.id === edge.from);
        const toNode = graphData.nodes.find(n => n.id === edge.to);
        if (!fromNode || !toNode) return;

        const fromLatLng = toLatLng(fromNode);
        const toLatLngCoords = toLatLng(toNode);

        const pathIndex1 = solvedPath ? solvedPath.path.indexOf(edge.from) : -1;
        const pathIndex2 = solvedPath ? solvedPath.path.indexOf(edge.to) : -1;
        const isSequential = pathIndex1 !== -1 && pathIndex2 !== -1 && Math.abs(pathIndex1 - pathIndex2) === 1;

        let strokeColor = '#9ca3af';
        let lineWidth = 2;
        let opacity = 0.6;
        let dashArray = null;

        if (edge.blocked) {
            strokeColor = '#111827';
            lineWidth = 3;
            opacity = 0.8;
        } else if (edge.hazard) {
            strokeColor = '#ef4444';
            lineWidth = 2;
            opacity = 0.8;
        } else if (isSequential) {
            strokeColor = '#facc15';
            lineWidth = 4;
            opacity = 0.95;
        } else {
            const risk = edge.risk ?? 1.0;
            if (risk >= 4.0) {
                strokeColor = '#dc2626';
            } else if (risk >= 2.0) {
                strokeColor = '#f97316';
            } else {
                strokeColor = '#22c55e';
            }

            if (isConflictRegion(fromNode.region_type, toNode.region_type)) {
                dashArray = '6 6';
                opacity = 0.45;
            }
        }

        L.polyline([fromLatLng, toLatLngCoords], {
            color: strokeColor,
            weight: lineWidth,
            opacity,
            dashArray
        }).addTo(edgeLayer);
    });
}

function drawPathMap() {
    if (!solvedPath || !solvedPath.path || solvedPath.path.length < 2) return;
    const pathLatLngs = solvedPath.path.map(nodeId => {
        const node = graphData.nodes.find(n => n.id === nodeId);
        return node ? toLatLng(node) : null;
    }).filter(Boolean);

    if (pathLatLngs.length > 1) {
        L.polyline(pathLatLngs, { color: '#facc15', weight: 5, opacity: 0.9 }).addTo(pathLayer);
    }
}

function drawNodesMap() {
    graphData.nodes.forEach(node => {
        // Start with region_type colors as base
        let regionColor = REGION_COLORS[node.region_type] || REGION_COLORS.default;
        let fillColor = regionColor.fill;
        let borderColor = regionColor.border;
        let borderWidth = 2;
        let radius = 7;

        // Check predictions for traffic/hazard overlays
        let nodeTraffic = trafficData ? trafficData.nodes[node.id] : null;
        let nodeHazardPred = hazardPredictions ? hazardPredictions.predictions[node.id] : null;
        
        // Preserve High-Risk Zone color identity
        const isHighRiskZone = node.region_type === 'High-Risk Zone';
        const isConflictZone = node.region_type === 'Conflict / Control Zone';

        if (blockedNodes.has(node.id)) {
            fillColor = '#1f2937';
            borderColor = '#000000';
            borderWidth = 3;
            radius = 8;  // Slightly larger to make blocked nodes stand out
        } else if (node.id === selectedStart) {
            fillColor = '#22c55e';  // Green - original start color
        } else if (node.id === selectedEnd) {
            fillColor = '#ef4444';  // Red - original end color
        } else if (hazardNodes.has(node.id)) {
            fillColor = '#f97316';
        } else if (solvedPath && solvedPath.path.includes(node.id)) {
            fillColor = '#facc15';
        } else if (nodeHazardPred && nodeHazardPred.probability >= 70) {
            // Critical hazard prediction - but preserve High-Risk/Conflict zones' base colors
            if (isHighRiskZone || isConflictZone) {
                // Keep original color, add pulsing border
                borderColor = '#fbbf24';
                borderWidth = 4;
                radius = 8;
            } else {
                // Other zones get red tint
                fillColor = '#fca5a5';
                borderColor = '#ef4444';
            }
        } else if (nodeHazardPred && nodeHazardPred.probability >= 50) {
            // High hazard prediction - preserve dangerous zones
            if (isHighRiskZone || isConflictZone) {
                // Keep original color, add warning border
                borderColor = '#fb923c';
                borderWidth = 3;
            } else {
                // Other zones get orange tint
                fillColor = '#fdba74';
                borderColor = '#f97316';
            }
        } else if (nodeTraffic && nodeTraffic > 70) {
            // High traffic - preserve dangerous zone colors
            if (isHighRiskZone || isConflictZone) {
                borderColor = '#ea580c';
                borderWidth = 3;
            } else {
                fillColor = '#fb923c';
                borderColor = '#ea580c';
            }
        } else if (nodeTraffic && nodeTraffic > 50) {
            // Moderate-high traffic
            if (!isHighRiskZone && !isConflictZone) {
                fillColor = '#fbbf24';
                borderColor = '#f59e0b';
            }
        } else if (nodeTraffic && nodeTraffic > 30) {
            // Moderate traffic
            if (!isHighRiskZone && !isConflictZone) {
                fillColor = '#fcd34d';
            }
        }

        const marker = L.circleMarker(toLatLng(node), {
            radius,
            color: borderColor,
            weight: borderWidth,
            fillColor,
            fillOpacity: 0.95
        }).addTo(nodeLayer);

        // Enhanced tooltip with prediction data
        let tooltipText = `${node.label || `Node ${node.id}`} • 👥 ${node.population ?? 0}`;
        if (nodeTraffic) {
            tooltipText += `<br>🚦 Traffic: ${nodeTraffic}%`;
        }
        if (nodeHazardPred) {
            tooltipText += `<br>⚠ Risk: ${nodeHazardPred.probability}% (${nodeHazardPred.risk_level})`;
        }
        
        marker.bindTooltip(tooltipText, { direction: 'top', offset: [0, -8] });

        marker.on('click', (e) => {
            if (editMode === 'start') {
                selectedStart = node.id;
                drawGraph();
                return;
            }

            if (editMode === 'end') {
                selectedEnd = node.id;
                drawGraph();
                return;
            }

            if (editMode === 'blocked') {
                toggleBlockedNode(node.id);
            }
        });
    });
}

function toggleBlockedNode(nodeId) {
    if (blockedNodes.has(nodeId)) {
        blockedNodes.delete(nodeId);
    } else {
        blockedNodes.add(nodeId);
        // Clear start/end if blocking them
        if (selectedStart === nodeId) {
            selectedStart = null;
        }
        if (selectedEnd === nodeId) {
            selectedEnd = null;
        }
    }
    updateBlockedNodesList();
    drawGraph();
}

function updateBlockedNodesList() {
    const blockedList = document.getElementById('blockedNodesList');
    if (blockedNodes.size === 0) {
        blockedList.innerHTML = '<span class="text-gray-500 italic">None selected</span>';
    } else {
        const nodeArray = Array.from(blockedNodes).sort((a, b) => a - b);
        blockedList.innerHTML = nodeArray.join(', ');
    }
}

async function toggleSingleNodeHazard(nodeId) {
    try {
        const isHazard = hazardNodes.has(nodeId) || graphData.nodes.find(n => n.id === nodeId)?.hazard;
        const response = await fetch(`${API_BASE}/graph/hazards`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                node_ids: [nodeId],
                edge_ids: [],
                set_to: !isHazard
            })
        });

        if (response.ok) {
            graphData = await response.json();
            if (!isHazard) {
                hazardNodes.add(nodeId);
            } else {
                hazardNodes.delete(nodeId);
            }
            drawGraph();
        }
    } catch (error) {
        console.error('Error toggling node hazard:', error);
    }
}

function drawLegendMap() {
    if (legendControl) return;

    legendControl = L.control({ position: 'bottomright' });
    legendControl.onAdd = function () {
        const div = L.DomUtil.create('div', 'bg-white rounded shadow-md p-2 text-xs');
        div.innerHTML = `
            <div class="font-bold mb-1">Legend</div>
            <div class="font-semibold mt-1">Region Types</div>
            <div class="flex items-center gap-2"><span style="background:#3b82f6;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Residential Zone</div>
            <div class="flex items-center gap-2"><span style="background:#9ca3af;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Transition Zone</div>
            <div class="flex items-center gap-2"><span style="background:#ef4444;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> High-Risk Zone*</div>
            <div class="flex items-center gap-2"><span style="background:#111827;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Control/Bottleneck*</div>
            <div class="flex items-center gap-2"><span style="background:#22c55e;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Safe Zone</div>
            <div class="text-[10px] italic mt-1 text-gray-600">*AI predictions use border styling</div>
            <div class="font-semibold mt-2">Special States</div>
            <div class="flex items-center gap-2"><span style="background:#f97316;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Manual Hazard</div>
            <div class="flex items-center gap-2"><span style="background:#1f2937;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Blocked</div>
            <div class="flex items-center gap-2"><span style="background:#facc15;width:10px;height:10px;display:inline-block;border-radius:2px;"></span> Active Path</div>
            <div class="font-semibold mt-2">Edge Risk</div>
            <div class="flex items-center gap-2"><span style="background:#22c55e;width:16px;height:2px;display:inline-block;"></span> Low Risk (&lt;2.0)</div>
            <div class="flex items-center gap-2"><span style="background:#f97316;width:16px;height:2px;display:inline-block;"></span> Medium Risk</div>
            <div class="flex items-center gap-2"><span style="background:#dc2626;width:16px;height:2px;display:inline-block;"></span> High Risk (≥4.0)</div>
            <div class="flex items-center gap-2"><span style="border-top:2px dashed #6b7280;width:16px;display:inline-block;"></span> Conflict Link</div>
        `;
        return div;
    };
    legendControl.addTo(map);
}

function calculatePathMetrics(path) {
    if (!graphData || !path || path.length < 2) {
        return { timeSum: 0, riskSum: 0, hazardEdges: 0, segments: 0 };
    }

    let timeSum = 0;
    let riskSum = 0;
    let hazardEdges = 0;
    let segments = 0;

    for (let i = 0; i < path.length - 1; i++) {
        const from = path[i];
        const to = path[i + 1];
        const edge = graphData.edges.find(e => e.from === from && e.to === to);
        if (!edge) continue;
        timeSum += edge.cost || 0;
        riskSum += edge.risk || 0;
        if (edge.hazard) hazardEdges += 1;
        segments += 1;
    }

    return { timeSum, riskSum, hazardEdges, segments };
}

function calculateConfidence(path) {
    const { timeSum, riskSum, hazardEdges, segments } = calculatePathMetrics(path);
    if (segments === 0) return { score: 0, label: 'Unknown' };

    const avgTime = timeSum / segments;
    const avgRisk = riskSum / segments;

    let score = 100 - (avgRisk * 12 + avgTime * 3 + hazardEdges * 8);
    score = Math.max(35, Math.min(98, score));

    const label = score >= 80 ? 'High' : score >= 60 ? 'Medium' : 'Low';
    return { score: Math.round(score), label };
}

async function solveRouting() {
    if (selectedStart === null || selectedEnd === null) {
        showToast('Please select both start and end nodes first.', 'warning');
        return;
    }
    
    if (blockedNodes.has(selectedStart) || blockedNodes.has(selectedEnd)) {
        showToast('Start or end node is blocked. Please choose different nodes.', 'warning');
        return;
    }

    // Step 1: Compute AI predictions
    setSolveStatus('🤖 Computing AI predictions...');
    await new Promise(requestAnimationFrame);
    
    try {
        const algorithm = document.getElementById('algorithmSelect').value;
        const hazardList = Array.from(hazardNodes).join(',');
        const blockedList = Array.from(blockedNodes).join(',');

        // Fetch all predictions in parallel
        const [trafficResp, hazardResp, qualityResp] = await Promise.all([
            fetch(`${API_BASE}/predict/traffic?hazard_nodes=${hazardList}&blocked_nodes=${blockedList}`),
            fetch(`${API_BASE}/predict/hazards?node_ids=${hazardList}&blocked_nodes=${blockedList}`),
            fetch(`${API_BASE}/predict/route-quality?start=${selectedStart}&end=${selectedEnd}&algorithm=${algorithm}&hazard_nodes=${hazardList}&blocked_nodes=${blockedList}`)
        ]);

        // Check for response errors
        if (!trafficResp.ok || !hazardResp.ok || !qualityResp.ok) {
            setSolveStatus('');
            showToast('Could not fetch AI predictions. Proceeding without predictions.', 'warning');
        } else {
            trafficData = await trafficResp.json();
            hazardPredictions = await hazardResp.json();
            routeQualityData = await qualityResp.json();

            // Check if any response is an error object
            if (!trafficData.detail && !hazardPredictions.detail && !routeQualityData.detail) {
                displayPredictions();
                drawGraph(); // Redraw with prediction overlays
            }
        }
    } catch (error) {
        console.error('Error fetching predictions:', error);
        showToast('AI predictions failed. Proceeding without predictions.', 'warning');
    }

    // Step 2: Find path
    setSolveStatus('🔍 Finding optimal path...');
    await new Promise(resolve => setTimeout(resolve, 500));

    // Step 2: Find path
    setSolveStatus('🔍 Finding optimal path...');
    await new Promise(resolve => setTimeout(resolve, 500));

    // Check route quality prediction if available
    if (routeQualityData) {
        if (routeQualityData.recommendation === 'REJECT') {
            setSolveStatus('');
            const confirmed = await showConfirm(
                'AI Prediction: REJECT',
                `${routeQualityData.reason}\n\nSuccess probability: ${routeQualityData.success_probability}%\n\nProceed anyway?`
            );
            if (!confirmed) {
                return;
            }
            setSolveStatus('🔍 Finding optimal path...');
        } else if (routeQualityData.recommendation === 'SLOW') {
            // No prompt for slow predictions
        } else if (routeQualityData.recommendation === 'CAUTION') {
            console.warn(`AI Prediction Caution: ${routeQualityData.reason}`);
        }
    }

    // Warn about high-risk nodes in path
    if (hazardPredictions && hazardPredictions.high_risk_nodes.length > 0) {
        const criticalNodes = Object.entries(hazardPredictions.predictions)
            .filter(([_, pred]) => pred.risk_level === 'CRITICAL')
            .map(([id, _]) => parseInt(id));
        
        if (criticalNodes.length > 0) {
            console.warn(`⚠ WARNING: ${criticalNodes.length} nodes at CRITICAL hazard risk: ${criticalNodes.join(', ')}`);
        }
    }

    try {
        const algorithm = document.getElementById('algorithmSelect').value;
        
        // Update blocked nodes on backend first (always sync to clear old blocks)
        await fetch(`${API_BASE}/graph/constraints`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                blocked_nodes: Array.from(blockedNodes),
                blocked_edges: []
            })
        });

        const response = await fetch(`${API_BASE}/solve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                start: selectedStart,
                end: selectedEnd,
                algorithm: algorithm,
                avoid_hazards: hazardNodes.size > 0,
                risk_weight: 0.5,
                hazard_weight: 0.0
            })
        });

        if (!response.ok) {
            setSolveStatus('');
            showToast('No path found between selected nodes.', 'error');
            return;
        }

        solvedPath = await response.json();
        const realMs = solvedPath.execution_time_ms ?? 0;
        const isClassical = CLASSICAL_ALGOS.has(algorithm);
        const multiplier = Math.max(1000, ALGO_MULTIPLIERS[algorithm] || 1000);
        const simulatedMs = isClassical
            ? Math.max(1200, Math.round(realMs * multiplier))
            : Math.max(400, Math.round(realMs));
        const simulatedMinutes = (simulatedMs / 60000).toFixed(2);

        if (isClassical) {
            setSolveStatus(`Computing route... (${simulatedMinutes} min)`);
        }

        await new Promise(resolve => setTimeout(resolve, simulatedMs));
        setSolveStatus('');
        drawGraph();
    } catch (error) {
        setSolveStatus('');
        console.error('Error solving routing:', error);
        showToast('Could not solve routing.', 'error');
    }
}

async function resetVisualization() {
    // Hide loading indicator immediately
    setSolveStatus('');
    
    selectedStart = null;
    selectedEnd = null;
    solvedPath = null;
    const hazardsToClear = graphData
        ? graphData.nodes.filter(n => n.hazard).map(n => n.id)
        : Array.from(hazardNodes);
    hazardNodes.clear();
    blockedNodes.clear();
    trafficData = null;
    hazardPredictions = null;
    routeQualityData = null;
    document.getElementById('predictions').style.display = 'none';
    if (hazardsToClear.length > 0) {
        try {
            await fetch(`${API_BASE}/graph/hazards`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    node_ids: hazardsToClear,
                    edge_ids: [],
                    set_to: false
                })
            });
        } catch (error) {
            console.error('Error clearing hazards:', error);
        }
    }
    updateBlockedNodesList();
    drawGraph();
}

async function fetchPredictions() {
    if (!selectedStart && selectedStart !== 0) {
        showToast('Please select start node first.', 'warning');
        return;
    }
    
    if (!selectedEnd && selectedEnd !== 0) {
        showToast('Please select end node first.', 'warning');
        return;
    }

    try {
        const algorithm = document.getElementById('algorithmSelect').value;
        const hazardList = Array.from(hazardNodes).join(',');
        const blockedList = Array.from(blockedNodes).join(',');

        // Fetch all predictions in parallel
        const [trafficResp, hazardResp, qualityResp] = await Promise.all([
            fetch(`${API_BASE}/predict/traffic?hazard_nodes=${hazardList}&blocked_nodes=${blockedList}`),
            fetch(`${API_BASE}/predict/hazards?node_ids=${hazardList}&blocked_nodes=${blockedList}`),
            fetch(`${API_BASE}/predict/route-quality?start=${selectedStart}&end=${selectedEnd}&algorithm=${algorithm}&hazard_nodes=${hazardList}&blocked_nodes=${blockedList}`)
        ]);

        // Check for response errors
        if (!trafficResp.ok || !hazardResp.ok || !qualityResp.ok) {
            const trafficError = !trafficResp.ok ? await trafficResp.text() : '';
            const hazardError = !hazardResp.ok ? await hazardResp.text() : '';
            const qualityError = !qualityResp.ok ? await qualityResp.text() : '';
            
            console.error('Prediction errors:', {trafficError, hazardError, qualityError});
            showToast('Could not fetch predictions. Please try again.', 'error');
            return;
        }

        trafficData = await trafficResp.json();
        hazardPredictions = await hazardResp.json();
        routeQualityData = await qualityResp.json();

        // Check if any response is an error object
        if (trafficData.detail || hazardPredictions.detail || routeQualityData.detail) {
            console.error('API errors:', {trafficData, hazardPredictions, routeQualityData});
            showToast('Prediction service encountered an error. Check console for details.', 'error');
            return;
        }

        displayPredictions();
        drawGraph(); // Redraw with prediction overlays
    } catch (error) {
        console.error('Error fetching predictions:', error);
        showToast(`Could not fetch predictions - ${error.message}`, 'error');
    }
}

function displayPredictions() {
    // Check if we have valid prediction data
    if (!trafficData || !hazardPredictions || !routeQualityData) {
        console.error('Invalid prediction data:', {trafficData, hazardPredictions, routeQualityData});
        showToast('Incomplete prediction data received.', 'error');
        return;
    }

    // Show predictions panel
    document.getElementById('predictions').style.display = 'block';

    // Route Quality
    const recommendation = routeQualityData.recommendation || 'UNKNOWN';
    const recBadge = document.getElementById('routeRecommendation');
    
    const badgeStyles = {
        'PROCEED': 'bg-green-100 text-green-800',
        'CAUTION': 'bg-yellow-100 text-yellow-800',
        'SLOW': 'bg-orange-100 text-orange-800',
        'REJECT': 'bg-red-100 text-red-800'
    };
    
    recBadge.textContent = recommendation;
    recBadge.className = `px-2 py-1 rounded text-xs font-bold ${badgeStyles[recommendation] || 'bg-gray-100 text-gray-800'}`;
    
    document.getElementById('successProb').textContent = `${routeQualityData.success_probability || 0}%`;
    document.getElementById('estTime').textContent = `${Math.round(routeQualityData.estimated_time || 0)} ms`;
    document.getElementById('complexity').textContent = `${Math.round(routeQualityData.complexity_score || 0)}%`;
    document.getElementById('estCost').textContent = (routeQualityData.estimated_cost || 0).toFixed(1);
    document.getElementById('routeReason').textContent = routeQualityData.reason || 'No prediction available';

    // Traffic Status
    document.getElementById('peakHourBadge').style.display = trafficData.peak_hour ? 'inline-block' : 'none';
    
    const highTrafficNodes = trafficData.nodes ? Object.entries(trafficData.nodes).filter(([_, traffic]) => traffic > 60).length : 0;
    document.getElementById('highTrafficCount').textContent = `${highTrafficNodes} zones`;

    // Hazard Predictions
    document.getElementById('nightTimeBadge').style.display = hazardPredictions.night_time ? 'inline-block' : 'none';
    
    const highRiskNodes = hazardPredictions.high_risk_nodes;
    document.getElementById('highRiskCount').textContent = `${highRiskNodes.length} nodes`;
    
    if (highRiskNodes.length > 0) {
        const criticalNodes = Object.entries(hazardPredictions.predictions)
            .filter(([_, pred]) => pred.risk_level === 'CRITICAL')
            .map(([id, _]) => id);
        
        if (criticalNodes.length > 0) {
            document.getElementById('highRiskList').textContent = `⚠ CRITICAL: Nodes ${criticalNodes.join(', ')}`;
        } else {
            document.getElementById('highRiskList').textContent = `High risk nodes: ${highRiskNodes.join(', ')}`;
        }
    } else {
        document.getElementById('highRiskList').textContent = 'All nodes at acceptable risk levels';
    }
}

document.addEventListener('DOMContentLoaded', initializeApp);