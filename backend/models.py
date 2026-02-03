from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EdgeRef(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_node: int = Field(alias="from")
    to: int


class NodeModel(BaseModel):
    id: int
    x: float
    y: float
    zone: str
    hazard: bool = False
    population: Optional[int] = None
    capacity: Optional[int] = None
    label: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class EdgeModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_node: int = Field(alias="from")
    to: int
    cost: float
    risk: float = 0.0
    hazard: bool = False
    blocked: bool = False
    capacity: Optional[int] = None


class GraphModel(BaseModel):
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    start: int
    end: int


class RoutingRequest(BaseModel):
    start: int
    end: int
    algorithm: str = "dijkstra"
    avoid_hazards: bool = False
    risk_weight: float = 0.0
    hazard_weight: float = 0.0


class PathResponse(BaseModel):
    path: List[int]
    cost: float
    nodes: List[NodeModel]
    edges: List[EdgeModel]
    algorithm: str
    execution_time_ms: float
    is_optimal: bool
    quantum_mode: Optional[str] = None  # "QAOA", "Quantum Annealing Simulation", etc.


class HazardUpdate(BaseModel):
    node_ids: List[int] = []
    edge_ids: List[EdgeRef] = []
    set_to: bool = True


class ConstraintsUpdate(BaseModel):
    blocked_nodes: List[int] = []
    blocked_edges: List[EdgeRef] = []


class TrafficPrediction(BaseModel):
    """Traffic/congestion predictions for nodes and edges"""
    nodes: dict  # {node_id: traffic_percentage}
    edges: dict  # {edge_key: traffic_percentage}
    peak_hour: bool
    prediction_time: str


class HazardPrediction(BaseModel):
    """Hazard probability predictions"""
    predictions: dict  # {node_id: {probability: float, risk_level: str}}
    high_risk_nodes: List[int]
    night_time: bool
    prediction_time: str


class RouteQualityPrediction(BaseModel):
    """Route quality prediction before computation"""
    success_probability: float
    estimated_time: float
    estimated_cost: float
    complexity_score: float
    recommendation: str  # "PROCEED", "CAUTION", "REJECT", "SLOW"
    reason: str
    obstacle_density: float
    prediction_time: str
